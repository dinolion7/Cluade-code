"""[참고용] 각색 프롬프트를 API로 쓰기 위한 도구. 웹 사용이 기본이며, 나중에 프로그램에 붙일 때 참고하는 예시 코드다.

웹과 다른 점은 아래 네 가지뿐이다. 프롬프트 본문은 웹과 같은 prompts/dist/*.txt 를 그대로 쓴다.
  1. 프롬프트는 system, 원문은 user 메시지로 보낸다.
  2. Claude는 프롬프트에 캐시 표시를 붙여 같은 프롬프트로 연속 처리할 때 입력 비용을 줄인다.
     (GPT는 1,024토큰 이상 같은 앞부분을 자동 캐시하므로 따로 할 일이 없다.)
  3. 응답의 코드블럭을 벗기고 인용 마커를 지운 뒤, 형식 규칙을 자동 점검한다(tools/rulecheck.py).
  4. 건강은 ①각색 → ②검수(웹 검색) → ③편집 → (필요하면) 재검수를 순서대로 잇는다.

사용 예
  python3 api/rewrite.py --persona A --topic C-세금 --model claude --input 원문.txt
  python3 api/rewrite.py --persona B --topic D-고용노동 --model gpt --input 원문.txt --out 결과.md
  python3 api/rewrite.py --persona A --topic 건강 --model claude --input 원문.txt --health
  python3 api/rewrite.py ... --dry-run      # API를 부르지 않고 보낼 요청만 출력(비용 0)

키: ANTHROPIC_API_KEY / OPENAI_API_KEY 환경변수. 모델은 --claude-model / --gpt-model 로 바꾼다.
"""
import argparse, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from rulecheck import check  # noqa: E402

DEFAULT_CLAUDE = 'claude-sonnet-5-5'
DEFAULT_GPT = 'gpt-4.1-mini'          # 테스트상 품질은 gpt-5.4-mini가 더 나았다(README 참고)
FILE_MODEL = {'claude': 'ClaudeSonnet', 'gpt': 'GPT'}
VERDICTS = ('재작성 권장', '보완 후 게시 권장', '게시 가능')


# ---------- 프롬프트 ----------
def prompt_path(persona, topic, family, stage=None):
    name = f'{persona}_{topic}' + (f'-{stage}' if stage else '') + f'_{FILE_MODEL[family]}.txt'
    path = os.path.join(ROOT, 'prompts', 'dist', name)
    if not os.path.exists(path):
        raise SystemExit(f'프롬프트 파일이 없습니다: prompts/dist/{name}')
    return path


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


# ---------- 모델 호출 ----------
class Caller:
    def __init__(self, family, claude_model, gpt_model, dry_run=False):
        self.family, self.dry = family, dry_run
        self.model = claude_model if family == 'claude' else gpt_model
        self.usage = []
        self._client = None

    def client(self):
        if self._client is None:
            if self.family == 'claude':
                import anthropic
                self._client = anthropic.Anthropic(max_retries=3)
            else:
                import openai
                self._client = openai.OpenAI(max_retries=3, timeout=600)
        return self._client

    def __call__(self, system, user, web_search=False):
        if self.dry:
            print(json.dumps({'model': self.model, 'web_search': web_search,
                              'system': system[:200] + f'… ({len(system)}자)',
                              'user': user[:200] + f'… ({len(user)}자)'}, ensure_ascii=False, indent=1))
            return '```markdown\n(dry-run)\n```'
        return self._claude(system, user, web_search) if self.family == 'claude' else self._gpt(system, user, web_search)

    def _claude(self, system, user, web_search):
        # 프롬프트(system)를 캐시 블록으로 보낸다: 같은 프롬프트를 5분 안에 다시 쓰면 입력 비용이 약 1/10.
        kw = dict(model=self.model, max_tokens=32000,
                  system=[{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}])
        if web_search:
            kw['tools'] = [{'type': 'web_search_20260209', 'name': 'web_search', 'max_uses': 20}]
        messages = [{'role': 'user', 'content': user}]
        for _ in range(6):  # 웹 검색이 길어지면 pause_turn으로 끊기므로 이어서 요청한다
            with self.client().messages.stream(messages=messages, **kw) as s:
                msg = s.get_final_message()
            self.usage.append(msg.usage.model_dump())
            if msg.stop_reason != 'pause_turn':
                break
            messages = [messages[0], {'role': 'assistant', 'content': msg.content}]
        if msg.stop_reason == 'refusal':
            raise RuntimeError('모델이 요청을 거절했습니다(stop_reason=refusal).')
        return ''.join(b.text for b in msg.content if b.type == 'text')

    def _gpt(self, system, user, web_search):
        if web_search:
            # 검수 단계: Responses API의 웹 검색 도구 사용
            r = self.client().responses.create(model=self.model, instructions=system, input=user,
                                               tools=[{'type': 'web_search'}])
            self.usage.append(r.usage.model_dump() if r.usage else {})
            return r.output_text
        r = self.client().chat.completions.create(
            model=self.model, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}])
        self.usage.append(r.usage.model_dump() if r.usage else {})
        return r.choices[0].message.content


