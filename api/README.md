# 코드(API)로 쓸 때 — `api/rewrite.py` (참고용)

> 웹 사용이 기본이다. 이 코드는 나중에 프로그램으로 옮길 때 참고하는 예시이며, 실제 API 호출로는 아직 검증하지 않았다.

웹 사용이 기본이고, 이 폴더는 API로 돌릴 때만 필요하다. 프롬프트는 웹과 똑같이 `prompts/dist/*.txt`를 쓴다.
프롬프트를 고치면 웹과 API에 함께 반영된다(`python3 tools/build.py`로 dist를 다시 만들면 됨).

## 웹과 달라지는 부분

| | 웹 | API (`rewrite.py`) |
|---|---|---|
| 프롬프트 전달 | 메시지에 붙여넣기 / 프로젝트 지침 | system 메시지로 보냄 |
| 원문 전달 | 같은 메시지 아래에 붙여넣기 | user 메시지로 보냄 |
| 반복 비용 | 해당 없음 | Claude: 프롬프트를 캐시해서 5분 안에 같은 프롬프트를 다시 쓰면 그 부분 입력 비용이 약 1/10. GPT: 같은 앞부분을 자동 캐시 |
| 결과 꺼내기 | 코드블럭 복사 버튼 | 코드블럭을 자동으로 벗기고 인용 마커(【…】, [1] 등)를 지움. 건강 편집 결과는 "=== 원고 ==="~"=== 끝 ===" 사이만 꺼냄 |
| 형식 확인 | 눈으로 확인 | 제목·볼드·표·리스트·해시태그·질문형 소제목(B·GPT)을 자동 점검해 경고 출력 |
| 건강 3단계 | 대화 3개를 손으로 이어 감 | 각색 → 검수(웹 검색 도구) → 편집 → 재검수까지 한 번에. 최대 2회 돌아도 통과 못 하면 "재검수 필요"로 멈춤 |

## 준비

```bash
pip install anthropic openai
export ANTHROPIC_API_KEY=...   # Claude를 쓸 때
export OPENAI_API_KEY=...      # GPT를 쓸 때
```

## 사용 예

```bash
# 일반 주제
python3 api/rewrite.py --persona A --topic C-세금 --model claude --input 원문.txt --out 결과.md
python3 api/rewrite.py --persona B --topic D-고용노동 --model gpt --input 원문.txt --out 결과.md

# 건강 3단계 (결과.md + 단계별 기록 결과.md.log.md)
python3 api/rewrite.py --persona A --topic 건강 --model claude --input 원문.txt --health --out 결과.md

# 비용 없이 어떤 요청이 나가는지만 확인
python3 api/rewrite.py --persona A --topic C-세금 --model gpt --input 원문.txt --dry-run
```

주제 이름은 파일 이름 그대로: `B-대출신용`, `C-세금`, `D-고용노동`, `E-연금복지`, `F-행정절차`, `G-임대차`, `IT-IT통신`, `교육`, `자동차`, `건강`.

## 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--claude-model` | `claude-sonnet-5-5` | Claude 모델. Haiku는 테스트에서 원문에 없는 내용을 지어내 권하지 않는다 |
| `--gpt-model` | `gpt-4.1-mini` | GPT 모델. 테스트에서는 `gpt-5.4-mini`가 창작이 적고 글이 더 자연스러웠다(글 1건 약 2센트) |
| `--retry` | 꺼짐 | 형식 점검에 걸리면 위반 항목을 알려 주고 1회 다시 요청한다. **호출 1회분 비용이 추가된다** |
| `--dry-run` | 꺼짐 | API를 부르지 않는다 |

## 글 1건당 대략 비용 (테스트 실측 기준, 캐시 미적용)

| 모델 | 1건 |
|---|---|
| claude-sonnet-5-5 (기본 설정) | 약 $0.15 |
| gpt-5.4-mini | 약 $0.018 |
| gpt-4.1-mini | 약 $0.008 |

- Sonnet 비용의 대부분은 모델이 내부적으로 생각하는 출력 토큰이다. 생각 깊이(effort)를 낮추면 싸지지만 형식 규칙을 많이 놓쳐서 기본값을 유지한다.
- 건강은 각색 + 검수(웹 검색 비용 별도) + 편집이라 일반 글의 3~5배 정도 든다.

## 아직 실제 호출로 확인하지 않은 부분

- 이 코드는 API 비용을 쓰지 않기 위해 `--dry-run`으로만 확인했다.
- 처음 쓸 때는 글 1건으로 일반 주제를 먼저 돌려 보기를 권한다(Claude 약 $0.15, GPT 약 $0.01).
- 특히 GPT 검수 단계는 Responses API의 웹 검색 도구를 쓴다. 계정에서 그 도구를 쓸 수 없으면 오류가 난다. 그때는 검수만 Claude로 돌리거나 웹에서 하면 된다.
