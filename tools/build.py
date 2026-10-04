"""prompts/src → prompts/dist 조립. 스타일 base의 <<<slot NNN>>> 자리에 주제 파일의 같은 슬롯 내용을 넣는다."""
import glob, os, re, shutil

ROOT = os.path.join(os.path.dirname(__file__), '..', 'prompts')
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
SLOT = re.compile(r'^<<<slot (\d+)>>>$')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read().split('\n')


def parse_topic(lines):
    slots, cur = {}, None
    for line in lines:
        m = SLOT.match(line)
        if m:
            cur = slots.setdefault(m.group(1), [])
        elif cur is None:
            raise ValueError(f'슬롯 표시 앞에 내용이 있음: {line!r}')
        else:
            cur.append(line)
    return slots


def assemble(base, slots):
    out = []
    for line in base:
        m = SLOT.match(line)
        if m:
            out.extend(slots.pop(m.group(1), []))
        else:
            out.append(line)
    if slots:
        raise ValueError(f'base에 없는 슬롯: {sorted(slots)}')
    return out


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    n = 0
    for style_dir in sorted(glob.glob(os.path.join(SRC, '*_*'))):
        style = os.path.basename(style_dir)
        persona, model = style.split('_', 1)
        base = read(os.path.join(style_dir, 'base.txt'))
        for tf in sorted(glob.glob(os.path.join(style_dir, 'topics', '*.txt'))):
            topic = os.path.basename(tf)[:-4]
            text = '\n'.join(assemble(base, parse_topic(read(tf))))
            with open(os.path.join(DIST, f'{persona}_{topic}_{model}.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
            n += 1
    for f in glob.glob(os.path.join(SRC, 'standalone', '*.txt')):
        shutil.copy(f, DIST)
        n += 1
    print(f'dist/ 에 {n}개 생성')


if __name__ == '__main__':
    main()
