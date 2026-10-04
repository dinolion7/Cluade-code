"""dist/ 결과가 original/ 원본과 같은지 확인한다 (줄바꿈 CRLF/LF 차이는 무시)."""
import glob, os, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', 'prompts')


def norm(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read().replace('\r\n', '\n')


orig = {os.path.basename(p): p for p in glob.glob(os.path.join(ROOT, 'original', '*.txt'))}
dist = {os.path.basename(p): p for p in glob.glob(os.path.join(ROOT, 'dist', '*.txt'))}
bad = sorted(set(orig) ^ set(dist)) + sorted(n for n in set(orig) & set(dist) if norm(orig[n]) != norm(dist[n]))
for n in bad:
    print('불일치:', n)
print(f'{len(orig)}개 중 일치 {len(orig) - len(bad)}개')
sys.exit(1 if bad else 0)
