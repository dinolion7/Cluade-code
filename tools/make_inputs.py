"""테스트용 입력 원문(AI 1차 각색 초안 형태)을 주제별로 합성한다. 실제 원문을 받으면 eval/inputs/를 교체한다."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from llm import claude

OUT = os.path.join(os.path.dirname(__file__), '..', 'eval', 'inputs')
TOPICS = {
    'C-세금': '프리랜서(3.3% 원천징수) 종합소득세 신고 — 단순경비율·기준경비율 구분, 5월 신고 기한, 홈택스 신고 경로, 환급',
    'D-고용노동': '권고사직 후 실업급여(구직급여) — 수급 요건, 이직확인서, 신청 절차, 지급액 상한·하한, 구직활동 인정',
    'G-임대차': '전세 계약 만료 시 보증금 반환 지연 — 임차권등기명령, 계약갱신요구권, 묵시적 갱신, 보증보험(HUG) 이행 청구',
    'IT-IT통신': '휴대폰 선택약정 25% 할인 vs 공시지원금 — 약정 기간, 위약금 구조, 자급제폰 가입, 재약정 시점',
    '자동차': '자동차보험 갱신 시 할증 — 사고 이력 등급, 3년 무사고 할인, 자기부담금, 다이렉트 보험 비교',
    '건강': '국가건강검진 결과 공복혈당 장애(100~125mg/dL) 판정 — 의미, 재검 시기, 생활관리, 당뇨 확진 기준, 단 갑작스러운 가슴 통증·호흡곤란 동반 시 응급 안내 필요',
}
SYSTEM = ('너는 네이버 지식인 질문을 리서치해서 블로그용 1차 초안을 쓰는 AI다. 질문자의 상황을 출발점으로, '
          '소제목(##)·불릿·짧은 표를 섞어 2000~3000자 분량의 정보형 초안을 쓴다. 보도자료·요약형 문장, '
          '"이번 확인 범위에서는 ~을 찾지 못했습니다" 같은 조사 메타코멘트도 1~2회 섞는다. '
          '제도명·기관명·수치·기한은 아는 범위에서 구체적으로 쓴다. 맨 앞에 원 질문(질문자 문장 그대로, 2~4문장)을 '
          '"[원 질문]" 아래에 적고, 이어서 "[1차 초안]" 아래에 초안을 쓴다.')

os.makedirs(OUT, exist_ok=True)
for name, theme in TOPICS.items():
    path = os.path.join(OUT, name + '.txt')
    if os.path.exists(path):
        continue
    text, meta = claude('claude-sonnet-5-5', SYSTEM, f'주제: {theme}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text.strip())
    print(name, meta)
