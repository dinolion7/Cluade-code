# 지식인 관리 프로그램

`kin_manager.py` — 사용자가 쓰는 지식인 관리 프로그램(tkinter, Windows). 받은 파일 이름은 `…GUI…2026-09-28…Final_Ver_9.28.py`이고, 저장소에서는 영문 이름으로 둔다. 줄바꿈은 원본 그대로 CRLF.

- 첫 커밋은 받은 원본 그대로, 다음 커밋부터 수정분이다. `git log -p program/kin_manager.py`로 바뀐 내용을 볼 수 있다.
- 변경 이력은 파일 맨 위 docstring(`[변경 이력 요약]`)에 기존 형식대로 적는다.
- 정책뉴스·복지로 프로그램은 다른 대화에서 다룬다. 여기서는 지식인만 다룬다.

## 탭 구성 (Ver9.28)

1)질문수집 · 2)질문적합분석(클로드) · 3)퍼플렉시티 수집 · 4)퍼플렉시티 자료검증(클로드) · 5)API설정 · 6)자동각색(API) · 7)1차 각색 · 8)2차 각색 · 9)썸네일/인포그래픽 · 10)통합 키워드 등록 · 11)주제 키워드 등록 · 12)포스팅 이력관리

- 최종 글 저장은 8)2차 각색의 `save_web_2nd_result` 한 곳뿐이다. 흐름: 붙여넣기 → "✅ 최종 확정"(H1 교체 + GPT 게시판 판정, 백그라운드) → "저장"(`_strip_ai_ui_chrome` → 포스팅DB 중복 차단 → MD 저장 → 포스팅DB·게시판목록.txt 기록).
- API: `Naver_blog_config_지식인.json`의 키로 OpenAI·Gemini·Claude 클라이언트를 만든다. 지금 실제로 쓰는 곳은 주제 분류와 게시판 판정이다(`gpt-4.1-mini-2025-04-14`, temperature 0).
- 포스팅 프로그램은 MD를 그대로 읽고, 빈 줄 하나를 문단 구분으로 쓴다.

## 알려진 문제 (고치지 않음 — 사용자 결정 대기)

- `_on_notebook_tab_changed`의 `refresh_map` 키 `"2)질문 상세분석"`이 실제 탭 이름 `"2)질문적합분석(클로드)"`과 달라, 2)탭은 다른 탭에 다녀와도 목록이 자동으로 새로고침되지 않는다.
- 호출하는 곳이 없는 코드: 워터마크 함수(`composite_anchor_on_image` 등), `_prefilter_*` 4개, `open_perplexity_question_picker`, `_copy_web2nd_title`, `_get_kin_thumbnail_group`·`_get_kin_thumbnail_template_path`, `select_classifier_file`.
