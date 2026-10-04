"""원본 주제 프롬프트에서 스타일 base.md가 요구하는 주제 필드를 Opus로 뽑아 topics/{주제}.md를 만든다.

사용: python3 tools/extract_fields.py <스타일> [주제 ...]
결과는 사람이 검토·수정하는 초안이다. 이미 있는 파일은 건너뛴다.
"""
import glob, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from llm import claude

ROOT = os.path.join(os.path.dirname(__file__), '..', 'prompts')
SYSTEM = """너는 블로그 각색 프롬프트를 모듈로 나누는 편집자다.
[공통 본문]은 같은 스타일의 모든 주제가 함께 쓰는 압축본이며, {{필드}} 자리에 주제별 내용이 들어간다.
[필드 설명]에 따라 [원본 주제 프롬프트]에서 이 주제의 필드 값을 뽑아 주제 파일을 만든다.

원칙
1. 주제별 문구(분야 용어·예시·안전 규칙·면책 예문 등)는 원본 표현을 그대로 옮긴다. 요약하거나 바꾸지 않는다.
   예외: [필드 설명]이 개수를 줄이라고 한 곳(예: 제목 유형 예시 1개만)은 원본 예시 중 가장 좋은 것을 고른다.
2. 공통 본문에 이미 있는 일반 규칙은 필드에 다시 넣지 않는다.
3. 원본에 있는 이 주제만의 규칙이 공통 본문과 어느 필드에도 들어갈 자리가 없으면 반드시 "추가규칙"(섹션 단위)이나
   해당 "…추가" 필드에 넣는다. 주제만의 규칙을 버리지 않는다.
4. 필수 필드인데 원본에 해당 내용이 없으면(예: 면책 문구 규칙이 없는 주제) 같은 분야 성격에 맞게 원본 문체로 새로 쓴다.
5. 맨 끝에 "@@ _메모" 필드를 두고 다음을 불릿으로 적는다: (a) 원본에 없어서 새로 쓴 필드, (b) 원본에 있었지만
   공통 본문과 내용이 달라 공통 본문 쪽으로 통일된 규칙(원본 문구 요약과 함께), (c) 원본의 복붙 흔적·오류로 보여 고친 것.
6. 출력은 주제 파일 내용만. 각 필드는 "@@ 필드명" 한 줄로 시작하고 그 아래에 값을 쓴다. 선택 필드(?)가 비면 아예 쓰지 않는다.
   코드블럭이나 설명을 붙이지 않는다."""


def run(style, topic_file):
    persona, model = style.split('_', 1)
    topic = os.path.basename(topic_file)[len(persona) + 1:-len(model) - 5]
    out = os.path.join(ROOT, 'src', style, 'topics', topic + '.md')
    if os.path.exists(out):
        return
    base = open(os.path.join(ROOT, 'src', style, 'base.md'), encoding='utf-8').read()
    spec = open(os.path.join(ROOT, 'src', style, 'fields.md'), encoding='utf-8').read()
    orig = open(topic_file, encoding='utf-8').read()
    user = f'[공통 본문]\n{base}\n\n[필드 설명]\n{spec}\n\n[원본 주제 프롬프트 — 주제: {topic}]\n{orig}'
    text, meta = claude('claude-opus-5-5', SYSTEM, user, max_tokens=32000, effort='high')
    text = text.strip().removeprefix('```markdown').removeprefix('```').removesuffix('```').strip()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(text + '\n')
    print('extracted', style, topic, meta, flush=True)


if __name__ == '__main__':
    style = sys.argv[1]
    persona, model = style.split('_', 1)
    files = sorted(glob.glob(os.path.join(ROOT, 'original', f'{persona}_*_{model}.txt')))
    files = [f for f in files if '검수' not in f and '편집' not in f]
    if sys.argv[2:]:
        files = [f for f in files if any(f'_{t}_' in os.path.basename(f) for t in sys.argv[2:])]
    with ThreadPoolExecutor(5) as ex:
        for fut in [ex.submit(run, style, f) for f in files]:
            fut.result()
