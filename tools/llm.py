"""Claude / GPT 호출 공통 함수. 키는 환경변수(ANTHROPIC_API_KEY) 또는 프록시 자격 증명(OpenAI)으로만 받는다."""
import time
import anthropic
import openai

# 1M 토큰당 USD (입력, 출력). GPT 단가는 OpenAI 공개 가격 기준 참고값.
PRICE = {
    'claude-sonnet-5-5': (2.00, 10.00),
    'claude-haiku-4-5': (1.00, 5.00),
    'claude-opus-5-5': (4.00, 20.00),
    'gpt-4.1-mini': (0.40, 1.60),
    'gpt-4.1': (2.00, 8.00),
    'gpt-5-mini': (0.25, 2.00),
    'gpt-5.4-mini': (0.75, 4.50),
}

_anthropic = None
_openai = None


def claude(model, system, user, max_tokens=16000, thinking=None, effort=None):
    global _anthropic
    _anthropic = _anthropic or anthropic.Anthropic(max_retries=4)
    kw = {}
    if thinking:
        kw['thinking'] = thinking
    if effort:
        kw['output_config'] = {'effort': effort}
    t = time.time()
    with _anthropic.messages.stream(model=model, max_tokens=max_tokens, system=system,
                                    messages=[{'role': 'user', 'content': user}], **kw) as s:
        msg = s.get_final_message()
    text = ''.join(b.text for b in msg.content if b.type == 'text')
    return text, {'model': model, 'stop': msg.stop_reason, 'in': msg.usage.input_tokens,
                  'out': msg.usage.output_tokens, 'sec': round(time.time() - t, 1)}


def gpt(model, system, user, reasoning_effort=None):
    global _openai
    # 키는 클라우드 환경의 프록시 자격 증명이 붙여 준다 (값은 자리표시)
    _openai = _openai or openai.OpenAI(api_key='set-by-proxy', max_retries=4, timeout=600)
    kw = {'reasoning_effort': reasoning_effort} if reasoning_effort else {}
    t = time.time()
    # 스트리밍으로 받아 긴 추론 중 연결이 끊기지 않게 한다
    stream = _openai.chat.completions.create(model=model, stream=True, stream_options={'include_usage': True},
                                             messages=[{'role': 'system', 'content': system},
                                                       {'role': 'user', 'content': user}], **kw)
    parts, finish, usage = [], None, None
    for ch in stream:
        if ch.usage:
            usage = ch.usage
        for c in ch.choices:
            parts.append(c.delta.content or '')
            finish = c.finish_reason or finish
    return ''.join(parts), {'model': model, 'stop': finish, 'in': usage.prompt_tokens,
                            'out': usage.completion_tokens, 'sec': round(time.time() - t, 1)}


def cost(meta):
    pin, pout = PRICE.get(meta['model'], (None, None))
    if pin is None:
        return None
    return (meta['in'] * pin + meta['out'] * pout) / 1e6
