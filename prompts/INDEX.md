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
| 10 | A | B 대출·카드·보험·투자 | Claude Sonnet | A_B-대출신용_ClaudeSonnet.txt |
| 11 | A | C 세금 | Claude Sonnet | A_C-세금_ClaudeSonnet.txt |
| 12 | A | D 고용·노동 | Claude Sonnet | A_D-고용노동_ClaudeSonnet.txt |
| 13 | A | E 연금·복지 | Claude Sonnet | A_E-연금복지_ClaudeSonnet.txt |
| 14 | A | F 행정절차·법률 | Claude Sonnet | A_F-행정절차_ClaudeSonnet.txt |
| 15 | A | G 부동산·임대차 | Claude Sonnet | A_G-임대차_ClaudeSonnet.txt |
| 16 | A | IT 통신·구독·약관 | Claude Sonnet | A_IT-IT통신_ClaudeSonnet.txt |
| 17 | A | (코드 미확인) 교육·입시·장학금 | Claude Sonnet | A_X1-교육_ClaudeSonnet.txt |
| 18 | A | (코드 미확인) 자동차·보험·정비 | Claude Sonnet | A_X2-자동차_ClaudeSonnet.txt |
| 19 | A | H 건강 — 각색 | Claude Sonnet | A_H-건강_ClaudeSonnet.txt |
| 20 | A | H 건강 — 1단계 팩트체크 검수(웹 검색) | Claude Sonnet | A_H-건강-1검수_ClaudeSonnet.txt |
| 21 | A | H 건강 — 2단계 검수 반영 편집(분기 A/B/C) | Claude Sonnet | A_H-건강-2편집_ClaudeSonnet.txt |

건강 주제만 3단계 파이프라인: 각색 → 검수 보고서 → 보고서 반영 편집(필요 시 재검수)
| 22 | B | B 대출·서민금융 | GPT | B_B-대출신용_GPT.txt |
| 23 | B | C 세금 | GPT | B_C-세금_GPT.txt |
| 24 | B | D 고용·노동 | GPT | B_D-고용노동_GPT.txt |
| 25 | B | E 연금·복지 | GPT | B_E-연금복지_GPT.txt |
| 26 | B | F 행정절차 | GPT | B_F-행정절차_GPT.txt |
| 27 | B | G 임대차 | GPT | B_G-임대차_GPT.txt |
| 28 | B | IT 통신·구독·계정 | GPT | B_IT-IT통신_GPT.txt |
| 29 | B | 교육·입시·장학금 | GPT | B_X1-교육_GPT.txt |
| 30 | B | 자동차·보험·정비 | GPT | B_X2-자동차_GPT.txt |
| 31 | A | B 금융·대출·투자 | GPT | A_B-대출신용_GPT.txt |
| 32 | A | C 세금 | GPT | A_C-세금_GPT.txt |
| 33 | A | D 채용·고용·노동 | GPT | A_D-고용노동_GPT.txt |
| 34 | A | E 사회보장·복지·연금 | GPT | A_E-연금복지_GPT.txt |
| 35 | A | F 법률·행정·민원 | GPT | A_F-행정절차_GPT.txt |
| 36 | A | G 부동산·임대차 | GPT | A_G-임대차_GPT.txt |
| 37 | A | IT 통신·구독 | GPT | A_IT-IT통신_GPT.txt |
| 38 | A | 교육·입시 | GPT | A_X1-교육_GPT.txt |
| 39 | A | 자동차·보험·정비 | GPT | A_X2-자동차_GPT.txt |
