"""dist 프롬프트 × 입력 원문 × 모델 설정을 실행해 eval/runs/<run>/에 결과를 저장한다.

사용: python3 tools/run_eval.py <run이름> [--prompts dist|original]
"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from llm import claude, gpt

ROOT = os.path.join(os.path.dirname(__file__), '..')
CONFIGS = {
    'Claude': {
        'sonnet-5.5': lambda s, u: claude('claude-sonnet-5-5', s, u),
        'haiku-4.5': lambda s, u: claude('claude-haiku-4-5', s, u),
        'sonnet-5.5-medium': lambda s, u: claude('claude-sonnet-5-5', s, u, effort='medium'),
        'sonnet-5.5-low': lambda s, u: claude('claude-sonnet-5-5', s, u, effort='low'),
        'haiku-4.5-think': lambda s, u: claude('claude-haiku-4-5', s, u, max_tokens=24000,
                                               thinking={'type': 'enabled', 'budget_tokens': 8000}),
    },
    'GPT': {
        'gpt-4.1-mini': lambda s, u: gpt('gpt-4.1-mini', s, u),
        'gpt-4.1': lambda s, u: gpt('gpt-4.1', s, u),
        'gpt-5-mini': lambda s, u: gpt('gpt-5-mini', s, u),
        'gpt-5.4-mini': lambda s, u: gpt('gpt-5.4-mini', s, u),
        'gpt-5.4-mini-reason': lambda s, u: gpt('gpt-5.4-mini', s, u, reasoning_effort='medium'),
    },
}
PROMPT_FILE = {'Claude': '{p}_{t}_ClaudeSonnet.txt', 'GPT': '{p}_{t}_GPT.txt'}


def jobs(run, prompts):
    for inp in sorted(os.listdir(os.path.join(ROOT, 'eval', 'inputs'))):
        topic = inp[:-4]
        user = open(os.path.join(ROOT, 'eval', 'inputs', inp), encoding='utf-8').read()
        for persona in 'AB':
            for family, cfgs in CONFIGS.items():
                pf = os.path.join(ROOT, 'prompts', prompts, PROMPT_FILE[family].format(p=persona, t=topic))
                if not os.path.exists(pf):
                    continue
                system = open(pf, encoding='utf-8').read()
                for name, fn in cfgs.items():
                    out = os.path.join(ROOT, 'eval', 'runs', run, f'{persona}_{family}', topic, name)
                    if not os.path.exists(out + '.json'):
                        yield out, fn, system, user


def work(job):
    out, fn, system, user = job
    try:
        text, meta = fn(system, user)
    except Exception as e:  # 한 건 실패가 전체를 멈추지 않게 기록만 한다
        print('FAIL', out, repr(e)[:200], flush=True)
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out + '.md', 'w', encoding='utf-8').write(text)
    json.dump(meta, open(out + '.json', 'w'), ensure_ascii=False)
    print('ok', os.path.relpath(out, ROOT), meta, flush=True)


if __name__ == '__main__':
    run = sys.argv[1]
    only = os.environ.get('ONLY')  # 쉼표로 구분한 설정 이름만 실행
    if only:
        keep = only.split(',')
        for cfgs in CONFIGS.values():
            for k in list(cfgs):
                if k not in keep:
                    del cfgs[k]
    prompts = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--prompts' else 'dist'
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(work, list(jobs(run, prompts))))
