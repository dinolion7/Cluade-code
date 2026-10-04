"""원본 프롬프트를 스타일 공통(base) + 주제 슬롯으로 무손실 분리한다 (1단계, 1회성).

같은 스타일(페르소나×모델)의 주제별 원본들에서 모든 파일에 공통인 줄(다중 LCS)을
base.txt에 두고, 그 사이에 주제마다 달라지는 줄은 <<<slot NNN>>> 자리표시로 남겨
topics/{주제}.txt에 슬롯별로 저장한다. 건강 3종은 구조가 달라 standalone/에 그대로 둔다.
"""
import glob, os, re, shutil

ROOT = os.path.join(os.path.dirname(__file__), '..', 'prompts')
ORIG = os.path.join(ROOT, 'original')
SRC = os.path.join(ROOT, 'src')
STYLES = ['A_ClaudeSonnet', 'B_ClaudeSonnet', 'A_GPT', 'B_GPT']


def read_lines(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read().replace('\r\n', '\n').split('\n')


def lcs_embed(a, b):
    """a와 b의 LCS를 (i, j) 짝 목록으로 돌려준다."""
    n, m = len(a), len(b)
    T = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        Ti, Tn, ai = T[i], T[i + 1], a[i]
        for j in range(m - 1, -1, -1):
            Ti[j] = Tn[j + 1] + 1 if ai == b[j] else max(Tn[j], Ti[j + 1])
    i = j = 0
    pairs = []
    while i < n and j < m:
        if a[i] == b[j]:
            pairs.append((i, j)); i += 1; j += 1
        elif T[i + 1][j] >= T[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def topic_of(path, style):
    name = os.path.basename(path)
    return name[2:-len('_' + style.split('_', 1)[1] + '.txt')]


def split_style(style):
    persona, model = style.split('_', 1)
    files = sorted(glob.glob(os.path.join(ORIG, f'{persona}_*_{model}.txt')))
    files = [f for f in files if '건강' not in os.path.basename(f)]
    texts = {topic_of(f, style): read_lines(f) for f in files}

    common = next(iter(texts.values()))
    for lines in texts.values():
        common = [common[i] for i, _ in lcs_embed(common, lines)]

    # gaps[topic][k] = common[k] 앞에 오는 주제 고유 줄들 (k == len(common)은 끝)
    gaps = {}
    for topic, lines in texts.items():
        pairs = lcs_embed(common, lines)
        assert len(pairs) == len(common)
        g, prev = {}, 0
        for k, (_, j) in enumerate(pairs + [(len(common), len(lines))]):
            if j > prev:
                g[k] = lines[prev:j]
            prev = j + 1
        gaps[topic] = g
    used = sorted({k for g in gaps.values() for k in g})
    slot_id = {k: f'{n:03d}' for n, k in enumerate(used, 1)}

    out = os.path.join(SRC, style)
    os.makedirs(os.path.join(out, 'topics'), exist_ok=True)
    base = []
    for k in range(len(common) + 1):
        if k in slot_id:
            base.append(f'<<<slot {slot_id[k]}>>>')
        if k < len(common):
            base.append(common[k])
    with open(os.path.join(out, 'base.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(base))
    for topic, g in gaps.items():
        body = []
        for k in sorted(g):
            body.append(f'<<<slot {slot_id[k]}>>>')
            body.extend(g[k])
        with open(os.path.join(out, 'topics', topic + '.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(body))
    avg = sum(len(t) for t in texts.values()) / len(texts)
    print(f'{style}: 주제 {len(texts)}개, 공통 {len(common)}줄 / 평균 {avg:.0f}줄 '
          f'({len(common) / avg:.0%}), 슬롯 {len(used)}개')


def main():
    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    for style in STYLES:
        split_style(style)
    os.makedirs(os.path.join(SRC, 'standalone'), exist_ok=True)
    for f in glob.glob(os.path.join(ORIG, '*건강*.txt')):
        with open(os.path.join(SRC, 'standalone', os.path.basename(f)), 'w', encoding='utf-8') as out:
            out.write('\n'.join(read_lines(f)))


if __name__ == '__main__':
    main()
