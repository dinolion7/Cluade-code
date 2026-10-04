"""judge 결과를 모델별로 집계해 출력한다. 사용: python3 tools/report.py <run이름>"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from llm import cost

ROOT = os.path.join(os.path.dirname(__file__), '..')
run = sys.argv[1]
KEYS = ['info', 'fidelity', 'rules', 'quality', 'overall']
score = collections.defaultdict(lambda: collections.defaultdict(list))
wins = collections.Counter()
issues = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(ROOT, 'eval', 'runs', run, 'judge', '*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    persona, family, topic = os.path.basename(f)[:-5].split('_', 2)
    for lab, c in d['candidates'].items():
        name = d['labels'][lab]
        for k in KEYS:
            score[(family, name)][k].append(c[k])
            score[(f'{persona}_{family}', name)][k].append(c[k])
        issues[(family, name)] += [f'[{persona}·{topic}] {i}' for i in c.get('issues', [])]
    wins[(family, d['labels'][d['ranking'][0]])] += 1
meta = collections.defaultdict(list)
for f in glob.glob(os.path.join(ROOT, 'eval', 'runs', run, '*_*', '*', '*.json')):
    m = json.load(open(f))
    meta[(os.path.basename(os.path.dirname(os.path.dirname(f))).split('_')[1], os.path.basename(f)[:-5])].append(m)
for group in sorted({g for g, _ in score}):
    print(f'\n## {group}')
    print('| 모델 | ' + ' | '.join(KEYS) + ' | 1위 | 건당 비용 | 평균 초 |')
    print('|---' * (len(KEYS) + 4) + '|')
    rows = sorted(((n, v) for (g, n), v in score.items() if g == group), key=lambda r: -sum(r[1]['overall']) / len(r[1]['overall']))
    for name, v in rows:
        fam = group.split('_')[-1]
        ms = meta[(fam, name)]
        c = sum(cost(m) or 0 for m in ms) / len(ms)
        sec = sum(m['sec'] for m in ms) / len(ms)
        w = wins[(group, name)] if group in ('Claude', 'GPT') else ''
        print(f'| {name} | ' + ' | '.join(f"{sum(v[k]) / len(v[k]):.1f}" for k in KEYS) + f' | {w} | ${c:.4f} | {sec:.0f} |')
if '--issues' in sys.argv:
    for k, v in sorted(issues.items()):
        print(f'\n### {k}')
        print('\n'.join('- ' + i for i in v))
