# 각색 프롬프트 모듈 관리

## 폴더
- `original/` — 받은 원본 그대로 (수정 금지, 회귀 비교 기준). 목록은 `INDEX.md`
- `src/` — 편집하는 곳
  - `src/{페르소나}_{모델}/base.txt` — 그 스타일의 공통 본문. `<<<slot NNN>>>` 자리에 주제별 내용이 들어감
  - `src/{페르소나}_{모델}/topics/{주제}.txt` — 주제별 슬롯 내용 (`<<<slot NNN>>>` 표시 아래 줄들)
  - `src/standalone/` — 아직 모듈화하지 않은 단독 프롬프트 (건강 3종)
- `dist/` — 조립 결과 (자동 생성, 직접 수정하지 않음). 실제 사용은 이 파일

## 명령
```
python3 tools/build.py    # src → dist 조립
python3 tools/verify.py   # dist가 original과 같은지 확인 (CRLF/LF 차이 무시)
```
`tools/split.py`는 original → src 초기 분리용(1회성)이다. 다시 돌리면 src 편집 내용이 덮어써진다.

## 진행 단계
1. 원문 그대로 분리 + 원본 재현 검증 ← 현재 (42개 전부 일치)
2. 중복·누락·불일치 정리, B의 "스타일 A와 다르게" 문구를 자기완결형으로 전환
3. 축약
4. 원본 vs 수정본 실제 출력 비교 테스트
5. 누락 조합(B·건강 Claude/GPT) 생성