# ---------- 후처리 ----------
CITATION = re.compile(r':contentReference\[[^\]]*\]\{[^}]*\}|【[^】]*】|\^\[[^\]]*\]|\[\d+\]|turn\d+search\d+')


def clean(text):
    """웹처럼 코드블럭으로 온 응답에서 본문만 꺼내고, 남은 인용 마커를 지운다."""
    m = re.search(r'```(?:markdown|md)?\n(.*?)```', text, re.S)
    body = m.group(1) if m else text
    return re.sub(r'[ \t]+\n', '\n', CITATION.sub('', body)).strip() + '\n'


def manuscript(edit_output):
    """편집 결과(코드블럭 하나: 상태 줄 / === 원고 === / 원고 / === 끝 === / 수정 내역)에서 원고만 꺼낸다."""
    m = re.search(r'=== 원고 ===\n(.*?)\n=== 끝 ===', edit_output, re.S)
    return (m.group(1).strip() + '\n') if m else edit_output


def style_of(persona, family):
    return f'{persona}_{"Claude" if family == "claude" else "GPT"}'


def report(persona, family, text):
    result, length = check(style_of(persona, family), text)
    failed = [k for k, ok in result.items() if not ok]
    return failed, length


# ---------- 일반 주제 ----------
def rewrite(call, persona, topic, source, retry=False):
    system = read(prompt_path(persona, topic, call.family))
    out = clean(call(system, source))
    if call.dry:
        return out, []
    failed, _ = report(persona, call.family, out)
    if failed and retry and not call.dry:
        # 형식 위반이 있을 때만 1회 재요청(비용 1회분 추가). 기본은 꺼져 있다.
        fix = ('아래 원문으로 다시 작성하되, 직전 결과에서 다음 형식 규칙을 어겼으니 반드시 지켜라: '
               + ', '.join(failed) + '\n\n' + source)
        out2 = clean(call(system, fix))
        if len(report(persona, call.family, out2)[0]) < len(failed):
            out, failed = out2, report(persona, call.family, out2)[0]
    return out, failed


# ---------- 건강 3단계 ----------
def verdict(review):
    head = review.split('## 검증 방식 요약')[0]
    for v in VERDICTS:
        if v in head:
            return v
    return None


def health(call, persona, source, max_rounds=2):
    log = []
    rewrite_prompt = read(prompt_path(persona, '건강', call.family))
    review_prompt = read(prompt_path(persona, '건강', call.family, '1검수'))
    edit_prompt = read(prompt_path(persona, '건강', call.family, '2편집'))

    draft = clean(call(rewrite_prompt, source))
    log.append(('①각색', draft))
    for rnd in range(1, max_rounds + 1):
        review = call(review_prompt, draft, web_search=True)
        v = verdict(review)
        log.append((f'②검수 {rnd}회차 — {v}', review))
        if v == '게시 가능' or call.dry:
            return draft, v, log
        user = (f'[검수 보고서]\n{review}\n\n[원고]\n{draft}\n\n[2차 각색 프롬프트 원문]\n{rewrite_prompt}')
        edited = call(edit_prompt, user)
        draft = manuscript(clean(edited))
        log.append((f'③편집 {rnd}회차', edited))
    # 마지막 편집본은 재검수를 한 번 더 거친 것이 아니므로 사람이 확인해야 한다
    return draft, '재검수 필요', log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--persona', required=True, choices=['A', 'B'])
    ap.add_argument('--topic', required=True, help='예: C-세금, D-고용노동, IT-IT통신, 교육, 자동차, 건강')
    ap.add_argument('--model', required=True, choices=['claude', 'gpt'])
    ap.add_argument('--input', required=True, help='원문 파일 경로')
    ap.add_argument('--out', help='결과 저장 경로(없으면 화면 출력)')
    ap.add_argument('--health', action='store_true', help='건강 3단계(각색→검수→편집) 실행')
    ap.add_argument('--retry', action='store_true', help='형식 위반 시 1회 재요청(비용 추가)')
    ap.add_argument('--dry-run', action='store_true', help='API를 부르지 않고 요청만 출력')
    ap.add_argument('--claude-model', default=DEFAULT_CLAUDE)
    ap.add_argument('--gpt-model', default=DEFAULT_GPT)
    a = ap.parse_args()

    call = Caller(a.model, a.claude_model, a.gpt_model, a.dry_run)
    source = read(a.input)
    if a.health:
        text, status, log = health(call, a.persona, source)
        print(f'[건강] 최종 상태: {status}', file=sys.stderr)
        if a.out:
            with open(a.out + '.log.md', 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(f'# {k}\n\n{v}' for k, v in log))
    else:
        text, failed = rewrite(call, a.persona, a.topic, source, a.retry)
        print('[형식 점검] ' + ('모두 통과' if not failed else '확인 필요: ' + ', '.join(failed)), file=sys.stderr)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print(text)
    if call.usage:
        print('[사용량] ' + json.dumps(call.usage, ensure_ascii=False), file=sys.stderr)


if __name__ == '__main__':
    main()
