"""결과물의 형식 규칙을 자동으로 센다(채점 없이 무료로 비교).
사용: python3 tools/rulecheck.py <run이름>  또는  python3 tools/rulecheck.py <결과 파일> <스타일(A_Claude·B_Claude·A_GPT·B_GPT)>"""
import collections, glob, os, re, statistics, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
LIMITS = {  # 스타일별 볼드 상한, 표 상한, 리스트 상한, 해시태그 범위
    'A_Claude': (4, 2, 2, (3, 5)), 'B_Claude': (4, 2, 2, (3, 5)),
    'A_GPT': (6, 2, 2, (3, 6)), 'B_GPT': (6, 3, 2, (3, 6)),
}
FAIL_TRACE = re.compile(r'확인되지 않|확인이 되지 않|단정하기 어렵|공식 자료가 제한|직접 확인하셔야|확인 필수|확인불가|확인 불가|퍼플렉시티|팩트체크|리서치 결과|조사 결과')
QTABLE = {2: (0, 1), 3: (1, 1), 4: (2, 2), 5: (2, 2), 6: (2, 3), 7: (3, 3), 8: (3, 3)}


def body(text):
    m = re.search(r'```(?:markdown|md)?\n(.*?)```', text, re.S)
    return m.group(1) if m else text


def paras(t):
    """본문 문단(빈 줄로 나뉜 산문 덩어리)만. 제목·소제목·표·리스트·태그·해시태그 줄, 짧은 시적 행은 뺀다."""
    out = []
    for p in re.split(r'\n\s*\n', t):
        p = p.strip()
        if p and not p.startswith(('#', '|', '- ', '* ', '[[', '1. ')):
            out.append(re.sub(r'\s*\n\s*', ' ', p))
    return out


def check(style, text):
    t = body(text)
    lines = t.split('\n')
    subs = [l[3:].strip() for l in lines if l.startswith('## ')]
    bold = len(re.findall(r'\*\*[^*\n]+?\*\*', t))
    tables = len(re.findall(r'(?m)^\|.*\|\s*\n\|[-: |]+\|', t))
    lists, prev = 0, False
    for l in lines:
        cur = bool(re.match(r'\s*[-*] ', l))
        lists += cur and not prev
        prev = cur
    tags = re.findall(r'#[^\s#]+', lines[-1] if lines else '') if lines else []
    for l in reversed(lines):
        if l.strip():
            tags = re.findall(r'(?<!\S)#[^\s#]+', l)
            break
    titles = [l for l in lines if re.match(r'# [^#]', l)]
    title = titles[0][2:].strip() if titles else ''
    bmax, tmax, lmax, (hmin, hmax) = LIMITS[style]
    r = {
        '제목1개': len(titles) == 1,
        '###없음': not any(l.startswith('###') for l in lines),
        f'볼드2~{bmax}': 2 <= bold <= bmax,
        f'표≤{tmax}': tables <= tmax,
        f'리스트≤{lmax}': lists <= lmax,
        f'해시태그{hmin}~{hmax}': hmin <= len(tags) <= hmax,
        '인용마커없음': not re.search(r'contentReference|oaicite|【|\[\d+\]', t),
        '소제목≤8': len(subs) <= 8,
        '제목≤60자': 0 < len(title) <= 60,
        '제목쉼표1개': title.count(',') == 1,
        '천단위쉼표없음': not re.search(r'\d,\d{3}', title),
        '소제목특수문자없음': not any(re.search(r'[-:/()\[\]]', s) or '?' in s[:-1] for s in subs),
        '문단≤150자': all(len(p) <= 150 for p in paras(t)),
        '해시태그기호없음': all(re.fullmatch(r'#[가-힣A-Za-z0-9]+', g) for g in tags),
        '확인실패문장없음': not FAIL_TRACE.search(t),
    }
    if style == 'B_Claude':
        r['질문형연속없음'] = not any(subs[i].endswith('?') and subs[i + 1].endswith('?') for i in range(len(subs) - 1))
    if style == 'B_GPT':
        q = sum(s.endswith('?') for s in subs)
        lo, hi = QTABLE.get(len(subs), (0, len(subs)))
        r['질문형소제목수'] = lo <= q <= hi
        r['질문형연속없음'] = not any(subs[i].endswith('?') and subs[i + 1].endswith('?') for i in range(len(subs) - 1))
    return r, len(re.sub(r'\s', '', t))


def main():
    if len(sys.argv) == 3 and os.path.isfile(sys.argv[1]):  # 결과물 한 편 점검: rulecheck.py <파일> <스타일>
        r, n = check(sys.argv[2], open(sys.argv[1], encoding='utf-8').read())
        for k, v in r.items():
            print(('통과 ' if v else '실패 ') + k)
        print(f'글자수(공백 제외) {n}')
        return
    run = sys.argv[1]
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(glob.glob(os.path.join(ROOT, 'eval', 'runs', run, '*_*', '*', '*.md'))):
        style = os.path.basename(os.path.dirname(os.path.dirname(f)))
        cfg = os.path.basename(f)[:-3]
        r, n = check(style, open(f, encoding='utf-8').read())
        for k, v in r.items():
            agg[(style, cfg)][k].append(v)
        agg[(style, cfg)]['_len'].append(n)
    for style in LIMITS:
        rows = sorted(k for k in agg if k[0] == style)
        if not rows:
            continue
        keys = [k for k in agg[rows[0]] if k != '_len']
        print(f'\n## {style} (규칙 통과 건수 / 전체)')
        print('| 설정 | ' + ' | '.join(keys) + ' | 통과율 | 평균 글자수 |')
        print('|---' * (len(keys) + 3) + '|')
        for k in rows:
            a = agg[k]
            tot = sum(sum(a[x]) for x in keys) / sum(len(a[x]) for x in keys)
            print(f'| {k[1]} | ' + ' | '.join(f'{sum(a[x])}/{len(a[x])}' for x in keys) + f' | {tot:.0%} | {statistics.mean(a["_len"]):.0f} |')


if __name__ == '__main__':
    main()
