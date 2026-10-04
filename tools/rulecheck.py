"""결과물의 형식 규칙을 자동으로 센다(채점 없이 무료로 비교). 사용: python3 tools/rulecheck.py <run이름>"""
import collections, glob, os, re, statistics, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
LIMITS = {  # 스타일별 볼드 상한, 표 상한, 리스트 상한, 해시태그 범위
    'A_Claude': (4, 2, 2, (3, 5)), 'B_Claude': (4, 2, 2, (3, 5)),
    'A_GPT': (6, 2, 2, (3, 6)), 'B_GPT': (6, 3, 2, (3, 6)),
}
QTABLE = {2: (0, 1), 3: (1, 1), 4: (2, 2), 5: (2, 2), 6: (2, 3), 7: (3, 3), 8: (3, 3)}


def body(text):
    m = re.search(r'```(?:markdown|md)?\n(.*?)```', text, re.S)
    return m.group(1) if m else text


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
    }
    if style == 'B_GPT':
        q = sum(s.endswith('?') for s in subs)
        lo, hi = QTABLE.get(len(subs), (0, len(subs)))
        r['질문형소제목수'] = lo <= q <= hi
        r['질문형연속없음'] = not any(subs[i].endswith('?') and subs[i + 1].endswith('?') for i in range(len(subs) - 1))
    return r, len(re.sub(r'\s', '', t))


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
