"""
[변경 이력 요약]
※ Ver7.19까지는 이 블록 없이 관리되어, 아래 과거 항목은 코드 곳곳의 인라인 주석을
  바탕으로 사후 복원한 것이라 일부 세부사항은 누락되어 있을 수 있음. Ver7.20부터는
  이 블록에 계속 이어서 기록.
※ 2026-09-28: 분량이 1900줄까지 늘어나 대폭 압축함. 이미 코드에서 완전히 제거된
  기능(다중질문검색/종합완성판 파이프라인, 대안 후보 생성 등)의 상세 개발·디버깅
  서술은 삭제하거나 한 줄로 축약했고, 지금도 코드에 남아있는 기능은 버전·날짜와
  최종 동작(net effect)만 남기고 설계 과정·시행착오는 생략함.

- Ver7.05: 썸네일 스타일 템플릿을 별도 폴더가 아닌 기존 사용 폴더에서 관리하도록 변경
- Ver7.06: "4)1차각색(웹)→저장" 기능 추가
- Ver7.07: 중복체크 warn/danger 임계값 분리(경고 50%↑/위험 70%↑), 저장 전 미리보기용
  중복체크 추가
- Ver7.08: 사전 필터링(질문 선별) 기능 신설, 상단 "주제 선택"과 각 탭 간 주제 선택
  동기화 로직 추가
- Ver7.09: 클로드 최종 검토 결과에서 [SELECTED_START]~[SELECTED_END] 구간 우선 파싱
- Ver7.10: 좌우분할 UI로 다수 탭 재구성, 탭별 프롬프트/모델 매핑 설정 팝업 다수 추가
- Ver7.13: hard_match 강제판정 로직 신설(제목 첫 어절+숫자 겹침), 네이버 검색 API
  (지식인) 공용 클라이언트 및 전용 탭 신설(이 탭 자체는 이후 재편되어 결국 삭제됨 -
  하단 Ver7.20 항목 참고)
- Ver7.14~7.15: hard_match 오탐 실측 반영 - 연도 단독 표기, 회/배/학년 등 범용
  카운터 단위를 숫자 겹침 판정에서 제외
- Ver7.16: 중복 판정 시 실제로 겹치는 연속 부분열을 근거 문구로 추출해 함께 표시
- Ver7.17: 좌우분할 탭 5곳 공용 "사용" 셀 갱신 헬퍼 신설, 완료 표시 시점을 저장
  시점으로 통일, 썸네일 프롬프트 주제별 매핑 추가
- Ver7.19: 프롬프트 파일(10개 도메인 카테고리) 구분자/출력 코드블럭 형식 통일

- Ver7.20 (2026-07-19) ~ Ver7.89 (2026-08-20): "🔍 네이버 API 검색"(이후 "다중질문
  검색")에 지식인 질문 여러 개를 묶어 하나의 글로 만드는 "종합완성판" 8단계 파이프
  라인(자동수집→수동상세수집→글감분석/검증→1·2차각색→저장→썸네일/인포그래픽→워터
  마크)을 Ver7.20에서 처음 만든 뒤, 수집 방식(붙여넣기→비로그인 크롬 자동수집→네이버
  내부 API 직접 호출)과 각 단계 UI를 수십 차례에 걸쳐 반복 재설계함. 2026-09-25에
  이 파이프라인 전체(탭, 서브탭 8개, 관련 _napi_* 함수와 프롬프트/설정 매핑)가 코드
  에서 완전히 삭제됨 - 더 이상 코드에 없음. (옛 기록 조회용으로 남겨졌던 "11)포스팅
  이력관리"의 "종합완성판만 보기" 체크박스는 2026-09-26에 별도로 삭제됨 - 하단 참고.)

- Ver7.35, 7.40, 7.54, 7.55, 7.71, 7.78, 7.89: "9)통합 키워드" 탭 "📂 경제통합 자료
  모으기" 버튼 - 경제 세부카테고리(경제-A~G) 폴더의 완성 MD/이미지를 "경제통합"
  폴더로 모으는 기능을 여러 차례 수정. 최종 동작: final_articles 하위 항목(폴더/
  파일)을 원본 형태 그대로 경제통합/오늘날짜/perplexity_collected_final_articles/
  로 이동(shutil.move)하고, 그 주제의 최종본을 하나라도 옮겼으면 그 주제 아래 모든
  날짜 폴더(중간산출물만 남은 폴더 포함)를 통째로 삭제. 경제-A~G "카테고리 폴더"
  자체(질문DB/포스팅DB 위치)는 삭제 대상이 아님. 이동 실패 항목은 개별 예외처리로
  로그/완료 팝업에 사유를 남기고 나머지 처리는 계속됨.

- Ver7.41, 7.42: "10)주제 키워드"(반자동 이식) 탭의 포스팅 폴더 복사(semi_copy_
  approved_files_to_markdown_folder) - 원본이 제목별 폴더면 폴더째 그대로 복사
  (shutil.copytree), 원본이 낱개 파일(MD+썸네일)이면 낱개 그대로 복사. 포스팅
  폴더 경로는 base_folder와 결합하지 않은 기존 상대경로 그대로 유지(다른 오토
  포스팅 프로그램들과 동일 폴더에서 실행된다는 전제).

- Ver7.44 (2026-07-30): "7)1차 각색"/"8)2차 각색" 좌측 하단 버튼줄에 "프롬프트만
  복사" 버튼 추가.

- Ver7.45, 7.46: 포스팅 중복 저장 방지 개선. check_posting_duplicate가 기존 기록의
  record_index를 함께 반환하도록 확장하고, 중복 경고창을 "취소"/"다른 글로 저장
  (중복 유지)"/"덮어쓰기(기존 기록 교체)" 3지선다로 분리("8)2차각색" 저장에 적용) -
  실수로 같은 글이 포스팅DB에 중복 등록되는 문제 해소. "11)포스팅 이력관리"에
  "🧹 중복 기록 일괄 정리" 버튼 신설 - 기존 중복 기록을 그룹으로 묶어 미리보기 후
  사람이 확인·실행해야만 삭제되는 방식(연쇄 중복도 한 그룹으로 묶음).

- Ver7.56 (2026-07-31): 포스팅 중복비교 엔진(extract_posting_core/check_posting_
  duplicate) 재설계 - 소제목(## ) 목록을 headings 필드로 추출해 소제목 자카드
  유사도(가중치 25)를 반영, 도입부/마무리 가중치는 낮추고 제목/숫자 가중치를
  재배분(합 100 유지). hard_match에 "제목 첫 어절 일치 + 소제목 자카드 0.6 이상"
  조건 추가 - 도입부·마무리만 고쳐 쓴 패러프레이징 글도 잡아냄. 옛 기록엔 headings가
  없을 수 있어 양쪽에 다 있을 때만 반영(하위호환).

- Ver7.57 (2026-07-31): 포스팅 저장 시 중복 차단 기준(%)을 하드코딩 70에서 사용자가
  조정 가능하게 변경("8)2차각색"에 30~100 스핀박스, ui_settings에 저장돼 재실행
  후에도 유지). 경고선(50%)은 고정, 조정 대상은 차단(danger) 기준선 하나뿐.

- Ver7.58 (2026-07-31): "⚙️ 썸네일 프롬프트 설정" 팝업 - 재미나이(Gemini) 변환
  프롬프트(D)를 전체 주제 공용 1개에서 주제별(11개) 지정으로 확장. 주제별 값이
  비어있으면 예전 공용값으로 자동 폴백(하위호환).

- Ver7.70: "⚙️ 썸네일 프롬프트 설정" 팝업에서 아직 개별 지정하지 않은 주제의
  프롬프트D 칸에 예전 공용값이 항상 미리 채워져 "저장이 안 되는 것처럼" 보이던
  화면 버그 수정 - 이제 실제 저장된 값만 보여주고(없으면 빈칸), 공용값 자동대체는
  실제 복사 시점에만 적용.

- Ver7.72: "11)포스팅 이력관리"에 "💰 경제(A~G) 모아보기" 체크박스 추가 - 경제
  세부주제 7개(경제-A~G, 실제로는 "경제통합" 블로그 하나로 운영)를 한 목록에
  모아 보여줌.

- Ver7.73: "8)2차 각색" 썸네일 버튼줄에 "📝 프롬프트만 복사"(스타일 템플릿 원문만,
  완성 본문 없이) 버튼 추가.

- Ver7.74, 7.75, 7.75 긴급수정: "7)1차 각색" 단계에 "🔍 사전 중복체크(참고용)"
  추가 - 2차 각색 전에 미리 값싸게 걸러냄(강제 차단 아님). 질문수집/질문상세분석
  단계에도 질문 core를 포스팅DB와 비교하는 check_question_vs_posting_duplicate
  신설(참고용 경고만). 이 작업 중 check_posting_duplicate 함수 선언 줄이 실수로
  삭제돼 NameError로 저장이 죽는 사고가 있었고 즉시 복구함(이후 함수 삽입 시
  anchor에 대상 함수의 def 줄을 반드시 포함하는 것으로 재발 방지).

- Ver7.76, 7.77: "3)퍼플렉시티 수집"/"4)퍼플렉시티 자료검증"/"7)1차 각색"/
  "8)2차 각색"에도 "🗑️ 선택 삭제"를 추가해 전 단계에 삭제 버튼을 일관되게 갖춤
  (각 탭은 자기 단계 산출물만 지우고 질문DB는 건드리지 않음). "2)질문 상세분석"
  목록에서 행을 클릭하면 원문을 미리보기 칸에 바로 보여주도록 개선.

- Ver7.79~7.81 (2026-08-19): "프롬프트만 복사"/"자료만 복사" 버튼들에, 같은
  채팅창을 여러 건에 걸쳐 재사용할 때 규칙이 느슨해지는 것을 막는 공용 안내 문구를
  추가(이후 탭이 완전히 분리되면서 Ver8.21에서 다시 단순한 공용 문구로 정리됨).

- Ver7.82, 7.83 (2026-08-19): 죽은 코드 정리 중 실제로는 다른 탭이 쓰는 헬퍼 함수
  9개를 함께 삭제해 "4)자료검증" 탭이 즉시 크래시하는 사고가 있었음 - 즉시 원복.
  이후 "self.메서드()" 호출 전수 대조 검증을 죽은 코드 삭제 절차에 추가.

- Ver7.84 (2026-08-19): "2)질문 상세분석"/"3)퍼플렉시티 수집"/"4)퍼플렉시티
  자료검증"에도 "프롬프트만 복사" 버튼 추가(7)/8)탭과 동일 패턴으로 통일).

- Ver7.85 (2026-08-20): "8)2차 각색"에 있던 썸네일/인포그래픽 생성 기능(프롬프트
  복사 4종+설정)을 독립된 "9)썸네일/인포그래픽" 탭으로 분리(create_thumbnail_tab).
  이후 탭 번호가 한 칸씩 밀림(10)통합 키워드/11)주제 키워드/12)포스팅 이력관리).

- Ver7.86, 7.87 (2026-08-20): 신설된 "9)썸네일/인포그래픽" 탭을 다른 좌우분할
  탭(2)/3)/4)/7)/8))과 동일한 좌(완성글 목록)/우(본문+버튼) 구조로 재구성 - 좌측
  목록 클릭 시 우측 본문칸에 자동으로 채워지고, 프롬프트/자료 복사 성공 시 좌측
  목록에 완료(✅) 표시가 남음. 탭 전환 새로고침 매핑 관련 버그도 함께 수정.

- Ver8.21~8.24 (2026-08-22~08-30): "9)썸네일/인포그래픽" 탭 UI 다듬기 - 제목 복사
  버튼을 이 탭으로 이동, 저장폴더 열기 버튼 추가, 사용여부 수동 토글 버튼 추가,
  프롬프트+자료/프롬프트만 복사 모두 완료 표시가 남도록 통일. _strip_ai_ui_chrome에
  코드펜스/구분선 찌꺼기 제거 로직 보강(언어 태그 붙은 펜스 포함).

- Ver8.30, 8.31 (2026-09-05): "8)2차 각색"에 제목선점 확인용 네이버 검색 버튼
  ("🔍 블로그tab 검색"/"🔍 통합검색", find_chrome_executable/open_naver_search_
  in_chrome, 복지로/정책뉴스 소스 이식) 추가 - 검색 전용 입력창(수정 가능, 실제
  저장 제목에는 영향 없음)의 현재 값을 그대로 검색어로 사용. extract_markdown_
  content의 코드펜스 제거 정규식을 언어 태그 붙은 펜스도 잡도록 보강, GPT
  싱크모드 인용 마커 제거 안전망을 저장 시점에도 추가.

- Ver8.32 (2026-09-05): "1)질문수집-수작업" 탭 저장 시에도 같은 누적 파일 안에서
  문자열 유사도 기반 중복 경고(90%↑) 추가 - 정식 판정은 여전히 "0-1)사전 필터링"
  단계 몫.

- Ver8.33 (2026-09-05): "11)주제 키워드" 탭에 사용자 지정 시작 기본 주제 저장
  기능("⭐ 이 주제를 시작 기본값으로 저장", env.txt의 semi_default_topic 키)
  추가, 관련 UI 레이아웃 정리.

- Ver9.06 (2026-09-06): "9)썸네일/인포그래픽" 탭에서 다른 탭에 갔다가 돌아오면
  우측 본문칸에 예전 글이 남아있던 버그 수정 - 탭 재진입 시 항상 빈 상태로
  초기화되고, 좌측 목록을 다시 클릭해야 채워지도록 함.

- Ver9.07 (2026-09-06): 저장 결과에 마크다운 하이퍼링크 각주(예: "[law.go]
  (https://...)")가 그대로 남는 문제 수정 - _strip_ai_ui_chrome/_napi_strip_
  citations 양쪽에 링크 문법 전체를 제거하는 정규식 추가.

- Ver9.08 (2026-09-12) ~ 2026-09-16: "8)2차 각색"에 네이버 검색광고 API
  (searchad.naver.com keywordstool) 기반 제목 후보 자동생성("🎯 대안 후보 생성",
  kin_generate_title_candidates/kin_fetch_ad_keyword_data 등) 기능을 신설한 뒤
  여러 차례 UI(라디오 후보 3개+직접입력, 검색/확정/복사 버튼, 사전체크 자동축약
  제안 등)와 로직을 재설계함. 2026-09-28에 이 기능(후보 3개 행 UI, 네이버 검색
  광고 API 설정 UI, 관련 함수/상수 전체)이 코드에서 완전히 제거됨 - "직접 입력으로
  확정" 행과 그 아래 검색 버튼들만 남음(하단 2026-09-28 항목 참고).

- 2026-09-25: "🔍 네이버 API 검색"(다중질문검색/종합완성판) 파이프라인 전체 삭제
  (탭·서브탭 8개, _napi_* 함수, 관련 프롬프트/설정 매핑, 전용 수집 크롬 인스턴스,
  전용 파서 함수 전부). 과거 기록 조회용 체크박스 일부는 남겨둠(위 Ver7.20 항목
  참고).

- 2026-09-26: "12)포스팅 이력관리"의 "🧩 전체 주제에서 종합완성판만 보기"
  체크박스와 관련 로직 전부 삭제(위 NAPI 삭제의 잔재 정리). "💰 경제(A~G)
  모아보기" 체크박스는 별개 기능이라 그대로 유지.

- 2026-09-27: (1) "8)2차 각색" 주제 콤보 옆 "각색모델" 표시가 상단 배너와
  어긋나던 버그 수정. "9)썸네일/인포그래픽" 우측 하단 버튼줄을 좌측 목록 아래로
  이동. (2) "11)주제 키워드 등록"에 게시판(카테고리) 자동 매칭 기능 신설 -
  Naver_blog_지식인_게시판설정.xlsx를 근거로 최종 처리 시 GPT가 제목/소제목/본문
  앞부분을 분석해 게시판 번호를 고르고, 확인 창(신뢰도 70 미만은 빨간색)에서
  확정한 값을 키워드 엑셀에 기록(semi_* 함수들). 설정이 없거나 기능을 끄면 예전
  방식(마지막 카테고리값 재사용)으로 폴백. (3) "8)2차 각색"에서 제목 확정 시 GPT가
  게시판을 자동 판정해 "게시판" 콤보에 채우고, 저장 시 포스팅DB 레코드에 board_
  number/board_name/board_conf/board_source로 기록(본문에는 넣지 않음). "11)주제
  키워드 등록"은 semi_lookup_saved_boards로 포스팅DB에서 저장값을 먼저 찾고, 없는
  글만 GPT로 새로 판정.

- 2026-09-28: [사이드카 파일 신설 + UI 개편 + 죽은 코드 정리 + changelog 압축]
  (1) 여러 컴퓨터에서 같은 base_folder를 나눠 쓸 때 게시판(카테고리) 배정값이
  컴퓨터마다 따로 갱신되는 문제를 해소하기 위해, perplexity_{모델}_final_
  articles/ 폴더마다 탭구분 텍스트 사이드카 파일 "게시판목록.txt"(제목+카테고리
  한 줄씩)를 두는 방식 신설(_kin_sidecar_read/write/upsert/remove/merge_into,
  _kin_find_final_articles_folder). save_web_2nd_result(저장)/
  _delete_db_manage_selected(삭제)/_reorganize_worker(경제통합 자료 모으기 병합)
  3곳에 연동 - 각 컴퓨터가 로컬 포스팅DB 없이도 사이드카 파일만으로 최신 게시판
  값을 주고받음.
  (2) "8)2차 각색" 탭 - "🎯 대안 후보 생성" 기능과 관련 후보 3개 행을 완전히
  제거하고 "직접 입력으로 확정" 행만 유지. 게시판 카테고리 버튼을 "✅ 최종 확정"
  버튼 우측으로 이동. 우측 패널의 캔버스/스크롤바를 제거(트리뷰는 자체 스크롤
  유지, height 14→20 확대).
  (3) 위 UI 개편으로 더 이상 쓰이지 않게 된 죽은 코드 제거 - 제목 후보 생성
  모듈 함수/상수 전체(kin_generate_title_candidates/kin_fetch_ad_keyword_data/
  _kin_ad_signature 등), 네이버 검색광고 API 설정 UI 및 관련 변수/메서드(_get_
  kin_ad_api_keys 등), _title_precheck_driver 헤드리스 크롬 정리 코드.
  (4) 이 changelog 자체를 1900줄에서 대폭 압축 - 이미 삭제된 기능(다중질문검색/
  종합완성판 파이프라인, 대안 후보 생성)의 상세 개발 서술을 삭제하고, 현재 코드에
  남아있는 기능 중심으로 재정리함.

- 2026-09-28 (2차): "11)주제 키워드 등록" 카테고리(B열) 기록을 게시판목록.txt(사이드카)
  기준으로 재설계. 최종 처리 시 선택한 주제/날짜 아래 perplexity_*_final_articles의
  사이드카에서 승인 제목의 번호를 그대로 B열에 기록(semi_category_map_from_sidecar).
  사이드카에 없는 제목/번호가 빈 글('기타' 저장분)은 B열을 빈칸으로 두고, 처리 완료 후
  팝업+로그로 제목 목록을 알림. 게시판 설정 엑셀 의존, GPT 자동 매칭 체크박스,
  포스팅DB 조회, "직전 카테고리 재사용" 폴백, 확인 창(semi_confirm_boards_dialog)과
  관련 함수(semi_match_boards/semi_lookup_saved_boards/semi_collect_article_texts)를
  11)탭에서 제거. 8)2차 각색의 게시판 판정(semi_load_board_config/semi_gpt_pick_board/
  semi_keyword_pick_board)은 그대로 유지.
"""
import re
import os
import sys
import json
import difflib
import urllib.request
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime
import time
import random
import pickle

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    SELENIUM_OK = True
except ImportError:
    SELENIUM_OK = False

# [Ver7.31 신규] 이미지 워터마크 가리기 탭(8번)용 - 정책뉴스 프로그램에서
# 이식. 없으면 그 탭만 안내 문구로 대체되고 나머지 프로그램 동작에는
# 영향 없음(pip install pillow).
try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

# 다른 오토포스팅 프로그램들과 동일 폴더에서 실행된다는 전제로 chrome_profile1/env.txt 경로 계산
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

# 작업 디렉토리를 BASE_DIR로 고정 - 상대경로 기본값들이 실행 방식과 무관하게 항상 프로그램 폴더 기준으로 해석되도록 함
os.chdir(BASE_DIR)

# ── IP/네트워크 체크 공용 설정 (메인/정책뉴스 프로그램과 동일한 env.txt 공유) ──
_ENV_CONFIG_CACHE = None

def _load_env_config():
    """공용 환경설정 파일 로드 (key=value 형식, 캐싱) - 다른 프로그램과 동일 파일 사용"""
    global _ENV_CONFIG_CACHE
    if _ENV_CONFIG_CACHE is not None:
        return _ENV_CONFIG_CACHE

    env = {}
    try:
        env_path = os.path.join(BASE_DIR, "Naver_blog_env_config", "env.txt")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, value = line.partition('=')
                env[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    except Exception:
        pass

    _ENV_CONFIG_CACHE = env
    return env

def get_env_value(key, default=""):
    """환경설정 값 조회 (없으면 default 반환)"""
    return _load_env_config().get(key, default)

def update_env_value(key, value):
    """env.txt 특정 키 값만 갱신 (없으면 추가, 있으면 교체) - 다른 프로그램과 동일 파일"""
    global _ENV_CONFIG_CACHE
    env_dir = os.path.join(BASE_DIR, "Naver_blog_env_config")
    os.makedirs(env_dir, exist_ok=True)
    env_path = os.path.join(env_dir, "env.txt")

    existing = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, _, v = line.partition('=')
                    existing[k.strip()] = v.strip()

    existing[key] = value

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# Naver 블로그 자동포스팅 환경설정\n\n")
        for k, v in existing.items():
            f.write(f"{k}={v}\n")

    _ENV_CONFIG_CACHE = None

def open_folder(path: str):
    """OS 기본 파일탐색기(또는 이미지 뷰어)로 폴더/파일을 연다.
    [Ver7.31 이식] 정책뉴스 프로그램의 동일 함수 그대로."""
    try:
        import subprocess
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("오류", f"폴더를 열 수 없습니다: {e}")

# ════════════════════════════════════════════════════════════
# [Ver7.31 이식] 이미지 워터마크 가리기 (앵커 이미지 합성)
# ════════════════════════════════════════════════════════════
# 정책뉴스 프로그램(TAB9)에서 그대로 이식. 재미나이(Gemini) 등 AI 이미지
# 생성 서비스가 우측 하단에 붙이는 워터마크 심볼은 직접 지우기 어렵다
# (주변 배경까지 같이 뭉개짐). 대신 그 자리를 별도 이미지(앵커 이미지 —
# 예: 인물 캐릭터)로 덮어 가리는 방식은 배경 손상 없이 간단하게 처리된다.
# PIL(Pillow)이 없으면 8번 탭 자체를 안내 문구로 대체하고, 이 영역의
# 함수들은 호출되지 않는다.

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
WM_OUTPUT_SUBFOLDER = "_워터마크가림"


def _wm_find_images(folder: str, recursive: bool) -> list:
    """대상 폴더에서 처리할 이미지 파일 경로 목록을 모은다.
    recursive=False면 folder 바로 안(1단계)만, True면 모든 하위 폴더까지 포함한다.
    합성 결과가 저장되는 WM_OUTPUT_SUBFOLDER는 재귀 스캔에서 항상 제외한다 —
    재실행 시 이미 처리된 결과물을 원본으로 오인해 또 처리하는 것을 막기 위함."""
    results = []
    if not os.path.isdir(folder):
        return results
    if recursive:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not d.startswith(WM_OUTPUT_SUBFOLDER)]
            for fn in sorted(files):
                if os.path.splitext(fn)[1].lower() in SUPPORTED_IMAGE_EXTS:
                    results.append(os.path.join(root, fn))
    else:
        for fn in sorted(os.listdir(folder)):
            fp = os.path.join(folder, fn)
            if os.path.isfile(fp) and os.path.splitext(fn)[1].lower() in SUPPORTED_IMAGE_EXTS:
                results.append(fp)
    return results


def composite_anchor_on_image(image_path: str, anchor_img, width_ratio: float = 0.22,
                               margin_x_ratio: float = 0.02, margin_y_ratio: float = 0.0):
    """base 이미지 우측 하단에 anchor_img(미리 로드된 RGBA PIL Image)를
    비율에 맞게 리사이즈해 합성한 새 PIL Image를 반환한다(원본 객체는 안 건드림).
    - width_ratio   : 앵커 이미지 폭 = base 폭 * width_ratio (워터마크를 확실히
                       덮을 만큼 충분히 크게, 기본 22%)
    - margin_x_ratio: 오른쪽 여백 = base 폭 * margin_x_ratio
    - margin_y_ratio: 아래쪽 여백 = base 높이 * margin_y_ratio (기본 0 = 바닥에
                       딱 붙임)
    JPG처럼 알파 채널이 없는 포맷은 최종적으로 RGB로 되돌려 저장 호환성을 유지한다."""
    base = Image.open(image_path)
    orig_mode = base.mode
    base = base.convert("RGBA")
    bw, bh = base.size

    aw = max(1, int(bw * width_ratio))
    ah = max(1, int(anchor_img.height * (aw / anchor_img.width)))
    anchor_resized = anchor_img.resize((aw, ah), Image.LANCZOS)

    margin_x = int(bw * margin_x_ratio)
    margin_y = int(bh * margin_y_ratio)
    x = max(0, bw - aw - margin_x)
    y = max(0, bh - ah - margin_y)

    base.paste(anchor_resized, (x, y), anchor_resized)

    if orig_mode != "RGBA":
        base = base.convert("RGB")
    return base


def _wm_output_path(src_path: str, target_folder: str, keep_original: bool) -> str:
    """'원본 유지' 옵션이면 target_folder 아래 WM_OUTPUT_SUBFOLDER 안에
    원본과 같은 상대경로 구조를 그대로 살려 저장 경로를 만든다. 원본
    덮어쓰기 옵션이면 같은 폴더·같은 파일명(확장자만 교체)으로 만든다.
    합성 결과는 원본 확장자와 무관하게 항상 PNG로 저장한다."""
    if keep_original:
        rel = os.path.relpath(src_path, target_folder)
        rel_png = os.path.splitext(rel)[0] + ".png"
        return os.path.join(target_folder, WM_OUTPUT_SUBFOLDER, rel_png)
    return os.path.splitext(src_path)[0] + ".png"


def get_current_public_ip():
    """현재 공인 IP 조회 (외부 서비스 순차 시도)"""
    for url in ['https://api.ipify.org', 'https://icanhazip.com', 'https://checkip.amazonaws.com']:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.read().decode().strip()
        except Exception:
            continue
    return None

# ════════════════════════════════════════════════════════════
# [지식인 중복체크] 질문DB / 포스팅DB 공용 엔진 (정책뉴스 컨셉 적용)
# - 주제(=블로그)별로 DB를 분리한다: base_folder/주제/질문DB.json, 포스팅DB.json
# - 질문DB: 저장 시 자동 차단만 하고 삭제는 없음 (계속 누적)
# - 포스팅DB: 저장(=포스팅) 시 자동 차단, 종합관리 탭에서 수동 삭제 가능
# ════════════════════════════════════════════════════════════

_KIN_NUM_PAT = re.compile(
    r'\d+[\.,]?\d*\s*(?:%|년|월|일|만원|억원|조원|개월|시간|분|세|명|건|회|배|학년|학기|등급|점|%p)'
)

# [Ver7.79 신규] "프롬프트만 복사" 공용 안내 문구 (B안). 같은 웹 AI 채팅창을
# 유지한 채 "프롬프트만 복사"를 한 번만 붙여넣고, 이후 항목들은 "자료만
# 복사"로 이어 붙이는 절약 워크플로우를 쓸 때, 대화가 길어지면서 규칙이
# 조금씩 느슨해지는 이탈(drift) 현상을 방지하기 위해 프롬프트 맨 앞에
# 붙인다. "프롬프트+자료 복사"(결합형) 버튼은 매번 프롬프트를 새로 함께
# 보내므로 대상에서 제외 - 이 문구가 필요한 지점은 프롬프트를 한 번만
# 보내고 이후 재전달하지 않는 워크플로우(=프롬프트만 복사)뿐이다.
KIN_PROMPT_CONTINUITY_NOTICE = """※ 작업 방식 안내
1) 이번에 전달하는 프롬프트를 먼저 끝까지 읽고 모든 규칙(형식, 금지 표현, 자기점검 항목 등)을 숙지해 주세요.
2) 이후 이 채팅에서는 원문(소스 자료)만 순서대로 이어서 전달합니다.
3) 제가 새 프롬프트를 다시 붙여넣기 전까지는, 지금 이 프롬프트를 그대로 기준 삼아 매 원문마다 동일하게 적용해 작업해 주세요.
4) 여러 건을 연속으로 처리하다 보면 규칙이 조금씩 느슨해지는 경우가 있으니, 매 건마다 이번 프롬프트 원칙을 다시 한번 상기하며 작업해 주세요.

"""

# [Ver7.81 신규, Ver8.21 수정] "8)2차각색(웹)" 전용 안내 문구. 위
# KIN_PROMPT_CONTINUITY_NOTICE는 1)질문선별/1차각색 등 4곳에도 공용으로
# 쓰이므로 2차각색에만 별도로 분리했었다. [Ver8.21] 탭이 완전히 분리된
# 지금은 한 대화창에서 2차각색만 연속으로 진행되고 인포그래픽과 번갈아
# 오지 않으므로, 라벨 기반 구분 지시를 빼고 공용 KIN_PROMPT_CONTINUITY_
# NOTICE와 동일한 취지의 단순한 형태로 되돌렸다(사용자 확인).
KIN_WEB2ND_PROMPT_CONTINUITY_NOTICE = """※ 작업 방식 안내
1) 이번에 전달하는 프롬프트를 먼저 끝까지 읽고 모든 규칙(형식, 금지 표현, 자기점검 항목 등)을 숙지해 주세요.
2) 이후 이 채팅에서는 원고(소스 자료)만 순서대로 이어서 전달합니다.
3) 제가 새 프롬프트를 다시 붙여넣기 전까지는, 지금 이 프롬프트를 그대로 기준 삼아 매 원고마다 동일하게 적용해 작업해 주세요.
4) 여러 건을 연속으로 처리하다 보면 규칙이 조금씩 느슨해지는 경우가 있으니, 매 건마다 이번 프롬프트 원칙을 다시 한번 상기하며 작업해 주세요.

"""

# [Ver7.80 신규, Ver8.21 수정] 썸네일/인포그래픽 스타일 템플릿("📝 프롬프트만
# 복사" 계열)용 안내 문구. 위 KIN_PROMPT_CONTINUITY_NOTICE와 취지는
# 동일하지만, 이쪽은 "형식·금지표현" 같은 글쓰기 규칙이 아니라 "색감·구도·
# 톤" 같은 이미지 스타일 규칙이라 예시 표현만 맞춤 조정했다. 템플릿을 매번
# 함께 보내는 결합형(_copy_kin_thumbnail_prompt)에는 넣지 않고, 템플릿만
# 한 번 보내고 이후 본문만 이어 붙이는 "프롬프트만 복사"(_copy_kin_
# thumbnail_prompt_only)에만 적용한다. [Ver8.21] 탭이 분리된 지금은 이
# 스타일 템플릿을 보내는 대화창에서 인포그래픽 작업만 연속으로 진행되고
# 2차각색과 번갈아 오지 않으므로, 라벨 기반 구분 지시를 빼고 단순한 형태로
# 되돌렸다(사용자 확인).
KIN_THUMBNAIL_PROMPT_CONTINUITY_NOTICE = """※ 작업 방식 안내
1) 이번에 전달하는 스타일 템플릿을 먼저 끝까지 읽고 모든 규칙(색감, 구도, 톤, 캐릭터/아이콘 시스템 등)을 숙지해 주세요.
2) 이후 이 채팅에서는 완성 본문(소스 자료)만 순서대로 이어서 전달합니다.
3) 제가 이 스타일 템플릿을 다시 붙여넣기 전까지는, 지금 이 템플릿을 그대로 기준 삼아 매 본문마다 동일하게 적용해 작업해 주세요.
4) 여러 건을 연속으로 처리하다 보면 스타일이 조금씩 흔들리는 경우가 있으니, 매 건마다 이번 템플릿 원칙을 다시 한번 상기하며 작업해 주세요.

"""

# [Ver7.81 신규] "자료만 복사" 시 자동으로 붙는 구분 라벨 - 8)2차각색(웹)과
# 썸네일/인포그래픽이 같은 대화창에서 번갈아 쓰인다는 점이 확인되어, AI가
# 매 순간 "지금 이 자료가 어느 작업 차례인지"를 헷갈리지 않도록 자료
# 텍스트 맨 앞에 붙인다. 완성본(md_text)을 그대로 재사용하는 인포그래픽
# 자료와, 1차각색 결과를 다듬는 2차각색 자료가 겉보기엔 둘 다 "글"이라
# 라벨 없이는 AI 쪽에서 구분할 근거가 없다.
KIN_WEB2ND_MATERIAL_LABEL = "[2차각색 자료]\n아래 원고를 방금 전달한 2차각색 프롬프트 규칙대로 다듬어 주세요.\n\n"
KIN_THUMBNAIL_MATERIAL_LABEL = ""  # 기본값을 공백으로하여 지시문 제거 (2026-08-24)

# [Ver8.21 신규 → Ver8.22 되돌림] "이미지 생성을 즉시 트리거하는 영어
# 지시문"을 코드(_build_kin_thumbnail_prompt)에서 프롬프트 맨 앞에 삽입하는
# 방식으로 시도했으나, 위치가 맞지 않다는 사용자 피드백으로 삭제함 - 이
# 지시문은 코드가 아니라 프롬프트 템플릿(.md, "6단계. 최종 생성 프롬프트
# 작성 규칙 > 공통 필수 포함 문구") 쪽에 사용자가 직접 넣는 것이 맞는
# 위치였다. 코드 쪽에는 더 이상 관여하지 않음(관련 상수 KIN_THUMBNAIL_
# IMAGE_GEN_DIRECTIVE 삭제).

# [Ver7.13 버그수정] hard_match 강제판정용 -- "2026년"처럼 연도만 단독으로
# 적힌 표기는 _KIN_NUM_PAT에 걸려 "숫자"로 집계되지만, 블로그 제목이 흔히
# "2026년 ~~" 형태로 시작해서 완전히 다른 글끼리도 "첫 어절 일치 + 숫자
# 겹침"이 우연히 다 성립해버리는 오탐을 유발했다(실측: 23% 낮은 유사도인데도
# 강제 차단됨). hard_match 판정에서는 연도 단독 토큰을 숫자 겹침 계산과
# 첫 어절 비교 양쪽에서 제외한다.
_KIN_YEAR_ONLY_PAT = re.compile(r'^\d{4}년$')

# [Ver7.15 버그수정] "1회", "50%", "A등급"처럼 교육/학습 콘텐츠 전반에서
# 극히 흔하게 반복되는 범용 카운터·등급 표현은 서로 완전히 다른 글에서도
# 우연히 겹치기 쉽다(실측: "국어"+"1회"만 겹쳤는데 강제 차단됨). hard_match
# 판정에는 실제로 구체적인 사실(금액·나이·기간)을 나타내는 단위만 인정하고,
# 회/배/학년/학기/등급/점/%/%p/명/건/시간/분/월 같은 범용 카운터는 제외한다.
# (일반 가중치 점수 15% 계산에는 그대로 남아있어 원래 기능은 안 건드림)
# [Ver7.56 변경] '일'도 목록에서 제외했다. "30일", "7일", "1일"처럼 기한·
# 유예기간·처리기간을 나타내는 표현은 도메인을 가리지 않고 거의 모든 글에
# 등장해서(예: 이번 대화에서 다룬 반대매매 글의 "T+2", "30일 동결"과
# 전혀 무관한 다른 글의 "30일 이내"가 우연히 겹치는 식) '만원/억원/조원/
# 세/개월'보다 훨씬 우연히 겹치기 쉽다. 나머지(금액·나이·개월수)는
# 우연히 같은 숫자가 나올 확률이 낮아 hard_match 근거로 남겨둔다.
_KIN_SPECIFIC_NUM_SUFFIXES = ('만원', '억원', '조원', '세', '개월')


def _kin_is_specific_number(token):
    """hard_match에 쓸 만큼 구체적인(=우연히 겹치기 어려운) 숫자 표현인지 판별."""
    if _KIN_YEAR_ONLY_PAT.match(token):
        return False
    return token.endswith(_KIN_SPECIFIC_NUM_SUFFIXES)

# [Ver7.05 수정] 썸네일 스타일 템플릿은 별도 폴더가 아니라, 지금 쓰는
# 작업 폴더(base_folder_var) 안에 그냥 놓고 쓴다. 실제 파일명 예시:
#   지식인_경제6개주제통합_썸네일_프롬프트_V1.md
#   지식인_교육_썸네일_프롬프트_V1.md
#   지식인_자동차_썸네일_프롬프트_V1.md
# 파일명을 고정하지 않고 "그룹 키워드가 포함된 .md 파일"을 작업 폴더
# 안에서 찾는 방식이라, 나중에 V2·V3로 올려도 코드 수정 없이 그대로
# 작동한다(여러 버전이 같이 있으면 파일명 정렬상 가장 나중 버전을 사용).

# 주제(폴더명) → 썸네일 스타일 그룹 키워드. 경제 A~G는 포스팅 프로그램이
# 동일해 유사 패턴에 걸리는 걸 피하기 위해 "경제" 하나로 통합.
# 건강·IT는 아직 템플릿이 없어 매핑하지 않음(템플릿 준비되면 한 줄만
# 추가하면 됨).
KIN_THUMBNAIL_GROUP_MAP = {
    "경제-A-거시경제-경기-통화-금리":             "경제",
    "경제-B-금융-대출-신용-투자-보험-연금상품":    "경제",
    "경제-C-세금-조세제도-연말정산":               "경제",
    "경제-D-고용-노동-근로관계-취업지원":          "경제",
    "경제-E-복지연금-사회보험-국민연금-생활지원":  "경제",
    "경제-F-법률-행정-행정절차-가사":              "경제",
    "경제-G-부동산-임대차-매매-등기":              "경제",
    "교육": "교육",
    "자동차": "자동차",
}
# [Ver7.20 추가] KIN_THUMBNAIL_GROUP_MAP은 예전 "그룹+작업폴더 자동탐색"
# 폴백에서만 쓰였는데 그 폴백을 제거하면서 더 이상 코드에서 참조되지
# 않는다. 삭제하지 않고 남겨둔 이유는 "경제-A-거시경제-경기-통화-금리"
# 처럼 현재 사용하지 않는 세부주제를 나중에 다시 쓰게 될 때 참고용으로
# 남겨두기 위함이며, 동작에는 영향이 없다.

# [Ver7.20 추가] 재미나이(Gemini) 변환 프롬프트는 주제별이 아니라 전체
# 주제 공용 1개 파일이다(도메인 스타일은 이미 썸네일 프롬프트 단계에서
# 반영되고, 이 단계는 "GPT 문법 → 재미나이 문법" 변환만 담당하기
# 때문). load_kin_thumbnail_prompts()/save_kin_thumbnail_prompts()가
# 쓰는 {주제: 파일명} 딕셔너리에 이 예약 키로 함께 저장해, 별도 JSON
# 파일을 새로 만들지 않고 기존 저장 구조를 그대로 재사용한다.
KIN_THUMBNAIL_GEMINI_KEY = "__GEMINI_CONVERTER__"


def get_topic_folder_path(base_folder, topic_name):
    return os.path.join(base_folder, topic_name)


def get_question_db_path(base_folder, topic_name):
    return os.path.join(base_folder, topic_name, "질문DB.json")


def get_posting_db_path(base_folder, topic_name):
    return os.path.join(base_folder, topic_name, "포스팅DB.json")


def load_json_db(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_json_db(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def extract_question_core(title, question_text):
    """지식인 질문 제목+본문에서 중복비교/저장용 핵심요소 추출.
    [Ver7.10 수정] 형태 B(Q&A 클러스터: 메인질문+실제답변 여러개+연관검색
    목록)를 온전히 넘기기 위해 기존의 500자 절단·줄바꿈 제거(re.sub(r'\\s+',' '))를
    없앴다. 과도하게 많은 빈 줄만 2줄로 정리해 구조(문단 구분)는 유지한다."""
    numbers = list(set(_KIN_NUM_PAT.findall(question_text)))[:10]
    body = (question_text or "").strip()
    body = re.sub(r'\n{3,}', '\n\n', body)
    return {
        "title": (title or "").strip(),
        "body": body,
        "numbers": numbers,
    }


# ── [Ver7.08 추가] 사전 필터링(질문 선별) 관련 파싱 함수 ──────────
# 0단계 저장 시 자동생성_{주제}.txt에 누적되는 형식:
#   \n{'='*60}\n[YYYY-MM-DD HH:MM:SS]\n{질문 원문(제목+본문)}\n
# 을 개별 질문 블록으로 분리하고, 사전 필터링 AI 응답에서
# "## 리서치 대상 선별 목록"만 뽑아내는 역할을 한다.

def parse_collected_kin_questions(raw_text):
    """자동생성_{주제}.txt 원문(누적된 여러 질문)을 개별 질문 블록으로 분리.
    반환: [{'title':..., 'body':..., 'raw':...}, ...] (파일에 저장된 순서 그대로)"""
    blocks = re.split(r'\n?={60}\n', raw_text)
    questions = []
    for block in blocks:
        block = block.strip('\n')
        if not block.strip():
            continue
        # 맨 앞 타임스탬프 줄 "[YYYY-MM-DD HH:MM:SS]" 제거
        block = re.sub(r'^\[\d{4}-\d{2}-\d{2}[^\]]*\]\n', '', block).strip('\n')
        if not block.strip():
            continue
        lines = block.split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        questions.append({"title": title, "body": body, "raw": block})
    return questions



def parse_prefilter_selection(ai_response_text):
    """사전 필터링 AI 응답에서 최종 선별 목록만 추출.
    [Ver7.09] 우선 [SELECTED_START]~[SELECTED_END] 사이의
    "번호|질문 문장" 고정 포맷(신규 프롬프트)을 파싱한다. 정규식이
    아니라 '|' 분리라서 AI가 마크다운 스타일을 조금 바꿔도 깨지지
    않는다. 이 표시가 없는 옛 프롬프트 응답이면 '## 리서치 대상
    선별 목록' 아래 번호 목록(마크다운)을 예비로 파싱한다(하위호환).
    반환: [(번호:int, 질문문장:str), ...]"""
    m = re.search(r'\[SELECTED_START\](.*?)\[SELECTED_END\]', ai_response_text, re.S)
    if m:
        items = []
        for line in m.group(1).split('\n'):
            line = line.strip()
            if not line or '|' not in line:
                continue
            num_part, _, sentence = line.partition('|')
            num_part = num_part.strip()
            sentence = sentence.strip()
            if num_part.isdigit() and sentence:
                items.append((int(num_part), sentence))
        return items

    # ── 예비(구버전) 파싱: [SELECTED_START] 표시가 없는 옛 프롬프트 응답 ──
    m2 = re.search(r'##\s*리서치\s*대상\s*선별\s*목록.*?\n(.*?)(?:\n##\s|\Z)', ai_response_text, re.S)
    if not m2:
        return []
    items = []
    for line in m2.group(1).split('\n'):
        line = line.strip()
        mm = re.match(r'^[-*]?\s*(\d+)[\.\)]\s*(.+)$', line)
        if mm:
            items.append((int(mm.group(1)), mm.group(2).strip()))
    return items


# ── [Ver7.10 추가] "클로드 최종 검토" 버튼용 내장 프롬프트 ─────────
# 같은 질문 목록을 퍼플렉시티·클로드 두 AI에 각각 돌린 사전 필터링
# 결과를 받아, 하나의 최종 결과로 병합하는 메타 프롬프트. 외부 파일이
# 아니라 프로그램 코드에 직접 심어둔다(사용자 요청). {perplexity_result},
# {claude_result} 자리에 두 결과 붙여넣기 박스 내용이 그대로 들어간다.
KIN_PREFILTER_FINAL_REVIEW_PROMPT = """[역할]
당신은 네이버 지식인 질문 사전 필터링 결과를 최종 검토하는 감수자입니다.
아래에 동일한 [입력 질문 목록]을 서로 다른 두 AI가 각각 심사한 결과가 주어집니다:
- [퍼플렉시티 결과]
- [클로드 결과]

각 결과는 번호별로 "적합 / 재구성 필요 / 부적합" 판정과 사유, 그리고 통과한
질문의 재구성 문장을 담고 있습니다. 이 두 결과를 비교해서 최종 하나의
결과로 병합하는 것이 당신의 역할입니다.

[병합 규칙]
1. 두 결과가 같은 번호에 대해 같은 방향(포함 vs 배제)으로 판정했다면 그대로
   채택합니다. 재구성 문장이 서로 다르게 쓰였다면, 개인정보(구체적 성적·
   특정 학교명·거주지역 등)를 더 완전히 제거하면서도 원래 질문의 정보
   수요를 가장 정확히 담은 문장을 선택하거나, 필요하면 더 다듬습니다.
2. 두 결과가 방향(포함 vs 배제)에서 서로 엇갈리면, 다수결로 넘기지 말고
   아래 원래 배제 규칙 5가지와 재구성 판단 기준을 다시 직접 적용해서
   스스로 최종 판정을 내립니다.
   - ① 상품 추천형: "추천해주세요"라는 표현과 함께 특정 문제집명·강의명·
     강사명·학원명이 질문의 핵심인 경우. 단, 그 이름을 지워도 남는
     일반적 정보 수요(학습 전략·선택 기준 등)가 있다면 "재구성 필요"로
     살립니다. 지우면 질문 자체가 성립하지 않을 때만 "부적합"입니다.
   - ② 단일 기관 행정형: 특정 학교/대학 한 곳의 내부 행정 규정(성적 산출
     방식, 휴학 신청 절차, 자체 평가 기준 등)만 묻는 경우.
   - ③ 순수 고민상담형: 사실 정보가 아니라 개인적 의견·위로·심리적
     조언을 원하는 경우. 단, "정보 자체"(예: 전과 시 생기부 준비 방향,
     제도 비교)를 묻는 부분이 함께 있다면 그 정보 수요만 뽑아 "재구성
     필요"로 살립니다. 순수하게 "계속할지 말지" 감정적 조언만 원하면
     "부적합"입니다.
   - ④ 해외 대학·해외 교육제도
   - ⑤ 개인 특정 가능
3. 판정이 엇갈렸던 번호는 [최종 판정 상세] 표에 두 AI의 원래 판정과 최종
   판정, 그리고 어떤 규칙을 적용해 그렇게 결정했는지 1문장 사유를 남깁니다.
   이 사유는 표에만 적고, 아래 SELECTED 블록의 질문 문장 안에는 절대
   섞지 않습니다.
4. 두 AI 모두 심사요약(총 N건 중 적합/재구성/부적합 건수)의 숫자와 실제
   표 내용이 서로 안 맞는 경우가 잦았습니다. 최종 결과의 심사요약 숫자는
   반드시 최종 판정 상세 내용을 실제로 세어서 채웁니다.

[최종 출력 형식]

전체 문서를 하나의 코드블럭으로 감싸서 출력합니다.

##### 병합 요약
- 총 N건 중 두 결과 일치 A건 / 판정 엇갈려 재검토 B건 / 최종 포함(적합+재구성완료) C건 / 최종 배제(부적합) D건

## 최종 판정 상세 (두 결과가 엇갈렸던 항목만)

| 번호 | 퍼플렉시티 판정 | 클로드 판정 | 최종 판정 | 최종 사유 |
|---|---|---|---|---|
| (엇갈렸던 항목만 나열, 일치했던 항목은 생략) |

## 리서치 대상 선별 목록 (최종)

이 섹션은 프로그램이 그대로 파싱합니다. 아래 형식을 한 글자도 벗어나지 않고 지킵니다.

- 시작 줄과 종료 줄을 정확히 그대로, 각각 단독 줄로 출력합니다: `[SELECTED_START]` 그리고 `[SELECTED_END]`
- 그 사이에는 최종 통과된 질문마다 한 줄씩, 다음 형식만 사용합니다: `원래 번호|질문 문장`
- 번호는 [입력 질문 목록]에서의 원래 번호를 그대로 사용합니다(두 AI가 매긴 번호와 동일).
- 질문 문장 안에는 줄바꿈과 `|` 문자를 절대 사용하지 않습니다.
- 부적합으로 최종 결정된 항목은 이 목록에 포함하지 않습니다.
- 통과 항목이 하나도 없어도 `[SELECTED_START]`와 `[SELECTED_END]` 두 줄은 반드시 출력하고, 그 사이는 비워둡니다.

[SELECTED_START]
(여기에 번호|질문 문장 형식으로 한 줄씩)
[SELECTED_END]

---

[퍼플렉시티 결과]
{perplexity_result}

[클로드 결과]
{claude_result}
"""


def extract_posting_core(md_text, title=""):
    """완성된 포스팅 MD 글에서 중복비교용 핵심요소 추출 (정책뉴스 extract_core와 동일 원리)"""
    lines = md_text.split("\n")

    # 도입부: 첫 ## 소제목 이전 단락
    intro_lines = []
    for line in lines:
        if line.strip().startswith("## "):
            break
        if line.strip() and not line.strip().startswith("#"):
            intro_lines.append(line.strip())
    intro = " ".join(intro_lines[:5])

    # 마무리: 마지막 ## 섹션 이후 텍스트
    last_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("## "):
            last_idx = i
    summary_lines = []
    for line in lines[last_idx:]:
        if line.strip() and not line.strip().startswith("#"):
            summary_lines.append(line.strip())
    summary = " ".join(summary_lines[:5])

    numbers = list(set(_KIN_NUM_PAT.findall(md_text)))[:10]

    # [Ver7.56 추가] 소제목(## ) 시그니처 - 중복비교가 도입부/마무리 200자
    # 스니펫만 보다 보니 본문 중간(2~N번째 섹션)이 통째로 표절 수준으로
    # 같아도 비교 대상에 안 들어가는 구조였음. 소제목은 "이 글이 어떤
    # 세부 사실들을 다루는지"를 가장 압축적으로 보여주는 지표라, 본문
    # 전체를 다시 스캔하지 않고도 중간 내용의 겹침을 저비용으로 잡아낼
    # 수 있다. 앞의 "1. ", "2)" 같은 번호 매김은 글마다 순서가 달라질 뿐
    # 내용과 무관하므로 비교 전에 제거한다.
    heading_num_pat = re.compile(r'^[\d]+[.\)]\s*')
    headings = []
    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            h = s[3:].strip()
            h = heading_num_pat.sub('', h)
            if h:
                headings.append(h)

    return {
        "title": (title or "").strip(),
        "intro": intro[:200],
        "summary": summary[:200],
        "numbers": numbers,
        "headings": headings,
    }


def check_question_duplicate(new_core, records, danger=70):
    """질문 중복 검사. 가중치: 제목 40 / 본문 45 / 숫자일치 15. danger 이상만 반환.
    [Ver7.13 추가, 정책뉴스 check_duplicate의 hard_match 참조] 정책뉴스는 "제목 첫
    어절 + 발표부처 일치"를 점수와 무관하게 강제 포함시키는 규칙이 있는데, 지식인은
    발표부처(기관명) 개념이 없어(DB가 이미 주제별로 분리돼 있어 그 역할을 어느정도
    대신함) 대신 "제목 첫 어절 + 숫자(수급기간·나이·금액 등) 최소 1개 일치"로
    바꿔 적용한다. 표현이 크게 달라져도(예: "~하다는데" -> "~로 확정됐다는 소식")
    구체적 숫자가 같으면 같은 질문일 확률이 높다는 판단."""
    results = []
    nt = new_core.get("title", "")
    nb = new_core.get("body", "")
    nn = set(str(x) for x in new_core.get("numbers", []))

    for r in records:
        score = 0
        matched = []

        rt = r.get("title", "")
        if nt and rt:
            tr = difflib.SequenceMatcher(None, nt, rt).ratio()
            score += tr * 40
            if tr > 0.5:
                matched.append(f"제목({round(tr*100)}%)")

        rb = r.get("body", "")
        if nb and rb:
            br = difflib.SequenceMatcher(None, nb, rb).ratio()
            score += br * 45
            if br > 0.4:
                matched.append(f"본문({round(br*100)}%)")

        rn = set(str(x) for x in r.get("numbers", []))
        if nn and rn:
            overlap = len(nn & rn) / max(len(nn), len(rn))
            score += overlap * 15
            if nn & rn:
                matched.append(f"숫자({'·'.join(list(nn & rn)[:2])})")

        # [Ver7.13 추가, Ver7.14/Ver7.15 버그수정] 강한 판정 규칙 -- 점수와
        # 무관하게 danger 미달이어도 강제 포함. 단, 오탐 실측 2건(연도 단독
        # 표기, "국어"+"1회" 같은 범용 과목명+범용 카운터)을 겪은 뒤 기준을
        # 더 보수적으로 조정했다: 첫 어절은 3글자 이상(2글자 과목명 등 흔한
        # 단어 배제)이어야 하고, 숫자는 구체적 사실(금액·나이·기간)만 인정한다.
        nt_first = nt.split()
        rt_first = rt.split()
        nn_hard = {n for n in nn if _kin_is_specific_number(n)}
        rn_hard = {n for n in rn if _kin_is_specific_number(n)}
        first_word_match = bool(
            nt_first and rt_first
            and len(nt_first[0]) >= 3
            and nt_first[0] == rt_first[0]
            and not _KIN_YEAR_ONLY_PAT.match(nt_first[0])
        )
        hard_match = bool(first_word_match and (nn_hard & rn_hard))
        if hard_match:
            matched.append(f"⚠️주제어+숫자일치({nt_first[0]})")

        if score >= danger or hard_match:
            results.append({
                "rate": round(score, 1), "title": rt, "date": r.get("date", ""),
                "matched": matched, "hard_match": hard_match,
            })

    # [Ver7.13 수정] hard_match 항목은 점수가 낮아도 상단에 뜨도록 우선 정렬
    results.sort(key=lambda x: (x.get("hard_match", False), x["rate"]), reverse=True)
    return results


def _kin_find_common_phrases(text1, text2, min_len=6, max_results=5):
    """[Ver7.16 신규] 두 텍스트에서 실제로 그대로 겹치는 표현(연속 부분열)을
    찾아 사람이 읽고 판단할 근거로 보여준다. "58% 유사"라는 숫자만으로는
    무엇이 겹쳤는지 알 수 없다는 지적을 반영 -- 짧은 조사/흔한 표현(6자 미만)
    은 노이즈라 제외하고, 긴 것부터 최대 max_results개만 돌려준다."""
    if not text1 or not text2:
        return []
    sm = difflib.SequenceMatcher(None, text1, text2)
    blocks = [text1[b.a:b.a + b.size].strip() for b in sm.get_matching_blocks() if b.size >= min_len]
    result = []
    for b in sorted(set(blocks), key=len, reverse=True):
        if not b:
            continue
        # 이미 뽑힌(더 긴) 문구에 완전히 포함되는 짧은 문구는 중복 정보라 건너뛴다.
        if any(b in existing for existing in result):
            continue
        result.append(b)
        if len(result) >= max_results:
            break
    return result


def check_question_vs_posting_duplicate(q_core, posting_records, danger=70):
    """[Ver7.75 신규] 원본 질문(아직 리서치/각색 전, extract_question_core로
    뽑은 title/body/numbers)을 "이미 발행 완료된" 포스팅DB와 교차 비교한다.

    배경: 지금까지 질문수집·질문상세분석 단계의 중복체크(check_question_
    duplicate)는 "질문DB끼리"만 비교했다 - 실제로 자주 벌어지는 낭비는
    "이미 포스팅까지 끝낸 주제인데 모르고 또 리서치→1차→2차까지 진행"하는
    경우인데, 이건 훨씬 이른 단계인 질문수집 시점에 질문 제목/숫자만
    봐도 뻔한 경우가 많다. 포스팅DB와 비교해 이 낭비를 가장 이른 지점에서
    막아보자는 취지(사용자 확인: "질문수집/질문상세분석 단계에서 포스팅DB와
    비교하면 더 빨리 찾을 수 있지 않을까").

    다만 "질문 문장"과 "완성된 글의 제목/도입부/소제목"은 표현 방식 자체가
    다른 종류의 텍스트라(정식 check_posting_duplicate가 완성글끼리 비교하는
    것보다) 정확도가 구조적으로 낮다. 그래서:
    (1) 정식 체크(check_posting_duplicate)처럼 저장을 강제 차단하는 용도가
        아니라, 질문DB에는 그대로 추가하되 "참고용 경고"만 얹는 용도로
        설계했다(호출부에서 이 결과를 이유로 건너뛰지 않는다).
    (2) 가중치도 그에 맞춰 "제목"과 "구체적 숫자 일치" 비중을 높이고
        (표현이 완전히 달라져도 안 흔들리는 강한 신호), 서술형 본문
        비교(도입부+마무리+소제목을 합친 텍스트 vs 질문 원문)는 참고
        수준의 비중만 준다.
    (3) hard_match(강제 표시)는 기존과 동일하게 "제목 첫 어절(3글자+)
        일치 + 구체적 숫자 일치"만 인정한다(소제목 자카드는 질문 쪽에
        애초에 소제목이 없어 적용 대상이 아님) - 그 대신 포스팅의 소제목이
        질문 본문 안에 그대로 등장하는 비율(coverage)을 보조 신호로 추가."""
    results = []
    nt = q_core.get("title", "")
    nb = q_core.get("body", "")
    nn = set(str(x) for x in q_core.get("numbers", []))
    nb_lower = nb.lower()

    for r in posting_records:
        score = 0
        matched = []

        rt = r.get("title", "")
        if nt and rt:
            tr = difflib.SequenceMatcher(None, nt, rt).ratio()
            score += tr * 35
            if tr > 0.5:
                matched.append(f"제목({round(tr*100)}%)")

        ri = r.get("intro", "")
        rs = r.get("summary", "")
        rh = r.get("headings", []) or []
        combined = f"{ri} {rs} {' '.join(rh)}".strip()
        if nb and combined:
            br = difflib.SequenceMatcher(None, nb, combined).ratio()
            score += br * 40
            if br > 0.35:
                matched.append(f"내용({round(br*100)}%)")

        rn = set(str(x) for x in r.get("numbers", []))
        if nn and rn:
            overlap = len(nn & rn) / max(len(nn), len(rn))
            score += overlap * 15
            if nn & rn:
                matched.append(f"숫자({'·'.join(list(nn & rn)[:2])})")

        # 포스팅 소제목이 질문 본문 안에 그대로 등장하는 비율(있으면 강한 신호)
        heading_hits = [h for h in rh if h and h.lower() in nb_lower]
        heading_coverage = len(heading_hits) / len(rh) if rh else 0
        if heading_hits:
            score += heading_coverage * 10
            matched.append(f"소제목 언급({'·'.join(heading_hits[:2])}{' 등' if len(heading_hits) > 2 else ''})")

        nt_first = nt.split()
        rt_first = rt.split()
        nn_hard = {n for n in nn if _kin_is_specific_number(n)}
        rn_hard = {n for n in rn if _kin_is_specific_number(n)}
        first_word_match = bool(
            nt_first and rt_first
            and len(nt_first[0]) >= 3
            and nt_first[0] == rt_first[0]
            and not _KIN_YEAR_ONLY_PAT.match(nt_first[0])
        )
        hard_match = bool(first_word_match and ((nn_hard & rn_hard) or heading_coverage >= 0.5))
        if hard_match:
            matched.append(f"⚠️주제어+강한일치({nt_first[0]})")

        if score >= danger or hard_match:
            results.append({
                "rate": round(score, 1), "title": rt, "date": r.get("date", ""),
                "matched": matched, "hard_match": hard_match,
                "file_path": r.get("file_path", ""),
            })

    results.sort(key=lambda x: (x.get("hard_match", False), x["rate"]), reverse=True)
    return results



def check_posting_duplicate(new_core, records, warn=50, danger=70):
    """포스팅 중복 검사. 가중치: 제목 25 / 도입부 15 / 마무리 15 / 소제목 25 / 숫자일치 20.
    [Ver7.07 수정] warn(기본 50) 이상이면 결과에 포함하고, danger(기본 70)
    이상인지는 "danger" 필드로 표시한다(정책뉴스와 동일한 2단계 방식).
    이렇게 해야 "저장 시 자동 차단"(70%↑)과 "저장 전 미리보기 중복체크
    버튼"(50%↑까지 넓게 보여줌)을 같은 함수로 같이 처리할 수 있다.
    기존처럼 danger만 필터링해서 쓰던 호출부는 결과의 "danger" 필드로
    다시 걸러내면 이전과 동일하게 동작한다.
    [Ver7.16 추가] "몇 % 겹침"이라는 숫자만으로는 원본 MD가 삭제된 뒤엔
    사람이 판단할 근거가 없다는 지적을 반영해, 실제로 겹친 숫자 전체 목록과
    그대로 겹치는 문구(common_phrases), 그리고 기존/신규 글의 도입부·마무리
    원문 스니펫(DB에 이미 저장돼 있던 것)까지 결과에 함께 담아 돌려준다.

    [Ver7.56 재설계] 실측으로 드러난 두 가지 약점을 보완했다.
    (1) 기존에는 도입부/마무리 200자 스니펫만 비교해서, 본문 중간(2~N번째
        섹션)이 통째로 똑같아도 비교 대상에 안 들어갔다. 소제목(## ) 목록의
        자카드 유사도를 새 축으로 추가해 "이 글이 어떤 세부 사실들을
        다루는가"를 저비용으로 반영한다(가중치 25) - 도입부/마무리는 이
        페르소나 특유의 정형화된 도입("~헷갈리는 경우가 많습니다" 류)
        비중이 커서 오탐 위험이 있던 만큼 각각 30→15로 낮췄다.
    (2) hard_match의 "구체적 숫자" 목록에서 '일'을 제외했다(위 상수 주석
        참조 - 기한·유예기간 표현이 너무 흔해 오탐 위험). 대신 숫자
        가중치는 15→20으로 올려서, 일반 점수 계산에서는 여전히 신호로
        쓰이되 강제 차단(hard_match) 근거로는 안 쓰이게 분리했다.
    (3) hard_match에 "제목 첫 어절 일치 + 소제목 자카드 0.6 이상" 조건을
        추가했다 - 도입부/마무리만 크게 고쳐 쓴 사실상 동일 글(패러프레이징)을
        숫자 겹침 없이도 잡기 위함이다."""
    results = []
    nt = new_core.get("title", "")
    ni = new_core.get("intro", "")
    ns = new_core.get("summary", "")
    nn = set(str(x) for x in new_core.get("numbers", []))
    nh = set(new_core.get("headings", []) or [])

    for idx, r in enumerate(records):
        score = 0
        matched = []
        title_pct = intro_pct = summary_pct = heading_pct = 0

        rt = r.get("title", "")
        if nt and rt:
            tr = difflib.SequenceMatcher(None, nt, rt).ratio()
            score += tr * 25
            title_pct = round(tr * 100)
            if tr > 0.5:
                matched.append(f"제목({title_pct}%)")

        ri = r.get("intro", "")
        if ni and ri:
            ir = difflib.SequenceMatcher(None, ni, ri).ratio()
            score += ir * 15
            intro_pct = round(ir * 100)
            if ir > 0.4:
                matched.append(f"도입부({intro_pct}%)")

        rs = r.get("summary", "")
        if ns and rs:
            sr = difflib.SequenceMatcher(None, ns, rs).ratio()
            score += sr * 15
            summary_pct = round(sr * 100)
            if sr > 0.4:
                matched.append(f"마무리({summary_pct}%)")

        # [Ver7.56 신규] 소제목 자카드 유사도 - 옛 기록에는 headings 필드가
        # 없을 수 있으니(하위호환) 양쪽 다 있을 때만 반영한다.
        rh = set(r.get("headings", []) or [])
        headings_overlap = sorted(nh & rh)
        if nh and rh:
            h_jaccard = len(nh & rh) / len(nh | rh)
            score += h_jaccard * 25
            heading_pct = round(h_jaccard * 100)
            if headings_overlap:
                matched.append(f"소제목({'·'.join(headings_overlap[:2])}{' 등' if len(headings_overlap) > 2 else ''})")

        rn = set(str(x) for x in r.get("numbers", []))
        numbers_overlap = sorted(nn & rn)
        if nn and rn:
            overlap = len(nn & rn) / max(len(nn), len(rn))
            score += overlap * 20
            if numbers_overlap:
                matched.append(f"숫자({'·'.join(numbers_overlap[:2])}{' 등' if len(numbers_overlap) > 2 else ''})")

        # [Ver7.13 추가, 정책뉴스 check_duplicate의 hard_match 참조] 제목 첫 어절 +
        # 숫자 최소 1개 일치 시 점수와 무관하게 강제로 danger 처리한다. 표현이 크게
        # 바뀐 후속 포스팅(예고 -> 확정)을 가중치 점수로는 못 잡는 경우를 대비.
        # [Ver7.14/Ver7.15 버그수정] 오탐 실측 2건을 겪은 뒤 기준을 더 보수적으로
        # 조정했다. 1건: 연도 단독 표기("2026년")가 숫자로 잡혀 대부분의 제목이
        # 우연히 겹침. 2건: "국어"(2글자 흔한 과목명) + "1회"(범용 카운터)만
        # 겹쳤는데도 강제 차단(매칭율 23.8%인데 저장 불가). 이제 첫 어절은
        # 3글자 이상만 인정하고, 숫자는 구체적 사실(금액·나이·기간)만 인정한다.
        # [Ver7.56 변경] '일' 제외는 위 상수 쪽에서 처리했고, 여기서는 숫자
        # 겹침 대신 소제목 자카드 0.6 이상도 hard_match 근거로 추가했다.
        nt_first = nt.split()
        rt_first = rt.split()
        nn_hard = {n for n in nn if _kin_is_specific_number(n)}
        rn_hard = {n for n in rn if _kin_is_specific_number(n)}
        first_word_match = bool(
            nt_first and rt_first
            and len(nt_first[0]) >= 3
            and nt_first[0] == rt_first[0]
            and not _KIN_YEAR_ONLY_PAT.match(nt_first[0])
        )
        number_hard_hit = bool(nn_hard & rn_hard)
        heading_hard_hit = bool(nh and rh and (len(nh & rh) / len(nh | rh)) >= 0.6)
        hard_match = bool(first_word_match and (number_hard_hit or heading_hard_hit))
        if hard_match:
            reason = "숫자일치" if number_hard_hit else "소제목일치"
            matched.append(f"⚠️주제어+{reason}({nt_first[0]})")

        if score >= warn or hard_match:
            # [Ver7.16 신규] 실제로 겹치는 문구를 찾아 근거로 첨부 (도입부+
            # 마무리를 합쳐서 비교 -- 제목은 위에서 이미 별도로 % 비교함)
            common_phrases = _kin_find_common_phrases(f"{ni} {ns}", f"{ri} {rs}")
            results.append({
                "rate": round(score, 1), "title": rt, "date": r.get("date", ""),
                "matched": matched, "danger": score >= danger or hard_match,
                "hard_match": hard_match,
                "file_path": r.get("file_path", ""),
                # [Ver7.45 추가] "덮어쓰기(같은 글로 교체)" 기능용 - records
                # 리스트 안에서 이 기존 기록의 원래 위치를 함께 반환한다.
                "record_index": idx,
                # -- 아래는 Ver7.16에서 추가된 상세 비교 근거 필드 --
                "title_pct": title_pct, "intro_pct": intro_pct, "summary_pct": summary_pct,
                "numbers_overlap": numbers_overlap,
                "common_phrases": common_phrases,
                "new_title": nt, "new_intro": ni, "new_summary": ns,
                "old_title": rt, "old_intro": ri, "old_summary": rs,
                # -- Ver7.56에서 추가된 소제목 비교 근거 필드 --
                "heading_pct": heading_pct, "headings_overlap": headings_overlap,
            })

    # [Ver7.13 수정] hard_match 항목은 점수가 낮아도 상단에 뜨도록 우선 정렬
    results.sort(key=lambda x: (x.get("hard_match", False), x["rate"]), reverse=True)
    return results


def find_duplicate_groups(records, threshold=90):
    """[Ver7.46 신규] "중복 기록 일괄 정리" 기능용. 레코드 리스트 안에서
    서로 threshold% 이상 겹치는 레코드들을 그룹으로 묶어 반환한다.

    check_posting_duplicate를 그대로 재사용해 판정 기준이 어긋나지 않게
    한다(레코드 자체가 new_core와 동일한 필드 구조라 그대로 넘길 수 있음).
    다만 hard_match만으로 걸리고 실제 rate는 threshold 미만인 항목은 사람
    판단이 필요한 애매한 경우라 자동 그룹핑에서는 제외한다(rate만 본다) -
    hard_match는 원래 "저장 차단" 경고용으로 설계된 규칙이라, 자동삭제
    대상을 고르는 이 기능에 그대로 쓰면 실제로는 다른 글까지 묶일 위험이
    있기 때문.

    같은 레코드가 A~B, B~C처럼 연쇄로 겹치는 경우도 하나의 그룹으로
    합치기 위해 Union-Find를 사용한다.

    반환값: [[idx, idx, ...], ...] - idx는 입력 records 리스트 기준 원본
    인덱스(그룹 내 오름차순 정렬), 2건 이상 겹친 그룹만 포함한다."""
    n = len(records)
    if n < 2:
        return []

    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i in range(n):
        sub = records[i + 1:]
        if not sub:
            continue
        results = check_posting_duplicate(records[i], sub, warn=threshold, danger=threshold)
        for r in results:
            if r["rate"] < threshold:
                continue
            union(i, i + 1 + r["record_index"])

    buckets = {}
    for idx in range(n):
        root = find(idx)
        buckets.setdefault(root, []).append(idx)
    return [sorted(v) for v in buckets.values() if len(v) > 1]

# [Ver8.30 신규] 정책뉴스·복지로 프로그램에 있던 "제목선점 확인용 네이버
# 검색" 기능을 지식인에도 이식. 8)2차 각색 탭에서 저장 전에 제목이 이미
# 다른 블로그에 선점됐는지 미리 확인하는 용도(복지로 소스 그대로 이식,
# subprocess로 크롬을 직접 실행하는 방식 - 계정/키워드 자동완성 이력 등이
# 검색에 영향을 주지 않도록 매번 새 임시 프로필로 비로그인 상태로 띄운다).
def find_chrome_executable() -> str:
    """설치된 크롬 실행파일 경로를 OS별로 탐색(못 찾으면 빈 문자열).
    Windows/맥/리눅스 순으로 흔한 설치 위치를 확인한다."""
    import shutil
    if sys.platform.startswith("win"):
        candidates = [
            os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                         "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                         "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Google", "Chrome", "Application", "chrome.exe"),
        ]
        for c in candidates:
            if c and os.path.exists(c):
                return c
        return ""
    if sys.platform == "darwin":
        c = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        return c if os.path.exists(c) else ""
    # 리눅스
    for name in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    return ""


def open_naver_search_in_chrome(keyword: str, blog_only: bool = False) -> bool:
    """네이버 검색 결과 창을 크롬으로 연다(성공 시 True). 매번 새로 만드는
    임시 프로필(--user-data-dir)로 실행해 항상 비로그인 상태로 뜨게 한다.
    blog_only=True면 네이버 블로그 탭 검색(ssc=tab.blog.all)으로 열어,
    제목이 이미 다른 블로그에 선점된 글이 있는지 확인하는 용도로 쓴다."""
    import subprocess
    import tempfile
    from urllib.parse import quote

    if blog_only:
        url = f"https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query={quote(keyword)}"
    else:
        url = f"https://search.naver.com/search.naver?query={quote(keyword)}"
    chrome_path = find_chrome_executable()
    if not chrome_path:
        # 크롬을 못 찾으면 기본 브라우저로라도 열어준다(비로그인 보장은 안 됨)
        import webbrowser
        webbrowser.open(url)
        return False
    profile_dir = tempfile.mkdtemp(prefix="naver_search_profile_")
    subprocess.Popen([
        chrome_path,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window",
        url,
    ])
    return True


#pip uninstall google-generativeai -y
#pip install google-genai

### 주제 및 카테고리 폴더
# Naver_blog_kin_topic_classify_config
# 주제 카테고리 폴더 생성방식이 수동과 반자동이 조금 다름 (코드 통합하지 말 것)
# 사람이 화면에서 보고 선택하는 구조- 드롭다운 -경제A (약어)화면 표시 -> 경제-A-거시경제-경기-통화-금리(변환 테이블 거침)

# 주제 매핑 설정
# self.kin_mapping_file = "Naver_blog_config_지식인.json"

class MarkdownExtractorGUI:
# __init__ 메서드 수정 - 처음부터 센터에 창 생성
    def __init__(self, root):
        
        self.root = root
        self.root.title("네이버 지식인의 질문을 퍼플렉시티 웹에서 수집한 후 GPT/Claude/Gemini로 각색하는 프로그램(수동작업)_2026-09-28_Ver 9.28")
        self._shared_chrome_driver = None  # 네이버 지식인 접속용 공유 크롬(chrome_profile1) 인스턴스

        # 창 크기와 위치를 한번에 설정 (처음부터 센터에 생성)
        window_width = 1650  # [Ver7.85 수정] 1500 -> 1650 ("9)썸네일/인포그래픽" 탭 신설로
        # 버튼 5개(썸네일 프롬프트 복사~프롬프트 설정)가 한 줄에 들어갈 가로 여유 확보
        window_height = 980  # 0)주제 분류 탭에 네이버 지식인 접속 UI가 추가되어 늘어난 높이 반영
        
        # 화면 크기 얻기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()-70
        
        # 중앙 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 크기와 위치를 동시에 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 탭 스타일 설정 추가
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('나눔고딕', 12, 'bold'))
        style.map('ColorTab.TNotebook.Tab',
                 background=[('selected', '#4CAF50')],
                 foreground=[('selected', 'blue')])
        
        # ========================================
        # 1. 기본 폴더 설정
        # ========================================
        self.base_folder = "Naver_blog_지식인_수동_markdown_work_folder"
        os.makedirs(self.base_folder, exist_ok=True)
        
        
        
        self.prompt_folder = "Naver_blog_sub_prompts"
        self.prompt_folder_var = tk.StringVar(value=self.prompt_folder)
        self.ensure_prompt_folder_exists()
        
        # ========================================
        # 2. 프롬프트 파일 설정
        # ========================================
        self.prompt_1st_file = "blog_rewrite_1st.txt"
        self.prompt_2nd_file = "blog_rewrite_2nd.txt"
        self.current_1st_prompt = tk.StringVar(value=self.prompt_1st_file)
        self.current_2nd_prompt = tk.StringVar(value=self.prompt_2nd_file)
        self.classifier_file_var = tk.StringVar(value="Naver blog topic classifier.json")

        # ========================================
        # 3. 모델 설정
        # ========================================

        # 1차 각색: GPT/Gemini 선택
        self.model_1st_type = tk.StringVar(value="GPT")
        self.gpt_model_1st = tk.StringVar(value="gpt-4.1-mini-2025-04-14")
        
        # 2차 각색: GPT/Gemini 선택
        self.model_2nd_type = tk.StringVar(value="GPT")
        self.gpt_model_2nd = tk.StringVar(value="gpt-4.1-mini-2025-04-14")
        self.claude_model_1st = tk.StringVar(value="claude-sonnet-4-5")
        self.claude_model_2nd = tk.StringVar(value="claude-sonnet-4-5")
        
        # ========================================
        # 4. Temperature 설정
        # ========================================
        self.temperature_1st = tk.DoubleVar(value=0.3)
        self.temperature_2nd = tk.DoubleVar(value=0.7)
        
        # ========================================
        # 5. 실행 모드 설정
        # ========================================
        self.rewrite_mode = tk.StringVar(value="both")  # first_only, second_only, both
        
        # ========================================
        # 6. API 클라이언트 초기화
        # ========================================
        self.openai_client = None
        self.gemini_client = None
        self.gemini_configured = False
        self.claude_client = None
        self.claude_configured = False
        #(step3 탭보다 먼저 선언해야 load_model_settings_from_config()에서 정상 로드됨)
        self.check_gpt_folder    = tk.BooleanVar(value=True)
        self.check_gemini_folder = tk.BooleanVar(value=True)
        self.check_claude_folder = tk.BooleanVar(value=True)
        # [Ver7.39 추가] 다중질문검색(종합완성판) "6)저장" 탭이 저장하는
        # perplexity_종합완성판_final_articles 폴더가 중복 검사 대상에서
        # 빠져 있던 문제 수정 - 기존 GPT/Gemini/Claude(단일질문용) 3개
        # 체크박스와 별도로 종합완성판용 체크박스를 추가.
        self.check_comprehensive_folder = tk.BooleanVar(value=True)

        # ========================================
        # 7. 대기 시간 설정
        # ========================================
        self.gpt_delay_between_stages = 3.0
        self.gpt_delay_between_files = 2.5
        
        # ========================================
        # 8. 통합 키워드 관리
        # ========================================
        self.duplicate_threshold = 50
        self.excel_keyword_filename_var = tk.StringVar(value="Naver_blog_지식인통합_keyword.xlsx")

        # ========================================
        # 9. 로그 버퍼 초기화
        # ========================================
        self._pending_logs = []

        # 주제 분류 외부 설정 로드
        self._classify_config = self._load_classify_config()

        # 매핑 설정 (로그 버퍼 초기화 후 호출)
        self.kin_mappings = {}
        self.load_kin_mapping()

        # ========================================
        # 10. 설정 로드
        # ========================================

        self.load_prompt_filename_from_config()
        self.load_model_settings_from_config()
        
        # ✅ 추가: 정지 플래그
        self.stop_rewrite_flag = False
        self._classify_secondary = ""  # 보조 분야 저장

        # ========================================
        # 11. GUI 생성
        # ========================================
        # 메인 프레임
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
        # 그리드 설정
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 1. 주제 선택 영역
        ttk.Label(main_frame, text="주제 선택:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        topic_frame = ttk.Frame(main_frame)
        topic_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        self.topic_var = tk.StringVar(value="경제-A-거시경제-경기-통화-금리")
        topics = ["경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품", "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원", "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사", "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"]
        self.topic_combo = ttk.Combobox(topic_frame, textvariable=self.topic_var, values=topics, state="readonly", width=40, height=11)
        self.topic_combo.grid(row=0, column=0, sticky=tk.W)

        # [Ver7.10 추가] 세로 공간을 새로 차지하지 않도록 주제 선택 콤보박스
        # "옆"(같은 행, topic_frame 안)에 배치. 매핑설정(⚙️)의 모델명만
        # 간단히 보여준다(프롬프트 파일명까지 넣으면 길어져서 제외).
        # 주제가 바뀔 때마다 self.topic_var trace(아래 12.항목 부근)로 자동 갱신.
        self.model_banner_label = tk.Label(
            topic_frame,
            text="📌 모델 정보 로딩 중...",
            bg="#E3F2FD", fg="Dark red",
            font=("맑은 고딕", 11, "bold"),
            anchor="w", justify=tk.LEFT
        )
        self.model_banner_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # 2. 주제 매핑설정 (Ver7.10: 파일 선택 UI는 자동화로 대체돼 제거,
        # 매핑설정 버튼만 유지)
        ttk.Label(main_frame, text="주제 매핑:").grid(row=1, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Button(main_frame, text="⚙️ 주제 매핑설정", command=self.open_kin_mapping_settings).grid(
            row=1, column=1, sticky=tk.W, pady=(5, 5))

        # 3. 기본 입출력 폴더 선택 영역
        ttk.Label(main_frame, text="기본 입출력 폴더:").grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 5))
        folder_frame.columnconfigure(0, weight=1)
        
        self.base_folder_var = tk.StringVar(value=self.base_folder)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.base_folder_var)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(folder_frame, text="폴더 선택", command=self.select_folder).grid(row=0, column=1)
        
        # 5. 탭 생성 (1단계/2단계/3단계)
        self.notebook = ttk.Notebook(main_frame, style='ColorTab.TNotebook')
        self.notebook.grid(row=4, column=0, columnspan=2, pady=(0, 5), sticky=(tk.W, tk.E, tk.N, tk.S))
    
        # 탭 생성
        self.create_step0_tab()
        self.create_prefilter_tab()
        self.create_step0_5_tab()
        # [Ver7.10] "텍스트→MD 변환" 워크플로우는 5)탭의 자동변환 버튼으로
        # 대체됐지만, 이 탭이 만드는 로그창(step1_log_text)은 self.log()가
        # 앱 전체에서 유일하게 쓰는 로그 표시 위치라 계속 필요하다.
        # → 탭은 남기고 내용만 "API설정"으로 단순화(create_step1_tab 참고).
        # 번호 순서(4=자료검증, 5=API설정)에 맞춰 교차검증을 먼저 생성한다.
        self.create_kin_verify_tab()
        self.create_step1_tab()
        self.create_step2_tab()
        self.create_web_1st_tab()
        self.create_web_2nd_tab()
        # [Ver7.85 신규] "8)2차 각색"에 섞여 있던 썸네일/인포그래픽 생성
        # 버튼을 분리한 전용 탭 - "9)통합 키워드" 바로 앞에 배치.
        self.create_thumbnail_tab()
        self.create_step3_tab()
        self.create_semi_migrated_tab()
        self.create_db_manage_tab()

        # ── [Ver7.08 추가] 상단 "주제 선택"과 각 탭(0-1·1·4·5·7·8)의 주제
        # 선택을 서로 동기화한다. 어느 한쪽에서 주제를 바꾸면 나머지
        # 전부 같은 주제로 맞춰진다. _topic_sync_lock으로 재귀 호출을
        # 막는다(동기화 도중 다시 동기화가 걸리는 것을 방지).
        self._topic_sync_lock = False
        self.topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.topic_var.get(), source='topic_var'))
        self.detail_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.detail_topic_var.get(), source='detail_topic_var'))
        self.perp_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.perp_topic_var.get(), source='perp_topic_var'))
        self.verify_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.verify_topic_var.get(), source='verify_topic_var'))
        self.web1st_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.web1st_topic_var.get().split('  (')[0], source='web1st_topic_var'))
        self.web2nd_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.web2nd_topic_var.get().split('  (')[0], source='web2nd_topic_var'))
        # [Ver7.87 수정] "9)썸네일/인포그래픽" 탭 콤보도 web1st/web2nd처럼
        # "주제명  (N개)" 표시형으로 바뀌어 접미사를 떼고 동기화해야 한다.
        self.thumb_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.thumb_topic_var.get().split('  (')[0], source='thumb_topic_var'))
        self.db_manage_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.db_manage_topic_var.get(), source='db_manage_topic_var'))
        self.semi_topic_var.trace_add(
            "write", lambda *_: self._sync_all_topic_selectors(self.semi_topic_var.get(), source='semi_topic_var'))

        # [Ver7.10 추가] 위 동기화 로직상 어떤 탭에서 주제를 바꾸든 결국
        # self.topic_var가 갱신되므로, 여기 하나만 걸어도 모든 경로에서
        # 배너가 실시간으로 따라간다.
        self.topic_var.trace_add("write", lambda *_: self._update_model_banner())
        self._update_model_banner()

        # [Ver7.10 추가] 예전엔 "파일 선택" 시 apply_kin_mapping()이 파일명
        # 기준으로 6)자동각색(API) 탭의 모델/프롬프트를 자동 세팅했는데,
        # 그 버튼을 없애면서 트리거가 사라졌다. 대신 주제가 바뀔 때마다
        # 주제 기준으로 매핑을 찾아 자동 적용한다. 이후 사용자가 6)탭에서
        # 직접 모델/프롬프트를 바꾸면 그 값이 그대로 유지된다(주제가 다시
        # 바뀌기 전까지는 자동 재적용되지 않음).
        self.topic_var.trace_add("write", lambda *_: self._apply_kin_mapping_by_topic(self.topic_var.get()))
        self._apply_kin_mapping_by_topic(self.topic_var.get())

        # [Ver7.10 추가] 탭을 전환해도 각 탭의 왼쪽 목록이 자동으로
        # 새로고침되지 않아 "다른 탭에서 방금 저장한 결과가 안 보인다"는
        # 문제가 있었다. 노트북 탭 전환 이벤트에 걸어서, 탭을 눌러 들어갈
        # 때마다 해당 탭 목록을 최신 상태로 다시 그린다.
        self.notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed)

        # 7. 진행 상황 텍스트 라벨
        self.progress_label = ttk.Label(main_frame, text="대기 중", foreground="blue", font=("", 9, "bold"))
        self.progress_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 2)) 
        
        # 8. 프로그레스 바
        self.progress = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5)) 
    
        # ========================================
        # 12. 시작 로그 출력
        # ========================================
        # 입력/출력 폴더 설정을 GUI 생성 후 반영
        if self.base_folder:
            self.base_folder_var.set(self.base_folder)
        if self.prompt_folder:
            self.prompt_folder_var.set(self.prompt_folder)
        
        self.root.after(100, self.log_startup_info)
        self.root.after(200, self._load_api_keys_async)
        self.root.after(400, self._check_classify_config_files)

        # ========================================
        # 13. 창 닫기 이벤트 바인딩
        # ========================================
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

    # ── [Ver7.08 추가] 주제 선택 동기화 ──
    def _sync_all_topic_selectors(self, new_topic, source=None):
        """상단 '주제 선택'과 1)퍼플렉시티수집·4)웹1차·5)웹2차·
        9)썸네일/인포그래픽·7)종합관리·8)반자동이식 탭의 주제 선택을
        모두 new_topic(순수 주제명, "  (N개)"
        표시 접미사 제외)으로 맞춘다.
        source: 이번 동기화를 시작한 변수 이름. 그 변수 자신은 이미 원하는
        값이므로 다시 set하지 않는다(불필요한 재대입/깜빡임 방지).
        self._topic_sync_lock으로 재귀 호출(동기화 도중 또 동기화가
        걸리는 것)을 막는다."""
        if getattr(self, '_topic_sync_lock', False):
            return
        self._topic_sync_lock = True
        try:
            # 상단 주제 선택 (순수 주제명)
            if source != 'topic_var' and hasattr(self, 'topic_var'):
                if self.topic_var.get() != new_topic:
                    self.topic_var.set(new_topic)

            # 0-1)질문 상세분석 탭 (순수 주제명)
            if source != 'detail_topic_var' and hasattr(self, 'detail_topic_var'):
                if self.detail_topic_var.get() != new_topic:
                    self.detail_topic_var.set(new_topic)

            # 1)퍼플렉시티수집 탭 (순수 주제명)
            if source != 'perp_topic_var' and hasattr(self, 'perp_topic_var'):
                if new_topic in getattr(self, '_perplexity_filename_map', {}) and self.perp_topic_var.get() != new_topic:
                    self.perp_topic_var.set(new_topic)

            # 2-1)퍼플렉시티 교차검증 탭 (순수 주제명)
            if source != 'verify_topic_var' and hasattr(self, 'verify_topic_var'):
                if self.verify_topic_var.get() != new_topic:
                    self.verify_topic_var.set(new_topic)

            # 4)웹1차 탭 ("주제명  (N개)" 표시형이라 콤보 목록에서 매칭되는 값을 찾아서 대입)
            if source != 'web1st_topic_var' and hasattr(self, 'web1st_combo'):
                for v in self.web1st_combo['values']:
                    if v.split('  (')[0] == new_topic:
                        if self.web1st_topic_var.get() != v:
                            self.web1st_topic_var.set(v)
                        break

            # 5)웹2차 탭 ("주제명  (N개)" 표시형)
            if source != 'web2nd_topic_var' and hasattr(self, 'web2nd_combo'):
                for v in self.web2nd_combo['values']:
                    if v.split('  (')[0] == new_topic:
                        if self.web2nd_topic_var.get() != v:
                            self.web2nd_topic_var.set(v)
                        break

            # [Ver7.87 수정] 9)썸네일/인포그래픽 탭 ("주제명  (N개)" 표시형 -
            # web1st/web2nd와 동일하게 콤보 목록에서 매칭되는 값을 찾아 대입)
            if source != 'thumb_topic_var' and hasattr(self, 'thumb_combo'):
                for v in self.thumb_combo['values']:
                    if v.split('  (')[0] == new_topic:
                        if self.thumb_topic_var.get() != v:
                            self.thumb_topic_var.set(v)
                        break

            # 7)종합관리 탭 (순수 주제명)
            if source != 'db_manage_topic_var' and hasattr(self, 'db_manage_topic_var'):
                if self.db_manage_topic_var.get() != new_topic:
                    self.db_manage_topic_var.set(new_topic)

            # 8)반자동이식 탭 (순수 주제명)
            if source != 'semi_topic_var' and hasattr(self, 'semi_topic_var'):
                if self.semi_topic_var.get() != new_topic:
                    self.semi_topic_var.set(new_topic)
        finally:
            self._topic_sync_lock = False

    # 설정파일 로딩 
    def log_startup_info(self):
        """시작 시 환경 정보 로그 출력"""
        # 기존 result_text 로그
        self.log("=" * 60)
        self.log("📁 환경 설정 완료")
        self.log(f"   설정 파일: Naver_blog_config_지식인.json (전용 설정 파일)")
        self.log(f"   작업 폴더: {self.base_folder}")
        self.log(f"   프롬프트 폴더: {self.prompt_folder}")
        self.log(f"   통합 키워드 파일: {self.get_excel_keyword_file_path()}")
        
        # 설정 파일 존재 여부
        if os.path.exists(self.get_kin_config_path()):
            self.log(f"✅ 설정 파일 존재")
        else:
            self.log(f"⚠️ 설정 파일 없음 (최초 실행 시 자동 생성됩니다)")


        # 폴더 존재 여부 확인
        if os.path.exists(self.base_folder):
            self.log(f"✅ 작업 폴더 준비 완료")
        else:
            self.log(f"📁 작업 폴더 생성됨")
        
        if os.path.exists(self.prompt_folder):
            self.log(f"✅ 프롬프트 폴더 준비 완료")
        
        input_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        if input_folder:
            self.log(f"📂 기본 입출력 폴더: {input_folder}")
        else:
            self.log(f"ℹ️ 기본 입출력 폴더: 미설정 (파일 선택 시 현재 폴더에서 시작)")
        
        self.log("🎯 프로그램이 준비되었습니다!")
        self.log("=" * 60)
        
        # ✅ 1단계 탭 로그
        self.log_to_step1("📁 환경 설정 로드 완료")
        self.log_to_step1("")
        
        # 설정 파일 정보
        config_file = self.get_kin_config_path()
        if os.path.exists(config_file):
            self.log_to_step1(f"✅ 설정 파일: Naver_blog_config_지식인.json")
        else:
            self.log_to_step1(f"⚠️ 설정 파일 없음: Naver_blog_config_지식인.json")
            self.log_to_step1(f"   (API 키는 수동으로 설정하세요)")


        self.log_to_step1("")
        
        # 작업 폴더 정보
        self.log_to_step1(f"📂 작업 폴더: {self.base_folder}")
        if os.path.exists(self.base_folder):
            try:
                subdirs = [d for d in os.listdir(self.base_folder) if os.path.isdir(os.path.join(self.base_folder, d))]
                self.log_to_step1(f"   주제 폴더: {len(subdirs)}개")
            except:
                pass
        else:
            self.log_to_step1(f"   상태: 자동 생성됨")
        
        self.log_to_step1("")
        
        
        # 통합 키워드 파일 정보
        self.log_to_step1(f"📊 통합 키워드 파일: Naver_blog_지식인통합_keyword.xlsx")

        if os.path.exists(self.get_excel_keyword_file_path()):
            self.log_to_step1(f"   경로: {self.get_excel_keyword_file_path()}")

        else:
            self.log_to_step1(f"   상태: 없음 (3단계 실행 시 자동 생성)")
        
        self.log_to_step1("")
        
        # API 키 상태
        if self.openai_client:
            self.log_to_step1("✅ OpenAI API 키 로드 완료")
        else:
            self.log_to_step1("⚠️ OpenAI API 키 없음 (2단계 GPT 각색 사용 불가)")
        
        if self.gemini_configured:
            self.log_to_step1("✅ Gemini API 키 로드 완료")
        else:
            self.log_to_step1("ℹ️ Gemini API 키 없음 (선택사항)")

        if self.claude_configured:
            self.log_to_step1("✅ Claude API 키 로드 완료")
        else:
            self.log_to_step1("ℹ️ Claude API 키 없음 (선택사항)")            
        
        self.log_to_step1("=" * 80)
        
        # 모델 설정 정보
        self.log_to_step1("🤖 AI 모델 설정")
        self.log_to_step1("")
        
        # 1차 각색 정보
        self.log_to_step1(f"📍 1차 각색 모델: {self.model_1st_type.get()}")
        if self.model_1st_type.get() == "GPT":
            self.log_to_step1(f"   모델 버전: gpt-4.1-mini-2025-04-14")
        elif self.model_1st_type.get() == "Gemini":
            self.log_to_step1(f"   모델 버전: gemini-2.5-flash")
        elif self.model_1st_type.get() == "Claude":
             self.log_to_step1(f"   모델 버전: claude-sonnet-4-5")
        
        # 1차 프롬프트 파일 확인
        prompt_1st_path = os.path.join(self.prompt_folder, self.prompt_1st_file)
        if os.path.exists(prompt_1st_path):
            self.log_to_step1(f"   프롬프트: {self.prompt_1st_file} ✅")
        else:
            self.log_to_step1(f"   프롬프트: {self.prompt_1st_file} ⚠️ 파일 없음")
        
        self.log_to_step1(f"   Temperature: {self.temperature_1st.get()}")
        
        self.log_to_step1("")
        
        # 2차 각색 정보
        self.log_to_step1(f"📍 2차 각색 모델: {self.model_2nd_type.get()}")
        if self.model_2nd_type.get() == "GPT":
            self.log_to_step1(f"   모델 버전: gpt-4.1-mini-2025-04-14")
        elif self.model_2nd_type.get() == "Gemini":
            self.log_to_step1(f"   모델 버전: gemini-2.5-flash")
        elif self.model_2nd_type.get() == "Claude":
            self.log_to_step1(f"   모델 버전: claude-sonnet-4-5")
        
        # 2차 프롬프트 파일 확인
        prompt_2nd_path = os.path.join(self.prompt_folder, self.prompt_2nd_file)
        if os.path.exists(prompt_2nd_path):
            self.log_to_step1(f"   프롬프트: {self.prompt_2nd_file} ✅")
        else:
            self.log_to_step1(f"   프롬프트: {self.prompt_2nd_file} ⚠️ 파일 없음")
        
        self.log_to_step1(f"   Temperature: {self.temperature_2nd.get()}")
        
        self.log_to_step1("")
        
        # 실행 모드
        mode_text = {
            "first_only": "1차 각색만 실행",
            "second_only": "2차 각색만 실행", 
            "both": "1차+2차 각색 모두 실행"
        }
        self.log_to_step1("=" * 60)
        self.log_to_step1(f"⚙️ 실행 모드: {mode_text.get(self.rewrite_mode.get(), self.rewrite_mode.get())}")
        
    def log_to_step1(self, message):
        """1단계 탭 로그에 메시지 추가 (thread-safe)"""
        if hasattr(self, 'step1_log_text'):
            def _do():
                self.step1_log_text.config(state=tk.NORMAL)
                self.step1_log_text.insert(tk.END, message + "\n")
                self.step1_log_text.see(tk.END)
                self.step1_log_text.config(state=tk.DISABLED)
            self.root.after(0, _do)

    def select_prompt_file(self, prompt_type='1st'):
        """
        프롬프트 파일 선택 다이얼로그
        
        Args:
            prompt_type: '1st' 또는 '2nd'
        """
        # 기본 경로를 프롬프트 폴더로 설정
        pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        initial_dir = pf if os.path.exists(pf) else "."
        
        file_path = filedialog.askopenfilename(
            title=f"{prompt_type}차 각색 프롬프트 파일 선택",
            initialdir=initial_dir,
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            # 선택한 파일명만 추출
            filename = os.path.basename(file_path)
            
            # prompt_type에 따라 저장
            if prompt_type == '1st':
                self.prompt_1st_file = filename
                self.current_1st_prompt.set(filename)
                self.log(f"✅ 1차 프롬프트 변경: {filename}")
                # 파일명으로 모델 자동 감지
                if filename.startswith("Claude_"):
                    self.model_1st_type.set("Claude")
                    self.update_model_1st_state()
                    self.log(f"🤖 1차 모델 자동 변경: Claude")
                elif filename.startswith("GPT_"):
                    self.model_1st_type.set("GPT")
                    self.update_model_1st_state()
                    self.log(f"🤖 1차 모델 자동 변경: GPT")
                elif filename.startswith("재미나이_"):
                    self.model_1st_type.set("Gemini")
                    self.update_model_1st_state()
                    self.log(f"🤖 1차 모델 자동 변경: Gemini")
            elif prompt_type == '2nd':
                self.prompt_2nd_file = filename
                self.current_2nd_prompt.set(filename)
                self.log(f"✅ 2차 프롬프트 변경: {filename}")
                # 파일명으로 모델 자동 감지
                if filename.startswith("Claude_"):
                    self.model_2nd_type.set("Claude")
                    self.update_gpt_2nd_state()
                    self.log(f"🤖 2차 모델 자동 변경: Claude")
                elif filename.startswith("GPT_"):
                    self.model_2nd_type.set("GPT")
                    self.update_gpt_2nd_state()
                    self.log(f"🤖 2차 모델 자동 변경: GPT")
                elif filename.startswith("재미나이_"):
                    self.model_2nd_type.set("Gemini")
                    self.update_gpt_2nd_state()
                    self.log(f"🤖 2차 모델 자동 변경: Gemini")
            
            # 설정 저장
            self.save_prompt_filename_to_config()

    def show_error(self, title, msg):
        """심각한 에러 - 로그 + 팝업 (스레드 안전)"""
        self.log(f"❌ {msg}")
        self.root.after(0, lambda: messagebox.showerror(title, msg))

    def ensure_prompt_folder_exists(self):
        """프롬프트 폴더가 없으면 생성"""
        try:
            folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                self.log(f"📁 프롬프트 폴더 생성: {folder}")
        except Exception as e:
            self.log(f"❌ 프롬프트 폴더 생성 실패: {str(e)}")
    
    def select_prompt_folder(self):
        """프롬프트 폴더 선택"""
        current = self.prompt_folder_var.get().strip()
        initial_dir = current if current and os.path.exists(current) else "."
        folder_path = filedialog.askdirectory(
            title="프롬프트 폴더 선택",
            initialdir=initial_dir
        )
        if folder_path:
            self.prompt_folder = folder_path
            self.prompt_folder_var.set(folder_path)
            self.save_model_settings_to_config()
            self.log(f"✅ 프롬프트 폴더 설정: {folder_path}")


    def load_prompt_from_file(self, prompt_type='1st'):
        """서브폴더에서 GPT 프롬프트 로드 (강화된 검증)"""
        try:
            # 선택된 프롬프트 파일명 가져오기
            if prompt_type == '1st':
                filename = self.prompt_1st_file
            elif prompt_type == '2nd':
                filename = self.prompt_2nd_file
            else:
                filename = self.prompt_1st_file
            
            if not filename or filename.strip() == '':
                self.show_error("프롬프트 오류", f"{prompt_type}차 프롬프트 파일명이 설정되지 않았습니다.")
                return None
            
            prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') and self.prompt_folder_var.get().strip() else self.prompt_folder
            full_path = os.path.join(prompt_folder, filename)
            
            # 폴더 자체가 없는 경우 먼저 체크
            if not os.path.exists(prompt_folder):
                self.show_error("프롬프트 오류", 
                    f"프롬프트 폴더가 존재하지 않습니다:\n{prompt_folder}\n\n"
                    f"2단계 탭에서 프롬프트 폴더를 다시 설정하세요.")
                return None

            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read().strip()

                # ========================================
                # ✅ 강화된 검증 시작
                # ========================================
                
                # 1. 최소 길이 검사 (200자)
                if len(prompt_content) < 200:
                    self.log(f"⚠️ 프롬프트가 너무 짧습니다: {len(prompt_content)}자 (최소 200자)")
                    return None
                
                # 2. 라인 수 검사 (10줄 이상)
                lines = [line.strip() for line in prompt_content.split('\n') if line.strip()]
                if len(lines) < 10:
                    self.log(f"⚠️ 프롬프트 라인이 부족합니다: {len(lines)}줄 (최소 10줄)")
                    return None
                
                # 3. 지시문 존재 확인
                has_instructions = any(
                    marker in prompt_content 
                    for marker in ['금지', '필수', '반드시', '해야', '하세요']
                )
                if not has_instructions:
                    self.log(f"⚠️ 프롬프트에 지시문(금지/필수/반드시)이 없습니다")
                    # 경고만 하고 계속 진행
                
                # 4. 타입별 특화 패턴 검사
                if prompt_type == '1st':
                    patterns = [
                        r'정보.*보존|보존.*정보|원문.*유지',
                        r'블록|섹션|단락|구조',
                        r'수치|날짜|숫자',
                    ]
                    found = sum(1 for p in patterns if re.search(p, prompt_content))
                    if found < 2:
                        self.log(f"⚠️ 1차 프롬프트 특화 패턴 부족: {found}/3개 발견")
                        self.log(f"   (정보보존, 블록구조, 수치 관련 키워드 권장)")
                        
                elif prompt_type == '2nd':
                    patterns = [
                        r'자연스럽|자연스러운',
                        r'블로그|포스팅|글',
                        r'문체|톤|어투',
                    ]
                    found = sum(1 for p in patterns if re.search(p, prompt_content))
                    if found < 2:
                        self.log(f"⚠️ 2차 프롬프트 특화 패턴 부족: {found}/3개 발견")
                        self.log(f"   (자연스러움, 블로그글, 문체/톤 관련 키워드 권장)")
                
                # 5. 최종 로그
                self.log(f"✅ 프롬프트 로드: {filename}")
                self.log(f"   - 길이: {len(prompt_content)}자")
                self.log(f"   - 라인: {len(lines)}줄")
                
                return prompt_content
                
            else:
                self.show_error("프롬프트 오류", f"프롬프트 파일이 없습니다:\n{full_path}")
                return None
                
        except Exception as e:
            self.show_error("프롬프트 오류", f"프롬프트 로드 실패: {str(e)}")
            return None


    # GPT 각색 프롬프트를 환경파일에서 읽어 옴
    def load_prompt_filename_from_config(self):
        """config에서 프롬프트 파일명 로드 (1차/2차 모두)"""
        try:
            import json
            config_path = self.get_kin_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # ✅ 1차 프롬프트 로드
                saved_1st = config.get('prompt_1st_filename', '')
                if saved_1st:
                    self.prompt_1st_file = saved_1st
                    self.current_1st_prompt.set(saved_1st)
                    self.log(f"✅ 1차 프롬프트 로드: {saved_1st}")
                else:
                    # 파일명 없으면 빈 문자열로 설정
                    self.prompt_1st_file = ''
                    self.current_1st_prompt.set('')
                
                # ✅ 2차 프롬프트 로드
                saved_2nd = config.get('prompt_2nd_filename', '')
                if saved_2nd:
                    self.prompt_2nd_file = saved_2nd
                    self.current_2nd_prompt.set(saved_2nd)
                    self.log(f"✅ 2차 프롬프트 로드: {saved_2nd}")
                else:
                    # 파일명 없으면 빈 문자열로 설정
                    self.prompt_2nd_file = ''
                    self.current_2nd_prompt.set('')
                    
            else:
                self.log("ℹ️ config 파일 없음 (프롬프트 파일을 선택하세요)")
                # config 파일이 없으면 빈 문자열로 초기화
                self.prompt_1st_file = ''
                self.current_1st_prompt.set('')
                self.prompt_2nd_file = ''
                self.current_2nd_prompt.set('')
                
        except Exception as e:
            self.log(f"⚠️ 프롬프트 설정 로드 실패: {str(e)}")


    # GPT 각색 프롬프트를 환경파일에 저장함
    def save_prompt_filename_to_config(self):
        """config에 프롬프트 파일명 저장 (1차/2차 모두)"""
        try:
            import json
            
            config_path = self.get_kin_config_path()
            
            # 기존 config 읽기 (없으면 빈 dict)
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # ✅ 1차/2차 프롬프트 파일명 모두 저장
            config['prompt_1st_filename'] = self.prompt_1st_file
            config['prompt_2nd_filename'] = self.prompt_2nd_file
            
            # config 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.log(f"💾 프롬프트 설정 저장 완료")
            
        except Exception as e:
            self.log(f"❌ 프롬프트 설정 저장 실패: {str(e)}")    

    # ── [Ver7.10 추가] "사용한 질문/자료 숨기기" 체크박스 등 자잘한 UI 설정을
    # Naver_blog_config_지식인.json의 "ui_settings" 하위에 저장/로드한다.
    # 팝업(질문/1차자료/원자료 피커)이 열릴 때마다 저장된 값을 그대로 읽어와
    # 매번 다시 체크할 필요가 없게 한다.
    def load_kin_ui_setting(self, key, default=False):
        """ui_settings에서 값 하나 로드 (없으면 default 반환)"""
        try:
            config_path = self.get_kin_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('ui_settings', {}).get(key, default)
        except Exception as e:
            self.log(f"⚠️ UI 설정 로드 실패({key}): {str(e)}")
        return default

    def save_kin_ui_setting(self, key, value):
        """ui_settings에 값 하나 저장 (체크박스 등 즉시 반영되는 UI 설정용)"""
        try:
            config_path = self.get_kin_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            config.setdefault('ui_settings', {})[key] = value
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"⚠️ UI 설정 저장 실패({key}): {str(e)}")

    # [Ver7.10 추가] 노트북 탭 전환 시 호출 - 방금 다른 탭에서 저장한
    # 결과가 그 탭 목록에 바로 반영되도록 새로고침한다.
    def _on_notebook_tab_changed(self, event=None):
        try:
            current = self.notebook.select()
            tab_text = self.notebook.tab(current, "text")
        except Exception:
            return

        # [Ver7.86 버그수정] "3)"·"4)" 키가 실제 탭 라벨과 어긋나 있어(과거
        # 탭 이름이 "3)퍼플렉시티 자료수집"/"4)퍼플렉시티 자료검증"이던 시절의
        # 잔재로 추정 - 이후 각각 "3)퍼플렉시티 수집", "4)퍼플렉시티
        # 자료검증(클로드)"로 이름이 바뀌었는데 여기는 안 따라와 있었음),
        # 이 두 탭은 탭을 전환해 들어갈 때마다 목록이 최신 상태로 갱신되지
        # 않는 문제가 있었다(초기 로드분만 보이고, 다른 탭에서 작업한 뒤
        # 돌아와도 새로 생긴 항목이 안 뜸). 실제 탭 텍스트와 정확히 일치하도록
        # 수정. ("9)썸네일/인포그래픽" 탭은 파일을 스캔해 만드는 목록 자체가
        # 없는 클립보드 왕복형 탭이라 여기 등록 대상이 아님.)
        refresh_map = {
            "2)질문 상세분석": getattr(self, '_detail_refresh_list', None),
            "3)퍼플렉시티 수집": getattr(self, '_perp_refresh_list', None),
            "4)퍼플렉시티 자료검증(클로드)": getattr(self, '_verify_refresh_list', None),
            "7)1차 각색": getattr(self, '_web1st_refresh_list', None),
            "8)2차 각색": getattr(self, '_web2nd_refresh_list', None),
            # [Ver7.87 추가] "9)썸네일/인포그래픽" 탭에도 완성 자료 좌측
            # 목록이 생겨서 다른 탭들과 동일하게 탭 전환 시 새로고침 필요.
            "9)썸네일/인포그래픽": getattr(self, '_thumb_refresh_list', None),
        }
        fn = refresh_map.get(tab_text)
        if fn:
            fn()

        # [Ver9.06 신규] "9)썸네일/인포그래픽" 탭은 좌측 목록만 새로고침하고
        # 우측 본문칸(thumb_text)은 그대로 둬서, 이 탭을 나갔다가 다시
        # 들어오면 예전에 선택했던 글 내용이 지금 목록과 안 맞는 채로 남아
        # 있는 문제가 있었다. 탭 진입 시마다 "내용 지우기"와 동일한
        # _clear_thumb_tab()을 호출해 우측을 항상 비우고, 좌측 트리뷰
        # 선택 하이라이트도 같이 해제한다 - 이제 새로 들어오면 우측은
        # 빈 상태로 시작하고, 좌측 목록을 클릭해야만 그 항목만 채워진다.
        if tab_text == "9)썸네일/인포그래픽" and hasattr(self, '_clear_thumb_tab'):
            self._clear_thumb_tab()
            if hasattr(self, 'thumb_list_tree'):
                try:
                    self.thumb_list_tree.selection_remove(*self.thumb_list_tree.selection())
                except Exception:
                    pass

        # 7)/8)탭은 목록 외에 주제 콤보의 (N개) 카운트도 같이 갱신
        if tab_text == "7)1차 각색" and hasattr(self, '_refresh_web1st_counts'):
            self._refresh_web1st_counts()
        elif tab_text == "8)2차 각색" and hasattr(self, '_refresh_web2nd_counts'):
            self._refresh_web2nd_counts()

    def get_kin_config_path(self):
        """Naver_blog_config_지식인.json 경로 반환"""
        return "Naver_blog_config_지식인.json"

    def get_kin_perplexity_config_path(self):
        """퍼플렉시티용 주제별 프롬프트 매핑 파일 경로 반환 (매핑설정과 별도 파일, base_folder 작업폴더 안에 저장)"""
        base_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        base_folder = base_folder or self.base_folder
        os.makedirs(base_folder, exist_ok=True)
        return os.path.join(base_folder, "Naver_blog_config_kin_perplexity.json")

    def load_kin_perplexity_prompts(self):
        """퍼플렉시티용 주제별 프롬프트 매핑 로드"""
        path = self.get_kin_perplexity_config_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('prompts', {})
        except Exception:
            return {}

    def save_kin_perplexity_prompts(self, prompts):
        """퍼플렉시티용 주제별 프롬프트 매핑 저장"""
        path = self.get_kin_perplexity_config_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)

    # ── [Ver7.08 추가] 사전 필터링(질문 선별)용 주제별 프롬프트 매핑 ──
    def get_kin_prefilter_config_path(self):
        """사전 필터링용 주제별 프롬프트 매핑 파일 경로 반환 (base_folder 작업폴더 안에 저장)"""
        base_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        base_folder = base_folder or self.base_folder
        os.makedirs(base_folder, exist_ok=True)
        return os.path.join(base_folder, "Naver_blog_config_kin_prefilter.json")

    def load_kin_prefilter_prompts(self):
        """사전 필터링용 주제별 프롬프트 매핑 로드"""
        path = self.get_kin_prefilter_config_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('prompts', {})
        except Exception:
            return {}

    def save_kin_prefilter_prompts(self, prompts):
        """사전 필터링용 주제별 프롬프트 매핑 저장"""
        path = self.get_kin_prefilter_config_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)

    # ── [Ver7.10 추가] "0-1)질문 상세분석" 탭용 주제별 프롬프트 설정.
    # 구조는 사전 필터링/퍼플렉시티 프롬프트 설정과 동일, 저장 파일만 다르다.
    def get_kin_detail_config_path(self):
        """질문 상세분석용 주제별 프롬프트 매핑 파일 경로 반환 (base_folder 작업폴더 안에 저장)"""
        base_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        base_folder = base_folder or self.base_folder
        os.makedirs(base_folder, exist_ok=True)
        return os.path.join(base_folder, "Naver_blog_config_kin_detail.json")

    def load_kin_detail_prompts(self):
        """질문 상세분석용 주제별 프롬프트 매핑 로드"""
        path = self.get_kin_detail_config_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('prompts', {})
        except Exception:
            return {}

    def save_kin_detail_prompts(self, prompts):
        """질문 상세분석용 주제별 프롬프트 매핑 저장"""
        path = self.get_kin_detail_config_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)

    # ── [Ver7.10 추가] "5)퍼플렉시티 자료검증" 탭용 주제별 프롬프트 설정.
    # 구조는 상세분석/사전필터링 프롬프트 설정과 동일, 저장 파일만 다르다.
    def get_kin_verify_config_path(self):
        """퍼플렉시티 교차검증용 주제별 프롬프트 매핑 파일 경로 반환"""
        base_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        base_folder = base_folder or self.base_folder
        os.makedirs(base_folder, exist_ok=True)
        return os.path.join(base_folder, "Naver_blog_config_kin_verify.json")

    def load_kin_verify_prompts(self):
        """퍼플렉시티 교차검증용 주제별 프롬프트 매핑 로드"""
        path = self.get_kin_verify_config_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('prompts', {})
        except Exception:
            return {}

    def save_kin_verify_prompts(self, prompts):
        """퍼플렉시티 교차검증용 주제별 프롬프트 매핑 저장"""
        path = self.get_kin_verify_config_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)

    # ── [Ver7.17 추가] 썸네일 프롬프트용 주제별 매핑.
    # 구조는 위 4개(퍼플렉시티/사전필터링/상세분석/교차검증) 프롬프트
    # 설정과 동일, 저장 파일만 다르다. 예전엔 KIN_THUMBNAIL_GROUP_MAP으로
    # "경제/교육/자동차" 3개 그룹만 묶어 작업폴더 안 파일명을 자동으로
    # 찾아 썼는데(건강·IT는 그룹조차 없어 아예 안 됐음), 이제 11개 주제
    # 각각을 이 설정 화면에서 직접 지정할 수 있다. 여기서 지정된 게
    # 있으면 그걸 최우선으로 쓰고(프롬프트 폴더 기준), 없으면 예전 방식
    # (그룹+작업폴더 파일명 스캔)으로 자동 대체한다.
    def get_kin_thumbnail_config_path(self):
        """썸네일 프롬프트용 주제별 매핑 파일 경로 반환"""
        base_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        base_folder = base_folder or self.base_folder
        os.makedirs(base_folder, exist_ok=True)
        return os.path.join(base_folder, "Naver_blog_config_kin_thumbnail.json")

    def _kin_gemini_key(self, topic):
        """[Ver7.58 신규] 주제별 재미나이 변환 프롬프트 저장용 키.
        C(GPT 썸네일)와 같은 딕셔너리(load_kin_thumbnail_prompts)에 같이
        저장하되, 키 이름만 구분해서 저장 구조를 새로 만들지 않는다."""
        return f"{topic}__GEMINI__"

    def _kin_get_gemini_prompt_filename(self, topic, thumbnail_prompts=None):
        """[Ver7.58 신규] 주제별 재미나이 변환 프롬프트 파일명을 조회한다.
        주제별 값이 아직 없으면(예전 방식 - 전체 주제 공용 1개만 있던 시절
        저장된 값) KIN_THUMBNAIL_GEMINI_KEY 공용 값을 폴백으로 써서, 기존에
        지정해둔 값이 마이그레이션 없이도 그대로 살아있게 한다."""
        if thumbnail_prompts is None:
            thumbnail_prompts = self.load_kin_thumbnail_prompts()
        per_topic = thumbnail_prompts.get(self._kin_gemini_key(topic), "")
        if per_topic:
            return per_topic
        return thumbnail_prompts.get(KIN_THUMBNAIL_GEMINI_KEY, "")

    def load_kin_thumbnail_prompts(self):
        """썸네일 프롬프트용 주제별 매핑 로드.
        [Ver7.69 수정] 예전에는 파일이 있는데 JSON 파싱에 실패하면(깨진 파일 등)
        아무 안내 없이 조용히 빈 딕셔너리를 반환했다 - 저장은 매번 정상적으로
        되고 있어도, 그 다음 읽기가 실패하면 설정 화면에는 마치 "아무것도
        저장 안 된 것"처럼 보여서 "저장이 안 된다"는 오해를 만들 수 있었다.
        이제는 파싱 실패 시 로그에 경고를 남겨 실제 원인(파일 손상 등)을
        구분할 수 있게 한다(반환값 자체는 기존과 동일하게 {}로 안전하게 처리)."""
        path = self.get_kin_thumbnail_config_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('prompts', {})
        except Exception as e:
            self.log(f"⚠️ 썸네일 프롬프트 설정 파일을 읽지 못했습니다({path}): {e} — 설정이 비어있는 것으로 처리됩니다.")
            return {}

    def save_kin_thumbnail_prompts(self, prompts):
        """썸네일 프롬프트용 주제별 매핑 저장"""
        path = self.get_kin_thumbnail_config_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)

    def open_kin_thumbnail_prompt_settings(self):
        """[Ver7.58 변경] 재미나이(D) 변환 프롬프트를 전체 주제 공용 1개에서
        주제별로 각각 지정할 수 있게 확장했다 - GPT 썸네일(C)과 나란히 한
        팝업, 한 줄에 같이 놓고 설정한다("다중질문검색"의 그룹별 C/D 동시
        설정 팝업과 동일한 패턴). 예전에 공용 1개로 지정해둔 값은 주제별
        값이 비어있는 동안 자동으로 폴백되어(_kin_get_gemini_prompt_filename)
        마이그레이션 없이 계속 동작한다."""
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        current = self.load_kin_thumbnail_prompts()

        popup = tk.Toplevel(self.root)
        popup.title("썸네일 프롬프트 설정 (주제별 C·D)")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 1360, 600
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()

        # [Ver7.20 수정] 자동탐색 폴백을 제거했으므로, 여기서 지정하지
        # 않은 주제는 예외 없이 썸네일 프롬프트를 만들 수 없다는 점을
        # 명확히 안내한다.
        ttk.Label(popup,
                  text="주제별로 프롬프트C(GPT 썸네일 인포그래픽 기획)와 프롬프트D(재미나이 변환)를 "
                       "나란히 지정하세요.\n"
                       "(자동탐색 폴백은 제거됐습니다 — 아래 11개 주제 모두 여기서 명시적으로 "
                       "지정해야 썸네일 프롬프트를 만들 수 있습니다. C를 비워두면 '🖼 썸네일 프롬프트 "
                       "복사' 클릭 시 안내 메시지만 뜨고 복사되지 않습니다. D는 GPT 이미지 생성이 "
                       "막혔을 때 대체용이라 비워둬도 무방합니다. 이 화면은 각 주제에 실제로 저장된 "
                       "값만 그대로 보여줍니다 — D가 빈칸인 주제는 실제 복사 시점에만 예전에 지정해둔 "
                       "공용값(있는 경우)으로 자동 대체되고, 이 화면에는 표시되지 않습니다.)",
                  foreground="gray", justify=tk.LEFT).pack(anchor="w", padx=10, pady=(10, 8))

        canvas_wrap = ttk.Frame(popup)
        canvas_wrap.pack(fill=tk.BOTH, expand=True, padx=10)
        body = ttk.Frame(canvas_wrap, padding=(0, 4))
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(3, weight=1)

        ttk.Label(body, text="주제", font=("", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        ttk.Label(body, text="프롬프트C (GPT 썸네일)", font=("", 9, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(body, text="프롬프트D (재미나이 변환)", font=("", 9, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5)

        c_vars, d_vars = {}, {}
        for i, topic in enumerate(topics, start=1):
            ttk.Label(body, text=topic).grid(row=i, column=0, sticky=tk.W, pady=3, padx=(0, 8))

            c_var = tk.StringVar(value=current.get(topic, ""))
            c_vars[topic] = c_var
            ttk.Entry(body, textvariable=c_var, width=42).grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

            def browse_c(v=c_var):
                pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else "."
                path = filedialog.askopenfilename(
                    title="GPT 썸네일 프롬프트 파일 선택", initialdir=pf or ".",
                    filetypes=[("텍스트/마크다운 파일", "*.txt *.md"), ("모든 파일", "*.*")])
                if path:
                    v.set(os.path.basename(path))

            ttk.Button(body, text="찾기", command=browse_c).grid(row=i, column=2, padx=(0, 12), pady=3)

            # [Ver7.69 수정] 실제 버그 지점 — 예전에는 주제별 값이 비어있으면
            # 화면에 레거시 공용값(KIN_THUMBNAIL_GEMINI_KEY)을 항상 미리
            # 채워서 보여줬다. 그 결과 아직 한 번도 개별 지정하지 않은
            # 주제 10개가 전부 "이미 뭔가 채워진" 것처럼 보이고, 사용자가
            # 특정 주제만 새 값으로 바꿔 저장해도 나머지 주제를 다시 열어보면
            # 여전히 그 예전 공용값 그대로라서 "내가 입력한 게 저장이 안
            # 된다/코드에 박혀있다"는 오해를 만들었다(실제로는 저장은 매번
            # 정상적으로 되고 있었고, 화면 표시 로직이 실제 저장값과
            # 레거시 폴백값을 구분 없이 섞어 보여준 것이 문제).
            # 이제 설정 화면에는 "이 주제에 실제로 저장된 값"만 그대로
            # 보여준다(없으면 빈칸). 레거시 공용값으로의 자동 대체는
            # 화면 표시가 아니라 실제 사용 시점(_kin_get_gemini_prompt_
            # filename, 프롬프트 복사 버튼을 눌렀을 때)에만 적용되도록
            # 유지해 하위호환은 그대로 살아있다.
            d_default = current.get(self._kin_gemini_key(topic), "")
            d_var = tk.StringVar(value=d_default)
            d_vars[topic] = d_var
            ttk.Entry(body, textvariable=d_var, width=42).grid(row=i, column=3, sticky=(tk.W, tk.E), padx=5, pady=3)

            def browse_d(v=d_var):
                pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else "."
                path = filedialog.askopenfilename(
                    title="재미나이 변환 프롬프트 파일 선택", initialdir=pf or ".",
                    filetypes=[("텍스트/마크다운 파일", "*.txt *.md"), ("모든 파일", "*.*")])
                if path:
                    v.set(os.path.basename(path))

            ttk.Button(body, text="찾기", command=browse_d).grid(row=i, column=4, padx=5, pady=3)

        def do_save():
            new_prompts = {}
            for t in topics:
                c_val = c_vars[t].get().strip()
                if c_val:
                    new_prompts[t] = c_val
                d_val = d_vars[t].get().strip()
                if d_val:
                    new_prompts[self._kin_gemini_key(t)] = d_val
            # [Ver7.58] 예전 공용 키(KIN_THUMBNAIL_GEMINI_KEY)는 더 이상 이
            # 팝업에서 편집하지 않지만, 혹시 아직 주제별 값을 하나도 안 채운
            # 주제가 있을 때의 폴백을 위해 기존 값이 있었으면 그대로 보존한다
            # (저장을 반복해도 예전 값이 사라지지 않도록).
            if current.get(KIN_THUMBNAIL_GEMINI_KEY, ""):
                new_prompts[KIN_THUMBNAIL_GEMINI_KEY] = current[KIN_THUMBNAIL_GEMINI_KEY]
            self.save_kin_thumbnail_prompts(new_prompts)
            self.log(f"💾 썸네일 프롬프트 설정 저장 완료: {len(new_prompts)}개")
            popup.destroy()

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="저장", command=do_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="취소", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    def load_kin_mapping(self):
        """매핑 설정 로드"""
        try:
            import json
            path = self.get_kin_config_path()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.kin_mappings = data.get('mappings', {})
                self.log(f"✅ 매핑 설정 로드: {len(self.kin_mappings)}개")
            else:
                self.kin_mappings = {}
        except Exception as e:
            self.log(f"⚠️ 매핑 설정 로드 실패: {str(e)}")
            self.kin_mappings = {}
    
    
    def save_kin_mapping(self):
        """매핑 설정 저장"""
        try:
            import json
            path = self.get_kin_config_path()
            
            # 기존 config 읽기 (없으면 빈 dict)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # mappings 키만 업데이트
            config['mappings'] = self.kin_mappings
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.log(f"💾 매핑 설정 저장 완료: {path}")
        except Exception as e:
            self.log(f"❌ 매핑 설정 저장 실패: {str(e)}")
    
    def _apply_kin_mapping_by_topic(self, topic):
        for key, mapping in getattr(self, 'kin_mappings', {}).items():
            if mapping.get('topic', '') != topic:
                continue

            model_1st = mapping.get('model_1st', '')
            if model_1st:
                self.model_1st_type.set(model_1st)
                self.update_model_1st_state()

            prompt_1st = mapping.get('prompt_1st', '')
            if prompt_1st:
                self.prompt_1st_file = prompt_1st
                self.current_1st_prompt.set(prompt_1st)

            model_2nd = mapping.get('model_2nd', '')
            if model_2nd:
                self.model_2nd_type.set(model_2nd)
                self.update_gpt_2nd_state()

            prompt_2nd = mapping.get('prompt_2nd', '')
            if prompt_2nd:
                self.prompt_2nd_file = prompt_2nd
                self.current_2nd_prompt.set(prompt_2nd)

            self.log(f"✅ 주제 매핑 자동 적용 [{topic}]: 1차={model_1st}/{prompt_1st} | 2차={model_2nd}/{prompt_2nd}")
            return True
        return False

    def open_kin_mapping_settings(self):
        """매핑 설정 팝업"""
        import json
    
        popup = tk.Toplevel(self.root)
        popup.title("입력파일 매핑 설정")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 1400, 700
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()
    
        # 작업용 매핑 복사
        work_mappings = {k: dict(v) for k, v in self.kin_mappings.items()}
    
        # ── 상단: 목록 ──
        list_frame = ttk.LabelFrame(popup, text="매핑 목록", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    
        columns = ('주제', '입력파일', '1차모델', '1차프롬프트', '2차모델', '2차프롬프트')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        widths = {'주제': 150, '입력파일': 230, '1차모델': 60, '1차프롬프트': 240, '2차모델': 60, '2차프롬프트': 240}
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col])

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        def refresh_tree():
            tree.delete(*tree.get_children())
            for key, val in work_mappings.items():
                tree.insert('', tk.END, iid=key, values=(
                    val.get('topic', ''),
                    val.get('input_file', ''),
                    val.get('model_1st', ''),
                    val.get('prompt_1st', ''),
                    val.get('model_2nd', ''),
                    val.get('prompt_2nd', '')
                ))
    
        refresh_tree()
    
        # ── 중단: 편집 영역 ──
        edit_frame = ttk.LabelFrame(popup, text="추가 / 수정", padding="8")
        edit_frame.pack(fill=tk.X, padx=10, pady=5)
        edit_frame.columnconfigure(1, weight=1)
    
        topics = ["경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
                  "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
                  "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
                  "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"]

        topic_var     = tk.StringVar()
        input_var     = tk.StringVar()
        model_1st_var = tk.StringVar(value="Claude")
        prompt_1st_var = tk.StringVar()
        model_var     = tk.StringVar(value="Claude")
        prompt_var    = tk.StringVar()
    
        ttk.Label(edit_frame, text="주제:").grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Combobox(edit_frame, textvariable=topic_var, values=topics, state="readonly", width=50, height=11).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=3)
    
        ttk.Label(edit_frame, text="입력파일:").grid(row=1, column=0, sticky=tk.W, pady=3)
        input_entry = ttk.Entry(edit_frame, textvariable=input_var, width=75)
        input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
    
        def browse_input():
            initial_dir = self.base_folder_var.get().strip() or "."
            path = filedialog.askopenfilename(
                title="입력 파일 선택", initialdir=initial_dir,
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
            if path:
                input_var.set(os.path.basename(path))
    
        ttk.Button(edit_frame, text="찾기", command=browse_input).grid(row=1, column=2, padx=5)
    
        # ── [Ver7.10 추가] 1차 모델/프롬프트 (2차와 완전히 동일한 구조, 대상만 1차) ──
        ttk.Label(edit_frame, text="1차 모델:").grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Combobox(edit_frame, textvariable=model_1st_var,
                     values=["GPT", "Gemini", "Claude"], state="readonly", width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=3)
    
        ttk.Label(edit_frame, text="1차 프롬프트:").grid(row=3, column=0, sticky=tk.W, pady=3)
        ttk.Entry(edit_frame, textvariable=prompt_1st_var, width=75).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
    
        def browse_prompt_1st():
            pf = self.prompt_folder_var.get().strip() or "."
            path = filedialog.askopenfilename(
                title="1차 프롬프트 파일 선택", initialdir=pf,
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
            if path:
                prompt_1st_var.set(os.path.basename(path))
    
        ttk.Button(edit_frame, text="찾기", command=browse_prompt_1st).grid(row=3, column=2, padx=5)
    
        ttk.Label(edit_frame, text="2차 모델:").grid(row=4, column=0, sticky=tk.W, pady=3)
        ttk.Combobox(edit_frame, textvariable=model_var,
                     values=["GPT", "Gemini", "Claude"], state="readonly", width=10).grid(
            row=4, column=1, sticky=tk.W, padx=5, pady=3)
    
        ttk.Label(edit_frame, text="2차 프롬프트:").grid(row=5, column=0, sticky=tk.W, pady=3)
        ttk.Entry(edit_frame, textvariable=prompt_var, width=75).grid(
            row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
    
        def browse_prompt():
            pf = self.prompt_folder_var.get().strip() or "."
            path = filedialog.askopenfilename(
                title="2차 프롬프트 파일 선택", initialdir=pf,
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
            if path:
                prompt_var.set(os.path.basename(path))
    
        ttk.Button(edit_frame, text="찾기", command=browse_prompt).grid(row=5, column=2, padx=5)
    
        # 현재 선택된 key 추적 (기존 key 삭제용)
        selected_key = {'value': None}

        # 목록 선택 시 편집 영역 자동 채우기
        def on_tree_select(event):
            sel = tree.selection()
            if not sel:
                return
            key = sel[0]
            selected_key['value'] = key
            val = work_mappings.get(key, {})
            topic_var.set(val.get('topic', ''))
            input_var.set(val.get('input_file', ''))
            model_1st_var.set(val.get('model_1st', 'Claude'))
            prompt_1st_var.set(val.get('prompt_1st', ''))
            model_var.set(val.get('model_2nd', 'Claude'))
            prompt_var.set(val.get('prompt_2nd', ''))

        tree.bind('<<TreeviewSelect>>', on_tree_select)
    
        # ── 하단: 버튼 ──
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=8)


        def add_mapping():
            topic = topic_var.get().strip()
            input_file = input_var.get().strip()
            model_1st = model_1st_var.get().strip()
            prompt_1st = prompt_1st_var.get().strip()
            model_2nd = model_var.get().strip()
            prompt_2nd = prompt_var.get().strip()
            if not topic or not input_file:
                messagebox.showwarning("입력 오류", "주제와 입력파일은 필수입니다.", parent=popup)
                return

            key = input_file
            new_val = {
                'topic': topic,
                'input_file': input_file,
                'model_1st': model_1st,
                'prompt_1st': prompt_1st,
                'model_2nd': model_2nd,
                'prompt_2nd': prompt_2nd
            }

            old_key = selected_key['value']
            is_rename = old_key and old_key != key and old_key in work_mappings

            if is_rename:
                # 파일명 변경: 기존 위치 유지하며 key 교체
                new_work = {}
                for k, v in work_mappings.items():
                    if k == old_key:
                        new_work[key] = new_val
                    else:
                        new_work[k] = v
                work_mappings.clear()
                work_mappings.update(new_work)
                self.log(f"✏️ 매핑 수정(파일명 변경): {old_key} → {key}")
            elif key in work_mappings:
                # 동일 key 수정: 위치 그대로
                work_mappings[key] = new_val
                self.log(f"✏️ 매핑 수정: {key}")
            else:
                # 새 항목 추가
                work_mappings[key] = new_val
                self.log(f"➕ 매핑 추가: {key}")

            # 새 추가 후 selected_key 초기화 (다음 추가 시 오작동 방지)
            selected_key['value'] = key if key in work_mappings else None
            refresh_tree()

        def delete_mapping():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("선택 없음", "삭제할 항목을 선택하세요.", parent=popup)
                return
            key = sel[0]
            if messagebox.askyesno("삭제 확인", f"'{key}' 매핑을 삭제하시겠습니까?", parent=popup):
                del work_mappings[key]
                refresh_tree()

        def save_and_close():
            self.kin_mappings = work_mappings
            self.save_kin_mapping()
            self._update_model_banner()  # [Ver7.10 추가] 매핑 저장 즉시 상단 배너에 반영
            self._apply_kin_mapping_by_topic(self.topic_var.get())  # [Ver7.10 추가] 6)탭 모델/프롬프트도 즉시 반영
            messagebox.showinfo("저장 완료", "매핑 설정이 저장되었습니다.", parent=popup)

        ttk.Button(btn_frame, text="➕ 추가/수정", command=add_mapping, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ 삭제", command=delete_mapping, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 저장", command=save_and_close, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ 닫기", command=popup.destroy, width=12).pack(side=tk.LEFT, padx=5)
        ### 자동 매핑을 위한 메소드 그룹 ,, 하단 


    def select_folder(self):
        folder_path = filedialog.askdirectory(title="기본 입출력 폴더 선택")
        if folder_path:
            self.base_folder_var.set(folder_path)
            self.save_model_settings_to_config()
            self.log(f"✅ 기본 입출력 폴더 설정: {folder_path}")
    

    # 1. create_output_directory 메서드 수정
    def create_output_directory(self, base_dir, topic):
        """
        Create folder structure: base_dir/topic/2025-09-10/perplexity_answers
        기본 폴더가 없으면 자동 생성
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 기본 디렉토리가 존재하지 않으면 생성
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
                self.log(f"✅ 기본 작업폴더가 생성되었습니다: {base_dir}")
            
            # Create folder path: base_dir/topic/date/perplexity_answers
            topic_folder = Path(base_dir) / topic / today / "perplexity_answers"
            topic_folder.mkdir(parents=True, exist_ok=True)
            
            self.log(f"📁 출력 폴더가 준비되었습니다: {topic_folder}")
            
            return str(topic_folder)
            
        except Exception as e:
            self.log(f"❌ 폴더 생성 실패: {str(e)}")
            raise Exception(f"폴더 생성 중 오류가 발생했습니다: {str(e)}")

    
    def extract_markdown_content(self, text):
        """
        Extract markdown content from text
        """
        # Find question summary section
        # ✅ 수정: \n# 다음에 공백이 있는 것만 H1으로 인식 (해시태그와 구분)
        summary_pattern = r'(##### 질문 요약.*?)(?=\n+# [^#]|$)'
        summary_match = re.search(summary_pattern, text, re.DOTALL)
        summary_content = ""
        if summary_match:
            summary_content = summary_match.group(1).strip()
        
        # Find markdown content start point (from # title)
        markdown_start = re.search(r'(?:^|\n)(# [^#].*)', text)
        if not markdown_start:
            return None, ""
        
        # group(1) = # 제목 본문만 (앞의 \n 제외)
        title_line = markdown_start.group(1).strip()
        title = title_line.replace('# ', '', 1).strip()
        
        start_pos = markdown_start.start()
        if text[start_pos] == '\n':
            start_pos += 1

        markdown_content = text[start_pos:]

        # Find #### 질문내용 section if exists
        question_content_match = re.search(r'(#### 질문내용.*?)(?=##### 질문 요약|$)', text, re.DOTALL)
        question_content = ""
        if question_content_match:
            question_content = question_content_match.group(1).strip()
        
        # Combine final content: ##### 질문 요약 + # title~[[강조]] + #### 질문내용
        final_content = ""
        if summary_content:
            final_content += summary_content + "\n\n"
        
        final_content += markdown_content.strip()
        
        if question_content:
            final_content += "\n\n" + question_content
        
        # Remove [web:number] patterns
        # [2026-09-27 수정] 기존에는 "web:"(영문)만 잡아서 "[웹:106]"처럼
        # 한글 라벨이 붙은 각주(퍼플렉시티가 한글 UI에서 만들어내는 형태)는
        # 그대로 남는 문제가 있었다(사용자 실측 확인). 라벨 부분을 "web"
        # 고정 문자열이 아니라 "대괄호 안, 콜론 앞의 임의 짧은 텍스트"로
        # 일반화해 "[web:3]"·"[웹:106]"·"[학술:12]" 등을 모두 잡는다.
        final_content = re.sub(r'\[[^\[\]\n:]{1,12}:\d+\]', '', final_content)  # [web:3], [웹:106] 등
        final_content = re.sub(r'\[\d+\]', '', final_content)       # [8], [11] 등

        # Clean up unnecessary spaces
        final_content = re.sub(r'\n\s*\n\s*\n', '\n\n', final_content)

        # [Ver8.30 수정] "```"만 제거하던 기존 정규식은 "```markdown"처럼
        # 언어 태그가 붙은 펜스를 못 잡았다(백틱 뒤 \s*가 "markdown" 같은
        # 글자는 못 건너뜀). 여러 질문을 이어붙인 통합 파일을 "##### 질문
        # 요약" 기준으로 쪼갤 때 다음 질문의 여는 펜스("```markdown")가
        # 현재 섹션 끝에 딸려 들어오는 경우도 있어 끝쪽에서도 언어 태그
        # 붙은 펜스가 남을 수 있었다. 위치(맨 앞/중간에 끼어든 경우/맨 끝)와
        # 무관하게, 펜스 기호만 있는 줄을 전부 제거한다(줄 전체가 이
        # 패턴에만 정확히 일치할 때만 지우므로 본문 중간 정상 문장은 안전).
        final_content = re.sub(r'(?m)^\s*```[a-zA-Z]*\s*$\n?', '', final_content)

        return final_content.strip(), title
    
    def create_safe_filename(self, title):
        """
        Convert title to safe filename
        """
        # Remove special characters that cannot be used in filenames
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        # Convert multiple spaces to single space
        safe_title = re.sub(r'\s+', ' ', safe_title)
        # Remove leading and trailing spaces
        safe_title = safe_title.strip()
        # Limit length (considering Windows filename restrictions)
        safe_title = safe_title[:100]
        # Remove trailing period
        safe_title = safe_title.rstrip('.')
        
        return safe_title if safe_title else "extracted_content"
    

    def process_text_string(self, text_content, output_dir="output"):
        """
        Process text string and save as MD files
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Split by sections (based on ##### 질문 요약)
        sections = re.split(r'(?=##### 질문 요약)', text_content)
        
        # 유효한 섹션만 필터링
        # ✅ 수정: ``` 찌꺼기 섹션 필터링
        valid_sections = [s for s in sections if s.strip().startswith('##### 질문 요약')]
        total_sections = len(valid_sections)


        created_files = []
        error_files = []
        error_folder = str(Path(output_dir).parent / "perplexity_errors")
        
        for i, section in enumerate(valid_sections):
            # 작업 시작 전에 라벨과 프로그레스바 업데이트
            current = i + 1
            progress_value = int(current / total_sections * 100)
            
            self.root.after(0, lambda cur=current, tot=total_sections: 
                           self.progress_label.config(text=f"변환 중: {cur}/{tot}"))
            self.root.after(0, lambda val=progress_value: self.progress.configure(value=val))

            # 형식 오류 감지: # 제목이 ##### 질문 요약보다 먼저 나오는 경우
            h1_match = re.search(r'(?:^|\n)# [^#]', section)
            summary_match = re.search(r'##### 질문 요약', section)
            if h1_match and summary_match and h1_match.start() < summary_match.start():
                Path(error_folder).mkdir(parents=True, exist_ok=True)
                error_filename = f"error_{i+1}.md"
                error_path = Path(error_folder) / error_filename
                with open(error_path, 'w', encoding='utf-8') as ef:
                    ef.write(section)
                error_files.append(str(error_path))
                self.log(f"⚠️ 형식 오류 섹션 → perplexity_errors/{error_filename}")
                continue
    
            markdown_content, title = self.extract_markdown_content(section)
            
            if markdown_content:
                # Generate filename
                if title:
                    filename = f"{self.create_safe_filename(title)}.md"
                else:
                    filename = f"extracted_content_{i+1}.md"
                
                # File path
                file_path = Path(output_dir) / filename
                
                # Handle duplicate filenames
                counter = 1
                original_path = file_path
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = original_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Save MD file
                try:
                    with open(file_path, 'w', encoding='utf-8') as md_file:
                        md_file.write(markdown_content)
                    created_files.append(str(file_path))
                except Exception as e:
                    print(f"Error saving file: {file_path}, Error: {e}")
            
        return created_files, error_files

    # 원본 수치를 변경 시 재 작성하도록 검사 (틀려도 통과)
    def verify_information_integrity(self, original, rewritten):
        """1차 각색 후 정보 변조 검사 (숫자, 금액, 날짜 등)"""
        try:
            # 1. 숫자 추출 (금액, 비율, 날짜, 개수 등)
            # 패턴: 숫자, 소수점, %, 억/만/천, 년/월/일
            number_pattern = r'\d+(?:\.\d+)?(?:[억만천%]|년|월|일)?'
            
            original_numbers = set(re.findall(number_pattern, original))
            rewritten_numbers = set(re.findall(number_pattern, rewritten))
            
            # 원문에 있는 숫자가 각색본에 없으면 경고
            missing_numbers = original_numbers - rewritten_numbers
            
            if len(missing_numbers) > 0:
                self.log(f"⚠️ 경고: 원문의 숫자 정보가 누락되었을 수 있습니다!")
                self.log(f"   누락 가능 숫자: {', '.join(list(missing_numbers)[:5])}")
                return False
            
            # 2. 새로 생긴 숫자가 많으면 의심 (원문 대비 30% 이상 증가)
            new_numbers = rewritten_numbers - original_numbers
            if len(original_numbers) > 0:
                change_rate = len(new_numbers) / len(original_numbers)
                if change_rate > 0.3:
                    self.log(f"⚠️ 경고: 원문에 없던 숫자가 추가되었을 수 있습니다!")
                    self.log(f"   추가된 숫자: {', '.join(list(new_numbers)[:5])}")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"⚠️ 정보 검증 중 오류: {str(e)}")
            return True  # 검증 실패 시 통과 (중단하지 않음)

    # 1차 각색 모델 선택
    def call_ai_for_rewrite_1st(self, original_content):
        """1차 각색 - 선택한 AI 모델 사용"""
        model_type = self.model_1st_type.get()
        
        if model_type == "GPT":
            return self.call_gpt_for_rewrite_1st(original_content)
        elif model_type == "Gemini":
            return self.call_gemini_for_rewrite_1st(original_content)
        elif model_type == "Claude":
            return self.call_claude_for_rewrite_1st(original_content)
        else:
            raise Exception(f"알 수 없는 모델 타입: {model_type}")
    

    # 2.  퍼플렉시티가 수집 요약한 자료를 기반으로 GPT가 새롭게 각색
    # 1차 각색 = GPT
    def call_gpt_for_rewrite_1st(self, original_content):
        """1차 각색 (GPT 전용)"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI 클라이언트가 초기화되지 않았습니다.")

            rewrite_prompt = self.load_prompt_from_file(prompt_type='1st')
            
            if not rewrite_prompt or len(rewrite_prompt.strip()) < 100:
                raise Exception(f"프롬프트 파일 로드 실패: {self.prompt_1st_file}")
    
            input_length = len(rewrite_prompt) + len(original_content)

            estimated_input_tokens = input_length // 4
            
            MAX_MODEL_TOKENS = 128000
            SAFETY_MARGIN = 1000
            
            if estimated_input_tokens > 120000:
                self.log(f"⚠️ 입력 토큰이 매우 큽니다 ({estimated_input_tokens})")
            
            max_tokens = min(3000, MAX_MODEL_TOKENS - estimated_input_tokens - SAFETY_MARGIN)
            max_tokens = max(max_tokens, 1000)
            
            if max_tokens < 1500:
                self.log(f"⚠️ 출력 토큰이 부족합니다 ({max_tokens})")
    
            # ✅ GUI에서 선택한 모델 버전 사용
            gpt_model = self.gpt_model_1st.get()
            temperature = self.temperature_1st.get()
            
            self.log(f"🤖 1차 각색: {gpt_model} (temp={temperature})")
    
            response = self.openai_client.chat.completions.create(
                model=gpt_model,
                messages=[
                    {
                        "role": "system",
                        "content": rewrite_prompt
                    },
                    {
                        "role": "user",
                        "content": (
                            "아래 원문을 규칙에 맞게 각색하시오.\n"
                            "⚠ 규칙을 하나라도 어기면 실패입니다.\n\n"
                            "----- 원문 시작 -----\n"
                            f"{original_content}\n"
                            "----- 원문 끝 -----"
                        )
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
    
            result = response.choices[0].message.content.strip()
    
            if not self.verify_information_integrity(original_content, result):
                self.log("⚠️ 숫자 정보 변조 감지되었으나 계속 진행합니다.")
            
            return result
    
        except Exception as e:
            raise Exception(f"GPT 1차 각색 실패: {str(e)}")


    # 1차 각색 = Gemini
    def call_gemini_for_rewrite_1st(self, original_content):
        """1차 각색 (Gemini) - 신 SDK 방식"""
        try:
            # ========================================
            # 1. Client 확인
            # ========================================
            if not hasattr(self, 'gemini_client') or self.gemini_client is None:
                raise Exception("Gemini 클라이언트가 초기화되지 않았습니다.")
    
            # ========================================
            # 2. 프롬프트 로드
            # ========================================
            rewrite_prompt = self.load_prompt_from_file(prompt_type='1st')
            
            if not rewrite_prompt or len(rewrite_prompt.strip()) < 100:
                raise Exception(f"프롬프트 파일 로드 실패: {self.prompt_1st_file}")
    
            # ========================================
            # 3. Temperature 설정
            # ========================================
            try:
                temperature = float(self.temperature_1st.get())
            except:
                temperature = 0.3
            
            self.log(f"🤖 1차 각색: Gemini 2.5 Flash (temp={temperature})")
    
            # ========================================
            # 4. Safety Settings (필수!)
            # ========================================
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
    
            # ========================================
            # 5. System Instruction 구성
            # ========================================
            system_instruction = rewrite_prompt
    
            # ========================================
            # 6. User Message 구성
            # ========================================
            user_message = (
                "아래 원문을 규칙에 맞게 각색하시오.\n"
                "⚠️ 규칙을 하나라도 어기면 실패입니다.\n\n"
                "----- 원문 시작 -----\n"
                f"{original_content}\n"
                "----- 원문 끝 -----"
            )
    
            # ========================================
            # 7. API 호출 (신 SDK 방식)
            # ========================================
            self.log(f"🔍 Gemini 1차 호출 중... (입력: {len(original_content)}자)")
            
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config={
                    'system_instruction': system_instruction,
                    'temperature': temperature,
                    'max_output_tokens': 8192,
                    'safety_settings': safety_settings,  # ✅ 추가!
                }
            )
    
            # ========================================
            # 8. 응답 추출
            # ========================================
            if not response or not response.text:
                raise Exception("1차 각색 응답 생성 실패")
            
            result = response.text.strip()
    
            self.log(f"✅ 1차 각색 완료 (Gemini 2.5 Flash)")
            return result
    
        except Exception as e:
            error_msg = str(e)
            self.show_error("Gemini 오류", f"Gemini 1차 각색 에러:\n{error_msg}")
            raise Exception(f"Gemini 1차 각색 최종 실패: {error_msg}")



    # 2차 각색 모델 선택
    def call_ai_for_rewrite_2nd(self, draft_1st):
        """2차 각색 - 선택한 AI 모델 사용"""
        model_type = self.model_2nd_type.get()
        
        if model_type == "GPT":
            return self.call_gpt_for_rewrite_2nd(draft_1st)
        elif model_type == "Gemini":
            return self.call_gemini_for_rewrite_2nd(draft_1st)
        elif model_type == "Claude":
            return self.call_claude_for_rewrite_2nd(draft_1st)            
        else:
            raise Exception(f"알 수 없는 모델 타입: {model_type}")
    
    # 2차 각색 = GPT 선택(초기값)
    def call_gpt_for_rewrite_2nd(self, draft_1st):
        """2차 각색 (GPT)"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI 클라이언트가 초기화되지 않았습니다.")
    
            rewrite_prompt = self.load_prompt_from_file(prompt_type='2nd')
    
            if not rewrite_prompt or len(rewrite_prompt.strip()) < 100:
                raise Exception(f"프롬프트 파일 로드 실패: {self.prompt_2nd_file}")
    
            input_length = len(rewrite_prompt) + len(draft_1st)
            estimated_input_tokens = input_length // 4
    
            MAX_MODEL_TOKENS = 128000
            SAFETY_MARGIN = 800
    
            max_tokens = min(2800, MAX_MODEL_TOKENS - estimated_input_tokens - SAFETY_MARGIN)
            max_tokens = max(max_tokens, 1000)
    
            # ✅ GUI에서 선택한 모델 버전 사용
            gpt_model = self.gpt_model_2nd.get()
            temperature = self.temperature_2nd.get()
            
            self.log(f"🎨 2차 각색: {gpt_model} (temp={temperature})")
    
            response = self.openai_client.chat.completions.create(
                model=gpt_model,
                messages=[
                    {
                        "role": "system",
                        "content": rewrite_prompt
                    },
                    {
                        "role": "user",
                        "content": draft_1st
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
    
            result = response.choices[0].message.content.strip()
           
            return result
    
        except Exception as e:
            raise Exception(f"GPT 2차 각색 실패: {str(e)}")
    
        
    # 2차 각색 = 재미나이 선택
    # temperature =  0.7 ~ 0.85 사이 추천
    def call_gemini_for_rewrite_2nd(self, draft_1st):
        """2차 각색 (Gemini) - 신 SDK 방식"""
        try:
            # ========================================
            # 1. Client 확인
            # ========================================
            if not hasattr(self, 'gemini_client') or self.gemini_client is None:
                raise Exception("Gemini 클라이언트가 초기화되지 않았습니다.")
    
            # ========================================
            # 2. 프롬프트 로드
            # ========================================
            rewrite_prompt = self.load_prompt_from_file(prompt_type='2nd')
    
            if not rewrite_prompt or len(rewrite_prompt.strip()) < 100:
                raise Exception(f"프롬프트 파일 로드 실패: {self.prompt_2nd_file}")
    
            # ========================================
            # 3. Temperature 설정
            # ========================================
            try:
                temperature = float(self.temperature_2nd.get())
            except:
                temperature = 0.8
            
            # Gemini 권장 범위 조정
            if temperature < 0.7:
                self.log(f"ℹ️ Gemini는 Temperature 0.7 이상 권장 (현재: {temperature})")
                self.log(f"   → 0.7로 자동 조정합니다")
                temperature = 0.7
            elif temperature > 0.85:
                self.log(f"ℹ️ Gemini는 Temperature 0.85 이하 권장 (현재: {temperature})")
                self.log(f"   → 0.85로 자동 조정합니다")
                temperature = 0.85
            
            self.log(f"🎨 2차 각색: Gemini 2.5 Flash (temp={temperature})")
    
            # ========================================
            # 4. Safety Settings (필수!)
            # ========================================
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
    
            # ========================================
            # 5. API 호출
            # ========================================
            self.log(f"🔍 Gemini 2차 호출 중... (입력: {len(draft_1st)}자)")
            
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=draft_1st,
                config={
                    'system_instruction': rewrite_prompt,
                    'temperature': temperature,
                    'max_output_tokens': 8192,
                    'safety_settings': safety_settings,  # ✅ 추가!
                }
            )
    
            # ========================================
            # 6. 결과 검증
            # ========================================
            if not response or not response.text:
                raise Exception("Gemini 응답이 비어 있습니다.")
            
            result = response.text.strip()

            return result
    
        except Exception as e:
            error_msg = str(e)
            self.show_error("Gemini 오류", f"Gemini 2차 각색 실패:\n{error_msg}")
            
            # RPM 제한 에러 처리
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                self.log("⏸️ Gemini API 할당량 초과. 10초 대기 후 재시도...")
                import time
                time.sleep(10)
            
            raise Exception(f"Gemini 2차 각색 실패: {error_msg}")

    # 1차 각색 = Claude (신규)
    def call_claude_for_rewrite_1st(self, original_content):
        """1차 각색 (Claude)"""
        try:
            if not self.claude_client:
                raise Exception("Claude 클라이언트가 초기화되지 않았습니다.")

            rewrite_prompt = self.load_prompt_from_file(prompt_type='1st')
            if not rewrite_prompt or len(rewrite_prompt.strip()) < 100:
                raise Exception(f"프롬프트 파일 로드 실패: {self.prompt_1st_file}")

            temperature = self.temperature_1st.get()
            claude_model = self.claude_model_1st.get()
            self.log(f"🤖 1차 각색: Claude {claude_model} (temp={temperature})")

            response = self.claude_client.messages.create(
                model=claude_model,
                max_tokens=8096,
                temperature=temperature,
                system=[
                    {
                        "type": "text",
                        "text": rewrite_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "아래 원문을 규칙에 맞게 각색하시오.\n"
                            "⚠ 규칙을 하나라도 어기면 실패입니다.\n\n"
                            "----- 원문 시작 -----\n"
                            f"{original_content}\n"
                            "----- 원문 끝 -----"
                        )
                    }
                ]
            )

            if not response.content or response.content[0].type != "text":
                raise Exception("Claude 응답 형식 오류: 텍스트 응답이 없습니다.")
            
            result = response.content[0].text.strip()

            # 캐시 사용 여부 로그
            usage = response.usage
            if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens > 0:
                self.log(f"💰 캐시 히트: {usage.cache_read_input_tokens:,} 토큰 절감")

            if not self.verify_information_integrity(original_content, result):
                self.log("⚠️ 숫자 정보 변조 감지되었으나 계속 진행합니다.")

            self.log(f"✅ 1차 각색 완료 (Claude)")
            return result

        except Exception as e:
            raise Exception(f"Claude 1차 각색 실패: {str(e)}")


    # 2차 각색 = Claude (신규)
    def call_claude_for_rewrite_2nd(self, draft_1st):
        """2차 각색 (Claude)"""
        try:
            if not self.claude_client:
                raise Exception("Claude 클라이언트가 초기화되지 않았습니다.")

            rewrite_prompt = self.load_prompt_from_file(prompt_type='2nd')
            if not rewrite_prompt or len(rewrite_prompt.strip()) < 100:
                raise Exception(f"프롬프트 파일 로드 실패: {self.prompt_2nd_file}")

            temperature = self.temperature_2nd.get()
            claude_model = self.claude_model_2nd.get()
            self.log(f"🎨 2차 각색: Claude {claude_model} (temp={temperature})")

            response = self.claude_client.messages.create(
                model=claude_model,
                max_tokens=8096,
                temperature=temperature,
                system=[
                    {
                        "type": "text",
                        "text": rewrite_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": draft_1st
                    }
                ]
            )

            # 응답 형식 검증
            if not response.content or response.content[0].type != "text":
                raise Exception("Claude 응답 형식 오류: 텍스트 응답이 없습니다.")

            result = response.content[0].text.strip()

            # 캐시 사용 여부 로그
            usage = response.usage
            if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens > 0:
                self.log(f"💰 캐시 히트: {usage.cache_read_input_tokens:,} 토큰 절감")

            self.log(f"✅ 2차 각색 완료 (Claude, {len(result)}자)")
            return result

        except Exception as e:
            raise Exception(f"Claude 2차 각색 실패: {str(e)}") from e

    def _select_1st_draft_folder_popup(self, base_dir, topic, model_name):
        """2차만 모드: 1차 초안 날짜 폴더 선택 팝업"""
        topic_path = os.path.join(base_dir, topic)
        if not os.path.exists(topic_path):
            return None

        folder_name = f"perplexity_{model_name}_1st_draft"
        candidates = []

        for date_folder in os.listdir(topic_path):
            date_path = os.path.join(topic_path, date_folder)
            if not os.path.isdir(date_path):
                continue
            draft_path = os.path.join(date_path, folder_name)
            if os.path.exists(draft_path):
                md_files = [f for f in os.listdir(draft_path) if f.endswith('.md')]
                if md_files:
                    candidates.append((date_folder, draft_path, len(md_files)))

        if not candidates:
            return None

        # 날짜 내림차순 (최신이 위)
        candidates.sort(key=lambda x: x[0], reverse=True)

        # 후보가 1개뿐이면 팝업 없이 바로 반환
        if len(candidates) == 1:
            d, p, n = candidates[0]
            self.log(f"📂 1차 초안 폴더 자동 선택: {d} ({n}개)")
            return p

        # 후보 여러 개 → 선택 팝업
        result = {'path': None}

        popup = tk.Toplevel(self.root)
        popup.title("1차 초안 날짜 선택")
        w, h = 500, 230
        sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
        popup.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)

        ttk.Label(popup,
                  text=f"[{model_name}] 2차 각색할 1차 초안의 날짜를 선택하세요.",
                  font=('', 10, 'bold'), padding=(10, 12)).pack()

        options = [f"{d}  ({n}개 파일)" for d, p, n in candidates]
        selected_var = tk.StringVar(value=options[0])

        combo_frame = ttk.Frame(popup, padding=(20, 5))
        combo_frame.pack(fill=tk.X)
        ttk.Label(combo_frame, text="날짜:").pack(side=tk.LEFT)
        ttk.Combobox(combo_frame, textvariable=selected_var,
                     values=options, state="readonly", width=36).pack(side=tk.LEFT, padx=8)

        info_var = tk.StringVar(value=f"경로: {candidates[0][1]}")
        ttk.Label(popup, textvariable=info_var, foreground="gray",
                  wraplength=460, justify=tk.LEFT, padding=(20, 4)).pack(fill=tk.X)

        def on_combo_change(*args):
            idx = options.index(selected_var.get())
            info_var.set(f"경로: {candidates[idx][1]}")

        selected_var.trace_add("write", on_combo_change)

        def on_confirm():
            idx = options.index(selected_var.get())
            result['path'] = candidates[idx][1]
            popup.destroy()

        def on_cancel():
            popup.destroy()

        def on_browse():
            folder = filedialog.askdirectory(
                title="1차 초안 폴더 직접 선택",
                initialdir=topic_path
            )
            if folder:
                result['path'] = folder
                popup.destroy()

        btn_frame = ttk.Frame(popup, padding=(0, 15))
        btn_frame.pack()
        ttk.Button(btn_frame, text="✅ 확인", command=on_confirm, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 폴더 직접 선택", command=on_browse, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ 취소", command=on_cancel, width=12).pack(side=tk.LEFT, padx=5)

        popup.wait_window()
        return result['path']

    # GPT 각색 중 정지
    def stop_gpt_rewrite(self):
        """GPT 각색 작업 중지"""
        self.stop_rewrite_flag = True
        self.log("⏸️ 각색 작업 중지 요청됨...")
        self.progress_label.config(text="중지 중...")
    
    
        # 3. start_gpt_rewrite 메서드에서 폴더 확인 부분 수정
    def start_gpt_rewrite(self):
        """2단계: GPT 각색 시작"""
        try:
            # ✅ 정지 플래그 초기화 + 버튼 상태 변경
            self.stop_rewrite_flag = False
            self.start_rewrite_btn.config(state=tk.DISABLED)
            self.stop_rewrite_btn.config(state=tk.NORMAL)
    
            # 3개의 API 키 확인
            model_1st = self.model_1st_type.get()
            model_2nd = self.model_2nd_type.get()
            rewrite_mode_check = self.rewrite_mode.get()
            
            def check_client(model_type):
                if model_type == "GPT" and not self.openai_client:
                    return "OpenAI API 키가 설정되지 않았습니다."
                elif model_type == "Gemini" and not self.gemini_configured:
                    return "Gemini API 키가 설정되지 않았습니다."
                elif model_type == "Claude" and not self.claude_configured:
                    return "Claude API 키가 설정되지 않았습니다."
                return None
            
            if rewrite_mode_check in ["first_only", "both"]:
                err = check_client(model_1st)
                if err:
                    messagebox.showerror("오류", f"1차 각색 모델 오류:\n{err}")
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
            
            if rewrite_mode_check in ["second_only", "both"]:
                err = check_client(model_2nd)
                if err:
                    messagebox.showerror("오류", f"2차 각색 모델 오류:\n{err}")
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return

            # 주제 선택 확인
            selected_topic = self.topic_var.get()
            base_dir = self.base_folder_var.get().strip()
            if not base_dir:
                base_dir = "Naver_blog_지식인_수동_markdown_work_folder"
            
            base_dir = os.path.abspath(base_dir)
            if self.rewrite_mode.get() != "second_only":
                output_dir = self.create_output_directory(base_dir, selected_topic)
            else:
                output_dir = os.path.join(base_dir, selected_topic, datetime.now().strftime("%Y-%m-%d"), "perplexity_answers")            
            
            # ========================================
            # ✅ 프롬프트 파일 사전 검증
            # ========================================
            rewrite_mode = self.rewrite_mode.get()
            # UI 입력값 우선, 없으면 초기값 사용
            effective_prompt_folder = self.prompt_folder_var.get().strip() or self.prompt_folder
            
            # 1차 프롬프트 검증
            if rewrite_mode in ["first_only", "both"]:
                if not self.prompt_1st_file or self.prompt_1st_file.strip() == '':
                    messagebox.showerror(
                        "프롬프트 오류",
                        "1차 프롬프트 파일이 선택되지 않았습니다!\n\n"
                        "2단계 탭에서 '1차 각색 프롬프트' 파일을 선택하세요."
                    )
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
                
                prompt_1st_path = os.path.join(effective_prompt_folder, self.prompt_1st_file)
                if not os.path.exists(prompt_1st_path):
                    messagebox.showerror(
                        "프롬프트 파일 없음",
                        f"1차 프롬프트 파일이 없습니다!\n\n"
                        f"파일: {self.prompt_1st_file}\n"
                        f"경로: {prompt_1st_path}\n\n"
                        f"파일을 추가하거나 다른 파일을 선택하세요."
                    )
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
                
                try:
                    with open(prompt_1st_path, 'r', encoding='utf-8') as f:
                        prompt_1st_content = f.read().strip()
                    
                    if len(prompt_1st_content) < 100:
                        messagebox.showerror(
                            "프롬프트 내용 오류",
                            f"1차 프롬프트 파일 내용이 너무 짧습니다!\n\n"
                            f"파일: {self.prompt_1st_file}\n"
                            f"길이: {len(prompt_1st_content)}자 (최소 100자 필요)\n\n"
                            f"프롬프트 파일 내용을 점검하세요."
                        )
                        # ✅ 버튼 복구 추가!
                        self.start_rewrite_btn.config(state=tk.NORMAL)
                        self.stop_rewrite_btn.config(state=tk.DISABLED)
                        return
                    
                    required_keywords = ["정보", "원문", "블록"]
                    if not any(kw in prompt_1st_content for kw in required_keywords):
                        result = messagebox.askyesno(
                            "프롬프트 검증 경고",
                            f"1차 프롬프트에 필수 키워드가 없습니다!\n\n"
                            f"파일: {self.prompt_1st_file}\n"
                            f"필수 키워드: {', '.join(required_keywords)}\n\n"
                            f"프롬프트가 올바른지 확인하세요.\n"
                            f"계속 진행하시겠습니까?",
                            icon='warning'
                        )
                        if not result:
                            # ✅ 버튼 복구 추가!
                            self.start_rewrite_btn.config(state=tk.NORMAL)
                            self.stop_rewrite_btn.config(state=tk.DISABLED)
                            return
                        
                except Exception as e:
                    messagebox.showerror(
                        "프롬프트 파일 읽기 오류",
                        f"1차 프롬프트 파일을 읽을 수 없습니다!\n\n"
                        f"파일: {self.prompt_1st_file}\n"
                        f"오류: {str(e)}\n\n"
                        f"파일 인코딩이나 권한을 확인하세요."
                    )
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
            
            # 2차 프롬프트 검증
            if rewrite_mode in ["second_only", "both"]:
                if not self.prompt_2nd_file or self.prompt_2nd_file.strip() == '':
                    messagebox.showerror(
                        "프롬프트 오류",
                        "2차 프롬프트 파일이 선택되지 않았습니다!\n\n"
                        "2단계 탭에서 '2차 각색 프롬프트' 파일을 선택하세요."
                    )
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
                
                prompt_2nd_path = os.path.join(effective_prompt_folder, self.prompt_2nd_file)
                if not os.path.exists(prompt_2nd_path):
                    messagebox.showerror(
                        "프롬프트 파일 없음",
                        f"2차 프롬프트 파일이 없습니다!\n\n"
                        f"파일: {self.prompt_2nd_file}\n"
                        f"경로: {prompt_2nd_path}\n\n"
                        f"파일을 추가하거나 다른 파일을 선택하세요."
                    )
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
                
                try:
                    with open(prompt_2nd_path, 'r', encoding='utf-8') as f:
                        prompt_2nd_content = f.read().strip()
                    
                    if len(prompt_2nd_content) < 100:
                        messagebox.showerror(
                            "프롬프트 내용 오류",
                            f"2차 프롬프트 파일 내용이 너무 짧습니다!\n\n"
                            f"파일: {self.prompt_2nd_file}\n"
                            f"길이: {len(prompt_2nd_content)}자 (최소 100자 필요)\n\n"
                            f"프롬프트 파일 내용을 점검하세요."
                        )
                        # ✅ 버튼 복구 추가!
                        self.start_rewrite_btn.config(state=tk.NORMAL)
                        self.stop_rewrite_btn.config(state=tk.DISABLED)
                        return
                    
                    required_keywords = ["자연스럽", "블로그", "글"]
                    if not any(kw in prompt_2nd_content for kw in required_keywords):
                        result = messagebox.askyesno(
                            "프롬프트 검증 경고",
                            f"2차 프롬프트에 필수 키워드가 없습니다!\n\n"
                            f"파일: {self.prompt_2nd_file}\n"
                            f"필수 키워드: {', '.join(required_keywords)}\n\n"
                            f"프롬프트가 올바른지 확인하세요.\n"
                            f"계속 진행하시겠습니까?",
                            icon='warning'
                        )
                        if not result:
                            # ✅ 버튼 복구 추가!
                            self.start_rewrite_btn.config(state=tk.NORMAL)
                            self.stop_rewrite_btn.config(state=tk.DISABLED)
                            return
                        
                except Exception as e:
                    messagebox.showerror(
                        "프롬프트 파일 읽기 오류",
                        f"2차 프롬프트 파일을 읽을 수 없습니다!\n\n"
                        f"파일: {self.prompt_2nd_file}\n"
                        f"오류: {str(e)}\n\n"
                        f"파일 인코딩이나 권한을 확인하세요."
                    )
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return

            self.log("✅ 프롬프트 파일 검증 완료")
            # ========================================
            # 기존 결과물 존재 여부 체크
            # ========================================
            draft_1st_folder = os.path.join(str(Path(output_dir).parent), f"perplexity_{model_1st}_1st_draft")
            final_folder = os.path.join(str(Path(output_dir).parent), f"perplexity_{model_2nd}_final_articles")
            
            if rewrite_mode == "first_only":
                existing = [f for f in os.listdir(draft_1st_folder) if f.endswith('.md')] if os.path.exists(draft_1st_folder) else []
                if existing:
                    result = messagebox.askyesno(
                        "기존 결과물 존재",
                        f"1차 결과 폴더에 이미 {len(existing)}개 파일이 있습니다.\n\n"
                        f"폴더: {draft_1st_folder}\n\n"
                        f"덮어쓰기 하시겠습니까?"
                    )
                    if not result:
                        self.start_rewrite_btn.config(state=tk.NORMAL)
                        self.stop_rewrite_btn.config(state=tk.DISABLED)
                        return
            
            elif rewrite_mode == "second_only":
                existing = [f for f in os.listdir(final_folder) if f.endswith('.md')] if os.path.exists(final_folder) else []
                if existing:
                    result = messagebox.askyesno(
                        "기존 결과물 존재",
                        f"2차 결과 폴더에 이미 {len(existing)}개 파일이 있습니다.\n\n"
                        f"폴더: {final_folder}\n\n"
                        f"덮어쓰기 하시겠습니까?"
                    )
                    if not result:
                        self.start_rewrite_btn.config(state=tk.NORMAL)
                        self.stop_rewrite_btn.config(state=tk.DISABLED)
                        return
            
            elif rewrite_mode == "both":
                existing_1st = [f for f in os.listdir(draft_1st_folder) if f.endswith('.md')] if os.path.exists(draft_1st_folder) else []
                existing_2nd = [f for f in os.listdir(final_folder) if f.endswith('.md')] if os.path.exists(final_folder) else []
                if existing_1st or existing_2nd:
                    result = messagebox.askyesno(
                        "기존 결과물 존재",
                        f"이미 생성된 결과물이 있습니다.\n\n"
                        f"1차 폴더: {len(existing_1st)}개\n"
                        f"2차 폴더: {len(existing_2nd)}개\n\n"
                        f"덮어쓰기 하시겠습니까?"
                    )
                    if not result:
                        self.start_rewrite_btn.config(state=tk.NORMAL)
                        self.stop_rewrite_btn.config(state=tk.DISABLED)
                        return

            # ========================================
            # 폴더 확인
            # ========================================
            if rewrite_mode == "second_only":
                model_1st_name = self.model_1st_type.get()
    
                # 항상 날짜 선택 팝업 표시 (날짜별 작업 혼용 방지)
                selected_path = self._select_1st_draft_folder_popup(base_dir, selected_topic, model_1st_name)
    
                if not selected_path:
                    messagebox.showerror("오류",
                        f"1차 초안 폴더를 찾을 수 없거나 선택이 취소되었습니다.\n\n"
                        f"탐색 경로: {os.path.join(base_dir, selected_topic)}\n\n"
                        f"모델: {model_1st_name}\n\n"
                        f"1차 각색을 먼저 실행하거나 다른 모드를 선택하세요.")
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return

                draft_1st_folder = selected_path
                self.log(f"📂 선택된 1차 초안 폴더: {draft_1st_folder}")
                output_dir = os.path.join(str(Path(selected_path).parent), "perplexity_answers")                

                md_files = [f for f in os.listdir(draft_1st_folder) if f.endswith('.md')]

                if not md_files:
                    messagebox.showwarning("알림",
                        f"선택한 폴더에 MD 파일이 없습니다.\n\n"
                        f"경로: {draft_1st_folder}")
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)

                    return
    
                self.log(f"🎨 2차 각색만 실행 모드 ({len(md_files)}개 파일)")
                source_folder = draft_1st_folder
    
            else:
                # [Ver7.10 추가] 4)탭(퍼플렉시티 자료검증)에서 수동으로
                # 교차검증까지 끝낸 자료가 있으면 그걸 우선 사용하고,
                # 없으면 기존처럼 원본 perplexity_answers를 사용한다
                # (하위호환 - 검증 단계를 안 거친 주제도 그대로 동작).
                model_1st_for_source = self.model_1st_type.get()
                verified_folder = os.path.join(Path(output_dir).parent, f"perplexity_{model_1st_for_source}_verified")
                perplexity_folder = os.path.join(Path(output_dir).parent, "perplexity_answers")

                verified_files = [f for f in os.listdir(verified_folder) if f.endswith('.md')] if os.path.exists(verified_folder) else []

                if verified_files:
                    perplexity_folder = verified_folder
                    md_files = verified_files
                    self.log(f"✅ 교차검증 완료 자료 사용: perplexity_{model_1st_for_source}_verified ({len(md_files)}개)")
                else:
                    if not os.path.exists(perplexity_folder):
                        messagebox.showerror("오류", "1단계에서 생성된 perplexity_answers 폴더가 없습니다.\n먼저 1단계를 실행하세요.")
                        # ✅ 버튼 복구 추가!
                        self.start_rewrite_btn.config(state=tk.NORMAL)
                        self.stop_rewrite_btn.config(state=tk.DISABLED)
                        return

                    md_files = [f for f in os.listdir(perplexity_folder) if f.endswith('.md')]
                    self.log(f"ℹ️ 검증완료 자료 없음 → 원본 perplexity_answers 사용 ({len(md_files)}개)")

                if not md_files:
                    messagebox.showwarning("알림", "처리할 MD 파일이 없습니다.")
                    # ✅ 버튼 복구 추가!
                    self.start_rewrite_btn.config(state=tk.NORMAL)
                    self.stop_rewrite_btn.config(state=tk.DISABLED)
                    return
                
                if rewrite_mode == "first_only":
                    self.log(f"🤖 1차 각색만 실행 모드 ({len(md_files)}개 파일)")
                else:
                    self.log(f"🤖 1차+2차 각색 실행 모드 ({len(md_files)}개 파일)")
                
                source_folder = perplexity_folder            
    
            self.progress['value'] = 0
            self.progress_label.config(text="GPT 각색 준비 중...")
    
            # ✅ rewrite_mode 파라미터 전달
            threading.Thread(
                target=self.gpt_rewrite_worker, 
                args=(source_folder, output_dir, md_files, rewrite_mode), 
                daemon=True
            ).start()
    
        except Exception as e:
            messagebox.showerror("오류", str(e))
            # ✅ 버튼 복구 추가!
            self.start_rewrite_btn.config(state=tk.NORMAL)
            self.stop_rewrite_btn.config(state=tk.DISABLED)

        
    def gpt_rewrite_worker(self, source_folder, output_dir, md_files, rewrite_mode="both"):
        """GPT 각색 작업자 (1차만/2차만/둘다 옵션 지원)"""
        try:
            # 모드별 로그 출력
            if rewrite_mode == "first_only":
                self.log("🤖 1차 각색만 실행 모드")
            elif rewrite_mode == "second_only":
                self.log("🎨 2차 각색만 실행 모드")
            else:
                self.log("🤖 1차+2차 각색 실행 모드")
            
            # 2차 각색 사용 여부 결정
            use_2nd_stage = (rewrite_mode in ["second_only", "both"])
            
            # 폴더 경로 설정 (모델명 포함)
            model_1st_name = self.model_1st_type.get()
            model_2nd_name = self.model_2nd_type.get()
            
            draft_1st_folder = os.path.join(Path(output_dir).parent, f"perplexity_{model_1st_name}_1st_draft")
            final_folder = os.path.join(Path(output_dir).parent, f"perplexity_{model_2nd_name}_final_articles")
            
            # 모드별 필요한 폴더만 생성
            if rewrite_mode in ["first_only", "both"]:
                os.makedirs(draft_1st_folder, exist_ok=True)
            
            if rewrite_mode in ["second_only", "both"]:
                os.makedirs(final_folder, exist_ok=True)
            
            # 글자수 미달 폴더
            short_folder = os.path.join(Path(output_dir).parent, f"perplexity_{model_2nd_name}_short_articles")

            success_count = 0
            failed_files = []
            total_files = len(md_files)
            
            for i, md_file in enumerate(md_files):
                # ✅ 정지 플래그 체크
                if self.stop_rewrite_flag:
                    self.log("⏹️ 사용자가 작업을 중지했습니다.")
                    break

                try:
                    current = i + 1
                    progress_value = int(current / total_files * 100)
                    
                    self.root.after(0, lambda cur=current, tot=total_files: 
                                   self.progress_label.config(text=f"GPT 각색 중: {cur}/{tot}"))
                    self.root.after(0, lambda val=progress_value: self.progress.configure(value=val))
                    
                    md_path = os.path.join(source_folder, md_file)
    
                    # 파일 읽기
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # ========================================
                    # 1차 각색 (first_only 또는 both 모드)
                    # ========================================
                    if rewrite_mode in ["first_only", "both"]:
                        self.log(f"🤖 1차 각색 중 ({i+1}/{total_files}): {md_file[:30]}...")
    
                        draft_1st = self.call_ai_for_rewrite_1st(content)

                        if not draft_1st:
                            raise Exception("1차 각색 결과가 비어있습니다")
                        
                        # ✅ 결과 품질 검증 추가
                        if len(draft_1st) < 300:
                            self.log(f"⚠️ 1차 각색 결과가 너무 짧습니다 ({len(draft_1st)}자)")
                            raise Exception("1차 각색 결과 품질 미달 (300자 미만)")
                        
                        # GPT 거부 메시지 탐지
                        reject_patterns = ["죄송합니다", "수행할 수 없", "도움을 드릴 수 없", "만들 수 없"]
                        if any(p in draft_1st[:200] for p in reject_patterns):
                            self.log(f"⚠️ GPT가 각색을 거부했습니다: {draft_1st[:100]}...")
                            raise Exception("GPT 각색 거부")
    
                        # 1차 제목 추출
                        lines = draft_1st.split('\n')
                        title_1st = None
                        
                        for line in lines:
                            line = line.strip()
                            if line.startswith('# ') and not line.startswith('## '):
                                title_1st = line[2:].strip()
                                break
                        
                        # 제목 없으면 원본 파일명 사용
                        if not title_1st or len(title_1st) < 5:
                            title_1st = md_file[:-3]  # 원본 파일명
                            self.log(f"⚠️ 제목 추출 실패. 원본 파일명 사용: {title_1st}")
    
                        # 1차 결과 저장 (항상 1st_draft 폴더에)
                        draft_1st_filename = f"{self.create_safe_filename(title_1st)}.md"
                        draft_1st_path = os.path.join(draft_1st_folder, draft_1st_filename)
                        
                        with open(draft_1st_path, 'w', encoding='utf-8') as f:
                            f.write(draft_1st)
                        
                        self.log(f"✅ 1차 각색 완료: {title_1st[:30]}...")
                        
                        # 1차만 모드면 여기서 종료 (2차 안 함)
                        if rewrite_mode == "first_only":
                            success_count += 1
                            time.sleep(self.gpt_delay_between_files)
                            continue


                    else:
                        # second_only 모드: 이미 읽은 content가 1차 초안
                        draft_1st = content
                        title_1st = md_file[:-3]  # .md 제거
                        self.log(f"⏩ 1차 초안 로드 ({i+1}/{total_files}): {title_1st[:30]}...")
                    
                    # ========================================
                    # 2차 각색 (second_only 또는 both 모드만 실행)
                    # ========================================
                    if use_2nd_stage:
                        # both 모드면 3초 대기
                        if rewrite_mode == "both":
                            self.log(f"⏳ 2차 각색 준비 중... (3초 대기)")
                            time.sleep(self.gpt_delay_between_stages)
                        
                        self.log(f"🎨 2차 각색 중 ({i+1}/{total_files}): {title_1st[:30]}...")
    
                        draft_2nd = self.call_ai_for_rewrite_2nd(draft_1st)
                        
                        if not draft_2nd:
                            self.log(f"⚠️ 2차 각색 결과 없음 → 건너뜁니다: {title_1st[:30]}")
                            failed_files.append(md_file)
                            continue

                        else:
                            # ✅ 2차 결과 품질 검증 추가
                            reject_patterns = ["죄송합니다", "수행할 수 없", "도움을 드릴 수 없"]
                            if any(p in draft_2nd[:200] for p in reject_patterns):
                                self.log(f"⚠️ 2차 각색 거부됨 → short 폴더 이동")
                                os.makedirs(short_folder, exist_ok=True)
                                save_path = os.path.join(short_folder, f"{self.create_safe_filename(title_1st)}_rejected.md")
                                with open(save_path, 'w', encoding='utf-8') as f:
                                    f.write(draft_2nd)
                                success_count += 1
                                time.sleep(self.gpt_delay_between_files)
                                continue
    
                        # 2차 제목 추출
                        lines = draft_2nd.split('\n')
                        title_2nd = title_1st
                        for line in lines:
                            line = line.strip()
                            if line.startswith('# ') and not line.startswith('## '):
                                title_2nd = line[2:].strip()
                                break
                        

                        # 2차 결과 저장 (글자수 기준으로 폴더 분기)
                        final_filename = f"{self.create_safe_filename(title_2nd)}.md"

                        if len(draft_2nd) < 900:
                            os.makedirs(short_folder, exist_ok=True)
                            save_path = os.path.join(short_folder, final_filename)
                            with open(save_path, 'w', encoding='utf-8') as f:
                                f.write(draft_2nd)
                            self.log(f"⚠️ 글자수 미달({len(draft_2nd)}자) → short 폴더 이동: {title_2nd[:30]}...")
                        else:
                            final_path = os.path.join(final_folder, final_filename)
                            with open(final_path, 'w', encoding='utf-8') as f:
                                f.write(draft_2nd)
                            self.log(f"✅ 2차 각색 완료: {title_2nd[:30]}...")


                    success_count += 1
                    
                    # 다음 파일 처리 전 대기
                    time.sleep(self.gpt_delay_between_files)


                except Exception as e:
                    error_msg = str(e)
                    
                    # API 에러 종류별 처리
                    if "rate_limit" in error_msg.lower() or "429" in error_msg:
                        self.log(f"⏸️ API 요청 한도 초과. 60초 대기...")
                        time.sleep(60)
                        failed_files.append(md_file)
                        continue
                    
                    elif "timeout" in error_msg.lower():
                        self.log(f"⏱️ API 타임아웃. 10초 대기...")
                        time.sleep(10)
                        failed_files.append(md_file)
                        continue
                    
                    elif "프롬프트 파일 로드 실패" in error_msg or "프롬프트" in error_msg:
                        self.log(f"❌ 프롬프트 오류로 작업을 중단합니다: {error_msg}")
                        self.root.after(0, lambda err=error_msg: messagebox.showerror(
                            "프롬프트 오류",
                            f"각색을 진행할 수 없습니다.\n\n{err}\n\n프롬프트 파일을 확인하세요."
                        ))
                        break
                    else:
                        self.log(f"❌ 각색 실패: {md_file} - {error_msg}")
                        failed_files.append(md_file)
                        continue

            # 완료 메시지
            if success_count > 0:
                if rewrite_mode == "first_only":
                    msg = f"✅ 1차 각색 완료! 성공: {success_count}개\n모델: {model_1st_name}\n저장 위치: {draft_1st_folder}"
                    self.log(msg)
                    self.root.after(0, lambda: messagebox.showinfo("완료", msg))
                elif rewrite_mode == "second_only":
                    msg = f"✅ 2차 각색 완료! 성공: {success_count}개\n모델: {model_2nd_name}\n저장 위치: {final_folder}"
                    self.log(msg)
                    self.root.after(0, lambda: messagebox.showinfo("완료", msg))
                else:  # both
                    msg = f"✅ 1차+2차 각색 완료! 성공: {success_count}개\n1차({model_1st_name}): {draft_1st_folder}\n2차({model_2nd_name}): {final_folder}"
                    self.log(msg)
                    self.root.after(0, lambda: messagebox.showinfo("완료", msg))

            else:
                self.show_error("GPT 오류", "GPT 각색에 실패했습니다.")
    
        except Exception as e:
            self.show_error("GPT 오류", f"GPT 각색 오류:\n{str(e)}")
            
        finally:
            self.root.after(0, lambda: self.progress.configure(value=100))
            self.root.after(0, lambda: self.progress_label.config(text="변환 완료!"))

            # ✅ 버튼 상태 복구
            self.root.after(0, lambda: self.start_rewrite_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_rewrite_btn.config(state=tk.DISABLED))
    
    # API KEY 초기값 입력 창
    def open_api_key_settings(self):
        """API 키 설정 팝업"""
        import json
        
        # 팝업 창 생성
        popup = tk.Toplevel(self.root)
        popup.title("API 키 설정")
        popup.geometry("600x620")

        # 중앙 배치
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 620) // 2
        popup.geometry(f"600x620+{x}+{y}")

        popup.transient(self.root)
        popup.grab_set()

        # 기존 키 로드
        config_path = self.get_kin_config_path()
        openai_key = ""
        gemini_key = ""
        claude_key = ""

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                openai_key = config.get('openai_api_key', '') or config.get('api_key', '')
                gemini_key = config.get('gemini_api_key', '')
                claude_key = config.get('claude_api_key', '')
            except:
                pass
        
        # UI 구성
        main_frame = ttk.Frame(popup, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # OpenAI
        ttk.Label(main_frame, text="OpenAI API Key:", font=('', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=8)
        openai_var = tk.StringVar(value=openai_key)
        openai_entry = ttk.Entry(main_frame, textvariable=openai_var, width=55, show="*")
        openai_entry.grid(row=0, column=1, pady=8, padx=5)
        
        # Gemini
        ttk.Label(main_frame, text="Gemini API Key:", font=('', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=8)
        gemini_var = tk.StringVar(value=gemini_key)
        gemini_entry = ttk.Entry(main_frame, textvariable=gemini_var, width=55, show="*")
        gemini_entry.grid(row=1, column=1, pady=8, padx=5)

        # Claude
        ttk.Label(main_frame, text="Claude API Key:", font=('', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=8)
        claude_var = tk.StringVar(value=claude_key)
        claude_entry = ttk.Entry(main_frame, textvariable=claude_var, width=55, show="*")
        claude_entry.grid(row=2, column=1, pady=8, padx=5)

        # 안내 문구
        info_label = ttk.Label(main_frame, text="※ 키 입력 후 '저장' 버튼을 누르면 프로그램 재시작 없이 즉시 적용됩니다.",
                              foreground="blue", font=('', 9))
        info_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 저장 함수
        def save_keys():
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {}
                
                config['openai_api_key'] = openai_var.get().strip()
                config['gemini_api_key'] = gemini_var.get().strip()
                config['claude_api_key'] = claude_var.get().strip()

                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                # ✅ 즉시 API 클라이언트 재초기화
                self.load_api_key_from_config()

                messagebox.showinfo("완료", "API 키가 저장되었습니다!\n클라이언트가 재초기화되었습니다.")
                popup.destroy()

            except Exception as e:
                messagebox.showerror("오류", f"저장 실패: {str(e)}")

        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="💾 저장", command=save_keys, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ 취소", command=popup.destroy, width=12).pack(side=tk.LEFT, padx=5)

    def _load_api_keys_async(self):
        """API 키 로딩을 백그라운드 스레드로 실행"""
        threading.Thread(target=self.load_api_key_from_config, daemon=True).start()

    # API Key 로딩
    def load_api_key_from_config(self):
        """Naver_blog_config_지식인.json 에서 모든 API 키 로드"""
        try:
            import json
            
            config_path = self.get_kin_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # ========================================
                # 1. OpenAI API 로드
                # ========================================
                openai_key = config.get('openai_api_key', '') or config.get('api_key', '')
                if openai_key and openai_key.startswith('sk-'):
                    import openai
                    self.openai_client = openai.OpenAI(api_key=openai_key)
                    self.log("✅ OpenAI API 키 로드 완료")
                else:
                    self.log("⚠️ OpenAI API 키 없음")
                
                # ========================================
                # 2. Gemini API 로드 (수정)
                # ========================================
                gemini_key = config.get('gemini_api_key', '')
                if gemini_key:
                    try:
                        from google import genai  # ✅ 신 SDK
                        
                        # ✅ Client 객체 생성 (신 SDK 방식)
                        self.gemini_client = genai.Client(api_key=gemini_key)
                        self.gemini_configured = True
                        self.log("✅ Gemini API 키 로드 완료 (google.genai)")
                    except ImportError:
                        self.log("⚠️ google-genai 패키지 없음")
                        self.log("   설치: pip install google-genai")
                        self.gemini_configured = False
                    except Exception as e:
                        self.log(f"⚠️ Gemini 초기화 실패: {str(e)}")
                        self.gemini_configured = False
                else:
                    self.log("ℹ️ Gemini API 키 없음 (선택사항)")
                    self.gemini_configured = False

                # ========================================
                # 3. Claude API 로드 (신규)
                # ========================================
                claude_key = config.get('claude_api_key', '')
                if claude_key:
                    try:
                        import anthropic
                        self.claude_client = anthropic.Anthropic(api_key=claude_key)
                        self.claude_configured = True
                        self.log("✅ Claude API 키 로드 완료")
                    except ImportError:
                        self.log("⚠️ anthropic 패키지 없음")
                        self.log("   설치: pip install anthropic")
                        self.claude_configured = False
                    except Exception as e:
                        self.log(f"⚠️ Claude 초기화 실패: {str(e)}")
                        self.claude_configured = False
                else:
                    self.log("ℹ️ Claude API 키 없음 (선택사항)")
                    self.claude_configured = False

        except Exception as e:
            self.show_error("설정 오류", f"API 키 로드 실패:\n{str(e)}")

    def log(self, message):
        """로그 메시지 출력 - step1_log_text 사용"""
        print(message)

        # step1_log_text 없으면 버퍼에 저장
        if not hasattr(self, 'step1_log_text'):
            if not hasattr(self, '_pending_logs'):
                self._pending_logs = []
            self._pending_logs.append(message)
            return

        self.log_to_step1(message)


    # 탭 생성
    # ──────────────────────────────────────────────────────
    # 네이버 지식인 접속용 공유 크롬 (chrome_profile1) - IP 체크 후 열기
    # ──────────────────────────────────────────────────────
    def _check_ip_before_naver_open(self):
        """네이버 접속 전 IP 체크. 차단해야 하면 True 반환 (조회 실패시에도 차단)"""
        base_ip = get_env_value('base_ip', '').strip()
        if not base_ip:
            return False  # base_ip 미설정이면 체크 안 함

        current_ip = get_current_public_ip()
        if hasattr(self, 'label_current_ip_kin'):
            self.label_current_ip_kin.config(text=current_ip if current_ip else '조회 실패')
        if current_ip is None:
            messagebox.showerror(
                "IP 조회 실패 - 접속 중지",
                "⛔ 공인 IP 조회에 실패했습니다.\n\n"
                "인터넷 연결 상태를 확인하거나 잠시 후 다시 시도해주세요.\n"
                "(동일 네트워크 환경 확인이 불가능하여 안전을 위해 접속을 중지합니다)"
            )
            return True

        mode = get_env_value('network_mode', 'public')
        if mode == 'public':
            if current_ip != base_ip:
                messagebox.showerror(
                    "IP 불일치 - 접속 중지",
                    f"⛔ 공인IP 모드: 등록된 네트워크가 아닙니다!\n\n"
                    f"설정 Base IP: {base_ip}\n현재 공인IP: {current_ip}"
                )
                return True
        else:
            if current_ip == base_ip:
                messagebox.showerror(
                    "IP 불일치 - 접속 중지",
                    f"⛔ 테더링 모드: 테더링이 되어 있지 않습니다!\n\n"
                    f"설정 Base IP: {base_ip}\n현재 공인IP: {current_ip}"
                )
                return True
        return False

    def _is_app_control_block_error(self, error) -> bool:
        """[Ver7.20 이식 - 메인 프로그램 동일 로직] Windows 애플리케이션 제어
        정책(Smart App Control 등)이 실행파일을 차단해서 발생한
        OSError([WinError 4551])인지 판별. (chromedriver.exe 실행 시 간헐적으로 발생 확인됨)"""
        try:
            if getattr(error, 'winerror', None) == 4551:
                return True
            msg = str(error)
            return ("4551" in msg) or ("애플리케이션 제어 정책" in msg) or ("Application Control policy" in msg)
        except Exception:
            return False

    def _show_app_control_block_popup(self, original_error):
        """[Ver7.20 이식 - 메인 프로그램 동일 로직] Smart App Control(Windows 보안
        정책)이 chromedriver.exe 실행을 차단했을 때 원인과 해결방법을 안내하는 팝업.
        (자동 재시도까지 실패한 경우에만 호출됨)"""
        title_msg = "Windows 보안 정책이 크롬 실행을 차단했습니다 (WinError 4551)"

        self.log(f"🚨 [CRITICAL] {title_msg} | 원인: {original_error}")
        try:
            with open("critical_image_error.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {title_msg} | {original_error}\n")
        except Exception:
            pass

        try:
            popup = tk.Toplevel()
            popup.title("❌ 크롬 실행 중단 - 보안 정책 차단")
            popup.configure(bg='#B71C1C')
            popup.geometry("620x360")
            popup.attributes('-topmost', True)

            tk.Label(
                popup,
                text=f"⛔ {title_msg}",
                bg='#B71C1C', fg='white',
                font=('나눔고딕', 13, 'bold'),
                wraplength=580, justify='left'
            ).pack(pady=(20, 10), padx=20, anchor='w')

            guide_text = (
                "원인: Windows의 'Smart App Control(스마트 앱 컨트롤)' 보안 기능이\n"
                "chromedriver.exe 실행 자체를 차단했습니다. (동일 파일이 평소엔 정상 실행됨 - 간헐적 오작동)\n\n"
                "해결 방법:\n"
                "1. 시작 메뉴 → 'Windows 보안' 실행\n"
                "2. 앱 및 브라우저 컨트롤 → Smart App Control → 설정 → 끄기\n"
                "3. 끈 뒤 프로그램을 다시 실행해 재시도하세요\n"
                "4. 반복되면 크롬드라이버 캐시 폴더\n"
                "   (C:\\Users\\사용자명\\.cache\\selenium\\chromedriver) 를 삭제 후 재시도"
            )
            tk.Label(
                popup,
                text=guide_text,
                bg='#B71C1C', fg='#FFCDD2',
                font=('나눔고딕', 10),
                wraplength=580, justify='left'
            ).pack(pady=5, padx=20, anchor='w')

            def _open_windows_security():
                try:
                    os.startfile("windowsdefender://")
                except Exception as _open_err:
                    self.log(f"⚠️ Windows 보안 앱 열기 실패: {_open_err}")

            btn_frame = tk.Frame(popup, bg='#B71C1C')
            btn_frame.pack(pady=15)
            tk.Button(
                btn_frame,
                text="Windows 보안 열기",
                command=_open_windows_security,
                bg='white', fg='#B71C1C',
                font=('나눔고딕', 11, 'bold'),
                width=16
            ).pack(side='left', padx=5)
            tk.Button(
                btn_frame,
                text="확인",
                command=popup.destroy,
                bg='white', fg='#B71C1C',
                font=('나눔고딕', 11, 'bold'),
                width=10
            ).pack(side='left', padx=5)
        except Exception as _popup_err:
            self.log(f"⚠️ 보안 정책 차단 안내 팝업 표시 실패: {_popup_err}")

    def _get_or_create_shared_chrome(self):
        """chrome_profile1 프로필로 크롬을 하나만 유지 (다른 오토포스팅 프로그램들과 동일 프로필 공유)"""
        if self._shared_chrome_driver is not None:
            try:
                _ = self._shared_chrome_driver.window_handles
                return self._shared_chrome_driver
            except Exception:
                self._shared_chrome_driver = None

        profile_path = os.path.join(BASE_DIR, "chrome_profile1")
        os.makedirs(profile_path, exist_ok=True)

        options = ChromeOptions()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        _default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={get_env_value('chrome_user_agent', _default_ua)}")
        # [Ver7.20 이식] Windows 보안 정책(Smart App Control 등)이 chromedriver.exe
        # 실행 자체를 차단하는 경우(OSError: [WinError 4551]) 대응 - 간헐적으로
        # 발생하는 것으로 확인되어(동일 파일이 직전엔 정상 실행됨) 5초 후 1회
        # 자동 재시도. 재시도까지 실패하면 원인/해결방법 안내 팝업을 띄우고 예외 전파.
        try:
            driver = webdriver.Chrome(options=options)
        except OSError as e:
            if self._is_app_control_block_error(e):
                self.log(f"⚠️ Windows 보안 정책이 크롬 실행을 차단 - 5초 후 재시도합니다: {e}")
                time.sleep(5)
                try:
                    driver = webdriver.Chrome(options=options)
                except OSError as e2:
                    if self._is_app_control_block_error(e2):
                        self._show_app_control_block_popup(e2)
                    raise
            else:
                raise

        # navigator.webdriver 숨기기 (다른 프로그램들과 동일한 지문 위장 - 같은 프로필 활동 이력 일관성 유지)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en-US', 'en'] });
                window.chrome = { runtime: {} };
                const getImageData = CanvasRenderingContext2D.prototype.getImageData;
                CanvasRenderingContext2D.prototype.getImageData = function(...args) {
                    const imageData = getImageData.apply(this, args);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] = imageData.data[i] ^ (Math.floor(Math.random() * 2));
                    }
                    return imageData;
                };
                const toDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {
                    const ctx = this.getContext('2d');
                    if (ctx) { ctx.getImageData(0, 0, 1, 1); }
                    return toDataURL.apply(this, args);
                };
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.apply(this, [parameter]);
                };
            """
        })

        self._shared_chrome_driver = driver
        return driver

    def _kin_naver_login(self, driver, wait_for_manual=True):
        """[Ver7.20 신규] 메인 포스팅 프로그램의 login() 로직 이식 - Chrome 프로필 →
        쿠키파일 → 수동 로그인 순서로 네이버 로그인을 확인/수행한다.

        chrome_profile1 폴더를 다른 오토포스팅 프로그램들과 공유하므로,
        naver_cookies.pkl도 동일 경로(chrome_profile1/naver_cookies.pkl)를 그대로
        사용한다 - 어느 프로그램에서 로그인해도 쿠키가 서로 공유됨.

        [Ver7.48 추가] wait_for_manual=False로 호출하면 3차(최대 300초
        수동 로그인 대기)를 건너뛴다. 지식인 검색결과/질문 상세페이지는
        로그인 없이도 누구나 열람 가능한 공개 콘텐츠이고, 이 지식인
        서브프로그램 자체가 "수집" 전용(실제 블로그 포스팅은 하지 않음)
        이라, 순수 읽기용 수집 동작에서는 로그인 여부와 무관하게 진행해도
        문제없다 - 오히려 쿠키가 만료돼 있으면 매번 최대 5분씩 수집이
        멈춰버리는 게 더 큰 문제였다. 1차/2차(Chrome 프로필 로그인 유지
        확인, 저장된 쿠키 재사용)는 원래도 빠르고 로그인돼 있으면 이득만
        있으므로 그대로 시도하되, 그래도 안 되면 비로그인 상태로 그냥
        진행한다."""
        profile_path = os.path.join(BASE_DIR, "chrome_profile1")
        os.makedirs(profile_path, exist_ok=True)
        cookie_file = os.path.join(profile_path, "naver_cookies.pkl")

        # 1차: Chrome 프로필 자체의 로그인 유지 상태 확인
        try:
            driver.get("https://www.naver.com")
            time.sleep(random.uniform(1.0, 2.0))
            profile_cookies = {c.get("name") for c in driver.get_cookies()}
            if "NID_AUT" in profile_cookies and "NID_SES" in profile_cookies:
                self.log("✅ 네이버 로그인 유지 확인(Chrome 프로필)")
                return
        except Exception as e:
            self.log(f"⚠️ Chrome 프로필 로그인 확인 실패(무시): {e}")

        # 2차: 저장된 쿠키 파일로 로그인 시도
        if os.path.exists(cookie_file):
            self.log("🔑 저장된 쿠키로 로그인 시도")
            try:
                with open(cookie_file, 'rb') as f:
                    cookies = pickle.load(f)

                for domain_url in ["https://nid.naver.com", "https://www.naver.com"]:
                    driver.get(domain_url)
                    time.sleep(random.uniform(0.7, 1.5))
                    if domain_url == "https://nid.naver.com":
                        driver.delete_all_cookies()
                    for cookie in cookies:
                        try:
                            c = dict(cookie)
                            c.pop("sameSite", None)
                            if "expiry" in c:
                                try:
                                    c["expiry"] = int(c["expiry"])
                                except Exception:
                                    del c["expiry"]
                            driver.add_cookie(c)
                        except Exception:
                            pass
                    driver.refresh()
                    time.sleep(random.uniform(0.7, 1.5))

                driver.get("https://www.naver.com")
                time.sleep(random.uniform(1.0, 2.0))
                current_cookies = {c.get("name") for c in driver.get_cookies()}
                if "NID_AUT" in current_cookies and "NID_SES" in current_cookies:
                    self.log("✅ 저장된 쿠키로 로그인 성공")
                    return
                else:
                    self.log("⚠️ 쿠키 세션 만료 - 수동 로그인으로 진행")
                    try:
                        os.remove(cookie_file)
                    except Exception:
                        pass
            except Exception as e:
                self.log(f"⚠️ 쿠키 로드/적용 실패(무시): {e}")
        else:
            self.log("쿠키 파일 없음 - 수동 로그인으로 진행")

        # [Ver7.48 추가] 순수 수집(읽기전용) 호출은 여기서 멈추지 않고
        # 비로그인 상태로 그대로 진행한다(공개 콘텐츠라 로그인이 필수가
        # 아님) - 매번 최대 5분씩 블로킹되던 문제 해소.
        if not wait_for_manual:
            self.log("ℹ️ 로그인 상태 아님 - 비로그인으로 수집을 계속 진행합니다(공개 콘텐츠라 로그인 불필요).")
            return

        # 3차: 수동 로그인 대기 (최대 300초, 5초 간격으로 쿠키 확인)
        self.log("🔐 수동 로그인이 필요합니다 - 크롬창에서 로그인해주세요")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(random.uniform(2.0, 4.0))
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id')))
        except Exception:
            pass

        login_timeout, interval, elapsed, logged_in = 300, 5, 0, False
        while elapsed < login_timeout:
            try:
                cookies_now = {c.get("name") for c in driver.get_cookies()}
            except Exception:
                cookies_now = set()
            if "NID_AUT" in cookies_now or "NID_SES" in cookies_now:
                logged_in = True
                break
            self.log(f"⏳ 크롬창에서 로그인해주세요 ({login_timeout - elapsed}초 남음)")
            time.sleep(interval)
            elapsed += interval

        if not logged_in:
            self.log("❌ 로그인 타임아웃")
            raise TimeoutException("로그인 타임아웃")

        self.log("✅ 로그인 완료 - 쿠키 저장 중")
        all_cookies = []
        for url in ["https://nid.naver.com", "https://www.naver.com"]:
            driver.get(url)
            time.sleep(random.uniform(1.0, 2.0))
            all_cookies.extend(driver.get_cookies())
        uniq = {}
        for c in all_cookies:
            uniq[(c.get("name"), c.get("domain"), c.get("path"))] = c
        try:
            with open(cookie_file, 'wb') as f:
                pickle.dump(list(uniq.values()), f)
            self.log(f"✅ 쿠키 저장 완료: {cookie_file}")
        except Exception as e:
            self.log(f"⚠️ 쿠키 저장 실패(무시): {e}")

        self.log("✅ 네이버 로그인 성공")

    def _open_naver_shared_chrome(self, url):
        """[Ver7.20 수정] IP 체크 통과 시 chrome_profile1 공유 크롬으로 로그인 확인
        후(_kin_naver_login) URL을 새 탭으로 연다. 수동 로그인 대기가 최대 300초까지
        걸릴 수 있어 UI가 멈추지 않도록 백그라운드 스레드에서 처리한다."""
        if not SELENIUM_OK:
            messagebox.showerror(
                "selenium 미설치",
                "selenium이 설치되어 있지 않습니다.\n\n명령 프롬프트에서 아래 명령을 실행 후 다시 시도하세요.\npip install selenium"
            )
            return
        if self._check_ip_before_naver_open():
            return

        def worker():
            try:
                driver = self._get_or_create_shared_chrome()
            except Exception:
                self._shared_chrome_driver = None
                try:
                    driver = self._get_or_create_shared_chrome()
                except Exception as e2:
                    self.root.after(0, lambda: messagebox.showerror("크롬 열기 실패", str(e2)))
                    return

            try:
                self._kin_naver_login(driver)
            except Exception as e:
                self.log(f"⚠️ 로그인 확인 중 오류(무시하고 계속 진행): {e}")

            try:
                driver.execute_script("window.open(arguments[0], '_blank');", url)
                driver.switch_to.window(driver.window_handles[-1])
            except Exception as e2:
                self.root.after(0, lambda err=str(e2): messagebox.showerror("탭 열기 실패", err))

        threading.Thread(target=worker, daemon=True).start()

    def _save_base_ip_kin(self):
        """Base IP 저장 버튼 - env.txt 갱신 (다른 프로그램들과 공유)"""
        ip = self.base_ip_var_kin.get().strip()
        update_env_value('base_ip', ip)
        messagebox.showinfo("저장 완료", f"Base IP가 저장되었습니다.\n{ip if ip else '(비워서 저장 - 체크 비활성)'}")

    def _refresh_ip_label_kin(self):
        """IP 라벨만 조용히 갱신 (팝업 없음) - 프로그램 시작 후 자동 호출용"""
        current_ip = get_current_public_ip()
        if hasattr(self, 'label_current_ip_kin'):
            self.label_current_ip_kin.config(text=current_ip if current_ip else '조회 실패')
        return current_ip

    def _manual_ip_check_kin(self):
        """지금 확인 버튼 - 현재 IP 조회 및 Base IP와 비교"""
        base_ip = get_env_value('base_ip', '').strip()
        current_ip = self._refresh_ip_label_kin()

        if not base_ip:
            messagebox.showinfo("IP 상태 확인", "Base IP가 설정되어 있지 않아 비교할 수 없습니다.\n먼저 Base IP를 입력하고 저장해주세요.")
            return
        if current_ip is None:
            messagebox.showwarning("IP 상태 확인", "공인 IP 조회에 실패했습니다.\n인터넷 연결을 확인해주세요.")
            return

        mode = get_env_value('network_mode', 'public')
        mode_label = "공인IP 모드" if mode == 'public' else "테더링 모드"
        ok = (current_ip == base_ip) if mode == 'public' else (current_ip != base_ip)

        if ok:
            messagebox.showinfo("IP 상태 확인", f"✅ 정상입니다.\n\n모드: {mode_label}\nBase IP: {base_ip}\n현재 IP: {current_ip}")
        else:
            reason = "집 네트워크가 아닙니다." if mode == 'public' else "테더링이 되어 있지 않습니다."
            messagebox.showwarning("IP 상태 확인", f"⛔ 불일치 감지!\n\n모드: {mode_label}\nBase IP: {base_ip}\n현재 IP: {current_ip}\n\n{reason}")

    def _on_network_mode_change_kin(self):
        """네트워크 모드 라디오버튼 변경 시 env.txt 즉시 갱신"""
        update_env_value('network_mode', self.network_mode_var_kin.get())

    def create_step0_tab(self):
        """0단계: 주제 분류 탭"""
        step0_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(step0_frame, text="1)질문수집")
        step0_frame.columnconfigure(1, weight=1)

        # 네이버 지식인 접속 (공유 크롬 chrome_profile1 + IP 확인)
        kin_access_f = ttk.LabelFrame(step0_frame, text="네이버 지식인 접속", padding="8")
        kin_access_f.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 8))

        kin_row1 = ttk.Frame(kin_access_f)
        kin_row1.pack(fill="x", pady=(0, 4))
        ttk.Button(kin_row1, text="🌐 지식인 열기",
                   command=lambda: self._open_naver_shared_chrome("https://kin.naver.com")).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(kin_row1, text="Base IP:").pack(side=tk.LEFT)
        self.base_ip_var_kin = tk.StringVar(value=get_env_value('base_ip', ''))
        ttk.Entry(kin_row1, textvariable=self.base_ip_var_kin, width=18).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(kin_row1, text="💾 저장", command=self._save_base_ip_kin).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(kin_row1, text="현재 IP:").pack(side=tk.LEFT)
        self.label_current_ip_kin = ttk.Label(kin_row1, text="(미확인)", foreground="blue")
        self.label_current_ip_kin.pack(side=tk.LEFT, padx=(5, 15))
        ttk.Button(kin_row1, text="🔍 지금 확인", command=self._manual_ip_check_kin).pack(side=tk.LEFT)

        kin_row2 = ttk.Frame(kin_access_f)
        kin_row2.pack(fill="x", pady=(4, 0))
        self.network_mode_var_kin = tk.StringVar(value=get_env_value('network_mode', 'public'))
        ttk.Radiobutton(kin_row2, text="공인IP 모드 (현재IP = Base IP 이어야 통과)", variable=self.network_mode_var_kin,
                        value="public", command=self._on_network_mode_change_kin).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(kin_row2, text="테더링 모드 (현재IP ≠ Base IP 이어야 통과)", variable=self.network_mode_var_kin,
                        value="tethering", command=self._on_network_mode_change_kin).pack(side=tk.LEFT)

        ttk.Label(kin_access_f,
            text="※ 이 설정은 메인/정책뉴스 오토포스팅 프로그램과 같은 파일(env.txt)을 공유합니다.",
            foreground="gray", justify=tk.LEFT).pack(anchor="w", pady=(6, 0))

        guide = (
            "지식인 질문 또는 키워드를 입력하면 GPT가 주제를 분류합니다.\n"
            "경제_A~F / 건강 / 교육 / 자동차 / IT"
        )

        ttk.Label(step0_frame, text=guide, foreground="gray", justify=tk.LEFT).grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))

        # 입력 모드 선택
        mode_frame = ttk.LabelFrame(step0_frame, text="입력 방식", padding="5")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))

        self.classify_mode = tk.StringVar(value="question")
        ttk.Radiobutton(mode_frame, text="질문 입력", variable=self.classify_mode, value="question").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(mode_frame, text="키워드 입력", variable=self.classify_mode, value="keyword").grid(row=0, column=1, padx=10)

        # 입력창
        ttk.Label(step0_frame, text="입력:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(5, 0))
        self.classify_input = scrolledtext.ScrolledText(step0_frame, height=20, wrap=tk.WORD)
        self.classify_input.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        # 버튼
        btn_frame = ttk.Frame(step0_frame)
        btn_frame.grid(row=4, column=1, sticky=tk.E, pady=8)
        ttk.Button(btn_frame, text="🔍 주제 분류", command=self.start_classify_topic).pack(side=tk.LEFT, padx=(0, 5))
        
        def clear_all():
            self.classify_input.delete("1.0", tk.END)
            self.classify_result.config(state=tk.NORMAL)
            self.classify_result.delete("1.0", tk.END)
            self.classify_result.config(state=tk.DISABLED)
            self.manual_result_var.set("")
        
        ttk.Button(btn_frame, text="🗑️ 질문 내용 지우기", command=clear_all).pack(side=tk.LEFT)


        self.save_question_btn = ttk.Button(btn_frame, text="💾 질문 저장", command=self.save_classified_question, state=tk.NORMAL)
        self.save_question_btn.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Button(btn_frame, text="🔄 분류설정 새로고침", command=self.reload_classify_config).pack(side=tk.LEFT, padx=(5, 0))


        # 결과창
        ttk.Label(step0_frame, text="결과:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=(0, 0))
        self.classify_result = scrolledtext.ScrolledText(step0_frame, height=7, wrap=tk.WORD, state=tk.DISABLED)
        self.classify_result.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E))

        # 분류 결과 수동 수정 드롭다운
        result_edit_frame = ttk.LabelFrame(step0_frame, text="분류 결과 수동 수정", padding="5")
        result_edit_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(result_edit_frame, text="최종 분류:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        self.manual_result_var = tk.StringVar(value="")
        manual_result_combo = ttk.Combobox(
            result_edit_frame,
            textvariable=self.manual_result_var,
            values=[
                "경제A", "경제B", "경제C", "경제D",
                "경제E", "경제F", "경제G",
                "건강", "교육", "자동차", "IT", "기타"
            ],
            state="readonly",
            width=15
        )
        manual_result_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(result_edit_frame, text="← GPT 분류가 틀렸을 때 여기서 직접 수정하세요",
                  foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=5)

        # 로딩 후 IP 자동 조회 (팝업 없이 라벨만 갱신)
        self.root.after(1500, self._refresh_ip_label_kin)

    def start_classify_topic(self):
        """주제 분류 시작"""
        text = self.classify_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("입력 없음", "질문 또는 키워드를 입력하세요.")
            return
        if not self.openai_client:
            messagebox.showerror("API 키 없음", "OpenAI API 키를 먼저 설정하세요.")
            return

        self.classify_result.config(state=tk.NORMAL)
        self.classify_result.delete("1.0", tk.END)
        self.classify_result.insert(tk.END, "분류 중...\n")
        self.classify_result.config(state=tk.DISABLED)

        mode = self.classify_mode.get()
        threading.Thread(target=self.classify_topic_worker, args=(text, mode), daemon=True).start()

    # 저정 전 지식인 형태의 질문인지 검증
    def _is_kin_format(self, text: str) -> bool:
        """네이버 지식인 질문 형식 검증"""
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return False
        # 첫 줄이 제목 (너무 길지 않아야 함, 100자 이내)
        if len(lines[0]) > 100:
            return False
        # 조회수/작성일 패턴 또는 본문 내용 존재 여부 확인
        has_meta = any('조회수' in l or '작성일' in l for l in lines[:3])
        has_content = len(lines) >= 3 or (len(lines) == 2 and len(lines[1]) > 10)
        return has_meta or has_content


    def save_classified_question(self):
        """분류된 질문을 주제별 파일에 저장"""
        try:
            text = self.classify_input.get("1.0", tk.END).strip()

            if not text:
                messagebox.showwarning("저장 오류", "질문 내용을 입력하세요.")
                return

            # 네이버 지식인 형식 검증
            if not self._is_kin_format(text):
                proceed = messagebox.askyesno(
                    "형식 확인",
                    "네이버 지식인 질문 형식이 아닐 수 있습니다.\n\n"
                    "예상 형식:\n"
                    "  첫 줄: 질문 제목\n"
                    "  둘째 줄: 조회수 N 작성일 N시간 전 (선택)\n"
                    "  이후: 질문 내용\n\n"
                    "그래도 저장하시겠습니까?"
                )
                if not proceed:
                    return

            # 수동 수정값 우선, 없으면 GPT 분류 결과 첫 줄 사용
            manual = self.manual_result_var.get().strip()
            result = manual if manual else self.classify_result.get("1.0", tk.END).strip().split('\n')[0].strip()

            if not result:
                messagebox.showwarning("저장 오류", "분류 결과가 없습니다.\n주제 분류를 실행하거나 수동으로 분류를 선택하세요.")
                return

            # _get_blog_mapping() 반환값 / 콤보박스 표시값 / 카테고리명 모두 커버
            topic_filename_map = {
                # 블로그 코드
                "경제A": "경제-A-거시경제-경기-통화-금리",
                "경제B": "경제-B-금융-대출-신용-투자-보험-연금상품",
                "경제C": "경제-C-세금-조세제도-연말정산",
                "경제D": "경제-D-고용-노동-근로관계-취업지원",
                "경제E": "경제-E-복지연금-사회보험-국민연금-생활지원",
                "경제F": "경제-F-법률-행정-행정절차-가사",
                "경제G": "경제-G-부동산-임대차-매매-등기",

                # 콤보박스 표시값(풀네임)
                "경제-A-거시경제-경기-통화-금리": "경제-A-거시경제-경기-통화-금리",
                "경제-B-금융-대출-신용-투자-보험-연금상품": "경제-B-금융-대출-신용-투자-보험-연금상품",
                "경제-C-세금-조세제도-연말정산": "경제-C-세금-조세제도-연말정산",
                "경제-D-고용-노동-근로관계-취업지원": "경제-D-고용-노동-근로관계-취업지원",
                "경제-E-복지연금-사회보험-국민연금-생활지원": "경제-E-복지연금-사회보험-국민연금-생활지원",
                "경제-F-법률-행정-행정절차-가사": "경제-F-법률-행정-행정절차-가사",
                "경제-G-부동산-임대차-매매-등기": "경제-G-부동산-임대차-매매-등기",

                # 단일 도메인
                "건강": "건강",
                "교육": "교육",
                "자동차": "자동차",
                "IT": "IT",
                "기타": "기타",

                # 카테고리명이 직접 들어오는 경우도 허용
                "거시경제": "경제-A-거시경제-경기-통화-금리",
                "금융": "경제-B-금융-대출-신용-투자-보험-연금상품",
                "세금": "경제-C-세금-조세제도-연말정산",
                "고용": "경제-D-고용-노동-근로관계-취업지원",
                "복지연금": "경제-E-복지연금-사회보험-국민연금-생활지원",
                "법률행정": "경제-F-법률-행정-행정절차-가사",
                "부동산": "경제-G-부동산-임대차-매매-등기",
            }

            topic_name = topic_filename_map.get(result)

            if not topic_name:
                self.log(f"❌ 분류 결과 매핑 실패: '{result}' → 저장 취소")
                messagebox.showerror(
                    "저장 오류",
                    f"분류 결과를 파일명으로 변환할 수 없습니다.\n\n"
                    f"분류 결과: '{result}'\n\n"
                    f"0단계에서 주제 분류를 다시 실행하세요."
                )
                return

            filename = f"자동생성_{topic_name}.txt"

            base_folder = self.base_folder_var.get().strip()
            if not base_folder:
                base_folder = self.base_folder

            file_path = os.path.join(base_folder, filename)

            # [Ver8.32 신규] 저장 전 중복 체크 - 정식 질문DB 중복판정
            # (check_question_duplicate)은 여전히 "0-1)사전 필터링" 단계
            # 몫이지만(이 탭은 원문 수집만 담당, 바로 아래 Ver7.08 주석
            # 참고), 같은 질문을 실수로 두 번 붙여넣고 저장하는 사고를
            # 막는 가벼운 안전망은 필요하다. "3)퍼플렉시티 수집"의
            # save_perplexity_collect와 동일한 컨셉 - 같은 누적 파일
            # (자동생성_{주제}.txt) 안의 기존 블록들과 새 내용의 앞부분
            # (300자)을 문자열 유사도로 비교해 90% 이상이면 확인 팝업.
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

                new_compare = re.sub(r'\s+', ' ', text[:300]).strip()
                existing_blocks = re.split(r'\n?={60}\n', existing_content)

                duplicate_title = None
                for block in existing_blocks:
                    block = re.sub(r'^\n?\[\d{4}-\d{2}-\d{2}[^\]]*\]\n', '', block.strip('\n'))
                    if not block.strip():
                        continue
                    existing_compare = re.sub(r'\s+', ' ', block[:300]).strip()
                    ratio = difflib.SequenceMatcher(None, new_compare, existing_compare).ratio()
                    if ratio >= 0.9:
                        duplicate_title = block.strip().split('\n')[0].strip()
                        break

                if duplicate_title:
                    proceed = messagebox.askyesno(
                        "중복 자료 감지",
                        f"유사한 질문이 이미 이 주제 파일에 저장되어 있습니다. (유사도 90% 이상)\n\n"
                        f"기존 질문: {duplicate_title}\n\n"
                        f"그래도 저장하시겠습니까?"
                    )
                    if not proceed:
                        return

            # [Ver7.08 변경] 0단계는 이제 "수집"만 담당한다. 적합성 사전
            # 필터링(상품추천형/단일기관행정형/순수고민상담형/해외교육/
            # 개인특정가능 등 배제)을 거쳐 통과한 질문만 질문DB에 넣는
            # 방식으로 역할을 분리했다. 질문DB 등록 및 그에 따른 중복
            # 차단은 "0-1) 사전 필터링" 탭에서 처리한다. 여기서는 원문을
            # 자동생성_{주제}.txt에 그대로 누적 저장만 한다.
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            separator = f"\n{'='*60}\n[{timestamp}]\n"

            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(separator)
                f.write(text)
                f.write("\n")

            self.log(f"💾 질문 저장 완료(수집): {filename}")
            self.log(f"   ℹ️ 질문DB 등록은 '0-1) 사전 필터링' 탭에서 선별 후 진행하세요.")

            # 입력창 클리어 및 버튼 비활성화
            self.classify_input.delete("1.0", tk.END)
            self.classify_result.config(state=tk.NORMAL)
            self.classify_result.delete("1.0", tk.END)
            self.classify_result.config(state=tk.DISABLED)

            #messagebox.showinfo("저장 완료", f"저장되었습니다.\n파일: {filename}")
            self.log(f"저장되었습니다.\n파일: {filename}")
        
        except Exception as e:
            self.log(f"❌ 질문 저장 오류: {str(e)}")
            messagebox.showerror("저장 오류", f"저장 중 오류 발생:\n{str(e)}")

    def _load_classify_config(self) -> dict:
        """주제 분류 외부 설정 파일 로드"""
        import json
        config_dir = Path(__file__).parent / "Naver_blog_kin_topic_classify_config"
        config = {}
        load_errors = 0
        try:
            with open(config_dir / "categories.json", encoding="utf-8") as f:
                config["categories"] = json.load(f)
        except Exception as e:
            self.log(f"⚠️ categories.json 로드 실패: {e}")
            config["categories"] = {}
            load_errors += 1
        try:
            with open(config_dir / "boundary_rules.txt", encoding="utf-8") as f:
                config["boundary_rules"] = f.read()
        except Exception as e:
            self.log(f"⚠️ boundary_rules.txt 로드 실패: {e}")
            config["boundary_rules"] = ""
            load_errors += 1
        try:
            with open(config_dir / "postprocess_rules.json", encoding="utf-8") as f:
                config["postprocess_rules"] = json.load(f)
        except Exception as e:
            self.log(f"⚠️ postprocess_rules.json 로드 실패: {e}")
            config["postprocess_rules"] = {"절대고정": []}
            load_errors += 1
        try:
            with open(config_dir / "fallback_keywords.json", encoding="utf-8") as f:
                config["fallback_keywords"] = json.load(f)
        except Exception as e:
            self.log(f"⚠️ fallback_keywords.json 로드 실패: {e}")
            config["fallback_keywords"] = {}
            load_errors += 1
        if load_errors == 0:
            self.log(f"✅ 주제분류 설정 로드 완료")
        else:
            self.log(f"⚠️ 주제분류 설정 로드 실패 ({load_errors}개 파일 누락) - 분류 기능 제한됨")
        return config

    def _check_classify_config_files(self):
        """주제 분류 설정 파일 존재 여부 확인 및 팝업 처리"""
        config_dir = Path(__file__).parent / "Naver_blog_kin_topic_classify_config"
        required_files = [
            "categories.json",
            "boundary_rules.txt",
            "postprocess_rules.json",
            "fallback_keywords.json"
        ]

        missing = []
        if not config_dir.exists():
            missing.append(f"폴더: {config_dir.name}")
        else:
            for fname in required_files:
                if not (config_dir / fname).exists():
                    missing.append(fname)

        if not missing:
            return

        detail = "\n".join(f"  • {m}" for m in missing)
        result = messagebox.askyesno(
            "주제 분류 설정 오류",
            f"주제 자동 분류에 필요한 파일이 없습니다.\n\n"
            f"누락 항목:\n{detail}\n\n"
            f"※ 2)주제자동분류 기능을 사용할 수 없습니다.\n\n"
            f"계속 프로그램을 사용하시겠습니까?",
            icon='warning'
        )
        if not result:
            self.quit_application()


    # 파일 수정 후 업데이트
    def reload_classify_config(self):
        """주제 분류 설정 파일 새로고침"""
        self._classify_config = self._load_classify_config()
        messagebox.showinfo("새로고침 완료",
            "주제 분류 설정이 새로고침되었습니다.\n\n"
            "✅ categories.json\n"
            "✅ boundary_rules.txt\n"
            "✅ postprocess_rules.json\n"
            "✅ fallback_keywords.json"
        )


    def _postprocess_category(self, text: str, category: str) -> str:
        """GPT 결과 후처리 - 외부 postprocess_rules.json 기반"""
        text = (text or "").strip()
        rules = self._classify_config.get("postprocess_rules", {}).get("절대고정", [])

        def has_any(keywords):
            t = text.replace(" ", "").lower()
            for kw in keywords:
                if kw.replace(" ", "").lower() in t:
                    return True
            return False

        for rule in rules:
            include = rule.get("포함키워드", [])
            exclude = rule.get("제외키워드", [])
            result = rule.get("결과", "")
            if has_any(include) and not has_any(exclude):
                return result

        return category

    def _call_gpt_classify(self, text: str) -> str:
        """
        2단계 GPT 분류:
        1단계: GPT → 핵심 추출 + 후보 카테고리 2~3개 압축
        2단계: GPT → 후보만 보고 최종 확정
        fallback: 키워드 보조
        """
        text = (text or "").strip()
        text_lower = text.lower()

        CATEGORIES = self._classify_config.get("categories", {})
        if not CATEGORIES:
            CATEGORIES = {"기타": "위 분류에 해당하지 않는 경우"}

        boundary_rules = self._classify_config.get("boundary_rules", "")

        # =========================
        # 1️⃣ GPT 1단계: 핵심 추출 + 후보 압축
        # =========================
        stage1_result = ""
        candidates = list(CATEGORIES.keys())

        try:
            prompt_stage1 = (
                "아래 질문을 읽고 3가지를 출력하세요.\n\n"
                f"[질문]\n{text}\n\n"
                "[출력 형식]\n"
                "행동: 질문자가 최종적으로 해결하려는 것 (1문장)\n"
                "소재: 질문의 주된 소재·영역 (핵심 단어 3개 이내)\n"
                f"후보: 아래 중 가능성 높은 카테고리 2~3개 (쉼표 구분)\n\n"
                f"카테고리 목록: {' / '.join(CATEGORIES.keys())}"
            )

            response1 = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                #model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt_stage1}],
                temperature=0,
                max_tokens=120
            )

            stage1_result = response1.choices[0].message.content.strip()
            self.log(f"🔍 1단계:\n{stage1_result}")

            # 후보 추출
            extracted = []
            for line in stage1_result.split('\n'):
                if line.strip().startswith("후보:"):
                    candidate_text = line.replace("후보:", "").strip()
                    for cat in CATEGORIES:
                        if cat in candidate_text:
                            extracted.append(cat)
                    break

            if extracted:
                candidates = extracted
                self.log(f"✅ 후보: {candidates}")
            else:
                self.log("⚠️ 후보 추출 실패 → 전체 카테고리 사용")

        except Exception as e:
            self.log(f"⚠️ GPT 1단계 오류: {e} → 전체 카테고리로 진행")

        # =========================
        # 2️⃣ GPT 2단계: 후보만 보고 최종 확정
        # =========================
        try:
            # 후보 카테고리 설명만 압축
            candidate_lines = "\n".join(
                f"{cat}: {CATEGORIES[cat]}"
                for cat in candidates if cat in CATEGORIES
            )

            prompt_stage2 = (
                "아래 [1단계 분석]과 [경계 기준]을 참고해서 "
                "[후보 카테고리] 중 정확히 1개만 선택하세요.\n\n"
                f"[원본 질문]\n{text}\n\n"
                f"[1단계 분석]\n{stage1_result}\n\n"
                f"[후보 카테고리]\n{candidate_lines}\n\n"
                f"[경계 기준]\n{boundary_rules}\n\n"
                "[출력 형식]\n"
                "최종: 카테고리명\n"
                "보조: 카테고리명 또는 없음\n\n"
                "[주의]\n"
                "- 최종 줄에는 카테고리명만 단독 출력\n"
                "- 보조 줄은 반드시 출력. 2개 분야에 걸치면 해당 카테고리명, 아니면 '없음'\n"
                f"- 반드시 후보 중에서만 선택: {', '.join(candidates)}"
            )

            response2 = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                #model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt_stage2}],
                temperature=0,
                max_tokens=80
            )

            stage2_result = response2.choices[0].message.content.strip()
            self.log(f"✅ 2단계 결과: {stage2_result}")

            lines2 = stage2_result.split('\n')

            # 보조 카테고리 추출
            self._classify_secondary = ""
            for line in lines2:
                line_s = line.strip()
                if line_s.startswith("보조:"):
                    secondary_text = line_s.replace("보조:", "").strip()
                    if secondary_text == "없음":
                        break
                    for cat in CATEGORIES:
                        if cat == secondary_text or cat in secondary_text:
                            self._classify_secondary = cat
                            break

            if self._classify_secondary:
                self.log(f"🔍 보조 분야: {self._classify_secondary}")

            # 최종 카테고리 추출
            main_cat = ""
            for line in lines2:
                line_s = line.strip()
                if line_s.startswith("최종:"):
                    main_cat = line_s.replace("최종:", "").strip()
                    break

            if main_cat in CATEGORIES:
                return self._postprocess_category(text, main_cat)
            for cat in CATEGORIES:
                if cat in main_cat:
                    return self._postprocess_category(text, cat)

            # 후보에서 재탐색
            for cat in candidates:
                if cat in stage2_result:
                    return self._postprocess_category(text, cat)

            self.log(f"⚠️ 2단계 매칭 실패 → 키워드 보조 시도")

        except Exception as e:
            self.log(f"⚠️ GPT 2단계 오류: {e} → 키워드 보조 시도")

        # =========================
        # 3️⃣ 키워드 보조 fallback
        # =========================
        fallback_category = "기타"
        fk = self._classify_config.get("fallback_keywords", {})
        order = fk.get("순서", [])

        for cat_key in order:
            if cat_key not in fk:
                continue
            rule = fk[cat_key]
            include = rule.get("포함", [])
            exclude = rule.get("제외", [])
            is_lower = rule.get("소문자", False)
            search_text = text_lower if is_lower else text
            matched = any(k.lower() in search_text.lower() for k in include)
            excluded = any(k in text for k in exclude)
            if matched and not excluded:
                actual_cat = cat_key.split("_")[0]
                fallback_category = actual_cat
                break

        final_category = self._postprocess_category(text, fallback_category)

        if final_category == "기타":
            self.log(f"⚠️ 미분류: {text[:80]}")

        return final_category

    def _get_blog_mapping(self, category: str) -> str:
        """
        2단계: 1단계 분류 결과를 2차 각색 프롬프트 단위로 매핑
        반환값:
          경제A / 경제B / 경제C / 경제D / 경제E / 경제F / 경제G /
          건강 / 교육 / 자동차 / IT / 기타
        """
        BLOG_MAPPING = {
            "거시경제": "경제A",
            "금융":     "경제B",
            "세금":     "경제C",
            "고용":     "경제D",
            "복지연금": "경제E",
            "법률행정": "경제F",
            "부동산":   "경제G",
            "건강":     "건강",
            "교육":     "교육",
            "자동차":   "자동차",
            "IT":       "IT",
            "기타":     "기타",
        }

        result = BLOG_MAPPING.get(category, "기타")
        self.log(f"✅ 분류: {category} → {result}")
        return result


    def classify_topic_worker(self, text, mode):
        try:
            category = self._call_gpt_classify(text)
            result   = self._get_blog_mapping(category)
        except Exception as e:
            result = f"❌ 분류 오류: {str(e)}"

        def update_ui():
            # 퍼플렉시티 분야 매핑
            perplexity_map = {
                "경제A": "[A] 거시경제·경제정책·경기",
                "경제B": "[B] 금융·대출·보험·투자·연금상품",
                "경제C": "[C] 세금·조세제도·연말정산",
                "경제D": "[D] 고용·노동·근로관계·고용보험",
                "경제E": "[E] 복지·사회보험·국민연금·생활지원",
                "경제F": "[F] 법률·행정·행정절차",
                "경제G": "[G] 부동산·임대차·매매·등기",
                "건강":  "건강",
                "교육":  "교육",
                "자동차": "자동차",
                "IT":    "IT",
                "기타":  "기타",
            }

            perplexity_label = perplexity_map.get(result, "알 수 없음")

            secondary = getattr(self, '_classify_secondary', '')
            secondary_mapped = self._get_blog_mapping(secondary) if secondary else ''
            secondary_label = perplexity_map.get(secondary_mapped, '') if secondary_mapped else ''

            # 퍼플렉시티 분야 표시 (보조 있으면 옆에 병기)
            if secondary_label:
                perplexity_display = f"{perplexity_label}  ·  보조: {secondary_label}"
            else:
                perplexity_display = perplexity_label

            display_text = (
                f"{result}\n"
                f"─────────────────────\n"
                f"퍼플렉시티 분야: {perplexity_display}\n"
                f"─────────────────────\n"
                f"※ 경계 질문은 수동 확인 권장"
            )

            self.classify_result.config(state=tk.NORMAL)
            self.classify_result.delete("1.0", tk.END)
            self.classify_result.insert(tk.END, display_text)
            self.classify_result.config(state=tk.DISABLED)

            # 드롭다운 자동 설정
            self.manual_result_var.set(result)

            pass  # 저장 버튼은 상시 활성화

        self.root.after(0, update_ui)


    def open_kin_perplexity_prompt_settings(self):
        """퍼플렉시티용 주제별 프롬프트 설정 팝업 (매핑설정과 별도 파일)"""
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        current = self.load_kin_perplexity_prompts()

        popup = tk.Toplevel(self.root)
        popup.title("퍼플렉시티 프롬프트 설정 (주제별)")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 900, 500
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text="주제별로 퍼플렉시티 조사 요청용 프롬프트 파일을 지정하세요.",
                  foreground="gray").pack(anchor="w", padx=10, pady=(10, 5))

        body = ttk.Frame(popup, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)

        prompt_vars = {}
        for i, topic in enumerate(topics):
            ttk.Label(body, text=topic).grid(row=i, column=0, sticky=tk.W, pady=3, padx=(0, 8))
            var = tk.StringVar(value=current.get(topic, ""))
            prompt_vars[topic] = var
            ttk.Entry(body, textvariable=var, width=60).grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

            def browse(v=var):
                pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else "."
                path = filedialog.askopenfilename(
                    title="퍼플렉시티 프롬프트 파일 선택", initialdir=pf or ".",
                    filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
                if path:
                    v.set(os.path.basename(path))

            ttk.Button(body, text="찾기", command=browse).grid(row=i, column=2, padx=5, pady=3)

        def do_save():
            new_prompts = {t: v.get().strip() for t, v in prompt_vars.items() if v.get().strip()}
            self.save_kin_perplexity_prompts(new_prompts)
            self.log(f"💾 퍼플렉시티 프롬프트 설정 저장 완료: {len(new_prompts)}개")
            popup.destroy()

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="저장", command=do_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="취소", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    def open_kin_prefilter_prompt_settings(self):
        """[Ver7.08 추가] 사전 필터링(질문 선별)용 주제별 프롬프트 설정 팝업.
        구조는 open_kin_perplexity_prompt_settings와 동일하며, 저장 대상
        파일만 Naver_blog_config_kin_prefilter.json으로 다르다."""
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        current = self.load_kin_prefilter_prompts()

        popup = tk.Toplevel(self.root)
        popup.title("사전 필터링 프롬프트 설정 (주제별)")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 900, 500
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text="주제별로 사전 필터링(질문 선별)용 프롬프트 파일을 지정하세요.\n"
                              "(프롬프트 파일 안에 {questions_batch} 자리에 불러온 질문 목록이 자동으로 채워집니다.)",
                  foreground="gray", justify=tk.LEFT).pack(anchor="w", padx=10, pady=(10, 5))

        body = ttk.Frame(popup, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)

        prompt_vars = {}
        for i, topic in enumerate(topics):
            ttk.Label(body, text=topic).grid(row=i, column=0, sticky=tk.W, pady=3, padx=(0, 8))
            var = tk.StringVar(value=current.get(topic, ""))
            prompt_vars[topic] = var
            ttk.Entry(body, textvariable=var, width=60).grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

            def browse(v=var):
                pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else "."
                path = filedialog.askopenfilename(
                    title="사전 필터링 프롬프트 파일 선택", initialdir=pf or ".",
                    filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
                if path:
                    v.set(os.path.basename(path))

            ttk.Button(body, text="찾기", command=browse).grid(row=i, column=2, padx=5, pady=3)

        def do_save():
            new_prompts = {t: v.get().strip() for t, v in prompt_vars.items() if v.get().strip()}
            self.save_kin_prefilter_prompts(new_prompts)
            self.log(f"💾 사전 필터링 프롬프트 설정 저장 완료: {len(new_prompts)}개")
            popup.destroy()

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="저장", command=do_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="취소", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    # ── [Ver7.10 추가] "0-1)질문 상세분석" 탭용 프롬프트 설정 팝업.
    # 구조는 open_kin_prefilter_prompt_settings와 동일하며, 저장 대상
    # 파일만 Naver_blog_config_kin_detail.json으로 다르다. {questions_batch}
    # 같은 치환 자리는 없음 — 프롬프트 뒤에 선택한 질문(제목+본문)이
    # 그대로 이어붙는 방식(1)/4)/5)탭과 동일).
    def open_kin_detail_prompt_settings(self):
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        current = self.load_kin_detail_prompts()

        popup = tk.Toplevel(self.root)
        popup.title("질문 상세분석 프롬프트 설정 (주제별)")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 900, 500
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text="주제별로 질문 상세분석(가치판단+관련질문확장+키워드전략+리서치브리프)용 프롬프트 파일을 지정하세요.\n"
                              "(프롬프트 파일 뒤에 왼쪽에서 고른 질문의 제목·본문이 자동으로 이어붙습니다.)",
                  foreground="gray", justify=tk.LEFT).pack(anchor="w", padx=10, pady=(10, 5))

        body = ttk.Frame(popup, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)

        prompt_vars = {}
        for i, topic in enumerate(topics):
            ttk.Label(body, text=topic).grid(row=i, column=0, sticky=tk.W, pady=3, padx=(0, 8))
            var = tk.StringVar(value=current.get(topic, ""))
            prompt_vars[topic] = var
            ttk.Entry(body, textvariable=var, width=60).grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

            def browse(v=var):
                pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else "."
                path = filedialog.askopenfilename(
                    title="질문 상세분석 프롬프트 파일 선택", initialdir=pf or ".",
                    filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
                if path:
                    v.set(os.path.basename(path))

            ttk.Button(body, text="찾기", command=browse).grid(row=i, column=2, padx=5, pady=3)

        def do_save():
            new_prompts = {t: v.get().strip() for t, v in prompt_vars.items() if v.get().strip()}
            self.save_kin_detail_prompts(new_prompts)
            self.log(f"💾 질문 상세분석 프롬프트 설정 저장 완료: {len(new_prompts)}개")
            popup.destroy()

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="저장", command=do_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="취소", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    # ── [Ver7.10 추가] "5)퍼플렉시티 자료검증" 탭용 프롬프트 설정 팝업.
    # 구조는 open_kin_detail_prompt_settings와 동일, 저장 파일만 다르다.
    def open_kin_verify_prompt_settings(self):
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        current = self.load_kin_verify_prompts()

        popup = tk.Toplevel(self.root)
        popup.title("퍼플렉시티 교차검증 프롬프트 설정 (주제별)")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 900, 500
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text="주제별로 퍼플렉시티 결과 교차검증용 프롬프트 파일을 지정하세요.\n"
                              "(프롬프트 파일 뒤에 왼쪽에서 고른 퍼플렉시티 원본자료가 자동으로 이어붙습니다.)",
                  foreground="gray", justify=tk.LEFT).pack(anchor="w", padx=10, pady=(10, 5))

        body = ttk.Frame(popup, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)

        prompt_vars = {}
        for i, topic in enumerate(topics):
            ttk.Label(body, text=topic).grid(row=i, column=0, sticky=tk.W, pady=3, padx=(0, 8))
            var = tk.StringVar(value=current.get(topic, ""))
            prompt_vars[topic] = var
            ttk.Entry(body, textvariable=var, width=60).grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

            def browse(v=var):
                pf = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else "."
                path = filedialog.askopenfilename(
                    title="퍼플렉시티 교차검증 프롬프트 파일 선택", initialdir=pf or ".",
                    filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
                if path:
                    v.set(os.path.basename(path))

            ttk.Button(body, text="찾기", command=browse).grid(row=i, column=2, padx=5, pady=3)

        def do_save():
            new_prompts = {t: v.get().strip() for t, v in prompt_vars.items() if v.get().strip()}
            self.save_kin_verify_prompts(new_prompts)
            self.log(f"💾 퍼플렉시티 교차검증 프롬프트 설정 저장 완료: {len(new_prompts)}개")
            popup.destroy()

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="저장", command=do_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="취소", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    def open_perplexity_question_picker(self):
        """질문DB에서 질문을 골라 퍼플렉시티 프롬프트와 함께 클립보드로 복사하는 팝업"""
        base_folder = self.base_folder_var.get().strip() or self.base_folder

        popup = tk.Toplevel(self.root)
        popup.title("질문 선택 → 퍼플렉시티 프롬프트와 함께 복사")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        w, h = 1300, 640
        popup.geometry(f"{w}x{h}+{(screen_width-w)//2}+{(screen_height-h)//2}")
        popup.transient(self.root)
        popup.grab_set()

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        top_frame = ttk.Frame(popup, padding=10)
        top_frame.pack(fill=tk.X)
        ttk.Label(top_frame, text="주제:").pack(side=tk.LEFT, padx=(0, 5))

        default_topic = self.perp_topic_var.get() if hasattr(self, 'perp_topic_var') else topics[0]
        topic_var = tk.StringVar(value=default_topic if default_topic in topics else topics[0])
        ttk.Combobox(top_frame, textvariable=topic_var, values=topics, state="readonly", width=40, height=11).pack(side=tk.LEFT, padx=(0, 10))

        hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_perplexity_picker', False))
        ttk.Checkbutton(top_frame, text="사용한 질문 숨기기", variable=hide_used_var).pack(side=tk.LEFT, padx=(10, 0))

        list_frame = ttk.Frame(popup, padding=(10, 0, 10, 10))
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("used", "title", "date")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=18)
        tree.heading("used", text="사용")
        tree.heading("title", text="질문 제목")
        tree.heading("date", text="저장일")
        tree.column("used", width=50, anchor=tk.CENTER)
        tree.column("title", width=850)
        tree.column("date", width=100, anchor=tk.CENTER)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        records_cache = {'records': []}

        def get_usage_path(topic):
            return os.path.join(base_folder, topic, "질문_퍼플렉시티_사용여부.json")

        def load_usage(topic):
            return load_json_db(get_usage_path(topic))

        def save_usage(topic, usage_list):
            save_json_db(get_usage_path(topic), usage_list)

        def refresh_list():
            tree.delete(*tree.get_children())
            topic = topic_var.get()
            db_path = get_question_db_path(base_folder, topic)
            records = load_json_db(db_path)
            records_cache['records'] = records

            usage_raw = load_usage(topic)
            used_titles = set(usage_raw) if isinstance(usage_raw, list) else set()

            for i, r in enumerate(records):
                used = r.get("title", "") in used_titles
                if hide_used_var.get() and used:
                    continue
                tree.insert("", tk.END, iid=str(i), values=(
                    "✅" if used else "", r.get("title", ""), r.get("date", "")
                ))

        topic_var.trace_add("write", lambda *_: refresh_list())
        hide_used_var.trace_add("write", lambda *_: refresh_list())
        hide_used_var.trace_add("write", lambda *_: self.save_kin_ui_setting('hide_used_perplexity_picker', hide_used_var.get()))
        refresh_list()

        def copy_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("알림", "복사할 질문을 먼저 선택하세요.")
                return
            idx = int(sel[0])
            record = records_cache['records'][idx]
            topic = topic_var.get()

            prompts = self.load_kin_perplexity_prompts()
            prompt_filename = prompts.get(topic, "")
            if not prompt_filename:
                messagebox.showwarning(
                    "퍼플렉시티 프롬프트 없음",
                    f"'{topic}' 주제에 등록된 퍼플렉시티 프롬프트가 없습니다.\n"
                    f"'퍼플렉시티 프롬프트 설정'에서 먼저 등록하세요."
                )
                return

            prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
            prompt_path = os.path.join(prompt_folder, prompt_filename)
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
            except Exception as e:
                messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
                return

            content = (
                f"{prompt_text}\n\n"
                f"───────────────────\n"
                f"[지식인 질문]\n"
                f"제목: {record.get('title', '')}\n"
                f"본문: {record.get('body', '')}\n"
            )

            popup.clipboard_clear()
            popup.clipboard_append(content)

            # 사용여부 표시
            usage_raw = load_usage(topic)
            used_titles = list(usage_raw) if isinstance(usage_raw, list) else []
            if record.get("title", "") not in used_titles:
                used_titles.append(record.get("title", ""))
            save_usage(topic, used_titles)
            refresh_list()

            self.log(f"📋 퍼플렉시티용 질문 복사 완료 (프롬프트: {prompt_filename}): {record.get('title','')}")
            messagebox.showinfo("복사 완료", "프롬프트 + 질문이 클립보드에 복사되었습니다.\n퍼플렉시티 웹에 붙여넣으세요.")

        def copy_prompt_only():
            topic = topic_var.get()
            prompts = self.load_kin_perplexity_prompts()
            prompt_filename = prompts.get(topic, "")
            if not prompt_filename:
                messagebox.showwarning(
                    "퍼플렉시티 프롬프트 없음",
                    f"'{topic}' 주제에 등록된 퍼플렉시티 프롬프트가 없습니다.\n"
                    f"'퍼플렉시티 프롬프트 설정'에서 먼저 등록하세요."
                )
                return
            prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
            prompt_path = os.path.join(prompt_folder, prompt_filename)
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
            except Exception as e:
                messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
                return
            popup.clipboard_clear()
            popup.clipboard_append(KIN_PROMPT_CONTINUITY_NOTICE + prompt_text)
            messagebox.showinfo("복사 완료", "프롬프트만 클립보드에 복사되었습니다.")

        def copy_question_only():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("알림", "복사할 질문을 먼저 선택하세요.")
                return
            idx = int(sel[0])
            record = records_cache['records'][idx]
            content = f"제목: {record.get('title', '')}\n본문: {record.get('body', '')}\n"
            popup.clipboard_clear()
            popup.clipboard_append(content)
            messagebox.showinfo("복사 완료", "질문만 클립보드에 복사되었습니다.")

        def toggle_used():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
                return
            idx = int(sel[0])
            record = records_cache['records'][idx]
            topic = topic_var.get()
            title = record.get("title", "")

            usage_raw = load_usage(topic)
            used_titles = list(usage_raw) if isinstance(usage_raw, list) else []
            if title in used_titles:
                used_titles.remove(title)  # 취소 (사용 안 함으로 되돌리기)
            else:
                used_titles.append(title)  # 사용함으로 체크
            save_usage(topic, used_titles)
            refresh_list()

        btn_frame = ttk.Frame(popup, padding=(10, 0, 10, 10))
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="📋 프롬프트+질문 복사", command=copy_selected).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="프롬프트만 복사", command=copy_prompt_only).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="질문만 복사", command=copy_question_only).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="사용여부 토글", command=toggle_used).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="🔄 새로고침", command=refresh_list).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="닫기", command=popup.destroy).pack(side=tk.RIGHT)

    # ══════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════
    # [Ver7.17 신규] 좌우분할 탭 5곳(0-1/1/2-1/4/5) 공용 "사용" 셀 갱신 헬퍼
    # ────────────────────────────────────────────────────────────
    # 문제: 기존엔 "복사" 버튼을 누른 그 순간 usage[title]=True를 즉시
    # 기록하고 목록 전체를 delete()+insert()로 다시 그렸다. 그 결과
    # ① 체크(✅)가 "복사했다"만 반영하고 "붙여넣기→저장까지 끝냈다"는
    #   전혀 확인하지 않아, 복사만 하고 저장을 깜빡해도 영구히 ✅로
    #   남아 작업 누락을 알아챌 방법이 없었고,
    # ② 목록을 통째로 새로 그리면서 선택/포커스가 매번 풀려 다시
    #   클릭해서 선택해야 하는 부자연스러운 흐름이 생겼다.
    #
    # 수정: "복사"는 그 행의 사용 셀만 "📋(진행중)"으로 바꾸고(트리
    # 재생성 없음 → 선택 유지), 실제 "저장" 함수가 성공했을 때만
    # usage 파일에 True를 기록하고 "✅(완료)"로 바꾼다. "사용한 항목
    # 숨기기"가 켜져 있을 때만 그 항목이 목록에서 사라져야 하므로
    # 예외적으로 전체 새로고침을 쓴다.
    def _kin_mark_row_in_progress(self, tree, iid):
        """복사 직후: 이미 완료(✅)된 행은 그대로 두고, 아직 미완료인
        행만 "📋(진행중)"으로 표시한다. 트리를 다시 그리지 않으므로
        선택·스크롤 위치가 그대로 유지된다."""
        if tree is None or iid is None:
            return
        try:
            if tree.set(iid, "used") != "✅":
                tree.set(iid, "used", "📋")
        except Exception:
            pass

    def _kin_mark_row_used(self, tree, iid, hide_used_var, refresh_fn, used=True):
        """저장(또는 사용여부 토글) 완료 시: usage 파일 반영은 호출부에서
        이미 끝냈다고 가정하고, 화면 표시만 갱신한다.
        - "사용한 항목 숨기기"가 켜져 있으면 완료된 항목은 목록에서
          사라져야 하므로 전체 새로고침(refresh_fn)을 쓴다.
        - 꺼져 있으면 트리를 다시 그리지 않고 그 행의 "사용" 셀만
          바꿔서 선택·포커스를 유지한다."""
        if hide_used_var is not None:
            try:
                if hide_used_var.get():
                    refresh_fn()
                    return
            except Exception:
                pass
        if tree is not None and iid is not None:
            try:
                tree.set(iid, "used", "✅" if used else "")
                return
            except Exception:
                pass
        refresh_fn()

    # [Ver7.08 추가] 0-1단계: 사전 필터링(질문 선별) 탭
    # 자동생성_{주제}.txt(0단계에서 수집만 해둔 원문)를 사전 필터링
    # 프롬프트와 함께 웹 AI에 보내 적합성 심사 → 통과된 질문만
    # 질문DB.json에 추가 → 원본 수집 파일은 사용 후 비운다.
    # ══════════════════════════════════════════════════════════
    def create_prefilter_tab(self):
        """0-1단계: 질문 상세분석 (가치판단+관련질문확장+키워드전략+리서치브리프)
        [Ver7.10 변경] 기존 "사전 필터링"(배치 전체를 퍼플렉시티+클로드로 교차검증
        하던 방식)을 완전히 대체. 새 파이프라인:
        질문DB → 여기(0-1) → 1)퍼플렉시티수집 → (검증단계, 추후 추가) → 4)1차각색 → 5)2차각색
        질문 1건을 골라 도메인별 프롬프트와 함께 웹으로 보내고, 돌아온 상세분석
        결과를 원본 질문과 함께 research_brief_{모델} 폴더에 저장해 1)탭으로 넘긴다.
        좌(질문DB 목록) / 우(붙여넣기·저장) 좌우분할은 1)/4)/5)탭과 동일한 패턴."""
        frame = ttk.Frame(self.notebook, padding="6")
        self.notebook.add(frame, text="2)질문적합분석(클로드)")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        # ── 왼쪽: 질문DB에서 질문 선택 ──
        left = ttk.Frame(paned, padding=(4, 4, 8, 4))
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(6, weight=1)

        ttk.Label(left, text="📋 질문 선택 (질문DB)", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        topic_row = ttk.Frame(left)
        topic_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(topic_row, text="주제:").pack(side=tk.LEFT, padx=(0, 5))
        self.detail_topic_var = tk.StringVar(value=topics[0])
        ttk.Combobox(
            topic_row, textvariable=self.detail_topic_var,
            values=topics, state="readonly", width=50, height=11
        ).pack(side=tk.LEFT)

        # [Ver7.10 복원] 0)탭이 쌓아둔 자동생성_{주제}.txt(원본 수집)를
        # 질문DB로 이관하는 통로. 예전 "사전 필터링" 탭이 하던 역할 중
        # "질문DB에 넣는다"는 부분만 남기고, AI 교차검증·선별 판단은
        # 이제 0-1)탭 자체(웹 AI에 보내는 상세분석 프롬프트의 0단계
        # 판정)가 대신하므로 여기서는 단순 이관 + 중복체크만 한다.
        import_row = ttk.Frame(left)
        import_row.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Button(import_row, text="📥 자동생성 파일 → 질문DB 가져오기",
                   command=self._detail_import_collected).pack(side=tk.LEFT)
        self.detail_import_count_var = tk.StringVar(value="")
        ttk.Label(import_row, textvariable=self.detail_import_count_var,
                  foreground="gray").pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(left, text="⚙️ 질문 상세분석 프롬프트 설정",
                   command=self.open_kin_detail_prompt_settings).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        self.detail_hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_detail_picker', False))
        ttk.Checkbutton(left, text="사용한 질문 숨기기", variable=self.detail_hide_used_var).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # [Ver7.10 추가] 날짜 필터(정확일치) + 총 개수 표시
        detail_filter_row = ttk.Frame(left)
        detail_filter_row.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(detail_filter_row, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.detail_date_var = tk.StringVar()
        detail_date_entry = ttk.Entry(detail_filter_row, textvariable=self.detail_date_var, width=11)
        detail_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        detail_date_entry.bind("<Return>", lambda e: self._detail_refresh_list())
        ttk.Button(detail_filter_row, text="오늘",
                   command=lambda: (self.detail_date_var.set(__import__('datetime').datetime.now().strftime("%Y-%m-%d")), self._detail_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(detail_filter_row, text="↺", width=3,
                   command=lambda: (self.detail_date_var.set(""), self._detail_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 8))
        self.detail_count_var = tk.StringVar(value="")
        ttk.Label(detail_filter_row, textvariable=self.detail_count_var, foreground="navy").pack(side=tk.LEFT)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("used", "title", "date")
        self.detail_list_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        self.detail_list_tree.heading("used", text="사용")
        self.detail_list_tree.heading("title", text="질문 제목")
        self.detail_list_tree.heading("date", text="저장일")
        self.detail_list_tree.column("used", width=40, anchor=tk.CENTER)
        self.detail_list_tree.column("title", width=320)
        self.detail_list_tree.column("date", width=80, anchor=tk.CENTER)
        self.detail_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.detail_list_tree.yview)
        self.detail_list_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.detail_list_tree.bind("<Double-1>", lambda e: self._detail_copy_selected())

        self._detail_list_cache = {'records': []}
        self._detail_selected_item = None

        list_btn_frame = ttk.Frame(left)
        list_btn_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame, text="📋 클로드 분석 프롬프트 + 질문 복사",
                   command=self._detail_copy_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="클로드 분석 프롬프트만 복사",
                   command=self._detail_copy_prompt_only).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="질문만 복사",
                   command=self._detail_copy_question_only).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame2 = ttk.Frame(left)
        list_btn_frame2.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame2, text="사용여부 토글",
                   command=self._detail_toggle_used).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🔄 새로고침",
                   command=self._detail_refresh_list).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🗑️ 선택 질문 삭제",
                   command=self._detail_delete_selected).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(left, text="더블클릭 = 프롬프트+질문 복사 → 웹 AI에 붙여넣기\n"
                              "다중선택 가능 (Ctrl+클릭 또는 Shift+클릭) → 삭제도 여러 개 한번에 가능",
                  justify=tk.LEFT, foreground="blue", wraplength=430).grid(
            row=9, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # [Ver7.77 추가] 사용자 요청: 목록엔 제목만 보여서, 지울지 말지
        # 판단하려면 매번 "질문만 복사" 눌러 다른 곳에 붙여넣어 봐야
        # 확인할 수 있었음. 행을 선택(클릭)하면 저장된 질문 원문(제목+
        # 본문)을 바로 아래에 보여주도록 함 - 삭제 전 검토용, 복사/저장
        # 동작에는 관여하지 않는 순수 조회 전용.
        ttk.Label(left, text="📄 선택한 질문 내용 미리보기:", font=("", 9, "bold")).grid(
            row=10, column=0, columnspan=2, sticky=tk.W, pady=(8, 2))
        preview_frame = ttk.Frame(left)
        preview_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E))
        preview_frame.columnconfigure(0, weight=1)
        self.detail_preview_text = scrolledtext.ScrolledText(
            preview_frame, height=9, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.detail_list_tree.bind("<<TreeviewSelect>>", lambda e: self._detail_update_preview())

        # ── 오른쪽: 상세분석 결과 붙여넣기 & 저장 ──
        right = ttk.Frame(paned, padding=(8, 4, 4, 4))
        paned.add(right, weight=3)
        right.columnconfigure(1, weight=1)

        guide = (
            "사용법:  1) 왼쪽에서 질문 골라 복사→웹 AI에 붙여넣기  2) 응답(가치판단+관련질문확장+키워드전략+리서치브리프)을 아래에 붙여넣기  3) [저장] 클릭\n"
            "저장 경로: 기본폴더/주제/오늘날짜/research_brief_[모델]/제목.md  (여기 저장된 결과는 1)탭 왼쪽 목록에 그대로 나타납니다)"
        )
        ttk.Label(right, text=guide, justify=tk.LEFT, foreground="blue", wraplength=560).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
        )

        ttk.Label(right, text="저장 모델:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.detail_model_var = tk.StringVar(value="Claude")
        model_frame = ttk.Frame(right)
        model_frame.grid(row=1, column=1, sticky=tk.W, pady=4)
        for m in ["Claude", "GPT", "Gemini"]:
            ttk.Radiobutton(
                model_frame, text="research_brief_{}".format(m),
                variable=self.detail_model_var, value=m
            ).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(right, text="작업 대상\n질문:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=4)
        self.detail_target_var = tk.StringVar(value="(왼쪽에서 질문을 복사하면 여기에 표시됩니다)")
        ttk.Label(right, textvariable=self.detail_target_var, foreground="darkgreen",
                  wraplength=480, justify=tk.LEFT).grid(row=2, column=1, sticky=tk.W, pady=4)

        ttk.Label(right, text="분석 결과\n붙여넣기:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(6, 0))
        self.detail_text = scrolledtext.ScrolledText(right, height=24, wrap=tk.WORD)
        self.detail_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(6, 0))
        self.detail_text.bind("<KeyRelease>", lambda e: self._detail_update_char_count())
        self.detail_text.bind("<<Paste>>", lambda e: self.root.after(10, self._detail_update_char_count))

        self.detail_char_count_var = tk.StringVar(value="한글 글자수: 0자")
        ttk.Label(right, textvariable=self.detail_char_count_var,
                  foreground="darkred", font=("", 9, "bold")).grid(
            row=4, column=1, sticky=tk.W, pady=(2, 0))

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(8, 0), sticky=tk.W)
        self.detail_save_btn = ttk.Button(btn_frame, text="저장",
                   command=self._detail_save_result)
        self.detail_save_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="내용 지우기",
                   command=self._detail_clear).pack(side=tk.LEFT)

        self.detail_topic_var.trace_add("write", lambda *_: self._detail_refresh_list())
        self.detail_hide_used_var.trace_add("write", lambda *_: self._detail_refresh_list())
        self.detail_hide_used_var.trace_add(
            "write", lambda *_: self.save_kin_ui_setting('hide_used_detail_picker', self.detail_hide_used_var.get()))
        self._detail_refresh_list()

    # ── [Ver7.10 추가] 0-1)탭 왼쪽 질문 목록(좌우분할)용 헬퍼 ──
    def _detail_get_usage_path(self, topic):
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        return os.path.join(base_folder, topic, "질문_상세분석_사용여부.json")

    def _detail_load_usage(self, topic):
        return load_json_db(self._detail_get_usage_path(topic))

    def _detail_save_usage(self, topic, usage_list):
        save_json_db(self._detail_get_usage_path(topic), usage_list)

    def _detail_import_collected(self):
        """[Ver7.10 복원] 0)탭이 자동생성_{주제}.txt에 누적해둔 원본 수집
        질문을 질문DB로 이관한다. 예전 "사전 필터링" 탭이 하던 이관+
        중복체크 역할만 남기고, AI 판단(적합성 심사)은 이제 이 값 자체가
        새 0-1)탭 프롬프트의 0단계가 대신하므로 여기서는 하지 않는다.
        형태 B(Q&A 클러스터)도 원문 그대로(절단 없이) 넘어간다."""
        topic = self.detail_topic_var.get()
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        filename = f"자동생성_{topic}.txt"
        file_path = os.path.join(base_folder, filename)

        if not os.path.exists(file_path):
            messagebox.showinfo("알림", f"수집된 질문 파일이 없습니다:\n{file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return

        if not raw.strip():
            messagebox.showinfo("알림", "가져올 새 질문이 없습니다. (파일이 비어 있음)")
            return

        questions = parse_collected_kin_questions(raw)
        if not questions:
            messagebox.showwarning("알림", "질문을 파싱하지 못했습니다. 파일 형식을 확인하세요.")
            return

        question_db_path = get_question_db_path(base_folder, topic)
        os.makedirs(get_topic_folder_path(base_folder, topic), exist_ok=True)
        question_records = load_json_db(question_db_path)
        # [Ver7.75 추가] 질문DB끼리의 중복체크에 더해, "이미 포스팅까지
        # 끝낸 주제"인지도 이 시점에 참고용으로 미리 확인한다(질문/완성글은
        # 텍스트 종류가 달라 정식체크보다 정확도가 낮으므로 차단은 하지
        # 않고 경고만 표시 - check_question_vs_posting_duplicate 주석 참고).
        posting_db_path = get_posting_db_path(base_folder, topic)
        posting_records = load_json_db(posting_db_path)

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        added = 0
        skipped_dup = []
        posting_warns = []
        for q in questions:
            core = extract_question_core(q['title'], q['body'])
            dup_results = check_question_duplicate(core, question_records, danger=70)
            if dup_results:
                skipped_dup.append((q['title'], dup_results[0]))
                continue
            posting_hits = check_question_vs_posting_duplicate(core, posting_records, danger=70)
            if posting_hits:
                posting_warns.append((q['title'], posting_hits[0]))
            core["date"] = today
            question_records.append(core)
            added += 1

        save_json_db(question_db_path, question_records)

        # 이관 끝난 원본 파일은 비운다 (0)탭이 다음에 또 누적해서 쓸 수 있게)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('')

        self.log(f"📥 질문DB 가져오기 완료 [{topic}]: {len(questions)}건 중 추가 {added}건 / 중복 제외 {len(skipped_dup)}건")
        if skipped_dup:
            for title, dup in skipped_dup:
                self.log(f"   ⛔ 중복 제외({dup['rate']}%): {title}")
        if posting_warns:
            self.log(f"   💡 이미 포스팅된 것과 비슷해 보이는 질문 {len(posting_warns)}건(참고용, 질문DB에는 그대로 추가됨):")
            for title, hit in posting_warns:
                self.log(f"      ⚠️ {title} ↔ 기존 포스팅 '{hit['title']}' ({hit['rate']}%)")

        self.detail_import_count_var.set(f"방금 {added}건 추가 (중복 제외 {len(skipped_dup)}건)")
        self._detail_refresh_list()

        posting_warn_note = (
            f"\n\n💡 참고: 이미 포스팅된 글과 비슷해 보이는 질문이 {len(posting_warns)}건 있습니다 "
            f"(질문DB에는 그대로 추가했습니다 - 아래 목록, 자세한 내용은 로그 확인).\n" +
            "\n".join(f"  • {title} ↔ 기존 '{hit['title']}' ({hit['rate']}%)" for title, hit in posting_warns[:10]) +
            (f"\n  … 외 {len(posting_warns) - 10}건 더" if len(posting_warns) > 10 else "")
        ) if posting_warns else ""

        messagebox.showinfo(
            "가져오기 완료",
            f"질문DB에 {added}건 추가했습니다. (중복 제외 {len(skipped_dup)}건)\n\n"
            f"원본 수집 파일({filename})을 비웠습니다."
            f"{posting_warn_note}"
        )

    def _detail_refresh_list(self):
        if not hasattr(self, 'detail_list_tree'):
            return
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        topic = self.detail_topic_var.get()
        self.detail_list_tree.delete(*self.detail_list_tree.get_children())
        db_path = get_question_db_path(base_folder, topic)
        records = load_json_db(db_path)
        self._detail_list_cache['records'] = records

        usage_raw = self._detail_load_usage(topic)
        used_titles = set(usage_raw) if isinstance(usage_raw, list) else set()

        # [Ver7.10 수정] "사용됨"을 복사 버튼 클릭 여부(usage_raw)만으로
        # 판단하면, "질문만 복사"로 작업했거나 다른 경로로 작업한 경우
        # 실제로 저장까지 끝냈어도 표시가 안 되는 문제가 있었다. 그래서
        # research_brief 폴더에 실제 저장된 파일이 있는지도 함께 확인해
        # 완료 여부를 더 정확히 잡는다(둘 중 하나라도 맞으면 사용됨).
        saved_titles = {item["title"] for item in self._scan_research_brief_items(base_folder, topic)}

        date_filter = self.detail_date_var.get().strip() if hasattr(self, 'detail_date_var') else ""
        shown = 0
        for i, r in enumerate(records):
            title = r.get("title", "")
            used = title in used_titles or self.create_safe_filename(title) in saved_titles
            if self.detail_hide_used_var.get() and used:
                continue
            if date_filter and r.get("date", "") != date_filter:
                continue
            self.detail_list_tree.insert("", tk.END, iid=str(i), values=(
                "✅" if used else "", title, r.get("date", "")
            ))
            shown += 1

        if hasattr(self, 'detail_count_var'):
            total = len(records)
            if date_filter:
                self.detail_count_var.set(f"검색결과 {shown}개 / 전체 {total}개")
            else:
                self.detail_count_var.set(f"총 {total}개")

        # [Ver7.77 추가] 목록이 다시 그려지면 선택이 풀리므로, 미리보기도
        # 같이 비워서 방금까지 보이던 질문이 목록과 안 맞는 채로 남아있지
        # 않게 한다.
        self._detail_update_preview()

    def _detail_update_preview(self):
        """[Ver7.77 신규] 질문 목록에서 행을 클릭(선택)할 때마다 그 질문의
        저장된 원문(제목+본문)을 아래 미리보기 칸에 그대로 보여준다.
        읽기전용(state=DISABLED)이라 여기서 직접 수정은 안 되고, 삭제할지
        말지 판단하기 위한 조회 전용이다. 여러 개를 동시에 선택했을 때는
        어느 걸 보여줘야 할지 애매하므로, 그 경우 "N개 선택됨" 안내만
        띄운다(삭제 자체는 다중선택으로도 그대로 가능, 미리보기만 1개
        선택일 때 표시)."""
        if not hasattr(self, 'detail_preview_text'):
            return
        sel = self.detail_list_tree.selection()
        self.detail_preview_text.configure(state=tk.NORMAL)
        self.detail_preview_text.delete("1.0", tk.END)
        if not sel:
            self.detail_preview_text.configure(state=tk.DISABLED)
            return
        if len(sel) > 1:
            self.detail_preview_text.insert(
                tk.END, f"({len(sel)}개 항목이 선택되어 있습니다 - 미리보기는 1개만 선택했을 때 표시됩니다)")
            self.detail_preview_text.configure(state=tk.DISABLED)
            return
        idx = int(sel[0])
        records = self._detail_list_cache.get('records', [])
        if not (0 <= idx < len(records)):
            self.detail_preview_text.configure(state=tk.DISABLED)
            return
        r = records[idx]
        title = r.get("title", "")
        body = r.get("body", "")
        self.detail_preview_text.insert(tk.END, f"[제목]\n{title}\n\n[내용]\n{body}")
        self.detail_preview_text.configure(state=tk.DISABLED)

    def _detail_copy_selected(self):
        sel = self.detail_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 질문을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        record = self._detail_list_cache['records'][idx]
        topic = self.detail_topic_var.get()

        prompts = self.load_kin_detail_prompts()
        prompt_filename = prompts.get(topic, "")
        if not prompt_filename:
            messagebox.showwarning(
                "상세분석 프롬프트 없음",
                f"'{topic}' 주제에 등록된 질문 상세분석 프롬프트가 없습니다.\n"
                f"'⚙️ 질문 상세분석 프롬프트 설정'에서 먼저 등록하세요."
            )
            return

        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
            return

        content = (
            f"{prompt_text}\n\n"
            f"───────────────────\n"
            f"[지식인 질문]\n"
            f"제목: {record.get('title', '')}\n"
            f"본문: {record.get('body', '')}\n"
        )

        self.root.clipboard_clear()
        self.root.clipboard_append(content)

        # 작업 대상 질문으로 기억해둔다 (저장 시 파일명·원본질문 삽입에 사용)
        self._detail_selected_item = {
            'title': record.get('title', ''),
            'body': record.get('body', ''),
        }
        self.detail_target_var.set(record.get('title', ''))

        # [Ver7.17 수정] 예전엔 여기서 usage(사용여부)를 바로 True로 기록해
        # 붙여넣기·저장을 안 해도 ✅가 떴다. 이제 "복사함"과 "저장 완료함"을
        # 구분한다 — 진짜 완료 표시(✅)는 _detail_save_result()가 실제로
        # research_brief 파일을 저장했을 때만 남긴다(saved_titles 스캔).
        # 여기서는 목록을 통째로 다시 그리지 않고 그 행만 "📋(진행중)"으로
        # 표시해 선택/포커스를 그대로 유지한다.
        self._kin_mark_row_in_progress(self.detail_list_tree, sel[0])

        self.log(f"📋 상세분석용 질문 복사 완료 (프롬프트: {prompt_filename}): {record.get('title','')}")

    def _detail_copy_prompt_only(self):
        """[Ver7.84 신규] 자료(질문) 선택 없이, 현재 선택된 주제에 매핑된
        질문 상세분석 프롬프트 텍스트만 클립보드에 복사한다. 7)1차각색/
        8)2차각색의 "프롬프트만 복사"와 동일한 컨셉(같은 웹 AI 채팅창에서
        프롬프트는 한 번만 보내고 이후 "질문만 복사"로 이어 붙이는 절약
        워크플로우 지원)을 이 탭에도 맞춰 추가."""
        topic = self.detail_topic_var.get()
        prompts = self.load_kin_detail_prompts()
        prompt_filename = prompts.get(topic, "")
        if not prompt_filename:
            messagebox.showwarning(
                "상세분석 프롬프트 없음",
                f"'{topic}' 주제에 등록된 질문 상세분석 프롬프트가 없습니다.\n"
                f"'⚙️ 질문 상세분석 프롬프트 설정'에서 먼저 등록하세요."
            )
            return
        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_PROMPT_CONTINUITY_NOTICE + prompt_text)
        self.log(f"📋 상세분석 프롬프트만 복사: {prompt_filename} ({topic})")
        messagebox.showinfo("복사 완료", "프롬프트만 클립보드에 복사되었습니다.")

    def _detail_copy_question_only(self):
        sel = self.detail_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 질문을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        record = self._detail_list_cache['records'][idx]
        content = f"제목: {record.get('title', '')}\n본문: {record.get('body', '')}\n"
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        # [Ver7.17 추가] "질문만 복사"만 쓰더라도 저장이 정상 동작하도록
        # 작업 대상을 함께 기억해둔다(안 그러면 나중에 저장할 때 "작업
        # 대상 질문이 없습니다" 오류가 난다).
        self._detail_selected_item = {
            'title': record.get('title', ''),
            'body': record.get('body', ''),
        }
        self.detail_target_var.set(record.get('title', ''))
        # "질문만 복사"도 실제로 작업을 시작한 것이므로
        # 그 행을 "📋(진행중)"으로 표시한다(선택만으로는 표시하지 않음).
        self._kin_mark_row_in_progress(self.detail_list_tree, sel[0])
        self.log(f"📋 질문만 복사: {record.get('title','')}")

    def _detail_toggle_used(self):
        sel = self.detail_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        record = self._detail_list_cache['records'][idx]
        topic = self.detail_topic_var.get()
        title = record.get("title", "")

        usage_raw = self._detail_load_usage(topic)
        used_titles = list(usage_raw) if isinstance(usage_raw, list) else []
        if title in used_titles:
            used_titles.remove(title)
        else:
            used_titles.append(title)
        self._detail_save_usage(topic, used_titles)
        self._detail_refresh_list()

    # [Ver7.10 추가] 질문DB 항목 삭제 (+ 연쇄삭제)
    # 같은 질문을 여러 번 작성해서 DB가 꼬였을 때 정리하는 용도.
    # research_brief 파일명은 원본 질문 제목을 그대로 쓰기 때문에(=
    # create_safe_filename(title)) 100% 정확히 연결되는 범위에서만
    # 같이 지운다. 그 뒤 단계(퍼플렉시티 원고·검증본·포스팅)는 AI가 새로
    # 지어낸 제목을 쓰기 때문에 프로그램적으로 원본 질문과 확실하게
    # 연결할 방법이 없어 자동 연쇄삭제 대상에서 제외한다(잘못 지우는
    # 사고 방지). 그 단계는 각 탭의 "사용여부 토글" 또는 11)포스팅
    # 이력관리 탭에서 별도로 정리하면 된다.
    def _detail_delete_selected(self):
        sel = self.detail_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "삭제할 질문을 먼저 선택하세요.")
            return

        topic = self.detail_topic_var.get()
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        indices = sorted((int(i) for i in sel), reverse=True)
        records = self._detail_list_cache['records']
        targets = [records[i] for i in indices if 0 <= i < len(records)]

        # 삭제 대상마다 실제로 딸려있는 research_brief 파일도 미리 찾아서
        # 경고창에 몇 건이나 같이 지워지는지 보여준다.
        brief_items = self._scan_research_brief_items(base_folder, topic)
        preview_lines = []
        files_to_delete = []
        for r in targets:
            title = r.get("title", "")
            safe = self.create_safe_filename(title)
            matched = [b for b in brief_items if b["title"] == safe]
            files_to_delete.extend(matched)
            tag = f" (+브리프 {len(matched)}건)" if matched else ""
            preview_lines.append(f"  • {title}{tag}")

        preview = "\n".join(preview_lines[:10])
        if len(preview_lines) > 10:
            preview += f"\n  … 외 {len(preview_lines) - 10}건 더"

        if not messagebox.askyesno(
                "⚠️ 질문 삭제 확인 (되돌릴 수 없음)",
                f"아래 {len(targets)}개 질문을 질문DB에서 영구 삭제합니다.\n"
                f"같이 표시된 브리프 파일도 함께 삭제됩니다(있는 경우).\n\n"
                f"{preview}\n\n"
                f"※ 이후 단계(퍼플렉시티 원고·검증본·포스팅)는 제목이 달라져서\n"
                f"자동으로 같이 안 지워집니다 - 필요하면 해당 탭에서 따로 정리하세요.\n\n"
                f"정말 삭제하시겠습니까?",
                icon="warning"):
            return

        # 1) 질문DB에서 제거
        titles_to_remove = {r.get("title", "") for r in targets}
        db_path = get_question_db_path(base_folder, topic)
        all_records = load_json_db(db_path)
        remaining = [r for r in all_records if r.get("title", "") not in titles_to_remove]
        save_json_db(db_path, remaining)

        # 2) 딸린 research_brief 파일 삭제
        deleted_files = 0
        for f in files_to_delete:
            try:
                os.remove(f["file_path"])
                deleted_files += 1
            except Exception as e:
                self.log(f"⚠️ 브리프 파일 삭제 실패: {f['file_path']} ({e})")

        # 3) 사용여부 기록 정리
        usage_raw = self._detail_load_usage(topic)
        used_titles = [t for t in (usage_raw if isinstance(usage_raw, list) else []) if t not in titles_to_remove]
        self._detail_save_usage(topic, used_titles)

        self.log(f"🗑️ 질문DB 삭제 완료: {len(targets)}개 ({topic}) + 브리프 파일 {deleted_files}개")
        self._detail_refresh_list()

    def _detail_update_char_count(self):
        text = self.detail_text.get("1.0", tk.END)
        korean = len(re.findall(r'[\uAC00-\uD7A3]', text))
        english = len(re.findall(r'[a-zA-Z0-9]', text))
        punct = len(re.findall(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', text))
        spaces = len(re.findall(r'[ \t]', text))
        total_excl = int(korean + english * 0.5 + punct)
        total_incl = int(korean + english * 0.5 + punct + spaces)
        self.detail_char_count_var.set(
            "한글 기준 글자수 │ 공백제외: {:,}자 │ 공백포함: {:,}자".format(total_excl, total_incl)
        )

    # [Ver7.10 추가] 웹 클로드 화면에서 드래그로 복사할 때 하단 UI 안내문구
    # ("Claude는 AI이며 실수할 수 있습니다...")가 문장 중간에서 끊긴 채로
    # 같이 딸려오는 경우가 있다. 저장 직전에 이런 꼬리표를 잘라낸다.
    def _strip_ai_ui_chrome(self, text):
        text = re.sub(r'\n*Claude는\s*AI이며\s*실수할\s*수\s*있.*$', '', text, flags=re.S).rstrip()
        # [Ver7.17 추가] 복사 편의를 위해 AI에게 "전체를 코드블럭 하나로
        # 감싸서 출력"하도록 요청하는 프롬프트를 쓰는 경우 대비. 응답 전체가
        # ```...``` 로 통째로 감싸져 있으면 바깥쪽 펜스만 벗겨내고 저장한다
        # (안쪽에 중첩된 다른 코드블럭·백틱은 건드리지 않음). 2)/4)/7)/8)탭
        # 저장 함수가 전부 이 함수를 거치므로 한 곳만 고치면 공통 적용된다.
        m = re.match(r'^```[^\n]*\n(.*)\n```\s*$', text, flags=re.S)
        if m:
            text = m.group(1).strip()

        # [Ver8.23 추가] GPT가 마크다운 코드블럭으로 응답을 감쌀 때, 위
        # 정규식이 잡아내지 못하는 형태(닫는 ``` 뒤에 ":::" 같은 부가 기호나
        # 빈 줄이 더 붙어 통째로-한-덩어리 매칭에 실패하는 경우)로 앞뒤에
        # 군더더기 줄이 남는 사례가 실측됨. 실제 저장 대상은 "# 제목"으로
        # 시작해 마지막 해시태그 줄로 끝나는 본문 하나뿐이므로, 그 앞뒤에
        # 남은 코드펜스(```)·구분선(--- 3개 이상)·(:::)·빈 줄을 본문에
        # 닿을 때까지 반복적으로 걷어낸다. 줄 전체가 이 패턴에만 정확히
        # 일치할 때만 지우므로(예: 표 구분선 "|---|---|"는 매칭 안 됨),
        # 본문 중간의 정상적인 --- 구분선은 건드리지 않는다.
        junk_line_pattern = re.compile(r'^(?:`{3,}[a-zA-Z]*|:{3,}|-{3,})\s*$')
        lines = text.split('\n')
        while lines and (lines[0].strip() == '' or junk_line_pattern.match(lines[0].strip())):
            lines.pop(0)
        while lines and (lines[-1].strip() == '' or junk_line_pattern.match(lines[-1].strip())):
            lines.pop()
        text = '\n'.join(lines).strip()

        # [Ver8.30 추가] 챗GPT 웹에서 싱크모드(실시간 검색)가 실수로 켜진
        # 채 최종 각색을 돌리면 인용·각주 마커가 본문에 섞여 나오는 사고가
        # 실제로 있었다(클로드는 이런 마커를 남기지 않음). 이 단계는 원래
        # 검색이 필요 없지만(원고가 이미 검증된 상태), 프롬프트 쪽에 금지
        # 문구를 넣어도(1차+2차 각색 프롬프트 전체) 실수로 켜져 있을 경우를
        # 대비한 안전망을 저장 시점에도 걸어둔다. 이 함수를 거치는 모든
        # 저장(0-1/1/2-1/7/8탭 - 1차·2차 각색 포함)에 공통 적용된다.
        text = re.sub(r':contentReference\[oaicite:\d+\]\{index=\d+\}', '', text)
        text = re.sub(r'【[^【】]*†[^【】]*】', '', text)  # 【...†...】 인용 마커(†가 있을 때만 - 일반 【】 강조는 보존)
        text = re.sub(r'\^\[[^\]]*\]', '', text)          # ^[...] 각주 문법
        text = re.sub(r'\bturn\d+\w*\b', '', text)        # turn0search... 류 내부 도구 호출 흔적
        # [2026-09-27 추가] extract_markdown_content()가 잡던 "[web:3]"류
        # 라벨형 각주가 이 함수에는 빠져 있어, 퍼플렉시티 원문에 섞인
        # "[웹:106]" 같은 한글 라벨 각주가 1차·2차 각색 저장 시점까지
        # 그대로 살아남는 문제가 있었다(사용자 실측 확인). 라벨을 "web"
        # 고정 문자열이 아니라 "대괄호 안, 콜론 앞의 임의 짧은 텍스트"로
        # 일반화해 "[web:3]"·"[웹:106]" 등을 모두 잡는다.
        text = re.sub(r'\[[^\[\]\n:]{1,12}:\d+\]', '', text)  # [web:3], [웹:106] 같은 라벨형 각주
        text = re.sub(r'\[\d+\]', '', text)               # [1], [12] 같은 각주 번호
        # [Ver9.07 추가] 퍼플렉시티 등 웹검색 결과에 붙는 마크다운 하이퍼링크
        # 각주 - "[law.go](https://www.law.go.kr/...)"처럼 대괄호 표시텍스트
        # 바로 뒤에 괄호 URL이 붙는 형태. 위의 [1]/[12] 정규식은 숫자만
        # 잡으므로 이 형태는 그대로 통과해 저장되고 있었다(사용자 실측 확인).
        # 표시텍스트만 남기면 "...연결돼요. law.go"처럼 문장 끝에 의미 없는
        # 사이트명만 남아 더 어색해지므로, 링크 전체(대괄호+괄호)를 통째로
        # 제거한다.
        text = re.sub(r'\[[^\[\]]+\]\(https?://(?:[^\s()]|\([^\s()]*\))+\)', '', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)             # 마커 제거 후 생긴 연속 공백 정리

        return text

    def _detail_save_result(self):
        """상세분석 결과를 원본 질문과 함께 research_brief_{모델} 폴더에 저장.
        [Ver7.10] 1)탭이 이 파일을 그대로 스캔해서 다음 단계로 넘겨받는다."""
        text = self._strip_ai_ui_chrome(self.detail_text.get("1.0", tk.END).strip())
        if not text:
            messagebox.showwarning("저장 오류", "저장할 분석 결과가 없습니다.")
            return
        item = self._detail_selected_item
        if not item or not item.get('title'):
            messagebox.showwarning(
                "저장 오류",
                "작업 대상 질문이 없습니다.\n"
                "왼쪽 목록에서 질문을 먼저 '복사'(또는 더블클릭)해서 대상으로 지정하세요."
            )
            return

        # [Ver7.10 추가] 상세분석 프롬프트는 0단계에서 "보류" 판정이면 리서치
        # 브리프 없이 거기서 끝난다. 보류인 채로 저장하면 1)탭에 무의미한
        # 항목이 올라가니, 저장 전에 한 번 확인만 받는다(막지는 않음).
        if re.search(r'판정\s*:\s*보류(?!\()', text):
            if not messagebox.askyesno(
                "보류 판정 확인",
                "이 분석 결과는 '보류' 판정입니다 (포스팅 부적합/가치 없음).\n"
                "리서치 브리프가 없을 수 있는데, 그래도 저장하시겠습니까?\n\n"
                "저장하면 1)탭 목록에도 그대로 나타납니다."
            ):
                return

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        topic = self.detail_topic_var.get()
        model = self.detail_model_var.get()
        base = self.base_folder_var.get().strip() or self.base_folder
        save_dir = os.path.join(base, topic, today, "research_brief_{}".format(model))
        os.makedirs(save_dir, exist_ok=True)

        filename = "{}.md".format(self.create_safe_filename(item['title']))
        save_path = os.path.join(save_dir, filename)

        if os.path.exists(save_path):
            if not messagebox.askyesno("덮어쓰기 확인",
                    "동일한 파일이 이미 존재합니다.\n\n{}\n\n덮어쓰시겠습니까?".format(filename)):
                return

        content = (
            f"# {item['title']}\n\n"
            f"## 원본 질문\n"
            f"{item['body']}\n\n"
            f"## 상세분석 결과\n"
            f"{text}\n"
        )

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"✅ 질문 상세분석 저장: {filename}")
            self.log(f"   -> {save_dir}")

            # [Ver7.10 추가] 저장 시점에도 사용여부를 명시적으로 기록해둔다
            # (복사 버튼을 안 눌렀거나 다른 경로로 작업했어도 저장 시 확실히 반영).
            usage_raw = self._detail_load_usage(topic)
            used_titles = list(usage_raw) if isinstance(usage_raw, list) else []
            if item['title'] not in used_titles:
                used_titles.append(item['title'])
            self._detail_save_usage(topic, used_titles)

            self._detail_clear()
            self._detail_refresh_list()
        except Exception as e:
            self.log(f"❌ 상세분석 저장 실패: {e}")
            messagebox.showerror("저장 실패", f"파일 저장 중 오류 발생:\n{e}")

    def _detail_clear(self):
        self.detail_text.delete("1.0", tk.END)
        self.detail_char_count_var.set("한글 글자수: 0자")
        self.detail_target_var.set("(왼쪽에서 질문을 복사하면 여기에 표시됩니다)")
        self._detail_selected_item = None


    def _prefilter_load_collected(self):
        """자동생성_{주제}.txt(0단계 수집 원문)를 불러와 개별 질문으로 분리, 미리보기에 표시"""
        try:
            topic = self.prefilter_topic_var.get()
            base_folder = self.base_folder_var.get().strip() or self.base_folder
            filename = f"자동생성_{topic}.txt"
            file_path = os.path.join(base_folder, filename)

            if not os.path.exists(file_path):
                messagebox.showwarning("알림", f"수집된 질문 파일이 없습니다:\n{file_path}")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                raw = f.read()

            if not raw.strip():
                messagebox.showinfo("알림", "수집된 질문이 없습니다. (파일이 비어 있음)")
                return

            questions = parse_collected_kin_questions(raw)
            if not questions:
                messagebox.showwarning("알림", "질문을 파싱하지 못했습니다. 파일 형식을 확인하세요.")
                return

            self._prefilter_loaded_questions = questions
            self._prefilter_loaded_path = file_path
            self.prefilter_loaded_count_var.set(f"불러온 질문: {len(questions)}건")

            preview_lines = [f"[질문 {i}] {q['title']}" for i, q in enumerate(questions, 1)]
            self.prefilter_preview_text.config(state=tk.NORMAL)
            self.prefilter_preview_text.delete("1.0", tk.END)
            self.prefilter_preview_text.insert("1.0", "\n".join(preview_lines))
            self.prefilter_preview_text.config(state=tk.DISABLED)

            self.log(f"📂 사전 필터링용 질문 불러오기 완료 [{topic}]: {len(questions)}건 ({filename})")

        except Exception as e:
            self.log(f"❌ 수집된 질문 불러오기 오류: {e}")
            messagebox.showerror("오류", f"불러오기 중 오류 발생:\n{e}")

    def _prefilter_copy_prompt(self):
        """사전 필터링 프롬프트({questions_batch} 채운 상태)를 클립보드에 복사"""
        try:
            topic = self.prefilter_topic_var.get()
            loaded = getattr(self, '_prefilter_loaded_questions', [])
            if not loaded:
                messagebox.showwarning("알림", "먼저 '📂 수집된 질문 불러오기'를 실행하세요.")
                return

            prompts = self.load_kin_prefilter_prompts()
            prompt_filename = prompts.get(topic, "")
            if not prompt_filename:
                messagebox.showwarning(
                    "사전 필터링 프롬프트 없음",
                    f"'{topic}' 주제에 등록된 사전 필터링 프롬프트가 없습니다.\n"
                    f"'⚙️ 사전 필터링 프롬프트 설정'에서 먼저 등록하세요."
                )
                return

            prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
            prompt_path = os.path.join(prompt_folder, prompt_filename)
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
            except Exception as e:
                messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
                return

            batch_text = "\n\n".join(
                f"[질문 {i}]\n제목: {q['title']}\n내용: {q['body']}"
                for i, q in enumerate(loaded, 1)
            )
            final_prompt = prompt_text.replace("{questions_batch}", batch_text)

            self.root.clipboard_clear()
            self.root.clipboard_append(final_prompt)

            self.log(f"📋 사전 필터링 프롬프트 복사 완료 [{topic}]: 질문 {len(loaded)}건 (프롬프트: {prompt_filename})")
            messagebox.showinfo("복사 완료", f"프롬프트 + 질문 {len(loaded)}건이 클립보드에 복사되었습니다.\n웹 AI에 붙여넣으세요.")

        except Exception as e:
            self.log(f"❌ 프롬프트 복사 오류: {e}")
            messagebox.showerror("오류", f"복사 중 오류 발생:\n{e}")

    def _prefilter_claude_final_review(self):
        """퍼플렉시티/클로드 두 결과 박스 내용을 내장된 최종검토 프롬프트에
        채워 넣어 클립보드로 복사한다. 이 텍스트를 웹 클로드에 붙여넣고,
        돌아온 응답을 '③ 최종 병합 결과' 칸에 붙여넣으면 저장할 수 있다."""
        try:
            perp_text = self.prefilter_result_perp_text.get("1.0", tk.END).strip()
            claude_text = self.prefilter_result_claude_text.get("1.0", tk.END).strip()

            if not perp_text or not claude_text:
                messagebox.showwarning(
                    "알림",
                    "퍼플렉시티 결과와 클로드 결과를 먼저 둘 다 붙여넣으세요.\n"
                    "(왼쪽: 퍼플렉시티 결과 / 오른쪽: 클로드 결과)"
                )
                return

            final_prompt = KIN_PREFILTER_FINAL_REVIEW_PROMPT.format(
                perplexity_result=perp_text, claude_result=claude_text
            )

            self.root.clipboard_clear()
            self.root.clipboard_append(final_prompt)

            self.log("🧭 클로드 최종 검토 프롬프트 복사 완료 (퍼플렉시티 결과 + 클로드 결과 포함)")
            messagebox.showinfo(
                "복사 완료",
                "최종 검토 프롬프트가 클립보드에 복사되었습니다.\n"
                "웹 클로드에 붙여넣고, 돌아온 응답을 ③ 최종 병합 결과 칸에 붙여넣은 뒤 저장하세요."
            )

        except Exception as e:
            self.log(f"❌ 클로드 최종 검토 프롬프트 복사 오류: {e}")
            messagebox.showerror("오류", f"복사 중 오류 발생:\n{e}")

    def _prefilter_save_selected_to_db(self):
        """③ 최종 병합 결과(클로드 최종 검토 응답)에서 '리서치 대상 선별 목록'만
        뽑아 질문DB에 추가하고, 사용이 끝난 원본 수집 파일(자동생성_{주제}.txt)은
        내용을 비운다."""
        try:
            topic = self.prefilter_topic_var.get()
            base_folder = self.base_folder_var.get().strip() or self.base_folder

            ai_text = self.prefilter_final_text.get("1.0", tk.END).strip()
            if not ai_text:
                messagebox.showwarning(
                    "알림",
                    "③ 최종 병합 결과가 비어 있습니다.\n"
                    "'🧭 클로드 최종 검토'로 복사한 내용을 웹 클로드에 붙여넣고,\n"
                    "돌아온 응답을 맨 아래 '최종 병합 결과' 칸에 붙여넣으세요."
                )
                return

            loaded = getattr(self, '_prefilter_loaded_questions', [])
            if not loaded:
                messagebox.showwarning("알림", "먼저 '📂 수집된 질문 불러오기'로 원본 질문을 불러오세요.")
                return

            selection = parse_prefilter_selection(ai_text)
            if not selection:
                messagebox.showerror(
                    "파싱 실패",
                    "최종 병합 결과에서 '[SELECTED_START]~[SELECTED_END]' 블록을 찾지 못했습니다.\n"
                    "클로드 최종 검토 응답 전체를 그대로 붙여넣었는지 확인하세요."
                )
                return

            question_db_path = get_question_db_path(base_folder, topic)
            os.makedirs(get_topic_folder_path(base_folder, topic), exist_ok=True)
            question_records = load_json_db(question_db_path)
            # [Ver7.75 추가] _detail_import_collected와 동일한 이유로,
            # 포스팅DB와도 참고용 교차 체크(차단 아님)를 추가한다.
            posting_db_path = get_posting_db_path(base_folder, topic)
            posting_records = load_json_db(posting_db_path)

            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")

            added = 0
            skipped_dup = []
            posting_warns = []
            for num, sentence in selection:
                # 원본 본문(숫자·상세정보)을 같이 확보해두면 중복비교 정확도가 올라간다.
                orig_body = loaded[num - 1]['body'] if 1 <= num <= len(loaded) else ""
                core = extract_question_core(sentence, orig_body or sentence)

                dup_results = check_question_duplicate(core, question_records, danger=70)
                if dup_results:
                    skipped_dup.append((sentence, dup_results[0]))
                    continue

                posting_hits = check_question_vs_posting_duplicate(core, posting_records, danger=70)
                if posting_hits:
                    posting_warns.append((sentence, posting_hits[0]))

                core["date"] = today
                question_records.append(core)
                added += 1

            save_json_db(question_db_path, question_records)

            # 사용 끝난 원본 수집 파일 비우기 (1단계 convert_text와 동일한 방식)
            src_path = getattr(self, '_prefilter_loaded_path', None)
            if src_path and os.path.exists(src_path):
                with open(src_path, 'w', encoding='utf-8') as f:
                    f.write('')

            self.log(
                f"✅ 사전 필터링 완료 [{topic}]: 최종 선별 {len(selection)}건 중 "
                f"질문DB 추가 {added}건 / 중복 제외 {len(skipped_dup)}건"
            )
            if skipped_dup:
                for sentence, dup in skipped_dup:
                    self.log(f"   ⛔ 중복 제외({dup['rate']}%): {sentence}")
            if posting_warns:
                self.log(f"   💡 이미 포스팅된 것과 비슷해 보이는 질문 {len(posting_warns)}건(참고용, 질문DB에는 그대로 추가됨):")
                for sentence, hit in posting_warns:
                    self.log(f"      ⚠️ {sentence} ↔ 기존 포스팅 '{hit['title']}' ({hit['rate']}%)")

            posting_warn_note = (
                f"\n\n💡 참고: 이미 포스팅된 글과 비슷해 보이는 질문이 {len(posting_warns)}건 있습니다 "
                f"(질문DB에는 그대로 추가했습니다 - 아래 목록, 자세한 내용은 로그 확인).\n" +
                "\n".join(f"  • {sentence} ↔ 기존 '{hit['title']}' ({hit['rate']}%)" for sentence, hit in posting_warns[:10]) +
                (f"\n  … 외 {len(posting_warns) - 10}건 더" if len(posting_warns) > 10 else "")
            ) if posting_warns else ""

            messagebox.showinfo(
                "완료",
                f"질문DB에 {added}건 저장했습니다. (중복 제외 {len(skipped_dup)}건)\n\n"
                f"원본 수집 파일(자동생성_{topic}.txt)을 비웠습니다."
                f"{posting_warn_note}"
            )

            # 화면 초기화 (퍼플렉시티/클로드/최종병합 3개 박스 + 미리보기 전부)
            self.prefilter_result_perp_text.delete("1.0", tk.END)
            self.prefilter_result_claude_text.delete("1.0", tk.END)
            self.prefilter_final_text.delete("1.0", tk.END)
            self.prefilter_preview_text.config(state=tk.NORMAL)
            self.prefilter_preview_text.delete("1.0", tk.END)
            self.prefilter_preview_text.config(state=tk.DISABLED)
            self.prefilter_loaded_count_var.set("불러온 질문: 0건")
            self._prefilter_loaded_questions = []
            self._prefilter_loaded_path = None

        except Exception as e:
            self.log(f"❌ 사전 필터링 저장 오류: {e}")
            messagebox.showerror("오류", f"저장 중 오류 발생:\n{e}")

    def create_step0_5_tab(self):
        """0.5단계: 퍼플렉시티 수집 내용 저장 탭
        [Ver7.10 변경] 왼쪽 목록의 소스가 질문DB에서 "0-1)질문 상세분석" 탭이
        만들어내는 리서치 브리프(research_brief_{모델} 폴더)로 바뀌었다.
        파이프라인: 질문DB → 0-1)질문 상세분석 → 1)퍼플렉시티수집(여기) → ..."""
        frame = ttk.Frame(self.notebook, padding="6")
        self.notebook.add(frame, text="3)퍼플렉시티 수집")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # 주제→파일명 매핑 (좌/우 패널 공용, 저장 대상 = 퍼플렉시티 수집 결과)
        self._perplexity_filename_map = {
            "경제-A-거시경제-경기-통화-금리":               "지식인-경제-A-거시경제-경기-통화-금리-퍼플렉시티생성MD.txt",
            "경제-B-금융-대출-신용-투자-보험-연금상품":      "지식인-경제-B-금융-대출-신용-투자-보험-연금상품-퍼플렉시티생성MD.txt",
            "경제-C-세금-조세제도-연말정산":                 "지식인-경제-C-세금-조세제도-연말정산-퍼플렉시티생성MD.txt",
            "경제-D-고용-노동-근로관계-취업지원":           "지식인-경제-D-고용-노동-근로관계-취업지원-퍼플렉시티생성MD.txt",
            "경제-E-복지연금-사회보험-국민연금-생활지원":   "지식인-경제-E-복지연금-사회보험-국민연금-생활지원-퍼플렉시티생성MD.txt",
            "경제-F-법률-행정-행정절차-가사":               "지식인-경제-F-법률-행정-행정절차-가사-퍼플렉시티생성MD.txt",
            "경제-G-부동산-임대차-매매-등기":               "지식인-경제-G-부동산-임대차-매매-등기-퍼플렉시티생성MD.txt",
            "건강":   "지식인-건강-퍼플렉시티생성MD.txt",
            "교육":   "지식인-교육-퍼플렉시티생성MD.txt",
            "자동차": "지식인-자동차-퍼플렉시티생성MD.txt",
            "IT":     "지식인-IT-퍼플렉시티생성MD.txt",
        }
        topics = list(self._perplexity_filename_map.keys())

        # ── 왼쪽: 리서치 브리프 선택 (0-1탭 결과물) ──
        left = ttk.Frame(paned, padding=(4, 4, 8, 4))
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(5, weight=1)

        ttk.Label(left, text="📋 리서치 브리프 선택 (0-1탭 상세분석 결과)", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        topic_row = ttk.Frame(left)
        topic_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(topic_row, text="주제:").pack(side=tk.LEFT, padx=(0, 5))
        self.perp_topic_var = tk.StringVar(value=topics[0])
        self.perp_count_var = tk.StringVar(value="")
        ttk.Combobox(
            topic_row, textvariable=self.perp_topic_var,
            values=topics, state="readonly", width=50, height=11
        ).pack(side=tk.LEFT)

        # [Ver7.10 복구] 좌우분할로 재구성하면서 빠졌던 버튼 - 함수는 계속
        # 있었지만 호출할 버튼이 없어서 프롬프트를 설정할 방법이 없었다.
        ttk.Button(left, text="⚙️ 퍼플렉시티 프롬프트 설정",
                   command=self.open_kin_perplexity_prompt_settings).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        self.perp_hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_research_brief_picker', False))
        ttk.Checkbutton(left, text="사용한 브리프 숨기기", variable=self.perp_hide_used_var).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # [Ver7.10 추가] 날짜 필터(정확일치) + 총 개수 표시
        perp_filter_row = ttk.Frame(left)
        perp_filter_row.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(perp_filter_row, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.perp_date_var = tk.StringVar()
        perp_date_entry = ttk.Entry(perp_filter_row, textvariable=self.perp_date_var, width=11)
        perp_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        perp_date_entry.bind("<Return>", lambda e: self._perp_refresh_list())
        ttk.Button(perp_filter_row, text="오늘",
                   command=lambda: (self.perp_date_var.set(__import__('datetime').datetime.now().strftime("%Y-%m-%d")), self._perp_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(perp_filter_row, text="↺", width=3,
                   command=lambda: (self.perp_date_var.set(""), self._perp_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 8))
        self.perp_list_count_var = tk.StringVar(value="")
        ttk.Label(perp_filter_row, textvariable=self.perp_list_count_var, foreground="navy").pack(side=tk.LEFT)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("used", "title", "date", "folder")
        self.perp_list_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        self.perp_list_tree.heading("used", text="사용")
        self.perp_list_tree.heading("title", text="질문 제목")
        self.perp_list_tree.heading("date", text="날짜")
        self.perp_list_tree.heading("folder", text="폴더(모델)")
        self.perp_list_tree.column("used", width=40, anchor=tk.CENTER)
        self.perp_list_tree.column("title", width=240)
        self.perp_list_tree.column("date", width=80, anchor=tk.CENTER)
        self.perp_list_tree.column("folder", width=140)
        self.perp_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.perp_list_tree.yview)
        self.perp_list_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.perp_list_tree.bind("<Double-1>", lambda e: self._perp_copy_selected())

        self._perp_list_cache = {'items': [], 'usage': {}}
        self._perp_selected_item = None  # [Ver7.17 추가] 복사한 항목을 저장 시점까지 기억(완료 판정용)

        list_btn_frame = ttk.Frame(left)
        list_btn_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame, text="📋 퍼플렉시티 프롬프트 + 클로드 브리프(요약)자료 복사",
                   command=self._perp_copy_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="퍼플렉시티 프롬프트만 복사",
                   command=self._perp_copy_prompt_only).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="요약 자료만 복사",
                   command=self._perp_copy_question_only).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame2 = ttk.Frame(left)
        list_btn_frame2.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame2, text="사용여부 토글",
                   command=self._perp_toggle_used).pack(side=tk.LEFT, padx=(0, 4))
        # [Ver7.76 추가] 사용자 요청: "1)질문수집"·"2)질문 상세분석"에는
        # 삭제 버튼이 있는데 이후 단계(퍼플렉시티 수집·1차 각색·2차 각색)
        # 에는 없어서, 여기서 더 진행하고 싶지 않은 자료를 지우려면 매번
        # 앞 탭으로 되돌아가야 하는 불편함이 있었음. 여기서 목록에 뜬
        # "이 단계의 원본 파일"(research_brief MD)을 바로 지울 수 있게 함
        # (질문DB 자체는 건드리지 않음 - 질문DB 삭제는 여전히 2)질문
        # 상세분석 탭의 역할, 여긴 "이 단계 자료"만 지움).
        ttk.Button(list_btn_frame2, text="🗑️ 선택 삭제",
                   command=self._perp_delete_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🔄 새로고침",
                   command=self._perp_refresh_list).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(left, text="더블클릭 = 프롬프트+브리프 복사 → 퍼플렉시티 웹에 붙여넣기",
                  justify=tk.LEFT, foreground="blue", wraplength=430).grid(
            row=8, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # ── 오른쪽: 퍼플렉시티가 준 수집 결과 붙여넣기 & 저장 ──
        right = ttk.Frame(paned, padding=(8, 4, 4, 4))
        paned.add(right, weight=3)
        right.columnconfigure(1, weight=1)

        guide = (
            "사용법:  1) 왼쪽에서 브리프 골라 복사→퍼플렉시티 웹에 붙여넣기  2) 퍼플렉시티 응답을 아래에 붙여넣기  3) [저장] 클릭\n"
            "파일이 있으면 추가, 없으면 자동 생성  |  저장 위치: 기본 작업 폴더"
        )
        ttk.Label(right, text=guide, justify=tk.LEFT, foreground="blue").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
        )

        ttk.Label(right, text="저장 파일명:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.perp_filename_var = tk.StringVar()
        filename_row = ttk.Frame(right)
        filename_row.grid(row=1, column=1, sticky=tk.W, pady=4)
        ttk.Label(filename_row, textvariable=self.perp_filename_var,
                  foreground="navy").pack(side=tk.LEFT)
        ttk.Label(filename_row, text="   수집 개수:").pack(side=tk.LEFT)
        ttk.Label(filename_row, textvariable=self.perp_count_var,
                  foreground="darkgreen").pack(side=tk.LEFT, padx=(2, 0))

        ttk.Label(right, text="수집 내용\n붙여넣기:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(6, 0))
        self.perp_text = scrolledtext.ScrolledText(right, height=30, wrap=tk.WORD)
        self.perp_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(6, 0))
        self.perp_text.bind("<KeyRelease>", lambda e: self._update_perp_char_count())
        self.perp_text.bind("<<Paste>>", lambda e: self.root.after(10, self._update_perp_char_count))

        self.perp_char_count_var = tk.StringVar(value="한글 글자수: 0자")
        ttk.Label(right, textvariable=self.perp_char_count_var,
                  foreground="darkred", font=("", 9, "bold")).grid(
            row=3, column=1, sticky=tk.W, pady=(2, 0))

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="저장",
                   command=self.save_perplexity_collect).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="내용 지우기",
                   command=lambda: self.perp_text.delete("1.0", tk.END)).pack(side=tk.LEFT)

        # 주제 변경 시 파일명·목록 갱신
        self.perp_topic_var.trace_add("write", lambda *_: self._update_perp_filename())
        self.perp_topic_var.trace_add("write", lambda *_: self._perp_refresh_list())
        self.perp_hide_used_var.trace_add("write", lambda *_: self._perp_refresh_list())
        self.perp_hide_used_var.trace_add(
            "write", lambda *_: self.save_kin_ui_setting('hide_used_research_brief_picker', self.perp_hide_used_var.get()))
        self._update_perp_filename()
        self._perp_refresh_list()

    # ── [Ver7.10 추가] 1)탭 왼쪽 목록(좌우분할)용 헬퍼 — 소스가
    # "0-1)질문 상세분석" 탭이 저장한 research_brief_{모델} 폴더로 바뀜 ──
    def _scan_research_brief_items(self, base_folder, topic):
        """base/주제/날짜/research_brief_*/ 안의 상세분석 결과 MD 파일들을 스캔.
        [Ver7.10 버그수정] 저장 폴더명이 'research_brief_{모델}'(접두사+모델)
        순서인데, 예전엔 반대로 '{모델}_research_brief'(접미사) 패턴으로
        검사해서 저장한 파일을 하나도 못 찾던 문제를 고쳤다."""
        items = []
        topic_path = os.path.join(base_folder, topic)
        if not os.path.exists(topic_path):
            return items
        for date_folder in os.listdir(topic_path):
            date_path = os.path.join(topic_path, date_folder)
            if not os.path.isdir(date_path):
                continue
            for folder_name in os.listdir(date_path):
                if not folder_name.startswith('research_brief_'):
                    continue
                brief_path = os.path.join(date_path, folder_name)
                for filename in os.listdir(brief_path):
                    if filename.endswith('.md'):
                        file_path = os.path.join(brief_path, filename)
                        items.append({
                            "title": filename[:-3],
                            "date": date_folder,
                            "folder": folder_name,
                            "file_path": file_path,
                        })
        # [Ver7.10 수정] 날짜(일 단위) 문자열만으로 정렬하면 같은 날짜
        # 안에서는 OS가 반환하는 임의 순서를 따라 새 항목이 중간에
        # 끼어드는 것처럼 보였다. 실제 파일 수정시각 기준 오름차순으로
        # 바꿔 "새로 추가된 항목이 항상 맨 아래"가 되도록 한다.
        items.sort(key=lambda x: os.path.getmtime(x["file_path"]) if os.path.exists(x["file_path"]) else 0)
        return items

    def _get_brief_usage_path(self, base_folder, topic):
        return os.path.join(base_folder, topic, "리서치브리프_사용여부.json")

    def _load_brief_usage(self, base_folder, topic):
        path = self._get_brief_usage_path(base_folder, topic)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_brief_usage(self, base_folder, topic, usage):
        path = self._get_brief_usage_path(base_folder, topic)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

    def _perp_refresh_list(self):
        if not hasattr(self, 'perp_list_tree'):
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.perp_topic_var.get()
        self.perp_list_tree.delete(*self.perp_list_tree.get_children())
        items = self._scan_research_brief_items(base, topic)
        usage = self._load_brief_usage(base, topic)
        self._perp_list_cache['items'] = items
        self._perp_list_cache['usage'] = usage
        date_filter = self.perp_date_var.get().strip() if hasattr(self, 'perp_date_var') else ""
        shown = 0
        for i, item in enumerate(items):
            used = usage.get(item["title"], False)
            if self.perp_hide_used_var.get() and used:
                continue
            if date_filter and item["date"] != date_filter:
                continue
            self.perp_list_tree.insert("", tk.END, iid=str(i), values=(
                "✅" if used else "", item["title"], item["date"], item["folder"]
            ))
            shown += 1

        if hasattr(self, 'perp_list_count_var'):
            total = len(items)
            if date_filter:
                self.perp_list_count_var.set(f"검색결과 {shown}개 / 전체 {total}개")
            else:
                self.perp_list_count_var.set(f"총 {total}개")

    # [Ver7.10 추가] 0-1)탭이 저장한 전체 상세분석 결과(가치판단+관련질문
    # 확장+키워드전략+리서치브리프 4개 섹션)에서, 실제로 퍼플렉시티에
    # 붙여넣도록 설계된 "## 퍼플렉시티 리서치 브리프" 밑 ---...--- 블록만
    # 뽑아낸다. 나머지 판정/근거 텍스트는 디스크 파일엔 그대로 남지만
    # 퍼플렉시티로는 안 넘어간다. 못 찾으면(형식이 다르거나 보류 판정 등)
    # 안전하게 전체 텍스트를 그대로 반환한다.
    def _extract_perplexity_brief(self, full_text):
        m = re.search(r'##\s*퍼플렉시티\s*리서치\s*브리프.*?\n-{3,}\s*\n(.*?)\n-{3,}', full_text, re.S)
        if m:
            return m.group(1).strip()
        return full_text.strip()

    def _perp_copy_selected(self):
        sel = self.perp_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 브리프를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._perp_list_cache['items'][idx]
        topic = self.perp_topic_var.get()

        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                full_content = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        material = self._extract_perplexity_brief(full_content)

        prompts = self.load_kin_perplexity_prompts()
        prompt_filename = prompts.get(topic, "")
        if not prompt_filename:
            messagebox.showwarning(
                "퍼플렉시티 프롬프트 없음",
                f"'{topic}' 주제에 등록된 퍼플렉시티 프롬프트가 없습니다.\n"
                f"'⚙️ 퍼플렉시티 프롬프트 설정'에서 먼저 등록하세요."
            )
            return

        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
            return

        content = (
            f"{prompt_text}\n\n"
            f"───────────────────\n"
            f"[리서치 브리프]\n"
            f"{material}\n"
        )

        self.root.clipboard_clear()
        self.root.clipboard_append(content)

        # [Ver7.17 수정] 복사 시점엔 usage를 바로 True로 기록하지 않는다.
        # "저장" 버튼(save_perplexity_collect)이 실제로 결과를 저장했을 때만
        # 완료 처리한다. 여기서 대상만 기억해두고, 목록은 그 행의 셀만
        # "📋(진행중)"으로 바꿔 선택/포커스를 유지한다.
        self._perp_selected_item = {'title': item['title'], 'iid': sel[0]}
        self._kin_mark_row_in_progress(self.perp_list_tree, sel[0])

        self.log(f"📋 퍼플렉시티용 브리프 복사 완료 (프롬프트: {prompt_filename}): {item['title']}")

    def _perp_copy_prompt_only(self):
        """[Ver7.84 신규] 자료(브리프) 선택 없이, 현재 선택된 주제에 매핑된
        퍼플렉시티 프롬프트 텍스트만 클립보드에 복사한다. 7)1차각색/
        8)2차각색의 "프롬프트만 복사"와 동일한 컨셉을 이 탭에도 맞춰 추가."""
        topic = self.perp_topic_var.get()
        prompts = self.load_kin_perplexity_prompts()
        prompt_filename = prompts.get(topic, "")
        if not prompt_filename:
            messagebox.showwarning(
                "퍼플렉시티 프롬프트 없음",
                f"'{topic}' 주제에 등록된 퍼플렉시티 프롬프트가 없습니다.\n"
                f"'⚙️ 퍼플렉시티 프롬프트 설정'에서 먼저 등록하세요."
            )
            return
        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_PROMPT_CONTINUITY_NOTICE + prompt_text)
        self.log(f"📋 퍼플렉시티 프롬프트만 복사: {prompt_filename} ({topic})")
        messagebox.showinfo("복사 완료", "프롬프트만 클립보드에 복사되었습니다.")

    def _perp_copy_question_only(self):
        sel = self.perp_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 브리프를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._perp_list_cache['items'][idx]
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                full_content = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        material = self._extract_perplexity_brief(full_content)
        self.root.clipboard_clear()
        self.root.clipboard_append(material)
        # [Ver7.17 추가] "브리프만 복사"만 쓰더라도 저장이 정상 동작하도록
        # 작업 대상을 함께 기억해둔다.
        self._perp_selected_item = {'title': item['title'], 'iid': sel[0]}
        self._kin_mark_row_in_progress(self.perp_list_tree, sel[0])
        self.log(f"📋 브리프만 복사: {item['title']}")

    def _perp_toggle_used(self):
        sel = self.perp_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._perp_list_cache['items'][idx]
        topic = self.perp_topic_var.get()
        base = self.base_folder_var.get().strip() or self.base_folder
        usage = self._perp_list_cache['usage']
        new_state = not usage.get(item["title"], False)
        usage[item["title"]] = new_state
        self._save_brief_usage(base, topic, usage)
        self._kin_mark_row_used(self.perp_list_tree, sel[0], self.perp_hide_used_var,
                                 self._perp_refresh_list, used=new_state)

    def _perp_delete_selected(self):
        """[Ver7.76 신규] "3)퍼플렉시티 수집" 목록에 뜬 research_brief MD
        파일을 여러 개 선택해 한번에 삭제한다. "2)질문 상세분석"의
        _detail_delete_selected와 달리 여기서는 질문DB 자체는 건드리지
        않는다(이미 질문DB→질문상세분석에서 상세분석까지 끝난, "이
        단계"의 산출물만 지운다는 의미) - 질문 자체를 지우고 싶으면
        여전히 "2)질문 상세분석" 탭에서 지워야 한다."""
        sel = self.perp_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "삭제할 항목을 먼저 선택하세요.")
            return
        indices = sorted((int(i) for i in sel), reverse=True)
        items = self._perp_list_cache['items']
        targets = [items[i] for i in indices if 0 <= i < len(items)]

        preview = "\n".join(f"  • {t['title']}" for t in targets[:10])
        if len(targets) > 10:
            preview += f"\n  … 외 {len(targets) - 10}건 더"

        if not messagebox.askyesno(
                "⚠️ 삭제 확인 (되돌릴 수 없음)",
                f"아래 {len(targets)}개 리서치 브리프 파일을 영구 삭제합니다.\n"
                f"(질문DB 자체는 지워지지 않습니다 - 질문 삭제는 \"2)질문 상세분석\" 탭에서)\n\n"
                f"{preview}\n\n정말 삭제하시겠습니까?",
                icon="warning"):
            return

        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.perp_topic_var.get()
        usage = self._perp_list_cache['usage']
        deleted = 0
        for t in targets:
            try:
                if os.path.exists(t["file_path"]):
                    os.remove(t["file_path"])
                usage.pop(t["title"], None)
                deleted += 1
            except Exception as e:
                self.log(f"⚠️ 브리프 파일 삭제 실패: {t['file_path']} ({e})")
        self._save_brief_usage(base, topic, usage)
        self.log(f"🗑️ 리서치 브리프 삭제 완료: {deleted}개 ({topic})")
        self._perp_refresh_list()


    def _update_perp_filename(self):
        topic = self.perp_topic_var.get()
        filename = self._perplexity_filename_map.get(topic, "")
        self.perp_filename_var.set(filename)
        self._update_perp_count()

    def _update_perp_count(self):
        topic = self.perp_topic_var.get()
        filename = self._perplexity_filename_map.get(topic, "")
        base = self.base_folder_var.get().strip() or self.base_folder
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            self.perp_count_var.set("0개 (파일 없음)")
            return
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        count = content.count("##### 질문")
        self.perp_count_var.set("{}개".format(count))

    def _update_perp_char_count(self):
        text = self.perp_text.get("1.0", tk.END)
        korean = len(re.findall(r'[\uAC00-\uD7A3]', text))
        english = len(re.findall(r'[a-zA-Z0-9]', text))
        punct = len(re.findall(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', text))
        spaces = len(re.findall(r'[ \t]', text))
        total_excl = int(korean + english * 0.5 + punct)
        total_incl = int(korean + english * 0.5 + punct + spaces)
        self.perp_char_count_var.set(
            "한글 기준 글자수 │ 공백제외: {:,}자 │ 공백포함: {:,}자".format(total_excl, total_incl)
        )

    def save_perplexity_collect(self):
        """퍼플렉시티 수집 내용을 txt 파일에 추가 저장"""
        text = self.perp_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("저장 오류", "저장할 내용이 없습니다.")
            return

        topic = self.perp_topic_var.get()
        filename = self._perplexity_filename_map.get(topic, "")
        if not filename:
            messagebox.showwarning("저장 오류", "주제를 선택하세요.")
            return

        base = self.base_folder_var.get().strip() or self.base_folder
        save_path = os.path.join(base, filename)

        # 형식 검증: ##### 질문 요약이 # 제목보다 먼저 나와야 함
        h1_match = re.search(r'(?:^|\n)# [^#]', text)
        summary_match = re.search(r'##### 질문 요약', text)

        if not summary_match:
            messagebox.showerror("형식 오류",
                "'##### 질문 요약' 이 없습니다.\n"
                "붙여넣기 내용을 확인 후 수정해주세요.")
            return

        if h1_match and h1_match.start() < summary_match.start():
            messagebox.showerror("형식 오류",
                "퍼플렉시티 자료 형식이 올바르지 않습니다.\n\n"
                "'##### 질문 요약' 이 '# 제목' 보다 먼저 나와야 합니다.\n"
                "붙여넣기 내용을 확인 후 수정해주세요.")
            return

    
        # ✅ 중복 체크
        if os.path.exists(save_path):
            import difflib
            with open(save_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
    
            new_compare = re.sub(r'\s+', ' ', text[:300]).strip()
            blocks = re.split(r'(?=##### 질문 요약)', existing_content)
    
            duplicate_title = None
            for block in blocks:
                if not block.strip():
                    continue
                existing_compare = re.sub(r'\s+', ' ', block[:300]).strip()
                ratio = difflib.SequenceMatcher(None, new_compare, existing_compare).ratio()
                if ratio >= 0.9:
                    duplicate_title = block.strip().split('\n')[0].strip()
                    break
    
            if duplicate_title:
                proceed = messagebox.askyesno(
                    "중복 자료 감지",
                    f"유사한 자료가 이미 저장되어 있습니다. (유사도 90% 이상)\n\n"
                    f"기존 자료: {duplicate_title}\n\n"
                    f"그래도 저장하시겠습니까?"
                )
                if not proceed:
                    return

        status = "추가 저장" if os.path.exists(save_path) else "신규 생성"
        try:
            with open(save_path, 'a', encoding='utf-8') as f:
                f.write("\n\n")
                f.write(text)
                f.write("\n")

            self.log("퍼플렉시티 수집 저장 ({}): {}".format(status, filename))
            self.perp_text.delete("1.0", tk.END)
            self._update_perp_count()

            # [Ver7.17 추가] 실제 저장이 끝난 시점에만 "완료"로 기록한다.
            # (복사만 하고 저장을 안 하면 목록에 "📋 진행중"으로 계속 남아
            # 누락을 바로 알아챌 수 있다.)
            target = getattr(self, '_perp_selected_item', None)
            if target and target.get('title'):
                usage = self._perp_list_cache.get('usage', {})
                usage[target['title']] = True
                self._save_brief_usage(base, topic, usage)
                self._kin_mark_row_used(self.perp_list_tree, target.get('iid'),
                                         self.perp_hide_used_var, self._perp_refresh_list)
                self._perp_selected_item = None

        except Exception as e:
            self.log("퍼플렉시티 저장 실패: {}".format(str(e)))
            messagebox.showerror("저장 실패", "저장 중 오류 발생:\n{}".format(str(e)))


    def create_step1_tab(self):
        """[Ver7.10 변경] 예전 "텍스트→MD 변환" 워크플로우는 2-1)탭의
        자동변환 버튼으로 대체됐다. 이 탭은 그 UI(파일선택+변환 버튼)를
        빼고, 앱 전체 로그 표시창 + API 키 설정만 남긴다 — self.log()가
        전역에서 이 로그창 하나에 의존하기 때문에 완전히 없앨 수는 없다."""
        step1_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(step1_frame, text="5)API설정")

        button_frame = ttk.Frame(step1_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(10, 5))
        ttk.Button(button_frame, text="⚙️ API 키 설정", command=self.open_api_key_settings).pack(side=tk.LEFT, padx=(0, 10))

        info_label = ttk.Label(
            step1_frame,
            text="📌 프로그램 실행 중 발생하는 모든 로그가 여기에 표시됩니다.",
            justify=tk.LEFT, foreground="blue")
        info_label.grid(row=1, column=0, columnspan=2, pady=(1, 1), sticky=(tk.W, tk.E))

        # ✅ 작업 로그 프레임 추가
        log_frame = ttk.LabelFrame(step1_frame, text="작업 로그", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))

        # 스크롤 가능한 텍스트 위젯
        self.step1_log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=26,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 9)
        )
        self.step1_log_text.pack(fill=tk.BOTH, expand=True)

        # 버퍼에 쌓인 로그 flush
        if hasattr(self, '_pending_logs') and self._pending_logs:
            for msg in self._pending_logs:
                self.step1_log_text.config(state=tk.NORMAL)
                self.step1_log_text.insert(tk.END, msg + "\n")
                self.step1_log_text.config(state=tk.DISABLED)
            self._pending_logs.clear()

        # 그리드 설정
        step1_frame.rowconfigure(2, weight=1)
        step1_frame.columnconfigure(0, weight=1)

    def create_kin_verify_tab(self):
        """2-1단계: 퍼플렉시티 결과 교차검증
        [Ver7.10 신설] 1)퍼플렉시티수집 → 2)텍스트→MD변환(perplexity_answers)
        다음, 4)1차각색(웹) 이전에 들어가는 검증단계. 2)탭이 만든 개별
        MD(퍼플렉시티 원문 그대로)를 골라 도메인별 교차검증 프롬프트와
        함께 웹 AI(클로드)에 보내고, 돌아온 검증 결과에서 "## 검증된
        자료" 섹션만 추출해 perplexity_[모델]_verified 폴더에 저장한다.
        이 저장분을 4)탭이 원자료로 그대로 이어받는다(1)/4)/5)탭과
        동일한 좌우분할 패턴)."""
        frame = ttk.Frame(self.notebook, padding="6")
        self.notebook.add(frame, text="4)퍼플렉시티 자료검증(클로드)")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        # ── 왼쪽: 검증할 퍼플렉시티 원본자료 선택 (2단계 산출물) ──
        left = ttk.Frame(paned, padding=(4, 4, 8, 4))
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(6, weight=1)

        ttk.Label(left, text="📋 검증할 자료 선택 (퍼플렉시티 원본)", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        topic_row = ttk.Frame(left)
        topic_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(topic_row, text="주제:").pack(side=tk.LEFT, padx=(0, 5))
        self.verify_topic_var = tk.StringVar(value=topics[0])
        ttk.Combobox(
            topic_row, textvariable=self.verify_topic_var,
            values=topics, state="readonly", width=50, height=11
        ).pack(side=tk.LEFT)

        # [Ver7.10 추가] 예전 "2)텍스트→MD 변환" 탭 기능을 주제 기준으로
        # 자동화한 버튼. 1)탭이 저장해둔 지식인-[주제]-퍼플렉시티생성MD.txt를
        # 읽어 개별 perplexity_answers/*.md로 변환하고, 왼쪽 목록을 바로
        # 새로고침한다. 파일 선택도, 별도 탭 이동도 필요 없다.
        ttk.Button(left, text="📥 새 퍼플렉시티 자료 가져오기 (자동 MD변환)",
                   command=self._verify_import_and_convert).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        ttk.Button(left, text="⚙️ 교차검증 프롬프트 설정",
                   command=self.open_kin_verify_prompt_settings).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        self.verify_hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_verify_picker', False))
        ttk.Checkbutton(left, text="검증 완료 자료 숨기기", variable=self.verify_hide_used_var).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # [Ver7.10 추가] 날짜 필터(정확일치) + 총 개수 표시
        verify_filter_row = ttk.Frame(left)
        verify_filter_row.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(verify_filter_row, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.verify_date_var = tk.StringVar()
        verify_date_entry = ttk.Entry(verify_filter_row, textvariable=self.verify_date_var, width=11)
        verify_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        verify_date_entry.bind("<Return>", lambda e: self._verify_refresh_list())
        ttk.Button(verify_filter_row, text="오늘",
                   command=lambda: (self.verify_date_var.set(__import__('datetime').datetime.now().strftime("%Y-%m-%d")), self._verify_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(verify_filter_row, text="↺", width=3,
                   command=lambda: (self.verify_date_var.set(""), self._verify_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 8))
        self.verify_list_count_var = tk.StringVar(value="")
        ttk.Label(verify_filter_row, textvariable=self.verify_list_count_var, foreground="navy").pack(side=tk.LEFT)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("used", "title", "date")
        self.verify_list_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        self.verify_list_tree.heading("used", text="검증")
        self.verify_list_tree.heading("title", text="제목")
        self.verify_list_tree.heading("date", text="날짜")
        self.verify_list_tree.column("used", width=40, anchor=tk.CENTER)
        self.verify_list_tree.column("title", width=320)
        self.verify_list_tree.column("date", width=80, anchor=tk.CENTER)
        self.verify_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.verify_list_tree.yview)
        self.verify_list_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.verify_list_tree.bind("<Double-1>", lambda e: self._verify_copy_selected())

        self._verify_list_cache = {'items': [], 'usage': {}}
        self._verify_selected_item = None

        list_btn_frame = ttk.Frame(left)
        list_btn_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame, text="📋 클로드 검증 프롬프트 + 자료 복사",
                   command=self._verify_copy_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="플로드 검증 프롬프트만 복사",
                   command=self._verify_copy_prompt_only).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="자료만 복사",
                   command=self._verify_copy_material_only).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame2 = ttk.Frame(left)
        list_btn_frame2.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame2, text="검증여부 토글",
                   command=self._verify_toggle_used).pack(side=tk.LEFT, padx=(0, 4))
        # [Ver7.77 추가] 다른 세 탭(퍼플렉시티 수집·1차 각색·2차 각색)과
        # 동일한 패턴 - 이 단계 목록에 뜬 원본자료(perplexity_answers) MD
        # 파일을 여기서 바로 지울 수 있게 함(질문DB는 건드리지 않음).
        ttk.Button(list_btn_frame2, text="🗑️ 선택 삭제",
                   command=self._verify_delete_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🔄 새로고침",
                   command=self._verify_refresh_list).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(left, text="더블클릭 = 프롬프트+자료 복사 → 웹 AI(클로드)에 붙여넣기",
                  justify=tk.LEFT, foreground="blue", wraplength=430).grid(
            row=9, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # ── 오른쪽: 검증 결과 붙여넣기 & 저장 ──
        right = ttk.Frame(paned, padding=(8, 4, 4, 4))
        paned.add(right, weight=3)
        right.columnconfigure(1, weight=1)

        guide = (
            "사용법:  1) 왼쪽에서 자료 골라 복사→웹 AI에 붙여넣기  2) 돌아온 검증 결과 전체를 아래에 붙여넣기  3) [저장] 클릭\n"
            "저장 시 '## 검증된 자료' 섹션만 자동으로 뽑아 저장합니다. 저장 경로: 기본폴더/주제/오늘날짜/perplexity_[모델]_verified/제목.md\n"
            "(여기 저장된 결과는 4)탭 왼쪽 목록에 그대로 나타납니다)"
        )
        ttk.Label(right, text=guide, justify=tk.LEFT, foreground="blue", wraplength=560).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
        )

        ttk.Label(right, text="저장 모델:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.verify_model_var = tk.StringVar(value="Claude")
        model_frame = ttk.Frame(right)
        model_frame.grid(row=1, column=1, sticky=tk.W, pady=4)
        for m in ["Claude", "GPT", "Gemini"]:
            ttk.Radiobutton(
                model_frame, text="perplexity_{}_verified".format(m),
                variable=self.verify_model_var, value=m
            ).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(right, text="검증 대상\n자료:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=4)
        self.verify_target_var = tk.StringVar(value="(왼쪽에서 자료를 복사하면 여기에 표시됩니다)")
        ttk.Label(right, textvariable=self.verify_target_var, foreground="darkgreen",
                  wraplength=480, justify=tk.LEFT).grid(row=2, column=1, sticky=tk.W, pady=4)

        ttk.Label(right, text="검증 결과\n붙여넣기:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(6, 0))
        self.verify_text = scrolledtext.ScrolledText(right, height=24, wrap=tk.WORD)
        self.verify_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(6, 0))
        self.verify_text.bind("<KeyRelease>", lambda e: self._verify_update_char_count())
        self.verify_text.bind("<<Paste>>", lambda e: self.root.after(10, self._verify_update_char_count))

        self.verify_char_count_var = tk.StringVar(value="한글 글자수: 0자")
        ttk.Label(right, textvariable=self.verify_char_count_var,
                  foreground="darkred", font=("", 9, "bold")).grid(
            row=4, column=1, sticky=tk.W, pady=(2, 0))

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(8, 0), sticky=tk.W)
        self.verify_save_btn = ttk.Button(btn_frame, text="저장",
                   command=self._verify_save_result)
        self.verify_save_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="내용 지우기",
                   command=self._verify_clear).pack(side=tk.LEFT)

        self.verify_topic_var.trace_add("write", lambda *_: self._verify_refresh_list())
        self.verify_hide_used_var.trace_add("write", lambda *_: self._verify_refresh_list())
        self.verify_hide_used_var.trace_add(
            "write", lambda *_: self.save_kin_ui_setting('hide_used_verify_picker', self.verify_hide_used_var.get()))
        self._verify_refresh_list()

    # ── [Ver7.10 추가] 2-1)탭 왼쪽 목록(좌우분할)용 헬퍼 ──
    # [Ver7.10 추가] 예전 "2)텍스트→MD 변환" 탭을 대체하는 자동화 함수.
    # 파일을 직접 선택할 필요 없이, 주제 하나만 넘기면 1)탭이 저장해둔
    # 지식인-[주제]-퍼플렉시티생성MD.txt를 찾아서 개별 MD로 변환한다.
    # process_text_string/create_output_directory는 2)탭 UI에 의존하지
    # 않는 공용 로직이라 그대로 재사용한다.
    def _auto_convert_perplexity_to_md(self, topic):
        base_dir = self.base_folder_var.get().strip() or self.base_folder
        filename_map = getattr(self, '_perplexity_filename_map', None) or {
            "경제-A-거시경제-경기-통화-금리":               "지식인-경제-A-거시경제-경기-통화-금리-퍼플렉시티생성MD.txt",
            "경제-B-금융-대출-신용-투자-보험-연금상품":      "지식인-경제-B-금융-대출-신용-투자-보험-연금상품-퍼플렉시티생성MD.txt",
            "경제-C-세금-조세제도-연말정산":                 "지식인-경제-C-세금-조세제도-연말정산-퍼플렉시티생성MD.txt",
            "경제-D-고용-노동-근로관계-취업지원":           "지식인-경제-D-고용-노동-근로관계-취업지원-퍼플렉시티생성MD.txt",
            "경제-E-복지연금-사회보험-국민연금-생활지원":   "지식인-경제-E-복지연금-사회보험-국민연금-생활지원-퍼플렉시티생성MD.txt",
            "경제-F-법률-행정-행정절차-가사":               "지식인-경제-F-법률-행정-행정절차-가사-퍼플렉시티생성MD.txt",
            "경제-G-부동산-임대차-매매-등기":               "지식인-경제-G-부동산-임대차-매매-등기-퍼플렉시티생성MD.txt",
            "건강":   "지식인-건강-퍼플렉시티생성MD.txt",
            "교육":   "지식인-교육-퍼플렉시티생성MD.txt",
            "자동차": "지식인-자동차-퍼플렉시티생성MD.txt",
            "IT":     "지식인-IT-퍼플렉시티생성MD.txt",
        }
        perp_filename = filename_map.get(topic)
        if not perp_filename:
            messagebox.showwarning("알림", f"'{topic}' 주제의 퍼플렉시티 수집 파일명을 찾을 수 없습니다.")
            return False

        file_path = os.path.join(base_dir, perp_filename)
        if not os.path.exists(file_path):
            messagebox.showinfo("알림", f"수집된 퍼플렉시티 자료 파일이 없습니다:\n{file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read().strip()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp949') as f:
                text_content = f.read().strip()

        if not text_content:
            messagebox.showinfo("알림", "변환할 새 자료가 없습니다. (수집 파일이 비어 있음)")
            return False

        output_dir = self.create_output_directory(base_dir, topic)
        created_files, error_files = self.process_text_string(text_content, output_dir)

        if created_files:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')

        msg = f"✅ [{topic}] 텍스트→MD 자동변환 완료: {len(created_files)}개 생성"
        if error_files:
            msg += f" (형식오류 {len(error_files)}개 → perplexity_errors/)"
        self.log(msg)

        if not created_files:
            messagebox.showinfo("알림", "새로 변환된 파일이 없습니다." +
                                 (f" (형식오류 {len(error_files)}개는 perplexity_errors 폴더 확인)" if error_files else ""))
            return False
        return True

    def _verify_import_and_convert(self):
        """2-1)탭 '📥 새 퍼플렉시티 자료 가져오기' 버튼 - 현재 선택된 주제
        기준으로 자동 MD변환 실행 후 왼쪽 목록을 바로 새로고침한다."""
        topic = self.verify_topic_var.get()
        ok = self._auto_convert_perplexity_to_md(topic)
        self._verify_refresh_list()
        if ok:
            messagebox.showinfo("완료", "새 자료를 가져와 변환했습니다. 왼쪽 목록에서 확인하세요.")

    def _verify_refresh_list(self):
        if not hasattr(self, 'verify_list_tree'):
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.verify_topic_var.get()
        self.verify_list_tree.delete(*self.verify_list_tree.get_children())
        items = self._scan_raw_material_items(base, topic)
        usage = self._load_verify_usage(base, topic)
        self._verify_list_cache['items'] = items
        self._verify_list_cache['usage'] = usage
        date_filter = self.verify_date_var.get().strip() if hasattr(self, 'verify_date_var') else ""
        shown = 0
        for i, item in enumerate(items):
            used = usage.get(item["title"], False)
            if self.verify_hide_used_var.get() and used:
                continue
            if date_filter and item["date"] != date_filter:
                continue
            self.verify_list_tree.insert("", tk.END, iid=str(i), values=(
                "✅" if used else "", item["title"], item["date"]
            ))
            shown += 1

        if hasattr(self, 'verify_list_count_var'):
            total = len(items)
            if date_filter:
                self.verify_list_count_var.set(f"검색결과 {shown}개 / 전체 {total}개")
            else:
                self.verify_list_count_var.set(f"총 {total}개")

    def _verify_copy_selected(self):
        sel = self.verify_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 자료를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._verify_list_cache['items'][idx]
        topic = self.verify_topic_var.get()

        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                material = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return

        prompts = self.load_kin_verify_prompts()
        prompt_filename = prompts.get(topic, "")
        if not prompt_filename:
            messagebox.showwarning(
                "교차검증 프롬프트 없음",
                f"'{topic}' 주제에 등록된 교차검증 프롬프트가 없습니다.\n"
                f"'⚙️ 교차검증 프롬프트 설정'에서 먼저 등록하세요."
            )
            return

        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
            return

        content = (
            f"{prompt_text}\n\n"
            f"───────────────────\n"
            f"[퍼플렉시티 리서치 결과물]\n"
            f"{material}\n"
        )

        self.root.clipboard_clear()
        self.root.clipboard_append(content)

        # 저장 시 파일명(원래 제목)을 그대로 유지하기 위해 대상 기억
        self._verify_selected_item = {'title': item['title'], 'iid': sel[0]}
        self.verify_target_var.set(item['title'])

        # [Ver7.17 수정] 복사 시점엔 usage를 바로 True로 기록하지 않는다.
        # "저장" 버튼(_verify_save_result)이 실제로 결과를 저장했을 때만
        # 완료 처리한다. 목록은 그 행의 셀만 "📋(진행중)"으로 바꿔
        # 선택/포커스를 유지한다.
        self._kin_mark_row_in_progress(self.verify_list_tree, sel[0])

        self.log(f"📋 교차검증용 자료 복사 완료 (프롬프트: {prompt_filename}): {item['title']}")

    def _verify_copy_prompt_only(self):
        """[Ver7.84 신규] 자료 선택 없이, 현재 선택된 주제에 매핑된 교차검증
        프롬프트 텍스트만 클립보드에 복사한다. 7)1차각색/8)2차각색의
        "프롬프트만 복사"와 동일한 컨셉을 이 탭에도 맞춰 추가."""
        topic = self.verify_topic_var.get()
        prompts = self.load_kin_verify_prompts()
        prompt_filename = prompts.get(topic, "")
        if not prompt_filename:
            messagebox.showwarning(
                "교차검증 프롬프트 없음",
                f"'{topic}' 주제에 등록된 교차검증 프롬프트가 없습니다.\n"
                f"'⚙️ 교차검증 프롬프트 설정'에서 먼저 등록하세요."
            )
            return
        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 파일을 읽을 수 없습니다:\n{prompt_path}\n{e}")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_PROMPT_CONTINUITY_NOTICE + prompt_text)
        self.log(f"📋 교차검증 프롬프트만 복사: {prompt_filename} ({topic})")
        messagebox.showinfo("복사 완료", "프롬프트만 클립보드에 복사되었습니다.")

    def _verify_copy_material_only(self):
        sel = self.verify_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 자료를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._verify_list_cache['items'][idx]
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                material = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(material)
        # [Ver7.17 추가] "자료만 복사"만 쓰더라도 저장이 정상 동작하도록
        # 작업 대상을 함께 기억해둔다.
        self._verify_selected_item = {'title': item['title'], 'iid': sel[0]}
        self.verify_target_var.set(item['title'])
        self._kin_mark_row_in_progress(self.verify_list_tree, sel[0])
        self.log(f"📋 검증용 자료만 복사: {item['title']}")

    def _verify_toggle_used(self):
        sel = self.verify_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._verify_list_cache['items'][idx]
        topic = self.verify_topic_var.get()
        base = self.base_folder_var.get().strip() or self.base_folder
        usage = self._verify_list_cache['usage']
        new_state = not usage.get(item["title"], False)
        usage[item["title"]] = new_state
        self._save_verify_usage(base, topic, usage)
        self._kin_mark_row_used(self.verify_list_tree, sel[0], self.verify_hide_used_var,
                                 self._verify_refresh_list, used=new_state)

    def _verify_delete_selected(self):
        """[Ver7.77 신규] "4)퍼플렉시티 자료검증(클로드)" 목록에 뜬
        원본자료(perplexity_answers) MD 파일을 여러 개 선택해 한번에
        삭제한다. 다른 세 탭(_perp_delete_selected/_web1st_delete_
        selected/_web2nd_delete_selected)과 동일한 이유·설계 - 질문DB는
        건드리지 않고 "이 단계"의 산출물만 지운다."""
        sel = self.verify_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "삭제할 항목을 먼저 선택하세요.")
            return
        indices = sorted((int(i) for i in sel), reverse=True)
        items = self._verify_list_cache['items']
        targets = [items[i] for i in indices if 0 <= i < len(items)]

        preview = "\n".join(f"  • {t['title']}" for t in targets[:10])
        if len(targets) > 10:
            preview += f"\n  … 외 {len(targets) - 10}건 더"

        if not messagebox.askyesno(
                "⚠️ 삭제 확인 (되돌릴 수 없음)",
                f"아래 {len(targets)}개 원본자료 파일을 영구 삭제합니다.\n"
                f"(질문DB 자체는 지워지지 않습니다 - 질문 삭제는 \"2)질문 상세분석\" 탭에서)\n\n"
                f"{preview}\n\n정말 삭제하시겠습니까?",
                icon="warning"):
            return

        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.verify_topic_var.get()
        usage = self._verify_list_cache['usage']
        deleted = 0
        for t in targets:
            try:
                if os.path.exists(t["file_path"]):
                    os.remove(t["file_path"])
                usage.pop(t["title"], None)
                deleted += 1
            except Exception as e:
                self.log(f"⚠️ 원본자료 파일 삭제 실패: {t['file_path']} ({e})")
        self._save_verify_usage(base, topic, usage)
        self.log(f"🗑️ 원본자료 삭제 완료: {deleted}개 ({topic})")
        self._verify_refresh_list()

    def _verify_update_char_count(self):
        text = self.verify_text.get("1.0", tk.END)
        korean = len(re.findall(r'[\uAC00-\uD7A3]', text))
        english = len(re.findall(r'[a-zA-Z0-9]', text))
        punct = len(re.findall(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', text))
        spaces = len(re.findall(r'[ \t]', text))
        total_excl = int(korean + english * 0.5 + punct)
        total_incl = int(korean + english * 0.5 + punct + spaces)
        self.verify_char_count_var.set(
            "한글 기준 글자수 │ 공백제외: {:,}자 │ 공백포함: {:,}자".format(total_excl, total_incl)
        )

    def _verify_save_result(self):
        """검증 결과 전체(검증요약+검증상세+검증된자료)에서 '## 검증된
        자료' 섹션만 뽑아 perplexity_[모델]_verified 폴더에 저장.
        [Ver7.10] 4)탭이 이 파일을 그대로 스캔해서 다음 단계로 넘겨받는다."""
        raw_text = self._strip_ai_ui_chrome(self.verify_text.get("1.0", tk.END).strip())
        if not raw_text:
            messagebox.showwarning("저장 오류", "저장할 검증 결과가 없습니다.")
            return
        item = self._verify_selected_item
        if not item or not item.get('title'):
            messagebox.showwarning(
                "저장 오류",
                "검증 대상 자료가 없습니다.\n"
                "왼쪽 목록에서 자료를 먼저 '복사'(또는 더블클릭)해서 대상으로 지정하세요."
            )
            return

        material = self._extract_verified_material(raw_text)

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        topic = self.verify_topic_var.get()
        model = self.verify_model_var.get()
        base = self.base_folder_var.get().strip() or self.base_folder
        save_dir = os.path.join(base, topic, today, "perplexity_{}_verified".format(model))
        os.makedirs(save_dir, exist_ok=True)

        filename = "{}.md".format(self.create_safe_filename(item['title']))
        save_path = os.path.join(save_dir, filename)

        if os.path.exists(save_path):
            if not messagebox.askyesno("덮어쓰기 확인",
                    "동일한 파일이 이미 존재합니다.\n\n{}\n\n덮어쓰시겠습니까?".format(filename)):
                return

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(material)
            self.log(f"✅ 교차검증 완료본 저장: {filename}")
            self.log(f"   -> {save_dir}")

            # [Ver7.17 추가] 실제 저장이 끝난 시점에만 "완료"로 기록한다.
            if item.get('title'):
                usage = self._verify_list_cache.get('usage', {})
                usage[item['title']] = True
                self._save_verify_usage(base, topic, usage)
                self._kin_mark_row_used(self.verify_list_tree, item.get('iid'),
                                         self.verify_hide_used_var, self._verify_refresh_list)

            self._verify_clear()
            self._refresh_web1st_counts()
        except Exception as e:
            self.log(f"❌ 교차검증 저장 실패: {e}")
            messagebox.showerror("저장 실패", f"파일 저장 중 오류 발생:\n{e}")

    def _verify_clear(self):
        self.verify_text.delete("1.0", tk.END)
        self.verify_char_count_var.set("한글 글자수: 0자")
        self.verify_target_var.set("(왼쪽에서 자료를 복사하면 여기에 표시됩니다)")
        self._verify_selected_item = None

    def create_step2_tab(self):
        """2단계: GPT 각색 탭 (재설계)"""
        step2_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(step2_frame, text="6)자동각색(API)")
        
        # ========================================
        # 0. 프롬프트 폴더 설정
        # ========================================
        prompt_folder_frame = ttk.LabelFrame(step2_frame, text="프롬프트 폴더", padding="8")
        prompt_folder_frame.grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky=(tk.W, tk.E))
        prompt_folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(prompt_folder_frame, text="폴더 경로:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(prompt_folder_frame, textvariable=self.prompt_folder_var).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(prompt_folder_frame, text="폴더 선택", command=self.select_prompt_folder).grid(
            row=0, column=2, padx=5
        )
        
        # ========================================
        # 1. 1차 각색 설정
        # ========================================
        first_frame = ttk.LabelFrame(step2_frame, text="1차 각색 설정", padding="10")
        first_frame.grid(row=1, column=0, columnspan=2, pady=(0, 8), sticky=(tk.W, tk.E))
        
        # 1차 모델 선택 + 버전 한 줄
        ttk.Label(first_frame, text="AI 모델:").grid(row=0, column=0, sticky=tk.W, pady=5)
        model_types_1st = ["GPT", "Gemini", "Claude"]
        model_1st_combo = ttk.Combobox(
            first_frame,
            textvariable=self.model_1st_type,
            values=model_types_1st,
            state="readonly",
            width=10
        )
        model_1st_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        model_1st_combo.bind('<<ComboboxSelected>>', self.on_1st_model_changed)
        self.model_1st_label = ttk.Label(first_frame, text="", foreground="gray")
        self.model_1st_label.grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # 1차 Claude 버전 콤보박스 (Claude 선택 시에만 표시)
        self.claude_model_1st_combo = ttk.Combobox(
            first_frame,
            textvariable=self.claude_model_1st,
            values=["claude-sonnet-4-5", "claude-haiku-4-5-20251001"],
            state="readonly",
            width=28
        )
        self.claude_model_1st_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.claude_model_1st_combo.grid_remove()  # 초기엔 숨김        
        
        
        # 1차 프롬프트
        ttk.Label(first_frame, text="프롬프트 파일:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(first_frame, textvariable=self.current_1st_prompt, state="readonly", width=100).grid(
            row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(first_frame, text="선택", command=lambda: self.select_prompt_file('1st')).grid(
            row=1, column=3, padx=5
        )
        
        # 1차 Temperature
        ttk.Label(first_frame, text="Temperature:").grid(row=2, column=0, sticky=tk.W, pady=5)
        temp_values = [f"{i/10:.1f}" for i in range(0, 11)]
        temp_1st_combo = ttk.Combobox(
            first_frame,
            textvariable=self.temperature_1st,
            values=temp_values,
            state="readonly",
            width=10
        )
        temp_1st_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        temp_1st_combo.bind('<<ComboboxSelected>>', lambda e: self.save_model_settings_to_config())
        ttk.Label(first_frame, text="(낮을수록 일관적, 높을수록 창의적)").grid(
            row=2, column=2, sticky=tk.W, padx=5
        )
        
        first_frame.columnconfigure(1, weight=0)
        first_frame.columnconfigure(2, weight=1)
        
        # ========================================
        # 2. 2차 각색 설정
        # ========================================
        second_frame = ttk.LabelFrame(step2_frame, text="2차 각색 설정", padding="10")
        second_frame.grid(row=2, column=0, columnspan=2, pady=(0, 8), sticky=(tk.W, tk.E))
        
        # 2차 모델 선택 + 버전 한 줄
        ttk.Label(second_frame, text="AI 모델:").grid(row=0, column=0, sticky=tk.W, pady=5)
        model_types = ["GPT", "Gemini", "Claude"]
        model_type_combo = ttk.Combobox(
            second_frame,
            textvariable=self.model_2nd_type,
            values=model_types,
            state="readonly",
            width=10
        )
        model_type_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        model_type_combo.bind('<<ComboboxSelected>>', self.on_2nd_model_changed)
        self.gpt_2nd_label = ttk.Label(second_frame, text="", foreground="gray")
        self.gpt_2nd_label.grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Claude 버전 선택 콤보박스 (Claude 선택 시에만 표시)
        self.claude_model_2nd_combo = ttk.Combobox(
            second_frame,
            textvariable=self.claude_model_2nd,
            values=["claude-sonnet-4-5", "claude-haiku-4-5-20251001"],
            state="readonly",
            width=28
        )
        self.claude_model_2nd_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.claude_model_2nd_combo.grid_remove()  # 초기엔 숨김


        # 2차 프롬프트
        ttk.Label(second_frame, text="프롬프트 파일:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(second_frame, textvariable=self.current_2nd_prompt, state="readonly", width=70).grid(
            row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(second_frame, text="선택", command=lambda: self.select_prompt_file('2nd')).grid(
            row=1, column=3, padx=5
        )
        
        # 2차 Temperature
        ttk.Label(second_frame, text="Temperature:").grid(row=2, column=0, sticky=tk.W, pady=5)
        temp_2nd_combo = ttk.Combobox(
            second_frame,
            textvariable=self.temperature_2nd,
            values=temp_values,
            state="readonly",
            width=10
        )
        temp_2nd_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        temp_2nd_combo.bind('<<ComboboxSelected>>', lambda e: self.save_model_settings_to_config())
        ttk.Label(second_frame, text="(낮을수록 일관적, 높을수록 창의적)").grid(
            row=2, column=2, sticky=tk.W, padx=5
        )
        
        second_frame.columnconfigure(1, weight=0)
        second_frame.columnconfigure(2, weight=1)
        
        # ========================================
        # 3. 실행 옵션
        # ========================================
        option_frame = ttk.LabelFrame(step2_frame, text="실행 옵션", padding="10")
        option_frame.grid(row=3, column=0, columnspan=2, pady=(0, 8), sticky=(tk.W, tk.E))
        
        ttk.Radiobutton(
            option_frame,
            text="1차 각색만 실행",
            variable=self.rewrite_mode,
            value="first_only",
            command=self.save_model_settings_to_config
        ).grid(row=0, column=0, sticky=tk.W, pady=3)
        
        ttk.Radiobutton(
            option_frame,
            text="2차 각색만 실행",
            variable=self.rewrite_mode,
            value="second_only",
            command=self.save_model_settings_to_config
        ).grid(row=1, column=0, sticky=tk.W, pady=3)
        
        ttk.Radiobutton(
            option_frame,
            text="1차+2차 각색 모두 실행",
            variable=self.rewrite_mode,
            value="both",
            command=self.save_model_settings_to_config
        ).grid(row=2, column=0, sticky=tk.W, pady=3)

        # ========================================
        # 4. 실행 버튼
        # ========================================
        button_frame = ttk.Frame(step2_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 5))
        
        self.start_rewrite_btn = ttk.Button(
            button_frame,
            text="각색 시작",
            command=self.start_gpt_rewrite
        )
        self.start_rewrite_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # ✅ 정지 버튼 추가
        self.stop_rewrite_btn = ttk.Button(
            button_frame,
            text="⏸️ 정지",
            command=self.stop_gpt_rewrite,
            state=tk.DISABLED
        )
        self.stop_rewrite_btn.pack(side=tk.LEFT, padx=(0, 10))


        # 초기 상태 설정
        self.update_model_1st_state()
        self.update_gpt_2nd_state()

    # 1차 모델 변경시 버전 표시 업데이트
    def on_1st_model_changed(self, event=None):
        """1차 모델 선택 변경시 버전 표시"""
        self.update_model_1st_state()
        self.save_model_settings_to_config()



    #############  아래 코드는 사용안하지만 삭제 보류 ##############################################
    #새로 만든 Naver_blog_kin_topic_classify_config 폴더 방식으로 전환했으니:
    #select_classifier_file → 더 이상 필요 없음
    #classifier_file_var → config 저장/로드에서 제거 가능
    #단, 당장 건드리면 config 저장/로드 부분도 같이 수정해야 함
    def select_classifier_file(self):
        """주제 분류 JSON 파일 선택"""
        initial_dir = self.prompt_folder_var.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = self.base_folder_var.get().strip() or "."
    
        file_path = filedialog.askopenfilename(
            title="주제 분류 파일 선택",
            initialdir=initial_dir,
            filetypes=[
                ("JSON 파일", "*.json"),
                ("모든 파일", "*.*")
            ]
        )
        if file_path:
            self.classifier_file_var.set(os.path.basename(file_path))
            self.save_model_settings_to_config()
            self.log(f"✅ 주제 분류 파일 설정: {os.path.basename(file_path)}")

    def update_model_1st_state(self):
        """1차 모델 타입에 따라 버전 표시 변경"""
        if self.model_1st_type.get() == "GPT":
            self.model_1st_label.config(foreground="gray", text="gpt-4.1-mini-2025-04-14 (고정)")
            self.model_1st_label.grid()
            self.claude_model_1st_combo.grid_remove()
        elif self.model_1st_type.get() == "Gemini":
            self.model_1st_label.config(foreground="gray", text="gemini-2.5-flash (자동)")
            self.model_1st_label.grid()
            self.claude_model_1st_combo.grid_remove()
        elif self.model_1st_type.get() == "Claude":
            self.claude_model_1st_combo.grid(row=0, column=2, sticky=tk.W, padx=5)
            self.model_1st_label.grid_remove()


    # 2차 모델 변경시 GPT 버전 활성화/비활성화
    def on_2nd_model_changed(self, event=None):
        """2차 모델 선택 변경시 GPT 버전 활성화/비활성화"""
        self.update_gpt_2nd_state()
        self.save_model_settings_to_config()

    def update_gpt_2nd_state(self):
        if self.model_2nd_type.get() == "GPT":
            self.gpt_2nd_label.config(foreground="gray", text="gpt-4.1-mini-2025-04-14 (고정)")
            self.gpt_2nd_label.grid()
            self.claude_model_2nd_combo.grid_remove()
        elif self.model_2nd_type.get() == "Gemini":
            self.gpt_2nd_label.config(foreground="gray", text="gemini-2.5-flash (자동)")
            self.gpt_2nd_label.grid()
            self.claude_model_2nd_combo.grid_remove()
        elif self.model_2nd_type.get() == "Claude":
            self.claude_model_2nd_combo.grid(row=0, column=2, sticky=tk.W, padx=5)  # label 자리에 배치
            self.gpt_2nd_label.grid_remove()   # label 숨김
    
    # ============================================================
    # 웹 2차 각색 결과 저장 탭 (반자동)
    # ============================================================
    # ──────────────────────────────────────────────────────
    # 2차 각색용 자료 선택 팝업 (프롬프트+자료 복사)
    # ──────────────────────────────────────────────────────
    def _get_prompt2nd_for_topic(self, topic):
        """매핑설정에서 해당 주제의 2차 프롬프트 내용을 가져온다 (주제 일치하는 첫번째 항목 사용)"""
        for key, mapping in getattr(self, 'kin_mappings', {}).items():
            if mapping.get('topic', '') == topic:
                prompt_filename = mapping.get('prompt_2nd', '')
                if not prompt_filename:
                    continue
                prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
                prompt_path = os.path.join(prompt_folder, prompt_filename)
                if os.path.exists(prompt_path):
                    try:
                        with open(prompt_path, 'r', encoding='utf-8') as f:
                            return f.read(), prompt_filename
                    except Exception:
                        continue
        return None, None

    # [Ver7.10 추가] 1차도 2차와 완전히 동일한 방식(매핑설정의 prompt_1st)으로 가져온다.
    def _get_prompt1st_for_topic(self, topic):
        """매핑설정에서 해당 주제의 1차 프롬프트 내용을 가져온다 (주제 일치하는 첫번째 항목 사용)"""
        for key, mapping in getattr(self, 'kin_mappings', {}).items():
            if mapping.get('topic', '') == topic:
                prompt_filename = mapping.get('prompt_1st', '')
                if not prompt_filename:
                    continue
                prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
                prompt_path = os.path.join(prompt_folder, prompt_filename)
                if os.path.exists(prompt_path):
                    try:
                        with open(prompt_path, 'r', encoding='utf-8') as f:
                            return f.read(), prompt_filename
                    except Exception:
                        continue
        return None, None

    # [Ver7.10 추가] 상단 배너용: 주제의 1차/2차 모델·프롬프트 파일명만 조회(내용은 읽지 않음)
    def _get_mapping_model_and_prompt(self, topic, stage='1st'):
        """kin_mappings에서 주제와 일치하는 첫 항목의 model_{stage}/prompt_{stage} 반환"""
        model_key = f'model_{stage}'
        prompt_key = f'prompt_{stage}'
        for mapping in getattr(self, 'kin_mappings', {}).values():
            if mapping.get('topic', '') == topic:
                model = mapping.get(model_key, '').strip()
                prompt = mapping.get(prompt_key, '').strip()
                if model or prompt:
                    return model, prompt
        return '', ''

    # [Ver7.10 추가] 상단 "주제 선택" 옆 배너 갱신 - 웹 작업 시 지금 주제에 어떤
    # 모델을 써야 하는지 한눈에 각인시켜준다(공간 문제로 모델명만, 프롬프트
    # 파일명은 넣지 않음). 주제가 바뀔 때마다 자동 호출됨.
    def _update_model_banner(self):
        if not hasattr(self, 'model_banner_label'):
            return
        topic = self.topic_var.get()
        m1_model, _ = self._get_mapping_model_and_prompt(topic, stage='1st')
        m2_model, _ = self._get_mapping_model_and_prompt(topic, stage='2nd')

        text = (f"📌 1차각색: {m1_model or '미지정'}  |  2차각색: {m2_model or '미지정'}, 각 모델별 웹에서 각색합니다.")
        self.model_banner_label.config(text=text)
        # [2026-09-27] 8)2차 각색 탭 주제 콤보 옆 모델 표시도 같은 시점에 갱신
        # (매핑설정 저장 직후에도 상단 배너와 항상 일치하도록)
        if hasattr(self, 'web2nd_model_var') and hasattr(self, 'web2nd_topic_var'):
            self._web2nd_auto_select_model()

    def _scan_1st_draft_items(self, base_folder, topic):
        """base/주제/날짜/perplexity_*_1st_draft/ 안의 1차 각색 결과 MD 파일들을 스캔"""
        items = []
        topic_path = os.path.join(base_folder, topic)
        if not os.path.exists(topic_path):
            return items

        for date_folder in os.listdir(topic_path):
            date_path = os.path.join(topic_path, date_folder)
            if not os.path.isdir(date_path):
                continue
            for folder_name in os.listdir(date_path):
                if not folder_name.endswith('_1st_draft'):
                    continue
                draft_path = os.path.join(date_path, folder_name)
                for filename in os.listdir(draft_path):
                    if filename.endswith('.md'):
                        file_path = os.path.join(draft_path, filename)
                        items.append({
                            "title": filename[:-3],
                            "date": date_folder,
                            "folder": folder_name,
                            "file_path": file_path,
                        })
        # [Ver7.10 수정] 날짜(일 단위) 문자열만으로 정렬하면 같은 날짜
        # 안에서는 OS가 반환하는 임의 순서를 따라 새 항목이 중간에
        # 끼어드는 것처럼 보였다. 실제 파일 수정시각 기준 오름차순으로
        # 바꿔 "새로 추가된 항목이 항상 맨 아래"가 되도록 한다.
        items.sort(key=lambda x: os.path.getmtime(x["file_path"]) if os.path.exists(x["file_path"]) else 0)
        return items

    def _get_1st_usage_path(self, base_folder, topic):
        return os.path.join(base_folder, topic, "2차각색_사용여부.json")

    def _load_1st_usage(self, base_folder, topic):
        path = self._get_1st_usage_path(base_folder, topic)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_1st_usage(self, base_folder, topic, usage):
        path = self._get_1st_usage_path(base_folder, topic)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

    def _scan_raw_material_items(self, base_folder, topic):
        """base/주제/날짜/perplexity_answers/ 안의 원본(2단계 산출물) MD
        파일들을 스캔한다 — 1차 각색의 입력 자료."""
        items = []
        topic_path = os.path.join(base_folder, topic)
        if not os.path.exists(topic_path):
            return items

        for date_folder in os.listdir(topic_path):
            date_path = os.path.join(topic_path, date_folder)
            if not os.path.isdir(date_path):
                continue
            answers_path = os.path.join(date_path, "perplexity_answers")
            if not os.path.isdir(answers_path):
                continue
            for filename in os.listdir(answers_path):
                if filename.endswith('.md'):
                    file_path = os.path.join(answers_path, filename)
                    items.append({
                        "title": filename[:-3],
                        "date": date_folder,
                        "folder": "perplexity_answers",
                        "file_path": file_path,
                    })
        # [Ver7.10 수정] 날짜(일 단위) 문자열만으로 정렬하면 같은 날짜
        # 안에서는 OS가 반환하는 임의 순서를 따라 새 항목이 중간에
        # 끼어드는 것처럼 보였다. 실제 파일 수정시각 기준 오름차순으로
        # 바꿔 "새로 추가된 항목이 항상 맨 아래"가 되도록 한다.
        items.sort(key=lambda x: os.path.getmtime(x["file_path"]) if os.path.exists(x["file_path"]) else 0)
        return items

    def _get_raw_usage_path(self, base_folder, topic):
        return os.path.join(base_folder, topic, "1차각색_사용여부.json")

    def _load_raw_usage(self, base_folder, topic):
        path = self._get_raw_usage_path(base_folder, topic)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_raw_usage(self, base_folder, topic, usage):
        path = self._get_raw_usage_path(base_folder, topic)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

    # ── [Ver7.10 추가] 2-1)퍼플렉시티 교차검증 탭용 ──
    # perplexity_answers(2단계 산출물)를 검증한 뒤 저장하는 곳(*_verified
    # 폴더)을 스캔한다. 4)1차각색(웹) 탭은 이제 perplexity_answers가 아니라
    # 여기(검증완료본)를 원자료로 쓴다.
    def _scan_verified_items(self, base_folder, topic):
        """base/주제/날짜/perplexity_[모델]_verified/ 안의 교차검증
        완료본 MD 파일들을 스캔한다 — 1차 각색의 새 입력 자료."""
        items = []
        topic_path = os.path.join(base_folder, topic)
        if not os.path.exists(topic_path):
            return items
        for date_folder in os.listdir(topic_path):
            date_path = os.path.join(topic_path, date_folder)
            if not os.path.isdir(date_path):
                continue
            for folder_name in os.listdir(date_path):
                if not folder_name.endswith('_verified'):
                    continue
                verified_path = os.path.join(date_path, folder_name)
                for filename in os.listdir(verified_path):
                    if filename.endswith('.md'):
                        file_path = os.path.join(verified_path, filename)
                        items.append({
                            "title": filename[:-3],
                            "date": date_folder,
                            "folder": folder_name,
                            "file_path": file_path,
                        })
        # [Ver7.10 수정] 날짜(일 단위) 문자열만으로 정렬하면 같은 날짜
        # 안에서는 OS가 반환하는 임의 순서를 따라 새 항목이 중간에
        # 끼어드는 것처럼 보였다. 실제 파일 수정시각 기준 오름차순으로
        # 바꿔 "새로 추가된 항목이 항상 맨 아래"가 되도록 한다.
        items.sort(key=lambda x: os.path.getmtime(x["file_path"]) if os.path.exists(x["file_path"]) else 0)
        return items

    def _get_verify_usage_path(self, base_folder, topic):
        return os.path.join(base_folder, topic, "교차검증_사용여부.json")

    def _load_verify_usage(self, base_folder, topic):
        path = self._get_verify_usage_path(base_folder, topic)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_verify_usage(self, base_folder, topic, usage):
        path = self._get_verify_usage_path(base_folder, topic)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

    # 교차검증 응답 전체(검증요약+검증상세+검증된자료)에서 "## 검증된
    # 자료" 섹션(=1차각색으로 넘길 최종본)만 뽑아낸다. 이 섹션은 프롬프트
    # 설계상 응답의 마지막 섹션이라 별도 종료 마커 없이 끝까지 잘라온다.
    # 못 찾으면(형식이 다른 경우) 안전하게 전체 텍스트를 그대로 반환한다.
    def _extract_verified_material(self, full_text):
        m = re.search(r'##\s*검증된\s*자료[^\n]*\n+(.*)', full_text, re.S)
        if m:
            return m.group(1).strip()
        return full_text.strip()



    def create_web_1st_tab(self):
        """4)1차각색(웹)→저장 — 5)클로드웹2차각색→저장과 동일한 컨셉.
        [Ver7.10 변경] 팝업으로 자료를 고르던 방식이 불편하다는 피드백에 따라
        좌(자료 목록·실시간 선택) / 우(붙여넣기·저장) 좌우분할 상시표시로 변경."""
        frame = ttk.Frame(self.notebook, padding="6")
        self.notebook.add(frame, text="7)1차 각색")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # ── 왼쪽: 1차 각색용 자료(2단계 원본 MD) 목록 ──
        left = ttk.Frame(paned, padding=(4, 4, 8, 4))
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)

        ttk.Label(left, text="📋 1차 각색용 자료 선택 (교차검증 완료본)", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        topic_row = ttk.Frame(left)
        topic_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(topic_row, text="주제:").pack(side=tk.LEFT, padx=(0, 5))

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        def count_1st_done(topic):
            """[Ver7.10 수정] (N개)는 각색 대상 원본 총개수가 아니라, 실제로 완료해서
            perplexity_[모델]_1st_draft 폴더에 저장해 둔 1차각색 결과 개수를 의미한다."""
            base = self.base_folder_var.get().strip() or self.base_folder
            return len(self._scan_1st_draft_items(base, topic))

        display_topics = [f"{t}  ({count_1st_done(t)}개)" for t in topics]
        self.web1st_topic_var = tk.StringVar(value=display_topics[0])
        self.web1st_combo = ttk.Combobox(
            topic_row, textvariable=self.web1st_topic_var,
            values=display_topics, state="readonly", width=50, height=11
        )
        self.web1st_combo.pack(side=tk.LEFT)

        # [추가] 이 탭 자체 주제 콤보박스 우측에도 각색모델 표시(상단 배너와
        # 동일한 진한적색). self.web1st_model_var(아래 "저장 모델" 라디오,
        # _web1st_auto_select_model로 주제 변경 시 자동 갱신)를 그대로 반영.
        self.web1st_model_display_var = tk.StringVar(value="각색모델:Claude")
        tk.Label(
            topic_row, textvariable=self.web1st_model_display_var,
            fg="Dark red", font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.web1st_hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_raw_material_picker', False))
        ttk.Checkbutton(left, text="사용한 자료 숨기기", variable=self.web1st_hide_used_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # [Ver7.10 추가] 날짜 필터(정확일치) + 총 개수 표시
        web1st_filter_row = ttk.Frame(left)
        web1st_filter_row.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(web1st_filter_row, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.web1st_date_var = tk.StringVar()
        web1st_date_entry = ttk.Entry(web1st_filter_row, textvariable=self.web1st_date_var, width=11)
        web1st_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        web1st_date_entry.bind("<Return>", lambda e: self._web1st_refresh_list())
        ttk.Button(web1st_filter_row, text="오늘",
                   command=lambda: (self.web1st_date_var.set(__import__('datetime').datetime.now().strftime("%Y-%m-%d")), self._web1st_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(web1st_filter_row, text="↺", width=3,
                   command=lambda: (self.web1st_date_var.set(""), self._web1st_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 8))
        self.web1st_list_count_var = tk.StringVar(value="")
        ttk.Label(web1st_filter_row, textvariable=self.web1st_list_count_var, foreground="navy").pack(side=tk.LEFT)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("used", "title", "date", "folder")
        self.web1st_list_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        self.web1st_list_tree.heading("used", text="사용")
        self.web1st_list_tree.heading("title", text="제목")
        self.web1st_list_tree.heading("date", text="날짜")
        self.web1st_list_tree.heading("folder", text="폴더")
        self.web1st_list_tree.column("used", width=40, anchor=tk.CENTER)
        self.web1st_list_tree.column("title", width=260)
        self.web1st_list_tree.column("date", width=80, anchor=tk.CENTER)
        self.web1st_list_tree.column("folder", width=140)
        self.web1st_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.web1st_list_tree.yview)
        self.web1st_list_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.web1st_list_tree.bind("<Double-1>", lambda e: self._web1st_copy_selected())

        self._web1st_list_cache = {'items': [], 'usage': {}}
        self._web1st_selected_item = None  # [Ver7.17 추가] 복사한 원본 자료를 저장 시점까지 기억(완료 판정용)

        list_btn_frame = ttk.Frame(left)
        list_btn_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame, text="📋 프롬프트+자료 복사",
                   command=self._web1st_copy_selected).pack(side=tk.LEFT, padx=(0, 4))
        # [Ver7.85 위치변경] 프롬프트만 복사 - 자료 선택 없이 현재 주제에 매핑된
        # 1차 프롬프트만 클립보드로 복사(프롬프트 자체를 확인/테스트하고 싶을 때 용도).
        # 다른 탭들(2/3/4탭)과 동일하게 "프롬프트만 복사"를 "자료만 복사"보다 앞에 배치.
        ttk.Button(list_btn_frame, text="프롬프트만 복사",
                   command=self._web1st_copy_prompt_only).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="자료만 복사",
                   command=self._web1st_copy_material_only).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame2 = ttk.Frame(left)
        list_btn_frame2.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame2, text="사용여부 토글",
                   command=self._web1st_toggle_used).pack(side=tk.LEFT, padx=(0, 4))
        # [Ver7.76 추가] "3)퍼플렉시티 수집"과 동일한 이유 - 이 단계 목록에
        # 뜬 "검증완료본" MD 파일을 여기서 바로 지울 수 있게 함(질문DB는
        # 건드리지 않음).
        ttk.Button(list_btn_frame2, text="🗑️ 선택 삭제",
                   command=self._web1st_delete_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🔄 새로고침",
                   command=self._web1st_refresh_list).pack(side=tk.LEFT, padx=(0, 4))

        guide_left = (
            "더블클릭 = 프롬프트+자료 복사.  저장 경로: 기본폴더/주제/오늘날짜/perplexity_[모델]_1st_draft/제목.md\n"
            "(여기 저장된 결과는 5)탭 왼쪽 목록에 그대로 나타납니다)"
        )
        ttk.Label(left, text=guide_left, justify=tk.LEFT, foreground="blue", wraplength=430).grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # ── 오른쪽: 붙여넣기 & 저장 ──
        right = ttk.Frame(paned, padding=(8, 4, 4, 4))
        paned.add(right, weight=3)
        right.columnconfigure(1, weight=1)

        ttk.Label(right, text="저장 모델:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.web1st_model_var = tk.StringVar(value="Claude")
        model_frame = ttk.Frame(right)
        model_frame.grid(row=0, column=1, sticky=tk.W, pady=4)
        for m in ["Claude", "GPT", "Gemini"]:
            ttk.Radiobutton(
                model_frame,
                text="perplexity_{}_1st_draft".format(m),
                variable=self.web1st_model_var,
                value=m,
                command=self._update_web1st_path_preview
            ).pack(side=tk.LEFT, padx=(0, 12))
        self.web1st_model_var.trace_add(
            "write", lambda *_: self.web1st_model_display_var.set(f"각색모델:{self.web1st_model_var.get()}"))

        ttk.Label(right, text="저장 방식:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.web1st_folder_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            right, text="제목별 폴더로 저장",
            variable=self.web1st_folder_mode_var,
            command=self._update_web1st_path_preview
        ).grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(right, text="마크다운\n붙여넣기:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(6, 0))
        self.web1st_text = scrolledtext.ScrolledText(right, height=24, wrap=tk.WORD)
        self.web1st_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(6, 0))
        self.web1st_text.bind("<<Modified>>", self._on_web1st_modified)

        preview_frame = ttk.LabelFrame(right, text="저장 정보 미리보기", padding="6")
        preview_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(8, 0))
        preview_frame.columnconfigure(1, weight=1)

        ttk.Label(preview_frame, text="추출 제목:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.web1st_title_var = tk.StringVar(value="(마크다운을 붙여넣으면 자동 추출됩니다)")
        ttk.Label(preview_frame, textvariable=self.web1st_title_var,
                  foreground="darkgreen").grid(row=0, column=1, sticky=tk.W)

        ttk.Label(preview_frame, text="파일명:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(3, 0))
        self.web1st_filename_var = tk.StringVar(value="")
        ttk.Label(preview_frame, textvariable=self.web1st_filename_var,
                  foreground="navy").grid(row=1, column=1, sticky=tk.W, pady=(3, 0))

        ttk.Label(preview_frame, text="저장 경로:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=(3, 0))
        self.web1st_path_var = tk.StringVar(value="")
        ttk.Label(preview_frame, textvariable=self.web1st_path_var,
                  foreground="gray", wraplength=480, justify=tk.LEFT).grid(
            row=2, column=1, sticky=tk.W, pady=(3, 0)
        )

        ttk.Label(preview_frame, text="글자수:").grid(row=3, column=0, sticky=tk.W, padx=(0, 8), pady=(3, 0))
        self.web1st_char_count_var = tk.StringVar(value="")
        ttk.Label(preview_frame, textvariable=self.web1st_char_count_var,
                  foreground="darkred", font=("", 9, "bold")).grid(row=3, column=1, sticky=tk.W, pady=(3, 0))

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky=tk.W)

        ttk.Button(btn_frame, text="제목 재추출",
                   command=self._extract_web1st_title).pack(side=tk.LEFT, padx=(0, 8))
        self.web1st_save_btn = ttk.Button(
            btn_frame, text="저장",
            command=self.save_web_1st_result, state=tk.DISABLED
        )
        self.web1st_save_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="내용 지우기",
                   command=self._clear_web1st).pack(side=tk.LEFT)

        # [Ver7.74 추가] 사용자 요청: 정식 중복체크(check_posting_duplicate)는
        # "8)2차 각색" 저장 직전에만 할 수 있는데, 그 시점까지 가려면 이미
        # 2차 각색(재작성) 비용/시간을 다 쓴 뒤라 너무 늦다는 문제 제기.
        # 여기 "7)1차 각색" 단계 - 아직 다듬어지기 전 초안이지만 제목·##
        # 소제목 구조는 이미 갖춰져 있으므로 extract_posting_core/
        # check_posting_duplicate 엔진을 그대로 재사용해 "미리, 참고용으로"
        # 겹치는 기존 글이 있는지 먼저 훑어볼 수 있게 함. 초안 단계라 소제목
        # 구성이 2차 각색 중 바뀔 수 있어 결과가 완전히 정확하진 않다는 점을
        # 버튼명/안내문에 명시("불완전 - 참고용"), 저장을 막는 강제 차단은
        # 하지 않는다(그건 여전히 2차 각색 저장 시 정식 체크의 역할).
        btn_frame_dup = ttk.Frame(right)
        btn_frame_dup.grid(row=5, column=0, columnspan=2, pady=(6, 0), sticky=tk.W)
        ttk.Button(btn_frame_dup, text="🔍 사전 중복체크(참고용)",
                   command=self._check_web1st_duplicate_pre).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(btn_frame_dup, text="기준(%):").pack(side=tk.LEFT, padx=(4, 2))
        self.web1st_dup_threshold_var = tk.IntVar(value=self.load_kin_ui_setting('web1st_dup_threshold', 70))
        ttk.Spinbox(btn_frame_dup, from_=30, to=100, increment=5, width=5,
                    textvariable=self.web1st_dup_threshold_var).pack(side=tk.LEFT)

        def _save_web1st_dup_threshold(*_):
            try:
                self.save_kin_ui_setting('web1st_dup_threshold', self.web1st_dup_threshold_var.get())
            except (tk.TclError, ValueError):
                pass
        self.web1st_dup_threshold_var.trace_add("write", _save_web1st_dup_threshold)

        ttk.Label(btn_frame_dup,
                  text="(초안 단계라 소제목이 2차 각색 중 바뀔 수 있어 완전하진 않습니다 - "
                       "최종 확인은 2차 각색 저장 시 정식 중복체크로)",
                  foreground="gray").pack(side=tk.LEFT, padx=(8, 0))

        self.web1st_dup_result_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.web1st_dup_result_var,
                  font=("", 9, "bold")).grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))

        self.web1st_topic_var.trace_add("write", lambda *_: self._update_web1st_path_preview())
        self.web1st_topic_var.trace_add("write", lambda *_: self._web1st_refresh_list())
        # [Ver7.10 추가] 주제 매핑설정에 등록된 1차 모델이 있으면 저장 모델
        # 라디오버튼을 자동으로 그 값으로 맞춘다(_get_mapping_model_and_prompt
        # 는 6)자동각색 탭 배너에도 쓰는 동일 로직 재사용).
        self.web1st_topic_var.trace_add("write", lambda *_: self._web1st_auto_select_model())
        self.web1st_hide_used_var.trace_add("write", lambda *_: self._web1st_refresh_list())
        self.web1st_hide_used_var.trace_add(
            "write", lambda *_: self.save_kin_ui_setting('hide_used_raw_material_picker', self.web1st_hide_used_var.get()))

        self._web1st_refresh_list()
        self._web1st_auto_select_model()

    # [Ver7.10 추가] 현재 주제의 매핑설정(⚙️ 주제 매핑설정)에 등록된 1차
    # 모델이 있으면 "저장 모델" 라디오버튼을 자동으로 맞춰준다. 등록된
    # 매핑이 없으면 사용자가 마지막으로 고른 값을 그대로 둔다.
    def _web1st_auto_select_model(self):
        if not hasattr(self, 'web1st_model_var'):
            return
        topic = self.web1st_topic_var.get().split('  (')[0]
        model, _ = self._get_mapping_model_and_prompt(topic, stage='1st')
        if model in ("Claude", "GPT", "Gemini"):
            self.web1st_model_var.set(model)

    # ── [Ver7.10 추가] 4)탭 왼쪽 목록(좌우분할)용 헬퍼 — open_raw_material_picker
    # 팝업의 로직을 그대로 상시표시 목록용으로 옮긴 것 ──
    def _web1st_refresh_list(self):
        if not hasattr(self, 'web1st_list_tree'):
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.web1st_topic_var.get().split('  (')[0]
        self.web1st_list_tree.delete(*self.web1st_list_tree.get_children())
        items = self._scan_verified_items(base, topic)
        usage = self._load_raw_usage(base, topic)
        self._web1st_list_cache['items'] = items
        self._web1st_list_cache['usage'] = usage
        date_filter = self.web1st_date_var.get().strip() if hasattr(self, 'web1st_date_var') else ""
        shown = 0
        for i, item in enumerate(items):
            used = usage.get(item["title"], False)
            if self.web1st_hide_used_var.get() and used:
                continue
            if date_filter and item["date"] != date_filter:
                continue
            self.web1st_list_tree.insert("", tk.END, iid=str(i), values=(
                "✅" if used else "", item["title"], item["date"], item["folder"]
            ))
            shown += 1

        if hasattr(self, 'web1st_list_count_var'):
            total = len(items)
            if date_filter:
                self.web1st_list_count_var.set(f"검색결과 {shown}개 / 전체 {total}개")
            else:
                self.web1st_list_count_var.set(f"총 {total}개")

    def _web1st_copy_selected(self):
        sel = self.web1st_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 자료를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._web1st_list_cache['items'][idx]
        topic = self.web1st_topic_var.get().split('  (')[0]
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                material = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        prompt_text, prompt_filename = self._get_prompt1st_for_topic(topic)
        if not prompt_text:
            messagebox.showwarning(
                "1차 프롬프트 없음",
                f"'{topic}' 주제에 등록된 1차 프롬프트가 없습니다.\n"
                f"'⚙️ 매핑 설정'에서 먼저 등록하세요."
            )
            return
        content = (
            f"{prompt_text}\n\n"
            f"───────────────────\n"
            f"[각색할 자료]\n"
            f"{material}\n"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        # [Ver7.17 수정] 복사 시점엔 usage를 바로 True로 기록하지 않는다.
        # 1차 각색은 AI가 새 제목을 지어내므로 저장 결과 파일명으로는
        # 원본 자료를 역추적할 수 없다 — 그래서 "저장" 버튼(save_web_1st_result)이
        # 성공했을 때, 여기서 기억해 둔 원본 자료 제목을 완료 처리한다.
        # 목록은 그 행의 셀만 "📋(진행중)"으로 바꿔 선택/포커스를 유지한다.
        self._web1st_selected_item = {'title': item['title'], 'iid': sel[0]}
        self._kin_mark_row_in_progress(self.web1st_list_tree, sel[0])
        self.log(f"📋 1차 각색용 자료 복사 완료 (프롬프트: {prompt_filename}): {item['title']}")

    def _web1st_copy_material_only(self):
        sel = self.web1st_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 자료를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._web1st_list_cache['items'][idx]
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                material = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(material)
        # [Ver7.17 추가] "자료만 복사"만 쓰더라도 완료 판정이 정상 동작하도록
        # 작업 대상을 함께 기억해두고, 그 행을 "📋(진행중)"으로 표시한다.
        self._web1st_selected_item = {'title': item['title'], 'iid': sel[0]}
        self._kin_mark_row_in_progress(self.web1st_list_tree, sel[0])
        self.log(f"📋 1차용 자료만 복사: {item['title']}")

    def _web1st_copy_prompt_only(self):
        """[Ver7.44 신규] 자료(목록 선택) 없이, 현재 선택된 주제에 매핑된
        1차 프롬프트 텍스트만 클립보드에 복사한다. 프롬프트 내용만 따로
        확인하거나 다른 곳에 붙여 테스트하고 싶을 때 쓰는 용도."""
        topic = self.web1st_topic_var.get().split('  (')[0]
        prompt_text, prompt_filename = self._get_prompt1st_for_topic(topic)
        if not prompt_text:
            messagebox.showwarning(
                "1차 프롬프트 없음",
                f"'{topic}' 주제에 등록된 1차 프롬프트가 없습니다.\n"
                f"'⚙️ 매핑 설정'에서 먼저 등록하세요."
            )
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_PROMPT_CONTINUITY_NOTICE + prompt_text)
        self.log(f"📋 1차 프롬프트만 복사: {prompt_filename} ({topic})")
        messagebox.showinfo("복사 완료", "프롬프트만 클립보드에 복사되었습니다.")

    def _web1st_toggle_used(self):
        sel = self.web1st_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._web1st_list_cache['items'][idx]
        topic = self.web1st_topic_var.get().split('  (')[0]
        base = self.base_folder_var.get().strip() or self.base_folder
        usage = self._web1st_list_cache['usage']
        new_state = not usage.get(item["title"], False)
        usage[item["title"]] = new_state
        self._save_raw_usage(base, topic, usage)
        self._kin_mark_row_used(self.web1st_list_tree, sel[0], self.web1st_hide_used_var,
                                 self._web1st_refresh_list, used=new_state)

    def _web1st_delete_selected(self):
        """[Ver7.76 신규] "7)1차 각색" 목록에 뜬 검증완료본(perplexity_*_
        verified) MD 파일을 여러 개 선택해 한번에 삭제한다. "3)퍼플렉시티
        수집"의 _perp_delete_selected와 동일한 이유·설계(질문DB는 건드리지
        않고 "이 단계"의 산출물만 지움)."""
        sel = self.web1st_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "삭제할 항목을 먼저 선택하세요.")
            return
        indices = sorted((int(i) for i in sel), reverse=True)
        items = self._web1st_list_cache['items']
        targets = [items[i] for i in indices if 0 <= i < len(items)]

        preview = "\n".join(f"  • {t['title']}" for t in targets[:10])
        if len(targets) > 10:
            preview += f"\n  … 외 {len(targets) - 10}건 더"

        if not messagebox.askyesno(
                "⚠️ 삭제 확인 (되돌릴 수 없음)",
                f"아래 {len(targets)}개 검증완료본 파일을 영구 삭제합니다.\n"
                f"(질문DB 자체는 지워지지 않습니다 - 질문 삭제는 \"2)질문 상세분석\" 탭에서)\n\n"
                f"{preview}\n\n정말 삭제하시겠습니까?",
                icon="warning"):
            return

        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.web1st_topic_var.get().split('  (')[0]
        usage = self._web1st_list_cache['usage']
        deleted = 0
        for t in targets:
            try:
                if os.path.exists(t["file_path"]):
                    os.remove(t["file_path"])
                usage.pop(t["title"], None)
                deleted += 1
            except Exception as e:
                self.log(f"⚠️ 검증완료본 파일 삭제 실패: {t['file_path']} ({e})")
        self._save_raw_usage(base, topic, usage)
        self.log(f"🗑️ 검증완료본 삭제 완료: {deleted}개 ({topic})")
        self._web1st_refresh_list()


    def _on_web1st_modified(self, event=None):
        if self.web1st_text.edit_modified():
            self._extract_web1st_title()
            self._update_web1st_char_count()
            self.web1st_text.edit_modified(False)

    def _update_web1st_char_count(self):
        text = self.web1st_text.get("1.0", tk.END)
        korean = len(re.findall(r'[\uAC00-\uD7A3]', text))
        english = len(re.findall(r'[a-zA-Z0-9]', text))
        punct = len(re.findall(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', text))
        spaces = len(re.findall(r'[ \t]', text))
        total_excl = int(korean + english * 0.5 + punct)
        total_incl = int(korean + english * 0.5 + punct + spaces)
        self.web1st_char_count_var.set(
            "한글 기준 글자수 │ 공백제외: {:,}자 │ 공백포함: {:,}자".format(total_excl, total_incl)
        )

    def _extract_web1st_title(self):
        text = self.web1st_text.get("1.0", tk.END).strip()

        if not text:
            self.web1st_title_var.set("(마크다운을 붙여넣으면 자동 추출됩니다)")
            self.web1st_filename_var.set("")
            self.web1st_path_var.set("")
            self.web1st_save_btn.config(state=tk.DISABLED)
            return

        title = None
        for line in text.split('\n'):
            s = line.strip()
            if s.startswith('# ') and not s.startswith('## '):
                title = s[2:].strip()
                break

        if not title or len(title) < 3:
            self.web1st_title_var.set("H1 제목을 찾을 수 없습니다 (첫 줄이  # 제목  형식인지 확인)")
            self.web1st_filename_var.set("")
            self.web1st_path_var.set("")
            self.web1st_save_btn.config(state=tk.DISABLED)
            return

        filename = "{}.md".format(self.create_safe_filename(title))
        self.web1st_title_var.set(title)
        self.web1st_filename_var.set(filename)
        self._update_web1st_path_preview()
        self.web1st_save_btn.config(state=tk.NORMAL)

    def _check_web1st_duplicate_pre(self):
        """[Ver7.74 신규] "8)2차 각색"의 정식 중복체크(_check_web2nd_duplicate)와
        동일한 엔진(extract_posting_core/check_posting_duplicate)을 재사용해,
        아직 초안 단계인 "7)1차 각색" 결과물을 상대로 미리 훑어보는 참고용
        체크. 2차 각색까지 다 마친 뒤에야 겹치는 글이었다는 걸 알게 되면
        그 사이 들인 시간/비용이 아까우므로, 최소한 "이미 비슷한 글이
        있다"는 뻔한 경우는 여기서 먼저 걸러내자는 취지.

        초안 단계라 소제목 구성이 2차 각색 과정에서 바뀔 수 있어 정확도가
        정식 체크보다 낮다 - 그래서 저장을 막는 강제 차단은 하지 않고
        결과만 보여준다(강제 차단은 여전히 2차 각색 저장 시 정식 체크의
        역할). 팝업은 "8)2차 각색"이 이미 쓰는 _show_web2nd_dup_result를
        그대로 재사용한다(내부적으로 self.web2nd_* 상태를 참조하지 않고
        전달받은 results/threshold만 그리므로 탭이 달라도 문제 없음)."""
        text = self.web1st_text.get("1.0", tk.END).strip()
        title = self.web1st_title_var.get()
        if not text:
            messagebox.showwarning("알림", "먼저 초안 마크다운을 붙여넣으세요.")
            return
        if not title or title.startswith("(") or title.startswith("H1"):
            messagebox.showwarning("알림", "제목을 먼저 추출하세요(제목 재추출 버튼).")
            return

        topic = self.web1st_topic_var.get().split('  (')[0]
        base = self.base_folder_var.get().strip() or self.base_folder
        posting_db_path = get_posting_db_path(base, topic)
        posting_records = load_json_db(posting_db_path)
        new_p_core = extract_posting_core(text, title)
        try:
            threshold = int(self.web1st_dup_threshold_var.get())
            threshold = min(100, max(30, threshold))
        except (tk.TclError, ValueError):
            threshold = 70
        results = check_posting_duplicate(new_p_core, posting_records, danger=threshold)

        if not results:
            self.web1st_dup_result_var.set("✅ (사전체크) 중복 없음 — 다만 초안 단계라 확정은 아닙니다")
        else:
            danger_count = sum(1 for r in results if r["danger"])
            if danger_count:
                self.web1st_dup_result_var.set(
                    f"⛔ (사전체크) 위험 {danger_count}건 포함(차단기준 {threshold}%↑) — 2차 각색 전에 먼저 확인하세요 (아래 팝업)")
            else:
                self.web1st_dup_result_var.set(
                    f"⚠️ (사전체크) 주의 {len(results)}건 발견 — 참고만 하고 계속 진행 가능")
        self._show_web2nd_dup_result(results, threshold)

    def _update_web1st_path_preview(self):
        filename = self.web1st_filename_var.get()
        if not filename:
            return
        from datetime import datetime
        today    = datetime.now().strftime("%Y-%m-%d")
        topic    = self.web1st_topic_var.get().split('  (')[0]
        model    = self.web1st_model_var.get()
        base     = self.base_folder_var.get().strip() or self.base_folder
        save_dir = os.path.join(base, topic, today, "perplexity_{}_1st_draft".format(model))
        if self.web1st_folder_mode_var.get():
            title_folder = filename[:-3] if filename.endswith('.md') else filename
            save_dir = os.path.join(save_dir, title_folder)
        self.web1st_path_var.set(os.path.join(save_dir, filename))

    def _refresh_web1st_counts(self):
        """주제 콤보박스의 (N개) 표시를 새로고침한다.
        [Ver7.10 수정] N은 각색 대상 원본 총개수가 아니라, 실제로 완료해서
        perplexity_[모델]_1st_draft 폴더에 저장해 둔 1차각색 결과 개수다."""
        if not hasattr(self, 'web1st_combo'):
            return
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        base = self.base_folder_var.get().strip() or self.base_folder
        current_topic = self.web1st_topic_var.get().split('  (')[0]
        display_topics = [f"{t}  ({len(self._scan_1st_draft_items(base, t))}개)" for t in topics]
        self.web1st_combo['values'] = display_topics
        for dt in display_topics:
            if dt.startswith(current_topic + "  ("):
                self.web1st_topic_var.set(dt)
                break

    def save_web_1st_result(self):
        """웹 1차 각색 결과를 perplexity_{모델}_1st_draft 폴더에 저장한다.
        1차는 최종 포스팅이 아니라 초안이라, 2차 저장과 달리 포스팅DB
        중복체크는 하지 않는다."""
        text     = self._strip_ai_ui_chrome(self.web1st_text.get("1.0", tk.END).strip())
        filename = self.web1st_filename_var.get()

        if not text or not filename:
            messagebox.showwarning("저장 오류", "저장할 내용 또는 파일명이 없습니다.")
            return

        from datetime import datetime
        today    = datetime.now().strftime("%Y-%m-%d")
        topic    = self.web1st_topic_var.get().split('  (')[0]
        model    = self.web1st_model_var.get()
        base     = self.base_folder_var.get().strip() or self.base_folder
        save_dir = os.path.join(base, topic, today, "perplexity_{}_1st_draft".format(model))
        if self.web1st_folder_mode_var.get():
            title_folder = filename[:-3] if filename.endswith('.md') else filename
            save_dir = os.path.join(save_dir, title_folder)

        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        if os.path.exists(save_path):
            if not messagebox.askyesno("덮어쓰기 확인",
                    "동일한 파일이 이미 존재합니다.\n\n{}\n\n덮어쓰시겠습니까?".format(filename)):
                return

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

            self.log("웹1차 저장: {}".format(filename))
            self.log("   -> {}".format(save_dir))

            # [Ver7.17 추가] 실제 저장이 끝난 시점에만, 복사해 뒀던 원본
            # 자료를 "완료"로 기록한다(1차 각색은 AI가 새 제목을 지어내
            # 저장 결과 파일명으로는 원본을 역추적할 수 없어, 복사 시점에
            # 기억해 둔 원본 제목을 그대로 쓴다).
            target = getattr(self, '_web1st_selected_item', None)
            if target and target.get('title'):
                usage = self._web1st_list_cache.get('usage', {})
                usage[target['title']] = True
                self._save_raw_usage(base, topic, usage)
                self._kin_mark_row_used(self.web1st_list_tree, target.get('iid'),
                                         self.web1st_hide_used_var, self._web1st_refresh_list)

            self._refresh_web1st_counts()
            self._clear_web1st()

        except Exception as e:
            self.log("웹1차 저장 실패: {}".format(str(e)))
            messagebox.showerror("저장 실패", "파일 저장 중 오류 발생:\n{}".format(str(e)))

    def _clear_web1st(self):
        self.web1st_text.delete("1.0", tk.END)
        self.web1st_title_var.set("(마크다운을 붙여넣으면 자동 추출됩니다)")
        self.web1st_filename_var.set("")
        self.web1st_path_var.set("")
        self.web1st_char_count_var.set("")
        self.web1st_save_btn.config(state=tk.DISABLED)
        self._web1st_selected_item = None  # [Ver7.17 추가]

    def create_web_2nd_tab(self):
        """2.5단계: 웹 2차 각색 결과 저장 탭
        [Ver7.10 변경] 팝업으로 자료를 고르던 방식이 불편하다는 피드백에 따라
        좌(자료 목록·실시간 선택) / 우(붙여넣기·저장) 좌우분할 상시표시로 변경."""
        frame = ttk.Frame(self.notebook, padding="6")
        self.notebook.add(frame, text="8)2차 각색")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # ── 왼쪽: 2차 각색용 자료(1차 결과물) 목록 ──
        left = ttk.Frame(paned, padding=(4, 4, 8, 4))
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)

        ttk.Label(left, text="📋 2차 각색용 자료 선택 (1차 결과물)", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        topic_row = ttk.Frame(left)
        topic_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(topic_row, text="주제:").pack(side=tk.LEFT, padx=(0, 5))

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        # 주제별 MD 파일 개수 카운트 (완료된 2차각색 결과 기준 - final_articles)
        def count_md_files(topic):
            base = self.base_folder_var.get().strip() or self.base_folder
            topic_path = os.path.join(base, topic)
            if not os.path.exists(topic_path):
                return 0
            count = 0
            for date_dir in os.listdir(topic_path):
                date_path = os.path.join(topic_path, date_dir)
                if not os.path.isdir(date_path):
                    continue
                for folder in os.listdir(date_path):
                    if "final_articles" in folder:
                        final_path = os.path.join(date_path, folder)
                        for entry in os.listdir(final_path):
                            entry_path = os.path.join(final_path, entry)
                            if entry.endswith('.md') and os.path.isfile(entry_path):
                                count += 1
                            elif os.path.isdir(entry_path):
                                count += len([f for f in os.listdir(entry_path) if f.endswith('.md')])
            return count

        display_topics = [f"{t}  ({count_md_files(t)}개)" for t in topics]
        self.web2nd_topic_var = tk.StringVar(value=display_topics[0])
        self.web2nd_combo = ttk.Combobox(
            topic_row, textvariable=self.web2nd_topic_var,
            values=display_topics, state="readonly", width=50, height=11
        )
        self.web2nd_combo.pack(side=tk.LEFT)

        # [추가] 이 탭 자체 주제 콤보박스 우측에도 각색모델 표시(상단 배너와
        # 동일한 진한적색). self.web2nd_model_var(아래 "저장 모델" 라디오,
        # _web2nd_auto_select_model로 주제 변경 시 자동 갱신)를 그대로 반영.
        self.web2nd_model_display_var = tk.StringVar(value="각색모델:Claude")
        tk.Label(
            topic_row, textvariable=self.web2nd_model_display_var,
            fg="Dark red", font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.web2nd_hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_1st_draft_picker', False))
        ttk.Checkbutton(left, text="사용한 자료 숨기기", variable=self.web2nd_hide_used_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # [Ver7.10 추가] 날짜 필터(정확일치) + 총 개수 표시
        web2nd_filter_row = ttk.Frame(left)
        web2nd_filter_row.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(web2nd_filter_row, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.web2nd_date_var = tk.StringVar()
        web2nd_date_entry = ttk.Entry(web2nd_filter_row, textvariable=self.web2nd_date_var, width=11)
        web2nd_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        web2nd_date_entry.bind("<Return>", lambda e: self._web2nd_refresh_list())
        ttk.Button(web2nd_filter_row, text="오늘",
                   command=lambda: (self.web2nd_date_var.set(__import__('datetime').datetime.now().strftime("%Y-%m-%d")), self._web2nd_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(web2nd_filter_row, text="↺", width=3,
                   command=lambda: (self.web2nd_date_var.set(""), self._web2nd_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 8))
        self.web2nd_list_count_var = tk.StringVar(value="")
        ttk.Label(web2nd_filter_row, textvariable=self.web2nd_list_count_var, foreground="navy").pack(side=tk.LEFT)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("used", "title", "date", "folder")
        # [2026-09-27 3차] 우측 패널의 "대안 후보 확정" 영역이 삭제되면서
        # 화면 전체 높이가 줄어든 만큼, 좌측 트리뷰 높이를 14→20으로 늘렸다
        # (사용자 요청: "스크롤이 안되는 범위에서 최대로" - 트리뷰 자체는
        # 아래 list_scroll로 내부 스크롤되므로 화면에 안 잘리는 선에서
        # 최대한 키운 값. 실제로 잘려 보이면 이 숫자만 다시 낮추면 된다).
        self.web2nd_list_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        self.web2nd_list_tree.heading("used", text="사용")
        self.web2nd_list_tree.heading("title", text="제목")
        self.web2nd_list_tree.heading("date", text="날짜")
        self.web2nd_list_tree.heading("folder", text="폴더(모델)")
        self.web2nd_list_tree.column("used", width=40, anchor=tk.CENTER)
        self.web2nd_list_tree.column("title", width=260)
        self.web2nd_list_tree.column("date", width=80, anchor=tk.CENTER)
        self.web2nd_list_tree.column("folder", width=140)
        self.web2nd_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.web2nd_list_tree.yview)
        self.web2nd_list_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.web2nd_list_tree.bind("<Double-1>", lambda e: self._web2nd_copy_selected())
        # [Ver9.08 추가] 트리뷰 자체 휠 스크롤을 명시적으로 바인딩하고 반드시
        # "break"를 반환한다. Tk는 위젯 자체(인스턴스) 바인딩 → 클래스
        # 바인딩 → 전역("all") 바인딩 순으로 같은 이벤트를 계속 전달하는데,
        # break 없이 두면 트리뷰 위에서 휠을 굴려도 그 이벤트가 계속 흘러가
        # 우측 패널 캔버스(right_canvas)까지 같이 스크롤시키는 간섭이
        # 있었다("트리뷰 스크롤할 땐 우측 스크롤이 움직이지 않게 해" 요청).
        # break로 이 위젯 선에서 이벤트를 확실히 끊어 독립적으로만 움직이게 함.
        def _web2nd_tree_on_wheel(event):
            if getattr(event, 'num', None) == 4:
                self.web2nd_list_tree.yview_scroll(-1, "units")
            elif getattr(event, 'num', None) == 5:
                self.web2nd_list_tree.yview_scroll(1, "units")
            else:
                self.web2nd_list_tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        self.web2nd_list_tree.bind("<MouseWheel>", _web2nd_tree_on_wheel)
        self.web2nd_list_tree.bind("<Button-4>", _web2nd_tree_on_wheel)
        self.web2nd_list_tree.bind("<Button-5>", _web2nd_tree_on_wheel)

        self._web2nd_list_cache = {'items': [], 'usage': {}}
        self._web2nd_selected_item = None  # [Ver7.17 추가] 복사한 원본 자료를 저장 시점까지 기억(완료 판정용)

        list_btn_frame = ttk.Frame(left)
        list_btn_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame, text="📋 프롬프트+자료 복사",
                   command=self._web2nd_copy_selected).pack(side=tk.LEFT, padx=(0, 4))
        # [Ver7.85 위치변경] 프롬프트만 복사 - 자료 선택 없이 현재 주제에 매핑된
        # 2차 프롬프트만 클립보드로 복사(프롬프트 자체를 확인/테스트하고 싶을 때 용도).
        # 다른 탭들(2/3/4탭)과 동일하게 "프롬프트만 복사"를 "자료만 복사"보다 앞에 배치.
        ttk.Button(list_btn_frame, text="프롬프트만 복사",
                   command=self._web2nd_copy_prompt_only).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="자료만 복사",
                   command=self._web2nd_copy_material_only).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame2 = ttk.Frame(left)
        list_btn_frame2.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame2, text="사용여부 토글",
                   command=self._web2nd_toggle_used).pack(side=tk.LEFT, padx=(0, 4))
        # [Ver7.76 추가] 위 두 탭과 동일한 이유 - 이 단계 목록에 뜬
        # "1차 각색본" MD 파일을 여기서 바로 지울 수 있게 함(질문DB는
        # 건드리지 않음).
        ttk.Button(list_btn_frame2, text="🗑️ 선택 삭제",
                   command=self._web2nd_delete_selected).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🔄 새로고침",
                   command=self._web2nd_refresh_list).pack(side=tk.LEFT, padx=(0, 4))

        guide_left = "더블클릭 = 프롬프트+자료 복사.  저장 경로: 기본폴더/주제/오늘날짜/perplexity_[모델]_final_articles/제목.md"
        ttk.Label(left, text=guide_left, justify=tk.LEFT, foreground="blue", wraplength=430).grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # ── 오른쪽: 붙여넣기 & 저장 ──
        # [2026-09-27 3차] "대안 후보 확정" 기능을 삭제하면서 우측 패널의
        # 내용 높이가 줄어 더 이상 세로 스크롤이 필요 없어졌다(사용자
        # 요청) - 캔버스+스크롤바로 감싸던 바깥 껍데기(right_outer/
        # right_canvas/right_scroll 및 관련 Configure 핸들러·마우스휠
        # 재귀 바인딩)를 전부 없애고, `right`를 paned에 바로 붙인다.
        right = ttk.Frame(paned, padding=(8, 4, 4, 4))
        paned.add(right, weight=3)
        right.columnconfigure(1, weight=1)

        # [2026-09-16 4차] 우측 패널 전체를 스크롤 없이 한 화면에 담고 싶다는
        # 요청에 따라, 각 행 사이 pady(세로 여백)를 전반적으로 줄였다 - 보기에
        # 답답하지 않은 선에서 조금씩만(4→2~3, 6→4, 8→5~6, 12→8 등) 줄여서
        # 스크롤 영역(scrollregion) 총 높이를 낮췄다.
        # 저장 모델 선택
        ttk.Label(right, text="저장 모델:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.web2nd_model_var = tk.StringVar(value="Claude")
        model_frame = ttk.Frame(right)
        model_frame.grid(row=0, column=1, sticky=tk.W, pady=2)
        for m in ["Claude", "GPT", "Gemini"]:
            ttk.Radiobutton(
                model_frame,
                text="perplexity_{}_final_articles".format(m),
                variable=self.web2nd_model_var,
                value=m,
                command=self._update_web2nd_path_preview
            ).pack(side=tk.LEFT, padx=(0, 12))

        # 저장 방식 선택 (평문 파일 / 제목별 폴더 - 반자동 방식과 동일)
        ttk.Label(right, text="저장 방식:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.web2nd_folder_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            right, text="제목별 폴더로 저장 (썸네일·소제목 이미지를 같은 폴더에 넣을 수 있음)",
            variable=self.web2nd_folder_mode_var,
            command=self._update_web2nd_path_preview
        ).grid(row=1, column=1, sticky=tk.W, pady=2)

        # 마크다운 붙여넣기 영역
        ttk.Label(right, text="마크다운\n붙여넣기:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(4, 0))
        self.web2nd_text = scrolledtext.ScrolledText(right, height=32, wrap=tk.WORD)
        self.web2nd_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(4, 0))
        self.web2nd_text.bind("<<Modified>>", self._on_web2nd_modified)
        # [Ver7.13, 정책뉴스 TAB3 참조] Ctrl+V·마우스 우클릭 붙여넣기(가상
        # 이벤트 <<Paste>>) 완료 직후 중복체크를 자동 실행한다. <<Modified>>는
        # 타이핑 등 모든 변경에 반응해 여기 얹으면 팝업이 계속 뜨므로, 붙여넣기
        # 전용 이벤트에만 별도로 건다. after(50)은 <<Modified>> 핸들러가 먼저
        # 돌아 제목 추출(web2nd_title_var)이 끝난 뒤 중복체크가 실행되게 하는
        # 지연시간이다.
        self.web2nd_text.bind("<<Paste>>", lambda e: self.root.after(50, self._auto_check_web2nd_duplicate))

        # 미리보기 영역
        # [2026-09-16 재설계] 화면 최적화 - 추출 제목/파일명/저장 경로는
        # 화면에서 뺐다. 세 값 다 실제 저장·중복체크·폴더열기 로직에서
        # 계속 내부적으로 쓰이므로 변수(web2nd_title_var/filename_var/
        # path_var) 자체는 그대로 두고 계속 갱신하되, 화면에는 더 이상
        # Label로 표시하지 않는다 - 제목은 아래 "제목 확정" 절차에서
        # 다시 정해지고 확정 시 별도 메시지로 보여지므로 미리보기 단계의
        # 제목 표시는 중복이고, 파일명/경로는 저장 직전에나 의미 있는
        # 기계적 정보라 "📁 저장폴더 열기"로 필요할 때 확인하면 충분하다는
        # 판단(사용자 확인). 화면에는 글자수만 남긴다.
        preview_frame = ttk.LabelFrame(right, text="저장 정보 미리보기", padding=(6, 3, 6, 3))
        preview_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        preview_frame.columnconfigure(1, weight=1)

        self.web2nd_title_var = tk.StringVar(value="(마크다운을 붙여넣으면 자동 추출됩니다)")
        self.web2nd_filename_var = tk.StringVar(value="")
        self.web2nd_path_var = tk.StringVar(value="")

        ttk.Label(preview_frame, text="글자수:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.web2nd_char_count_var = tk.StringVar(value="")
        ttk.Label(preview_frame, textvariable=self.web2nd_char_count_var,
                  foreground="darkred", font=("", 9, "bold")).grid(row=0, column=1, sticky=tk.W)

        # 버튼 — [Ver7.85 수정] 예전에는 버튼이 9개(제목재추출~썸네일 계열)라
        # 두 줄로 나눴었는데, 썸네일/인포그래픽 생성 버튼 5개는 "9)썸네일/
        # 인포그래픽" 탭으로 분리해 이 탭은 본문 편집/저장 계열 한 줄만 남았다.
        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(6, 0), sticky=tk.W)

        ttk.Button(btn_frame, text="제목 추출",
                   command=self._extract_web2nd_title).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btn_frame, text="🔍 중복 체크",
                   command=self._check_web2nd_duplicate).pack(side=tk.LEFT, padx=(0, 8))

        # [Ver7.57 신규] 중복 차단 기준(%)을 고정값(70) 대신 직접 조정 -
        # 미리보기 중복체크와 실제 저장 시 자동차단 모두 이 값을 그대로 쓴다.
        ttk.Label(btn_frame, text="차단 기준(%):").pack(side=tk.LEFT, padx=(0, 4))
        self.web2nd_dup_threshold_var = tk.IntVar(value=self.load_kin_ui_setting('web2nd_dup_threshold', 70))
        web2nd_dup_spin = ttk.Spinbox(btn_frame, from_=30, to=100, increment=5, width=4,
                                       textvariable=self.web2nd_dup_threshold_var)
        web2nd_dup_spin.pack(side=tk.LEFT, padx=(0, 8))

        def _save_web2nd_dup_threshold(*_):
            try:
                self.save_kin_ui_setting('web2nd_dup_threshold', self.web2nd_dup_threshold_var.get())
            except (tk.TclError, ValueError):
                pass  # 스핀박스 입력 중 빈 값/잘못된 값일 때는 저장을 건너뛴다
        self.web2nd_dup_threshold_var.trace_add("write", _save_web2nd_dup_threshold)

        self.web2nd_save_btn = ttk.Button(
            btn_frame, text="저장",
            command=self.save_web_2nd_result, state=tk.DISABLED
        )
        self.web2nd_save_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="내용 지우기",
                   command=self._clear_web2nd).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btn_frame, text="📁 저장폴더 열기",
                   command=self._open_web2nd_save_folder).pack(side=tk.LEFT, padx=(0, 8))

        # [Ver8.21 이전위치] "📋 제목 복사" 버튼은 "9)썸네일/인포그래픽" 탭
        # 그리드 하단으로 이동됨(create_thumbnail_tab 참고, _copy_thumb_title
        # 사용) - 제목이 인포그래픽 이미지 파일명에 쓰이므로 그쪽에 있는 게
        # 맞다는 사용자 확인. 이 탭(8)2차 각색)에서는 완전히 제거.

        # [Ver7.85 이전위치] 썸네일/이미지 생성 버튼 5개(🖼 썸네일 프롬프트
        # 복사/📝 프롬프트만 복사/자료만 복사/🔁 재미나이 변환 프롬프트
        # 복사/⚙️ 썸네일 프롬프트 설정)는 "9)썸네일/인포그래픽" 탭으로
        # 그대로 이전됨(create_thumbnail_tab 참고). 본문 편집 화면과
        # 썸네일 작업 화면이 하나로 묶여 있어 헷갈린다는 피드백 반영.

        # [2026-09-27 2차 신규 → 3차 이동] 게시판(카테고리) 자동 판정 위젯은
        # "✅ 최종 확정" 버튼 우측(top_btn_row)으로 옮겼다(사용자 요청) -
        # 관련 변수·위젯 생성은 아래 title_gen_box 구성부에서 이어진다.

        self.web2nd_dup_result_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.web2nd_dup_result_var,
                  font=("", 9, "bold")).grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))

        # ── [2026-09-15 2차 재설계] 제목 후보 확정 영역 - 탈락/회피 목록
        # 제거, 제목 라벨을 화면 폭에 맞춰 넓게, 버튼 구성 단순화 ──
        # (2026-09-15 1차에서는 후보별 ☐탈락 체크 + 회피 목록 복사까지
        # 만들었으나, "라디오로 고르고 최종확정하면 되니 탈락은 굳이
        # 필요없다"는 판단에 따라 탈락/회피 관련 기능은 전부 제거한다.
        # 제목 라벨은 액션 버튼과 같은 줄에 있으면 wraplength가 좁게
        # 고정돼 화면 폭을 못 쓰는 문제가 있어, 제목 줄과 버튼 줄을
        # 분리하고 wraplength를 title_gen_box 실제 폭에 맞춰 동적으로
        # 갱신한다(_web2nd_on_title_box_resize). 버튼은 "🔍 블로그" →
        # "🔍 블로그탭검색"으로 이름을 명확히 하고, "🔍 통합"은 제거,
        # 그 자리에 "📋 제목복사"를 넣는다.
        # [2026-09-16 4차] 맨 하단 프레임(title_gen_box) 안쪽 아래 여백이
        # 스크롤을 유발할 만큼 남는다는 지적 - LabelFrame 기본 padding="6"은
        # 4면 모두 동일해서 아래쪽도 6px씩 비었다. 위/아래만 좁혀서
        # (top 4, bottom 2) 그 공백을 줄인다.
        title_gen_box = ttk.LabelFrame(
            right, text="✅ 제목 확정 (네이버 실측) - 확정해야 저장 가능", padding=(6, 4, 6, 2))
        title_gen_box.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        title_gen_box.columnconfigure(0, weight=1)

        # [2026-09-16 2차 → 2026-09-27 3차 단순화] 대안 후보 확정 기능이
        # 삭제되어 "직접 입력으로 확정" 하나만 남았으므로, 안내 문구도
        # 후보/라디오선택 언급을 빼고 실제 절차(직접 입력 → 검색 확인 →
        # 최종 확정)만 남긴다.
        guide_text = (
            "제목을 직접 입력(또는 수정)하고 🔍 블로그탭검색으로 직접 확인 → ✅ 최종 확정을 누르세요."
        )
        # [2026-09-16 3차] 화면 안의 빨간 계열 색상이 "red"/"darkred"로
        # 섞여 있어 헷갈린다는 지적 - 글자수 라벨(위 preview_frame)과
        # 동일한 "darkred"로 통일한다.
        guide_label = ttk.Label(title_gen_box, text=guide_text, foreground="darkred", justify=tk.LEFT, font=("", 8))
        guide_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 4))

        # [2026-09-16 1차 화면 최적화 → 2026-09-27 3차 단순화] "📋 제목복사"·
        # "🗑 제목 지우기"·"✅ 최종 확정"을 한 줄에 모아 상단에 배치한다 -
        # 이전에는 최종확정 버튼이 맨 아래에 있어 매번 스크롤을 크게
        # 내려야 했다. "대안 후보 확정" 기능은 후보군이 쓸모없다는 판단에
        # 따라 완전히 삭제했다(사용자 요청) - "🎯 대안 후보 생성" 버튼도
        # 함께 제거. "제목복사"는 "직접 입력으로 확정" 칸의 제목을
        # 클립보드에 복사하는 단일 버튼이다(_web2nd_copy_selected_title).
        top_btn_row = ttk.Frame(title_gen_box)
        top_btn_row.grid(row=1, column=0, sticky=tk.W, pady=(0, 4))
        ttk.Button(top_btn_row, text="📋 제목복사",
                   command=self._web2nd_copy_selected_title).pack(side=tk.LEFT, padx=(0, 6))
        # [2026-09-16 3차 신규] "직접 입력으로 확정" 입력창을 비우는 용도의
        # "제목 지우기" 버튼 - 제목복사 옆에 배치(사용자 요청).
        ttk.Button(top_btn_row, text="🗑 제목 지우기",
                   command=self._web2nd_clear_manual_title).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top_btn_row, text="✅ 최종 확정",
                   command=self._web2nd_confirm_selected_title).pack(side=tk.LEFT)

        # [2026-09-27 3차 이동] 게시판(카테고리) 자동 판정 위젯 - 원래
        # 우측 패널 상단(제목 확정 영역 밖)에 있었는데, "✅ 최종 확정"
        # 버튼 바로 옆으로 옮겨달라는 요청에 따라 이 자리로 이동했다.
        # 제목을 확정하면 GPT(또는 키워드 규칙)가 게시판 설정 엑셀을
        # 기준으로 골라 채우고, 저장 시 포스팅DB에 기록한다.
        ttk.Label(top_btn_row, text="게시판:").pack(side=tk.LEFT, padx=(14, 4))
        self._web2nd_boards = []
        self._web2nd_board_token = 0
        self._web2nd_board_pending = False
        self._web2nd_board_meta = {}
        self.web2nd_board_var = tk.StringVar(value=self.WEB2ND_BOARD_WAIT)
        self.web2nd_board_info_var = tk.StringVar(value="")
        self.web2nd_board_combo = ttk.Combobox(
            top_btn_row, textvariable=self.web2nd_board_var, state="readonly", width=34,
            values=[self.WEB2ND_BOARD_WAIT, self.WEB2ND_BOARD_ETC])
        self.web2nd_board_combo.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top_btn_row, text="🔄 다시 판정",
                   command=self._web2nd_start_board_classify).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(top_btn_row, textvariable=self.web2nd_board_info_var,
                  foreground="gray", font=("", 9)).pack(side=tk.LEFT)
        self.web2nd_topic_var.trace_add("write", lambda *_: self._web2nd_on_topic_changed_board())

        # [화면폭 활용] 제목 라디오/사전체크 라벨의 wraplength를 title_gen_box
        # 실제 폭에 맞춰 동적으로 갱신하기 위해 대상 위젯을 여기 모아둔다
        # (_web2nd_on_title_box_resize 참고).
        self._web2nd_title_wrap_widgets = []

        # [2026-09-26 변경] 초기 선택값을 -1(미선택)에서 3("직접 입력으로
        # 확정")으로 변경 - 사용자 요청.
        self.web2nd_title_radio_var = tk.IntVar(value=3)

        # [2026-09-16 1차] "직접 입력으로 확정"을 후보 3개보다 위로
        # 올린다 - 실제로는 후보를 참고해 마지막에 직접 다듬어 확정하는
        # 경우가 많아, 매번 후보 아래로 스크롤해서 찾아야 했다. 입력창은
        # 고정폭(width=42) 대신 grid + columnconfigure(weight=1)로 패널
        # 폭에 맞춰 늘어나게 해 제목이 최대한 길게 보이도록 한다.
        manual_block = ttk.Frame(title_gen_box)
        manual_block.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        manual_block.columnconfigure(0, weight=1)
        # [2026-09-16 4차] "직접 입력으로 확정" 문구 뒤에 입력 중인 제목의
        # 글자수를 실시간으로 표시 - 후보 3개 쪽은 사전체크 결과에 글자수를
        # 같이 보여주므로(아래), 직접입력 쪽도 타이핑하는 대로 바로 보이게
        # 맞췄다.
        self.web2nd_working_title_var = tk.StringVar(value="")
        self.web2nd_manual_title_label_var = tk.StringVar(value="직접 입력으로 확정 (0자)")

        def _web2nd_update_manual_title_label(*_):
            self.web2nd_manual_title_label_var.set(
                "직접 입력으로 확정 ({}자)".format(len(self.web2nd_working_title_var.get())))
        self.web2nd_working_title_var.trace_add("write", _web2nd_update_manual_title_label)

        tk.Radiobutton(manual_block, variable=self.web2nd_title_radio_var, value=3,
                       textvariable=self.web2nd_manual_title_label_var, anchor=tk.W).grid(
            row=0, column=0, columnspan=2, sticky=tk.W)
        manual_entry_row = ttk.Frame(manual_block)
        manual_entry_row.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(20, 0), pady=(2, 0))
        manual_entry_row.columnconfigure(0, weight=1)
        ttk.Entry(manual_entry_row, textvariable=self.web2nd_working_title_var).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 6))
        ttk.Button(manual_entry_row, text="🔍 블로그탭검색",
                   command=self._web2nd_search_manual_title).grid(row=0, column=1)

        # [2026-09-27 3차] "대안 후보 확정" 기능(후보 3개 라디오·사전체크·
        # 블로그tab검색 행)을 완전히 삭제했다(사용자 요청: "후보군이
        # 쓸모없어서 기능 삭제했으면 해"). "직접 입력으로 확정"(manual_block)
        # 만 남고, 그 아래 확정 상태 안내 라벨만 이어진다.
        self.web2nd_title_confirm_status_var = tk.StringVar(value="")
        confirm_status_label = ttk.Label(title_gen_box, textvariable=self.web2nd_title_confirm_status_var,
                                          foreground="darkred", wraplength=460, justify=tk.LEFT)
        confirm_status_label.grid(row=3, column=0, sticky=tk.W, pady=(4, 0))
        self._web2nd_title_wrap_widgets.append(confirm_status_label)

        # [화면폭 활용] title_gen_box 폭이 바뀔 때마다(창 크기 조절,
        # 좌우분할 경계 이동 등) 위 라벨들의 wraplength를 실제 폭에 맞춰
        # 다시 계산한다 - 이전에는 340/480 같은 고정값이라 패널이 넓어도
        # 제목이 일찍 줄바꿈됐다(사용자 지적: "제목이 잘 보여야하니까
        # 화면을 최대한 활용").
        def _web2nd_on_title_box_resize(event=None):
            width = title_gen_box.winfo_width()
            wrap = max(200, width - 40)
            for w in self._web2nd_title_wrap_widgets:
                try:
                    w.configure(wraplength=wrap)
                except tk.TclError:
                    pass
        title_gen_box.bind("<Configure>", _web2nd_on_title_box_resize)

        self._web2nd_title_confirmed = False
        self._web2nd_programmatic_edit = False

        # 주제 변경 시 경로·목록 갱신
        self.web2nd_topic_var.trace_add("write", lambda *_: self._update_web2nd_path_preview())
        self.web2nd_topic_var.trace_add("write", lambda *_: self._web2nd_refresh_list())
        # [Ver7.10 추가] 주제 매핑설정에 등록된 2차 모델이 있으면 저장 모델
        # 라디오버튼을 자동으로 그 값으로 맞춘다.
        self.web2nd_topic_var.trace_add("write", lambda *_: self._web2nd_auto_select_model())
        self.web2nd_hide_used_var.trace_add("write", lambda *_: self._web2nd_refresh_list())
        self.web2nd_hide_used_var.trace_add(
            "write", lambda *_: self.save_kin_ui_setting('hide_used_1st_draft_picker', self.web2nd_hide_used_var.get()))

        self._web2nd_refresh_list()
        self._web2nd_auto_select_model()

    # [Ver7.10 추가] 현재 주제의 매핑설정에 등록된 2차 모델이 있으면
    # "저장 모델" 라디오버튼을 자동으로 맞춰준다.
    def _web2nd_auto_select_model(self):
        if not hasattr(self, 'web2nd_model_var'):
            return
        topic = self.web2nd_topic_var.get().split('  (')[0]
        model, _ = self._get_mapping_model_and_prompt(topic, stage='2nd')
        if model in ("Claude", "GPT", "Gemini"):
            self.web2nd_model_var.set(model)
        # [2026-09-27] 주제 콤보 우측의 "각색모델" 표시가 초기값("Claude")에서
        # 한 번도 갱신되지 않아 상단 배너와 어긋나던 문제 수정 - 상단 배너와
        # 동일하게 매핑설정의 2차 모델을 그대로 표시한다(미지정이면 '미지정').
        if hasattr(self, 'web2nd_model_display_var'):
            self.web2nd_model_display_var.set(f"각색모델:{model or '미지정'}")

    # ── [Ver7.10 추가] 5)탭 왼쪽 목록(좌우분할)용 헬퍼 — open_1st_draft_picker
    # 팝업의 로직을 그대로 상시표시 목록용으로 옮긴 것 ──
    def _web2nd_refresh_list(self):
        if not hasattr(self, 'web2nd_list_tree'):
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.web2nd_topic_var.get().split('  (')[0]
        self.web2nd_list_tree.delete(*self.web2nd_list_tree.get_children())
        items = self._scan_1st_draft_items(base, topic)
        usage = self._load_1st_usage(base, topic)
        self._web2nd_list_cache['items'] = items
        self._web2nd_list_cache['usage'] = usage
        date_filter = self.web2nd_date_var.get().strip() if hasattr(self, 'web2nd_date_var') else ""
        shown = 0
        for i, item in enumerate(items):
            used = usage.get(item["title"], False)
            if self.web2nd_hide_used_var.get() and used:
                continue
            if date_filter and item["date"] != date_filter:
                continue
            self.web2nd_list_tree.insert("", tk.END, iid=str(i), values=(
                "✅" if used else "", item["title"], item["date"], item["folder"]
            ))
            shown += 1

        if hasattr(self, 'web2nd_list_count_var'):
            total = len(items)
            if date_filter:
                self.web2nd_list_count_var.set(f"검색결과 {shown}개 / 전체 {total}개")
            else:
                self.web2nd_list_count_var.set(f"총 {total}개")

    # ── [2026-09-27 3차 단순화] "직접 입력으로 확정" 단일 경로 ──────────

    def _web2nd_reset_title_candidates_ui(self):
        """제목 확정 상태를 초기화한다(새로 붙여넣을 때, 저장 뒤 탭
        초기화할 때 공용으로 사용). [2026-09-27 3차] 후보 3개 관련 상태는
        기능 삭제로 함께 제거 - "직접 입력으로 확정" 칸과 게시판 판정
        상태만 초기화한다."""
        if hasattr(self, 'web2nd_title_radio_var'):
            self.web2nd_title_radio_var.set(3)  # [2026-09-26] 기본값 = "직접 입력으로 확정"
        if hasattr(self, 'web2nd_title_confirm_status_var'):
            self.web2nd_title_confirm_status_var.set("")
        if hasattr(self, 'web2nd_working_title_var'):
            self.web2nd_working_title_var.set("")
        self._web2nd_reset_board_ui()

    # ── [2026-09-27 2차 신규] 8)2차 각색: 게시판 자동 판정 ──
    def _web2nd_board_topic(self):
        return self.web2nd_topic_var.get().split('  (')[0]

    def _web2nd_reset_board_ui(self):
        """게시판 판정 상태 초기화(새 글 붙여넣기/제목 재생성/저장 후 초기화 공용).
        진행 중인 판정 결과가 뒤늦게 도착해도 무시되도록 토큰을 올린다."""
        if not hasattr(self, 'web2nd_board_var'):
            return
        self._web2nd_board_token += 1
        self._web2nd_board_pending = False
        self._web2nd_board_meta = {}
        self.web2nd_board_var.set(self.WEB2ND_BOARD_WAIT)
        self.web2nd_board_info_var.set("")

    def _web2nd_on_topic_changed_board(self):
        if not hasattr(self, 'web2nd_board_var'):
            return
        self._web2nd_reset_board_ui()
        self._web2nd_refresh_board_options()

    def _web2nd_refresh_board_options(self):
        """현재 주제의 게시판 목록을 읽어 콤보박스 항목을 갱신한다. 설정이 없으면 []."""
        topic = self._web2nd_board_topic()
        boards, err = [], ""
        try:
            boards = self.semi_load_board_config(topic)
        except Exception as e:
            err = str(e)
        self._web2nd_boards = boards
        opts = [self.WEB2ND_BOARD_WAIT, self.WEB2ND_BOARD_ETC] + [f"{b['number']} - {b['name']}" for b in boards]
        self.web2nd_board_combo.config(values=opts)
        if err:
            self.web2nd_board_info_var.set(f"⚠️ 게시판 설정 오류: {err}")
        elif not boards and not self._web2nd_board_pending:
            self.web2nd_board_info_var.set("이 주제는 게시판 설정이 없어 분류하지 않습니다.")
        return boards

    def _web2nd_start_board_classify(self):
        """제목 확정 직후(또는 '다시 판정' 클릭) 백그라운드로 게시판을 판정한다."""
        if not hasattr(self, 'web2nd_board_var'):
            return
        boards = self._web2nd_refresh_board_options()
        if not boards:
            self.web2nd_board_var.set(self.WEB2ND_BOARD_WAIT)
            return
        title = self.web2nd_title_var.get().strip()
        body = self.web2nd_text.get("1.0", tk.END)
        if not title or title.startswith("("):
            messagebox.showwarning("알림", "먼저 본문을 붙여넣고 제목을 확정하세요.")
            return
        self._web2nd_board_token += 1
        token = self._web2nd_board_token
        self._web2nd_board_pending = True
        self.web2nd_board_var.set(self.WEB2ND_BOARD_WAIT)
        self.web2nd_board_info_var.set("⏳ 게시판 판정 중...")
        use_gpt = bool(self.openai_client)

        def worker():
            try:
                if use_gpt:
                    res = self.semi_gpt_pick_board(title, body, boards)
                else:
                    res = self.semi_keyword_pick_board(title, body, boards)
            except Exception as e:
                res = self.semi_keyword_pick_board(title, body, boards)
                res["reason"] = f"GPT 오류로 예비 판정({str(e)[:60]})"
            self.root.after(0, lambda: self._web2nd_apply_board_result(token, res, boards))

        threading.Thread(target=worker, daemon=True).start()

    def _web2nd_apply_board_result(self, token, res, boards):
        if token != self._web2nd_board_token:
            return  # 그 사이 본문/주제가 바뀜 - 오래된 결과 폐기
        self._web2nd_board_pending = False
        num = res.get("number", "") or ""
        conf = int(res.get("confidence", 0) or 0)
        reason = res.get("reason", "")
        by_number = {b["number"]: f"{b['number']} - {b['name']}" for b in boards}
        self._web2nd_board_meta = {"auto_number": num, "conf": conf, "reason": reason}
        if num in by_number and conf >= self.WEB2ND_BOARD_MIN_CONF:
            self.web2nd_board_var.set(by_number[num])
            self.web2nd_board_info_var.set(f"신뢰도 {conf} · {reason}")
        else:
            # 미지정이거나 신뢰도가 낮으면 코드 규칙으로 "기타" (GPT가 고른 값 아님)
            self._web2nd_board_meta["auto_number"] = ""
            self.web2nd_board_var.set(self.WEB2ND_BOARD_ETC)
            self.web2nd_board_info_var.set(
                f"기타(미분류) · 신뢰도 {conf} · {reason} - 직접 고르거나 그대로 저장(키워드 등록 때 지정)")
        self.log(f"🗂 게시판 판정: {self.web2nd_board_var.get()} (신뢰도 {conf})")

    def _web2nd_collect_board_fields(self):
        """저장 직전 게시판 값을 정리한다. 반환 (진행여부, 포스팅DB에 넣을 필드 dict).
        게시판 설정이 없는 주제는 ({}, 통과)."""
        boards = self._web2nd_refresh_board_options()
        if not boards:
            return True, {}
        if self._web2nd_board_pending:
            messagebox.showinfo("알림", "게시판 판정이 아직 진행 중입니다. 잠시 후 다시 저장하세요.")
            return False, {}
        sel = self.web2nd_board_var.get()
        by_label = {f"{b['number']} - {b['name']}": b for b in boards}
        meta = self._web2nd_board_meta or {}
        if sel in by_label:
            b = by_label[sel]
            auto = (b["number"] == meta.get("auto_number"))
            return True, {
                "board_number": b["number"], "board_name": b["name"],
                "board_conf": int(meta.get("conf", 0)) if auto else 100,
                "board_source": "auto" if auto else "manual",
            }
        # 기타(미분류) 또는 아직 판정 전
        if not messagebox.askyesno(
                "게시판 미분류",
                "이 글은 게시판이 지정되지 않아 '기타'(내부 표시)로 저장됩니다.\n"
                "'기타'는 실제 게시판이 아니므로, 11)주제 키워드 등록 때 실제 게시판을 지정해야 합니다.\n\n"
                "이대로 저장하시겠습니까?"):
            return False, {}
        return True, {
            "board_number": "", "board_name": self.BOARD_ETC_NAME,
            "board_conf": int(meta.get("conf", 0)), "board_source": "etc",
        }

    def _web2nd_apply_confirmed_title(self, confirmed_title):
        """[2026-09-14 재설계 → 2026-09-15 1차 재설계 → 2026-09-27 3차 단순화]
        확정 제목 적용 로직 - 현재는 "✅ 최종 확정" 버튼
        (_web2nd_confirm_selected_title)이 "직접 입력으로 확정" 칸의
        제목을 뽑아 이 함수를 호출한다(후보 확정 기능은 삭제됨). 새
        파일을 만들거나 마커를 심는 대신, 우측 web2nd_text 안의
        H1(# 제목) 줄 자체를 확정 제목으로 즉시 교체한다 - 이후 "저장"을
        누르면 이미 확정 제목이 반영된 본문이 그대로 저장되므로
        파일명·저장경로·포스팅DB 등록이 별도 처리 없이 확정 제목 기준으로
        정상 동작한다."""
        text = self.web2nd_text.get("1.0", tk.END)
        lines = text.split('\n')
        replaced = False
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith('# ') and not s.startswith('## '):
                lines[i] = f"# {confirmed_title}"
                replaced = True
                break
        if not replaced:
            lines.insert(0, f"# {confirmed_title}")
        new_text = "\n".join(lines)

        # Text 위젯의 delete/insert도 <<Modified>>를 발생시키므로, 이
        # 프로그램 자체 편집이 방금 확정한 상태를 스스로 무효화하지
        # 않도록 가드 플래그를 세워둔다(_on_web2nd_modified 참고).
        self._web2nd_programmatic_edit = True
        self.web2nd_text.delete("1.0", tk.END)
        self.web2nd_text.insert("1.0", new_text)

        self._web2nd_title_confirmed = True
        self._extract_web2nd_title()  # title_var/filename_var/path_var 갱신 + 저장 버튼 활성화
        self.web2nd_title_confirm_status_var.set(f"✅ 제목 확정 완료: {confirmed_title}")
        self.log(f"🎯 2차 제목 확정: {confirmed_title}")
        # [2026-09-27 2차] 제목이 확정되면 게시판을 자동 판정한다.
        self._web2nd_start_board_classify()

    def _web2nd_confirm_selected_title(self):
        """[2026-09-15 1차 신규 → 2026-09-27 3차 단순화] 하단 "✅ 최종 확정"
        버튼 - "직접 입력으로 확정" 칸의 제목을 그대로 확정한다(후보
        확정 기능은 삭제되어 이 경로만 남았다)."""
        title = self.web2nd_working_title_var.get().strip()
        if not title:
            messagebox.showwarning("알림", "직접 입력 칸에 제목을 입력하세요.")
            return
        self._web2nd_apply_confirmed_title(title)

    def _web2nd_copy_selected(self):
        sel = self.web2nd_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 자료를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._web2nd_list_cache['items'][idx]
        topic = self.web2nd_topic_var.get().split('  (')[0]
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                material = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        prompt_text, prompt_filename = self._get_prompt2nd_for_topic(topic)
        if not prompt_text:
            messagebox.showwarning(
                "2차 프롬프트 없음",
                f"'{topic}' 주제에 등록된 2차 프롬프트가 없습니다.\n"
                f"'⚙️ 매핑 설정'에서 먼저 등록하세요."
            )
            return
        content = (
            f"{prompt_text}\n\n"
            f"───────────────────\n"
            f"[각색할 자료]\n"
            f"{material}\n"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        # [Ver7.17 수정] 복사 시점엔 usage를 바로 True로 기록하지 않는다.
        # 2차 각색도 AI가 새 제목을 지어내므로 저장 결과 파일명으로는
        # 원본 자료를 역추적할 수 없다 — "저장" 버튼(save_web_2nd_result)이
        # 성공했을 때, 여기서 기억해 둔 원본 자료 제목을 완료 처리한다.
        # 목록은 그 행의 셀만 "📋(진행중)"으로 바꿔 선택/포커스를 유지한다.
        self._web2nd_selected_item = {'title': item['title'], 'iid': sel[0]}
        self._kin_mark_row_in_progress(self.web2nd_list_tree, sel[0])
        self.log(f"📋 2차 각색용 자료 복사 완료 (프롬프트: {prompt_filename}): {item['title']}")

    def _web2nd_copy_prompt_only(self):
        """[Ver7.44 신규] 자료(목록 선택) 없이, 현재 선택된 주제에 매핑된
        2차 프롬프트 텍스트만 클립보드에 복사한다."""
        topic = self.web2nd_topic_var.get().split('  (')[0]
        prompt_text, prompt_filename = self._get_prompt2nd_for_topic(topic)
        if not prompt_text:
            messagebox.showwarning(
                "2차 프롬프트 없음",
                f"'{topic}' 주제에 등록된 2차 프롬프트가 없습니다.\n"
                f"'⚙️ 매핑 설정'에서 먼저 등록하세요."
            )
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_WEB2ND_PROMPT_CONTINUITY_NOTICE + prompt_text)
        self.log(f"📋 2차 프롬프트만 복사: {prompt_filename} ({topic})")
        messagebox.showinfo("복사 완료", "프롬프트만 클립보드에 복사되었습니다.")

    def _web2nd_copy_material_only(self):
        sel = self.web2nd_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "복사할 자료를 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._web2nd_list_cache['items'][idx]
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                material = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        clip_content = KIN_WEB2ND_MATERIAL_LABEL + material
        self.root.clipboard_clear()
        self.root.clipboard_append(clip_content)
        # [Ver7.17 추가] "자료만 복사"만 쓰더라도 완료 판정이 정상 동작하도록
        # 작업 대상을 함께 기억해두고, 그 행을 "📋(진행중)"으로 표시한다.
        self._web2nd_selected_item = {'title': item['title'], 'iid': sel[0]}
        self._kin_mark_row_in_progress(self.web2nd_list_tree, sel[0])
        self.log(f"📋 2차용 자료만 복사: {item['title']}")

    def _web2nd_toggle_used(self):
        sel = self.web2nd_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        item = self._web2nd_list_cache['items'][idx]
        topic = self.web2nd_topic_var.get().split('  (')[0]
        base = self.base_folder_var.get().strip() or self.base_folder
        usage = self._web2nd_list_cache['usage']
        new_state = not usage.get(item["title"], False)
        usage[item["title"]] = new_state
        self._save_1st_usage(base, topic, usage)
        self._kin_mark_row_used(self.web2nd_list_tree, sel[0], self.web2nd_hide_used_var,
                                 self._web2nd_refresh_list, used=new_state)

    def _web2nd_delete_selected(self):
        """[Ver7.76 신규] "8)2차 각색" 목록에 뜬 1차 각색본(perplexity_*_
        1st_draft) MD 파일을 여러 개 선택해 한번에 삭제한다. 위 두 탭과
        동일한 이유·설계(질문DB는 건드리지 않고 "이 단계"의 산출물만
        지움)."""
        sel = self.web2nd_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "삭제할 항목을 먼저 선택하세요.")
            return
        indices = sorted((int(i) for i in sel), reverse=True)
        items = self._web2nd_list_cache['items']
        targets = [items[i] for i in indices if 0 <= i < len(items)]

        preview = "\n".join(f"  • {t['title']}" for t in targets[:10])
        if len(targets) > 10:
            preview += f"\n  … 외 {len(targets) - 10}건 더"

        if not messagebox.askyesno(
                "⚠️ 삭제 확인 (되돌릴 수 없음)",
                f"아래 {len(targets)}개 1차 각색본 파일을 영구 삭제합니다.\n"
                f"(질문DB 자체는 지워지지 않습니다 - 질문 삭제는 \"2)질문 상세분석\" 탭에서)\n\n"
                f"{preview}\n\n정말 삭제하시겠습니까?",
                icon="warning"):
            return

        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.web2nd_topic_var.get().split('  (')[0]
        usage = self._web2nd_list_cache['usage']
        deleted = 0
        for t in targets:
            try:
                if os.path.exists(t["file_path"]):
                    os.remove(t["file_path"])
                usage.pop(t["title"], None)
                deleted += 1
            except Exception as e:
                self.log(f"⚠️ 1차 각색본 파일 삭제 실패: {t['file_path']} ({e})")
        self._save_1st_usage(base, topic, usage)
        self.log(f"🗑️ 1차 각색본 삭제 완료: {deleted}개 ({topic})")
        self._web2nd_refresh_list()


    def _on_web2nd_modified(self, event=None):
        """텍스트 변경 감지 -> 제목 자동 추출
        [Ver9.08 최종] 사용자가 새로 붙여넣거나 직접 고친 경우는 이전에
        확정해둔 제목 후보를 무효화한다(저장 버튼도 다시 비활성화됨 -
        _extract_web2nd_title 참고). 단, "✅ 이 제목으로 확정" 버튼이
        코드로 H1 줄만 바꿔 쓰는 경우(_web2nd_programmatic_edit)는
        방금 확정한 상태 그대로 유지해야 하므로 무효화하지 않는다."""
        if self.web2nd_text.edit_modified():
            if not getattr(self, '_web2nd_programmatic_edit', False):
                self._web2nd_title_confirmed = False
                self._web2nd_reset_title_candidates_ui()
            self._web2nd_programmatic_edit = False
            self._extract_web2nd_title()
            self._update_web2nd_char_count()
            self.web2nd_text.edit_modified(False)
    
    def _update_web2nd_char_count(self):
        text = self.web2nd_text.get("1.0", tk.END)
        korean = len(re.findall(r'[\uAC00-\uD7A3]', text))
        english = len(re.findall(r'[a-zA-Z0-9]', text))
        punct = len(re.findall(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', text))
        spaces = len(re.findall(r'[ \t]', text))
        total_excl = int(korean + english * 0.5 + punct)
        total_incl = int(korean + english * 0.5 + punct + spaces)
        self.web2nd_char_count_var.set(
            "한글 기준 글자수 │ 공백제외: {:,}자 │ 공백포함: {:,}자".format(total_excl, total_incl)
        )

    def _extract_web2nd_title(self):
        """마크다운 H1에서 제목 추출 후 미리보기 갱신"""
        text = self.web2nd_text.get("1.0", tk.END).strip()

        if not text:
            self.web2nd_title_var.set("(마크다운을 붙여넣으면 자동 추출됩니다)")
            self.web2nd_filename_var.set("")
            self.web2nd_path_var.set("")
            self.web2nd_save_btn.config(state=tk.DISABLED)
            return

        title = None
        for line in text.split('\n'):
            s = line.strip()
            if s.startswith('# ') and not s.startswith('## '):
                title = s[2:].strip()
                break

        if not title or len(title) < 3:
            self.web2nd_title_var.set("H1 제목을 찾을 수 없습니다 (첫 줄이  # 제목  형식인지 확인)")
            self.web2nd_filename_var.set("")
            self.web2nd_path_var.set("")
            self.web2nd_save_btn.config(state=tk.DISABLED)
            return

        filename = "{}.md".format(self.create_safe_filename(title))
        self.web2nd_title_var.set(title)
        self.web2nd_filename_var.set(filename)
        self._update_web2nd_path_preview()
        # [Ver9.08 최종] "저장"은 더 이상 H1 인식만으로 열리지 않는다.
        # 제목 후보를 확정(_web2nd_title_confirmed)해야만 열리도록 해서,
        # 확정 절차 없이 저장되는 경로를 원천 차단한다.
        if getattr(self, '_web2nd_title_confirmed', False):
            self.web2nd_save_btn.config(state=tk.NORMAL)
        else:
            self.web2nd_save_btn.config(state=tk.DISABLED)
        # [2026-09-14 → 2026-09-15 1차] "직접 입력으로 확정" 칸에도
        # 추출된 제목을 우선 채워둔다(그대로 확정해도 되고, 다듬어서
        # 확정해도 됨). 저장용 web2nd_title_var와는 별개 변수라, 확정
        # 전에 이 칸에서 직접 고쳐 써도 실제 저장 제목·파일명에는
        # 영향이 없다(직접 고친 값을 그대로 확정하면 그때 비로소 반영됨).
        if hasattr(self, 'web2nd_working_title_var'):
            self.web2nd_working_title_var.set(title)

    def _web2nd_search_manual_title(self):
        """[2026-09-15 2차] "직접 입력으로 확정" 행의 "🔍 블로그탭검색"
        버튼 - 그 입력창의 현재 값으로 블로그탭 검색을 연다."""
        title = self.web2nd_working_title_var.get().strip()
        if not title:
            messagebox.showwarning("알림", "검색어(제목)를 입력하세요.")
            return
        open_naver_search_in_chrome(title, blog_only=True)
        self.log(f"🔍 직접입력 블로그탭검색: {title}")

    def _web2nd_copy_selected_title(self):
        """[2026-09-16 1차 신규 → 2026-09-27 3차 단순화] 상단 공용
        "📋 제목복사" 버튼 - "직접 입력으로 확정" 칸의 제목을 그대로
        클립보드에 복사한다(후보 확정 기능 삭제로 이 경로만 남았다)."""
        title = self.web2nd_working_title_var.get().strip()
        if not title:
            messagebox.showwarning("알림", "복사할 제목이 없습니다.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(title)
        self.log(f"📋 선택된 제목 복사 완료: {title}")

    def _web2nd_clear_manual_title(self):
        """[2026-09-16 3차 신규] "🗑 제목 지우기" 버튼 - "직접 입력으로
        확정" 입력창(web2nd_working_title_var)만 비운다(후보 3개나
        라디오 선택 상태에는 영향 없음)."""
        self.web2nd_working_title_var.set("")

    def _update_web2nd_path_preview(self):
        """저장 전체 경로 미리보기"""
        filename = self.web2nd_filename_var.get()
        if not filename:
            return
        from datetime import datetime
        today    = datetime.now().strftime("%Y-%m-%d")
        topic    = self.web2nd_topic_var.get().split('  (')[0]
        model    = self.web2nd_model_var.get()
        base     = self.base_folder_var.get().strip() or self.base_folder
        save_dir = os.path.join(base, topic, today, "perplexity_{}_final_articles".format(model))
        if self.web2nd_folder_mode_var.get():
            title_folder = filename[:-3] if filename.endswith('.md') else filename  # 제목별 하위폴더 (확장자 제외)
            save_dir = os.path.join(save_dir, title_folder)
        self.web2nd_path_var.set(os.path.join(save_dir, filename))

    # [수정] 파일명(제목 추출)과 무관하게, 작업폴더+주제+모델+오늘날짜만으로
    # 저장 폴더를 바로 계산해서 연다. 마크다운을 아직 안 붙여넣었어도 동작한다.
    def _open_web2nd_save_folder(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        topic = self.web2nd_topic_var.get().split('  (')[0]
        model = self.web2nd_model_var.get()
        base = self.base_folder_var.get().strip() or self.base_folder
        folder = os.path.join(base, topic, today, "perplexity_{}_final_articles".format(model))

        # 제목별 폴더 저장 모드 + 제목이 이미 추출돼 있으면 그 하위 폴더까지 연다
        filename = self.web2nd_filename_var.get()
        if self.web2nd_folder_mode_var.get() and filename:
            title_folder = filename[:-3] if filename.endswith('.md') else filename
            folder = os.path.join(folder, title_folder)

        try:
            os.makedirs(folder, exist_ok=True)
            if os.name == "nt":
                os.startfile(folder)
            else:
                import subprocess, platform
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
            self.log(f"📁 저장폴더 열기: {folder}")
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 여는 중 오류가 발생했습니다:\n{e}")

    # [수정] 미리보기 라벨에 이미 값이 있는지와 무관하게, 텍스트박스 내용에서
    # 직접(바로) H1 제목을 뽑아 클립보드로 복사한다. "제목 재추출" 버튼을
    # 먼저 누를 필요 없음 — 마크다운이 붙여져 있으면 그걸로 바로 추출한다.
    def _copy_web2nd_title(self):
        text = self.web2nd_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("알림", "마크다운을 먼저 붙여넣으세요.")
            return

        title = None
        for line in text.split('\n'):
            s = line.strip()
            if s.startswith('# ') and not s.startswith('## '):
                title = s[2:].strip()
                break

        if not title or len(title) < 3:
            messagebox.showwarning("알림", "H1 제목을 찾을 수 없습니다 (첫 줄이 '# 제목' 형식인지 확인하세요).")
            return

        # [Ver7.10 추가] 제목 중간/끝 어디에 물음표가 있든 전부 제거
        title = title.replace('?', '').replace('？', '').strip()

        self.root.clipboard_clear()
        self.root.clipboard_append(title)
        self.log(f"📋 제목 복사 완료: {title}")

    # [Ver8.21 신규] "9)썸네일/인포그래픽" 탭용 제목 복사 - _copy_web2nd_title과
    # 로직은 동일하되(H1 제목 추출 + 물음표 제거) 대상 위젯만 web2nd_text가
    # 아니라 thumb_text(9)탭 본문칸)로 바꿨다. 인포그래픽 이미지 파일명에
    # 제목을 쓰는 용도이므로 8)탭이 아니라 9)탭에 있어야 한다는 사용자 확인
    # 반영(기존 버튼은 8)탭에서 제거하고 이쪽으로 이동).
    def _copy_thumb_title(self):
        text = self.thumb_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("알림", "완성 본문을 먼저 붙여넣으세요.")
            return

        title = None
        for line in text.split('\n'):
            s = line.strip()
            if s.startswith('# ') and not s.startswith('## '):
                title = s[2:].strip()
                break

        if not title or len(title) < 3:
            messagebox.showwarning("알림", "H1 제목을 찾을 수 없습니다 (첫 줄이 '# 제목' 형식인지 확인하세요).")
            return

        title = title.replace('?', '').replace('？', '').strip()

        self.root.clipboard_clear()
        self.root.clipboard_append(title)
        self.log(f"📋 제목 복사 완료(인포그래픽): {title}")


    # [Ver7.13 추가, 정책뉴스 TAB3 '_auto_check_dup_post' 참조] 붙여넣기 시점에
    # 버튼(🔍 중복 체크)을 누르지 않아도 자동으로 한 번 실행한다. 본문/제목이
    # 아직 없으면(예: 다른 목적으로 붙여넣었거나 붙여넣기 직후 제목 추출 실패)
    # 정책뉴스와 동일하게 경고 팝업 없이 조용히 건너뛴다 — 자동 트리거인데
    # 매번 경고가 뜨면 방해가 된다. 버튼은 그대로 남아있어 수동 재확인에 계속
    # 쓸 수 있다. 정책뉴스는 본문만 확인하지만, 지식인은 저장 경로 계산에
    # 제목이 필수라 title 상태(H1 못찾음 안내 문구)까지 같이 확인한다.
    def _auto_check_web2nd_duplicate(self):
        text = self.web2nd_text.get("1.0", tk.END).strip()
        if not text:
            return
        title = self.web2nd_title_var.get()
        if not title or title.startswith("(") or title.startswith("H1"):
            return
        self._check_web2nd_duplicate()

    # [Ver7.07 추가] 저장 전 미리보기용 중복체크 — 정책뉴스 TAB3의
    # '포스팅 중복 체크'와 동일한 컨셉. 저장 버튼과 별개로 언제든 눌러서
    # 결과를 눈으로 확인할 수 있다.
    def _web2nd_get_dup_threshold(self):
        """[Ver7.57 신규] 화면의 '차단 기준(%)' 스핀박스 값을 danger로 쓴다.
        입력이 비정상(빈 값 등)이면 기존 기본값 70으로 되돌아간다."""
        try:
            v = int(self.web2nd_dup_threshold_var.get())
        except (tk.TclError, ValueError):
            return 70
        return min(100, max(30, v))

    def _check_web2nd_duplicate(self):
        """[Ver7.57 변경] danger 임계값을 하드코딩 70 대신 화면에서 조정한 값을 쓴다."""
        text  = self.web2nd_text.get("1.0", tk.END).strip()
        title = self.web2nd_title_var.get()
        if not text:
            messagebox.showwarning("알림", "먼저 완성 본문을 붙여넣으세요.")
            return
        if not title or title.startswith("(") or title.startswith("H1"):
            messagebox.showwarning("알림", "제목을 먼저 추출하세요(제목 추출 버튼).")
            return

        topic = self.web2nd_topic_var.get().split('  (')[0]
        base = self.base_folder_var.get().strip() or self.base_folder
        posting_db_path = get_posting_db_path(base, topic)
        posting_records = load_json_db(posting_db_path)
        new_p_core = extract_posting_core(text, title)
        threshold = self._web2nd_get_dup_threshold()
        results = check_posting_duplicate(new_p_core, posting_records, danger=threshold)

        if not results:
            self.web2nd_dup_result_var.set("✅ 중복 없음 — 저장해도 안전합니다")
        else:
            danger_count = sum(1 for r in results if r["danger"])
            if danger_count:
                self.web2nd_dup_result_var.set(
                    f"⛔ 위험 {danger_count}건 포함(차단기준 {threshold}%↑) — 저장 시 자동 차단됩니다 (아래 팝업 확인)")
            else:
                self.web2nd_dup_result_var.set(
                    f"⚠️ 주의 {len(results)}건 발견 — 저장은 막히지 않지만 확인해보세요")
        self._show_web2nd_dup_result(results, threshold)

    def _show_web2nd_dup_result(self, results, threshold=70):
        top = tk.Toplevel(self.root)
        top.title("중복 체크 결과")
        w, h = 780, 460
        sw, sh = top.winfo_screenwidth(), top.winfo_screenheight()
        top.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        top.transient(self.root)

        if not results:
            ttk.Label(top, text="✅ 중복 없음 — 포스팅DB에 유사한 기존 글이 없습니다.",
                      font=("", 11, "bold"), foreground="darkgreen").pack(pady=20)
            ttk.Button(top, text="닫기", command=top.destroy).pack(pady=(0, 10))
            return

        ttk.Label(top, text=f"⚠️ 유사한 기존 포스팅 {len(results)}건 발견",
                  font=("", 11, "bold"), foreground="darkred").pack(pady=(10, 4))
        ttk.Label(top, text=f"50%↑ 주의 / {threshold}%↑ 위험(저장 시 자동 차단)",
                  font=("", 9), foreground="gray").pack(pady=(0, 8))

        columns = ("rate", "title", "date", "matched")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=12)
        tree.heading("rate", text="중복률")
        tree.heading("title", text="기존 글 제목")
        tree.heading("date", text="저장일")
        tree.heading("matched", text="매칭 항목")
        tree.column("rate", width=70, anchor=tk.CENTER)
        tree.column("title", width=340)
        tree.column("date", width=90, anchor=tk.CENTER)
        tree.column("matched", width=220)
        tree.tag_configure("danger", foreground="#B00020")
        tree.tag_configure("warn", foreground="#B8860B")
        tree.pack(fill=tk.BOTH, expand=True, padx=10)

        for r in results:
            tag = "danger" if r["danger"] else "warn"
            tree.insert("", tk.END, values=(
                f"{r['rate']}%", r["title"], r["date"], ", ".join(r["matched"])
            ), tags=(tag,))

        def show_detail(event=None):
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("알림", "먼저 항목을 선택하세요.")
                return
            idx = tree.index(sel[0])
            self._show_kin_dup_detail(results[idx], force_save_mode=False)

        tree.bind("<Double-1>", show_detail)

        btn_frame = ttk.Frame(top, padding=(10, 8))
        btn_frame.pack(fill=tk.X)

        def open_selected_folder():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("알림", "먼저 항목을 선택하세요.")
                return
            idx = tree.index(sel[0])
            fp = results[idx].get("file_path", "")
            if fp and os.path.exists(fp):
                os.startfile(os.path.dirname(fp)) if os.name == "nt" else \
                    os.system(f'open "{os.path.dirname(fp)}"')
            else:
                messagebox.showinfo("알림", "원본 파일 경로를 찾을 수 없습니다.")

        ttk.Button(btn_frame, text="🔍 상세 비교 (더블클릭도 가능)", command=show_detail).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="📁 선택 항목 폴더 열기", command=open_selected_folder).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(btn_frame, text="닫기", command=top.destroy).pack(side=tk.RIGHT)

    # ── [Ver7.16 신규] 중복 상세 비교 다이얼로그 ──
    # "몇 % 겹침"이라는 숫자만 보여주면 사람이 판단할 근거가 없다는 지적을
    # 반영해, 실제로 겹치는 문구/숫자와 기존·신규 글의 도입부·마무리 원문
    # 스니펫(DB에 이미 저장돼 있던 것 -- 원본 MD가 삭제됐어도 이건 남아있음)을
    # 나란히 보여준다. force_save_mode=True면 하단에 "그래도 저장/취소"
    # 버튼이 뜨고, 그 선택 결과(True/False)를 반환한다. False(미리보기용)면
    # 그냥 정보 확인용 "닫기" 버튼만 뜬다.
    def _show_kin_dup_detail(self, r, force_save_mode=False):
        """[Ver7.45 변경] force_save_mode=True일 때 버튼이 "취소"/"그래도
        저장" 둘뿐이라, 사실은 같은 글을 재저장하는 상황에서도 "그래도
        저장"을 누르면 포스팅DB에 사실상 같은 기록이 하나 더 쌓이는 문제가
        있었다(11)포스팅 이력관리에 거의 동일한 글이 중복으로 보이는 원인).
        "🔁 덮어쓰기(같은 글 - 기존 기록 교체)" 버튼을 추가해 선택지를
        분리했다 - 반환값도 True/False에서 "cancel"/"append"/"overwrite"
        문자열로 바뀐다. force_save_mode=False(미리보기 전용)일 때는 버튼이
        "닫기" 하나뿐이라 반환값을 실질적으로 쓰지 않는다."""
        result = {"action": "cancel"}

        top = tk.Toplevel(self.root)
        top.title("중복 상세 비교")
        w, h = 900, 700
        sw, sh = top.winfo_screenwidth(), top.winfo_screenheight()
        top.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        top.transient(self.root)
        top.grab_set()

        outer = ttk.Frame(top, padding="14")
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)

        head = "⛔ 위험 (저장 시 자동 차단 대상)" if r.get("danger") else "⚠️ 주의"
        head_color = "#B00020" if r.get("danger") else "#B8860B"
        ttk.Label(outer, text=f"{head} — 총 매칭율 {r['rate']}%",
                  font=("", 13, "bold"), foreground=head_color).grid(
            row=0, column=0, columnspan=2, sticky=tk.W)

        if r.get("hard_match"):
            ttk.Label(outer,
                      text="※ 매칭율과 별개로, 제목 첫 단어와 구체적 숫자(금액·나이·기간)가 "
                           "동시에 일치해 강제 판정 규칙(hard_match)에도 걸렸습니다.",
                      foreground="#B00020", wraplength=850, justify=tk.LEFT).grid(
                row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))

        breakdown = (f"세부 매칭율 — 제목 {r.get('title_pct', 0)}%  ·  "
                     f"도입부 {r.get('intro_pct', 0)}%  ·  마무리 {r.get('summary_pct', 0)}%  ·  "
                     f"소제목 {r.get('heading_pct', 0)}%")
        ttk.Label(outer, text=breakdown, foreground="gray").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 10))

        # 제목 비교
        title_frame = ttk.LabelFrame(outer, text="제목 비교", padding="8")
        title_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        ttk.Label(title_frame, text="기존:", foreground="gray").grid(row=0, column=0, sticky=tk.NW)
        ttk.Label(title_frame, text=r.get("old_title", ""), wraplength=760, justify=tk.LEFT).grid(
            row=0, column=1, sticky=tk.W)
        ttk.Label(title_frame, text="신규:", foreground="gray").grid(row=1, column=0, sticky=tk.NW, pady=(4, 0))
        ttk.Label(title_frame, text=r.get("new_title", ""), wraplength=760, justify=tk.LEFT).grid(
            row=1, column=1, sticky=tk.W, pady=(4, 0))

        # 겹치는 표현 / 겹치는 숫자 -- 실제 근거
        evidence_frame = ttk.LabelFrame(outer, text="실제로 겹치는 근거", padding="8")
        evidence_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        phrases = r.get("common_phrases", [])
        if phrases:
            ttk.Label(evidence_frame, text="그대로 겹치는 문구:", foreground="gray").pack(anchor=tk.W)
            for p in phrases:
                ttk.Label(evidence_frame, text=f'  • "{p}"', wraplength=830, justify=tk.LEFT).pack(anchor=tk.W)
        else:
            ttk.Label(evidence_frame, text="그대로 겹치는 문구: 없음 (문장 표현은 다름)",
                      foreground="gray").pack(anchor=tk.W)

        numbers_overlap = r.get("numbers_overlap", [])
        num_text = ", ".join(numbers_overlap) if numbers_overlap else "없음"
        ttk.Label(evidence_frame, text=f"겹치는 숫자 전체: {num_text}",
                  foreground="gray", wraplength=830, justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 0))

        # [Ver7.56 신규] 본문 중간 소제목까지 겹치는지 - 도입부/마무리만 보고는
        # 놓치던 "중간 섹션이 실질적으로 같은 글" 판단 근거
        headings_overlap = r.get("headings_overlap", [])
        headings_text = ", ".join(headings_overlap) if headings_overlap else "없음"
        ttk.Label(evidence_frame, text=f"겹치는 소제목: {headings_text}",
                  foreground="gray", wraplength=830, justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 0))

        # 도입부/마무리 원문 스니펫 -- 원본 MD가 삭제됐어도 DB에 저장돼 있던 것
        snippet_frame = ttk.Frame(outer)
        snippet_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        snippet_frame.columnconfigure(0, weight=1)
        snippet_frame.columnconfigure(1, weight=1)
        snippet_frame.rowconfigure(1, weight=1)
        snippet_frame.rowconfigure(3, weight=1)
        outer.rowconfigure(5, weight=1)

        ttk.Label(snippet_frame, text="기존 글 도입부 (저장 당시 스니펫)", font=("", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W)
        ttk.Label(snippet_frame, text="신규 글 도입부", font=("", 9, "bold")).grid(
            row=0, column=1, sticky=tk.W)

        old_intro_box = scrolledtext.ScrolledText(snippet_frame, height=6, wrap=tk.WORD)
        old_intro_box.insert(tk.END, r.get("old_intro", "") or "(저장된 스니펫 없음)")
        old_intro_box.config(state=tk.DISABLED)
        old_intro_box.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(0, 4), pady=(2, 8))

        new_intro_box = scrolledtext.ScrolledText(snippet_frame, height=6, wrap=tk.WORD)
        new_intro_box.insert(tk.END, r.get("new_intro", "") or "(내용 없음)")
        new_intro_box.config(state=tk.DISABLED)
        new_intro_box.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(4, 0), pady=(2, 8))

        ttk.Label(snippet_frame, text="기존 글 마무리 (저장 당시 스니펫)", font=("", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W)
        ttk.Label(snippet_frame, text="신규 글 마무리", font=("", 9, "bold")).grid(
            row=2, column=1, sticky=tk.W)

        old_summary_box = scrolledtext.ScrolledText(snippet_frame, height=6, wrap=tk.WORD)
        old_summary_box.insert(tk.END, r.get("old_summary", "") or "(저장된 스니펫 없음)")
        old_summary_box.config(state=tk.DISABLED)
        old_summary_box.grid(row=3, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(0, 4), pady=(2, 0))

        new_summary_box = scrolledtext.ScrolledText(snippet_frame, height=6, wrap=tk.WORD)
        new_summary_box.insert(tk.END, r.get("new_summary", "") or "(내용 없음)")
        new_summary_box.config(state=tk.DISABLED)
        new_summary_box.grid(row=3, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(4, 0), pady=(2, 0))

        # 하단 버튼
        btn_frame = ttk.Frame(outer, padding=(0, 10, 0, 0))
        btn_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))

        def open_folder():
            fp = r.get("file_path", "")
            if fp and os.path.exists(fp):
                os.startfile(os.path.dirname(fp)) if os.name == "nt" else \
                    os.system(f'open "{os.path.dirname(fp)}"')
            else:
                messagebox.showinfo("알림", "원본 파일 경로를 찾을 수 없습니다(이미 삭제됐을 수 있습니다).")

        ttk.Button(btn_frame, text="📁 기존 글 폴더 열기", command=open_folder).pack(side=tk.LEFT)

        if force_save_mode:
            def on_force_save():
                result["action"] = "append"
                top.destroy()

            def on_overwrite():
                result["action"] = "overwrite"
                top.destroy()

            def on_cancel():
                result["action"] = "cancel"
                top.destroy()

            ttk.Button(btn_frame, text="❌ 취소 (저장 안 함)", command=on_cancel).pack(side=tk.RIGHT, padx=(6, 0))
            ttk.Button(btn_frame, text="✅ 다른 글로 저장 (중복 유지)", command=on_force_save).pack(side=tk.RIGHT, padx=(6, 0))
            ttk.Button(btn_frame, text="🔁 덮어쓰기 (같은 글 - 기존 기록 교체)", command=on_overwrite).pack(side=tk.RIGHT)
        else:
            ttk.Button(btn_frame, text="닫기", command=top.destroy).pack(side=tk.RIGHT)

        top.wait_window()
        return result["action"]

    def save_web_2nd_result(self):
        """웹 2차 각색 결과를 해당 모델 폴더에 저장"""
        text     = self._strip_ai_ui_chrome(self.web2nd_text.get("1.0", tk.END).strip())
        filename = self.web2nd_filename_var.get()
        title    = self.web2nd_title_var.get()

        if not text or not filename:
            messagebox.showwarning("저장 오류", "저장할 내용 또는 파일명이 없습니다.")
            return

        from datetime import datetime
        today    = datetime.now().strftime("%Y-%m-%d")
        topic    = self.web2nd_topic_var.get().split('  (')[0]
        model    = self.web2nd_model_var.get()
        base     = self.base_folder_var.get().strip() or self.base_folder
        save_dir = os.path.join(base, topic, today, "perplexity_{}_final_articles".format(model))
        if self.web2nd_folder_mode_var.get():
            title_folder = filename[:-3] if filename.endswith('.md') else filename  # 제목별 하위폴더 (확장자 제외)
            save_dir = os.path.join(save_dir, title_folder)

        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        if os.path.exists(save_path):
            if not messagebox.askyesno("덮어쓰기 확인",
                    "동일한 파일이 이미 존재합니다.\n\n{}\n\n덮어쓰시겠습니까?".format(filename)):
                return

        # ✅ 포스팅DB(주제별 JSON) 기반 중복 체크 - 매칭율이 차단 기준(%) 이상이면 저장 자체를 차단 (저장=포스팅이므로)
        # [Ver7.07 수정] check_posting_duplicate가 이제 50%↑도 함께 반환하므로
        # (미리보기 중복체크 버튼용), 여기서는 "danger"인 것만 걸러서 차단한다.
        # [Ver7.57 변경] danger 임계값이 하드코딩 70 대신 화면의 '차단 기준(%)'
        # 스핀박스 값을 그대로 쓴다 - 미리보기 중복체크와 항상 같은 기준.
        posting_db_path = get_posting_db_path(base, topic)
        posting_records = load_json_db(posting_db_path)
        new_p_core = extract_posting_core(text, title)
        threshold = self._web2nd_get_dup_threshold()
        all_dup_results = check_posting_duplicate(new_p_core, posting_records, danger=threshold)
        dup_results = [r for r in all_dup_results if r["danger"]]

        if dup_results:
            dup_top = dup_results[0]
            # [Ver7.16 변경] "몇 % 겹침"이라는 문구만 보여주는 확인창 대신,
            # 실제로 겹치는 문구·숫자와 기존/신규 글의 도입부·마무리 원문
            # 스니펫을 나란히 보여주는 상세 비교 다이얼로그를 띄운다. 원본
            # MD를 이미 삭제한 경우(포스팅 완료 후 삭제하는 운영방식)에도
            # DB에 저장돼 있던 스니펫으로 판단 근거를 제공한다. 최종 판단은
            # 사람이 직접 내리고, 강행 시 로그에 남겨 추적 가능하게 한다.
            # [Ver7.45 변경] "취소"/"다른 글로 저장(append)" 외에 "🔁 덮어쓰기
            # (overwrite)"를 추가 - 실수로 같은 글을 다시 저장해도 포스팅DB에
            # 중복 기록이 쌓이지 않고, 기존 기록을 지우고 새 기록으로 교체한다.
            action = self._show_kin_dup_detail(dup_top, force_save_mode=True)
            if action == "cancel":
                return
            if action == "overwrite":
                self.log(
                    "🔁 동일 글로 판단 - 기존 포스팅DB 기록을 교체해 저장: {} (매칭율 {}%)".format(
                        filename, dup_top['rate']
                    )
                )
            else:
                self.log(
                    "⚠️ 중복체크 경고 확인 후 강제 저장(별개 글로 판단): {} (매칭율 {}%, 일치항목: {})".format(
                        filename, dup_top['rate'], ', '.join(dup_top['matched'])
                    )
                )
        else:
            action = None
            dup_top = None

        # [2026-09-27 2차] 게시판 값 확정(기타면 확인) - 취소하면 저장하지 않는다.
        board_ok, board_fields = self._web2nd_collect_board_fields()
        if not board_ok:
            return

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

            # 포스팅DB(JSON)에 등록 - 저장(=포스팅) 성공 시점에만 등록
            new_p_core["date"] = datetime.now().strftime("%Y-%m-%d")
            new_p_core["file_path"] = save_path
            new_p_core.update(board_fields)  # 게시판 번호/이름(또는 기타) - MD 본문에는 넣지 않음
            # [Ver7.45 추가] "덮어쓰기" 선택 시 기존 기록을 지우고 새 기록으로
            # 교체한다(같은 글이 포스팅DB에 두 번 쌓이는 것 방지). 실제 MD
            # 파일은 기존 관례대로 자동 삭제하지 않는다(사람이 직접 정리).
            if action == "overwrite" and dup_top is not None:
                overwrite_index = dup_top.get("record_index")
                if overwrite_index is not None and 0 <= overwrite_index < len(posting_records):
                    del posting_records[overwrite_index]
            posting_records.append(new_p_core)
            save_json_db(posting_db_path, posting_records)

            # [2026-09-27 3차] 다른 컴퓨터로 완성본 폴더를 통째로 옮길 때
            # 쓸 수 있도록, 같은 final_articles 폴더에 사이드카(제목+카테고리
            # 번호만)도 같이 남긴다. 제목별 폴더 저장 모드여도 사이드카는
            # 항상 final_articles 폴더 바로 밑(제목 폴더 밖)에 둔다.
            final_articles_dir = os.path.join(base, topic, today, "perplexity_{}_final_articles".format(model))
            self._kin_sidecar_upsert(final_articles_dir, title, board_fields.get("board_number", ""))

            self.log("웹2차 저장: {}".format(filename))
            self.log("   -> {}".format(save_dir))

            self.log("저장 완료: {} → {}".format(filename, save_dir))

            # [Ver7.17 추가] 실제 저장(=포스팅DB 등록)까지 끝난 시점에만,
            # 복사해 뒀던 원본 1차각색 자료를 "완료"로 기록한다.
            target = getattr(self, '_web2nd_selected_item', None)
            if target and target.get('title'):
                usage = self._web2nd_list_cache.get('usage', {})
                usage[target['title']] = True
                self._save_1st_usage(base, topic, usage)
                self._kin_mark_row_used(self.web2nd_list_tree, target.get('iid'),
                                         self.web2nd_hide_used_var, self._web2nd_refresh_list)

            self._refresh_web2nd_counts()
            self._clear_web2nd()

        except Exception as e:
            self.log("웹2차 저장 실패: {}".format(str(e)))
            messagebox.showerror("저장 실패", "파일 저장 중 오류 발생:\n{}".format(str(e)))

    # [Ver7.04 추가] 썸네일 인포그래픽 프롬프트
    def _get_kin_thumbnail_group(self, topic: str) -> str:
        """주제(폴더명)를 썸네일 스타일 그룹명으로 변환. 매핑에 없으면
        빈 문자열(아직 템플릿 준비 안 된 주제)."""
        return KIN_THUMBNAIL_GROUP_MAP.get(topic, "")

    def _get_kin_thumbnail_template_path(self, group: str):
        """작업 폴더(base_folder_var) 안에서 그룹 키워드가 포함된
        '썸네일_프롬프트' .md 파일을 찾는다. 여러 버전(V1, V2...)이
        같이 있으면 파일명 정렬상 가장 나중 것을 쓴다(보통 버전이
        더 큰 쪽). 못 찾으면 None."""
        work_folder = self.base_folder_var.get().strip() if hasattr(self, 'base_folder_var') else self.base_folder
        work_folder = work_folder or self.base_folder
        if not os.path.isdir(work_folder):
            return None
        candidates = [
            fname for fname in os.listdir(work_folder)
            if fname.endswith(".md") and "썸네일" in fname
            and "프롬프트" in fname and group in fname
        ]
        if not candidates:
            return None
        candidates.sort()  # 파일명 끝의 V1/V2/V3... 사전순 정렬 -> 최신판 우선
        return os.path.join(work_folder, candidates[-1])

    def _build_kin_thumbnail_prompt(self, topic: str, md_text: str):
        """주제별 스타일 템플릿 + 완성 본문을 합쳐 클로드에게 그대로
        복사해서 넘길 수 있는 프롬프트를 만든다. 템플릿을 못 찾으면
        (None, 안내문구)를 반환한다.

        [Ver7.20 수정 — 자동탐색 폴백 제거] 예전에는 "⚙️ 썸네일 프롬프트
        설정" 팝업에서 이 주제에 직접 지정해둔 프롬프트 파일이 있으면
        그것을 우선 쓰고, 지정이 없으면 그룹(경제/교육/자동차) + 작업폴더
        안에서 파일명에 "썸네일"·"프롬프트"·그룹명이 모두 포함된 .md
        파일을 자동으로 찾는 폴백이 있었다. 이 폴백은 같은 작업폴더에
        여러 스타일 문서(V10, Navy계열, 텍스트배너계열 등)를 함께 두면
        파일명 사전순 정렬로 의도하지 않은 파일이 선택되는 문제가 있어
        제거했다. 이제는 주제별로 팝업에서 명시적으로 지정한 파일만
        사용하며, 지정이 없으면 그룹·자동탐색 없이 바로 안내 메시지를
        띄운다. (건강·IT를 포함한 모든 주제가 동일하게 팝업 지정을
        요구하므로, 그룹이 없어 예외 취급됐던 이전 방식보다 동작이
        일관적이다.)"""
        thumbnail_prompts = self.load_kin_thumbnail_prompts()
        prompt_filename = thumbnail_prompts.get(topic, "")
        if not prompt_filename:
            return None, (f"'{topic}' 주제에 썸네일 프롬프트가 지정되지 않았습니다.\n"
                           f"'⚙️ 썸네일 프롬프트 설정'에서 이 주제의 프롬프트 파일을 등록하세요.")

        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_folder = prompt_folder or self.prompt_folder
        template_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                style_template = f.read().strip()
        except Exception as e:
            return None, (f"'{topic}' 주제에 지정된 썸네일 프롬프트 파일을 읽을 수 "
                           f"없습니다:\n{template_path}\n{e}")
        prompt = (
            f"{style_template}\n\n"
            f"────────────────────\n\n"
            f"아래는 분석할 완성 본문입니다.\n\n"
            f"{md_text.strip()}"
        )
        return prompt, f"✅ '{prompt_filename}' (주제별 설정)으로 썸네일 프롬프트를 만들어 복사했습니다."

    def _copy_kin_thumbnail_prompt(self):
        """지금 붙여넣어둔 완성 본문 기준으로 썸네일 프롬프트를 만들어
        클립보드에 복사한다.
        [Ver7.85 이전] "8)2차 각색" 탭 안에 있던 완성 본문(web2nd_text)
        대신, 별도로 분리된 "9)썸네일/인포그래픽" 탭 자체의 붙여넣기
        칸(thumb_text)·주제 선택(thumb_topic_var)을 사용하도록 변경."""
        md_text = self.thumb_text.get("1.0", tk.END).strip()
        if not md_text:
            messagebox.showwarning("알림", "먼저 완성 본문을 붙여넣으세요.")
            return

        topic = self.thumb_topic_var.get().split('  (')[0]
        prompt, msg = self._build_kin_thumbnail_prompt(topic, md_text)

        if prompt is None:
            self.thumb_result_var.set(f"⚠️ {msg}")
            messagebox.showwarning("템플릿 없음", msg)
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        self.thumb_result_var.set(msg)
        self.log(f"🖼 썸네일 프롬프트 + 자료 복사 완료 (주제: {topic})")
        self._thumb_mark_used()  # [Ver7.87] 좌측 목록에서 선택된 항목이면 ✅ 표시

    def _copy_kin_thumbnail_prompt_only(self):
        """[Ver7.73 신규] "🖼 썸네일 프롬프트 + 자료 복사"와 달리, 완성 본문을
        붙여넣지 않은 대신 주제별로 지정된 스타일 템플릿(C) 원문 그 자체만
        클립보드에 복사한다("자료만 복사"의 정반대 짝). 완성 본문 유무와
        무관하게 동작하며(_copy_kin_thumbnail_prompt처럼 본문이 비어있다고
        막지 않음), 템플릿을 못 찾으면 동일하게 안내 메시지를 띄운다.
        [Ver7.85 이전] "9)썸네일/인포그래픽" 탭 전용 위젯 사용.
        [Ver8.24 추가] "🖼 프롬프트+자료 복사"/"자료만 복사"와 동일하게,
        좌측 목록에서 선택된 항목이 있으면 완료(✅) 표시가 남도록
        _thumb_mark_used()를 호출한다."""
        topic = self.thumb_topic_var.get().split('  (')[0]
        thumbnail_prompts = self.load_kin_thumbnail_prompts()
        prompt_filename = thumbnail_prompts.get(topic, "")
        if not prompt_filename:
            msg = (f"'{topic}' 주제에 썸네일 프롬프트가 지정되지 않았습니다.\n"
                   f"'⚙️ 썸네일 프롬프트 설정'에서 이 주제의 프롬프트 파일을 등록하세요.")
            self.thumb_result_var.set(f"⚠️ {msg}")
            messagebox.showwarning("템플릿 없음", msg)
            return

        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_folder = prompt_folder or self.prompt_folder
        template_path = os.path.join(prompt_folder, prompt_filename)
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                style_template = f.read().strip()
        except Exception as e:
            msg = (f"'{topic}' 주제에 지정된 썸네일 프롬프트 파일을 읽을 수 "
                   f"없습니다:\n{template_path}\n{e}")
            self.thumb_result_var.set(f"⚠️ {msg}")
            messagebox.showwarning("파일 읽기 실패", msg)
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_THUMBNAIL_PROMPT_CONTINUITY_NOTICE + style_template)
        msg = f"✅ '{prompt_filename}' 프롬프트 템플릿만(본문 제외) 복사했습니다."
        self.thumb_result_var.set(msg)
        self.log(f"📝 썸네일 프롬프트만 복사 완료 (주제: {topic})")
        self._thumb_mark_used()  # [Ver8.24] 좌측 목록에서 선택된 항목이면 ✅ 표시

    def _copy_kin_thumbnail_material_only(self):
        """[Ver7.20 신규] "자료만 복사" — 1차각색/2차각색 등 프로그램
        전반에서 이미 쓰이던 명명 규칙(_web1st_copy_material_only,
        _web2nd_copy_material_only)과 통일했다. 썸네일 스타일 템플릿
        (V10 등, 대개 매우 긴 문서)을 같은 Claude 대화창에 이미 한 번
        전달한 상태에서, 이어서 다른 글의 썸네일을 만들 때 전용 —
        템플릿을 다시 붙여넣지 않고 완성 본문만 클립보드에 복사한다.
        반드시 '🖼 썸네일 프롬프트 복사'를 먼저 실행한 그 대화창에서
        이어 써야 한다(새 대화창에는 스타일 규칙이 없어 실패한다).
        [Ver7.85 이전] "9)썸네일/인포그래픽" 탭 전용 위젯 사용."""
        md_text = self.thumb_text.get("1.0", tk.END).strip()
        if not md_text:
            messagebox.showwarning("알림", "먼저 완성 본문을 붙여넣으세요.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(KIN_THUMBNAIL_MATERIAL_LABEL + md_text)
        topic = self.thumb_topic_var.get().split('  (')[0]
        self.thumb_result_var.set(
            "✅ 완성 본문만 복사했습니다. (스타일 규칙을 이미 전달한 그 대화창에 Ctrl+V)")
        self.log(f"📋 썸네일용 자료만 복사 (주제: {topic})")
        self._thumb_mark_used()  # [Ver7.87] 좌측 목록에서 선택된 항목이면 ✅ 표시

    def _copy_kin_thumbnail_gemini_prompt(self):
        """[Ver7.20 신규] 방금 위에서 만든 썸네일 프롬프트(V10 등)의
        분석 결과를 재미나이(Gemini) 이미지 생성용으로 변환하는 프롬프트를
        클립보드에 복사한다. 정책뉴스 프로그램의 "프롬프트D"와 동일한
        설계 — 변환 프롬프트 원문 자체가 "바로 위에서 만든 기획 결과를
        입력받는다"고 정의돼 있으므로, 반드시 '🖼 썸네일 프롬프트 복사'로
        만든 프롬프트를 실행한 바로 그 Claude 대화창에서 이어 써야 한다.
        [Ver7.58 변경] 예전에는 주제와 무관하게 파일 1개만 썼는데(전체
        주제 공용), 이제는 주제별로 다르게 지정할 수 있다. 주제별 값이
        비어있으면 예전 공용 값으로 자동 폴백한다(_kin_get_gemini_prompt_
        filename).
        [Ver7.85 이전] "9)썸네일/인포그래픽" 탭 전용 위젯 사용."""
        topic = self.thumb_topic_var.get().split('  (')[0]
        gemini_filename = self._kin_get_gemini_prompt_filename(topic)
        if not gemini_filename:
            msg = ("재미나이 변환 프롬프트가 지정되지 않았습니다.\n"
                   "'⚙️ 썸네일 프롬프트 설정'에서 이 주제의 '프롬프트D(재미나이 변환)' 파일을 등록하세요.")
            self.thumb_result_var.set(f"⚠️ {msg}")
            messagebox.showwarning("변환 프롬프트 없음", msg)
            return

        prompt_folder = self.prompt_folder_var.get().strip() if hasattr(self, 'prompt_folder_var') else self.prompt_folder
        prompt_folder = prompt_folder or self.prompt_folder
        template_path = os.path.join(prompt_folder, gemini_filename)
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                gemini_template = f.read().strip()
        except Exception as e:
            msg = f"재미나이 변환 프롬프트 파일을 읽을 수 없습니다:\n{template_path}\n{e}"
            self.thumb_result_var.set(f"⚠️ {msg}")
            messagebox.showwarning("파일 읽기 실패", msg)
            return

        content = (
            f"{gemini_template}\n\n"
            f"────────────────────\n\n"
            f"[입력값]\n"
            f"바로 위에서 만든 '{topic}' 주제 썸네일 프롬프트의 분석 결과(1~17번 항목 등\n"
            f"핵심 오브젝트·배지 아이콘·핵심 키워드·색상·배경 등 전체)를 그대로 사용해주세요.\n"
            f"(다시 붙여넣지 않습니다 — 같은 대화창의 바로 위 turn을 참고하세요)\n"
            f"────────────────────\n"
            f"위 분석 결과를 바탕으로 재미나이(Gemini) 이미지 생성용 프롬프트로 변환해주세요."
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        msg = f"✅ '{gemini_filename}'으로 재미나이 변환 프롬프트를 만들어 복사했습니다. (썸네일 프롬프트를 실행한 그 대화창에 Ctrl+V)"
        self.thumb_result_var.set(msg)
        self.log(f"🔁 재미나이 변환 프롬프트 복사 완료 (주제: {topic})")

    def _clear_thumb_tab(self):
        """[Ver7.85 신규] "9)썸네일/인포그래픽" 탭 전체 초기화 - 붙여넣은
        완성 본문과 결과 안내 문구를 지운다(주제 선택은 유지).
        [Ver7.87 추가] 좌측 목록 선택 참조도 함께 초기화 - 안 그러면
        지운 뒤 수동으로 새 글을 붙여넣어도 이전 선택 항목이 ✅ 표시될
        수 있다."""
        self.thumb_text.delete("1.0", tk.END)
        self.thumb_result_var.set("")
        self._thumb_selected_item = None

    def _clear_web2nd(self):
        """웹 2차 탭 전체 초기화"""
        self.web2nd_text.delete("1.0", tk.END)
        self.web2nd_title_var.set("(마크다운을 붙여넣으면 자동 추출됩니다)")
        self.web2nd_filename_var.set("")
        self.web2nd_path_var.set("")
        self.web2nd_char_count_var.set("")
        self.web2nd_save_btn.config(state=tk.DISABLED)
        self._web2nd_selected_item = None  # [Ver7.17 추가]
        # [Ver9.08 최종] 제목 확정 상태도 함께 초기화 - 다음 자료로 넘어갔는데
        # 이전 확정 안내·저장 버튼 활성 상태가 남아있지 않도록 한다.
        self._web2nd_title_confirmed = False
        self._web2nd_reset_title_candidates_ui()

    def _count_md_files(self, topic):
        base = self.base_folder_var.get().strip() or self.base_folder
        tp = os.path.join(base, topic)
        if not os.path.exists(tp):
            return 0
        cnt = 0
        for dd in os.listdir(tp):
            dp = os.path.join(tp, dd)
            if not os.path.isdir(dp):
                continue
            for fd in os.listdir(dp):
                if "final_articles" in fd:
                    fp = os.path.join(dp, fd)
                    for entry in os.listdir(fp):
                        entry_path = os.path.join(fp, entry)
                        if entry.endswith('.md') and os.path.isfile(entry_path):
                            cnt += 1
                        elif os.path.isdir(entry_path):
                            # 폴더모드 저장 - 제목별 하위폴더 안의 md도 포함
                            cnt += len([f for f in os.listdir(entry_path) if f.endswith('.md')])
        return cnt

    def _refresh_web2nd_counts(self):
        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]
        current = self.web2nd_topic_var.get().split('  (')[0]
        new_display = ["{}  ({}개)".format(t, self._count_md_files(t)) for t in topics]
        self.web2nd_combo['values'] = new_display
        matched = next((d for d in new_display if d.startswith(current)), new_display[0])
        self.web2nd_topic_var.set(matched)

    # [Ver7.85 신규, Ver7.87 좌우분할로 재구성] 썸네일/인포그래픽 전용 탭 —
    # "8)2차 각색"에 섞여 있던 썸네일 생성 버튼 5개를 분리. "8)2차 각색"과
    # "9)통합 키워드" 사이에 배치(뒤 탭들은 9→10, 10→11, 11→12로 한 칸씩
    # 밀림). 본문 작성/저장 화면과 썸네일 이미지 프롬프트 작업 화면이
    # 하나로 묶여 있어 헷갈린다는 피드백에 따라 처음엔 수동 붙여넣기
    # 전용 단일 화면으로 분리했었으나("완성 본문을 여기 다시 붙여넣어야
    # 함"), 탭이 통합되어 있을 때는 "8)2차 각색"의 좌측 목록·저장 흐름을
    # 그대로 이어 썼던 것이므로 탭을 분리했으면 그 목록도 자동으로 이
    # 탭에 딸려와야 한다는 지적을 반영해 재구성함. "2/3/4/7/8"번 탭과
    # 동일한 좌(완성 자료 목록)/우(내용+버튼) 좌우분할 구조로 바꾸고,
    # 좌측에서 완성된 2차 결과물(final_articles)을 선택하면 파일 내용을
    # 자동으로 읽어와 우측 본문 칸에 채운다(수동 붙여넣기 불필요). 생성된
    # 프롬프트 자체는 파일로 저장하지 않고 그대로 클립보드 복사 → 웹
    # AI에 붙여넣는 기존 워크플로우 그대로 유지(요청사항).
    def create_thumbnail_tab(self):
        """9) 썸네일/인포그래픽 전용 탭"""
        frame = ttk.Frame(self.notebook, padding="6")
        self.notebook.add(frame, text="9)썸네일/인포그래픽")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # ── 왼쪽: 완성된 2차 결과물(final_articles) 목록 ──
        left = ttk.Frame(paned, padding=(4, 4, 8, 4))
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)

        ttk.Label(left, text="📋 썸네일 만들 완성 글 선택 (2차 각색 결과물)", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        topic_row = ttk.Frame(left)
        topic_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(topic_row, text="주제:").pack(side=tk.LEFT, padx=(0, 5))

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        def count_thumb_items(topic):
            base = self.base_folder_var.get().strip() or self.base_folder
            return len(self._scan_final_articles_items(base, topic))

        display_topics = [f"{t}  ({count_thumb_items(t)}개)" for t in topics]
        self.thumb_topic_var = tk.StringVar(value=display_topics[0])
        self.thumb_combo = ttk.Combobox(
            topic_row, textvariable=self.thumb_topic_var,
            values=display_topics, state="readonly", width=45, height=11
        )
        self.thumb_combo.pack(side=tk.LEFT)

        self.thumb_hide_used_var = tk.BooleanVar(value=self.load_kin_ui_setting('hide_used_thumb_picker', False))
        ttk.Checkbutton(left, text="썸네일 생성한 자료 숨기기", variable=self.thumb_hide_used_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        thumb_filter_row = ttk.Frame(left)
        thumb_filter_row.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(thumb_filter_row, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.thumb_date_var = tk.StringVar()
        thumb_date_entry = ttk.Entry(thumb_filter_row, textvariable=self.thumb_date_var, width=11)
        thumb_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        thumb_date_entry.bind("<Return>", lambda e: self._thumb_refresh_list())
        ttk.Button(thumb_filter_row, text="오늘",
                   command=lambda: (self.thumb_date_var.set(__import__('datetime').datetime.now().strftime("%Y-%m-%d")), self._thumb_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(thumb_filter_row, text="↺", width=3,
                   command=lambda: (self.thumb_date_var.set(""), self._thumb_refresh_list())
                   ).pack(side=tk.LEFT, padx=(0, 8))
        self.thumb_list_count_var = tk.StringVar(value="")
        ttk.Label(thumb_filter_row, textvariable=self.thumb_list_count_var, foreground="navy").pack(side=tk.LEFT)

        list_frame = ttk.Frame(left)
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("used", "title", "date", "folder")
        self.thumb_list_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        self.thumb_list_tree.heading("used", text="생성")
        self.thumb_list_tree.heading("title", text="제목")
        self.thumb_list_tree.heading("date", text="날짜")
        self.thumb_list_tree.heading("folder", text="폴더(모델)")
        self.thumb_list_tree.column("used", width=40, anchor=tk.CENTER)
        self.thumb_list_tree.column("title", width=260)
        self.thumb_list_tree.column("date", width=80, anchor=tk.CENTER)
        self.thumb_list_tree.column("folder", width=140)
        self.thumb_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.thumb_list_tree.yview)
        self.thumb_list_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # [핵심] 목록에서 선택(클릭)하는 순간 파일 내용을 자동으로 읽어와
        # 우측 본문 칸에 채운다 - 수동으로 다시 붙여넣을 필요가 없다.
        self.thumb_list_tree.bind("<<TreeviewSelect>>", self._thumb_on_list_select)

        self._thumb_list_cache = {'items': [], 'usage': {}}
        self._thumb_selected_item = None

        # [2026-09-27] 우측 하단에 있던 목록 관련 버튼(프롬프트/자료 복사 계열,
        # 재미나이 변환, 프롬프트 설정)을 "7)1차 각색"/"8)2차 각색" 탭처럼
        # 좌측 목록 아래로 이동. 함수/동작은 그대로이고 배치만 옮김.
        list_btn_frame = ttk.Frame(left)
        list_btn_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame, text="🖼 프롬프트+자료 복사",
                   command=self._copy_kin_thumbnail_prompt).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="📝 프롬프트만 복사",
                   command=self._copy_kin_thumbnail_prompt_only).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame, text="자료만 복사",
                   command=self._copy_kin_thumbnail_material_only).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame_g = ttk.Frame(left)
        list_btn_frame_g.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        ttk.Button(list_btn_frame_g, text="🔁 재미나이 변환 프롬프트 복사",
                   command=self._copy_kin_thumbnail_gemini_prompt).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame_g, text="⚙️ 썸네일 프롬프트 설정",
                   command=self.open_kin_thumbnail_prompt_settings).pack(side=tk.LEFT, padx=(0, 4))
        list_btn_frame2 = ttk.Frame(left)
        list_btn_frame2.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))
        # [Ver8.24 신규] "8)2차 각색" 탭과 동일한 "사용여부 토글" 버튼 -
        # 자동 ✅ 표시(_thumb_mark_used)와 별개로 수동으로 켜고 끌 수 있게 함.
        ttk.Button(list_btn_frame2, text="사용여부 토글",
                   command=self._thumb_toggle_used).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(list_btn_frame2, text="🔄 새로고침",
                   command=self._thumb_refresh_list).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(left, text="※ 목록을 클릭하면 오른쪽 본문 칸에 자동으로 채워집니다.\n"
                              "생성된 프롬프트는 저장하지 않고 그대로 웹 AI에 복사/붙여넣기만 합니다.",
                  justify=tk.LEFT, foreground="blue").grid(
            row=8, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # ── 오른쪽: 본문(자동 로드/수동 붙여넣기 겸용) + 썸네일 버튼 ──
        right = ttk.Frame(paned, padding=(8, 4, 4, 4))
        paned.add(right, weight=3)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(right, text="📋 완성 본문 (왼쪽 목록 선택 시 자동 로드, 필요시 직접 붙여넣기도 가능)",
                  font=("", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 4))

        self.thumb_text = scrolledtext.ScrolledText(right, wrap=tk.WORD, height=24)
        self.thumb_text.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=2, column=0, pady=(8, 0), sticky=tk.W)

        # [2026-09-27] 복사 계열/재미나이/프롬프트 설정 버튼은 좌측 목록 아래로 이동함.
        ttk.Button(btn_frame, text="내용 지우기",
                   command=self._clear_thumb_tab).pack(side=tk.LEFT, padx=(0, 8))
        # [Ver8.21 신규] "8)2차 각색" 탭에 있던 "📋 제목 복사" 버튼을 이곳으로
        # 이동 - 인포그래픽 이미지 파일명에 제목을 쓰므로 9)탭에 있는 게
        # 맞다는 사용자 확인. thumb_text(9)탭 본문칸) 기준으로 제목을 추출.
        ttk.Button(btn_frame, text="📋 제목 복사",
                   command=self._copy_thumb_title).pack(side=tk.LEFT, padx=(0, 8))
        # [Ver8.23 신규] "8)2차 각색" 탭의 "📁 저장폴더 열기"와 동일 패턴 -
        # 왼쪽 목록에서 선택한 완성 글의 MD 파일이 실제로 저장돼 있는 폴더를 연다.
        ttk.Button(btn_frame, text="📁 저장폴더 열기",
                   command=self._open_thumb_save_folder).pack(side=tk.LEFT, padx=(0, 8))

        self.thumb_result_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.thumb_result_var,
                  foreground="darkgreen", wraplength=700, justify=tk.LEFT).grid(
            row=3, column=0, sticky=tk.W, pady=(8, 0))

        # 주제 변경 시 목록 갱신
        self.thumb_topic_var.trace_add("write", lambda *_: self._thumb_refresh_list())
        self.thumb_hide_used_var.trace_add("write", lambda *_: self._thumb_refresh_list())
        self.thumb_hide_used_var.trace_add(
            "write", lambda *_: self.save_kin_ui_setting('hide_used_thumb_picker', self.thumb_hide_used_var.get()))

        self._thumb_refresh_list()

    def _thumb_refresh_list(self):
        """[Ver7.87 신규] "9)썸네일/인포그래픽" 탭 좌측 목록 새로고침 -
        "5)웹2차 각색" 등 다른 탭들의 _web2nd_refresh_list와 동일한 패턴."""
        if not hasattr(self, 'thumb_list_tree'):
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.thumb_topic_var.get().split('  (')[0]
        self.thumb_list_tree.delete(*self.thumb_list_tree.get_children())
        items = self._scan_final_articles_items(base, topic)
        usage = self._load_thumb_usage(base, topic)
        self._thumb_list_cache['items'] = items
        self._thumb_list_cache['usage'] = usage
        date_filter = self.thumb_date_var.get().strip() if hasattr(self, 'thumb_date_var') else ""
        shown = 0
        for i, item in enumerate(items):
            used = usage.get(item["title"], False)
            if self.thumb_hide_used_var.get() and used:
                continue
            if date_filter and item["date"] != date_filter:
                continue
            self.thumb_list_tree.insert("", tk.END, iid=str(i), values=(
                "✅" if used else "", item["title"], item["date"], item["folder"]
            ))
            shown += 1

        if hasattr(self, 'thumb_list_count_var'):
            total = len(items)
            if date_filter:
                self.thumb_list_count_var.set(f"검색결과 {shown}개 / 전체 {total}개")
            else:
                self.thumb_list_count_var.set(f"총 {total}개")

    def _thumb_on_list_select(self, event=None):
        """[Ver7.87 신규] 좌측 목록에서 항목을 클릭하면 해당 완성 글
        파일을 즉시 읽어 우측 본문 칸(thumb_text)에 자동으로 채운다.
        다른 탭들처럼 "선택→복사" 대신 여기서는 프롬프트 생성 재료가
        파일 내용 그 자체이므로, 선택 즉시 로드해두면 바로 버튼을 눌러
        프롬프트를 만들 수 있다(수동 붙여넣기 불필요)."""
        sel = self.thumb_list_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        try:
            item = self._thumb_list_cache['items'][idx]
        except (IndexError, KeyError):
            return
        try:
            with open(item["file_path"], 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{e}")
            return
        self.thumb_text.delete("1.0", tk.END)
        self.thumb_text.insert("1.0", content)
        self._thumb_selected_item = item
        self.thumb_result_var.set(f"📄 '{item['title']}' 본문을 불러왔습니다.")

    def _open_thumb_save_folder(self):
        """[Ver8.23 신규] "8)2차 각색" 탭의 _open_web2nd_save_folder와 동일
        패턴 - 왼쪽 목록에서 선택한 완성 글의 MD 파일이 실제로 들어있는
        폴더(final_articles 폴더, 폴더형 저장이면 제목별 하위폴더까지)를
        연다. 9)탭은 자체 저장을 하지 않고 기존 완성 파일을 불러오기만
        하므로, "저장된 폴더"는 곧 선택된 항목의 file_path가 있는 폴더."""
        item = self._thumb_selected_item
        if not item:
            messagebox.showwarning("알림", "왼쪽 목록에서 완성 글을 먼저 선택하세요.")
            return
        folder = os.path.dirname(item["file_path"])
        try:
            os.makedirs(folder, exist_ok=True)
            if os.name == "nt":
                os.startfile(folder)
            else:
                import subprocess, platform
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
            self.log(f"📁 저장폴더 열기(9탭): {folder}")
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 여는 중 오류가 발생했습니다:\n{e}")

    def _thumb_mark_used(self):
        """[Ver7.87 신규] 방금 프롬프트를 만든 항목을 '생성완료(✅)'로
        표시 - 좌측 목록에서 선택된 상태였을 때만 기록(수동 붙여넣기로
        작업한 경우는 대상 항목이 없으므로 건너뜀)."""
        item = self._thumb_selected_item
        if not item:
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.thumb_topic_var.get().split('  (')[0]
        usage = self._load_thumb_usage(base, topic)
        usage[item["title"]] = True
        self._save_thumb_usage(base, topic, usage)
        self._thumb_refresh_list()

    def _thumb_toggle_used(self):
        """[Ver8.24 신규] "9)썸네일/인포그래픽" 탭 좌측 목록의 사용여부(✅)를
        수동으로 켜고 끌 수 있게 함 - "8)2차 각색" 탭의 _web2nd_toggle_used와
        동일한 패턴. 복사 버튼을 누르면 자동으로 ✅ 표시되지만(_thumb_mark_used),
        잘못 표시된 항목을 되돌리거나 아직 프롬프트를 만들지 않았어도 미리
        완료 처리해두고 싶을 때 좌측 목록에서 항목을 선택한 뒤 이 버튼으로
        직접 켜고 끌 수 있다."""
        sel = self.thumb_list_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 먼저 선택하세요.")
            return
        idx = int(sel[0])
        try:
            item = self._thumb_list_cache['items'][idx]
        except (IndexError, KeyError):
            return
        base = self.base_folder_var.get().strip() or self.base_folder
        topic = self.thumb_topic_var.get().split('  (')[0]
        usage = self._thumb_list_cache['usage']
        new_state = not usage.get(item["title"], False)
        usage[item["title"]] = new_state
        self._save_thumb_usage(base, topic, usage)
        self._kin_mark_row_used(self.thumb_list_tree, sel[0], self.thumb_hide_used_var,
                                 self._thumb_refresh_list, used=new_state)

    def _scan_final_articles_items(self, base_folder, topic):
        """[Ver7.87 신규] base/주제/날짜/perplexity_*_final_articles/ 안의
        완성된 2차 각색 결과(최종 본문) MD 파일들을 스캔한다 - "9)썸네일/
        인포그래픽" 탭 좌측 목록용. 폴더형 저장(제목별 하위폴더)과
        평면형 저장(final_articles 바로 아래 .md) 둘 다 지원(count_md_files
        와 동일한 판정 방식)."""
        items = []
        topic_path = os.path.join(base_folder, topic)
        if not os.path.exists(topic_path):
            return items

        for date_folder in os.listdir(topic_path):
            date_path = os.path.join(topic_path, date_folder)
            if not os.path.isdir(date_path):
                continue
            for folder_name in os.listdir(date_path):
                if "final_articles" not in folder_name:
                    continue
                final_path = os.path.join(date_path, folder_name)
                if not os.path.isdir(final_path):
                    continue
                for entry in os.listdir(final_path):
                    entry_path = os.path.join(final_path, entry)
                    if entry.endswith('.md') and os.path.isfile(entry_path):
                        items.append({
                            "title": entry[:-3],
                            "date": date_folder,
                            "folder": folder_name,
                            "file_path": entry_path,
                        })
                    elif os.path.isdir(entry_path):
                        for sub in os.listdir(entry_path):
                            if sub.endswith('.md'):
                                items.append({
                                    "title": sub[:-3],
                                    "date": date_folder,
                                    "folder": folder_name,
                                    "file_path": os.path.join(entry_path, sub),
                                })
        # 새로 저장된 항목이 항상 맨 아래로 가도록 실제 파일 수정시각 기준 정렬
        items.sort(key=lambda x: os.path.getmtime(x["file_path"]) if os.path.exists(x["file_path"]) else 0)
        return items

    def _get_thumb_usage_path(self, base_folder, topic):
        return os.path.join(base_folder, topic, "썸네일_사용여부.json")

    def _load_thumb_usage(self, base_folder, topic):
        path = self._get_thumb_usage_path(base_folder, topic)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_thumb_usage(self, base_folder, topic, usage):
        path = self._get_thumb_usage_path(base_folder, topic)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

    # 통합키워드 관리
    def create_step3_tab(self):
        """3단계: 통합 키워드 관리 탭"""
        step3_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(step3_frame, text="10)통합 키워드 등록")
        
        # 설명
        info_text = """
        📌 전체 주제 폴더의 키워드를 통합 관리합니다:
        • 모든 주제 폴더(경제-법률, 건강-의학 등)의 MD 파일들을 스캔
        • Naver_blog_지식인통합_keyword.xlsx 파일과 중복 검사
        • O 표시된 키워드만 선택하여 통합 엑셀에 추가
        """
        
        info_label = ttk.Label(step3_frame, text=info_text, justify=tk.LEFT, foreground="blue")
        info_label.grid(row=0, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # 엑셀 파일 선택
        excel_frame = ttk.LabelFrame(step3_frame, text="통합 키워드 엑셀 파일", padding="8")
        excel_frame.grid(row=1, column=0, columnspan=3, pady=(0, 8), sticky=(tk.W, tk.E))
        excel_frame.columnconfigure(1, weight=1)
        
        ttk.Label(excel_frame, text="파일명:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(excel_frame, textvariable=self.excel_keyword_filename_var, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(excel_frame, text="파일 선택", command=self.select_excel_keyword_file).grid(
            row=0, column=2
        )


        # ========================================
        # ✅ 새로 추가: 모델 폴더 선택
        # ========================================
        model_select_frame = ttk.LabelFrame(step3_frame, text="사용된 모델의 최종 결과물 폴더 선택", padding="10")
        model_select_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # 체크박스 생성
        ttk.Checkbutton(model_select_frame, text="GPT 최종 (perplexity_GPT_final_articles)",
            variable=self.check_gpt_folder).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Checkbutton(model_select_frame, text="Gemini 최종 (perplexity_Gemini_final_articles)",
            variable=self.check_gemini_folder).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Checkbutton(model_select_frame, text="Claude 최종 (perplexity_Claude_final_articles)",
            variable=self.check_claude_folder).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        # [Ver7.39 추가] 다중질문검색(종합완성판) 저장 폴더도 중복 검사 대상에 포함
        ttk.Checkbutton(model_select_frame, text="종합완성판 최종 (perplexity_종합완성판_final_articles)",
            variable=self.check_comprehensive_folder).grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        
        # ========================================
        # 기존 코드 계속 (row 번호만 +1)
        # ========================================
        
        # 중복률 설정
        threshold_frame = ttk.Frame(step3_frame)
        threshold_frame.grid(row=3, column=0, columnspan=3, pady=10)  # ← row=1에서 2로 변경
        
        ttk.Label(threshold_frame, text="중복률 임계값:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        saved_threshold = "50"
        try:
            import json
            if os.path.exists(self.get_kin_config_path()):
                with open(self.get_kin_config_path(), 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                saved_threshold = cfg.get('duplicate_threshold', '50')
        except:
            pass
        self.step3_threshold_var = tk.StringVar(value=saved_threshold)

        ttk.Entry(threshold_frame, textvariable=self.step3_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Label(threshold_frame, text="% 이상이면 중복으로 판정").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 실행 버튼
        button_frame = ttk.Frame(step3_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)  # ← row=2에서 3으로 변경
        
        self.step3_check_button = ttk.Button(button_frame, text="🔍 전체 날짜 중복 검사", command=self.start_all_dates_duplicate_check)
        self.step3_check_button.grid(row=0, column=0, padx=5)
        
        self.step3_add_button = ttk.Button(button_frame, text="✅ 통합파일에 키워드 추가", command=self.add_keywords_to_all_excel)
        self.step3_add_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="💾 환경파일 저장", command=self.manual_save_config).grid(row=0, column=2, padx=5)

        # 기존 버튼들 아래에 추가
        self.reorganize_btn = tk.Button(
            button_frame, 
            text="📂 경제통합 자료 모으기", 
            command=self.start_reorganize_folders,
            bg="#E74C3C",  # 빨간색 계열
            fg="white",
            font=('나눔고딕', 10, 'bold'),
            relief=tk.RAISED,
            padx=8
        )
        self.reorganize_btn.grid(row=0, column=3, padx=5)

        # [Ver7.78 추가] "경제통합 자료 모으기" 실행 후 결과물이 쌓이는
        # base_folder/경제통합/오늘날짜/perplexity_collected_final_articles/
        # 폴더를 바로 열어 확인할 수 있는 버튼. 아직 실행 전(폴더가 없는
        # 상태)에도 누르면 os.makedirs로 만들고 열어준다(다른 "저장폴더
        # 열기" 버튼들과 동일한 패턴 - _open_web2nd_save_folder 참고).
        ttk.Button(button_frame, text="📁 경제통합 폴더 열기",
                   command=self._open_econ_collect_folder).grid(row=0, column=4, padx=5)

        # 진행 상황
        progress_frame = ttk.LabelFrame(step3_frame, text="엑셀 중복 체크 진행 상황", padding="5")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)  # ← row=3에서 4로 변경
        
        self.step3_progress_var = tk.StringVar(value="대기 중...")
        ttk.Label(progress_frame, textvariable=self.step3_progress_var).grid(row=0, column=0, sticky=tk.W)
        
        # 프로그레스바 추가
        self.step3_progressbar = ttk.Progressbar(progress_frame, mode='determinate', maximum=100)
        self.step3_progressbar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        progress_frame.columnconfigure(0, weight=1)

    # ──────────────────────────────────────────────────────
    # 종합관리 : 포스팅DB 조회 / 삭제 (주제=블로그 별로 관리)
    # ──────────────────────────────────────────────────────
    def create_db_manage_tab(self):
        """포스팅DB 종합관리 탭 - 주제별 조회 + 수동 삭제 (DB만 삭제, MD 파일은 유지)"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="12)포스팅 이력관리")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

        ttk.Label(frame,
            text="주제(=블로그)별 포스팅DB를 조회하고, 필요 없는 기록을 삭제할 수 있습니다.\n"
                 "※ 여기서 삭제해도 실제 MD 파일은 지워지지 않고, 중복비교용 DB 기록만 삭제됩니다.\n"
                 "다중선택 가능 (Ctrl+클릭 또는 Shift+클릭) → 삭제도 여러 개 한번에 가능",
            foreground="gray", justify=tk.LEFT).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        topics = [
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        self._db_manage_topics = topics  # [Ver7.44] 전체 주제 순회용으로 보관
        # [Ver7.72 추가] "경제(A~G) 모아보기"용 - 경제 세부주제 7개만 별도 보관
        # (다른 여러 곳의 ECON_TOPICS와 동일한 7개, 이름만 로컬로 새로 둠).
        self._db_manage_econ_topics = [t for t in topics if t.startswith("경제-")]

        top_frame = ttk.Frame(frame)
        top_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Label(top_frame, text="주제:").pack(side=tk.LEFT, padx=(0, 5))
        self.db_manage_topic_var = tk.StringVar(value=topics[0])
        self.db_manage_topic_combo = ttk.Combobox(
            top_frame, textvariable=self.db_manage_topic_var, values=topics,
            state="readonly", width=40, height=11)
        self.db_manage_topic_combo.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_frame, text="🔄 새로고침", command=self._refresh_db_manage_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="🗑️ 선택 삭제", command=self._delete_db_manage_selected).pack(side=tk.LEFT)
        self.db_manage_integrity_btn = ttk.Button(
            top_frame, text="🔍 파일 무결성 검사", command=self._check_db_file_integrity)
        self.db_manage_integrity_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.db_manage_topic_var.trace_add("write", lambda *_: self._refresh_db_manage_list())

        # [Ver7.72 추가] 경제 세부주제 7개(경제-A~G)가 실제로는 "경제통합"
        # 블로그 하나로 운영되는데도 주제DB는 A~G로 쪼개져 있어 매번 7번
        # 주제를 바꿔가며 봐야 하는 불편함이 있었음. 체크 시 경제-A~G 7개
        # DB를 전부 훑어 하나의 목록으로 모아 보여준다.
        self.db_manage_show_econ_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            top_frame, text="💰 경제(A~G) 모아보기",
            variable=self.db_manage_show_econ_var,
            command=self._on_db_manage_toggle_mode
        ).pack(side=tk.LEFT, padx=(10, 0))

        # [Ver7.46 추가] "중복 기록 일괄 정리" - 실수로 같은 글이 여러 번
        # 저장돼 포스팅DB에 거의 동일한 기록이 쌓인 경우를 한 번에 찾아
        # 정리하는 기능. 11개 주제 DB를 전부 훑어(비교는 항상 같은 주제
        # 안에서만) 임계값(%) 이상 겹치는 레코드들을 그룹으로 묶어 미리보기
        # 팝업으로 보여주고, 사람이 그룹마다 남길 1건을 확인/선택한 뒤에만
        # 실제 삭제가 실행된다(완전 자동삭제 아님).
        dedupe_row = ttk.Frame(frame)
        dedupe_row.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))
        ttk.Button(dedupe_row, text="🧹 중복 기록 일괄 정리(전체 주제)",
                   command=self._open_db_dedupe_dialog).pack(side=tk.LEFT)
        ttk.Label(dedupe_row, text="  판정 기준:").pack(side=tk.LEFT, padx=(6, 2))
        self.db_dedupe_threshold_var = tk.IntVar(value=90)
        ttk.Spinbox(dedupe_row, from_=70, to=100, increment=5, width=5,
                    textvariable=self.db_dedupe_threshold_var).pack(side=tk.LEFT)
        ttk.Label(dedupe_row, text="% 이상 (엄격하게 - 진짜 거의 같은 글만)",
                  foreground="gray").pack(side=tk.LEFT, padx=(4, 0))

        # [Ver7.10 추가] 검색어(버튼/엔터로 실행) + 날짜 범위 필터 + 초기화.
        # 실시간(입력할 때마다) 필터링이 아니라, 버튼을 눌러야 적용된다.
        filter_frame = ttk.Frame(frame)
        filter_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))

        ttk.Label(filter_frame, text="검색어:").pack(side=tk.LEFT, padx=(0, 4))
        self.db_manage_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.db_manage_search_var, width=22)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self._apply_db_manage_filter())

        ttk.Label(filter_frame, text="날짜:").pack(side=tk.LEFT, padx=(0, 4))
        self.db_manage_date_var = tk.StringVar()
        date_entry = ttk.Entry(filter_frame, textvariable=self.db_manage_date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=(0, 4))
        date_entry.bind("<Return>", lambda e: self._apply_db_manage_filter())
        ttk.Label(filter_frame, text="(YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(filter_frame, text="오늘",
                   command=self._set_db_manage_today).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(filter_frame, text="🔍 검색", command=self._apply_db_manage_filter).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_frame, text="↺ 필터 초기화", command=self._reset_db_manage_filter).pack(side=tk.LEFT)

        # [Ver7.44 추가] "주제" 컬럼 신설 - 평소(단일 주제 조회)에도 어느 주제인지
        # 바로 보이고, "경제(A~G) 모아보기" 모드에서는 이 컬럼이 각 기록의
        # 출처 주제를 구분하는 핵심 정보가 된다.
        columns = ("type", "topic", "title", "date", "intro")
        self.db_manage_tree = ttk.Treeview(frame, columns=columns, show="headings", height=22)
        self.db_manage_tree.heading("type", text="유형")
        self.db_manage_tree.heading("topic", text="주제")
        self.db_manage_tree.heading("title", text="제목")
        self.db_manage_tree.heading("date", text="저장일")
        self.db_manage_tree.heading("intro", text="도입부 미리보기")
        self.db_manage_tree.column("type", width=70, anchor=tk.CENTER)
        self.db_manage_tree.column("topic", width=110, anchor=tk.CENTER)
        self.db_manage_tree.column("title", width=300)
        self.db_manage_tree.column("date", width=80, anchor=tk.CENTER)
        self.db_manage_tree.column("intro", width=250)
        self.db_manage_tree.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.db_manage_tree.yview)
        self.db_manage_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))

        self.db_manage_count_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.db_manage_count_var, foreground="navy").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        self._db_manage_all_records = []
        self._db_manage_record_topics = []     # [Ver7.44] 기록별 출처 주제(병렬 리스트)
        self._db_manage_record_localidx = []   # [Ver7.44] 기록별 원본 DB 내 인덱스(병렬 리스트, 삭제용)
        self._db_manage_current_db_path = ""
        self._refresh_db_manage_list()

    def _on_db_manage_toggle_mode(self):
        """[Ver7.44 신규, Ver7.72 확장] '경제(A~G) 모아보기' 체크/해제 시
        주제 콤보박스와 파일 무결성 검사 버튼을 비활성/활성화한다. "주제
        하나" 기준으로 동작하는 기능들인데, 이 모드가 켜져 있으면 여러
        주제 기록이 함께 표시되어 어느 주제 기준인지 모호해지므로(특히
        무결성 검사를 엉뚱한 주제 기준으로 돌리는 사고를 막기 위해)
        건드릴 수 없게 막는다."""
        any_mode_on = self.db_manage_show_econ_var.get()
        self.db_manage_topic_combo.configure(state=tk.DISABLED if any_mode_on else "readonly")
        self.db_manage_integrity_btn.configure(state=tk.DISABLED if any_mode_on else tk.NORMAL)
        self._refresh_db_manage_list()

    def _refresh_db_manage_list(self):
        """선택된 주제(또는 [Ver7.72] '경제(A~G) 모아보기' 모드일 경우 경제
        세부주제 7개 전체)의 포스팅DB를 디스크에서 다시 읽어 캐시에
        저장하고, 현재 검색어/날짜 필터를 그대로 재적용해서 표시한다.

        [Ver7.44 추가] 여러 주제를 합쳐 보여주는 모드에서는 여러 DB 파일의
        기록이 하나의 리스트로 합쳐지므로, 각 기록이 "어느 주제의, 그 주제
        DB 내 몇 번째 기록인지"를 병렬 리스트(_db_manage_record_topics/
        _record_localidx)로 함께 기억해 둔다 - 나중에 삭제할 때 올바른 DB
        파일의 올바른 위치를 지우기 위해 필요하다."""
        base_folder = self.base_folder_var.get().strip() or self.base_folder

        show_econ = self.db_manage_show_econ_var.get()

        if show_econ:
            merged, rec_topics, rec_localidx = [], [], []
            for t in self._db_manage_econ_topics:
                db_path = get_posting_db_path(base_folder, t)
                recs = load_json_db(db_path)
                for i, r in enumerate(recs):
                    merged.append(r)
                    rec_topics.append(t)
                    rec_localidx.append(i)
            self._db_manage_all_records = merged
            self._db_manage_record_topics = rec_topics
            self._db_manage_record_localidx = rec_localidx
            self._db_manage_current_db_path = "(경제 A~G 모아보기)"
        else:
            topic = self.db_manage_topic_var.get()
            db_path = get_posting_db_path(base_folder, topic)
            recs = load_json_db(db_path)
            self._db_manage_all_records = recs
            self._db_manage_record_topics = [topic] * len(recs)
            self._db_manage_record_localidx = list(range(len(recs)))
            self._db_manage_current_db_path = db_path

        self._apply_db_manage_filter()

    def _apply_db_manage_filter(self):
        """캐시된 전체 레코드에 검색어(제목/도입부/마무리 부분일치, 대소문자
        무시)와 날짜 범위 필터를 적용해 트리에 표시한다. 삭제 시 원본 인덱스가
        필요하므로, 필터링 후에도 iid는 항상 필터 이전(전체) 목록 기준
        인덱스를 그대로 쓴다."""
        for item in self.db_manage_tree.get_children():
            self.db_manage_tree.delete(item)

        records = self._db_manage_all_records
        rec_topics = self._db_manage_record_topics
        keyword = self.db_manage_search_var.get().strip().lower()
        date_filter = self.db_manage_date_var.get().strip()

        shown = 0
        for i, r in enumerate(records):
            title = r.get("title", "")
            intro = r.get("intro", "")
            summary = r.get("summary", "")
            date = r.get("date", "")
            # [Ver7.20 추가] content_type은 저장 데이터에만 있는 구분용 필드 -
            # 실제 블로그에 올라가는 title 문자열 자체는 절대 건드리지 않고,
            # 표시(유형 컬럼)에서만 구분한다(제목에 접두어를 붙이면 실제
            # 포스팅 제목까지 오염될 위험이 있어 데이터와 표시를 분리함).
            type_label = "🧩종합판" if r.get("content_type") == "종합완성판" else "일반"
            # [Ver7.44 추가] 주제 컬럼 - 병렬 리스트에서 해당 기록의 출처 주제를 가져옴
            topic_label = rec_topics[i] if i < len(rec_topics) else ""

            if keyword:
                haystack = f"{title} {intro} {summary}".lower()
                if keyword not in haystack:
                    continue
            if date_filter and date != date_filter:
                continue

            self.db_manage_tree.insert("", tk.END, iid=str(i),
                values=(type_label, topic_label, title, date, intro[:60]))
            shown += 1

        total = len(records)
        # [Ver7.44 변경, Ver7.72 확장] 경제 모아보기 모드에서는 db 경로가
        # 여러 개라 단일 경로 표시가 의미 없어져, "경로" 대신 현재 조회
        # 모드를 보여주도록 함.
        show_econ = self.db_manage_show_econ_var.get()
        if show_econ:
            mode_label = "💰 경제(A~G) 모아보기"
        else:
            mode_label = self.db_manage_topic_var.get()
        if keyword or date_filter:
            self.db_manage_count_var.set(f"[{mode_label}] 검색결과 {shown}개 / 전체 {total}개")
        else:
            self.db_manage_count_var.set(f"[{mode_label}] 총 {total}개")

    def _set_db_manage_today(self):
        """'오늘' 버튼 - 날짜 필터를 오늘 날짜로 채우고 바로 검색까지 실행"""
        from datetime import datetime
        self.db_manage_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self._apply_db_manage_filter()

    def _reset_db_manage_filter(self):
        """검색어·날짜 필터를 모두 지우고 전체 목록을 다시 보여준다."""
        self.db_manage_search_var.set("")
        self.db_manage_date_var.set("")
        self._apply_db_manage_filter()

    def _delete_db_manage_selected(self):
        """선택된 레코드를 포스팅DB에서 삭제 (MD 파일은 그대로 둠)
        [Ver7.10 강화] 삭제는 되돌릴 수 없는 작업이라, 어떤 항목이
        지워지는지 제목까지 보여주는 명확한 경고창을 반드시 거치도록 함.

        [Ver7.44 변경] '경제(A~G) 모아보기' 모드에서는 선택 항목들이 서로
        다른 주제의 DB 파일에 흩어져 있을 수 있다 - _db_manage_record_topics/
        _record_localidx 병렬 리스트로 각 선택 항목의 실제 출처(주제, 그
        주제 DB 안에서의 원래 인덱스)를 찾아 주제별로 그룹핑한 뒤, 각 DB
        파일을 따로 읽고/지우고/저장한다(단일 주제 모드에서는 그룹이 하나뿐
        이라 기존과 동일하게 동작). 확인창 제목 미리보기도 기존에 "유형"
        컬럼(🧩종합판/일반)이 잘못 표시되던 것을 "제목" 컬럼으로 바로잡음."""
        selected = self.db_manage_tree.selection()
        if not selected:
            messagebox.showwarning("알림", "삭제할 항목을 먼저 선택하세요.")
            return

        titles = [self.db_manage_tree.item(iid, "values")[2] for iid in selected]  # 컬럼순: 유형/주제/제목/저장일/도입부
        preview = "\n".join(f"  • {t}" for t in titles[:10])
        if len(titles) > 10:
            preview += f"\n  … 외 {len(titles) - 10}건 더"

        if not messagebox.askyesno(
                "⚠️ 삭제 확인 (되돌릴 수 없음)",
                f"아래 {len(selected)}개 기록을 포스팅DB에서 영구 삭제합니다.\n"
                f"이 작업은 되돌릴 수 없습니다.\n\n"
                f"{preview}\n\n"
                f"(실제 MD 파일은 삭제되지 않고, 중복비교용 DB 기록만 지워집니다)\n\n"
                f"정말 삭제하시겠습니까?",
                icon="warning"):
            return

        base_folder = self.base_folder_var.get().strip() or self.base_folder

        by_topic = {}
        for iid in selected:
            i = int(iid)
            topic = self._db_manage_record_topics[i]
            local_idx = self._db_manage_record_localidx[i]
            by_topic.setdefault(topic, []).append(local_idx)

        total_deleted = 0
        for topic, local_indices in by_topic.items():
            db_path = get_posting_db_path(base_folder, topic)
            records = load_json_db(db_path)
            for idx in sorted(set(local_indices), reverse=True):
                if 0 <= idx < len(records):
                    rec = records[idx]
                    # [2026-09-27 3차] 포스팅DB 기록 삭제와 같이, 그 글이
                    # 들어있던 final_articles 폴더의 사이드카 줄도 지운다.
                    final_folder = self._kin_find_final_articles_folder(rec.get("file_path"))
                    if final_folder:
                        self._kin_sidecar_remove(final_folder, rec.get("title"))
                    del records[idx]
                    total_deleted += 1
            save_json_db(db_path, records)

        self.log(f"🗑️ 포스팅DB 삭제 완료: {total_deleted}개 (주제 {len(by_topic)}곳: {', '.join(by_topic.keys())})")
        self._refresh_db_manage_list()

    # [Ver7.10 추가] 포스팅DB 기록과 실제 파일 상태를 대조.
    # 1) file_path가 실제로 있는지  2) 있다면 파일 안의 진짜 제목(# 첫 줄)과
    # DB의 title이 같은지 확인한다. 제목만 어긋난 경우는 "파일이 진실"이라는
    # 원칙으로 실제 파일 기준 자동 수정을 제안한다. 파일 자체가 없는 경우는
    # 어떤 파일이 맞는 파일인지 프로그램이 추측할 수 없으므로 자동수정하지
    # 않고 목록만 보여준다(잘못 짝지어 고치는 사고 방지).
    def _check_db_file_integrity(self):
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        topic = self.db_manage_topic_var.get()
        db_path = get_posting_db_path(base_folder, topic)
        records = load_json_db(db_path)

        if not records:
            messagebox.showinfo("검사 완료", f"'{topic}' 주제 포스팅DB에 기록이 없습니다.")
            return

        missing = []
        mismatched = []

        for i, r in enumerate(records):
            fp = r.get("file_path", "")
            if not fp or not os.path.exists(fp):
                missing.append((i, r))
                continue
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                missing.append((i, r))
                continue
            real_title = ""
            for line in content.split("\n"):
                s = line.strip()
                if s.startswith("# ") and not s.startswith("## "):
                    real_title = s[2:].strip()
                    break
            if real_title and real_title != r.get("title", ""):
                mismatched.append((i, r, real_title, content))

        if not missing and not mismatched:
            messagebox.showinfo("검사 완료", f"✅ '{topic}' 주제 포스팅DB {len(records)}건 모두 실제 파일과 일치합니다.")
            return

        lines = []
        if mismatched:
            lines.append(f"📝 제목 불일치 {len(mismatched)}건 (실제 파일 기준으로 자동 수정 가능):")
            for _, r, real_title, _ in mismatched:
                lines.append(f"  • DB: {r.get('title','')}")
                lines.append(f"    실제: {real_title}")
        if missing:
            lines.append(f"\n❌ 파일 없음 {len(missing)}건 (자동수정 불가 - 직접 확인 필요):")
            for _, r in missing:
                lines.append(f"  • {r.get('title','')}")
                lines.append(f"    경로: {r.get('file_path','(없음)')}")

        report = "\n".join(lines)

        if mismatched:
            do_fix = messagebox.askyesno(
                "불일치 발견",
                report + "\n\n제목 불일치 항목을 실제 파일 기준으로 지금 자동 수정할까요?\n"
                "(파일 없음 항목은 자동수정 대상이 아닙니다)"
            )
            if do_fix:
                for i, r, real_title, content in mismatched:
                    core = extract_posting_core(content, real_title)
                    core["date"] = r.get("date", "")
                    core["file_path"] = r.get("file_path", "")
                    records[i] = core
                save_json_db(db_path, records)
                self.log(f"🔧 포스팅DB 제목 불일치 자동 수정: {len(mismatched)}건 ({topic})")
                self._refresh_db_manage_list()
                messagebox.showinfo("수정 완료", f"{len(mismatched)}건 수정했습니다.")
        else:
            messagebox.showwarning("불일치 발견", report)

    # ── [Ver7.46 신규] 중복 기록 일괄 정리 ──────────────────────────
    def _open_db_dedupe_dialog(self):
        """"🧹 중복 기록 일괄 정리" - 11개 주제 포스팅DB를 전부 훑어(비교는
        항상 같은 주제 DB 안에서만) 임계값(%) 이상 겹치는 레코드들을
        find_duplicate_groups로 그룹핑한 뒤 미리보기 팝업을 띄운다. 이
        단계에서는 아무것도 지우지 않는다 - 실제 삭제는 팝업에서 사람이
        확인/선택한 뒤 실행 버튼을 눌러야 일어난다."""
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        try:
            threshold = int(self.db_dedupe_threshold_var.get())
        except Exception:
            threshold = 90
        threshold = max(70, min(100, threshold))

        self.log(f"🧹 중복 기록 일괄 정리 - 전체 주제 스캔 시작 (기준 {threshold}%↑)")
        all_groups = []
        for t in self._db_manage_topics:
            db_path = get_posting_db_path(base_folder, t)
            recs = load_json_db(db_path)
            for g in find_duplicate_groups(recs, threshold):
                all_groups.append({'topic': t, 'db_path': db_path, 'records': recs, 'indices': g})
        self.log(f"🧹 스캔 완료 - 중복 의심 그룹 {len(all_groups)}개 발견")

        if not all_groups:
            messagebox.showinfo("중복 기록 일괄 정리",
                                 f"중복 의심 기록이 없습니다 (기준: {threshold}% 이상 일치).")
            return

        self._show_db_dedupe_popup(all_groups, threshold)

    def _show_db_dedupe_popup(self, all_groups, threshold):
        """중복 그룹 미리보기/선택 팝업. 그룹마다 기본 "유지" 후보를 미리
        골라두되(①실제 파일이 남아있는 쪽 우선 ②그마저 여러 개거나 없으면
        날짜가 가장 오래된 쪽), 행을 더블클릭하면 사람이 언제든 바꿀 수
        있다. "실행" 버튼을 눌러야만 실제 삭제가 일어난다(MD 파일은 삭제
        대상이 아니며, 포스팅DB 기록만 정리된다)."""
        top = tk.Toplevel(self.root)
        top.title(f"중복 기록 일괄 정리 (기준 {threshold}%↑, {len(all_groups)}개 그룹)")
        w, h = 980, 620
        sw, sh = top.winfo_screenwidth(), top.winfo_screenheight()
        top.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        top.transient(self.root)
        top.grab_set()

        ttk.Label(top,
                  text="같은 주제 안에서 서로 거의 동일한 기록들을 그룹으로 묶었습니다. "
                       "그룹마다 남길 1건이 ✅유지로 표시됩니다(파일이 남아있는 쪽 → 더 오래된 날짜 순으로 자동 선택). "
                       "행을 더블클릭하면 그 행을 유지로 바꿀 수 있습니다(그룹 내 나머지는 자동으로 삭제예정 처리).\n"
                       "실제 삭제는 아래 실행 버튼을 눌러야 일어나며, MD 파일은 지워지지 않고 포스팅DB 기록만 삭제됩니다.",
                  foreground="gray", wraplength=940, justify=tk.LEFT).pack(padx=10, pady=(10, 6), anchor=tk.W)

        tree_frame = ttk.Frame(top)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        columns = ("group", "status", "topic", "type", "title", "date", "file")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        tree.heading("group", text="그룹")
        tree.heading("status", text="상태")
        tree.heading("topic", text="주제")
        tree.heading("type", text="유형")
        tree.heading("title", text="제목")
        tree.heading("date", text="저장일")
        tree.heading("file", text="파일존재")
        tree.column("group", width=50, anchor=tk.CENTER)
        tree.column("status", width=90, anchor=tk.CENTER)
        tree.column("topic", width=120, anchor=tk.CENTER)
        tree.column("type", width=60, anchor=tk.CENTER)
        tree.column("title", width=320)
        tree.column("date", width=90, anchor=tk.CENTER)
        tree.column("file", width=70, anchor=tk.CENTER)
        tree.tag_configure("keep", foreground="#1B7A1B")
        tree.tag_configure("dropcand", foreground="#B00020")

        vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vscroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 그룹별 기본 "유지" 인덱스 계산(그룹 순번 -> records 리스트 기준 원본 인덱스)
        keep_state = {}
        for gi, group in enumerate(all_groups):
            records = group['records']
            indices = group['indices']
            existing = [i for i in indices
                        if records[i].get('file_path') and os.path.exists(records[i]['file_path'])]
            if len(existing) == 1:
                keep_state[gi] = existing[0]
            else:
                candidates = existing if existing else indices
                keep_state[gi] = min(candidates, key=lambda i: (records[i].get('date', ''), i))

        def populate():
            for item in tree.get_children():
                tree.delete(item)
            for gi, group in enumerate(all_groups):
                records = group['records']
                keep_idx = keep_state[gi]
                for idx in group['indices']:
                    r = records[idx]
                    type_label = "🧩종합판" if r.get("content_type") == "종합완성판" else "일반"
                    exists = "있음" if r.get('file_path') and os.path.exists(r.get('file_path', '')) else "없음"
                    status = "✅ 유지" if idx == keep_idx else "🗑 삭제예정"
                    tag = "keep" if idx == keep_idx else "dropcand"
                    iid = f"{gi}:{idx}"
                    tree.insert("", tk.END, iid=iid, values=(
                        gi + 1, status, group['topic'], type_label, r.get('title', ''), r.get('date', ''), exists
                    ), tags=(tag,))

        populate()

        def on_double_click(event=None):
            sel = tree.selection()
            if not sel:
                return
            gi_str, idx_str = sel[0].split(":")
            keep_state[int(gi_str)] = int(idx_str)
            populate()

        tree.bind("<Double-1>", on_double_click)

        btn_frame = ttk.Frame(top, padding=(10, 8))
        btn_frame.pack(fill=tk.X)

        def execute_cleanup():
            by_dbpath = {}
            total_delete = 0
            for gi, group in enumerate(all_groups):
                keep_idx = keep_state[gi]
                for idx in group['indices']:
                    if idx != keep_idx:
                        by_dbpath.setdefault(group['db_path'], set()).add(idx)
                        total_delete += 1

            if total_delete == 0:
                messagebox.showinfo("알림", "삭제 대상이 없습니다.")
                return

            if not messagebox.askyesno(
                    "⚠️ 일괄 삭제 확인 (되돌릴 수 없음)",
                    f"총 {total_delete}개 기록을 삭제합니다({len(by_dbpath)}개 주제 DB에 걸쳐).\n"
                    f"각 그룹에서 ✅유지로 표시된 1건만 남고 나머지는 삭제됩니다.\n"
                    f"(실제 MD 파일은 삭제되지 않고, 포스팅DB 기록만 삭제됩니다)\n\n"
                    f"정말 진행하시겠습니까?",
                    icon="warning"):
                return

            # [Ver7.46] 스캔 시점과 실행 시점 사이에 다른 조작이 있었을 가능성을
            # 대비해, 삭제 직전 각 DB 파일을 다시 읽어(fresh load) 인덱스를
            # 적용한다(단일 주제 삭제/전체주제 삭제와 동일한 안전 패턴).
            for db_path, idx_set in by_dbpath.items():
                records = load_json_db(db_path)
                for idx in sorted(idx_set, reverse=True):
                    if 0 <= idx < len(records):
                        del records[idx]
                save_json_db(db_path, records)

            self.log(f"🧹 중복 기록 일괄 정리 완료 - {total_delete}개 삭제 ({len(by_dbpath)}개 주제 DB)")
            messagebox.showinfo("완료", f"{total_delete}개 중복 기록을 정리했습니다.")
            top.destroy()
            self._refresh_db_manage_list()

        ttk.Button(btn_frame, text="🧹 선택 반영하여 삭제 실행", command=execute_cleanup).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="닫기", command=top.destroy).pack(side=tk.RIGHT)

    # 통합키워드 파일 작업을 위한 헬퍼 메소드 
    def get_selected_model_folders(self):
        """선택된 모델의 최종 폴더명 리스트 반환"""
        folders = []
        
        if self.check_gpt_folder.get():
            folders.append("perplexity_GPT_final_articles")
        
        if self.check_gemini_folder.get():
            folders.append("perplexity_Gemini_final_articles")

        if self.check_claude_folder.get():
            folders.append("perplexity_Claude_final_articles")

        # [Ver7.39 추가] 다중질문검색(종합완성판) 저장 폴더
        if self.check_comprehensive_folder.get():
            folders.append("perplexity_종합완성판_final_articles")

        return folders
        
    # 기존 create_safe_filename을 sanitize_filename으로도 사용
    def sanitize_filename(self, filename):
        """파일명에 사용할 수 없는 문자 제거 (create_safe_filename 재활용)"""
        return self.create_safe_filename(filename)

    # [Ver7.41 추가] "경제통합 자료 모으기"(_reorganize_worker)와
    # "포스팅 폴더 복사"(semi_copy_approved_files_to_markdown_folder)가
    # 공통으로 쓰는 유틸 - 대상 경로가 이미 있으면 뒤에 _2, _3...을 붙여
    # 충돌을 피한다. 파일/폴더 둘 다 사용 가능.
    def _kin_unique_path(self, path):
        if not os.path.exists(path):
            return path
        base, ext = os.path.splitext(path)
        counter = 2
        candidate = f"{base}_{counter}{ext}"
        while os.path.exists(candidate):
            counter += 1
            candidate = f"{base}_{counter}{ext}"
        return candidate

    # ---------------------------------------
    # ✅ 호환용 find_matching_keywords (삭제 금지)
    # 기존 3단계 코드에서 호출되므로 반드시 존재해야 함
    # 2025-12-28 로직 업데이트
    # ---------------------------------------
    def find_matching_keywords(self, new_title, existing_keywords):
        """
        개선된 중복 검사: 조사 제거 + 위치 가중치
        """
        try:
            if not new_title or not existing_keywords:
                return [], 0.0
    
            # ===== 헬퍼 함수 ===== 조사 기본
            #def remove_josa(word):
            #    """단어에서 조사 제거"""
            #    josa_pattern = r'(은|는|이|가|을|를|에|의|도|와|과|로|으로|에서|부터|까지|만|라도|이나|나|든지|거나|에게|께서|한테|보고|더러)$'
            #    return re.sub(josa_pattern, '', word)
            
            # ===== 헬퍼 함수 ===== 조사 추가 최적안
            def remove_josa(word):
                """단어에서 조사 제거 (실전 9000개 기반 최적화)"""
                # 기본 조사 제거
                josa_pattern = r'(은|는|이|가|을|를|에|에서|에게|께서|와|과|로|으로|의|도|만|까지|부터|만큼|조차|마저|라도|이라도|든지|이든지|거나|이거나|며|이며|랑|이랑|한테|더러|보고|처럼|같이|대로|씩|뿐|밖에|마다|없이|및|vs|&)$'
                return re.sub(josa_pattern, '', word)

            def extract_first_word_clean(title):
                """첫 단어 추출 후 조사 제거"""
                words = re.findall(r'[가-힣a-zA-Z0-9]+', title)
                if not words:
                    return ""
                return remove_josa(words[0])
    
            def extract_words_with_position(title):
                """단어 추출 + 조사 제거 + 위치 → 딕셔너리"""
                exclude_words = {
                    '은', '는', '이', '가', '을', '를', '에', '의', '도', '와', '과',
                    '로', '으로', '에서', '부터', '까지', '만', '라도', '이나', '나',
                    '든지', '거나', '어떻게', '어떤', '무엇', '언제', '어디', '왜',
                    '얼마나', '몇', '어느', '하는', '있는', '없는', '같은', '그런',
                    '이런', '저런', '모든', '해결', '할까', '받', '수', '있', '28'
                }
                
                words = re.findall(r'[가-힣a-zA-Z0-9]+', title)
                
                word_positions = {}
                for idx, word in enumerate(words):
                    # ✅ 조사 제거
                    clean_word = remove_josa(word)
                    
                    if len(clean_word) >= 2 and clean_word not in exclude_words:
                        if clean_word not in word_positions:
                            word_positions[clean_word] = idx + 1
                
                return word_positions
    
            def calculate_position_score(position):
                """위치별 점수"""
                if position == 1:
                    return 5
                elif position == 2:
                    return 3
                elif position == 3:
                    return 2
                else:
                    return 1
    
            # ===== 메인 로직 =====
            
            # 신규 제목 분석
            first_word_clean = extract_first_word_clean(new_title)
            new_words_pos = extract_words_with_position(new_title)
            
            if not first_word_clean or not new_words_pos:
                return [], 0.0
    
            # 결과 저장
            match_results = []
    
            # 1단계: 첫 단어 완전 일치 (가중치 1.5배)
            for existing in existing_keywords:
                existing_first_clean = extract_first_word_clean(existing)
                
                if existing_first_clean == first_word_clean:
                    existing_words_pos = extract_words_with_position(existing)
                    
                    # 점수 계산
                    total_score = 0
                    matched_words = []
                    
                    for word, new_pos in new_words_pos.items():
                        if word in existing_words_pos:
                            existing_pos = existing_words_pos[word]
                            
                            new_score = calculate_position_score(new_pos)
                            existing_score = calculate_position_score(existing_pos)
                            avg_score = (new_score + existing_score) / 2
                            
                            total_score += avg_score
                            matched_words.append(word)
                    
                    final_score = total_score * 1.5
                    
                    if final_score > 0:
                        match_results.append({
                            'original_keyword': existing,
                            'match_score': final_score,
                            'matched_words': ', '.join(matched_words),
                            'match_type': '첫단어일치'
                        })
    
            # 2단계: 중간 포함 (가중치 1.0배)
            for existing in existing_keywords:
                existing_first_clean = extract_first_word_clean(existing)
                
                # 1단계 제외
                if existing_first_clean == first_word_clean:
                    continue
                
                # ✅ 조사 제거 후 포함 여부 체크
                if first_word_clean in remove_josa(existing):
                    existing_words_pos = extract_words_with_position(existing)
                    
                    # 점수 계산
                    total_score = 0
                    matched_words = []
                    
                    for word, new_pos in new_words_pos.items():
                        if word in existing_words_pos:
                            existing_pos = existing_words_pos[word]
                            
                            new_score = calculate_position_score(new_pos)
                            existing_score = calculate_position_score(existing_pos)
                            avg_score = (new_score + existing_score) / 2
                            
                            total_score += avg_score
                            matched_words.append(word)
                    
                    final_score = total_score * 1.0
                    
                    if final_score > 0:
                        match_results.append({
                            'original_keyword': existing,
                            'match_score': final_score,
                            'matched_words': ', '.join(matched_words),
                            'match_type': '중간포함'
                        })
    
            # 점수 기준 정렬
            match_results.sort(key=lambda x: x['match_score'], reverse=True)
    
            # 중복률 계산
            if match_results:
                max_score = match_results[0]['match_score']
                max_possible = sum(calculate_position_score(p) for p in new_words_pos.values()) * 1.5
                duplicate_rate = min((max_score / max_possible) * 100, 100)
            else:
                duplicate_rate = 0.0
    
            return match_results, duplicate_rate
    
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"❌ find_matching_keywords 오류: {str(e)}")
            return [], 0.0

    def start_all_dates_duplicate_check(self):
        """3단계-1: 전체 날짜 중복 검사 시작"""
        try:
            # 확인 팝업
            result = messagebox.askyesno(
                "전체 중복 검사 확인",
                "전체 주제 폴더의 MD 파일들을 검사합니다.\n\n"
                "📌 작업 내용:\n"
                "• 모든 주제 폴더(IT-테크, 경제-법률 등) 스캔\n"
                "• 통합 키워드 파일과 중복률 검사\n"
                "• 결과를 엑셀 파일에 저장\n\n"
                "계속 진행하시겠습니까?",
                icon='question'
            )
            
            if not result:
                self.log("ℹ️ 사용자가 중복 검사를 취소했습니다.")
                return
            
            try:
                threshold = int(self.step3_threshold_var.get())
                if threshold < 0 or threshold > 100:
                    raise ValueError
            except ValueError:
                messagebox.showerror("오류", "중복률 임계값은 0-100 사이의 숫자여야 합니다.")
                return
            
            # UI 상태 변경
            self.step3_check_button.config(state=tk.DISABLED)
            
            # 별도 스레드에서 중복 검사 실행
            threading.Thread(target=self.all_dates_duplicate_check_worker, args=(threshold,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", str(e))


    def all_dates_duplicate_check_worker(self, threshold):
        """전체 날짜 중복 검사 작업자"""
        try:
            self.log("🔍 전체 주제 폴더 중복 검사를 시작합니다...")
    
            # ========================================
            # ✅ 선택된 폴더 확인 (추가)
            # ========================================
            selected_folders = self.get_selected_model_folders()
            
            if not selected_folders:
                self.root.after(0, lambda: messagebox.showwarning("알림", "검사할 모델 폴더를 최소 1개 이상 선택하세요."))
                return
            
            self.log(f"📂 검사 대상: {', '.join(selected_folders)}")
    
            # ========================================
            # 기존 코드 그대로
            # ========================================
            # 작업 폴더 설정
            work_folder = self.base_folder_var.get().strip()
            if not work_folder:
                work_folder = self.base_folder
            
            # Naver_blog_지식인통합_keyword.xlsx 파일 사용 (작업 폴더에 고정)
            all_keyword_file = self.get_excel_keyword_file_path()
    
            if not os.path.exists(work_folder):
                wf = work_folder
                self.root.after(0, lambda: messagebox.showerror("오류", f"작업 폴더가 없습니다: {wf}"))
                return
    
            
            # 모든 주제 폴더와 MD 파일 수집
            all_md_files = []  # [(제목, 파일경로, 주제폴더명)]
            
            for topic_folder in os.listdir(work_folder):
                topic_path = os.path.join(work_folder, topic_folder)
                if not os.path.isdir(topic_path):
                    continue
                
                self.log(f"📂 주제 폴더 스캔 중: {topic_folder}")
                
                # 각 날짜 폴더 탐색
                for date_folder in os.listdir(topic_path):
                    date_path = os.path.join(topic_path, date_folder)
                    if not os.path.isdir(date_path):
                        continue
                    
                    # ========================================
                    # ✅ 수정: 선택된 모델 폴더들 모두 검사 (기존 단일 폴더 대신 반복)
                    # ========================================
                    for folder_name in selected_folders:
                        final_folder = os.path.join(date_path, folder_name)
                        
                        if not os.path.exists(final_folder):
                            continue
                        
                        # ========================================
                        # 기존 코드 그대로
                        # ========================================
                        # MD 파일들 수집 (평문 저장 + 제목별 폴더 저장 두 방식 모두 지원)
                        for entry in os.listdir(final_folder):
                            entry_path = os.path.join(final_folder, entry)
                            if entry.endswith('.md') and os.path.isfile(entry_path):
                                title = entry[:-3]  # .md 제거
                                all_md_files.append((title, entry_path, topic_folder))
                            elif os.path.isdir(entry_path):
                                # 폴더모드 저장 - 제목별 하위폴더 안의 md 탐색
                                for filename in os.listdir(entry_path):
                                    if filename.endswith('.md'):
                                        title = filename[:-3]
                                        file_path = os.path.join(entry_path, filename)
                                        all_md_files.append((title, file_path, topic_folder))
            
            if not all_md_files:
                self.root.after(0, lambda: messagebox.showwarning("알림", "처리할 MD 파일이 없습니다."))
                return
            
            self.log(f"📊 총 {len(all_md_files)}개 파일 발견")
            
            # ========================================
            # 기존 코드 완전히 그대로
            # ========================================
            # 기존 키워드 로드
            existing_keywords = []
            if os.path.exists(all_keyword_file):
                from openpyxl import load_workbook
                wb = load_workbook(all_keyword_file)
                ws = wb.active
                for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
                    if row[0]:
                        existing_keywords.append(str(row[0]).strip())
                wb.close()
            
            self.log(f"📋 기존 키워드 {len(existing_keywords)}개 로드됨")
            
            # 프로그레스바 초기화
            self.root.after(0, lambda: self.step3_progressbar.configure(value=0))
            
            # 중복 검사 실행
            check_results = []
            total_files = len(all_md_files)
            
            for i, (title, file_path, topic_folder) in enumerate(all_md_files):
                # 프로그레스바 업데이트
                progress_value = int((i + 1) / total_files * 100)
                self.root.after(0, lambda val=progress_value: self.step3_progressbar.configure(value=val))
                self.root.after(0, lambda cur=i+1, tot=total_files: 
                               self.step3_progress_var.set(f"검사 중... ({cur}/{tot})"))
                
                self.log(f"검사 중: {title} (주제: {topic_folder})")
                
                # 매칭되는 키워드들 찾기
                matching_results, duplicate_rate = self.find_matching_keywords(title, existing_keywords)
                
                # 자동 판정
                auto_decision = "X" if duplicate_rate >= threshold else "O"
                
                check_results.append({
                    'title': title,
                    'topic_folder': topic_folder,
                    'matching_results': matching_results,
                    'duplicate_rate': duplicate_rate,
                    'decision': auto_decision
                })
                
                self.log(f"  - 주제: {topic_folder}, 중복률: {duplicate_rate:.1f}%, 판정: {auto_decision}")
            
            # 엑셀에 결과 저장
            self.save_duplicate_check_results(check_results, all_keyword_file)
            
            self.root.after(0, lambda: self.step3_progress_var.set("완료!"))
            self.log(f"✅ 전체 중복 검사 완료! {len(check_results)}개 제목 검사됨")
            
        except Exception as e:
            self.show_error("중복 검사 오류", f"전체 중복 검사 중 오류가 발생했습니다:\n{str(e)}")
        
        finally:
            self.root.after(0, lambda: self.step3_check_button.config(state=tk.NORMAL))


    def save_duplicate_check_results(self, results, keyword_file=None):
        """중복 검사 결과를 엑셀에 저장 - D열 다음에 중복률과 판정 추가"""
        try:
            # keyword_file이 없으면 통합 파일 사용
            if keyword_file is None:
                keyword_file = self.get_excel_keyword_file_path()
            
            self.log(f"📝 엑셀 파일 생성 중...")
            
            from openpyxl import Workbook, load_workbook
                
            if os.path.exists(keyword_file):
                wb = load_workbook(keyword_file)
                ws = wb.active
            else:
                wb = Workbook()
                ws = wb.active
                # 통합 파일용 헤더
                ws['A1'] = "키워드"
                ws['B1'] = "주제"
                ws['C1'] = ""  # 공백
    
            max_row = ws.max_row if ws.max_row else 1
    
            # 1) D열부터 끝까지 초기화
            self.log(f"🧹 기존 검사 결과 초기화 중...")
            max_col = ws.max_column if ws.max_column else 3
            for col in range(4, max_col + 50):
                for row in range(1, max_row + 10):
                    ws.cell(row=row, column=col).value = None
    
            # 2) 헤더 설정
            ws.cell(row=1, column=3).value = '작업날짜'      # C열 (추가)
            ws.cell(row=1, column=4).value = '신규키워드'    # D열
            ws.cell(row=1, column=5).value = '중복률'        # E열
            ws.cell(row=1, column=6).value = '판정'         # F열
    
            # 3) 결과 기록
            self.log(f"✏️ {len(results)}개 결과 기록 중...")
            
            # 오늘 날짜 가져오기
            from datetime import datetime
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            for i, result in enumerate(results):
                row_num = i + 2
                
                # 진행률 로그 (10개마다)
                if (i + 1) % 10 == 0 or (i + 1) == len(results):
                    self.log(f"   → {i+1}/{len(results)} 기록 완료")
                
                # C열: 작업 날짜 (추가)
                ws.cell(row=row_num, column=3).value = today_date
                
                # D열: 신규 키워드
                ws.cell(row=row_num, column=4).value = result.get('title', '')
                
                # E열: 중복률
                duplicate_rate = result.get('duplicate_rate', 0.0)
                ws.cell(row=row_num, column=5).value = f"{duplicate_rate:.1f}%"
                
                # F열: 판정
                ws.cell(row=row_num, column=6).value = result.get('decision', '')

                
                # G열부터: 매칭된 키워드들 순서대로
                matched_keywords = result.get('matching_results', [])[:20]
                for j, match in enumerate(matched_keywords):
                    col_num = 7 + j  # G열부터 시작
                    ws.cell(row=row_num, column=col_num).value = match.get('original_keyword', '')
                
                # B열에 주제 폴더명 기록
                topic_folder = result.get('topic_folder', '')
                if topic_folder:
                    ws.cell(row=row_num, column=2).value = topic_folder
    
            self.log(f"💾 엑셀 파일 저장 중...")
            wb.save(keyword_file)
            wb.close()
    
            self.log(f"✅ 엑셀 저장 완료: {keyword_file}")
            self.log(f"   - 총 {len(results)}개 기록됨")
    
            # 엑셀 파일 열기
            self.log(f"📂 엑셀 파일 여는 중...")
            self.open_excel_keyword_file_all()
                
            self.log("✅ 중복 검사 결과 저장 완료 (D:신규키워드, E:중복률, F:판정, G~:매칭키워드)")

        except Exception as e:
            self.log(f"❌ 엑셀 저장 오류: {str(e)}")
            import traceback
            self.log(f"상세 오류:\n{traceback.format_exc()}")
            raise

    def get_excel_keyword_file_path(self):
        """통합 키워드 엑셀 파일 경로 반환 (일관성 유지)"""
        work_folder = self.base_folder_var.get().strip()
        if not work_folder:
            work_folder = self.base_folder
        filename = self.excel_keyword_filename_var.get().strip()
        if not filename:
            filename = "Naver_blog_지식인통합_keyword.xlsx"
        return os.path.join(work_folder, filename)


    def select_excel_keyword_file(self):
        """통합 키워드 엑셀 파일 선택"""
        initial_dir = self.base_folder_var.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = self.base_folder
    
        file_path = filedialog.askopenfilename(
            title="통합 키워드 엑셀 파일 선택",
            initialdir=initial_dir,
            filetypes=[("엑셀 파일", "*.xlsx"), ("모든 파일", "*.*")]
        )
        if file_path:
            selected_dir = os.path.dirname(os.path.abspath(file_path))
            base_dir = os.path.abspath(self.base_folder_var.get().strip() or self.base_folder)
            
            if selected_dir != base_dir:
                messagebox.showwarning(
                    "경고",
                    f"선택한 파일이 기본 작업 폴더 외부에 있습니다.\n\n"
                    f"작업 폴더: {base_dir}\n"
                    f"선택한 경로: {selected_dir}\n\n"
                    f"파일명만 저장되므로 재시작 후 파일을 찾지 못할 수 있습니다.\n"
                    f"가능하면 기본 작업 폴더 안의 파일을 선택하세요."
                )
            
            self.excel_keyword_filename_var.set(os.path.basename(file_path))
            self.save_model_settings_to_config()
            self.log(f"✅ 통합 키워드 파일 설정: {os.path.basename(file_path)}")


    def open_excel_keyword_file_all(self):
        """통합 키워드 엑셀 파일 열기"""
        try:
            import subprocess
            import platform
            
            # 작업 폴더 경로 포함
            work_folder = self.base_folder_var.get().strip()
            if not work_folder:
                work_folder = self.base_folder
            
            keyword_file = self.get_excel_keyword_file_path()

            # 파일 존재 확인
            if not os.path.exists(keyword_file):
                self.log(f"❌ 파일을 찾을 수 없습니다: {keyword_file}")
                return
            
            if platform.system() == "Windows":
                subprocess.Popen(['start', keyword_file], shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', keyword_file])
            else:  # Linux
                subprocess.Popen(['xdg-open', keyword_file])
            
            self.log(f"📊 엑셀 파일 열기: {keyword_file}")
            
        except Exception as e:
            self.log(f"❌ 엑셀 파일 열기 오류: {str(e)}")



    def add_keywords_to_all_excel(self):
        """3단계-2: 통합파일에 키워드 추가"""
        try:
            # 확인 팝업
            result = messagebox.askyesno(
                "키워드 추가 확인",
                "통합 엑셀 파일에 키워드를 추가합니다.\n\n"
                "📌 작업 내용:\n"
                "• O 표시된 키워드를 통합 파일 A/B열에 추가\n"
                "• X 표시된 파일을 중복 폴더로 이동\n"
                "• 검사 결과(D~F열) 삭제\n\n"
                "⚠️ 주의: 이 작업은 되돌릴 수 없습니다!\n\n"
                "계속 진행하시겠습니까?",
                icon='warning'
            )
            
            if not result:
                self.log("ℹ️ 사용자가 키워드 추가를 취소했습니다.")
                return
            
            # 별도 스레드에서 키워드 추가 실행
            threading.Thread(target=self.add_keywords_worker, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", str(e))


    def add_keywords_worker(self):
        """키워드 추가 작업자"""
        try:
            self.log("✅ 통합파일에 키워드 추가를 시작합니다...")
    
            # Naver_blog_지식인통합_keyword.xlsx 파일 사용 (작업 폴더에 고정)
            work_folder = self.base_folder_var.get().strip()
            if not work_folder:
                work_folder = self.base_folder
            
            keyword_file = self.get_excel_keyword_file_path()

            if not os.path.exists(keyword_file):
                self.root.after(0, lambda: messagebox.showerror("오류", "Naver_blog_지식인통합_keyword.xlsx 파일이 없습니다."))
                return
    
            from openpyxl import load_workbook
            wb = load_workbook(keyword_file)
            ws = wb.active
    
            approved_list = []  # [(제목, 주제폴더명)]
            max_row = ws.max_row if ws.max_row else 1
            max_col = ws.max_column if ws.max_column else 1
                
            # D(4)=제목, E(5)=중복률, F(6)=판정(O/X) 기준
            if max_col < 6:
                wb.close()
                self.root.after(0, lambda: messagebox.showwarning("알림", "판정(F열)이 없습니다. 3단계-1을 먼저 실행하세요."))
                return
    
            # F열(판정) 기준으로 읽기
            for r in range(2, max_row + 1):
                title_d = ws.cell(row=r, column=4).value    # D열: 신규키워드
                decision_f = ws.cell(row=r, column=6).value  # F열: 판정
                
                if not title_d:
                    continue
                    
                if decision_f and str(decision_f).strip().upper() == 'O':
                    # B열에서 주제 폴더명 가져오기 (없으면 빈 문자열)
                    topic_b = ws.cell(row=r, column=2).value
                    approved_list.append((str(title_d).strip(), str(topic_b).strip() if topic_b else ""))
    
            wb.close()
    
            if not approved_list:
                self.root.after(0, lambda: messagebox.showwarning("알림", "O 표시된 키워드가 없습니다."))
                return
    
            # 1. 먼저 X 표시 파일 이동 (D~F열 삭제 전에)
            self.move_rejected_files_step3()
    

            # 2. 승인된 키워드들을 A/B/C에 추가
            wb2 = load_workbook(keyword_file)
            ws2 = wb2.active
    
            # 오늘 날짜 가져오기
            from datetime import datetime
            today_date = datetime.now().strftime("%Y-%m-%d")
    
            # 마지막 행 다음부터 기록
            write_row = ws2.max_row + 1 if ws2.max_row >= 1 else 2
            for title, topic_folder in approved_list:
                ws2.cell(row=write_row, column=1, value=title)         # A: 제목
                ws2.cell(row=write_row, column=2, value=topic_folder)  # B: 주제폴더명
                ws2.cell(row=write_row, column=3, value=today_date)    # C: 작업날짜 (추가)
                write_row += 1

    
            wb2.save(keyword_file)
            wb2.close()
            
            self.log(f"✅ 승인 키워드 {len(approved_list)}개 A/B 추가 완료")
    
            # 3. 마지막으로 D열부터 끝까지 삭제
            wb3 = load_workbook(keyword_file)
            ws3 = wb3.active
            max_col_to_delete = ws3.max_column - 3  # A,B,C 제외한 나머지
            if max_col_to_delete > 0:
                ws3.delete_cols(4, max_col_to_delete)
            wb3.save(keyword_file)
            wb3.close()
    
            self.root.after(0, lambda: self.step3_progress_var.set("완료!"))
            self.log(f"✅ 통합파일 키워드 추가 완료! 승인: {len(approved_list)}개 (D~F 삭제됨)")
            msg = f"통합파일에 키워드가 추가되었습니다!\n승인: {len(approved_list)}개"
            self.root.after(0, lambda: messagebox.showinfo("완료", msg))
    
        except Exception as e:
            self.show_error("키워드 오류", f"키워드 추가 중 오류가 발생했습니다:\n{str(e)}")

    def move_rejected_files_step3(self):
        """3단계: X 표시된 파일들을 중복 폴더로 이동"""
        try:
            self.root.after(0, lambda: self.step3_progress_var.set("X 표시 파일 이동 중..."))
            self.log("🗂️ X 표시된 파일 이동을 시작합니다...")
            
            # ========================================
            # ✅ 선택된 폴더 확인 (추가)
            # ========================================
            selected_folders = self.get_selected_model_folders()
            
            if not selected_folders:
                self.log("⚠️ 검사할 모델 폴더가 선택되지 않았습니다.")
                return
            
            self.log(f"📂 이동 대상 폴더: {', '.join(selected_folders)}")
            
            # ========================================
            # 기존 코드 그대로
            # ========================================
            # 엑셀 파일 읽기
            work_folder = self.base_folder_var.get().strip()
            if not work_folder:
                work_folder = self.base_folder
            
            keyword_file = self.get_excel_keyword_file_path()
            
            if not os.path.exists(keyword_file):
                self.log(f"❌ 엑셀 파일이 없습니다: {keyword_file}")
                self.root.after(0, lambda: self.step3_progress_var.set("오류: 엑셀 파일 없음"))
                return
            
            from openpyxl import load_workbook
            wb = load_workbook(keyword_file)
            ws = wb.active
            
            rejected_dict = {}  # {제목: 주제폴더명}
            
            # F열(판정)에서 X 표시된 항목 찾기
            self.root.after(0, lambda: self.step3_progress_var.set("X 표시 항목 수집 중..."))
            self.log("📋 X 표시 항목 수집 중...")
            
            for r in range(2, ws.max_row + 1):
                title_d = ws.cell(row=r, column=4).value    # D열: 신규키워드
                topic_b = ws.cell(row=r, column=2).value    # B열: 주제
                decision_f = ws.cell(row=r, column=6).value  # F열: 판정
                
                if not title_d:
                    continue
                
                # 디버깅 로그 (처음 3개만)
                if r <= 4:
                    self.log(f"   행{r}: 제목={title_d}, 주제={topic_b}, 판정={decision_f}")
                
                if decision_f and str(decision_f).strip().upper() == 'X':
                    title_normalized = str(title_d).strip()
                    topic_normalized = str(topic_b).strip() if topic_b else ""
                    rejected_dict[title_normalized] = topic_normalized
                    self.log(f"   ✓ X 발견: {title_normalized} (주제: {topic_normalized})")
            
            wb.close()
            
            if not rejected_dict:
                self.log("ℹ️ X 표시된 파일이 없습니다.")
                self.root.after(0, lambda: self.step3_progress_var.set("완료 (X 표시 파일 없음)"))
                return
            
            self.log(f"📋 X 표시 파일 {len(rejected_dict)}개 발견")
            self.root.after(0, lambda: self.step3_progress_var.set(f"X 표시 파일 {len(rejected_dict)}개 처리 중..."))
            
            # 프로그레스바 초기화
            self.root.after(0, lambda: self.step3_progressbar.configure(value=0))
            
            # 각 주제 폴더에서 파일 찾아서 이동
            moved_count = 0
            not_found_count = 0
            total_count = len(rejected_dict)
            
            for idx, (title, topic_folder) in enumerate(rejected_dict.items(), 1):
                # 진행률 업데이트
                progress = (idx / total_count) * 100
                self.root.after(0, lambda val=progress: self.step3_progressbar.configure(value=val))
                
                self.root.after(0, lambda cur=idx, tot=total_count: 
                               self.step3_progress_var.set(f"파일 이동 중... ({cur}/{tot})"))
                self.root.update_idletasks()
                
                if not topic_folder:
                    self.log(f"⚠️ 주제 폴더 정보 없음: {title}")
                    not_found_count += 1
                    continue
                
                topic_path = os.path.join(work_folder, topic_folder)
                if not os.path.exists(topic_path):
                    self.log(f"⚠️ 주제 폴더 없음: {topic_folder}")
                    not_found_count += 1
                    continue
                
                file_found = False
                
                # 날짜 폴더들 탐색
                for date_folder in os.listdir(topic_path):
                    date_path = os.path.join(topic_path, date_folder)
                    if not os.path.isdir(date_path):
                        continue
                    
                    # ========================================
                    # ✅ 수정: 선택된 모든 모델 폴더에서 검색 (기존 단일 폴더 대신 반복)
                    # ========================================
                    for folder_name in selected_folders:
                        final_folder = os.path.join(date_path, folder_name)
                        
                        if not os.path.exists(final_folder):
                            continue
                        
                        # ========================================
                        # 기존 코드 그대로
                        # ========================================
                        # MD 파일 찾기
                        for filename in os.listdir(final_folder):
                            if not filename.endswith('.md'):
                                continue
                            
                            file_title = filename[:-3]  # .md 제거
                            
                            # 정규화해서 비교
                            normalized_file = self.sanitize_filename(file_title).lower()
                            normalized_target = self.sanitize_filename(title).lower()
                            
                            # 제목이 일치하면 중복 폴더로 이동
                            if normalized_file == normalized_target:
                                # ========================================
                                # ✅ 수정: 모델별 중복 폴더 구분 (기존 단일 폴더 대신)
                                # ========================================
                                if "GPT" in folder_name:
                                    duplicate_folder = os.path.join(date_path, "perplexity_GPT_duplicated")
                                elif "Gemini" in folder_name:
                                    duplicate_folder = os.path.join(date_path, "perplexity_Gemini_duplicated")
                                elif "Claude" in folder_name:
                                    duplicate_folder = os.path.join(date_path, "perplexity_Claude_duplicated")                                    
                                else:
                                    duplicate_folder = os.path.join(date_path, "perplexity_duplicated")
                                
                                os.makedirs(duplicate_folder, exist_ok=True)
                                
                                src_path = os.path.join(final_folder, filename)
                                dst_path = os.path.join(duplicate_folder, filename)
                                
                                # ========================================
                                # 기존 코드 그대로
                                # ========================================
                                import shutil
                                shutil.move(src_path, dst_path)
                                moved_count += 1
                                file_found = True
                                self.log(f"🗑️ 중복 파일 이동: {topic_folder}/{date_folder}/{filename}")
                                break
                        
                        if file_found:
                            break
                    
                    if file_found:
                        break
                
                if not file_found:
                    not_found_count += 1
                    self.log(f"❌ 파일을 찾지 못함: {title} (주제: {topic_folder})")
            
            # ========================================
            # 기존 코드 완전히 그대로
            # ========================================
            # 최종 결과
            self.root.after(0, lambda: self.step3_progressbar.configure(value=100))
            
            self.root.after(0, lambda: self.step3_progress_var.set(f"완료! 이동: {moved_count}개, 미발견: {not_found_count}개"))
            self.log(f"✅ X 표시 파일 이동 완료!")
            self.log(f"   - 이동 성공: {moved_count}개")
            self.log(f"   - 찾지 못함: {not_found_count}개")
            
        except Exception as e:
            self.root.after(0, lambda: self.step3_progress_var.set("오류 발생!"))
            self.show_error("파일 이동 오류", f"파일 이동 중 오류가 발생했습니다:\n{str(e)}")
            import traceback
            self.log(f"상세 오류:\n{traceback.format_exc()}")
    
    # 경제 카테고리 7개의 최종본 MD(+이미지)를 "경제통합"으로 모으기
    # (경제-A~G 카테고리 폴더 자체는 이동하지 않고, 그 안의 완성 파일만 이동)
    def _open_econ_collect_folder(self):
        """[Ver7.78 추가] "경제통합 자료 모으기"의 저장 대상 폴더
        (base_folder/경제통합/오늘날짜/perplexity_collected_final_articles/)를
        탐색기(또는 macOS/Linux 기본 파일관리자)로 연다. _open_web2nd_save_folder와
        동일한 os.startfile/open/xdg-open 분기 패턴을 그대로 사용."""
        base_folder = self.base_folder_var.get().strip() or self.base_folder
        if not base_folder:
            messagebox.showerror("오류", "기본 작업 폴더가 설정되어 있지 않습니다.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        folder = os.path.join(base_folder, "경제통합", today, "perplexity_collected_final_articles")

        try:
            os.makedirs(folder, exist_ok=True)
            if os.name == "nt":
                os.startfile(folder)
            else:
                import subprocess, platform
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
            self.log(f"📁 경제통합 저장폴더 열기: {folder}")
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 여는 중 오류가 발생했습니다:\n{e}")

    def start_reorganize_folders(self):
        """경제통합 자료 모으기 - 경제-A~G 7개 카테고리 폴더는 원래 위치에 그대로
        두고, 각 폴더 안의 perplexity_*_final_articles에 있는 완성 MD(+이미지)
        파일만 경제통합/오늘날짜/perplexity_collected_final_articles/로
        "이동"한다(건강/교육/IT/자동차는 대상 아님 - ECON_TOPICS가 경제-A~G로
        고정되어 있어 이 함수는 처음부터 경제 카테고리 전용). [Ver7.54 변경]
        원래는 복사(shutil.copy2/copytree)만 하고 원본을 그대로 뒀으나,
        사용자 요청으로 이동(shutil.move)으로 변경 - 이동 후에는 원본
        final_articles 안의 해당 파일/폴더가 사라진다. [Ver7.55 변경]
        경제-A~G 카테고리 폴더 자체는 그대로 유지되지만, 최종본 폴더를
        하나라도 처리한 "주제"는 그 주제 아래의 날짜 폴더를 전부(최종본이
        없던 날짜 폴더까지 포함) 통째로 삭제한다. [Ver7.88→7.89 변경 경위]
        한때(Ver7.88) "최종본이 있던 그 날짜 폴더만" 지우도록 좁혔었으나,
        하루를 걸쳐(전날 저녁+다음날 아침) 이어서 작업하면 중간 단계
        파일이 "시작한 날" 폴더에 남아 최종본은 이미 옮겨졌는데도 그
        날짜 폴더만 안 지워져 "일부만 끝난 것처럼" 보이는 혼란이 있어
        원상복구 - 최종본을 옮긴 주제는 그 주제의 모든 날짜 폴더를
        삭제하는 것이 맞는 동작으로 확정됨(실제 신고·확인 사례 기반).
        최종본이 하나도 없던(이번에 옮길 게 없는) 주제는 삭제 대상이
        아니므로 무관한 진행 중 작업은 건드리지 않는다."""

        # [경제통합 개선 - 재수정] 이전 버전은 경제-A~G 폴더 자체를 "경제통합"
        # 폴더 아래로 shutil.move해서 원래 위치에서 사라지게 했으나, 실제
        # 요구사항은 "경제 카테고리 폴더는 그대로 유지하고, final_articles
        # 안의 완성 MD 파일만 경제통합으로 모아달라"는 것이었음. 폴더 이동을
        # 완전히 제거하고 파일 복사(shutil.copy2)만 하도록 재작성.
        # [Ver7.54 변경] 복사 후 원본을 남겨두던 것을, 사용자 요청으로 다시
        # "파일 단위 이동"으로 변경 - 단, 경제-A~G 카테고리 폴더 자체를
        # 통째로 옮기는 게 아니라 그 안의 완성 파일/제목별 폴더만 이동한다
        # (카테고리 폴더 구조 자체는 유지). 아래 ECON_TOPICS 목록이 경제
        # 카테고리로 고정되어 있으므로 다른 주제는 이 변경의 영향을 받지 않음.
        ECON_TOPICS = [
            "경제-A-거시경제-경기-통화-금리",
            "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산",
            "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원",
            "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기",
        ]

        base_folder = self.base_folder_var.get().strip()

        if not base_folder or not os.path.exists(base_folder):
            messagebox.showerror("오류", "기본 작업 폴더가 존재하지 않습니다.")
            return

        # 미리보기 생성 - 경제 카테고리 폴더 존재 여부만 확인(이동 대상이
        # 아니라 스캔 대상이므로 존재 여부만 알려주면 충분)
        preview_lines = []
        any_source_exists = False
        for topic in ECON_TOPICS:
            src = os.path.join(base_folder, topic)
            if os.path.exists(src):
                preview_lines.append(f"   ✅ {topic}")
                any_source_exists = True
            else:
                preview_lines.append(f"   ⬜ {topic} (폴더 없음 - 스킵)")

        # 모을 경제 카테고리 폴더가 하나도 없으면 확인 팝업 없이 안내만
        if not any_source_exists:
            messagebox.showinfo(
                "📂 경제통합 자료 모으기",
                "모을 경제 카테고리 폴더가 없습니다.\n\n"
                "경제-A~G 주제 폴더 중 존재하는 것이 하나도 없어\n"
                "경제통합으로 모을 자료가 없습니다."
            )
            self.log("ℹ️ 경제통합 모으기 대상 없음 - 경제 카테고리 폴더가 하나도 존재하지 않음")
            return

        preview_text = "\n".join(preview_lines)

        result = messagebox.askyesno(
            "📂 경제통합 자료 모으기 확인",
            f"아래 경제 카테고리 폴더 안의 최종본 MD(+이미지) 파일을 찾아\n"
            f"'경제통합/오늘날짜/perplexity_collected_final_articles/'로\n"
            f"이동합니다.\n\n"
            f"⚠️ 최종본을 하나라도 옮긴 주제는, 그 주제 아래의 날짜 폴더를\n"
            f"전부(최종본이 없던 날짜 폴더까지 포함) 통째로 삭제합니다 -\n"
            f"research_brief/perplexity_answers/검증/1차각색 등 중간\n"
            f"산출물이 남아있어도 함께 삭제되니, 아직 안 끝난 작업이 있는\n"
            f"주제라면 먼저 그 주제 작업을 마무리한 뒤 실행하세요.\n"
            f"경제-A~G 카테고리 폴더 자체는 그대로 유지되며, 대상은 경제\n"
            f"카테고리에만 적용됩니다.\n\n"
            f"대상 카테고리:\n{preview_text}\n\n"
            f"계속 진행하시겠습니까?"
        )

        if not result:
            self.log("ℹ️ 경제통합 자료 모으기 취소됨")
            return

        self.reorganize_btn.config(state=tk.DISABLED)

        # 별도 스레드에서 실행 (UI 블로킹 방지)
        threading.Thread(
            target=self._reorganize_worker,
            args=(ECON_TOPICS, base_folder),
            daemon=True
        ).start()


    def _reorganize_worker(self, econ_topics, base_folder):
        """경제 카테고리 폴더(경제-A~G)는 그대로 두고, 각 폴더 아래
        perplexity_*_final_articles 바로 아래에 있는 항목(제목별 폴더 또는
        낱개 MD/이미지 파일)을 원본 형태 그대로 경제통합/오늘날짜/
        perplexity_collected_final_articles/로 이동한다(원본 자리에는
        남지 않음).

        [Ver7.40 재작성] 이전 버전은 final_articles 안을 os.walk로 재귀
        스캔해서 모든 MD/이미지 파일을 하나의 폴더에 평탄하게 모았는데,
        실제 요구사항은 그게 아니라 "이미 있는 제목별 폴더 구조를 그대로
        옮기는" 것이었음. 제목별 폴더가 있으면 그 폴더를 통째로 이동하고,
        폴더 없이 낱개 파일로 있으면 그 파일만 그대로 이동한다 - 새로
        폴더를 만들어 묶는 로직은 두지 않는다.
        [Ver7.54 변경] 기존에는 shutil.copytree/copy2로 "복사"만 하고
        원본을 남겨뒀으나, 사용자 요청으로 shutil.move를 사용한 "이동"으로
        변경 - 대상은 econ_topics(경제-A~G)로 이미 고정되어 있어 경제
        카테고리에만 적용되고 다른 주제에는 영향이 없다. 이동이므로
        복사 때와 달리 중간에 실패하면 일부만 옮겨진 상태로 남을 수
        있으니(부분 이동), 오류 로그의 "몇 번째까지 처리됐는지"를 보고
        나머지를 수동으로 확인해야 한다(복사 시절의 "실패해도 원본 안전"
        전제는 더 이상 유효하지 않음).
        [Ver7.55 변경] 최종본 폴더(perplexity_*_final_articles)를 하나라도
        처리한 날짜 폴더는, 이동이 끝난 뒤 shutil.rmtree로 날짜 폴더
        자체를 통째로 삭제한다(요청 반영 - 빈 폴더만 남기는 게 아니라
        폴더 자체가 사라져야 함). MD/이미지가 아니라서 이동 대상에서
        제외된 파일이 그 날짜 폴더 안에 남아 있었더라도 함께 삭제되므로
        주의. 최종본 폴더가 하나도 없던 날짜 폴더는 이 작업과 무관하므로
        건드리지 않는다.
        [Ver7.89 변경] 삭제 범위를 "날짜 폴더 단위"에서 "주제 단위"로
        확장. 하루를 걸쳐(전날 저녁+다음날 아침) 이어서 작업하면 중간
        단계 산출물(research_brief/perplexity_answers/검증/1차각색)은
        "시작한 날"의 날짜 폴더에, 최종본은 "끝낸 날"의 날짜 폴더에 나뉘어
        남는 경우가 있는데, 예전처럼 최종본이 있던 날짜 폴더만 지우면
        시작한 날의 폴더가 고스란히 남아 "일부만 끝난 것처럼" 보이는
        혼란이 생겼다(실사용 신고 사례). 이 주제(topic)에서 최종본을
        하나라도 옮겼다면, 최종본이 없던 날짜 폴더까지 포함해 그 주제의
        모든 날짜 폴더를 삭제한다. 최종본이 하나도 없던 주제는 대상이
        아니므로 무관하게 진행 중인 다른 주제 작업은 건드리지 않는다.
        [Ver8.21 확인] 사용자 실사용 신고(경제통합 폴더에 날짜+빈 폴더만
        생기고 MD가 없으며 원본도 그대로 남아있는 증상) 재점검 결과, 이
        함수(Ver7.89) 자체의 이동/삭제 로직에는 문제가 없음을 확인함 -
        신고된 증상은 final_articles 하위 항목의 이동이 한 건도 실행되지
        않았을 때(예: 구버전 실행 중이었거나, 실제 폴더명이 "final_articles"
        패턴과 불일치)만 나타날 수 있는 결과이며, collect_folder를 미리
        os.makedirs로 만들어두는 부분만 실행되고 그 아래 실제 이동은 한
        건도 못 찾은 상태와 정확히 일치한다. 로직 자체는 변경하지 않음
        (사용자 확인 완료)."""
        import shutil

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            collect_folder = os.path.join(base_folder, "경제통합", today, "perplexity_collected_final_articles")
            os.makedirs(collect_folder, exist_ok=True)

            self.log("📂 경제통합 자료 모으기 시작 (원본 폴더 구조 그대로 이동, 원본 위치에는 남지 않음)...")

            scanned_topics = 0
            collect_total = 0
            failed_deletes = []

            for topic in econ_topics:
                topic_path = os.path.join(base_folder, topic)
                if not os.path.isdir(topic_path):
                    self.log(f"⬜ 스킵 (폴더 없음): {topic}")
                    continue

                scanned_topics += 1
                topic_count = 0
                topic_had_final_articles = False  # [Ver7.89] 주제 단위 청소 여부 판단용

                # 날짜 폴더 탐색
                for date_folder in os.listdir(topic_path):
                    date_path = os.path.join(topic_path, date_folder)
                    if not os.path.isdir(date_path):
                        continue

                    # final_articles 폴더 탐색
                    date_had_final_articles = False
                    for folder_name in os.listdir(date_path):
                        if "final_articles" not in folder_name:
                            continue

                        final_path = os.path.join(date_path, folder_name)
                        if not os.path.isdir(final_path):
                            continue

                        date_had_final_articles = True

                        # [2026-09-27 3차] 사이드카(게시판목록.txt)는 이동
                        # 대상(.md/이미지)이 아니라 아래 루프에서 그냥
                        # 건너뛰어지고, 뒤이어 원본 날짜 폴더가 통째로
                        # 삭제되면서 같이 사라진다 - 그 전에 내용을
                        # collect_folder 쪽 사이드카로 먼저 병합해둔다.
                        self._kin_sidecar_merge_into(final_path, collect_folder)

                        # final_articles 바로 아래 항목만 원본 형태 그대로 이동
                        # [Ver7.54 변경] 복사(copytree/copy2) → 이동(move) -
                        # 이동 후 원본 위치(경제-A~G 쪽 final_articles)에는
                        # 더 이상 남지 않는다(재귀로 파일을 뒤섞지 않음 -
                        # 폴더는 폴더째로, 파일은 파일째로 이동).
                        for entry in os.listdir(final_path):
                            if entry == self.KIN_SIDECAR_FILENAME:
                                continue  # 위에서 이미 병합 처리함
                            src_path = os.path.join(final_path, entry)
                            dst_path = os.path.join(collect_folder, entry)

                            if os.path.isdir(src_path):
                                # 제목별 폴더 - 통째로 이동(충돌 시 이름 뒤에 _2 등 추가)
                                dst_path = self._kin_unique_path(dst_path)
                                file_count_before = sum(len(files) for _r, _d, files in os.walk(src_path))
                                shutil.move(src_path, dst_path)
                                topic_count += file_count_before
                            elif os.path.isfile(src_path):
                                # 낱개 파일 - MD/이미지만 그대로 이동
                                if not (entry.endswith('.md') or
                                        entry.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
                                    continue
                                dst_path = self._kin_unique_path(dst_path)
                                shutil.move(src_path, dst_path)
                                topic_count += 1

                    if date_had_final_articles:
                        topic_had_final_articles = True

                # [Ver7.89 재수정] Ver7.88에서는 "final_articles가 있던 그
                # 날짜 폴더" 하나만 건드리지 않게 좁혀놨는데, 실제 사용
                # 패턴과 맞지 않았다 - 하루를 걸쳐(전날 저녁+다음날 아침)
                # 이어서 작업하면 research_brief/perplexity_answers/
                # 검증/1차각색 등 중간 단계 파일은 "시작한 날"(예: 19일)
                # 폴더에, 최종본(final_articles)은 "끝낸 날"(예: 20일)
                # 폴더에 나뉘어 남는다. 이미 "경제통합"으로 최종본까지
                # 옮겨졌다면 그 항목은 전 단계가 다 끝난 것이므로, 시작한
                # 날짜 폴더에 남은 중간 산출물도 더 이상 쓸모가 없는
                # 잔재다 - 그대로 두면 "19일치만 남아서 뭔가 안 끝난 것처럼
                # 보이는" 혼란을 유발한다(실제 신고 사례). 그래서 이번
                # 주제(topic)에서 최종본을 하나라도 옮겼다면, 그 주제
                # 아래의 "모든" 날짜 폴더를 통째로 삭제한다(최종본이 없던
                # 날짜 폴더까지 포함 - 어차피 그 주제 자체가 이번에 정리
                # 대상이었다는 뜻이므로). 최종본이 하나도 없던 주제(이번에
                # 경제통합으로 옮길 게 없는 주제)는 이 삭제 대상이 아니므로
                # 완전히 무관한 진행 중 작업까지 건드리지 않는다.
                # [Ver7.71에서 고친 대로] rmtree 실패(파일 잠김/권한 등)는
                # 예외를 삼키지 않고 실패 목록에 남겨 최종 완료 메시지에
                # 노출한다.
                if topic_had_final_articles:
                    for date_folder in os.listdir(topic_path):
                        date_path = os.path.join(topic_path, date_folder)
                        if not os.path.isdir(date_path):
                            continue
                        try:
                            shutil.rmtree(date_path)
                            self.log(f"   🗑 원본 날짜 폴더 삭제: {topic}/{date_folder}")
                        except Exception as rm_err:
                            failed_deletes.append((f"{topic}/{date_folder}", str(rm_err)))
                            self.log(f"   ⚠️ 원본 날짜 폴더 삭제 실패: {topic}/{date_folder} — {rm_err}")

                self.log(f"✅ {topic}: {topic_count}개 수집")
                collect_total += topic_count

            msg = (
                f"✅ 경제통합 자료 모으기 완료!\n"
                f"스캔한 카테고리: {scanned_topics}개\n"
                f"이동: {collect_total}개\n"
                f"→ 경제통합/{today}/perplexity_collected_final_articles/\n\n"
                f"(경제-A~G 카테고리 폴더 자체는 그대로 유지되지만, 최종본을\n"
                f"하나라도 옮긴 주제는 그 주제 아래 날짜 폴더 전체가 원본\n"
                f"위치에서 삭제됩니다 - 최종본이 없던 날짜 폴더까지 포함)"
            )
            # [Ver7.71 추가] 삭제 실패가 하나라도 있으면(파일 잠김/권한 문제 등)
            # 완료 팝업에 그 목록과 이유를 그대로 노출한다 - 조용히 넘어가면
            # "분명 삭제된다고 안내했는데 왜 남아있지?"라는 혼란만 반복되므로,
            # 파일/폴더가 왜 못 지워졌는지 사용자가 그 자리에서 바로 알 수
            # 있게 한다(예: 탐색기·뷰어에서 해당 폴더를 열어둔 상태면 닫고
            # 다시 시도).
            if failed_deletes:
                fail_lines = "\n".join(f"   • {name}: {reason}" for name, reason in failed_deletes)
                msg += (
                    f"\n\n⚠️ 다음 {len(failed_deletes)}개 원본 날짜 폴더는 삭제하지 "
                    f"못했습니다(파일이 다른 프로그램에서 열려있거나 권한 문제일 "
                    f"수 있습니다 - 해당 폴더/파일을 닫고 다시 실행해보세요):\n{fail_lines}"
                )
            self.log(msg)
            self.root.after(0, lambda: messagebox.showinfo("완료", msg))

        except Exception as e:
            self.log(f"❌ 오류 발생: {str(e)}")
            import traceback
            self.log(f"상세 오류:\n{traceback.format_exc()}")
            self.root.after(0, lambda err=str(e): messagebox.showerror(
                "오류",
                f"경제통합 자료를 모으는 중 오류가 발생했습니다:\n{err}"
            ))

        finally:
            self.root.after(0, lambda: self.reorganize_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress.configure(value=0))


    # 환경파일 저장
    def save_model_settings_to_config(self):
        """모델 설정 자동 저장"""
        try:
            import json
            
            config_path = self.get_kin_config_path()
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # ✅ 설정 저장 (모든 항목)
            config['model_1st_type'] = self.model_1st_type.get()
            config['gpt_model_1st'] = "gpt-4.1-mini-2025-04-14"
            config['model_2nd_type'] = self.model_2nd_type.get()
            config['gpt_model_2nd'] = "gpt-4.1-mini-2025-04-14"
            config['temperature_1st'] = self.temperature_1st.get()
            config['temperature_2nd'] = self.temperature_2nd.get()
            config['rewrite_mode'] = self.rewrite_mode.get()
            config['duplicate_threshold'] = self.step3_threshold_var.get()
            # [Ver7.13] 회사/집 등 PC마다 전체경로(드라이브·계정명)가 달라 시작 시
            # 에러가 나는 문제 방지: 전체경로가 아닌 "폴더명만" 저장한다.
            config['base_output_folder'] = os.path.basename(
                self.base_folder_var.get().strip().rstrip("/\\"))
            config['prompt_folder'] = os.path.basename(
                self.prompt_folder_var.get().strip().rstrip("/\\"))
            config['classifier_file'] = self.classifier_file_var.get().strip()
            config['check_gpt_folder']    = self.check_gpt_folder.get()
            config['check_gemini_folder'] = self.check_gemini_folder.get()
            config['check_claude_folder'] = self.check_claude_folder.get()
            # [Ver7.39 추가]
            config['check_comprehensive_folder'] = self.check_comprehensive_folder.get()
            config['claude_model_1st'] = self.claude_model_1st.get()
            config['claude_model_2nd'] = self.claude_model_2nd.get()
            config['excel_keyword_filename'] = self.excel_keyword_filename_var.get().strip()


            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.log(f"❌ 설정 저장 실패: {str(e)}")
    
    def manual_save_config(self):
        """환경파일 수동 저장"""
        self.save_model_settings_to_config()
        self.log("💾 환경파일 저장 완료 (Naver_blog_config_지식인.json)")
        messagebox.showinfo("저장 완료", "환경파일이 저장되었습니다.\nNaver_blog_config_지식인.json")
    
    # 환경파일 로딩
    def load_model_settings_from_config(self):
        """모델 설정 로드"""
        try:
            import json
            config_path = self.get_kin_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # ✅ 설정 로드 (모든 항목)
                self.model_1st_type.set(config.get('model_1st_type', 'GPT'))
                self.gpt_model_1st.set('gpt-4.1-mini-2025-04-14')
                self.model_2nd_type.set(config.get('model_2nd_type', 'GPT'))
                self.gpt_model_2nd.set('gpt-4.1-mini-2025-04-14')
                self.temperature_1st.set(config.get('temperature_1st', 0.3))
                self.temperature_2nd.set(config.get('temperature_2nd', 0.7))
                self.rewrite_mode.set(config.get('rewrite_mode', 'both'))
                self.check_gpt_folder.set(config.get('check_gpt_folder', True))
                self.check_gemini_folder.set(config.get('check_gemini_folder', True))
                self.check_claude_folder.set(config.get('check_claude_folder', True))
                # [Ver7.39 추가]
                self.check_comprehensive_folder.set(config.get('check_comprehensive_folder', True))
                self.claude_model_1st.set(config.get('claude_model_1st', 'claude-sonnet-4-5'))
                self.claude_model_2nd.set(config.get('claude_model_2nd', 'claude-sonnet-4-5'))

                if hasattr(self, 'step3_threshold_var'):
                    self.step3_threshold_var.set(config.get('duplicate_threshold', '50'))                

                # [Ver7.13] 구버전 config에 전체경로가 남아있을 수 있으므로
                # basename만 취해 PC(회사/집)가 달라도 항상 실행 위치 기준
                # 상대경로로 동작하게 한다. 폴더가 없으면 자동 생성한다.
                saved_output_folder = config.get('base_output_folder', '')
                if saved_output_folder:
                    saved_output_folder = os.path.basename(saved_output_folder.rstrip("/\\"))
                    self.base_folder = saved_output_folder

                if hasattr(self, 'base_folder_var') and saved_output_folder:
                    self.base_folder_var.set(saved_output_folder)

                if self.base_folder:
                    os.makedirs(self.base_folder, exist_ok=True)

                saved_prompt_folder = config.get('prompt_folder', '')
                if saved_prompt_folder:
                    saved_prompt_folder = os.path.basename(saved_prompt_folder.rstrip("/\\"))
                    self.prompt_folder = saved_prompt_folder
                if hasattr(self, 'prompt_folder_var') and saved_prompt_folder:
                    self.prompt_folder_var.set(saved_prompt_folder)

                if self.prompt_folder:
                    os.makedirs(self.prompt_folder, exist_ok=True)

                saved_classifier = config.get('classifier_file', 'Naver_blog_topic_classifier.txt')
                if hasattr(self, 'classifier_file_var') and saved_classifier:
                    self.classifier_file_var.set(saved_classifier)

                saved_excel = config.get('excel_keyword_filename', 'Naver_blog_지식인통합_keyword.xlsx')
                if hasattr(self, 'excel_keyword_filename_var') and saved_excel:
                    self.excel_keyword_filename_var.set(saved_excel)

                if hasattr(self, 'auto_convert'):
                    pass  # [Ver7.10] auto_convert 기능 제거됨 - 하위호환용 config 무시

                
                self.log("✅ 모델 설정 로드 완료")
            else:
                self.log("ℹ️ config 파일 없음 (기본값 사용)")
                
        except Exception as e:
            self.log(f"⚠️ 설정 로드 실패: {str(e)}")


    def quit_application(self):
        """애플리케이션 안전 종료"""
        try:
            # 프로그레스 바가 실행 중인지 확인
            if hasattr(self, 'progress'):
                self.progress.stop()
            
            if messagebox.askyesno("종료", "프로그램을 종료하시겠습니까?\n(실행 중인 작업이 있다면 중단됩니다)"):
                if getattr(self, "_shared_chrome_driver", None):
                    try:
                        self._shared_chrome_driver.quit()
                    except Exception:
                        pass
                # 강제 종료
                self.root.quit()
                self.root.destroy()
                
                # 프로세스 완전 종료 (스레드가 남아있을 경우 대비)
                import sys
                sys.exit(0)
                
        except Exception as e:
            # 오류가 발생해도 강제 종료
            import sys
            sys.exit(0)

    # ══════════════════════════════════════════════════════════
    # [Ver7.10 추가] 반자동 프로그램의 "5단계: 중복 검사" + "6단계: 최종
    # 처리(포스팅 폴더로 이동)" 로직을 완전히 별도의 새 탭으로 그대로
    # 이식한 것. 기존 "9)통합 키워드 관리" 탭의 변수·함수는 일절 건드리지
    # 않고, semi_ 접두어가 붙은 독립된 함수들로만 동작한다.
    # 반자동과의 차이점(의도적 조정): 반자동은 항상 "작업폴더에서 찾은
    # 첫 번째 주제 폴더"만 처리했지만, 수동 프로그램은 다른 모든 탭이
    # 주제를 직접 선택하는 방식이라 여기도 주제 드롭다운을 추가했다.
    # 나머지 알고리즘(중복 판정 D~F열 기록, O열 승인 시 포스팅 폴더로
    # 파일 복사, X는 중복 폴더로 이동)은 반자동 원본과 동일하다.
    # ══════════════════════════════════════════════════════════

    def create_semi_migrated_tab(self):
        """반자동 이식 탭: 주제별 중복검사 + 최종처리(포스팅 폴더 이동)"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="11)주제 키워드 등록")
        tab.columnconfigure(1, weight=1)

        ttk.Label(tab,
            text="반자동 프로그램의 중복검사(5단계)+최종처리(6단계) 로직을 그대로 이식한 탭입니다.\n"
                 "기존 '6)통합 키워드 관리' 탭과는 완전히 독립적으로 동작합니다(같은 파일/변수를 공유하지 않음).",
            foreground="gray", justify=tk.LEFT).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        topics = [
            "경제통합",
            "경제-A-거시경제-경기-통화-금리", "경제-B-금융-대출-신용-투자-보험-연금상품",
            "경제-C-세금-조세제도-연말정산", "경제-D-고용-노동-근로관계-취업지원",
            "경제-E-복지연금-사회보험-국민연금-생활지원", "경제-F-법률-행정-행정절차-가사",
            "경제-G-부동산-임대차-매매-등기", "건강", "교육", "자동차", "IT"
        ]

        # 주제 선택
        # [Ver8.33 신규] 사용자 지정 시작 기본 주제 - env.txt(semi_default_topic)에
        # 저장된 값이 있고 그 값이 현재 topics 목록에 있으면 그 주제로, 아니면
        # 기존처럼 topics[0]으로 초기화한다.
        ttk.Label(tab, text="주제:").grid(row=1, column=0, sticky=tk.W, pady=4)
        _semi_saved_default_topic = get_env_value('semi_default_topic', '').strip()
        _semi_initial_topic = _semi_saved_default_topic if _semi_saved_default_topic in topics else topics[0]
        self.semi_topic_var = tk.StringVar(value=_semi_initial_topic)
        semi_topic_frame = ttk.Frame(tab)
        semi_topic_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=4)
        semi_topic_combo = ttk.Combobox(semi_topic_frame, textvariable=self.semi_topic_var, values=topics,
                                         state="readonly", width=40, height=12)
        semi_topic_combo.pack(side=tk.LEFT)

        self.semi_default_topic_label_var = tk.StringVar()

        def refresh_semi_default_topic_label():
            saved = get_env_value('semi_default_topic', '').strip()
            self.semi_default_topic_label_var.set(f"(현재 기본값: {saved})" if saved else "(기본값 미설정 - 매번 '경제통합'으로 시작)")

        def save_semi_default_topic():
            update_env_value('semi_default_topic', self.semi_topic_var.get())
            refresh_semi_default_topic_label()
            self.log(f"⭐ [11)주제 키워드] 시작 기본 주제를 '{self.semi_topic_var.get()}'(으)로 저장했습니다.")

        ttk.Button(semi_topic_frame, text="⭐ 이 주제를 시작 기본값으로 저장",
                   command=save_semi_default_topic).pack(side=tk.LEFT, padx=(8, 8))
        ttk.Label(semi_topic_frame, textvariable=self.semi_default_topic_label_var,
                  foreground="gray").pack(side=tk.LEFT)
        refresh_semi_default_topic_label()

        # 날짜 선택
        # [Ver8.33 UI 정리] 날짜 콤보와 새로고침 버튼을 같은 프레임에 묶어 콤보 바로
        # 옆에 배치 - 이전에는 버튼이 2번 열에 있었는데, 1번 열이 columnconfigure
        # (weight=1)로 늘어나 있어서 버튼이 화면 오른쪽 끝으로 멀리 떨어져 보였음.
        ttk.Label(tab, text="날짜:").grid(row=2, column=0, sticky=tk.W, pady=4)
        semi_date_frame = ttk.Frame(tab)
        semi_date_frame.grid(row=2, column=1, sticky=tk.W, pady=4)
        self.semi_date_var = tk.StringVar()
        self.semi_date_combo = ttk.Combobox(semi_date_frame, textvariable=self.semi_date_var, width=20)
        self.semi_date_combo.pack(side=tk.LEFT)

        def refresh_semi_dates():
            base = self.base_folder_var.get().strip() or self.base_folder
            topic = self.semi_topic_var.get()
            topic_path = os.path.join(base, topic)
            dates = []
            if os.path.exists(topic_path):
                dates = [d for d in os.listdir(topic_path)
                         if os.path.isdir(os.path.join(topic_path, d)) and re.match(r'\d{4}-\d{2}-\d{2}', d)]
            dates = sorted(dates, reverse=True)
            self.semi_date_combo['values'] = dates
            if dates:
                self.semi_date_var.set(dates[0])
            else:
                self.semi_date_var.set("")

        ttk.Button(semi_date_frame, text="🔄 날짜 새로고침", command=refresh_semi_dates).pack(side=tk.LEFT, padx=(8, 0))
        self.semi_topic_var.trace_add("write", lambda *_: refresh_semi_dates())
        refresh_semi_dates()

        # 주제별 키워드 엑셀 파일
        ttk.Label(tab, text="키워드 엑셀:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.semi_keyword_file_var = tk.StringVar()

        def refresh_semi_keyword_display():
            topic = self.semi_topic_var.get()
            self.semi_keyword_file_var.set(self.semi_get_excel_keyword_file_path(topic))

        ttk.Entry(tab, textvariable=self.semi_keyword_file_var, state="readonly", width=55).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=4)

        def browse_semi_keyword_file():
            path = filedialog.askopenfilename(title="주제별 키워드 엑셀 선택",
                                               filetypes=[("Excel 파일", "*.xlsx"), ("모든 파일", "*.*")])
            if path:
                mapping = self.load_semi_keyword_mapping()
                mapping[self.semi_topic_var.get()] = path
                self.save_semi_keyword_mapping(mapping)
                refresh_semi_keyword_display()
                self.log(f"💾 [{self.semi_topic_var.get()}] 키워드 엑셀 지정: {path}")

        ttk.Button(tab, text="파일 선택", command=browse_semi_keyword_file).grid(row=3, column=2, padx=(0, 0), pady=4, sticky=tk.W)
        self.semi_topic_var.trace_add("write", lambda *_: refresh_semi_keyword_display())
        refresh_semi_keyword_display()

        # 중복률 임계값
        # [Ver7.20 버그수정] 이 탭 전용 변수(semi_threshold_var)를 별도로 만들어
        # 썼더니 config에 저장되는 대상은 9)통합 키워드의 step3_threshold_var뿐이라
        # 재시작 시 항상 기본값 50으로 초기화되는 문제가 있었다. 중복률 판정
        # 로직이 9)통합 키워드와 완전히 동일하므로 별도 저장 로직을 새로 만드는
        # 대신 step3_threshold_var를 그대로 공유해서 쓴다 - 값이 이미 저장/로드
        # 되는 변수라 이 탭에서 입력한 값도 함께 자동으로 저장/복원된다(두 탭이
        # 같은 값을 공유하게 됨).
        # [Ver8.33 UI 정리] 입력칸과 안내 라벨을 같은 프레임에 묶어 입력칸 바로 옆에
        # 배치(위 날짜 새로고침 버튼과 동일한 사유 - 2번 열이 화면 오른쪽 끝으로
        # 멀리 떨어져 보이는 문제 수정).
        ttk.Label(tab, text="중복률 임계값:").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.semi_threshold_var = self.step3_threshold_var
        semi_threshold_frame = ttk.Frame(tab)
        semi_threshold_frame.grid(row=4, column=1, sticky=tk.W, pady=4)
        ttk.Entry(semi_threshold_frame, textvariable=self.semi_threshold_var, width=10).pack(side=tk.LEFT)
        ttk.Label(semi_threshold_frame, text="% 이상이면 중복(X)으로 자동 판정").pack(side=tk.LEFT, padx=(8, 0))

        # 실행 버튼
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(16, 8))

        self.semi_check_btn = ttk.Button(btn_frame, text="🔍 중복 검사(5단계 이식)", command=self.semi_start_duplicate_check)
        self.semi_check_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.semi_final_btn = ttk.Button(btn_frame, text="✅ 최종 처리 - 승인반영+포스팅폴더 이동(6단계 이식)",
                                          command=self.semi_start_final_processing)
        self.semi_final_btn.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btn_frame, text="📂 키워드 엑셀 열기",
                   command=lambda: self.semi_open_excel_keyword_file(self.semi_get_excel_keyword_file_path(self.semi_topic_var.get()))
                   ).pack(side=tk.LEFT, padx=(0, 8))

        # [2026-09-28 변경] 이 탭의 카테고리(B열)는 게시판 설정 엑셀이 아니라 8)2차
        # 저장 때 만들어진 게시판목록.txt만 기준으로 기록한다. 이 버튼은 설정 엑셀
        # (8탭 게시판 판정용 기준표)을 열어 보는 용도로만 남겨 둔다.
        ttk.Button(btn_frame, text="📋 게시판 설정 열기",
                   command=self.semi_open_board_config).pack(side=tk.LEFT, padx=(0, 8))
        # 설명
        desc = ("사용법: 주제·날짜 선택 → 🔍 중복 검사 실행(D~G열에 결과 기록, 엑셀 자동으로 열림) → "
                "엑셀 F열의 판정(O/X)을 검토·수정 후 저장 → ✅ 최종 처리 클릭.\n"
                "최종 처리 시: X는 perplexity_{모델}_duplicated 폴더로 이동, O는 키워드 엑셀 A/B열에 추가(B=게시판목록.txt의 카테고리 번호, 없으면 빈칸+팝업 알림)되고 "
                "MD파일(+썸네일/소제목 이미지)이 Naver_blog_keyword_perplexity_gpt_manual_markdown_for_posting 폴더로 복사됩니다.")
        ttk.Label(tab, text=desc, foreground="blue", justify=tk.LEFT, wraplength=1150).grid(
            row=6, column=0, columnspan=4, sticky=tk.W, pady=(4, 8))

        # 진행 상황
        progress_frame = ttk.LabelFrame(tab, text="진행 상황", padding="5")
        progress_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        self.semi_progress_var = tk.StringVar(value="대기 중...")
        ttk.Label(progress_frame, textvariable=self.semi_progress_var).grid(row=0, column=0, sticky=tk.W)
        progress_frame.columnconfigure(0, weight=1)

    # ── 주제별 키워드 엑셀 파일 매핑 (기본값: {base}/{topic}/{topic}_키워드.xlsx) ──
    def get_semi_keyword_config_path(self):
        base = self.base_folder_var.get().strip() or self.base_folder
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "Naver_blog_config_kin_semi_keyword.json")

    def load_semi_keyword_mapping(self):
        path = self.get_semi_keyword_config_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f).get('files', {})
        except Exception:
            return {}

    def save_semi_keyword_mapping(self, mapping):
        path = self.get_semi_keyword_config_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'files': mapping}, f, ensure_ascii=False, indent=2)

    def semi_get_excel_keyword_file_path(self, topic):
        """주제별 키워드 엑셀 경로. 사용자가 '파일 선택'으로 지정한 경로가 있으면 그것을,
        없으면 기본값 {base}/{topic}/{topic}_키워드.xlsx 를 사용한다."""
        base = self.base_folder_var.get().strip() or self.base_folder
        mapping = self.load_semi_keyword_mapping()
        filename = mapping.get(topic, '').strip()
        if filename:
            return filename if os.path.isabs(filename) else os.path.join(base, filename)
        return os.path.join(base, topic, f"{topic}_키워드.xlsx")

    # ── [반자동 이식] 주제/날짜 아래 존재하는 모든 perplexity_*_final_articles 폴더 자동탐지 ──
    def semi_find_final_article_folders(self, topic, date):
        base = self.base_folder_var.get().strip() or self.base_folder
        topic_date_path = os.path.join(base, topic, date)
        result = []
        if not os.path.isdir(topic_date_path):
            return result
        pattern = re.compile(r'^perplexity_(.+)_final_articles$')
        for entry in os.listdir(topic_date_path):
            entry_path = os.path.join(topic_date_path, entry)
            if os.path.isdir(entry_path):
                m = pattern.match(entry)
                if m:
                    result.append((m.group(1), entry_path))
        return result

    def semi_load_existing_keywords(self, keyword_file):
        """[반자동 이식] 키워드 엑셀 A열의 기존 키워드 목록 로드"""
        from openpyxl import load_workbook
        try:
            if not os.path.exists(keyword_file):
                return []
            wb = load_workbook(keyword_file)
            ws = wb.active
            keywords = []
            for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
                if row[0]:
                    keywords.append(str(row[0]).strip())
            wb.close()
            return keywords
        except Exception as e:
            self.log(f"기존 키워드 로드 오류: {str(e)}")
            return []

    def semi_open_excel_keyword_file(self, target_file):
        try:
            if not os.path.exists(target_file):
                messagebox.showinfo("알림", f"아직 파일이 없습니다:\n{target_file}")
                return
            if os.name == "nt":
                os.startfile(target_file)
            else:
                import subprocess, platform
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", target_file])
                else:
                    subprocess.Popen(["xdg-open", target_file])
        except Exception as e:
            messagebox.showerror("오류", f"엑셀 파일을 여는 중 오류:\n{e}")

    # ── [반자동 이식] 5단계: 중복 검사 ──
    def semi_start_duplicate_check(self):
        topic = self.semi_topic_var.get()
        date = self.semi_date_var.get()
        if not date:
            messagebox.showerror("오류", "검사할 날짜를 선택하세요.")
            return
        try:
            threshold = int(self.semi_threshold_var.get())
            if threshold < 0 or threshold > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("오류", "중복률 임계값은 0-100 사이의 숫자여야 합니다.")
            return

        self.semi_check_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.semi_duplicate_check_worker, args=(topic, date, threshold), daemon=True).start()

    def semi_duplicate_check_worker(self, topic, date, threshold):
        """[반자동 duplicate_check_worker 이식] 지정 주제/날짜의 모든 최종본 폴더를 스캔해 중복 판정"""
        try:
            self.log(f"🔍 [반자동이식] 중복 검사를 시작합니다... ({topic} / {date})")

            model_folders = self.semi_find_final_article_folders(topic, date)
            if not model_folders:
                self.root.after(0, lambda: messagebox.showwarning(
                    "알림", f"{topic}/{date} 아래 최종본 폴더(perplexity_*_final_articles)가 없습니다."))
                return

            new_titles = []
            for model_name, final_folder in model_folders:
                for entry in os.listdir(final_folder):
                    entry_path = os.path.join(final_folder, entry)
                    if entry.endswith('.md') and os.path.isfile(entry_path):
                        new_titles.append((entry[:-3], entry))
                    elif os.path.isdir(entry_path):
                        for f in os.listdir(entry_path):
                            if f.endswith('.md'):
                                new_titles.append((f[:-3], f))
                                break

            if not new_titles:
                self.root.after(0, lambda: messagebox.showwarning("알림", "처리할 MD 파일이 없습니다."))
                return

            scanned_folder_names = ", ".join(f"perplexity_{m}_final_articles" for m, _ in model_folders)
            keyword_file = self.semi_get_excel_keyword_file_path(topic)
            existing_keywords = self.semi_load_existing_keywords(keyword_file)
            self.log(f"📂 [{topic}] ({scanned_folder_names}) 키워드파일: {keyword_file}, 기존 키워드 {len(existing_keywords)}개")

            check_results = []
            total = len(new_titles)
            for i, (title, filename) in enumerate(new_titles):
                self.root.after(0, lambda cur=i + 1, tot=total: self.semi_progress_var.set(f"검사 중... ({cur}/{tot})"))
                self.log(f"검사 중: {title}")
                matching_results, duplicate_rate = self.find_matching_keywords(title, existing_keywords)
                auto_decision = "X" if duplicate_rate >= threshold else "O"
                self.log(f"  - 매칭 결과: {len(matching_results)}개, 중복률: {duplicate_rate:.1f}%, 판정: {auto_decision}")
                check_results.append({
                    'title': title, 'filename': filename,
                    'matching_results': matching_results,
                    'duplicate_rate': duplicate_rate, 'decision': auto_decision
                })

            self.semi_save_duplicate_check_results(check_results, keyword_file)

            self.root.after(0, lambda: self.semi_progress_var.set("완료!"))
            self.log(f"✅ 중복 검사 완료! {len(check_results)}개 제목 검사됨")
            self.root.after(0, lambda: messagebox.showinfo("완료", f"중복 검사 완료!\n검사: {len(check_results)}개\n엑셀 F열의 판정을 검토해주세요."))

        except Exception as e:
            self.log(f"❌ 중복 검사 오류: {str(e)}")
            self.root.after(0, lambda err=str(e): messagebox.showerror("오류", f"중복 검사 중 오류가 발생했습니다:\n{err}"))
        finally:
            self.root.after(0, lambda: self.semi_check_btn.config(state=tk.NORMAL))

    def semi_save_duplicate_check_results(self, results, keyword_file):
        """[반자동 save_duplicate_check_results 이식] D~G열에 결과 기록"""
        from openpyxl import Workbook, load_workbook
        try:
            self.log("📝 엑셀 파일 생성 중...")
            os.makedirs(os.path.dirname(keyword_file), exist_ok=True)

            if os.path.exists(keyword_file):
                wb = load_workbook(keyword_file)
                ws = wb.active
            else:
                wb = Workbook()
                ws = wb.active
                ws['A1'] = "키워드"
                ws['B1'] = "카테고리"
                ws['C1'] = "상태"

            max_row = ws.max_row if ws.max_row else 1

            # D열부터 끝까지 초기화
            self.log("🧹 기존 검사 결과 초기화 중...")
            max_col = ws.max_column if ws.max_column else 3
            for col in range(4, max_col + 50):
                for row in range(1, max_row + 10):
                    ws.cell(row=row, column=col).value = None

            ws.cell(row=1, column=4).value = '신규키워드'
            ws.cell(row=1, column=5).value = '중복률'
            ws.cell(row=1, column=6).value = '판정'

            self.log(f"✏️ {len(results)}개 결과 기록 중...")
            for i, result in enumerate(results):
                row_num = i + 2
                ws.cell(row=row_num, column=4).value = result.get('title', '')
                duplicate_rate = result.get('duplicate_rate', 0.0)
                ws.cell(row=row_num, column=5).value = f"{duplicate_rate:.1f}%"
                ws.cell(row=row_num, column=6).value = result.get('decision', '')
                matched_keywords = result.get('matching_results', [])[:20]
                for j, match in enumerate(matched_keywords):
                    ws.cell(row=row_num, column=7 + j).value = match.get('original_keyword', '')

            wb.save(keyword_file)
            wb.close()
            self.log(f"✅ 엑셀 저장 완료: {keyword_file}")

            self.semi_open_excel_keyword_file(keyword_file)
            self.log("✅ 중복 검사 결과 저장 완료 (D:신규키워드, E:중복률, F:판정, G~:매칭키워드)")

        except Exception as e:
            self.log(f"❌ 엑셀 저장 오류: {str(e)}")
            import traceback
            self.log(f"상세 오류:\n{traceback.format_exc()}")
            raise

    # ══════════════════════════════════════════════════════════
    # [2026-09-27 신규] 게시판(카테고리) 자동 매칭
    # ──────────────────────────────────────────────────────────
    # 환경파일: {작업폴더}/Naver_blog_지식인_게시판설정.xlsx
    #   헤더: 주제 | 카테고리명 | 카테고리 설명 | 카테고리 번호
    #   - 주제는 11)탭 주제 콤보의 값과 같은 이름을 쓴다. 경제 세부주제
    #     (경제-A~G)는 하나의 "경제통합" 블로그로 운영되므로 주제를 "경제통합"으로
    #     적은 행은 경제-A~G 어느 주제에서도 후보가 된다.
    #   - 카테고리 번호가 비어 있는 행은 무시한다(예시 행 보호).
    # 동작(2026-09-28 재설계): 이 설정 엑셀은 8)2차 각색에서 제목 확정 시 GPT가 게시판을
    # 판정하는 기준표로만 쓰인다. 11)탭 최종 처리(6단계)는 이 파일을 쓰지 않고, 8)탭
    # 저장 때 만들어진 사이드카(게시판목록.txt)의 "제목\t번호"를 그대로 키워드 엑셀
    # B열에 기록한다(사이드카에 없거나 번호가 빈 글은 B열 빈칸 + 완료 후 팝업 알림).
    # ══════════════════════════════════════════════════════════
    SEMI_BOARD_CONFIG_FILENAME = "Naver_blog_지식인_게시판설정.xlsx"
    SEMI_BOARD_HEADERS = ["주제", "카테고리명", "카테고리 설명", "카테고리 번호"]
    # [2026-09-27 2차] 8)2차 각색 저장 시 게시판 분류. "기타"는 실제 블로그 게시판이
    # 아닌 내부 상태(미분류) - GPT가 고르는 값이 아니라 코드 규칙으로만 부여한다.
    WEB2ND_BOARD_WAIT = "(제목 확정 후 자동 판정)"
    WEB2ND_BOARD_ETC = "기타(미분류)"
    BOARD_ETC_NAME = "기타"
    WEB2ND_BOARD_MIN_CONF = 60

    # [2026-09-27 3차] 다른 컴퓨터로 완성본 폴더를 통째로 옮길 때(중앙
    # 포스팅DB.json 없이도) 게시판 번호를 알 수 있도록, 같은 폴더
    # (perplexity_{모델}_final_articles/)에 같이 두는 초경량 사이드카
    # 파일. 포스팅DB처럼 본문·요약 등은 담지 않고 "제목\t카테고리번호"
    # 한 줄씩만 담는다. 추가(저장)/변경(다시 판정 후 재저장)/삭제(종합관리
    # 수동 삭제)가 전부 포스팅DB와 같은 시점에 같이 반영되어야 한다.
    KIN_SIDECAR_FILENAME = "게시판목록.txt"

    def _kin_sidecar_read(self, final_folder):
        """final_folder(perplexity_{모델}_final_articles 폴더) 안의 사이드카
        파일을 [(제목, 카테고리번호), ...] 리스트로 읽는다. 없으면 []."""
        path = os.path.join(final_folder, self.KIN_SIDECAR_FILENAME)
        items = []
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.rstrip('\n').rstrip('\r')
                        if not line.strip():
                            continue
                        parts = line.split('\t', 1)
                        t = parts[0]
                        b = parts[1] if len(parts) > 1 else ""
                        items.append((t, b))
            except Exception as e:
                self.log(f"⚠️ 사이드카 파일 읽기 오류({path}): {e}")
        return items

    def _kin_sidecar_write(self, final_folder, items):
        """items([(제목, 카테고리번호), ...])를 사이드카 파일에 그대로 쓴다.
        비어 있으면 파일을 지운다(빈 파일을 남기지 않음)."""
        path = os.path.join(final_folder, self.KIN_SIDECAR_FILENAME)
        if not items:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                self.log(f"⚠️ 사이드카 파일 삭제 오류({path}): {e}")
            return
        try:
            os.makedirs(final_folder, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                for t, b in items:
                    t_clean = str(t).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()
                    b_clean = str(b or '').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()
                    f.write(f"{t_clean}\t{b_clean}\n")
        except Exception as e:
            self.log(f"⚠️ 사이드카 파일 쓰기 오류({path}): {e}")

    def _kin_sidecar_upsert(self, final_folder, title, board_number):
        """제목 기준으로 한 줄을 추가하거나(없으면) 값을 교체한다(있으면).
        저장/재저장(다시 판정 후 재저장)에서 공용으로 쓴다."""
        norm = lambda s: self.sanitize_filename(s or "").lower()
        items = [(t, b) for t, b in self._kin_sidecar_read(final_folder) if norm(t) != norm(title)]
        items.append((title, board_number))
        self._kin_sidecar_write(final_folder, items)

    def _kin_sidecar_remove(self, final_folder, title):
        """제목이 일치하는 줄을 사이드카에서 지운다(종합관리 수동 삭제와 연동)."""
        if not final_folder:
            return
        norm = lambda s: self.sanitize_filename(s or "").lower()
        items = [(t, b) for t, b in self._kin_sidecar_read(final_folder) if norm(t) != norm(title)]
        self._kin_sidecar_write(final_folder, items)

    def _kin_sidecar_merge_into(self, src_final_folder, dst_final_folder):
        """(경제통합 자료 모으기 전용) src의 사이드카 내용을 dst의 사이드카에
        이어붙인다. 제목이 이미 dst에 있으면 건너뛴다(정상적으로는 경제
        세부주제 간 제목이 겹치지 않으므로 충돌이 생길 일은 없다)."""
        src_items = self._kin_sidecar_read(src_final_folder)
        if not src_items:
            return
        norm = lambda s: self.sanitize_filename(s or "").lower()
        dst_items = self._kin_sidecar_read(dst_final_folder)
        seen = {norm(t) for t, _ in dst_items}
        merged = list(dst_items)
        for t, b in src_items:
            if norm(t) in seen:
                continue
            merged.append((t, b))
            seen.add(norm(t))
        self._kin_sidecar_write(dst_final_folder, merged)

    def _kin_find_final_articles_folder(self, file_path):
        """포스팅DB 레코드의 file_path에서 'final_articles'가 포함된
        상위 폴더를 찾는다(제목별 폴더 저장 모드면 file_path의 부모가
        제목 폴더이고, 그 부모가 실제 final_articles 폴더이므로 위로
        최대 3단계까지 올라가며 찾는다). 못 찾으면 None."""
        if not file_path:
            return None
        d = os.path.dirname(file_path)
        for _ in range(3):
            if not d:
                return None
            if "final_articles" in os.path.basename(d):
                return d
            d = os.path.dirname(d)
        return None

    def semi_get_board_config_path(self):
        base = self.base_folder_var.get().strip() or self.base_folder
        return os.path.join(base, self.SEMI_BOARD_CONFIG_FILENAME)

    def semi_ensure_board_config_template(self):
        """설정 파일이 없으면 헤더+예시 1행이 들어간 빈 양식을 만든다."""
        path = self.semi_get_board_config_path()
        if os.path.exists(path):
            return path
        from openpyxl import Workbook
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.append(self.SEMI_BOARD_HEADERS)
        # 번호가 비어 있어 프로그램이 무시하는 예시 행
        ws.append(["경제통합", "(예시) 세금", "종합소득세·연말정산·양도세 등 세금 신고와 절세를 다루는 글", ""])
        for col, w in zip("ABCD", (24, 20, 70, 14)):
            ws.column_dimensions[col].width = w
        wb.save(path)
        wb.close()
        self.log(f"📋 게시판 설정 양식을 만들었습니다: {path}")
        return path

    def semi_open_board_config(self):
        try:
            path = self.semi_ensure_board_config_template()
            self.semi_open_excel_keyword_file(path)
        except Exception as e:
            messagebox.showerror("오류", f"게시판 설정 파일을 여는 중 오류:\n{e}")

    def semi_load_board_config(self, topic):
        """현재 주제에서 쓸 수 있는 게시판 후보 [{name, desc, number}, ...]."""
        path = self.semi_get_board_config_path()
        if not os.path.exists(path):
            return []
        from openpyxl import load_workbook
        wb = load_workbook(path, data_only=True)
        ws = wb.active
        header = [str(c.value).strip() if c.value is not None else "" for c in ws[1]]

        def col(name):
            key = name.replace(" ", "")
            for i, h in enumerate(header):
                if h.replace(" ", "") == key:
                    return i
            return None

        ci = {n: col(n) for n in self.SEMI_BOARD_HEADERS}
        if any(v is None for v in ci.values()):
            wb.close()
            raise ValueError(f"게시판 설정 헤더가 다릅니다. 1행에 {', '.join(self.SEMI_BOARD_HEADERS)} 가 필요합니다.")

        def norm_num(v):
            if v is None:
                return ""
            if isinstance(v, float) and v.is_integer():
                v = int(v)
            return str(v).strip()

        rows = []
        for r in ws.iter_rows(min_row=2, values_only=True):
            t = str(r[ci["주제"]]).strip() if r[ci["주제"]] is not None else ""
            num = norm_num(r[ci["카테고리 번호"]])
            if not t or not num:
                continue
            if t == topic or (topic.startswith("경제") and t == "경제통합") \
                    or (topic == "경제통합" and t.startswith("경제")):
                rows.append({
                    "name": str(r[ci["카테고리명"]] or "").strip(),
                    "desc": str(r[ci["카테고리 설명"]] or "").strip(),
                    "number": num,
                })
        wb.close()
        # 같은 번호 중복 제거(경제통합 행 + 경제-X 행이 함께 걸린 경우)
        seen, uniq = set(), []
        for b in rows:
            if b["number"] in seen:
                continue
            seen.add(b["number"])
            uniq.append(b)
        return uniq

    def semi_gpt_pick_board(self, title, body, boards):
        """GPT가 글을 분석해 게시판 하나를 고른다. 반환 {number, confidence, reason}."""
        heads = [l[3:].strip() for l in (body or "").split('\n') if l.startswith('## ')]
        plain = "\n".join(l for l in (body or "").split('\n') if not l.startswith('#')).strip()
        board_lines = "\n".join(f"{b['number']} | {b['name']} | {b['desc']}" for b in boards)
        prompt = (
            "당신은 블로그 게시판 분류 담당자입니다. 아래 글을 읽고 가장 알맞은 게시판 하나를 고르세요.\n\n"
            "[게시판 목록: 번호 | 이름 | 설명]\n" + board_lines + "\n\n"
            f"[글 제목]\n{title}\n\n"
            f"[소제목]\n{chr(10).join(heads[:12]) or '(없음)'}\n\n"
            f"[본문 앞부분]\n{plain[:1200]}\n\n"
            "[규칙]\n"
            "- 반드시 위 목록에 있는 번호 중 하나만 고릅니다. 목록에 없는 번호는 만들지 않습니다.\n"
            "- 글의 핵심 주제(제목의 중심 키워드)를 기준으로 판단하고, 게시판 설명에 가장 가까운 것을 고릅니다.\n"
            "- 어느 게시판에도 맞지 않으면 number를 null로 둡니다.\n"
            "- confidence는 0~100 정수(확신 정도)입니다.\n"
            '- 아래 JSON만 출력합니다: {"number": "번호 또는 null", "confidence": 0, "reason": "한 문장"}'
        )
        resp = self.openai_client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = (resp.choices[0].message.content or "").strip()
        try:
            data = json.loads(raw)
        except Exception:
            m = re.search(r'\{.*\}', raw, re.S)
            data = json.loads(m.group(0)) if m else {}
        num = data.get("number")
        num = "" if num in (None, "null", "None") else str(num).strip()
        valid = {b["number"] for b in boards}
        if num not in valid:
            num = ""
        try:
            conf = int(data.get("confidence", 0))
        except Exception:
            conf = 0
        return {"number": num, "confidence": conf if num else 0, "reason": str(data.get("reason", ""))[:120]}

    def semi_keyword_pick_board(self, title, body, boards):
        """GPT를 못 쓸 때의 예비 판정 - 카테고리명/설명의 단어가 제목·소제목에 얼마나 나오는지."""
        heads = " ".join(l[3:] for l in (body or "").split('\n') if l.startswith('## '))
        best, best_score = None, 0
        for b in boards:
            toks = set(re.findall(r'[가-힣A-Za-z0-9]{2,}', f"{b['name']} {b['desc']}"))
            score = sum(3 for t in toks if t in title) + sum(1 for t in toks if t in heads)
            if score > best_score:
                best, best_score = b, score
        if best is None:
            return {"number": "", "confidence": 0, "reason": "키워드 일치 없음"}
        return {"number": best["number"], "confidence": min(60, best_score * 10), "reason": "키워드 일치(예비 판정)"}

    def semi_category_map_from_sidecar(self, topic, date, titles):
        """[2026-09-28 신규] 11)탭 카테고리 기록용. 선택한 주제/날짜 아래 모든
        perplexity_*_final_articles 폴더의 게시판목록.txt(사이드카)를 읽어
        {제목: 카테고리 번호}를 만든다. 제목 비교는 사이드카 저장 때와 같은 정규화
        (sanitize_filename 후 소문자)를 쓴다.
        반환 (category_map, 사이드카에 없는 제목 목록, 번호가 빈 제목 목록)."""
        norm = lambda s: self.sanitize_filename(s or "").lower()
        by_title = {}
        for _model, folder in self.semi_find_final_article_folders(topic, date):
            for t, b in self._kin_sidecar_read(folder):
                by_title[norm(t)] = str(b or "").strip()
        category_map, missing, empty = {}, [], []
        for title in titles:
            key = norm(title)
            if key not in by_title:
                missing.append(title)
                category_map[title] = ""
            elif not by_title[key]:
                empty.append(title)
                category_map[title] = ""
            else:
                category_map[title] = by_title[key]
        return category_map, missing, empty

    # ── [반자동 이식] 6단계: 최종 처리 ──
    def semi_start_final_processing(self):
        # tk 변수는 메인 스레드에서 읽어 워커에 넘긴다.
        self._semi_run_ctx = {
            "date": self.semi_date_var.get().strip(),
        }
        threading.Thread(target=self.semi_final_processing_worker, daemon=True).start()

    def semi_final_processing_worker(self):
        """[반자동 final_processing_worker 이식] F열(판정) 기준으로 O만 A/B 추가,
        파일 분류(X→중복폴더 이동, O→포스팅폴더 복사) 후 D~끝 열 삭제."""
        from openpyxl import load_workbook
        try:
            topic = self.semi_topic_var.get()
            self.log(f"✅ [반자동이식] 최종 처리를 시작합니다... (주제: {topic})")

            keyword_file = self.semi_get_excel_keyword_file_path(topic)
            if not os.path.exists(keyword_file):
                self.root.after(0, lambda: messagebox.showwarning("알림", "키워드 엑셀 파일이 없습니다. 먼저 중복 검사를 실행하세요."))
                return

            wb = load_workbook(keyword_file)
            ws = wb.active

            approved_titles, rejected_titles = [], []
            max_row = ws.max_row if ws.max_row else 1
            max_col = ws.max_column if ws.max_column else 1

            if max_col < 6:
                wb.close()
                self.root.after(0, lambda: messagebox.showwarning("알림", "판정(F열)이 없습니다. 중복 검사를 먼저 실행하세요."))
                return

            for r in range(2, max_row + 1):
                title_d = ws.cell(row=r, column=4).value
                decision_f = ws.cell(row=r, column=6).value
                if not title_d:
                    continue
                if decision_f and str(decision_f).strip().upper() == 'O':
                    approved_titles.append(str(title_d).strip())
                elif decision_f and str(decision_f).strip().upper() == 'X':
                    rejected_titles.append(str(title_d).strip())

            wb.close()

            if not approved_titles and not rejected_titles:
                self.root.after(0, lambda: messagebox.showwarning("알림", "처리할 데이터가 없습니다. 중복 검사를 먼저 실행하세요."))
                return

            self.log(f"📂 [{topic}] 키워드파일: {keyword_file} (승인 {len(approved_titles)}개, 거부 {len(rejected_titles)}개)")

            # [2026-09-28 재설계] 카테고리는 8)2차 저장 때 만들어진 사이드카
            # (게시판목록.txt)의 "제목\t번호"만 기준으로 삼는다. 게시판 설정 엑셀/
            # GPT 판정/포스팅DB 조회/직전 카테고리 재사용은 이 경로에서 쓰지 않는다.
            # 사이드카에 없는 제목(프로그램을 거쳐 만들어지지 않은 글)이나 번호가
            # 비어 있는 글('기타' 저장분)은 B열을 비워 두고 끝난 뒤 팝업으로 알린다.
            category_map = {}
            cat_missing, cat_empty = [], []
            if approved_titles:
                ctx = getattr(self, '_semi_run_ctx', {}) or {}
                category_map, cat_missing, cat_empty = self.semi_category_map_from_sidecar(
                    topic, ctx.get("date", ""), approved_titles)
                self.log(f"🗂 사이드카 기준 카테고리: 매칭 {len(approved_titles) - len(cat_missing) - len(cat_empty)}건 / "
                         f"사이드카에 없음 {len(cat_missing)}건 / 번호 비어 있음(기타) {len(cat_empty)}건")
                for t in cat_missing:
                    self.log(f"  ⚠️ 카테고리 미매칭(사이드카에 없음): {t}")
                for t in cat_empty:
                    self.log(f"  ⚠️ 카테고리 비어 있음(8탭 '기타' 저장): {t}")

            # 파일 이동(거부분 중복 폴더로)
            self.semi_move_files_by_decision(topic, approved_titles, rejected_titles)

            # 승인된 것만 A/B 추가
            if approved_titles:
                self.semi_add_approved_keywords(approved_titles, keyword_file, category_map)

            # 승인된 MD 파일들을 포스팅 폴더로 복사
            if approved_titles:
                self.semi_copy_approved_files_to_markdown_folder(approved_titles, topic)

            # D열부터 끝까지 삭제
            wb2 = load_workbook(keyword_file)
            ws2 = wb2.active
            max_col_to_delete = ws2.max_column - 3
            if max_col_to_delete > 0:
                ws2.delete_cols(4, max_col_to_delete)
            wb2.save(keyword_file)
            wb2.close()

            self.root.after(0, lambda: self.semi_progress_var.set("완료!"))
            self.log(f"✅ 최종 처리 완료! 승인: {len(approved_titles)}개, 거부: {len(rejected_titles)}개 (D열~ 삭제됨)")
            self.root.after(0, lambda: messagebox.showinfo(
                "완료", f"최종 처리가 완료되었습니다!\n승인: {len(approved_titles)}개\n거부: {len(rejected_titles)}개"))
            if cat_missing or cat_empty:
                def _show_cat_warning(miss=list(cat_missing), emp=list(cat_empty)):
                    lines = ["아래 키워드는 카테고리(B열)를 채우지 못해 빈칸으로 기록했습니다.",
                             "포스팅DB와 어긋날 수 있으니 확인 후 직접 지정하세요.", ""]
                    if miss:
                        lines.append(f"■ 게시판목록.txt에 없는 제목 ({len(miss)}건) - 프로그램을 거쳐 만들어진 글이 아닐 수 있음")
                        lines += [f"  · {t}" for t in miss[:30]]
                        if len(miss) > 30:
                            lines.append(f"  … 외 {len(miss) - 30}건")
                    if emp:
                        lines.append(f"■ 번호가 비어 있는 제목 ({len(emp)}건) - 8)2차 저장 때 '기타(미분류)'로 저장됨")
                        lines += [f"  · {t}" for t in emp[:30]]
                        if len(emp) > 30:
                            lines.append(f"  … 외 {len(emp) - 30}건")
                    messagebox.showwarning("카테고리 미매칭 알림", "\n".join(lines))
                self.root.after(0, _show_cat_warning)

        except Exception as e:
            self.log(f"❌ 최종 처리 오류: {str(e)}")
            self.root.after(0, lambda err=str(e): messagebox.showerror("오류", f"최종 처리 중 오류가 발생했습니다:\n{err}"))

    def semi_move_files_by_decision(self, topic, approved_titles, rejected_titles):
        """[반자동 move_files_by_decision 이식] 거부된 제목의 MD를 각 모델별 중복 폴더로 이동"""
        import shutil
        try:
            base = self.base_folder_var.get().strip() or self.base_folder
            item_path = os.path.join(base, topic)
            if not os.path.isdir(item_path):
                self.log(f"⚠️ 주제 폴더 없음: {item_path}")
                return

            normalized_rejected = [self.sanitize_filename(title) for title in rejected_titles]

            date_dirs = [d for d in os.listdir(item_path)
                         if os.path.isdir(os.path.join(item_path, d)) and re.match(r'\d{4}-\d{2}-\d{2}', d)]
            if not date_dirs:
                return
            latest_date = sorted(date_dirs, reverse=True)[0]

            model_folders = self.semi_find_final_article_folders(topic, latest_date)
            if not model_folders:
                return

            for model_name, final_folder in model_folders:
                duplicate_folder = os.path.join(item_path, latest_date, f"perplexity_{model_name}_duplicated")
                os.makedirs(duplicate_folder, exist_ok=True)

                for entry in os.listdir(final_folder):
                    entry_path = os.path.join(final_folder, entry)

                    if entry.endswith('.md') and os.path.isfile(entry_path):
                        filename = entry
                        file_path = entry_path
                        is_folder = False
                    elif os.path.isdir(entry_path):
                        md_in_folder = next((f for f in os.listdir(entry_path) if f.endswith('.md')), None)
                        if not md_in_folder:
                            continue
                        filename = md_in_folder
                        file_path = os.path.join(entry_path, md_in_folder)
                        is_folder = True
                    else:
                        continue

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    lines = content.split('\n')
                    file_title = ""
                    for line in lines:
                        if line.startswith('# '):
                            file_title = line[2:].strip()
                            break
                    if not file_title:
                        continue

                    normalized_file_title = self.sanitize_filename(file_title)
                    title_rejected = any(normalized_file_title.lower() == rt.lower() for rt in normalized_rejected)

                    if title_rejected:
                        if is_folder:
                            duplicate_path = os.path.join(duplicate_folder, entry)
                            os.rename(entry_path, duplicate_path)
                            self.log(f"중복 폴더 이동: {entry} ({model_name})")
                        else:
                            duplicate_path = os.path.join(duplicate_folder, filename)
                            os.rename(file_path, duplicate_path)
                            self.log(f"중복 파일 이동: {filename} ({model_name})")

        except Exception as e:
            self.log(f"파일 이동 오류: {str(e)}")

    def semi_add_approved_keywords(self, approved_titles, keyword_file, category_map=None):
        """[반자동 add_approved_keywords 이식] 승인된 제목을 A/B열에 추가.
        [2026-09-28] B열은 category_map({제목: 카테고리 번호})의 값만 기록한다(사이드카
        게시판목록.txt 기준). 값이 없으면 빈칸이며, 예전의 '마지막 카테고리 값 재사용'은
        더 이상 쓰지 않는다."""
        from openpyxl import Workbook, load_workbook
        category_map = category_map or {}
        try:
            if not os.path.exists(keyword_file):
                os.makedirs(os.path.dirname(keyword_file), exist_ok=True)
                wb = Workbook()
                ws = wb.active
                ws['A1'] = "키워드"
                ws['B1'] = "카테고리"
                wb.save(keyword_file)

            wb = load_workbook(keyword_file)
            ws = wb.active

            write_row = ws.max_row + 1 if ws.max_row >= 1 else 2
            for title in approved_titles:
                ws.cell(row=write_row, column=1, value=str(title))
                ws.cell(row=write_row, column=2, value=category_map.get(title, "") or "")
                write_row += 1

            wb.save(keyword_file)
            wb.close()
            self.log(f"✅ 승인 키워드 {len(approved_titles)}개 A/B 추가 완료 ({keyword_file}, B=사이드카 카테고리 번호)")

        except Exception as e:
            self.log(f"❌ 승인 키워드 추가 오류: {str(e)}")
            raise

    def semi_copy_approved_files_to_markdown_folder(self, approved_titles, topic):
        """[반자동 copy_approved_files_to_markdown_folder 이식, Ver7.42 재작성]
        승인된 MD 파일을 지정된 포스팅 폴더(Naver_blog_keyword_perplexity_
        gpt_manual_markdown_for_posting)로 복사한다.

        [Ver7.42 재작성 배경 - Ver7.41 되돌림] 실제 소스 구조는 딱 두
        가지뿐이라는 사용자 확인:
          1) 작업폴더 안에 "키워드명" 폴더가 이미 있고, 그 안에 MD/썸네일/
             소제목이미지가 여러 개 들어있는 경우 → 그 폴더를 통째로
             (shutil.copytree) 지정 포스팅 폴더로 복사.
          2) 작업폴더에 MD 파일과 썸네일 이미지가 낱개로(폴더 없이) 존재
             하는 경우 → 새 폴더를 만들지 않고 낱개 상태 그대로 지정
             포스팅 폴더로 복사.
        Ver7.41에서는 2)번 케이스에서 썸네일이 발견되면 새 제목 폴더를
        만들어 안에 넣도록 잘못 고쳤었음(원본 첫 코드의 "낱개는 낱개로"
        동작과 다름) - 이번에 원래 동작대로 되돌림. 또한 존재하지도
        않는 "소제목 이미지가 낱개로 흩어져 있는 경우"를 찾던 매칭
        로직도 제거(실제로는 소제목이미지는 항상 1)번처럼 이미 폴더
        안에 같이 있고, 낱개 상태로 흩어져 있는 경우는 없음).
        지정 포스팅 폴더 경로는 base_folder와 결합하지 않은 고정
        상대경로 그대로 유지(다른 오토포스팅 프로그램들과 동일 폴더에서
        실행된다는 전제로 정해진 지정 경로이므로 손대지 않음)."""
        import shutil
        try:
            base = self.base_folder_var.get().strip() or self.base_folder
            # 지정된 포스팅 폴더 - 고정 상대경로 그대로 유지(수정 금지)
            markdown_folder = "Naver_blog_keyword_perplexity_gpt_manual_markdown_for_posting"
            os.makedirs(markdown_folder, exist_ok=True)

            copied_count = 0
            normalized_approved = [self.sanitize_filename(title) for title in approved_titles]
            self.log(f"승인된 제목 수: {len(approved_titles)} (주제: {topic})")

            item_path = os.path.join(base, topic)
            if not os.path.isdir(item_path):
                return
            date_dirs = [d for d in os.listdir(item_path)
                         if os.path.isdir(os.path.join(item_path, d)) and re.match(r'\d{4}-\d{2}-\d{2}', d)]
            if not date_dirs:
                return
            latest_date = sorted(date_dirs, reverse=True)[0]
            model_folders = self.semi_find_final_article_folders(topic, latest_date)
            if not model_folders:
                return

            image_exts = [".png", ".jpg", ".jpeg", ".webp"]

            for model_name, final_folder in model_folders:
                for entry in os.listdir(final_folder):
                    entry_path = os.path.join(final_folder, entry)

                    if entry.endswith('.md') and os.path.isfile(entry_path):
                        filename = entry
                        file_path = entry_path
                        source_asset_folder = final_folder
                        is_folder = False
                    elif os.path.isdir(entry_path):
                        md_in_folder = next((f for f in os.listdir(entry_path) if f.endswith('.md')), None)
                        if not md_in_folder:
                            continue
                        filename = md_in_folder
                        file_path = os.path.join(entry_path, md_in_folder)
                        source_asset_folder = entry_path
                        is_folder = True
                    else:
                        continue

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    lines = content.split('\n')
                    file_title = ""
                    for line in lines:
                        if line.startswith('# '):
                            file_title = line[2:].strip()
                            break
                    if not file_title:
                        self.log(f"제목을 찾을 수 없는 파일: {filename}")
                        continue

                    normalized_file_title = self.sanitize_filename(file_title)
                    title_matched = False
                    matched_raw_title = None
                    for raw_title, norm_title in zip(approved_titles, normalized_approved):
                        if normalized_file_title.lower() == norm_title.lower():
                            title_matched = True
                            matched_raw_title = raw_title
                            break

                    if not title_matched:
                        self.log(f"매칭되지 않은 파일: {filename} (제목: {file_title[:30]}...)")
                        continue

                    base_name, _ = os.path.splitext(os.path.basename(file_path))

                    if is_folder:
                        # ── 케이스1: 이미 키워드명 폴더로 존재(MD+썸네일+
                        # 소제목이미지 다수) - 폴더째 그대로 지정 포스팅
                        # 폴더로 복사 ──
                        dest_title_folder = self._kin_unique_path(
                            os.path.join(markdown_folder, matched_raw_title))
                        shutil.copytree(source_asset_folder, dest_title_folder)
                        file_count = sum(len(fs) for _r, _d, fs in os.walk(dest_title_folder))
                        copied_count += 1
                        self.log(f"📁 폴더째 복사(원본 구조 그대로, {file_count}개 파일): {matched_raw_title}")
                        continue

                    # ── 케이스2: MD+썸네일이 낱개로 존재 - 새 폴더를 만들지
                    # 않고 낱개 상태 그대로 지정 포스팅 폴더로 복사 ──
                    dest_path = self._kin_unique_path(os.path.join(markdown_folder, filename))
                    shutil.copy2(file_path, dest_path)

                    for ext in image_exts:
                        image_path = os.path.join(source_asset_folder, base_name + ext)
                        if os.path.exists(image_path):
                            try:
                                dest_img_path = self._kin_unique_path(
                                    os.path.join(markdown_folder, base_name + ext))
                                shutil.copy2(image_path, dest_img_path)
                                self.log(f"🖼️ 썸네일도 낱개로 함께 복사됨: {base_name + ext}")
                            except Exception as e:
                                self.log(f"⚠️ 썸네일 복사 오류: {base_name + ext} → {e}")

                    copied_count += 1
                    self.log(f"MD 파일 복사(낱개): {filename} (제목: {file_title[:30]}...)")

            self.log(f"승인된 MD 파일 {copied_count}개 복사 완료 -> {markdown_folder}")
            if copied_count < len(approved_titles):
                self.log(f"⚠️ 일부 파일이 복사되지 않았습니다. 예상: {len(approved_titles)}개, 실제: {copied_count}개")

        except Exception as e:
            self.log(f"MD 파일 복사 오류: {str(e)}")


def main():
    root = tk.Tk()
    app = MarkdownExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()