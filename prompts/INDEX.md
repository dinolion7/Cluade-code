# 원본 프롬프트 목록

파일명 규칙: `{페르소나}_{주제코드}-{주제}_{모델}.txt`

- 페르소나 A = 기초(초기) 버전, 원본 파일명에 접두어 없음
- 페르소나 B = 나중에 추가한 타입·버전, 원본 파일명 접두어 `B-`
- 주제 10개: B 대출신용, C 세금, D 고용노동, E 연금복지, F 행정절차, G 임대차, IT, 교육, 자동차, 건강
- 누락된 조합(예: B·건강)은 같은 주제의 반대 페르소나와 같은 페르소나의 다른 주제를 참조해 새로 만든다
(업로드 시 파일명의 한글이 `_`로 깨져서, 주제명은 프롬프트 본문 [역할] 기준으로 복원함)

| # | 페르소나 | 주제 | 모델 | 파일 |
|---|---|---|---|---|
| 1 | B | B 대출·신용·서민금융·투자 | Claude Sonnet | B_B-대출신용_ClaudeSonnet.txt |
| 2 | B | C 세금(종소세·연말정산·양도·증여) | Claude Sonnet | B_C-세금_ClaudeSonnet.txt |
| 3 | B | D 고용·노동 | Claude Sonnet | B_D-고용노동_ClaudeSonnet.txt |
| 4 | B | E 연금·복지 | Claude Sonnet | B_E-연금복지_ClaudeSonnet.txt |
| 5 | B | F 행정절차(기한·과태료·처분) | Claude Sonnet | B_F-행정절차_ClaudeSonnet.txt |
| 6 | B | G 전월세·임대차 | Claude Sonnet | B_G-임대차_ClaudeSonnet.txt |
| 7 | B | IT 통신·구독·기기·계정 | Claude Sonnet | B_IT-IT통신_ClaudeSonnet.txt |
| 8 | B | (코드 미확인) 교육·입시·장학금 | Claude Sonnet | B_X1-교육_ClaudeSonnet.txt |
| 9 | B | (코드 미확인) 자동차·보험·정비 — 화자명 "차박사" | Claude Sonnet | B_X2-자동차_ClaudeSonnet.txt |
