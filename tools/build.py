"""prompts/src → prompts/dist 조립.

스타일 폴더 구성
- base.md + topics/{주제}.md : base의 {{필드}} / {{?필드}}(없어도 됨) 자리에 주제 파일의 "@@ 필드" 블록을 넣는다.
  자리표시가 한 줄을 통째로 차지하면 여러 줄 값으로 바꾸고, 선택 필드가 비어 있으면 그 줄을 지운다.
- base.txt + topics/{주제}.txt : 1단계 무손실 분리 형식(<<<slot NNN>>>). 아직 정리 전인 스타일용.
- 건강 주제가 있는 스타일은 src/health/1검수.md(공통)와 2편집.md(+스타일의 health.md)로 ②검수·③편집도 만든다.
"""
import glob, os, re, shutil

ROOT = os.path.join(os.path.dirname(__file__), '..', 'prompts')
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
SLOT = re.compile(r'^<<<slot (\d+)>>>$')
FIELD = re.compile(r'\{\{(\?)?([^{}]+?)\}\}')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read().split('\n')


# ---- 슬롯 형식 (1단계) ----
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


# ---- 필드 형식 ----
def parse_fields(lines, where):
    fields, cur = {}, None
    for line in lines:
        if line.startswith('@@ '):
            cur = line[3:].strip()
            if cur in fields:
                raise ValueError(f'{where}: 필드 중복 {cur}')
            fields[cur] = []
        elif cur is None:
            if line.strip() and not line.startswith('#'):
                raise ValueError(f'{where}: 필드 표시 앞에 내용이 있음: {line!r}')
        else:
            fields[cur].append(line)
    return {k: '\n'.join(v).strip('\n') for k, v in fields.items() if not k.startswith('_')}


def fill(base, fields, where, optional=frozenset()):
    used, out = set(optional), []
    for line in base:
        whole = FIELD.fullmatch(line.strip())
        if whole:
            opt, name = whole.group(1), whole.group(2)
            used.add(name)
            if name in fields and fields[name]:
                out.extend(fields[name].split('\n'))
            elif not opt:
                raise ValueError(f'{where}: 필수 필드 없음 {name}')
            continue

        def sub(m):
            used.add(m.group(2))
            v = fields.get(m.group(2), '')
            if not v and not m.group(1):
                raise ValueError(f'{where}: 필수 필드 없음 {m.group(2)}')
            if '\n' in v:
                raise ValueError(f'{where}: 줄 안 필드에 여러 줄 값 {m.group(2)}')
            return v
        out.append(FIELD.sub(sub, line))
    extra = set(fields) - used
    if extra:
        raise ValueError(f'{where}: base에 없는 필드 {sorted(extra)}')
    text = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip('\n')
    return text + '\n'


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    n = 0
    for style_dir in sorted(glob.glob(os.path.join(SRC, '*_*'))):
        style = os.path.basename(style_dir)
        persona, model = style.split('_', 1)
        if glob.glob(os.path.join(style_dir, 'topics', '*.md')):
            base = read(os.path.join(style_dir, 'base.md'))
            dpath = os.path.join(style_dir, 'defaults.md')
            defaults = parse_fields(read(dpath), f'{style}/defaults') if os.path.exists(dpath) else {}
            for tf in sorted(glob.glob(os.path.join(style_dir, 'topics', '*.md'))):
                topic = os.path.basename(tf)[:-3]
                where = f'{style}/{topic}'
                text = fill(base, {**defaults, **parse_fields(read(tf), where)}, where, set(defaults))
                with open(os.path.join(DIST, f'{persona}_{topic}_{model}.txt'), 'w', encoding='utf-8') as f:
                    f.write(text)
                n += 1
        else:
            base = read(os.path.join(style_dir, 'base.txt'))
            for tf in sorted(glob.glob(os.path.join(style_dir, 'topics', '*.txt'))):
                topic = os.path.basename(tf)[:-4]
                text = '\n'.join(assemble(base, parse_topic(read(tf))))
                with open(os.path.join(DIST, f'{persona}_{topic}_{model}.txt'), 'w', encoding='utf-8') as f:
                    f.write(text)
                n += 1
        # 건강 파이프라인: ②검수는 공통, ③편집은 스타일별 톤 문장(health.md)만 다르다
        hpath = os.path.join(style_dir, 'health.md')
        if os.path.exists(os.path.join(style_dir, 'topics', '건강.md')) and os.path.exists(hpath):
            review = '\n'.join(read(os.path.join(SRC, 'health', '1검수.md'))).strip('\n') + '\n'
            edit = fill(read(os.path.join(SRC, 'health', '2편집.md')),
                        parse_fields(read(hpath), f'{style}/health'), f'{style}/health')
            for stage, text in (('1검수', review), ('2편집', edit)):
                with open(os.path.join(DIST, f'{persona}_건강-{stage}_{model}.txt'), 'w', encoding='utf-8') as f:
                    f.write(text)
                n += 1
    # 앞단계(지식인 1~4)와 정책뉴스·복지로는 조립 없이 원본을 그대로 복사해, 최종본을 dist 한곳에 모은다
    for sub, folder, skip in (('pipeline', '지식인_앞단계', 'README.md'), ('policy', '정책복지로', 'README.md')):
        out = os.path.join(DIST, folder)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        for src in sorted(glob.glob(os.path.join(ROOT, sub, '*.md'))):
            if os.path.basename(src) != skip:
                shutil.copy(src, os.path.join(out, os.path.basename(src)[:-3] + '.txt'))
                n += 1
    print(f'dist/ 에 {n}개 생성')


if __name__ == '__main__':
    main()
