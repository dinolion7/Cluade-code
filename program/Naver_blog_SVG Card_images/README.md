# 블로그 이미지 자동화

정책뉴스 블로그의 썸네일과 소제목 인포그래픽을 만드는 도구 모음입니다.

**원칙: 그림은 AI가, 글자는 코드가.**
이미지 생성 도구에는 글자 없는 장면만 맡기고, 한국어가 들어가는 부분은 모두 코드로 만듭니다.
그래서 한글이 깨지지 않고, 시리즈 톤이 글마다 똑같이 유지됩니다.

## 폴더 구성

| 폴더 | 내용 |
|---|---|
| `prompt_c/` | 정책뉴스 프롬프트 C V18, 복지로 프롬프트 ⑦ V7: 본문 분석 → 썸네일 장면 프롬프트 + JSON 설계도 |
| `cards/make_cards.py` | JSON 설계도를 읽어 썸네일 타이틀·인포그래픽 PNG를 만드는 코드 |
| `cards/icons.py` | 아이콘 47종 |
| `cards/examples/` | 7개 글 설계도(정책뉴스 6 + 복지로 학교우유급식)와 썸네일 배경 예시 |
| `cards/samples/` | 결과 이미지 예시 |
| `fonts/` | Noto Sans KR 웹폰트 (SIL Open Font License, `fonts/OFL.txt`) |
| `svg_scenes/` | 초기 실험: 책상 장면·소제목 장면·탈것 등을 SVG로 그린 스크립트 |

## 작업 순서

```
1. 본문 + 프롬프트 C V18 → 클로드 → 썸네일 장면 프롬프트 + JSON 설계도
2. 장면 프롬프트 → 이미지 생성 도구(퍼플렉시티 등) → 00_thumbnail_scene.png 로 저장
3. JSON을 spec.json 으로 저장 (2번 이미지와 같은 폴더)
4. python make_cards.py spec.json  → 같은 폴더의 out/ 에 PNG 완성
```

## 준비 (최초 1회)

```bash
pip install playwright
playwright install chromium
```

## 실행 예시

```bash
cd blog-images/cards/examples
python ../make_cards.py 생계비계좌_spec.json
python ../make_cards.py table_timeline_sample.json
```

크롬 경로를 직접 지정해야 하면 `CHROME_PATH` 환경변수를 쓰고,
다른 폰트를 쓰려면 `FONT_CSS` 환경변수에 CSS 경로(URL)를 넣습니다.

## 레이아웃 13종

| 양식 | layout |
|---|---|
| 썸네일 (장면 + 타이틀, shape fade·wave·slant·wall) | `thumbnail` |
| 숫자 강조형 | `rows` |
| 목록형 | `list` |
| 체크리스트형 (번호·왼쪽 3단 가능) | `checks` |
| 그리드형 (3~6칸) | `grid` |
| 비교형 | `compare` |
| 전/후 비교형 | `before_after` |
| 분할 흐름형 | `split` |
| 절차형 | `steps` |
| 배지 행 (2027년·이후·장기) | `badges` |
| 타임라인형 | `timeline` |
| 계산표형 | `table` |
| 벤토형 | `bento` |

공통 옵션: `card_tone: "pastel"`(카드 바탕 순환), `icon_style: "plain"`, `footers`(하단 카드 good·info·point·danger·unknown).
옵션 전체 목록과 JSON 형식은 `prompt_c/정책뉴스_C_이미지기획_V18.md`에 있습니다.

## 이미지 슬롯

사람·풍경처럼 코드로 못 그리는 그림은 GPT로 글자 없이 그려서 설계도와 같은 폴더에 `slot_01.png`처럼 저장하고,
설계도의 `"image": "slot_01.png"`로 넣습니다. 파일이 없으면 함께 적힌 `"icon"`으로 자동 대체됩니다.

## 썸네일 장면 모드

| 모드 | 언제 | 장면 프롬프트 |
|---|---|---|
| 웹 (기본) | GPT·퍼플렉시티 웹, 고급 모델 | 8~12문장으로 자세히 |
| API | 완전 자동화, 저가 모델 | 5~6문장, 글자를 부르는 단어·소품 금지 |

## 아이콘 47종

`cards/icons.py`에 있습니다. 달력은 `calendar_red:2`(이틀 강조), `calendar_green:even`(짝수일 무늬)처럼 변형할 수 있습니다.
아이콘을 추가하면 `icons.py`의 `BODIES`와 프롬프트 C의 [아이콘 목록]을 함께 고칩니다.

## 시리즈 (정책뉴스 / 복지로)

설계도 JSON 맨 위의 `"series"`로 색이 바뀝니다. 레이아웃·아이콘·글꼴은 같습니다.

| series | 메인 색 | 포인트 색 | 특징 |
|---|---|---|---|
| `policy` (기본) | 딥 네이비 #1F3A5F | 그린 #2E9E6B | 정책뉴스(**새로 바뀌는 정책**): 썸네일 배지 = 그린 테두리 알약형 `"새 정책 · ○○ 시행"` |
| `welfare` | 딥 틸 #1D5C5A | 골드 #C9A227 | 복지로(**지금 적용 중인 정책**): 타이틀 바 왼쪽 골드 띠, 썸네일 배지 = 골드 리본형 `"○○○○ ○○ 안내"` |

썸네일 배지는 `"badge"`에 글자만 넣으면 시리즈에 맞는 모양(알약/리본)으로 그려집니다. 모양을 바꾸려면 `"badge_style": "pill"|"ribbon"`.

예시: `cards/examples/학교우유급식_spec.json`(실제 글), `cards/examples/복지로_예시_spec.json`(자리 표시)

## 색 (정책뉴스 팔레트)

| 이름 | 색 | 용도 |
|---|---|---|
| navy | #1F3A5F | 타이틀 바 |
| green | #2E9E6B | 포인트 단어 |
| amber | #E8A33D | 금액·숫자·날짜 |
| coral | #E05A47 | 주의 |
| charcoal | #2B2B2B | 카드 위 글자 |
| (바탕) | #F6F1E7 | 아이보리 |
