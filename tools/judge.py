"""같은 (스타일, 주제)의 여러 모델 결과를 익명으로 섞어 Opus가 한 번에 비교 채점한다.

사용: python3 tools/judge.py <run이름>  →  eval/runs/<run>/judge/*.json
"""
import glob, json, os, random, re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from llm import claude

ROOT = os.path.join(os.path.dirname(__file__), '..')
PROMPT_FILE = {'Claude': '{p}_{t}_ClaudeSonnet.txt', 'GPT': '{p}_{t}_GPT.txt'}
JUDGE_SYSTEM = """너는 블로그 각색 결과물을 평가하는 엄격한 편집장이다.
[각색 프롬프트]는 작성 모델이 받은 지시 전체이고, [입력 원문]은 작성 모델이 받은 원문이다.
여러 후보 결과물(후보 X1, X2 …)을 같은 기준으로 비교해 채점한다. 후보가 어떤 모델인지는 알 수 없고 추측하지 않는다.

항목별 1~10점 (10이 최고):
- info: 입력 원문의 핵심 정보(수치·기준·기한·기관명·제도명·절차·예외)를 빠짐없이 정확히 보존했는가
- fidelity: 원문에 없는 수치·제도·사실을 만들어 내거나 원문과 다르게 바꾼 것이 없는가 (하나라도 있으면 크게 감점)
- rules: 각색 프롬프트의 형식·구조 규칙(출력 형식, 제목·소제목 규칙, 도입부, 볼드·표·리스트 횟수, 면책 문구, 해시태그, 금지 표현, 분량 등)을 얼마나 지켰는가
- quality: 프롬프트가 요구하는 페르소나·문체로 자연스럽고 읽기 좋은 글인가, 실제 블로그에 바로 올릴 만한가
- overall: 위를 종합해 "이대로 발행해도 되는가" 기준의 총점

출력은 아래 JSON만, 코드블럭 없이:
{"candidates": {"X1": {"info": n, "fidelity": n, "rules": n, "quality": n, "overall": n, "issues": ["가장 중요한 문제 1~3개, 구체적으로"]}, ...}, "ranking": ["X?", ...], "note": "후보 간 차이 한두 문장"}"""


def judge_one(run, style_dir):
    persona, family = os.path.basename(os.path.dirname(style_dir)).split('_')
    topic = os.path.basename(style_dir)
    out = os.path.join(ROOT, 'eval', 'runs', run, 'judge', f'{persona}_{family}_{topic}.json')
    if os.path.exists(out):
        return
    prompt = open(os.path.join(ROOT, 'prompts', 'dist', PROMPT_FILE[family].format(p=persona, t=topic)), encoding='utf-8').read()
    source = open(os.path.join(ROOT, 'eval', 'inputs', topic + '.txt'), encoding='utf-8').read()
    names = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(style_dir, '*.md')))
    rnd = random.Random(f'{run}/{persona}/{family}/{topic}')
    rnd.shuffle(names)
    labels = {f'X{i}': n for i, n in enumerate(names, 1)}
    body = [f'[각색 프롬프트]\n{prompt}\n\n[입력 원문]\n{source}\n']
    for lab, n in labels.items():
        body.append(f'\n===== 후보 {lab} =====\n' + open(os.path.join(style_dir, n + '.md'), encoding='utf-8').read())
    text, meta = claude('claude-opus-5-5', JUDGE_SYSTEM, ''.join(body), effort='high')
    data = json.loads(re.search(r'\{.*\}', text, re.S).group(0))
    data['labels'] = labels
    data['meta'] = meta
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('judged', persona, family, topic, meta, flush=True)


if __name__ == '__main__':
    run = sys.argv[1]
    dirs = glob.glob(os.path.join(ROOT, 'eval', 'runs', run, '*_*', '*'))
    dirs = [d for d in dirs if os.path.isdir(d) and '/judge' not in d]
    with ThreadPoolExecutor(6) as ex:
        for f in [ex.submit(judge_one, run, d) for d in dirs]:
            try:
                f.result()
            except Exception as e:
                print('FAIL', repr(e)[:300], flush=True)
