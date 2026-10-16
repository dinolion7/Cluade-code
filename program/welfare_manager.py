# -*- coding: utf-8 -*-
"""
welfare_manager.py — 복지로 관리 프로그램 (Ver10.13, 2026-10-16)
복지로(중앙부처·지자체) Open API로 복지서비스를 모으고, Claude 웹으로 블로그 글·인포그래픽을
만드는 준비 프로그램(단일 파일 Tkinter). 실제 네이버 발행은 포스팅 프로그램(blog_poster.py)이 한다.

[이 머리말 쓰는 법] 지금 동작·지켜야 할 규칙·"이런 경우 이렇게"만 적는다. 실패했다 고친 과정은
적지 않는다(git 기록에 있다). 버전 한 줄은 맨 아래 [버전]에만. 상세 화면 설명은 program/README.md.

[파일·폴더] (실행 파일 옆)
  Naver_blog_config_복지로.json            설정(인증키·프롬프트 파일명·경로·Base IP 등)
  Naver_blog_복지로_markdown_work_folder/  작업 폴더
    data/            수집 원본(services_list.json, first_seen.json, posting_status.json,
                     quota_state.json, services/, services_lcgv/), 서비스별 자료 폴더
    final_posts/     최종각색 MD(제목별 폴더) → 6)키워드 등록 때 final_posts_backup/으로 이동
    Naver_blog_복지로_keyword.xlsx / _posting_history.xlsx
  Naver_blog_keyword_perplexity_gpt_manual_markdown_for_posting/  포스팅 프로그램이 읽는 공용 폴더
  ui_theme.py                              화면 디자인(왼쪽 메뉴·카드·버튼 색, 정책뉴스와 공용) — 없거나 오류면 예전 모습으로 실행
  준비: pip install requests openpyxl selenium (코드 카드는 playwright)

[탭과 흐름]
  1)중앙부처복지서비스 · 2)지자체복지서비스 — 목록조회 → 상세조회(받은 건 건너뜀, 일일 한도 표시)
  3)리스트업 — 전체·미수집·신규, 우선순위, 연관정책, 중복 정책 재검사
  4)포스팅 관리 — 목록에서 서비스 선택 → STEP 1~4 (그만둘 글은 목록 아래 "⏭ 이 글 패스")
    STEP 1 포스팅 가치 빠른 판단: 📋 원문자료 + 프롬프트 복사(새 대화창) → 💾 판정결과 저장(메모리값
           자동저장) → 진행이면 키워드 리서치 + 상위 경쟁 블로그 스크랩 자동. 결과 두 줄, 경쟁 블로그 "보기".
    STEP 2 가치판단·제목 후보: 📋 판정결과·키워드 리서치 + 프롬프트 복사(같은 대화창) · 📂 공식자료
           폴더 열기 · 키워드 리서치 줄(늘 보임) · 💾 가치판단 저장. Claude가 자료를 요청하면 저장하지
           않고 안내, 키워드를 다시 요청하면 그 키워드로 리서치해 "AI에게 결과 전달" 내용을 클립보드에.
    STEP 3 제목 확정: 📋 제목 후보 불러오기 → 🔍 블로그·🔍 앞구·🔍 뒷구로 직접 확인 → ✅ 최종 확정
    STEP 4 초안(📋 확정제목 + 프롬프트 복사) → 최종각색(📋 프롬프트 복사 / 📋 초안 + 프롬프트 복사)
           → 💾 최종각색 저장(확인 창: 제목·출처 줄 점검, 문단 정리) → 포스팅 전 확인 → 인포그래픽으로 이동
  5)인포그래픽 작성 — 📋 프롬프트 복사 / 📋 최종원고 + 프롬프트 복사, 제목 목록, 코드 카드(선택)
                      → ✅ 인포그래픽 완료 → 6)키워드 등록으로 이동
  6)키워드 등록 — 날짜 선택(MD 저장한 날)·🔄 폴더 새로고침·상태 필터(정책뉴스와 같은 줄) → final_posts 스캔
                 (신규/이미등록) → 등록(선택 없으면 화면에 보이는 신규만): 백업 이동·공용 폴더 복사·키워드 엑셀·🟢 포스팅대기
  7)포스팅 이력관리 — 🟢 포스팅대기 → ✅ 포스팅완료(실제 발행 뒤), 🗑 포스팅후삭제
  8)설정 — 인증키·프롬프트 파일명·경로·네이버 접속 IP·OpenAI 키(문단 정리)

[상태]  🆕 신규 → 🔎 가치판단대기 → 📝 초안작성중 → ✒️ 최종각색중 → 🎨 인포그래픽준비중
        (복사 버튼이 자동으로 올림, 뒤로 내리지 않음) → 🟢 포스팅대기(6)등록) → 📤 포스팅완료(7)에서)
        ⏭ 패스 / ⏸ 보류(빠른 판단·가치판단이 보류면 확인 후). 패스·보류 글은 STEP 1 복사 때 다시 할지 묻는다.

[반드시 지킬 규칙]
  - 본문 주소에는 https://·http://·www. 를 붙이지 않는다(하이퍼링크 안 씀 — 네이버가 링크·미리보기 카드로
    바꿔 줄이 깨짐). 최종각색 저장 때 strip_url_prefixes()가 떼고 알려 준다.
  - 📤 포스팅완료는 되돌리지 않는다(set_posting_status가 거부). 🗑 포스팅후삭제로는
    mark_post_deleted_from_blog() 한 통로로만(이중 확인).
  - 중앙부처를 포스팅완료로 바꿀 때 이름이 비슷한 지자체 정책이 미처리면 막고 연관 정책 팝업으로 안내.
  - 버튼 이름·배치는 CLAUDE.md 작업 원칙대로: 칸 제목이 단계, 버튼 "(넘기는 것) + 프롬프트 복사",
    "(무엇) 저장(메모리값 자동저장)". 정책뉴스와 같은 기능은 정책뉴스 이름(키워드 리서치 실행·검색량·
    자동완성 조회·AI에게 결과 전달·🔍 앞구/뒷구·✅ 최종 확정). 같은 대화창용 "📋 프롬프트 복사"는
    한도를 아끼는 버튼 — 새 대화창용과 함께 두고 지우지 않는다.
  - 자동 처리가 실패하면 그 자리에 원인과 누를 버튼을 보여 준다(접힌 보조 칸에 숨기지 않는다).
  - 공식 출처 원칙: 블로그 글은 구성 참고용으로만 복사본에 넣고 사실·출처로 쓰지 않는다. 최종각색
    저장 때 출처 줄(공식기관 도메인)을 점검한다.
  - 네이버 검색 창은 매번 새 임시 프로필(비로그인)로 연다. Base IP가 있으면 IP가 다를 때 열지 않는다.
  - 프롬프트 파일 맨 위 [참고 메모] 블록은 복사할 때 뺀다.
  - 문단 정리(GPT)는 기본 꺼짐 — 줄바꿈만 넣고, 공백 뺀 본문이 원본과 다르면 원본을 쓴다.

[이런 경우 이렇게]
  - Claude가 키워드를 "/"·"·" 등으로 묶어 보냄 → split_keyword_line()이 , / · | 、 ; 줄바꿈·목록 기호로
    나눠 하나씩 리서치한다(묶음째 검색하면 0건).
  - 재조사 요청 키워드 → "재조사 요청 키워드:" 아래 작은 코드블럭(통합 V13)과 같은 줄 형식 둘 다 읽는다.
  - 복사한 답이 ``` 로 감싸져 있음 → 바깥 울타리만 벗기고 읽는다.
  - 경쟁 블로그 0개 → 원인(검색 0건·쓸 글 없음·스크랩 실패)을 적고 직접 고르는 줄을 펼친다. 없어도 진행 가능.
  - 같은 서비스를 다시 선택(트리 새로고침) → 키워드 칸을 덮어쓰지 않는다(servId 비교).
  - 코드 카드 JSON 오류 → Claude가 낸 JSON 자체가 틀린 경우가 있다(예: compare의 "right": 이름표 빠짐). ④가 오류 자리
    앞뒤 글자와 함께 고쳐 달라는 문구를 클립보드에 넣고, Claude가 고친 답을 복사한 뒤 ④를 다시 누르면 ② 칸의 옛 답 대신
    클립보드의 고친 답을 읽는다. 안 보이는 공백·굽은 따옴표·끝 쉼표는 card_json_loads()가 고쳐 읽는다.
  - ④를 눌렀는데 ② 칸이 비었음(프로그램을 다시 켠 뒤 등) → 클립보드에 읽을 수 있는 설계도가 있으면 그걸 쓴다.
    없을 때만 _카드작업의 지난 답변 파일을 쓸지 날짜를 보여 주고 묻는다(말없이 지난 답을 읽지 않는다).
  - API 일일 한도 초과 → QuotaExceededError로 멈춘다(재시도 안 함). 일일 사용량은 quota_state.json.

[버전] Ver10.13 — 최종각색 저장 때 주소의 https://·www. 를 뗌(네이버 자동 링크 방지).
       Ver10.12 6)키워드 등록 날짜 선택·상태 필터 줄. Ver10.11 화면 디자인(ui_theme.py).
       이전 버전의 바뀐 점은 program/README.md와 git 기록.
"""

import sys
import os
import shutil
import json
import time
import difflib
import bisect
import math
import re
import queue
import datetime
import threading
import mimetypes
import tempfile
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse, quote

import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# ✅ [2026-09-05] 통합 키워드/포스팅 파일 관리 모듈(선택적 연동) - 복지로/
# 정책뉴스 두 게시판의 키워드를 한 블로그에서 같이 운영하기 위해, 새 키워드를
# 원본 엑셀에 쓸 때 통합 엑셀에도 같이 쓴다(dual-write). 이 모듈 파일이 같은
# 폴더에 없어도(=아직 통합 기능을 안 쓰는 환경) 이 서브프로그램 자체는 지금과
# 완전히 동일하게 동작해야 하므로 optional import로 처리한다.
try:
    from Naver_blog_unified_management_module import append_titles_to_unified_keyword_excel
    HAS_UNIFIED_MODULE = True
except ImportError:
    HAS_UNIFIED_MODULE = False

# ✅ [2026-09-29] 게시판(카테고리) 판정 공용 모듈(선택적 연동) - 이 모듈이나 게시판
# 설정 엑셀이 없으면 6)키워드 등록 탭은 예전 방식(카테고리 입력란)으로 동작한다.
try:
    import Naver_blog_board_module as board_mod
    HAS_BOARD_MODULE = True
except ImportError:
    board_mod = None
    HAS_BOARD_MODULE = False

# 블로그 스크랩(v4.5, 예전 5)블로그 스크랩 탭 — Ver10.08에서 탭은 삭제, 자동 준비가 씀) — naver_blog_scraper.py 독립 프로그램을 통째로
# 이식. selenium이 없어도 프로그램 자체는 뜨게 하고(다른 탭은 정상 사용),
# 이 탭 실행 시점에만 안내 메시지로 막는다(다른 optional 의존성과 동일 패턴).
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as SeleniumChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

# ============================================================
# 경로 / 상수 설정 (정책뉴스·지식인 프로그램과 동일한 컨벤션)
#   - BASE_DIR   : 실행파일(.py 또는 .exe)이 있는 위치
#   - CONFIG_PATH: 설정파일(인증키 포함) — BASE_DIR에 위치(실행파일과 함께 이동)
#   - WORK_DIR   : 메인 작업폴더 — 기본값은 있지만 설정 탭에서 다른 위치로
#                  바꿀 수 있다(정책뉴스 프로그램의 output_dir/prompt_dir과
#                  동일한 방식). 아래 값들은 "기본값"이고, 실제로는 항상
#                  apply_work_dir_from_config()가 config.json을 반영해
#                  이 전역값들을 재계산한다 — 이 상수들을 직접 쓰는 코드는
#                  없고, 전부 이 전역 이름을 그때그때 참조한다(재할당되면
#                  자동으로 새 값을 보게 됨).
# ============================================================
BASE_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
BASE_DIR = str(BASE_DIR)

CONFIG_PATH = os.path.join(BASE_DIR, "Naver_blog_config_복지로.json")
# 예전 버전에서 쓰던 인증키 파일 — 있으면 config.json으로 1회 마이그레이션 후 참고용으로만 남김
_LEGACY_KEY_FILE = os.path.join(BASE_DIR, "service_key.txt")

WORK_FOLDER_NAME = "Naver_blog_복지로_markdown_work_folder"
_DEFAULT_WORK_DIR = os.path.join(BASE_DIR, WORK_FOLDER_NAME)


# ============================================================
# 공용 환경설정(env.txt) — 정책뉴스/지식인/메인 오토포스팅 프로그램과
# 완전히 동일한 방식으로 이식(Naver_blog_env_config/env.txt, BASE_DIR
# 기준 상대경로). 여러 서브프로그램이 전부 같은 폴더 트리 안에 있다면
# 물리적으로 같은 파일을 공유하게 되어, 어느 프로그램에서 Base IP나
# 네트워크 모드를 바꿔도 다른 프로그램에 즉시 반영된다. config.json
# (복지로 전용 설정)과는 별개의 파일이다 — 이건 "여러 프로그램이 공유
# 해야 하는 값"만 담는 자리.
# ============================================================
_ENV_CONFIG_CACHE = None


def _load_env_config() -> dict:
    """공용 환경설정 파일 로드(key=value 형식, 캐싱) — 메인 프로그램과 동일 파일 사용."""
    global _ENV_CONFIG_CACHE
    if _ENV_CONFIG_CACHE is not None:
        return _ENV_CONFIG_CACHE

    env = {}
    try:
        env_path = os.path.join(BASE_DIR, "Naver_blog_env_config", "env.txt")
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    except OSError:
        pass

    _ENV_CONFIG_CACHE = env
    return env


def get_env_value(key: str, default: str = "") -> str:
    """환경설정 값 조회(없으면 default 반환)."""
    return _load_env_config().get(key, default)


def update_env_value(key: str, value: str):
    """env.txt 특정 키 값만 갱신(없으면 추가, 있으면 교체) — 메인 프로그램과 동일 파일."""
    global _ENV_CONFIG_CACHE
    env_dir = os.path.join(BASE_DIR, "Naver_blog_env_config")
    os.makedirs(env_dir, exist_ok=True)
    env_path = os.path.join(env_dir, "env.txt")

    existing = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    existing[k.strip()] = v.strip()

    existing[key] = value

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# Naver 블로그 자동포스팅 환경설정\n\n")
        for k, v in existing.items():
            f.write(f"{k}={v}\n")

    _ENV_CONFIG_CACHE = None


def get_current_public_ip():
    """현재 공인 IP 조회(외부 서비스 3개 순차 시도) — 정책뉴스 프로그램과
    동일한 서비스 목록. requests가 이미 있으므로 urllib 대신 그걸 쓴다."""
    for url in ["https://api.ipify.org", "https://icanhazip.com", "https://checkip.amazonaws.com"]:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp.text.strip()
        except requests.RequestException:
            continue
    return None


def find_chrome_executable() -> str:
    """설치된 크롬 실행파일 경로를 OS별로 탐색(못 찾으면 빈 문자열).
    Windows/맥/리눅스 순으로 흔한 설치 위치를 확인한다."""
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
    """네이버 검색 결과 창을 크롬으로 연다(성공 시 True). 계정/키워드
    자동완성 이력 등이 검색에 영향을 주지 않도록, 블로그 순위체크 모듈과
    동일하게 매번 새로 만드는 임시 프로필(--user-data-dir)로 실행해 항상
    비로그인 상태로 뜨게 한다(크롬 기본 --incognito는 동기화 계정이 남아
    있으면 완전한 비로그인이 보장되지 않는 경우가 있어 임시 프로필 방식이
    더 확실함). 임시 프로필 폴더는 자동 정리하지 않는다(크롬이 켜져 있는
    동안 지우면 오류가 나므로) — OS 임시폴더에 쌓이지만 용량이 작고 OS가
    주기적으로 정리한다.
    [v7.0 추가, 정책뉴스에서 이식] blog_only=True면 네이버 블로그 탭
    검색(ssc=tab.blog.all)으로 열어, 제목이 이미 다른 블로그에 선점된
    글이 있는지 확인하는 용도로 쓴다(기존 통합검색과는 동작 그대로 공유,
    쿼리 파라미터만 다르게 구성).
    """
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


def _to_stored_dir(abs_path: str) -> str:
    """작업폴더 경로를 config.json에 저장할 때, BASE_DIR 바로 하위 폴더면
    폴더명만 저장(회사PC↔집PC처럼 경로가 다른 PC를 오가도 안전), 그 외
    위치(다른 드라이브 등)를 직접 지정했으면 절대경로 그대로 저장한다.
    정책뉴스 프로그램의 _to_stored_dir와 동일한 방식."""
    if not abs_path:
        return WORK_FOLDER_NAME
    abs_path = os.path.abspath(abs_path)
    base_abs = os.path.abspath(BASE_DIR)
    if os.path.dirname(abs_path) == base_abs:
        return os.path.basename(abs_path)
    return abs_path


def _resolve_work_dir(stored: str) -> str:
    """config.json에 저장된 값을 실제 절대경로로 해석. 비어있으면 기본값,
    상대경로(폴더명)면 BASE_DIR과 결합, 이미 절대경로면 그대로 사용."""
    if not stored:
        return _DEFAULT_WORK_DIR
    if os.path.isabs(stored):
        return stored
    return os.path.join(BASE_DIR, stored)


def apply_work_dir_from_config():
    """config.json의 work_dir 값을 반영해 WORK_DIR 및 그 하위 경로 전역값을
    전부 재계산한다. 프로그램 시작 시 1회, 설정 탭에서 경로를 바꿔 저장할
    때마다 다시 호출한다 — 재시작 없이 즉시 반영되도록 하기 위함."""
    global WORK_DIR, DATA_DIR, SERVICES_DIR, SERVICES_DIR_LCGV
    global LIST_OUTPUT_FILE, LIST_OUTPUT_FILE_LCGV, QUOTA_STATE_FILE
    global FIRST_SEEN_FILE, POSTING_STATUS_FILE, PROMPT_DIR, FINAL_POSTS_DIR
    global FINAL_POSTS_BACKUP_DIR
    global SERVICES_DIR_HUB, LIST_OUTPUT_FILE_HUB

    cfg = load_config()
    WORK_DIR = _resolve_work_dir(cfg.get("work_dir", ""))

    DATA_DIR = os.path.join(WORK_DIR, "data")
    SERVICES_DIR = os.path.join(DATA_DIR, "services")            # 중앙부처
    SERVICES_DIR_LCGV = os.path.join(DATA_DIR, "services_lcgv")  # 지자체
    LIST_OUTPUT_FILE = os.path.join(DATA_DIR, "services_list.json")
    LIST_OUTPUT_FILE_LCGV = os.path.join(DATA_DIR, "services_list_lcgv.json")
    # [v7.20 신규] "허브(종합)" 소스 — 여러 서비스를 사람이 직접 종합해서
    # 쓰는 글을 위한 세 번째 소스. 중앙부처/지자체와 완전히 분리된 파일에
    # 저장해, bokjiro API 목록조회로 갱신되는 두 리스트를 절대 건드리지
    # 않는다(재동기화 시 덮어써져 사라질 위험이 없다).
    SERVICES_DIR_HUB = os.path.join(DATA_DIR, "services_hub")
    LIST_OUTPUT_FILE_HUB = os.path.join(DATA_DIR, "services_list_hub.json")
    QUOTA_STATE_FILE = os.path.join(DATA_DIR, "quota_state.json")
    # servId별 "최초 발견일"을 누적 기록하는 파일. 목록조회는 매번 전체를
    # 새로 받아오므로(overwrite), 여기서 별도로 최초 등장일을 추적해야
    # "오늘 신규로 추가된 서비스"를 알 수 있다. 한 번 기록된 first_seen
    # 값은 절대 덮어쓰지 않는다.
    FIRST_SEEN_FILE = os.path.join(DATA_DIR, "first_seen.json")
    # 포스팅 상태 관리 파일. 실제 네이버 포스팅은 별도 프로그램에서 하지만,
    # "이미 포스팅했는지"를 이 프로그램에서도 알고 있어야 나중에 같은
    # 자료를 중복으로 다시 작업하지 않는다. 실제 포스팅 여부는 자동으로
    # 알 수 없으므로 사람이 포스팅 후 수동으로 "📤 포스팅완료"로 표시한다.
    POSTING_STATUS_FILE = os.path.join(DATA_DIR, "posting_status.json")
    # 썸네일/각색 프롬프트 등 추후 추가될 자료도 작업폴더 바로 아래에 놓는다
    # (정책뉴스 프로그램의 PROMPT_DIR = 작업폴더와 동일한 배치).
    PROMPT_DIR = WORK_DIR
    # 최종각색 결과를 제목 기반 폴더명으로 저장하는 폴더. v2.8부터
    # "{제목}.md" 단독 파일이 아니라 "{제목}/{제목}.md" 폴더 구조로 바뀜 —
    # 인포그래픽 이미지도 같은 폴더에 같이 넣어서(정책뉴스 프로그램과 동일한
    # 관례) 나중에 "키워드 등록" 탭에서 MD+이미지를 통째로 한 번에 처리할
    # 수 있게 하기 위함.
    FINAL_POSTS_DIR = os.path.join(WORK_DIR, "final_posts")
    # 키워드 등록 처리 시 원본을 여기로 옮겨 보관한다(포스팅 폴더로는
    # 별도 복사본을 보냄 — 메인 포스팅 프로그램이 포스팅 후 포스팅
    # 폴더의 파일을 지우더라도 이 백업은 남아있어 나중에 수작업 확인·
    # 수정이 필요할 때 참고할 수 있다). 삭제는 사람이 포스팅 확인 후
    # 수동으로 한다 — 프로그램이 자동으로 지우지 않는다.
    FINAL_POSTS_BACKUP_DIR = os.path.join(WORK_DIR, "final_posts_backup")


# 모듈 최초 로딩 시 1회 적용 (이 시점엔 아직 config.json이 없을 수 있으므로
# load_config()는 기본값으로 동작 -> _DEFAULT_WORK_DIR이 그대로 쓰인다)
WORK_DIR = _DEFAULT_WORK_DIR
DATA_DIR = os.path.join(WORK_DIR, "data")
SERVICES_DIR = os.path.join(DATA_DIR, "services")
SERVICES_DIR_LCGV = os.path.join(DATA_DIR, "services_lcgv")
LIST_OUTPUT_FILE = os.path.join(DATA_DIR, "services_list.json")
LIST_OUTPUT_FILE_LCGV = os.path.join(DATA_DIR, "services_list_lcgv.json")
SERVICES_DIR_HUB = os.path.join(DATA_DIR, "services_hub")
LIST_OUTPUT_FILE_HUB = os.path.join(DATA_DIR, "services_list_hub.json")
QUOTA_STATE_FILE = os.path.join(DATA_DIR, "quota_state.json")
FIRST_SEEN_FILE = os.path.join(DATA_DIR, "first_seen.json")
POSTING_STATUS_FILE = os.path.join(DATA_DIR, "posting_status.json")
PROMPT_DIR = WORK_DIR
FINAL_POSTS_DIR = os.path.join(WORK_DIR, "final_posts")
FINAL_POSTS_BACKUP_DIR = os.path.join(WORK_DIR, "final_posts_backup")

# 메인 오토포스팅 프로그램이 최종적으로 읽어가는 공용 폴더. 정책뉴스·
# 지식인 서브프로그램과 완전히 같은 폴더명을 그대로 쓴다(전부 BASE_DIR
# 기준 상대 위치가 같아야 여러 서브프로그램이 실제로 같은 물리적 폴더를
# 공유하게 된다) — 이름을 다르게 바꾸면 메인 프로그램이 복지로 결과물을
# 못 찾는다. 절대 이 상수를 프로그램마다 다르게 고치지 않는다.
POSTING_MD_FOLDER = os.path.join(BASE_DIR, "Naver_blog_keyword_perplexity_gpt_manual_markdown_for_posting")

# 작업 디렉토리를 BASE_DIR로 고정 — 상대경로 기본값들이 실행 방식과 무관하게
# 항상 프로그램 폴더 기준으로 해석되도록 함 (정책뉴스 프로그램과 동일)
os.chdir(BASE_DIR)

# 중앙부처복지서비스
BASE_URL = "https://apis.data.go.kr/B554287/NationalWelfareInformationsV001"
LIST_PATH = "/NationalWelfarelistV001"
DETAIL_PATH = "/NationalWelfaredetailedV001"
DAILY_QUOTA_LIST = 100
DAILY_QUOTA_DETAIL = 100

# 지자체복지서비스 (Swagger 명세 2026-08-11 확인 기준)
LCGV_BASE_URL = "https://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations"
LCGV_LIST_PATH = "/LcgvWelfarelist"
LCGV_DETAIL_PATH = "/LcgvWelfaredetailed"
DAILY_QUOTA_LCGV_LIST = 1000
DAILY_QUOTA_LCGV_DETAIL = 1000

REQUEST_INTERVAL_SEC = 0.5

LIFE_CYCLE_CODES = {
    "": "(전체)", "001": "영유아", "002": "아동", "003": "청소년",
    "004": "청년", "005": "중장년", "006": "노년", "007": "임신·출산",
}
INTEREST_THEME_CODES = {
    "": "(전체)", "010": "신체건강", "020": "정신건강", "030": "생활지원",
    "040": "주거", "050": "일자리", "060": "문화·여가", "070": "안전·위기",
    "080": "임신·출산", "090": "보육", "100": "교육", "110": "입양·위탁",
    "120": "보호·돌봄", "130": "서민금융", "140": "법률", "150": "관계개선",
    "160": "에너지",
}
ERROR_CODES = {
    "0": "SUCCESS - 정상 조회",
    "04": "HTTP_ERROR",
    "10": "INVALID_REQUEST_PARAMETER_ERROR - 잘못된 요청 파라메터",
    "12": "NO_OPENAPI_SERVICE_ERROR - 서비스 없음/폐기",
    "20": "SERVICE_ACCESS_DENIED_ERROR - 서비스 접근거부",
    "22": "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR - 요청제한횟수 초과",
    "30": "SERVICE_KEY_IS_NOT_REGISTERED_ERROR - 미등록 서비스키",
    "31": "DEADLINE_HAS_EXPIRED_ERROR - 활용기간 만료",
    "99": "UNKNOWN_ERROR",
}


# 지자체는 "가구유형" 대신 "가구상황"이라는 명칭을 쓰지만 코드값 체계는 동일
HOUSEHOLD_SITUATION_CODES = {
    "": "(전체)", "010": "다문화·탈북민", "020": "다자녀", "030": "보훈대상자",
    "040": "장애인", "050": "저소득", "060": "한부모·조손",
}

# 포스팅 상태 단계. 정책뉴스 프로그램의 상태 체계(🆕신규→🟡발행준비완료→
# 📤포스팅완료)를 참고. 이 자료는 성격상 인포그래픽 형태로 포스팅하는 게
# 맞다고 판단해 "인포그래픽준비중/완료" 단계를 넣었다. "가치판단대기"는
# 가치판단 프롬프트를 돌리는 단계, "초안작성중"은 원문+첨부파일+필요시
# 웹검색 보강을 거쳐 실제 글 초안을 쓰는 단계(가치판단만으로는 내용이
# 부실한 경우가 많아 별도 단계로 분리함). "최종각색중"은 1차 초안을
# 페르소나(복지정책 블로거 톤)를 입혀 실제 발행용 글로 다듬는 2차 각색
# 단계 — 초안작성과 별도 단계로 분리한 이유는 초안은 "정확한 사실 정리"에
# 집중하고, 최종각색은 "네이버 블로그 발행 형식(SEO 구조/해시태그/톤)"에
# 집중하도록 역할을 나누기 위함.
POSTING_STATUS_LIST = [
    "🆕 신규", "🔦 사전스크리닝중", "🔎 가치판단대기", "📝 초안작성중", "✒️ 최종각색중",
    "🎨 인포그래픽준비중", "🟢 포스팅대기", "📤 포스팅완료", "🗑️ 포스팅후삭제",
    "⏭ 패스", "⏸ 보류",
]
# "작업중" 빠른 필터용 — 신규/포스팅대기/포스팅완료/포스팅후삭제/패스/보류를
# 제외한 나머지(가치판단대기~인포그래픽준비중)가 실제로 사람이 다음 액션을
# 취해야 하는 단계다. 인덱스 하드코딩 대신 이렇게 뽑아둬야 나중에 단계가
# 추가/변경돼도 안전하다.
IN_PROGRESS_STATUSES = [
    s for s in POSTING_STATUS_LIST
    if s not in ("🆕 신규", "🟢 포스팅대기", "📤 포스팅완료", "🗑️ 포스팅후삭제", "⏭ 패스", "⏸ 보류")
]
# 이 상태에 도달하면 보호 대상 — 다른 상태로 되돌리는 걸 막는다
# (실수로 발행 이력이 지워지는 것을 방지, 정책뉴스 프로그램의
# is_published 보호 로직과 동일한 취지). "🗑️ 포스팅후삭제"로의 전환만
# 예외적으로 허용되는데, 이건 set_posting_status()가 아니라 전용 함수
# mark_post_deleted_from_blog()를 통해서만 가능하다(실수로 아무 상태
# 변경이나 이걸 우회하지 못하도록 통로를 하나로 좁혀둠).
PROTECTED_STATUS = "📤 포스팅완료"
DELETED_STATUS = "🗑️ 포스팅후삭제"
# 포스팅 관리 탭 상태 필터 "패스 제외(기본)"에서 제외할 상태 모음. 기존에는
# "패스"만 제외해서 포스팅완료/포스팅대기까지 계속 섞여 나왔는데, 이 4개
# (패스/보류/포스팅완료/포스팅대기)만 빼면 나머지(🆕 신규 포함 가치판단대기~
# 인포그래픽준비중, 포스팅후삭제)는 전부 다음 액션이 필요한 항목이라 그대로
# 보여준다. 🆕 신규를 여기서 빼지 않는 게 핵심 — 예전 "작업중만" 필터는
# 신규까지 제외해버려서 신규 항목 작업을 시작할 때마다 매번 필터를
# "전체"로 바꿔야 했던 불편함이 있었다.
DEFAULT_FILTER_EXCLUDED_STATUSES = {"⏭ 패스", "⏸ 보류", PROTECTED_STATUS, "🟢 포스팅대기"}


# ============================================================
# 예외
# ============================================================
class QuotaExceededError(Exception):
    pass


class ApiResponseError(Exception):
    pass


# ============================================================
# 일일 트래픽 상태 관리
# ============================================================
QUOTA_KINDS = {
    "list": DAILY_QUOTA_LIST,
    "detail": DAILY_QUOTA_DETAIL,
    "lcgv_list": DAILY_QUOTA_LCGV_LIST,
    "lcgv_detail": DAILY_QUOTA_LCGV_DETAIL,
}


def load_quota_state():
    today = datetime.date.today().isoformat()
    default = {"date": today}
    default.update({f"{k}_count": 0 for k in QUOTA_KINDS})
    if os.path.exists(QUOTA_STATE_FILE):
        with open(QUOTA_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("date") == today:
            for k in QUOTA_KINDS:  # 예전 버전 상태파일에 없던 키 방어
                state.setdefault(f"{k}_count", 0)
            return state
    return default


def save_quota_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(QUOTA_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_and_increment(kind: str):
    state = load_quota_state()
    key = f"{kind}_count"
    limit = QUOTA_KINDS[kind]
    if state[key] >= limit:
        raise QuotaExceededError(
            f"오늘 '{kind}' 조회 일일 한도({limit}건)를 이미 사용했습니다. "
            f"내일 다시 시도하거나 data.go.kr에서 트래픽 증설을 신청하세요."
        )
    state[key] += 1
    save_quota_state(state)
    return state[key], limit


def get_quota_status():
    state = load_quota_state()
    return tuple(state[f"{k}_count"] for k in QUOTA_KINDS)


# ============================================================
# XML 파싱
# ============================================================
def xml_to_dict(elem):
    children = list(elem)
    if not children:
        return (elem.text or "").strip()
    result = {}
    for child in children:
        value = xml_to_dict(child)
        tag = child.tag
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value
    return result


def check_result_code(parsed: dict, raw_xml: str):
    result_code = parsed.get("resultCode")
    if result_code is not None and result_code != "0":
        msg = ERROR_CODES.get(result_code, "알 수 없는 에러코드")
        raise ApiResponseError(f"[resultCode={result_code}] {msg}")


# ============================================================
# 최초 발견일(first_seen) 관리 — "오늘 신규로 추가된 서비스" 판별용
# ============================================================
def load_first_seen() -> dict:
    if os.path.exists(FIRST_SEEN_FILE):
        with open(FIRST_SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def update_first_seen(items: list, source: str) -> int:
    """목록조회 결과를 first_seen.json에 반영. 이미 기록된 servId는 건드리지
    않고, 새로 나타난 servId만 오늘 날짜로 추가. 새로 추가된 건수를 반환."""
    first_seen = load_first_seen()
    today = datetime.date.today().isoformat()
    added = 0
    for item in items:
        sid = item.get("servId")
        if not sid:
            continue
        if sid not in first_seen:
            first_seen[sid] = {
                "date_first_seen": today,
                "source": source,
                "servNm": item.get("servNm", ""),
            }
            added += 1
        else:
            # 이름이 바뀌었을 수 있으니(기관측 수정) 표시용 이름만 최신화,
            # 최초발견일(date_first_seen)은 절대 덮어쓰지 않음.
            first_seen[sid]["servNm"] = item.get("servNm", first_seen[sid].get("servNm", ""))

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FIRST_SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(first_seen, f, ensure_ascii=False, indent=2)
    return added


# ============================================================
# 포스팅 상태 관리
# ============================================================
def load_posting_status() -> dict:
    if os.path.exists(POSTING_STATUS_FILE):
        with open(POSTING_STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_posting_status(status_map: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(POSTING_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_map, f, ensure_ascii=False, indent=2)


def init_posting_status_if_new(serv_id: str, serv_nm: str, source: str):
    """상세조회로 처음 자료를 받은 시점에 상태를 "🆕 신규"로 초기화한다.
    이미 상태가 있으면(재수집 등) 절대 건드리지 않는다 — 특히 포스팅완료
    표시가 재수집 한 번에 지워지면 안 되므로."""
    status_map = load_posting_status()
    if serv_id not in status_map:
        status_map[serv_id] = {
            "status": POSTING_STATUS_LIST[0],
            "source": source,
            "servNm": serv_nm,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        save_posting_status(status_map)


def set_posting_status(serv_id: str, new_status: str, serv_nm: str = "", source: str = "") -> tuple:
    """상태 변경. 포스팅완료 보호 로직 포함 — 성공하면 (True, ""),
    막히면 (False, 사유). "🗑️ 포스팅후삭제"로 바꾸는 것도 여기로는
    막힌다 — 그 전환은 반드시 mark_post_deleted_from_blog()를 통해서만
    (사용자가 명시적으로 "블로그에서 실제 삭제함"을 확인한 경우에만)
    가능하게 하기 위함."""
    status_map = load_posting_status()
    current = status_map.get(serv_id, {}).get("status", "")
    if current == PROTECTED_STATUS and new_status != PROTECTED_STATUS:
        return False, (
            "이미 '📤 포스팅완료'로 표시된 자료는 다른 상태로 되돌릴 수 없습니다.\n"
            "(외부 포스팅 프로그램과의 중복 방지 이력을 보호하기 위한 제한입니다)\n"
            "실제로 블로그에서 글을 삭제했다면, 7)포스팅 이력관리 탭의 "
            "'🗑️ 포스팅완료 삭제 처리' 버튼을 사용하세요."
        )
    # [2026-09-29 2차] 기존 항목을 복사해 갱신한다 - 게시판 값 등 덧붙인 필드 보존
    entry = dict(status_map.get(serv_id, {}))
    entry.update({
        "status": new_status,
        "source": source or status_map.get(serv_id, {}).get("source", ""),
        "servNm": serv_nm or status_map.get(serv_id, {}).get("servNm", ""),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    status_map[serv_id] = entry
    save_posting_status(status_map)
    return True, ""


def set_posting_board(serv_id: str, board_fields: dict) -> bool:
    """[2026-09-29 2차] 포스팅 상태 DB의 해당 서비스ID 항목에 게시판 값
    (board_number/board_name/board_conf/board_source)을 기록한다.
    항목이 없으면(상태 DB에 초기화된 적 없는 ID) 새로 만들지 않고 False."""
    if not serv_id or not board_fields:
        return False
    status_map = load_posting_status()
    if serv_id not in status_map:
        return False
    status_map[serv_id].update(board_fields)
    save_posting_status(status_map)
    return True


def mark_post_deleted_from_blog(serv_id: str, serv_nm: str = "", source: str = "") -> tuple:
    """실제로 네이버 블로그에서 글을 삭제한 뒤, 포스팅완료 상태를
    "🗑️ 포스팅후삭제"로 바꾸는 전용 함수. set_posting_status()의 보호
    로직을 의도적으로 우회하는 유일한 통로다 — 호출부(GUI)에서 반드시
    두 번 확인(재차 확인 팝업)을 거친 뒤에만 호출해야 한다.

    "🆕 신규"로 되돌리지 않는 이유: 신규로 돌아가면 이 프로그램이 다시
    수집 대상으로 취급해 가치판단부터 처음부터 다시 작업하라고 유도하게
    되는데, 블로그에서 내린 글을 처음부터 재작성할 필요는 없는 경우가
    많다(예: 정책 자체가 종료됐거나, 다른 이유로 내림). "🗑️ 포스팅후삭제"
    로 남겨두면 이력은 보존하면서도 리스트업/포스팅관리의 "작업중만"
    필터에는 안 걸리게(더 이상 할 일이 없는 상태로) 정리된다. 저장된
    stage_outputs.json/final_posts_index.json 등 다른 데이터는 그대로
    보존한다(사람이 나중에 다시 참고할 수 있도록)."""
    status_map = load_posting_status()
    entry = dict(status_map.get(serv_id, {}))   # [2026-09-29 2차] 덧붙인 필드 보존
    entry.update({
        "status": DELETED_STATUS,
        "source": source or status_map.get(serv_id, {}).get("source", ""),
        "servNm": serv_nm or status_map.get(serv_id, {}).get("servNm", ""),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    status_map[serv_id] = entry
    save_posting_status(status_map)
    return True, ""


def advance_posting_status(serv_id: str, target_status: str, serv_nm: str = "", source: str = "") -> bool:
    """현재 상태가 target_status보다 앞 단계일 때만 target_status로 올려준다
    (뒤로 되돌리지 않음). "가치판단 프롬프트 복사"→가치판단대기,
    "초안 프롬프트 복사"→초안작성중, "최종각색 프롬프트 복사"→최종각색중,
    "인포그래픽 프롬프트 복사"→인포그래픽준비중 처럼, 각 단계별 복사
    버튼을 누르면 그 단계로 자동 승격시키는 데 쓴다."""
    status_map = load_posting_status()
    current = status_map.get(serv_id, {}).get("status", POSTING_STATUS_LIST[0])
    try:
        cur_idx = POSTING_STATUS_LIST.index(current)
    except ValueError:
        cur_idx = 0
    target_idx = POSTING_STATUS_LIST.index(target_status)
    if cur_idx < target_idx:
        ok, _ = set_posting_status(serv_id, target_status, serv_nm, source)
        return ok
    return False


# ============================================================
# 단계별 결과(가치판단/초안/최종각색) 저장 — Claude/GPT 등 외부 LLM에서
# 실행한 결과를 사람이 복사해와 이 프로그램에 붙여넣어 저장해두면, 다음
# 단계 프롬프트를 생성할 때 자동으로 포함시켜 넘겨준다("가치판단 결과를
# 초안 프롬프트로", "초안 결과를 최종각색 프롬프트로"). 이렇게 해야 다른
# 대화창/다른 AI로 넘어가도 앞 단계에서 이미 정리된 내용을 이어받아
# 작업할 수 있다 — 매번 원문부터 처음 판단부터 다시 시키지 않아도 됨.
# ============================================================
STAGE_RESULT_LABELS = {
    "quick_judgment": "빠른 판정 결과",   # [Ver10.08] STEP 1
    "prescreening": "사전스크리닝 결과",
    "value_judgment": "가치판단 결과",
    "draft": "초안 결과",
    "final_adaptation": "최종각색 결과",
}


def get_stage_outputs_path() -> str:
    return os.path.join(DATA_DIR, "stage_outputs.json")


def load_stage_outputs() -> dict:
    path = get_stage_outputs_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_stage_outputs(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_stage_outputs_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_stage_output(serv_id: str, stage_key: str) -> str:
    return load_stage_outputs().get(serv_id, {}).get(stage_key, "")


def normalize_markdown_bullets(text: str) -> str:
    """마크다운 리스트 기호를 "*"에서 "-"로 통일한다. GPT가 리스트 항목을
    "* 항목" 형태로 쓰는 경우가 많은데, 이 파이프라인/네이버 블로그
    쪽에서는 "-" 기호를 쓰기로 정해서 저장 시 자동 변환한다.
    **볼드(굵게) 표시로 쓰인 "**텍스트**"는 절대 건드리지 않는다** —
    줄 맨 앞(들여쓰기 허용)에 "*" 하나 + 공백으로 시작하는, 즉 진짜
    리스트 기호로 쓰인 경우만 변환 대상으로 삼는다."""
    lines = text.split("\n")
    converted = []
    for line in lines:
        # 줄 시작의 공백(들여쓰기, 중첩 리스트 유지) + "*" 하나 + 공백 1개 이상
        # 뒤에 "*"가 하나 더 오면(=**볼드**) 리스트 기호가 아니므로 건드리지 않는다.
        m = re.match(r"^(\s*)\*(?!\*)(\s+)(.*)$", line)
        if m:
            indent, spaces, rest = m.groups()
            converted.append(f"{indent}-{spaces}{rest}")
        else:
            converted.append(line)
    return "\n".join(converted)


def set_stage_output(serv_id: str, stage_key: str, text: str):
    data = load_stage_outputs()
    entry = data.setdefault(serv_id, {})
    entry[stage_key] = normalize_markdown_bullets(text.strip())
    entry[f"{stage_key}_saved_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    save_stage_outputs(data)


def format_previous_stage_for_prompt(stage_key: str, serv_id: str) -> str:
    """이전 단계 결과를 다음 단계 프롬프트에 붙여넣을 섹션으로 만든다.
    아직 저장된 결과가 없으면(사람이 아직 붙여넣기 저장을 안 한 경우)
    그 사실을 그대로 안내문으로 넣는다 — 없는 걸 지어내지 않도록."""
    label = STAGE_RESULT_LABELS.get(stage_key, stage_key)
    text = get_stage_output(serv_id, stage_key)
    if not text:
        return (
            f"## 이전 단계 결과 ({label})\n\n"
            f"(아직 저장된 결과가 없습니다 — 이전 단계 프롬프트를 실행한 결과를 "
            f"'📥 {label} 저장' 버튼으로 붙여넣어 저장한 뒤 다시 이 프롬프트를 "
            f"복사하면 이 섹션에 자동으로 포함됩니다. 저장 없이 진행할 경우, 이번 "
            f"단계는 원문·첨부자료만 근거로 처음부터 다시 판단해야 합니다.)"
        )
    return f"## 이전 단계 결과 ({label})\n\n{text}"


# ============================================================
# 설정 파일 (Naver_blog_config_복지로.json) — 정책뉴스/지식인 프로그램과
# 동일한 컨벤션. 인증키를 포함해 추후 다른 설정(엑셀 경로 등)도 이 파일에
# 계속 추가될 예정이라 dict 구조로 관리한다.
# ============================================================
_DEFAULT_CONFIG = {
    "service_key": "",
    "work_dir": "",                    # 빈 문자열 = 기본값(WORK_FOLDER_NAME) 사용
    "keyword_excel_path": "",          # 빈 문자열 = 기본값(작업폴더 안) 사용
    "unified_keyword_excel_path": "",  # ✅ [2026-09-05] 통합 키워드 엑셀 경로. 빈
                                        # 문자열 = 통합 기능 미사용(dual-write 건너뜀)
    "board_config_path": "",           # ✅ [2026-09-29] 게시판 설정 엑셀 경로. 빈 문자열이면
                                        # 프로그램 폴더의 Naver_blog_게시판설정.xlsx를 찾고, 없으면
                                        # 게시판 기능 미사용(예전 카테고리 입력란 방식)
    "posting_history_excel_path": "",  # 빈 문자열 = 기본값(작업폴더 안) 사용
    # 2단계 키워드 리서치용 API 인증 (모두 선택사항 — 없으면 해당 항목만 건너뜀)
    "naver_openapi_client_id": "",      # 네이버 오픈API (블로그 검색) - developers.naver.com
    "naver_openapi_client_secret": "",
    "naver_ad_api_key": "",             # 네이버 검색광고 API - searchad.naver.com
    "naver_ad_secret_key": "",
    "naver_ad_customer_id": "",
    # 프롬프트 파일명 (정책뉴스/지식인 프로그램과 동일한 방식 — PROMPT_DIR
    # 안의 파일명만 저장. 프로그램 코드를 안 건드리고 메모장으로 프롬프트
    # 문구를 자유롭게 고칠 수 있게 하기 위함)
    "prompt_value_judgment_file": "Naver_blog_복지로_프롬프트_가치판단.md",
    "prompt_draft_file": "Naver_blog_복지로_프롬프트_초안작성.md",
    "prompt_final_adaptation_file": "Naver_blog_복지로_프롬프트_최종각색_GPT용.md",
    "prompt_infographic_file": "Naver_blog_복지로_프롬프트_인포그래픽.md",
    # v4.4에서 추가된 프롬프트. 🧩 초안+최종각색 통합은 ③~⑤(초안 작성→
    # 최종각색)를 한 번의 Claude 대화로 처리하는 프롬프트 — 결과물은
    # final_adaptation과 동일한 형식이라 저장은 기존 "⑥ 최종각색 결과
    # 저장" 버튼을 그대로 재사용한다(별도 저장 버튼 불필요).
    # v6.2: ⓪ 사전스크리닝의 Perplexity 전용 경로(prompt_prescreening_file /
    # get_prompt_prescreening_instructions() / ⓪ 프롬프트+자료 복사·프롬프트만
    # 복사 버튼)는 제거했다 — 첨부파일 분석에 제약이 많아 실사용이 불편하다는
    # 피드백. ⓪ 사전스크리닝 자체는 아래 prompt_prescreening_gemini_file
    # (Gemini 전용) 경로로 계속 쓸 수 있고, 둘 다 어려우면 "⓪+①(Claude
    # 올인원)" 경로(prompt_prescreening_value_combo_file)로 대체 가능하다.
    # "⓪ 사전스크리닝 결과 저장" 버튼은 Gemini 경로가 계속 쓰므로 그대로 둔다.
    # [Ver10.06] Gemini 경로와 그 저장 버튼도 삭제 — 통합(Claude) 경로 하나만 쓴다. 아래 키는
    # 예전 설정 호환을 위해 남겨 두지만 프로그램은 쓰지 않는다.
    # v6.1: 제미나이 전용 사전스크리닝 프롬프트 — 작업 내용(작업 A/B)은
    # 퍼플렉시티용과 동일하지만, 제미나이가 자주 보이는 습성(응답이
    # 길어지면 코드블럭을 나눠서 출력, 맞장구·자체 논평 덧붙이기, 마크다운
    # 임의 재포맷)을 억제하는 출력 규율 문구를 강화해 별도 파일로 분리.
    "prompt_prescreening_gemini_file": "Naver_blog_복지로_프롬프트_사전스크리닝_Gemini용.md",
    # v6.0: ⓪+① 통합(Claude 올인원) 프롬프트 — Perplexity로 사전스크리닝을
    # 따로 돌리기 어려울 때(PDF 파싱 실패, 첨부 개수 제한 등) 사전스크리닝
    # (원본 PDF 직접 스캔 + 경쟁 블로그 구조 분석)과 가치판단을 Claude
    # 한 번의 실행으로 처리하는 경로. 기존 ⓪→① 2단계 경로와 병렬로
    # 선택해 쓸 수 있다(어느 쪽을 쓰든 결과는 "가치판단 결과"로 동일하게
    # 저장·전달됨).
    "prompt_prescreening_value_combo_file": "Naver_blog_복지로_프롬프트_사전스크리닝_가치판단_통합_Claude용.md",
    # v4.7: 1차 초안이 이미 별도로 저장돼 있을 때(③ 초안 작성 프롬프트
    # 결과 등), 처음부터 다시 초안을 쓰지 않고 검증·각색 단계만 실행하고
    # 싶을 때 사용 — ⑤ GPT 각색 버튼 옆에 나란히 배치.
    "prompt_claude_second_stage_file": "Naver_blog_복지로_프롬프트_2차각색_Claude용.md",
    # [Ver10.08] STEP 1 빠른 판정 — 원문 + 첨부 이름만 보고 진행/보류·필요 자료·리서치 키워드를 낸다.
    "prompt_quick_judgment_file": "복지로_00_빠른판정.md",
    # [Ver10.08] 판정 읽기 뒤 경쟁 블로그 자동 스크랩 개수(0~5)와 뺄 내 블로그 아이디(콤마 구분)
    "auto_blog_count": 3,
    "my_blog_ids": "nnuiz",
    # [Ver10.06] ⑥ 최종각색 저장 전 모바일 문단 정리(GPT) — 기본 꺼짐. 키가 없으면 건너뛴다.
    "openai_api_key": "",
    "para_reflow_on": False,
    "para_reflow_limit": 150,
    # [Ver10.07] 코드 카드(선택) — 5)인포그래픽 작성 탭의 체크를 켤 때만 쓴다.
    "prompt_infographic_card_file": "복지로_7_카드설계.md",
    "card_tool_dir": "Naver_blog_SVG Card_images",
    "card_chrome_path": "",
    "card_panel_on": False,
    "card_last_shape": "",
    "kw_last_category": "",  # 6)키워드 등록 탭 카테고리 입력란 마지막 값(복지로 전용 — 다른 서브프로그램과 공유하지 않음)
}


def load_config() -> dict:
    cfg = dict(_DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg.update(saved)
        except (json.JSONDecodeError, OSError):
            pass  # 손상된 설정파일이면 기본값으로 진행 (다음 저장 시 정상화됨)

    # 예전 버전의 service_key.txt 마이그레이션 — config.json에 키가 아직
    # 없을 때만 1회 가져온다. 이후로는 config.json이 유일한 저장소.
    if not cfg.get("service_key") and os.path.exists(_LEGACY_KEY_FILE):
        with open(_LEGACY_KEY_FILE, "r", encoding="utf-8") as f:
            legacy_key = f.read().strip()
        if legacy_key:
            cfg["service_key"] = legacy_key
            save_config(cfg)
    return cfg


def save_config(cfg: dict):
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_keyword_excel_path() -> str:
    cfg = load_config()
    return cfg.get("keyword_excel_path") or os.path.join(WORK_DIR, "Naver_blog_복지로_keyword.xlsx")


def get_unified_keyword_excel_path() -> str:
    """✅ [2026-09-05] 통합 키워드 엑셀 경로. 설정 안 했으면 빈 문자열을
    반환한다(기본값 폴더로 자동 추정하지 않음 - 통합 파일은 명시적으로
    지정한 경우에만 써야 함)."""
    cfg = load_config()
    return cfg.get("unified_keyword_excel_path", "").strip()


# ✅ [2026-09-29] 게시판 설정 엑셀 조회 - 파일 수정 시각이 바뀔 때만 다시 읽는다.
_BOARD_CFG_CACHE = {"path": None, "mtime": None, "cfg": None}


def get_board_config_path() -> str:
    """설정 탭에서 지정한 경로, 없으면 프로그램 폴더의 기본 파일명(존재할 때만)."""
    if not HAS_BOARD_MODULE:
        return ""
    p = load_config().get("board_config_path", "").strip()
    if p:
        return p
    default = os.path.join(BASE_DIR, board_mod.BOARD_CONFIG_FILENAME)
    return default if os.path.exists(default) else ""


def load_board_cfg() -> dict:
    """게시판 설정을 읽어 dict로 돌려준다. 모듈/파일이 없거나 형식이 다르면
    {"ok": False, "error": ...} - 호출부는 이 경우 예전 방식으로 동작한다."""
    if not HAS_BOARD_MODULE:
        return {"ok": False, "error": "게시판 모듈 없음", "boards": []}
    path = get_board_config_path()
    if not path:
        return {"ok": False, "error": "게시판 설정 엑셀 미지정", "boards": []}
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = None
    c = _BOARD_CFG_CACHE
    if c["cfg"] is not None and c["path"] == path and c["mtime"] == mtime:
        return c["cfg"]
    cfg = board_mod.load_board_config(path)
    c.update({"path": path, "mtime": mtime, "cfg": cfg})
    return cfg


def get_posting_history_excel_path() -> str:
    cfg = load_config()
    return cfg.get("posting_history_excel_path") or os.path.join(WORK_DIR, "Naver_blog_복지로_posting_history.xlsx")


def get_research_api_keys() -> dict:
    """2단계 키워드 리서치용 API 인증정보를 한 번에 가져온다."""
    cfg = load_config()
    return {
        "naver_openapi_client_id": cfg.get("naver_openapi_client_id", ""),
        "naver_openapi_client_secret": cfg.get("naver_openapi_client_secret", ""),
        "naver_ad_api_key": cfg.get("naver_ad_api_key", ""),
        "naver_ad_secret_key": cfg.get("naver_ad_secret_key", ""),
        "naver_ad_customer_id": cfg.get("naver_ad_customer_id", ""),
    }


# ============================================================
# 프롬프트 외부 파일 관리 (정책뉴스/지식인 프로그램과 동일한 방식)
#   프롬프트 문구는 코드에 박아두지 않고 PROMPT_DIR(=작업폴더) 안의 .md
#   파일로 관리한다. 메모장으로 자유롭게 고치면 프로그램 재시작 없이
#   다음 호출부터 바로 반영된다(매번 파일을 새로 읽으므로).
# ============================================================
PROMPT_MEMO_MARKER = "[참고 메모"   # [Ver9.30] 프롬프트 파일 맨 앞 검토용 메모 블록의 표시


def strip_prompt_memo(text: str) -> str:
    """[Ver9.30 신규 — 정책뉴스 Ver10.02와 같은 함수] 프롬프트 파일 맨 앞의 검토용 참고 메모를 뺀다.
    "# 제목" 줄 → "> [참고 메모 — 실행 규칙 아님] …" 인용 블록 → "---" 줄 → 본문 순서로 된 파일에서,
    첫 "---" 줄 앞에 메모 표시가 있을 때만 그 앞부분을 "# 제목" 줄만 남기고 덜어낸다.
    메모가 없는 파일은 그대로 돌려준다."""
    m = re.search(r"^---[ \t]*$", text, re.M)
    if not m:
        return text
    head = text[:m.start()]
    if PROMPT_MEMO_MARKER not in head:
        return text
    title = next((ln for ln in head.splitlines() if ln.startswith("# ")), "")
    body = text[m.end():].lstrip("\n")
    return (title + "\n\n" + body) if title else body


def load_prompt_file(filename: str, prompt_dir: str) -> str:
    if not filename:
        return ""
    path = os.path.join(prompt_dir, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return strip_prompt_memo(f.read().strip())   # [Ver9.30] 검토용 메모는 빼고 보낸다


def get_prompt_value_judgment() -> str:
    """가치판단 프롬프트 문구를 외부 .md 파일에서 그대로 가져온다.
    프롬프트 문구는 코드에 두지 않고 전부 PROMPT_DIR 안의 파일로만
    관리한다 — 메모장으로 수정하면 프로그램 재시작 없이 바로 반영되고,
    다른 프로그램(예: 자동 발행 프로그램)에서도 같은 파일을 그대로
    가져다 쓸 수 있다."""
    return require_prompt_file("prompt_value_judgment_file", "가치판단")


def get_prompt_draft_instructions() -> str:
    """초안 작성 프롬프트. 가치판단을 통과한 자료를 실제 글 초안으로
    풀어내는 단계 — 원문만으로 빈약할 수 있어 첨부파일·웹검색 보강을
    반드시 거치도록 지시한다. (문구 실체는 외부 .md 파일)"""
    return require_prompt_file("prompt_draft_file", "초안작성")


def get_prompt_final_adaptation_instructions() -> str:
    """최종각색(2차 각색) 프롬프트 — 1차 초안에 복지정책 블로거 페르소나와
    네이버 블로그 발행 형식(SEO 구조/해시태그)을 입혀 실제 발행용 글로
    다듬는 단계. GPT로 실행하는 걸 전제로 문구를 튜닝했다(완곡한 지시보다
    명확한 MUST/금지 규칙 위주). (문구 실체는 외부 .md 파일)"""
    return require_prompt_file("prompt_final_adaptation_file", "최종각색")


def get_prompt_infographic_instructions() -> str:
    """인포그래픽 기획 프롬프트(프롬프트 C') 전체를 가져온다. 이 프롬프트는
    자체적으로 이미지 생성 프롬프트 첫 줄 고정 문구("Consistent dark navy
    editorial Korean welfare-info flat vector illustration series.")를
    포함하고 있으므로, 예전 버전과 달리 코드에서 별도 접두문구를 덧붙이지
    않는다. (문구 실체는 외부 .md 파일 — 서비스 데이터가 아니라 최종각색
    결과 전체를 입력값으로 쓰는 방식이라 서비스 데이터 자동생성 부분도
    없음)"""
    return require_prompt_file("prompt_infographic_file", "인포그래픽")


def get_prompt_prescreening_gemini_instructions() -> str:
    """⓪ 사전스크리닝 프롬프트(제미나이 전용). 작업 내용(작업 A/B)은
    Perplexity/Sonnet5용과 동일하지만, 제미나이가 자주 보이는 습성
    (응답이 길어지면 코드블럭을 나눠서 출력, 맞장구·자체 논평 덧붙이기,
    마크다운 임의 재포맷)을 억제하는 출력 규율을 강화한 별도 버전. GPT는
    이 파이프라인 용도로는 부적합하다고 판단되어(응답이 길어지면 주제
    이탈, 코드블럭 분할 출력) 별도 버전을 만들지 않았다. (문구 실체는
    외부 .md 파일)"""
    return require_prompt_file("prompt_prescreening_gemini_file", "사전스크리닝(Gemini)")


def get_prompt_prescreening_value_combo_instructions() -> str:
    """⓪+① 통합(Claude 올인원) 프롬프트. 사전스크리닝(공식 첨부 PDF
    직접 스캔 + 경쟁 블로그 구조 분석)과 가치판단을 Claude 한 번의
    실행으로 이어서 처리한다 — Perplexity가 PDF 파싱에 실패하거나
    일일 첨부파일 개수 제한에 걸릴 때, ⓪→① 2단계 경로 대신 쓰는
    병렬 경로. 결과 형식이 가치판단 결과와 동일하므로, 저장은 별도
    버튼 없이 기존 "① 가치판단 결과저장" 버튼을 그대로 쓴다. (문구
    실체는 외부 .md 파일)"""
    return require_prompt_file("prompt_prescreening_value_combo_file", "사전스크리닝+가치판단 통합(Claude)")


def get_prompt_quick_judgment_instructions() -> str:
    """[Ver10.08] STEP 1 빠른 판정 프롬프트(짧음). 통합 프롬프트(약 1,260줄)를 보내기 전에 원문과
    첨부파일 이름만으로 진행/보류를 정해, 보류될 서비스에 사용량을 쓰지 않게 한다."""
    return require_prompt_file("prompt_quick_judgment_file", "빠른 판정")


def get_prompt_claude_second_stage_instructions() -> str:
    """1차 초안을 검증·각색만 하는 프롬프트(Claude용). 1차 초안이 이미
    별도로 저장돼 있을 때(예: ③ 초안 작성 프롬프트 결과) 처음부터 다시
    초안을 쓰지 않고 이 검증·각색 단계만 바로 실행하고 싶을 때 쓴다.
    입력값은 ⑤ 최종각색(GPT)과 동일(원문+첨부+1차 초안 결과) — 출력
    형식도 동일하므로 결과 저장 역시 기존 "⑥ 최종각색 결과 저장" 버튼을
    그대로 쓴다. (문구 실체는 외부 .md 파일)"""
    return require_prompt_file("prompt_claude_second_stage_file", "2차 각색(Claude)")


class PromptFileMissingError(Exception):
    """프롬프트 .md 파일이 PROMPT_DIR에 없을 때 발생. 코드 안에 내장
    기본값이 더 이상 없으므로(요청에 따라 전부 제거), 파일이 없으면 그냥
    빈 프롬프트로 진행하지 않고 이 예외로 명확히 멈춰서 어떤 파일을
    어디에 채워 넣어야 하는지 알려준다."""
    pass


def require_prompt_file(cfg_key: str, label: str) -> str:
    """프롬프트 .md 파일을 PROMPT_DIR에서 읽어온다. 파일이 없거나 비어
    있으면 PromptFileMissingError를 발생시킨다 — 코드에 내장 기본값이
    없으므로 조용히 빈 프롬프트로 넘어가면 안 되기 때문."""
    cfg = load_config()
    filename = cfg.get(cfg_key) or _DEFAULT_CONFIG[cfg_key]
    text = load_prompt_file(filename, PROMPT_DIR)
    if not text:
        raise PromptFileMissingError(
            f"{label} 프롬프트 파일을 찾을 수 없습니다.\n\n"
            f"찾는 위치: {os.path.join(PROMPT_DIR, filename)}\n\n"
            f"프롬프트 문구는 프로그램 코드가 아니라 위 경로의 .md 파일에서만 "
            f"관리됩니다. 해당 파일을 그 경로에 채워 넣은 뒤 다시 시도하세요."
        )
    return text


def check_prompt_files_status() -> list:
    """프롬프트 파일이 PROMPT_DIR에 실제로 존재하는지 점검만 한다([Ver9.30] GPT용 최종각색은
    폐기돼 점검 대상에서 뺐다 — 파일이 없다는 시작 안내가 매번 뜨지 않게)
    (더 이상 코드 내장 기본값으로 자동 생성하지 않음 — 프롬프트는 순전히
    외부 파일로만 관리하라는 요청에 따름). 없는 파일 목록을
    [(라벨, 전체경로), ...] 형태로 돌려준다 — 시작 시 로그에 안내하는 데
    사용."""
    os.makedirs(PROMPT_DIR, exist_ok=True)
    cfg = load_config()
    checks = [
        # [Ver10.06] Gemini 사전스크리닝·별도 가치판단 경로 삭제 — 통합(Claude) 하나만 점검한다.
        ("prompt_quick_judgment_file", "빠른 판정"),
        ("prompt_prescreening_value_combo_file", "사전스크리닝+가치판단 통합(Claude)"),
        ("prompt_draft_file", "초안작성"),
        ("prompt_claude_second_stage_file", "2차 각색(Claude)"),
        ("prompt_infographic_file", "인포그래픽"),
    ]
    missing = []
    for cfg_key, label in checks:
        filename = cfg.get(cfg_key) or _DEFAULT_CONFIG[cfg_key]
        path = os.path.join(PROMPT_DIR, filename)
        if not os.path.exists(path) or not load_prompt_file(filename, PROMPT_DIR):
            missing.append((label, path))
    return missing


# config.json 로딩 함수 정의가 끝났으니, 여기서 work_dir 설정을 실제로
# 반영한다 (모듈 최초 로딩 시 1회 — 이후에는 설정 탭에서 저장할 때마다
# 다시 호출됨).
apply_work_dir_from_config()


# ============================================================
# 인증키 관리 (config.json의 "service_key" 필드에 저장)
# ============================================================
def load_service_key() -> str:
    env_key = os.environ.get("WELFARE_SERVICE_KEY")
    if env_key:
        return env_key.strip()
    return load_config().get("service_key", "")


def save_service_key(key: str):
    cfg = load_config()
    cfg["service_key"] = key.strip()
    save_config(cfg)


# ============================================================
# API 호출
# ============================================================
def fetch_list(service_key, page_no=1, num_of_rows=500, **filters):
    used, limit = check_and_increment("list")
    params = {
        "serviceKey": service_key,
        "callTp": "L",
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "srchKeyCode": "001",  # 필수 파라미터. 검색어 없어도 반드시 전송해야 함 (001:제목/002:내용/003:제목+내용)
    }
    params.update({k: v for k, v in filters.items() if v})

    resp = requests.get(BASE_URL + LIST_PATH, params=params, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    parsed = xml_to_dict(root)
    check_result_code(parsed, resp.text)
    time.sleep(REQUEST_INTERVAL_SEC)
    return parsed, used, limit


def fetch_detail(service_key, serv_id):
    used, limit = check_and_increment("detail")
    params = {"serviceKey": service_key, "callTp": "D", "servId": serv_id}

    resp = requests.get(BASE_URL + DETAIL_PATH, params=params, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    parsed = xml_to_dict(root)
    check_result_code(parsed, resp.text)
    time.sleep(REQUEST_INTERVAL_SEC)
    return parsed, used, limit


# ------------------------------------------------------------------
# 지자체복지서비스 (필드명이 중앙부처와 다름에 주의: servDgst는 동일하지만
# tgtrDtlCn -> sprtTrgtCn, applmetList -> aplyMtdCn 등 상당수 이름이 다름)
# ------------------------------------------------------------------
def fetch_lcgv_list(service_key, page_no=1, num_of_rows=500, **filters):
    used, limit = check_and_increment("lcgv_list")
    params = {
        "serviceKey": service_key,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "srchKeyCode": "001",  # 중앙부처와 동일하게 기본값을 넣어 필수 파라미터 누락을 방지
    }
    params.update({k: v for k, v in filters.items() if v})

    resp = requests.get(LCGV_BASE_URL + LCGV_LIST_PATH, params=params, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    parsed = xml_to_dict(root)
    check_result_code(parsed, resp.text)
    time.sleep(REQUEST_INTERVAL_SEC)
    return parsed, used, limit


def fetch_lcgv_detail(service_key, serv_id):
    used, limit = check_and_increment("lcgv_detail")
    params = {"serviceKey": service_key, "servId": serv_id}  # callTp 없음 (URL 경로로 구분)

    resp = requests.get(LCGV_BASE_URL + LCGV_DETAIL_PATH, params=params, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    parsed = xml_to_dict(root)
    check_result_code(parsed, resp.text)
    time.sleep(REQUEST_INTERVAL_SEC)
    return parsed, used, limit


def _fetch_with_retry(fetch_fn, log_fn, max_retries=2, retry_wait_sec=3, **kwargs):
    """네트워크 타임아웃/연결오류처럼 '일시적인' 문제로 보이는 경우에만
    자동으로 재시도한다. QuotaExceededError(일일 한도 초과)나
    ApiResponseError(API가 명확한 오류 응답을 준 경우)는 재시도해도
    똑같이 실패할 뿐이므로 그대로 올려보내 호출부의 기존 처리(한도초과
    시 조용히 중단, 그 외 오류 시 기존 데이터 보존)가 그대로 동작하게
    한다. requests.exceptions.RequestException(타임아웃, 연결 끊김 등
    네트워크 레벨 오류)만 재시도 대상.

    fetch_list()/fetch_lcgv_list()처럼 페이지 하나 실패로 전체 수집이
    중단되던 지점(사용자 리포트: 'Read timed out' 간헐 발생, 2026-08-25)
    에 적용해, 일시적 지연 정도는 사람이 매번 다시 누르지 않아도 자동
    으로 넘어가게 한다. (v6.6)"""
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            return fetch_fn(**kwargs)
        except requests.exceptions.RequestException as e:
            last_err = e
            if attempt < max_retries:
                log_fn(f"  ⏳ 일시적 네트워크 오류({type(e).__name__}) — {retry_wait_sec}초 후 "
                       f"자동 재시도 ({attempt + 1}/{max_retries})...")
                time.sleep(retry_wait_sec)
    raise last_err


# ============================================================
# 수집 로직 (백그라운드 스레드에서 실행, log_fn으로 GUI에 로그 전달)
# ============================================================
def collect_list_all(service_key, log_fn, stop_event, life_code="", theme_code="", search_wrd=""):
    os.makedirs(DATA_DIR, exist_ok=True)
    all_items = []
    page_no = 1
    total_count = None
    had_error = False

    while not stop_event.is_set():
        try:
            result, used, limit = _fetch_with_retry(
                fetch_list, log_fn,
                service_key=service_key, page_no=page_no, num_of_rows=500,
                lifeArray=life_code, intrsThemaArray=theme_code, searchWrd=search_wrd,
            )
        except QuotaExceededError as e:
            log_fn(f"⚠ {e}")
            break
        except Exception as e:
            log_fn(f"✗ 목록조회 실패: {e}")
            had_error = True
            break

        if total_count is None:
            total_count = int(result.get("totalCount", 0))
            log_fn(f"전체 서비스 수: {total_count}건 (일일 목록조회 {used}/{limit})")

        items = result.get("servList", [])
        if isinstance(items, dict):
            items = [items]
        all_items.extend(items)
        log_fn(f"  page {page_no}: {len(items)}건 수집 (누적 {len(all_items)}/{total_count})")

        if len(all_items) >= total_count or not items:
            break
        page_no += 1

    if had_error:
        # 네트워크 오류(타임아웃 등)로 중간에 끊긴 경우, 지금까지 이 실행에서
        # 모은 all_items(비어있거나 일부만 있음)로 기존 파일을 덮어쓰지 않는다.
        # 예전에는 여기서 무조건 저장해버려서, 타임아웃 한 번에 그동안 쌓아둔
        # 목록 전체가 0건/일부만 남은 파일로 통째로 사라지는 사고가 있었음
        # (2026-08-14 사용자 리포트).
        existing_count = 0
        if os.path.exists(LIST_OUTPUT_FILE):
            try:
                with open(LIST_OUTPUT_FILE, "r", encoding="utf-8") as f:
                    existing_count = len(json.load(f))
            except (OSError, json.JSONDecodeError):
                pass
        log_fn(f"⚠ 목록조회가 도중에 실패해 저장을 건너뛰고 기존 데이터({existing_count}건)를 "
               f"그대로 유지합니다. 네트워크 상태를 확인한 뒤 다시 시도해주세요.")
        return existing_count

    with open(LIST_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    newly_added = update_first_seen(all_items, "central")
    log_fn(f"✓ 목록 저장 완료: {len(all_items)}건 -> {LIST_OUTPUT_FILE} (오늘 신규 발견 {newly_added}건)")
    return len(all_items)


def sanitize_folder_name(name: str, max_len: int = 60) -> str:
    """서비스명을 폴더명으로 쓸 수 있게 정리 (Windows 금지문자 제거 + 길이 제한)"""
    name = (name or "").strip()
    name = re.sub(r'[\\/:*?"<>|]', "", name)   # Windows 폴더명 금지문자 제거
    name = re.sub(r"\s+", " ", name).strip()    # 연속 공백 정리
    name = name.rstrip(" .")                    # 끝의 점/공백 제거 (Windows 규칙)
    if len(name) > max_len:
        name = name[:max_len].rstrip()
    return name or "이름없음"


def service_folder_path(serv_id: str, serv_nm: str) -> str:
    """서비스별 폴더 경로: data/services/{서비스명}_{servId}/"""
    folder_name = f"{sanitize_folder_name(serv_nm)}_{serv_id}"
    return os.path.join(SERVICES_DIR, folder_name)


def hub_folder_path(serv_id: str, serv_nm: str) -> str:
    """[v7.20 신규] 허브(종합) 서비스별 폴더 경로: data/services_hub/
    {서비스명}_{servId}/. service_folder_path와 같은 규칙이지만 완전히
    분리된 디렉터리를 쓴다."""
    folder_name = f"{sanitize_folder_name(serv_nm)}_{serv_id}"
    return os.path.join(SERVICES_DIR_HUB, folder_name)


def create_hub_service(serv_nm: str, raw_text: str) -> str:
    """[v7.20 신규] 여러 서비스를 사람이 직접 종합해서 쓰는 "허브(종합)"
    항목을 새로 만든다. bokjiro API 목록(services_list.json/
    services_list_lcgv.json)은 절대 건드리지 않고, 완전히 별도인
    services_list_hub.json + services_hub/ 폴더에만 기록한다.

    detail.json은 중앙부처/지자체처럼 bokjiro API 필드(tgtrDtlCn,
    slctCritCn 등)를 흉내 내지 않는다 — 여러 서비스를 사람이 이미
    자기 판단으로 종합한 글이라 항목별로 도로 쪼갤 이유가 없으므로,
    {"servNm": ..., "raw_text": ...} 형태로 원문 전체를 한 필드에
    그대로 담는다. build_value_judgment_package()/
    build_prescreening_value_combo_package()가 source == "허브"일 때
    이 raw_text를 그대로 "## 서비스 원문"에 싣도록 분기돼 있다.

    반환값: 새로 만든 servId."""
    os.makedirs(DATA_DIR, exist_ok=True)
    serv_id = f"HUB{int(time.time() * 1000)}"

    items = []
    if os.path.exists(LIST_OUTPUT_FILE_HUB):
        with open(LIST_OUTPUT_FILE_HUB, "r", encoding="utf-8") as f:
            items = json.load(f)
    items.append({"servId": serv_id, "servNm": serv_nm})
    with open(LIST_OUTPUT_FILE_HUB, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    folder = hub_folder_path(serv_id, serv_nm)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "detail.json"), "w", encoding="utf-8") as f:
        json.dump({"servNm": serv_nm, "raw_text": raw_text}, f, ensure_ascii=False, indent=2)

    update_first_seen([{"servId": serv_id, "servNm": serv_nm}], "hub")
    invalidate_score_cache()
    return serv_id


# [v7.2 신규] 제목 점검 — 정책뉴스 서브프로그램의 validate_title()/
# TITLE_MIN_LEN/TITLE_MAX_LEN/HOOK_WORDS를 그대로 이식(복지로 코드에는
# 지금까지 이 기능이 아예 없었음). 복지로는 서비스 1건 = 소재 1개라
# 정책뉴스의 "복합 소재형 75자 예외"에 해당하는 개념이 없으므로 60자를
# 예외 없는 절대 상한으로만 둔다.
TITLE_MIN_LEN = 40   # [Ver10.06] 통합 V9(앞부분에 속마음 후킹) — 35→40
TITLE_MAX_LEN = 60
HOOK_WORDS = ["주목", "눈길", "관심", "충격", "화제", "이슈", "꿀팁", "대박"]


def validate_title(title: str) -> dict:
    """[Ver9.30 갱신] 가치판단 V8 [제목 형식 규칙] 기준 제목 점검(정책뉴스 Ver10.02와 같은 기준).
    제목 = "[메인 + 서브 + 핵심 포인트], [롱테일 + 세부사항]" — 35~60자(60자 절대 상한), 쉼표
    1개, 앞부분 30자 이내, 핵심 숫자 1개. 물음표 종결은 이제 선택이라 경고하지 않는다.
    반환: {length, ok_length, hook_words, num_count, warnings}
    완벽한 분석은 아니고 명백한 실수만 잡는 가벼운 점검이다."""
    title = (title or "").strip()
    length = len(title)
    warnings = []

    ok_length = TITLE_MIN_LEN <= length <= TITLE_MAX_LEN
    if length > TITLE_MAX_LEN:
        warnings.append(
            f"제목이 {length}자로 60자 절대 상한을 넘었습니다 — "
            f"반드시 줄이세요.")
    elif length and length < TITLE_MIN_LEN:
        warnings.append(
            f"제목이 {length}자로 {TITLE_MIN_LEN}자 미만입니다 — 앞부분(메인·서브)이나 뒷부분(롱테일)이 "
            f"빠졌는지 확인하세요.")

    commas = len(_TITLE_COMMA_RE.findall(title))   # 숫자 속 천 단위 쉼표는 세지 않는다
    # [Ver10.06] 통합 V9 속마음 후킹: 앞부분 메인 바로 뒤 작은따옴표 한 쌍, 앞 25자 안에서 끝남.
    hook, hook_end = tchk_title_hook(title)
    if title and not hook:
        warnings.append("앞부분(첫 쉼표 앞)에 작은따옴표 속마음 후킹이 없습니다 — 통합 V9 제목은 "
                        "[메인 + '속마음 후킹'], [롱테일] 구조입니다(피드에서 멈추게 하는 자리).")
    elif hook and hook_end > TITLE_HOOK_VISIBLE_LEN:
        warnings.append(f"속마음 후킹이 {hook_end}자에서 끝납니다 — 피드 카드에는 앞 약 "
                        f"{TITLE_HOOK_VISIBLE_LEN}자만 보이므로 메인과 후킹을 앞으로 당기세요.")
    if title and commas == 0:
        warnings.append("쉼표가 없습니다 — 제목은 '앞부분, 뒷부분' 쉼표 1개 구조입니다 "
                        "(앞구 검색은 앞 30자로 대체됩니다).")
    elif commas >= 2:
        warnings.append(f"쉼표가 {commas}개입니다 — 첫 쉼표 앞만 앞구, 뒤 전체가 뒷구로 "
                        f"검색됩니다(쉼표 1개 권장).")
    if commas >= 1:
        # [Ver10.06] 앞부분 길이는 속마음 후킹을 포함한 그대로 센다(검색용 앞구와 다름).
        _front_len = _TITLE_COMMA_RE.search(title).start()
        if _front_len > 30:
            warnings.append(f"앞부분(첫 쉼표 앞)이 {_front_len}자입니다 — 30자 이내를 권장합니다.")
    if re.search(r"\d[,，]\d", title):
        warnings.append("숫자에 천 단위 쉼표가 있습니다 — 제목에서는 '1200만 원'처럼 쉼표 없이 쓰세요.")

    number_groups = re.findall(r'\d+(?:[.,]\d+)?', title)
    num_count = len(number_groups)
    if num_count >= 2:
        warnings.append(
            f"숫자가 {num_count}개({', '.join(number_groups)}) 들어있습니다 — "
            f"핵심 숫자는 원칙적으로 1개만 남기세요(나이·기간 범위처럼 "
            f"하나의 조건을 이루는 숫자 2개라면 예외로 볼 수 있으니 직접 확인하세요).")

    found_hooks = [w for w in HOOK_WORDS if w in title]
    if found_hooks:
        warnings.append(f"호객형 수식어 발견: {', '.join(found_hooks)} — "
                         f"검색 가중치가 높은 자리를 낭비할 수 있습니다.")

    if "?" in title.rstrip("?").rstrip():
        warnings.append("물음표가 제목 중간에 있습니다 — 물음표는 맨 끝 의문형 어미에만 붙이세요.")

    return {
        "length":     length,
        "ok_length":  ok_length,
        "hook_words": found_hooks,
        "num_count":  num_count,
        "warnings":   warnings,
    }


def extract_title_from_final_text(text: str) -> str:
    """최종각색 결과(마크다운)에서 제목을 추출한다. 최종각색 프롬프트의
    출력 형식상 문서 맨 앞이 "# 제목" 형태의 헤딩으로 시작하므로, 첫 번째
    마크다운 헤딩(#, ##, ### 등) 줄을 찾아 그 텍스트만 돌려준다. 헤딩이
    없으면(형식을 안 지켰거나 사람이 손으로 고친 경우) 첫 번째 비어있지
    않은 줄을 대신 쓴다."""
    for line in text.split("\n"):
        stripped = line.strip()
        m = re.match(r"^#{1,3}\s+(.+)$", stripped)
        if m:
            return m.group(1).strip()
    for line in text.split("\n"):
        if line.strip():
            return line.strip()
    return ""


def sanitize_md_filename(title: str, max_len: int = 80) -> str:
    """추출한 제목을 .md 파일명으로 쓸 수 있게 정리한다
    (sanitize_folder_name과 동일한 규칙 + 확장자 없이 순수 제목만)."""
    return sanitize_folder_name(title, max_len=max_len)


def get_final_post_folder(title: str) -> str:
    """이 제목의 최종원고 패키지(MD+인포그래픽 이미지)가 들어가는 폴더
    경로. final_posts/{제목}/ — 제목이 곧 폴더명이며 그 외 아무것도
    붙이지 않는다(요청사항)."""
    return os.path.join(FINAL_POSTS_DIR, sanitize_md_filename(title))


def get_final_posts_index_path() -> str:
    return os.path.join(DATA_DIR, "final_posts_index.json")


def load_final_posts_index() -> dict:
    """제목(폴더명) -> servId 매핑. final_posts/{제목}/ 폴더 자체에는
    servId를 안 붙이기로 했으므로(폴더명 = 순수 제목), 어느 servId가 그
    제목을 썼는지는 이 인덱스로 따로 추적해서 "다른 서비스가 같은 제목을
    덮어쓰려는" 상황을 감지하거나, 등록 시 제목 → servId 역참조가
    필요할 때(키워드 등록 탭) 쓴다."""
    path = get_final_posts_index_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_final_posts_index(index: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_final_posts_index_path(), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def check_final_post_title_conflict(serv_id: str, text: str, serv_nm: str = "") -> tuple:
    """이 최종각색 결과를 저장하면 폴더명(제목)이 될 값을 미리 계산해서,
    이미 "다른" servId가 같은 제목으로 저장해둔 게 있는지 확인한다.
    돌려주는 값: (title, folder_name, conflicting_serv_id 또는 None).
    같은 servId가 이전에 쓴 제목이면 충돌로 치지 않는다(재저장은 항상
    허용) — 오직 서로 다른 두 서비스가 같은 제목을 쓰려는 경우만 잡는다."""
    title = extract_title_from_final_text(text) or serv_nm or "제목없음"
    folder_name = sanitize_md_filename(title)
    index = load_final_posts_index()
    existing_serv_id = index.get(folder_name)
    conflict = existing_serv_id if (existing_serv_id and existing_serv_id != serv_id) else None
    return title, folder_name, conflict


# [Ver10.06 신규] 저장 전 모바일 문단 정리 — 지식인 관리 프로그램 Ver10.05(kin_manager.py)와 같은 코드.
# ══════════════════════════════════════════════════════════
# 저장 전 모바일 문단 정리 (복지로: ⑥ 최종각색 결과 저장 창, 기본 꺼짐)
# ──────────────────────────────────────────────────────────
# 각색 결과는 이미 빈 줄로 문단이 나뉘어 있으므로(대부분 1~3문장, 중간값 약
# 100자) 기존 문단 구분은 그대로 두고, 기준 글자 수(기본 150자, 저장 창에서 조정)를
# 넘는 문단만 나눈다. 문단을 합치지는 않는다. 넘는 문단이 없으면 GPT를 부르지
# 않는다. 나누는 자리는 한 문단에 한 곳, "첫 문장 뒤(앞)" 또는 "마지막 문장 앞(뒤)"
# 둘 중 하나이고, GPT가 문단을 읽고 앞/뒤/없음(문맥이 어색하면 그대로) 중 하나만
# JSON으로 답한다. 코드가 원래 문장 그대로 다시 이어 붙이며 나눈 자리에만 빈 줄
# (포스팅 프로그램의 문단 구분)을 넣는다. 마지막에 공백·줄바꿈을 모두 뺀 전후
# 본문을 대조해 한 글자라도 다르면 원본을 그대로 쓴다.
# 제목·소제목·해시태그(#), 표(|), 리스트(- * + 1.), 인용(>), 이미지,
# 코드펜스, 구분선, 굵은 글씨만 있는 줄, [[강조]] 줄은 건드리지 않는다.
# ══════════════════════════════════════════════════════════
PARA_REFLOW_MODEL = "gpt-4.1-mini-2025-04-14"
PARA_REFLOW_DEFAULT_LIMIT = 150

_PARA_LOCK_PAT = re.compile(
    r'^\s*(?:#|\||>|!\[|[-*+]\s|\d+[.)]\s|`{3,}|-{3,}\s*$|\*\*[^*].*\*\*\s*$|\[\[)')
# 문장 끝: . ! ? … 뒤에 닫는 따옴표·괄호가 붙을 수 있고, 그 뒤가 공백이어야 한다
# ("1.5", "2026.10.5" 같은 숫자 안의 점은 뒤에 공백이 없어 나뉘지 않는다).
_PARA_SENT_END_PAT = re.compile(r'[.!?…][)"\'”’」』\]]*(?=\s)')

PARA_REFLOW_RULES = (
    "당신은 네이버 블로그 글의 긴 문단을 모바일에서 읽기 좋게 나누는 편집자입니다.\n"
    "아래 [문단]은 기준 길이({limit}자)를 넘어 둘로 나누려는 문단이며, 문장에 번호가 붙어 있습니다.\n"
    "문단 전체를 읽고 문단마다 아래 셋 중 하나를 고르세요.\n"
    "- 앞: 첫 문장 뒤에서 나눔 (1번 | 2번~끝)\n"
    "- 뒤: 마지막 문장 앞에서 나눔 (1번~끝 앞 | 마지막 문장)\n"
    "- 없음: 나누지 않음\n\n"
    "떼어 낸 문장과 남은 문장이 각각 앞뒤 없이도 뜻이 자연스럽게 통하고 흐름이 끊기지 않는 쪽을\n"
    "고릅니다. 앞뒤 문장과 이어져야 뜻이 통해서 어느 쪽으로 나눠도 어색하면 \"없음\"을 고릅니다.\n"
    "문장은 고치지 않습니다. 문장이 2개인 문단은 앞과 뒤가 같습니다.\n\n"
    "[출력]\n"
    '아래 JSON만 출력합니다: {{"paragraphs": {{"3": "앞", "7": "뒤", "9": "없음"}}}} (키는 [문단] 번호)'
)


def para_split_sentences(line):
    """한 줄을 문장 단위로 나눈다(앞뒤 공백만 떼므로 이어 붙이면 원문과 글자가 같다)."""
    out, start = [], 0
    for m in _PARA_SENT_END_PAT.finditer(line):
        out.append(line[start:m.end()].strip())
        start = m.end()
    rest = line[start:].strip()
    if rest:
        out.append(rest)
    return [s for s in out if s]


def para_find_paragraphs(md_text):
    """빈 줄·잠금 줄로 구분되는 일반 문단을 찾는다.
    반환 (lines, paras) - paras는 [(시작줄, 끝줄, [문장, ...], 글자수), ...](끝줄 포함).
    글자수는 문장을 공백 하나로 이어 붙인 길이(공백 포함)."""
    lines = md_text.split('\n')
    paras, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        if not ln.strip() or _PARA_LOCK_PAT.match(ln):
            i += 1
            continue
        j = i
        while j + 1 < n and lines[j + 1].strip() and not _PARA_LOCK_PAT.match(lines[j + 1]):
            j += 1
        sents = []
        for x in lines[i:j + 1]:
            sents.extend(para_split_sentences(x))
        paras.append((i, j, sents, len(" ".join(sents))))
        i = j + 1
    return lines, paras


def para_long_targets(md_text, limit):
    """나눌 문단만 [(문단순번, 문장들, 글자수)]로 돌려준다. 대상: 기준 글자 수를 넘고
    문장이 2개 이상인 문단. 아래는 대상에서 뺀다(그대로 둔다).
    - 여러 줄로 된 문단(한 줄 바꿈으로 이어진 블록 - B·Claude 도입부의 시적 줄바꿈 등):
      줄바꿈 자체가 형식이라 건드리지 않는다.
    - [[강조]]·[[주의]]가 문단 안에 섞인 문단: 프롬프트상 태그는 독립 문단이라 정상
      글에는 없고, 섞여 있으면 어디서 나눠도 태그나 문장이 잘릴 수 있다.
    - 해시태그 줄 바로 앞 문단: 면책 문장("해시태그 앞 별도 한 줄").
    - 도입부(첫 ## 소제목 앞 문단)."""
    lines, paras = para_find_paragraphs(md_text)
    # 도입부(첫 "## " 소제목 앞)는 나누지 않는다.
    first_h2 = next((i for i, x in enumerate(lines) if re.match(r'\s*##\s', x)), len(lines))
    last_prose = None
    for k, (s, e, _, _) in enumerate(paras):
        nxt = next((x for x in lines[e + 1:] if x.strip()), "")
        if nxt.lstrip().startswith('#') and not re.match(r'\s*#{1,6}\s', nxt):
            last_prose = k
    out = []
    for k, (s, e, sents, total) in enumerate(paras):
        if s < first_h2 or total <= limit or len(sents) < 2 or e > s or k == last_prose:
            continue
        if '[[' in lines[s]:
            continue
        out.append((k + 1, sents, total))
    return out


def para_valid_groups(groups, n):
    """GPT가 준 묶음이 1..n을 순서대로 한 번씩만 덮는지 확인."""
    if not isinstance(groups, list) or not groups:
        return False
    flat = []
    for g in groups:
        if not isinstance(g, list) or not g:
            return False
        flat.extend(g)
    return flat == list(range(1, n + 1))


def para_apply_splits(md_text, splits):
    """splits({문단순번: [[1,2],[3]]})대로 해당 문단만 나눈다. 나머지 문단·줄은 그대로.
    묶음이 잘못됐거나 하나로 둔 문단은 손대지 않는다. 반환 (새 본문, 나눈 문단 수, 잘못된 응답 수)."""
    lines, paras = para_find_paragraphs(md_text)
    changed = invalid = 0
    for idx in range(len(paras), 0, -1):
        if idx not in splits:
            continue
        s, e, sents, _ = paras[idx - 1]
        groups = splits[idx]
        if groups is None or not para_valid_groups(groups, len(sents)):
            invalid += 1
            continue
        if len(groups) < 2:
            continue
        new_lines = []
        for g_i, g in enumerate(groups):
            if g_i:
                new_lines.append("")
            new_lines.append(" ".join(sents[k - 1] for k in g))
        lines[s:e + 1] = new_lines
        changed += 1
    return "\n".join(lines), changed, invalid


def para_same_text(a, b):
    """공백·줄바꿈을 모두 뺀 글자가 같은지(문단 정리 안전장치)."""
    return re.sub(r'\s', '', a) == re.sub(r'\s', '', b)


def para_reflow_with_gpt(openai_client, md_text, limit=PARA_REFLOW_DEFAULT_LIMIT, model=PARA_REFLOW_MODEL):
    """기준 글자 수를 넘는 문단만 GPT에게 나눌 자리를 받아 나눈다.
    반환 (새 본문 또는 None, 안내 문구). None이면 원본을 그대로 쓴다."""
    targets = para_long_targets(md_text, limit)
    if not targets:
        return None, f"{limit}자 넘는 문단 없음 - GPT 호출 안 함(원본 유지)"
    parts = []
    for pid, sents, total in targets:
        parts.append(f"[문단 {pid}] (전체 {total}자)")
        parts.extend(f"{k}. ({len(x)}자) {x}" for k, x in enumerate(sents, 1))
        parts.append("")
    resp = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user",
                   "content": PARA_REFLOW_RULES.format(limit=limit) + "\n\n" + "\n".join(parts)}],
        temperature=0,
        max_tokens=300,
        response_format={"type": "json_object"},
    )
    raw = (resp.choices[0].message.content or "").strip()
    try:
        data = json.loads(raw)
    except Exception:
        m = re.search(r'\{.*\}', raw, re.S)
        data = json.loads(m.group(0)) if m else {}
    # "앞" = 첫 문장 뒤, "뒤" = 마지막 문장 앞, "없음" = 그대로. 그 밖의 답은 잘못된 응답.
    counts = {pid: len(sents) for pid, sents, _ in targets}
    splits = {}
    for k, v in (data.get("paragraphs") or {}).items():
        try:
            k = int(k)
        except (TypeError, ValueError):
            continue
        if k not in counts:
            continue
        n = counts[k]
        v = str(v).strip()
        if v == "앞":
            splits[k] = [[1], list(range(2, n + 1))]
        elif v == "뒤":
            splits[k] = [list(range(1, n)), [n]]
        elif v == "없음":
            splits[k] = [list(range(1, n + 1))]
        else:
            splits[k] = None  # para_apply_splits에서 잘못된 응답으로 센다
    new_text, changed, invalid = para_apply_splits(md_text, splits)
    if not para_same_text(md_text, new_text):
        return None, "대조 실패 - 원본 유지"
    note = f"{limit}자 넘는 문단 {len(targets)}개 중 {changed}개 나눔"
    if invalid:
        note += f"(잘못된 응답 {invalid}개는 그대로)"
    if new_text == md_text:
        return None, note + " - 바뀐 것 없음(원본 유지)"
    return new_text, note


def save_final_adaptation_markdown(serv_id: str, serv_nm: str, text: str) -> str:
    """최종각색 결과를 "final_posts/{제목}/{제목}.md"로 저장하고 그 경로를
    돌려준다. 파일 하나가 아니라 제목별 폴더로 만드는 이유: 이 폴더 안에
    인포그래픽 이미지(5)인포그래픽 작성 탭에서 만든 것)도 같이 넣어서,
    나중에 "📤 키워드 등록" 탭이 MD+이미지를 통째로 한 번에 옮길 수 있게
    하기 위함(정책뉴스 프로그램의 제목별 폴더 관례와 동일). 폴더명 = 제목
    그대로(그 외 아무것도 붙이지 않음). 같은 제목으로 다시 저장하면 같은
    폴더의 .md만 덮어쓴다(같은 servId의 재저장은 항상 허용 — 충돌 여부는
    호출부에서 check_final_post_title_conflict()로 먼저 확인하고 사용자에게
    물어본 뒤에 이 함수를 호출해야 한다)."""
    title = extract_title_from_final_text(text) or serv_nm or "제목없음"
    folder = get_final_post_folder(title)
    os.makedirs(folder, exist_ok=True)
    folder_name = os.path.basename(folder)
    path = os.path.join(folder, f"{folder_name}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    index = load_final_posts_index()
    index[folder_name] = serv_id
    save_final_posts_index(index)
    return path


def get_final_adaptation_text_for_use(serv_id: str, serv_nm: str = "") -> str:
    """최종각색 결과 "실제 사용할" 텍스트를 돌려준다. final_posts/{제목}/
    {제목}.md 파일이 이미 저장되어 있으면 그 파일 내용을 최우선으로
    읽어온다 — 사용자가 "📂 자료폴더 열기"로 폴더를 열어 메모장 등으로
    MD 파일을 직접 고친 경우, 그 수정 내용이 항상 최신이기 때문이다.
    (이전 버전 문제: 5)인포그래픽 작성 탭의 "제목 목록 새로고침"·
    "📂 자료폴더 열기"가 stage_outputs.json에 저장된 텍스트만 읽어서,
    MD 파일을 직접 고쳐도 목록/프롬프트가 계속 옛날 내용으로 나왔음.)
    .md 파일이 아직 없으면(최종각색 결과를 아직 저장 전) stage_outputs.
    json에 저장된 텍스트로 폴백한다."""
    stage_text = get_stage_output(serv_id, "final_adaptation")
    title = extract_title_from_final_text(stage_text) or serv_nm or ""
    if title:
        folder = get_final_post_folder(title)
        folder_name = os.path.basename(folder)
        md_path = os.path.join(folder, f"{folder_name}.md")
        if os.path.exists(md_path):
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    file_text = f.read()
                if file_text.strip():
                    return file_text
            except OSError:
                pass
    return stage_text


def _fix_mojibake_filename(name: str) -> str:
    """Content-Disposition 헤더는 HTTP 규격상 Latin-1로 파싱된다. 서버가
    파일명을 퍼센트 인코딩 없이 UTF-8 바이트 그대로 헤더에 실어 보내면,
    requests/urllib3가 이를 Latin-1로 잘못 디코딩해 깨진 문자열이 된다
    (예: '사회보장급여' -> 'ì¬íë³´ì¥ê¸ì¬'). Latin-1로 재인코딩해 원래
    UTF-8 바이트를 복원한 뒤 다시 UTF-8로 디코딩하면 복구된다. 애초에
    깨지지 않은 정상 파일명(순수 ASCII 등)은 이 왕복을 거쳐도 그대로
    유지되므로 항상 시도해도 안전하다.

    [완화 복구] 응답 헤더 전달 과정에서 일부 바이트가 유실되면(관측된
    사례: 특정 제어문자 범위가 중간에 빠짐) 엄격 복구(errors="strict")가
    실패한다. 이 경우 완전히 포기하지 않고 errors="replace"로 다시 시도해,
    한글이 하나라도 살아나면(대부분의 문자는 정상 복구되고 유실된 자리만
    □로 대체) 그쪽을 채택한다 — 완전히 깨진 것보다 부분 복구가 훨씬
    쓸모 있기 때문."""
    try:
        return name.encode("latin-1").decode("utf-8")
    except UnicodeEncodeError:
        return name  # 애초에 Latin-1 범위를 벗어난 문자 포함 -> 이미 정상 텍스트로 간주
    except UnicodeDecodeError:
        pass

    try:
        lenient = name.encode("latin-1").decode("utf-8", errors="replace")
        if any("\uac00" <= c <= "\ud7a3" for c in lenient):
            return lenient
    except UnicodeEncodeError:
        pass
    return name


def _guess_extension(resp, url: str, cd_filename: str) -> str:
    """확장자만 뽑아낸다. 확장자는 항상 ASCII(.pdf, .hwp 등)라 Content-Disposition
    헤더의 한글 인코딩 문제와 무관하게 안전하다 — 그래서 이름 전체가 아니라
    확장자만 헤더에서 신뢰해서 쓴다."""
    if cd_filename and "." in cd_filename:
        ext = os.path.splitext(cd_filename)[1]
        if 1 < len(ext) <= 6 and ext[1:].isalnum():
            return ext

    content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
    ext = mimetypes.guess_extension(content_type) if content_type else None
    if ext:
        return ext

    path = urlparse(url).path
    if "." in path:
        ext = os.path.splitext(path)[1]
        if 1 < len(ext) <= 6:
            return ext

    return ".pdf"  # 그래도 못 찾으면 가장 흔한 서식자료 확장자로 대체


def download_attachment(url: str, save_dir: str, display_name: str = "", log_fn=None) -> str:
    """서식/자료 URL을 다운로드해서 save_dir에 저장하고 저장된 경로를 반환.

    파일명은 가능하면 display_name(= API 응답의 "서식/자료명" 필드,
    예: servSeDetailNm/wlfareInfoReldNm)을 우선 사용한다. 이 값은 API의
    JSON/XML 응답 본문에서 온 것이라 처음부터 정상 UTF-8이고, 다운로드
    응답의 Content-Disposition 헤더(HTTP 규격상 Latin-1로 파싱되어 한글이
    깨지기 쉬운 소스)를 거치지 않는다. Content-Disposition은 확장자를
    뽑는 데만 보조적으로 쓴다."""
    os.makedirs(save_dir, exist_ok=True)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    cd_filename = None
    cd = resp.headers.get("Content-Disposition", "")
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd)
    if match:
        cd_filename = requests.utils.unquote(match.group(1))
        cd_filename = _fix_mojibake_filename(cd_filename)

    ext = _guess_extension(resp, url, cd_filename)

    if display_name.strip():
        filename = sanitize_folder_name(display_name.strip(), max_len=90) + ext
    elif cd_filename:
        filename = sanitize_folder_name(cd_filename, max_len=100)
    else:
        tail = url.split("atcflId=")[-1].split("&")[0] if "atcflId=" in url else "file"
        filename = tail + ext

    path = os.path.join(save_dir, filename)
    # display_name을 파일명으로 쓰면 같은 이름의 첨부가 여러 개일 수 있다
    # (예: "관련 사이트" 링크 여러 개). 덮어쓰지 않도록 번호를 붙인다.
    if os.path.exists(path):
        base, ext2 = os.path.splitext(filename)
        n = 2
        while os.path.exists(os.path.join(save_dir, f"{base}({n}){ext2}")):
            n += 1
        path = os.path.join(save_dir, f"{base}({n}){ext2}")

    with open(path, "wb") as f:
        f.write(resp.content)
    return path


def collect_detail_all(service_key, log_fn, stop_event, download_files=True):
    if not os.path.exists(LIST_OUTPUT_FILE):
        log_fn("✗ services_list.json이 없습니다. 목록조회를 먼저 실행하세요.")
        return

    os.makedirs(SERVICES_DIR, exist_ok=True)
    with open(LIST_OUTPUT_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)
    # servId -> servNm 매핑 (목록조회 시점의 이름으로 폴더명 결정)
    id_to_name = {item["servId"]: item.get("servNm", "") for item in items if item.get("servId")}
    serv_ids = list(id_to_name.keys())

    def already_done(sid):
        folder = service_folder_path(sid, id_to_name[sid])
        return os.path.exists(os.path.join(folder, "detail.json"))

    pending = [sid for sid in serv_ids if not already_done(sid)]
    log_fn(f"전체 {len(serv_ids)}건 중 미수집 {len(pending)}건")

    collected = 0
    for serv_id in pending:
        if stop_event.is_set():
            log_fn("■ 사용자 요청으로 중지되었습니다.")
            break
        try:
            detail, used, limit = fetch_detail(service_key, serv_id)
        except QuotaExceededError as e:
            log_fn(f"⚠ {e}")
            break
        except Exception as e:
            log_fn(f"  ! servId={serv_id} 실패: {e} -> 건너뜀")
            continue

        folder = service_folder_path(serv_id, detail.get("servNm", id_to_name.get(serv_id, "")))
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "detail.json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, indent=2)
        init_posting_status_if_new(serv_id, detail.get("servNm", ""), "central")
        collected += 1
        log_fn(f"  [{used}/{limit}] {serv_id} - {detail.get('servNm', '')}")

        # 첨부 서식자료(basfrmList)가 있으면 attachments/ 하위에 같이 다운로드
        if download_files:
            forms = detail.get("basfrmList", [])
            if isinstance(forms, dict):
                forms = [forms]
            for form in forms:
                link = form.get("servSeDetailLink", "")
                if not link or not link.startswith("http"):
                    continue
                try:
                    saved = download_attachment(
                        link, os.path.join(folder, "attachments"),
                        display_name=form.get("servSeDetailNm", ""),
                    )
                    log_fn(f"      ↳ 첨부 다운로드: {os.path.basename(saved)}")
                except Exception as e:
                    log_fn(f"      ↳ 첨부 다운로드 실패({form.get('servSeDetailNm', '')}): {e}")

    still_pending = len([sid for sid in serv_ids if not already_done(sid)])
    log_fn(f"✓ 이번 실행 수집: {collected}건 / 전체 누적 완료: {len(serv_ids) - still_pending} / {len(serv_ids)}")
    invalidate_score_cache()  # 상세데이터가 바뀌었으니 우선순위 점수 다음 조회 시 재계산


# ============================================================
# 지자체복지서비스 수집 로직
# ============================================================
def collect_lcgv_list_all(service_key, log_fn, stop_event, life_code="", theme_code="",
                           household_code="", ctpv_nm="", sgg_nm="", search_wrd=""):
    os.makedirs(DATA_DIR, exist_ok=True)
    all_items = []
    page_no = 1
    total_count = None
    had_error = False

    while not stop_event.is_set():
        try:
            result, used, limit = _fetch_with_retry(
                fetch_lcgv_list, log_fn,
                service_key=service_key, page_no=page_no, num_of_rows=500,
                lifeArray=life_code, intrsThemaArray=theme_code,
                trgterIndvdlArray=household_code, ctpvNm=ctpv_nm, sggNm=sgg_nm,
                searchWrd=search_wrd,
            )
        except QuotaExceededError as e:
            log_fn(f"⚠ {e}")
            break
        except Exception as e:
            log_fn(f"✗ 지자체 목록조회 실패: {e}")
            had_error = True
            break

        if total_count is None:
            total_count = int(result.get("totalCount", 0))
            log_fn(f"전체 지자체 서비스 수: {total_count}건 (일일 목록조회 {used}/{limit})")

        items = result.get("servList", [])
        if isinstance(items, dict):
            items = [items]
        all_items.extend(items)
        log_fn(f"  page {page_no}: {len(items)}건 수집 (누적 {len(all_items)}/{total_count})")

        if len(all_items) >= total_count or not items:
            break
        page_no += 1

    if had_error:
        # 위 collect_list_all()과 동일한 이유로, 도중에 실패했으면 기존
        # services_list_lcgv.json을 (비어있거나 일부뿐인 all_items로) 덮어쓰지
        # 않고 그대로 둔다 — 2026-08-14 사용자 리포트: read timeout 발생 시
        # 0건으로 덮어써져 기존 지자체 목록이 전부 사라진 사고.
        existing_count = 0
        if os.path.exists(LIST_OUTPUT_FILE_LCGV):
            try:
                with open(LIST_OUTPUT_FILE_LCGV, "r", encoding="utf-8") as f:
                    existing_count = len(json.load(f))
            except (OSError, json.JSONDecodeError):
                pass
        log_fn(f"⚠ 지자체 목록조회가 도중에 실패해 저장을 건너뛰고 기존 데이터"
               f"({existing_count}건)를 그대로 유지합니다. 네트워크 상태를 확인한 뒤 "
               f"다시 시도해주세요.")
        return existing_count

    with open(LIST_OUTPUT_FILE_LCGV, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    newly_added = update_first_seen(all_items, "lcgv")
    log_fn(f"✓ 지자체 목록 저장 완료: {len(all_items)}건 -> {LIST_OUTPUT_FILE_LCGV} (오늘 신규 발견 {newly_added}건)")
    return len(all_items)


def _find_first_url(d: dict):
    """dict 값들 중 http(s)로 시작하는 첫 값을 찾아 반환 (지자체 basfrmList는
    central과 달리 링크/이름 필드가 명확히 구분되지 않아 값 자체로 판별)"""
    for v in d.values():
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


def collect_lcgv_detail_all(service_key, log_fn, stop_event, download_files=True):
    if not os.path.exists(LIST_OUTPUT_FILE_LCGV):
        log_fn("✗ services_list_lcgv.json이 없습니다. 지자체 목록조회를 먼저 실행하세요.")
        return

    os.makedirs(SERVICES_DIR_LCGV, exist_ok=True)
    with open(LIST_OUTPUT_FILE_LCGV, "r", encoding="utf-8") as f:
        items = json.load(f)
    id_to_name = {item["servId"]: item.get("servNm", "") for item in items if item.get("servId")}
    serv_ids = list(id_to_name.keys())

    def folder_for(sid):
        return os.path.join(
            SERVICES_DIR_LCGV, f"{sanitize_folder_name(id_to_name[sid])}_{sid}"
        )

    def already_done(sid):
        return os.path.exists(os.path.join(folder_for(sid), "detail.json"))

    pending = [sid for sid in serv_ids if not already_done(sid)]
    log_fn(f"전체 {len(serv_ids)}건 중 미수집 {len(pending)}건")

    collected = 0
    for serv_id in pending:
        if stop_event.is_set():
            log_fn("■ 사용자 요청으로 중지되었습니다.")
            break
        try:
            detail, used, limit = fetch_lcgv_detail(service_key, serv_id)
        except QuotaExceededError as e:
            log_fn(f"⚠ {e}")
            break
        except Exception as e:
            log_fn(f"  ! servId={serv_id} 실패: {e} -> 건너뜀")
            continue

        folder = os.path.join(
            SERVICES_DIR_LCGV,
            f"{sanitize_folder_name(detail.get('servNm', id_to_name.get(serv_id, '')))}_{serv_id}",
        )
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "detail.json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, indent=2)
        init_posting_status_if_new(serv_id, detail.get("servNm", ""), "lcgv")
        collected += 1
        log_fn(f"  [{used}/{limit}] {serv_id} - {detail.get('servNm', '')}")

        if download_files:
            forms = detail.get("basfrmList", [])
            if isinstance(forms, dict):
                forms = [forms]
            for form in forms:
                link = _find_first_url(form)
                if not link:
                    continue
                try:
                    saved = download_attachment(
                        link, os.path.join(folder, "attachments"),
                        display_name=form.get("wlfareInfoReldNm", ""),
                    )
                    log_fn(f"      ↳ 첨부 다운로드: {os.path.basename(saved)}")
                except Exception as e:
                    label = form.get("wlfareInfoReldNm", "")
                    log_fn(f"      ↳ 첨부 다운로드 실패({label}): {e}")

    still_pending = len([sid for sid in serv_ids if not already_done(sid)])
    log_fn(f"✓ 이번 실행 수집: {collected}건 / 전체 누적 완료: {len(serv_ids) - still_pending} / {len(serv_ids)}")
    invalidate_score_cache()  # 상세데이터가 바뀌었으니 우선순위 점수 다음 조회 시 재계산


# ============================================================
# 포스팅 우선순위 점수 (100점 만점)
#   API 호출 없이 이미 수집된 detail.json만으로 계산. 화면을 열 때마다(또는
#   상세조회가 끝날 때마다) 그 시점까지 모인 데이터 기준으로 다시 계산되며,
#   별도로 저장하지 않는다(고정값이 아니라 "지금 시점 참고용" 순위이므로).
#   중앙부처/지자체는 모수가 다르므로 반드시 각 소스 안에서만 백분위를 계산.
# ============================================================
_SCORE_CACHE = {"중앙부처": None, "지자체": None}

# v6.3: build_listing_rows()가 지자체 행마다(이름이 중앙부처와 매칭될 때)
# central_detail.json + lcgv_detail.json을 매번 다시 읽고 confirm_duplicate_
# via_detail()을 재계산하던 부분 — 캐시가 전혀 없어 build_listing_rows()를
# 부를 때마다(3)리스트업, 4)포스팅 관리 새로고침, 7)포스팅 이력관리 등) 매번 같은
# 계산을 반복하고 있었음. (central_sid, lcgv_sid) 쌍 -> bool(중복 확정 여부)
# 로 캐시하고, detail 데이터가 바뀔 때만(=invalidate_score_cache 호출 시점과
# 완전히 동일한 시점) 함께 비운다 — 점수 캐시와 무효화 조건이 정확히
# 같으므로(둘 다 "상세조회로 detail.json이 새로 생기거나 바뀜") 별도 무효화
# 지점을 새로 추가하지 않고 편승.
_DUPLICATE_MATCH_CACHE = {}

# [v7.11 신규] _find_similar_serv_name()의 difflib 스캔 결과 캐시.
# 정규화된 지자체 이름(norm_name) -> (best_sid, best_ratio). v7.9에서
# 퍼지 매칭을 추가할 때 이 캐시를 깜빡해서, build_listing_rows()가
# 호출될 때마다(그것도 _get_selected_posting_row()가 트리 클릭 한
# 번마다 매번 build_listing_rows() 전체를 다시 부르는 기존 구조 위에서)
# 정확 일치가 안 되는 지자체 행마다 전체 중앙부처 목록을 O(n) difflib로
# 훑는 게 매번 반복돼, 목록 스크롤·클릭할 때마다 랙이 걸리는 심각한
# 성능 회귀가 생겼다(사용자 리포트: "포스팅관리 리스트 스크롤하고
# 클릭시 랙 걸려... 백그라운드 로딩도 오히려 시간이 더 걸려" — 이건
# 별개의 새 기능이 아니라 build_listing_rows() 자체가 무거워져 시작
# 시 백그라운드 스캔(_compute_status_and_rows)도 같이 느려진 것).
# _DUPLICATE_MATCH_CACHE와 동일하게 invalidate_score_cache()에 편승해
# 무효화한다.
_FUZZY_MATCH_CACHE = {}


def invalidate_score_cache():
    """수집 데이터가 바뀌었을 때(상세조회 완료 등) 캐시를 비운다.
    다음 조회 시 자동으로 새로 계산됨."""
    global _SCORE_CACHE, _DUPLICATE_MATCH_CACHE, _FUZZY_MATCH_CACHE, _CENTRAL_NAMES_SORTED_CACHE
    _SCORE_CACHE = {"중앙부처": None, "지자체": None}
    _DUPLICATE_MATCH_CACHE = {}
    _FUZZY_MATCH_CACHE = {}
    _CENTRAL_NAMES_SORTED_CACHE = None


_PLACEHOLDER_PATTERNS = ["참고해 주시기 바랍니다", "참고 바랍니다", "해당없음", "해당 없음"]


def _is_placeholder_text(s: str) -> bool:
    """"지원대상의 내용을 참고해 주시기 바랍니다." 같은 사실상 빈 답변인지 판별"""
    s = (s or "").strip()
    if len(s) < 10:
        return True
    return len(s) < 40 and any(p in s for p in _PLACEHOLDER_PATTERNS)


def _parse_yyyymmdd(s: str):
    try:
        return datetime.datetime.strptime((s or "").strip(), "%Y%m%d").date()
    except (ValueError, AttributeError):
        return None


def _score_one_detail(detail: dict, source: str, percentile_fn) -> dict:
    """개별 서비스 하나의 점수 계산. percentile_fn(inqNum)은 같은 소스 안에서의
    백분위(0~1, 1에 가까울수록 조회수 상위)를 돌려주는 함수."""
    criteria = (detail.get("slctCritCn") or "").strip()
    benefit = (detail.get("alwServCn") or "").strip()

    # 하드 필터: 각색할 내용 자체가 없음
    if not criteria and not benefit:
        return {"score": None, "excluded": True, "reason": "선정기준/혜택 내용 없음"}

    # 하드 필터: 지자체 사업이 이미 종료됨
    if source == "지자체":
        end_date = _parse_yyyymmdd(detail.get("enfcEndYmd", ""))
        if end_date and end_date < datetime.date.today():
            return {"score": None, "excluded": True, "reason": f"시행종료({end_date.isoformat()})"}

    score = 0

    # ① 조회수 신호 40점 (소스 내 백분위)
    try:
        inq = int(detail.get("inqNum", 0) or 0)
    except (TypeError, ValueError):
        inq = 0
    pct = percentile_fn(inq)
    if pct >= 0.9:
        score += 40
    elif pct >= 0.7:
        score += 25
    elif pct >= 0.4:
        score += 10

    # ② 정보 완성도 25점
    if not (_is_placeholder_text(criteria) and _is_placeholder_text(benefit)):
        combined_len = len(criteria) + len(benefit)
        if combined_len >= 100:
            score += 25
        elif combined_len >= 50:
            score += 15
        else:
            score += 5

    # ③ 실행 가능성 15점
    if source == "중앙부처":
        if detail.get("onapPsbltYn") == "Y":
            score += 15
    else:
        apply_txt = detail.get("aplyMtdCn", "") or ""
        if "온라인" in apply_txt or "인터넷" in apply_txt:
            score += 15

    # ④ 대상 폭 10점
    breadth = 0
    for key in ("lifeArray", "lifeNmArray", "trgterIndvdlArray", "trgterIndvdlNmArray"):
        val = detail.get(key)
        if isinstance(val, str) and val.strip():
            breadth += len([x for x in val.split(",") if x.strip()])
    # 중앙부처/지자체 각각 생애주기+가구유형 두 필드에서 중복 집계되지 않도록
    # (중앙부처는 lifeArray/trgterIndvdlArray만, 지자체는 lifeNmArray/trgterIndvdlNmArray만 채워짐)
    breadth = min(breadth, 6)
    if breadth >= 2:
        score += 10
    elif breadth == 1:
        score += 5

    # ⑤ 최신성 10점
    if source == "중앙부처":
        try:
            yr = int(detail.get("crtrYr", 0) or 0)
            age = datetime.date.today().year - yr
            if 0 <= age <= 1:
                score += 10
            elif age <= 2:
                score += 5
        except (TypeError, ValueError):
            pass
    else:
        mod_date = _parse_yyyymmdd(detail.get("lastModYmd", ""))
        if mod_date:
            days = (datetime.date.today() - mod_date).days
            if days <= 365:
                score += 10
            elif days <= 730:
                score += 5

    return {"score": score, "excluded": False, "reason": ""}


def _compute_scores_for_source(source_label: str) -> dict:
    if source_label == "중앙부처":
        list_file, folder_fn = LIST_OUTPUT_FILE, service_folder_path
    else:
        list_file = LIST_OUTPUT_FILE_LCGV
        folder_fn = lambda sid, nm: os.path.join(SERVICES_DIR_LCGV, f"{sanitize_folder_name(nm)}_{sid}")  # noqa: E731

    if not os.path.exists(list_file):
        return {}
    with open(list_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    items_with_detail = []
    for item in items:
        sid = item.get("servId")
        nm = item.get("servNm", "")
        if not sid:
            continue
        detail_path = os.path.join(folder_fn(sid, nm), "detail.json")
        if not os.path.exists(detail_path):
            continue
        try:
            with open(detail_path, "r", encoding="utf-8") as f:
                detail = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        items_with_detail.append((sid, detail))

    if not items_with_detail:
        return {}

    inq_values = []
    for _, detail in items_with_detail:
        try:
            inq_values.append(int(detail.get("inqNum", 0) or 0))
        except (TypeError, ValueError):
            inq_values.append(0)
    sorted_inq = sorted(inq_values)
    n = len(sorted_inq)

    def percentile_fn(v):
        import bisect
        return bisect.bisect_right(sorted_inq, v) / n if n else 0.0

    return {
        sid: _score_one_detail(detail, source_label, percentile_fn)
        for sid, detail in items_with_detail
    }


def get_priority_scores(source_label: str) -> dict:
    """servId -> {"score": int|None, "excluded": bool, "reason": str}.
    캐시되며, invalidate_score_cache() 호출 전까지는 재계산하지 않는다
    (수천 건 detail.json을 매 화면 갱신마다 다시 읽지 않도록)."""
    global _SCORE_CACHE
    if _SCORE_CACHE.get(source_label) is None:
        _SCORE_CACHE[source_label] = _compute_scores_for_source(source_label)
    return _SCORE_CACHE[source_label]


def format_priority_score(row: dict) -> str:
    """리스트업/포스팅관리 트리에 표시할 우선순위 점수 문자열"""
    if not row.get("downloaded"):
        return "-"
    if row.get("excluded"):
        return "❌제외"
    score = row.get("priority_score")
    return str(score) if score is not None else "-"


def sort_rows(rows: list, sort_label: str) -> list:
    """리스트업/포스팅관리 공통 정렬. 기본은 우선순위 높은순이며, 미수집/제외
    항목은 점수와 무관하게 항상 맨 아래로 보낸다."""
    if sort_label == "최초발견일 최신순":
        return sorted(rows, key=lambda r: r.get("first_seen_date") or "", reverse=True)
    if sort_label == "서비스명":
        return sorted(rows, key=lambda r: r.get("servNm") or "")

    def key(r):
        if r.get("downloaded") and not r.get("excluded") and r.get("priority_score") is not None:
            return (0, -r["priority_score"])
        return (1, 0)

    return sorted(rows, key=key)


# ============================================================
# 리스트업 (전체 현황 대시보드) — 지식인 프로그램 이력관리 탭 패턴 참고:
# Treeview + 상태필터 + 검색 + 엑셀 내보내기, "오늘 신규"는 first_seen 기준
# ============================================================
COMMON_SERVICE_NAME_SUFFIXES = [
    "지원사업", "지원 사업", "지원서비스", "지원 서비스",
    "지원", "사업", "서비스", "프로그램",
]  # 지자체가 중앙부처 사업명 뒤에 흔히 덧붙이는 접미어. 긴 것부터 매칭해야
   # "지원사업" 전체가 먼저 빠지고 "지원"만 남아 또 한 번 잘리는 이중 스트립을
   # 피할 수 있다("OO지원사업" -> "OO"가 한 번에 되도록).


def _normalize_serv_name(name: str) -> str:
    """정책명 비교(중앙부처↔지자체 동일 정책 판별)용 정규화. 괄호 안 내용
    (지역명 등이 들어가는 경우가 있어 제거)과 공백을 모두 없애고, 지자체가
    흔히 덧붙이는 접미어("지원", "사업" 등)까지 제거한 뒤 비교한다.
    예: "방과후학교 자유수강권 지원" -> "방과후학교자유수강권" (중앙부처
    "방과후학교 자유수강권"과 일치).

    접미어 제거는 반복 적용한다(예: "OO 지원 사업"처럼 두 단어가 겹쳐
    붙는 경우까지 커버하기 위해) — 단, 접미어를 다 떼고 나면 아무것도
    안 남는 경우(접미어 자체가 정책명 전체인 경우)는 원래 정규화 결과를
    그대로 둔다(오탐 방지)."""
    name = (name or "").strip()
    name = re.sub(r"[\(（].*?[\)）]", "", name)
    name = re.sub(r"\s+", "", name)
    if not name:
        return name
    stripped = name
    changed = True
    while changed:
        changed = False
        for suffix in COMMON_SERVICE_NAME_SUFFIXES:
            suffix_nospace = re.sub(r"\s+", "", suffix)
            if stripped.endswith(suffix_nospace) and len(stripped) > len(suffix_nospace):
                stripped = stripped[: -len(suffix_nospace)]
                changed = True
                break
    return stripped or name


SIMILAR_SERV_NAME_THRESHOLD = 0.82  # 이 이상이면 "이름 유사"로 본다 —
# 오탐(전혀 다른 정책인데 이름이 비슷해 묶이는 것) 방지를 위해 다소
# 보수적으로 잡았다. 낮추면 더 많이 잡히지만 오탐 위험도 커진다.

# [v7.14 신규] difflib.SequenceMatcher.ratio()는 항상
# ratio <= 2*min(len(a),len(b)) / (len(a)+len(b)) 를 만족한다(매칭되는
# 글자 수가 아무리 많아도 짧은 쪽 길이를 넘을 수 없으므로). 그래서
# 길이 차이가 큰 후보는 실제로 비교해볼 것도 없이 threshold를 못
# 넘는다는 게 수학적으로 확정된다 — 이 범위 밖은 아예 건너뛴다.
# 중앙부처 이름들을 길이순으로 한 번 정렬해두고(캐시), 매 비교마다
# bisect로 그 범위만 잘라내면 전수비교보다 훨씬 적게 훑는다(정확도
# 손실 없음 — 놓칠 수 있는 후보가 수학적으로 없다).
_CENTRAL_NAMES_SORTED_CACHE = None  # [(길이, 정규화이름, servId), ...] 길이순


def _get_central_names_sorted(central_name_to_id: dict) -> list:
    global _CENTRAL_NAMES_SORTED_CACHE
    if _CENTRAL_NAMES_SORTED_CACHE is not None:
        return _CENTRAL_NAMES_SORTED_CACHE
    items = sorted(
        ((len(norm), norm, sid) for norm, sid in central_name_to_id.items() if len(norm) >= 4),
        key=lambda t: t[0],
    )
    _CENTRAL_NAMES_SORTED_CACHE = items
    return items


def _find_similar_serv_name(norm_name: str, central_name_to_id: dict) -> tuple:
    """[v7.9 신규, v7.14에서 길이 가지치기로 속도 개선] 접미어 스트립
    후에도 완전히 똑같지 않은 정책명 쌍을 잡기 위한 퍼지 매칭 폴백.
    _normalize_serv_name()의 정확 일치 사전조회(central_name_to_id.get
    (...))가 실패했을 때만 호출한다 — 사전조회로 이미 잡히는 케이스
    까지 매번 전체를 훑을 필요는 없어서(성능), 실패 케이스에서만
    비용을 쓴다. COMMON_SERVICE_NAME_SUFFIXES 목록에 없는 접미어
    ("지원금", "혜택", "바우처" 등)나, 정책명 중간에 수식어가 붙어
    정확히는 안 맞는 경우(예: "청년월세지원" vs "청년월세한시특별지원")
    를 잡기 위한 것.

    difflib.SequenceMatcher 비율이 SIMILAR_SERV_NAME_THRESHOLD 이상인
    후보 중 가장 높은 것 하나를 돌려준다. 너무 짧은 이름(4자 미만)은
    비교하지 않는다 — 짧을수록 우연히 비율이 높게 나오기 쉬워서(예:
    "노인" vs "장애인") 오탐 위험이 크다.

    반환: (central_servId 또는 None, 유사도 0~1)"""
    if norm_name in _FUZZY_MATCH_CACHE:
        return _FUZZY_MATCH_CACHE[norm_name]

    la = len(norm_name)
    if la < 4:
        result = (None, 0.0)
        _FUZZY_MATCH_CACHE[norm_name] = result
        return result

    sorted_items = _get_central_names_sorted(central_name_to_id)
    lengths = [t[0] for t in sorted_items]
    t = SIMILAR_SERV_NAME_THRESHOLD
    # ratio <= 2*min(la,lb)/(la+lb) >= t 를 만족하는 lb 범위.
    lo_lb = math.ceil(la * t / (2 - t))
    hi_lb = math.floor(la * (2 - t) / t)
    left = bisect.bisect_left(lengths, lo_lb)
    right = bisect.bisect_right(lengths, hi_lb)

    best_sid, best_ratio = None, 0.0
    for _length, cand_norm, cand_sid in sorted_items[left:right]:
        ratio = difflib.SequenceMatcher(None, norm_name, cand_norm).ratio()
        if ratio > best_ratio:
            best_sid, best_ratio = cand_sid, ratio
    result = (best_sid, best_ratio) if best_ratio >= SIMILAR_SERV_NAME_THRESHOLD else (None, best_ratio)
    _FUZZY_MATCH_CACHE[norm_name] = result
    return result


def _extract_tag_set(detail: dict, central_key: str, lcgv_key: str) -> set:
    """중앙부처/지자체 API는 같은 의미의 필드도 이름이 다르다(예:
    trgterIndvdlArray vs trgterIndvdlNmArray). 두 필드명을 다 시도해서
    쉼표로 구분된 태그 문자열을 집합으로 바꾼다."""
    raw = detail.get(central_key) or detail.get(lcgv_key) or ""
    return {t.strip() for t in raw.split(",") if t.strip()}


def _load_detail_json(folder: str) -> dict:
    path = os.path.join(folder, "detail.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def confirm_duplicate_via_detail(central_detail: dict, lcgv_detail: dict) -> bool:
    """이름 매칭으로 이미 "의심"된 두 항목의 detail.json이 둘 다 있으면,
    대상자특성(trgterIndvdl) 태그 집합이 얼마나 겹치는지로 확신도를 한
    번 더 높인다. 태그가 하나라도 있고 절반 이상 겹치면 "확인됨"으로
    본다 — 이름 접미어 매�판만으로는 걸러지지 않는 우연의 일치(전혀
    다른 정책인데 이름이 비슷한 경우)를 줄이기 위한 보조 확인용이며,
    이 함수 결과가 False라고 해서 제외 처리 자체를 취소하지는 않는다
    (이름 일치가 이미 충분히 강한 신호이므로) — 사유 문구를 더
    구체적으로 만드는 데만 쓴다."""
    central_tags = _extract_tag_set(central_detail, "trgterIndvdlArray", "trgterIndvdlNmArray")
    lcgv_tags = _extract_tag_set(lcgv_detail, "trgterIndvdlArray", "trgterIndvdlNmArray")
    if not central_tags or not lcgv_tags:
        return False
    overlap = central_tags & lcgv_tags
    smaller = min(len(central_tags), len(lcgv_tags))
    return smaller > 0 and len(overlap) / smaller >= 0.5


def build_listing_rows(include_fuzzy: bool = False) -> list:
    """중앙부처+지자체 전체 목록을 읽어, 서비스별 수집상태/최초발견일/포스팅상태/
    우선순위점수를 합쳐 리스트업 화면에 쓸 행 목록을 만든다. API 호출 없이
    로컬 파일만 읽음.

    [중앙부처/지자체 동일 정책명 처리] 지자체가 중앙부처와 똑같은(또는
    "지원"/"사업" 같은 흔한 접미어만 다른) 이름의 정책을 운영하는 경우
    (중앙부처 사업을 그 지역에서 집행하는 경우가 많음), 지자체 쪽은
    우선순위 계산에서 자동으로 "제외" 처리해 목록 맨 아래로 보낸다 —
    중앙부처는 전국 단위라 한 번만 검토/포스팅하면 되고, 같은 정책의
    지자체 건까지 중복으로 작업할 필요는 없다는 판단. 이름 정규화만으로
    매칭되면 일단 제외로 표시하고, 양쪽 detail.json이 이미 수집되어
    있으면 대상자특성 태그 겹침까지 확인해 사유 문구에 확신도를 덧붙인다
    (예: 방과후학교 자유수강권 지원(제주) ↔ 방과후학교 자유수강권(중앙),
    대상자특성 "다문화·탈북민/한부모·조손/저소득" 완전일치로 확인됨).
    데이터 자체는 지우지 않으므로, 실제로 지자체판이 지원금 증액 등으로
    내용이 다르면 사람이 직접 열어보고 예외적으로 진행할 수 있다.

    [v7.15] include_fuzzy=True일 때만 _find_similar_serv_name() 퍼지
    매칭(v7.9)까지 돈다 — 이름 정규화만으로는 정확히 안 맞는 "거의
    중복" 건까지 잡아주지만, 첫 스캔(캐시 없음)에서 여전히 체감되는
    비용이 있다(v7.14로 길이 가지치기까지 넣었지만 완전히 없애지는
    못함 — 자세한 배경은 v7.14 changelog 참고). 기본값을 False로
    바꿔서, 트리 클릭·시작 스캔 등 일반적인 새로고침에서는 이 비용을
    아예 안 치르고(2026-09-03 구버전과 동일한 속도로 돌아감 —
    구버전 비교 확인 결과, 그 버전 자체는 지금과 구조가 거의 같고
    퍼지 매칭만 없었던 것으로 확인됨), "🔁 중복 정책 재검사(전체
    스캔)"처럼 사용자가 명시적으로 원할 때만 include_fuzzy=True로
    한 번 돌리는 방식으로 바꿨다."""
    first_seen = load_first_seen()
    posting_status = load_posting_status()
    today = datetime.date.today().isoformat()
    rows = []

    # 지자체 중복 판별용 — 중앙부처 정책명(정규화됨) -> servId 매핑을 먼저
    # 확보(수집 여부와 무관하게 목록조회만 되어 있으면 비교 대상에 포함).
    # 나중에 detail.json 대조를 위해 이름뿐 아니라 servId도 함께 들고 있는다.
    central_name_to_id = {}
    if os.path.exists(LIST_OUTPUT_FILE):
        with open(LIST_OUTPUT_FILE, "r", encoding="utf-8") as f:
            central_items_all = json.load(f)
        for it in central_items_all:
            nm = it.get("servNm", "")
            sid = it.get("servId", "")
            if nm and sid:
                central_name_to_id.setdefault(_normalize_serv_name(nm), sid)

    sources = [
        ("중앙부처", LIST_OUTPUT_FILE, service_folder_path),
        ("지자체", LIST_OUTPUT_FILE_LCGV,
         lambda sid, nm: os.path.join(SERVICES_DIR_LCGV, f"{sanitize_folder_name(nm)}_{sid}")),
        # [v7.20 신규] 허브(종합) — create_hub_service()로 사람이 직접
        # 만든 항목만 들어있다. 중앙부처/지자체 중복 판별 로직은
        # source_label == "지자체"에서만 도므로 허브는 자동으로 건너뛴다.
        ("허브", LIST_OUTPUT_FILE_HUB, hub_folder_path),
    ]

    for source_label, list_file, folder_fn in sources:
        if not os.path.exists(list_file):
            continue
        with open(list_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        scores = get_priority_scores(source_label)
        for item in items:
            sid = item.get("servId")
            if not sid:
                continue
            nm = item.get("servNm", "")
            folder = folder_fn(sid, nm)
            downloaded = os.path.exists(os.path.join(folder, "detail.json"))
            fs = first_seen.get(sid, {})
            first_seen_date = fs.get("date_first_seen", "")
            status = posting_status.get(sid, {}).get("status", "") if downloaded else ""
            score_info = scores.get(sid, {"score": None, "excluded": False, "reason": ""})

            excluded = score_info["excluded"]
            exclude_reason = score_info["reason"]
            matched_central_id = ""
            match_confidence = ""
            if source_label == "지자체":
                norm_nm = _normalize_serv_name(nm)
                central_sid = central_name_to_id.get(norm_nm)
                if central_sid:
                    matched_central_id = central_sid
                    match_confidence = "이름 일치"
                else:
                    # [v7.9 신규, v7.15에서 include_fuzzy 플래그로 옵트인
                    # 전환] 정확 일치가 아니면 퍼지 매칭(difflib)으로
                    # 한 번 더 확인 — COMMON_SERVICE_NAME_SUFFIXES에 없는
                    # 접미어나 중간 수식어 차이로 사전조회가 실패하는
                    # "거의 중복"까지 잡기 위함. 기본 새로고침에서는
                    # 건너뛰고(빠름), "🔁 중복 정책 재검사"에서만 돈다.
                    if include_fuzzy:
                        fuzzy_sid, fuzzy_ratio = _find_similar_serv_name(norm_nm, central_name_to_id)
                        if fuzzy_sid:
                            central_sid = fuzzy_sid
                            matched_central_id = fuzzy_sid
                            match_confidence = f"이름 유사 {fuzzy_ratio:.0%}"
                if central_sid:
                    if downloaded:
                        # service_folder_path는 폴더명에 서비스명을 쓰므로 servId만으로는
                        # 정확한 폴더를 못 찾는다 — 중앙부처 목록에서 이름을 찾아 폴더를 만든다.
                        central_nm = next(
                            (it.get("servNm", "") for it in central_items_all if it.get("servId") == central_sid),
                            "",
                        )
                        central_folder = service_folder_path(central_sid, central_nm)
                        # v6.3: (central_sid, lcgv_sid) 쌍으로 캐시 — 같은 쌍을
                        # 다시 만나면 detail.json을 또 읽지 않고 이전 결과를 재사용
                        dup_cache_key = (central_sid, sid)
                        if dup_cache_key not in _DUPLICATE_MATCH_CACHE:
                            central_detail = _load_detail_json(central_folder)
                            lcgv_detail = _load_detail_json(folder)
                            _DUPLICATE_MATCH_CACHE[dup_cache_key] = bool(
                                central_detail and lcgv_detail
                                and confirm_duplicate_via_detail(central_detail, lcgv_detail)
                            )
                        if _DUPLICATE_MATCH_CACHE[dup_cache_key]:
                            match_confidence = (
                                "이름+대상자특성 일치" if match_confidence == "이름 일치"
                                else f"{match_confidence}+대상자특성 일치"
                            )
                    if not excluded:
                        excluded = True
                        if match_confidence.endswith("대상자특성 일치"):
                            exclude_reason = f"🔁 중앙부처 동일 정책 확인됨({match_confidence}) — 중앙부처만 검토 권장"
                        elif match_confidence.startswith("이름 유사"):
                            # 퍼지 매칭은 정확 일치보다 신뢰도가 낮으므로 문구를
                            # 다르게 해 "반드시 직접 확인"을 강조한다.
                            exclude_reason = f"🔁 중앙부처 유사 정책 의심({match_confidence}, 이름 완전 일치 아님) — 직접 열어 같은 정책인지 확인 필요"
                        else:
                            exclude_reason = f"🔁 중앙부처 동일 정책 추정({match_confidence}) — 중앙부처만 검토 권장"

            rows.append({
                "source": source_label,
                "servId": sid,
                "servNm": nm,
                "downloaded": downloaded,
                "folder": folder,
                "first_seen_date": first_seen_date,
                "is_new_today": first_seen_date == today,
                "posting_status": status,
                "priority_score": score_info["score"],
                "excluded": excluded,
                "exclude_reason": exclude_reason,
                # 아래 두 필드는 지자체 행에만 채워짐(중앙부처 행은 밑에서 역방향으로 채움)
                "matched_central_id": matched_central_id,
                "match_confidence": match_confidence,
                "related_lcgv_ids": [],  # 중앙부처 행에서만 사용 — 이 정책과 매칭된 지자체 servId 목록
            })

    # 역방향 연결: 지자체 행에서 찾은 matched_central_id를 이용해, 해당
    # 중앙부처 행에 "연관된 지자체가 몇 건 있는지"를 채워 넣는다. 리스트업
    # 화면에서 중앙부처 쪽에도 "지자체 N건 연관"을 보여주기 위함 — 중앙부처를
    # 먼저 포스팅완료 처리하기 전에, 아직 처리 안 된 지자체 중복 건이 있는지
    # 미리 확인할 수 있게 하려는 목적.
    central_row_by_id = {r["servId"]: r for r in rows if r["source"] == "중앙부처"}
    for r in rows:
        if r["source"] == "지자체" and r["matched_central_id"]:
            central_row = central_row_by_id.get(r["matched_central_id"])
            if central_row is not None:
                central_row["related_lcgv_ids"].append(r["servId"])

    return rows


def get_infographic_candidate_rows() -> list:
    """5)인포그래픽 작성 탭 콤보박스용 후보 목록(servId/servNm/source만
    필요)을 만든다. 예전에는 build_listing_rows()를 그대로 재사용했는데,
    그 함수는 중앙부처+지자체 전체(수천 건)를 순회하며 건마다 detail.json
    존재 확인(os.path.exists) + 지자체는 중복정책 대조용 detail.json
    재읽기(confirm_duplicate_via_detail) + get_priority_scores()의 전체
    우선순위 점수 계산까지 수행한다 — 정작 이 탭이 쓰는 필드는
    servId/servNm/source 3개뿐이라 완전히 낭비였음(v5.7에서 인포그래픽
    탭 전환이 느리다는 사용자 리포트로 발견).

    최종각색 결과는 stage_outputs.json에 servId 기준으로 이미 저장되어
    있고(보통 수십~수백 건, 전체 서비스 대비 훨씬 적음), servNm/source는
    posting_status.json에 각 단계 진입 시(advance_posting_status)
    이미 기록되어 있으므로, 이 두 파일만 읽으면 충분하다. API 호출 없이
    로컬 파일 2개만 읽으므로 build_listing_rows() 대비 훨씬 빠르다."""
    stage_outputs = load_stage_outputs()
    posting_status = load_posting_status()
    rows = []
    for serv_id, entry in stage_outputs.items():
        if not entry.get("final_adaptation"):
            continue
        info = posting_status.get(serv_id, {})
        rows.append({
            "source": info.get("source", ""),
            "servId": serv_id,
            "servNm": info.get("servNm", ""),
            "posting_status": info.get("status", ""),
        })
    return rows


def export_listing_xlsx(rows: list, save_path: str):
    """리스트업 현황을 엑셀로 저장. openpyxl 미설치면 (False, 안내문구) 반환."""
    if not HAS_OPENPYXL:
        return False, "openpyxl이 설치되어 있지 않습니다. 'pip install openpyxl' 후 다시 시도하세요."

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "리스트업"

        headers = ["출처", "서비스명", "서비스ID", "수집상태", "최초발견일", "오늘신규"]
        ws.append(headers)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill

        for r in rows:
            ws.append([
                r["source"], r["servNm"], r["servId"],
                "완료" if r["downloaded"] else "미수집",
                r["first_seen_date"],
                "신규" if r["is_new_today"] else "",
            ])

        widths = [10, 45, 16, 10, 14, 8]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        wb.save(save_path)
        return True, save_path
    except PermissionError:
        return False, f"파일이 열려있어 저장할 수 없습니다: {save_path}\n엑셀에서 파일을 닫고 다시 시도하세요."
    except Exception as e:
        return False, str(e)


def export_posting_status_xlsx(rows: list, save_path: str):
    """포스팅 관리 탭 전용 엑셀 내보내기 (상태 컬럼 포함)"""
    if not HAS_OPENPYXL:
        return False, "openpyxl이 설치되어 있지 않습니다. 'pip install openpyxl' 후 다시 시도하세요."
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "포스팅관리"

        headers = ["출처", "서비스명", "서비스ID", "포스팅상태", "최초발견일"]
        ws.append(headers)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill

        for r in rows:
            ws.append([
                r["source"], r["servNm"], r["servId"],
                r["posting_status"] or "(미수집)", r["first_seen_date"],
            ])

        widths = [10, 45, 16, 16, 14]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        wb.save(save_path)
        return True, save_path
    except PermissionError:
        return False, f"파일이 열려있어 저장할 수 없습니다: {save_path}\n엑셀에서 파일을 닫고 다시 시도하세요."
    except Exception as e:
        return False, str(e)


def normalize_keyword_for_match(text: str) -> str:
    """키워드 엑셀에 이미 등록된 제목인지 비교할 때 쓰는 정규화 —
    파일명 금지문자 제거 + 공백 정리 + 대소문자 무시(정책뉴스 프로그램의
    _normalize_title_for_match와 동일한 규칙, 스키마 통일 목적)."""
    s = re.sub(r'[\\/:*?"<>|]', "", text or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s.lower()


def load_registered_keyword_titles() -> set:
    """키워드 엑셀(A열, 헤더 제외)에 이미 등록된 제목들을 정규화해서
    set으로 반환. 파일이 없으면 빈 set(전부 신규로 처리됨)."""
    path = get_keyword_excel_path()
    if not HAS_OPENPYXL or not os.path.exists(path):
        return set()
    try:
        wb = load_workbook(path, read_only=True)
        ws = wb.active
        titles = set()
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[0]:
                titles.add(normalize_keyword_for_match(str(row[0])))
        wb.close()
        return titles
    except Exception:
        return set()


def get_last_used_keyword_category() -> str:
    """키워드 엑셀 B열에서 데이터가 있는 마지막 행의 값을 읽어온다.
    카테고리 입력란의 기본값(placeholder)으로 쓴다 — 매번 새로 타이핑
    안 해도 직전에 쓴 카테고리가 미리 채워져 있게 하기 위함."""
    path = get_keyword_excel_path()
    if not HAS_OPENPYXL or not os.path.exists(path):
        return ""
    try:
        wb = load_workbook(path, read_only=True)
        ws = wb.active
        last_category = ""
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[1] not in (None, ""):
                last_category = str(row[1])
        wb.close()
        return last_category
    except Exception:
        return ""


# 카테고리는 복지로 프로그램 전용 값이라 config.json(Naver_blog_config_복지로.json)에
# 저장한다 — env.txt는 지식인/정책뉴스/메인 오토포스팅 등 "여러 프로그램이
# 공유해야 하는 값"(Base IP, 네트워크 모드)만 담는 자리이므로 프로그램별
# 설정을 섞지 않는다.
def get_default_keyword_category() -> str:
    """카테고리 입력란의 기본값을 결정한다. config.json에 저장된 직전 값이
    있으면 그것을 우선 사용하고(프로그램을 껐다 켜도, 아직 이번 회차
    등록을 한 번도 안 한 상태에서도 값이 유지됨), 없으면 기존 방식대로
    키워드 엑셀 B열의 마지막 값을 사용한다."""
    cfg_value = load_config().get("kw_last_category", "").strip()
    if cfg_value:
        return cfg_value
    return get_last_used_keyword_category()


def save_last_used_keyword_category(category: str):
    """카테고리 값을 config.json에 저장(다음 실행 시 입력란 기본값으로 복원)."""
    cfg = load_config()
    cfg["kw_last_category"] = category
    save_config(cfg)


def append_titles_to_keyword_excel(titles: list, category="") -> str:
    """승인된 제목들을 키워드 엑셀에 추가한다. 실제 운영 중인 정책뉴스
    키워드 엑셀 파일을 직접 확인해서 맞춘 스키마다:
      - 시트명 "Keywords"
      - A열 "키워드"(제목 텍스트) / B열 "카테고리" / C열 "상태"
      - **C열(상태)은 이 서브프로그램에서는 항상 비워둔다** — 실제
        포스팅을 마친 뒤 메인 포스팅 프로그램이 그 값을 채워 넣는다
        (서브프로그램이 상태를 미리 채우면 안 됨).
      - B열(카테고리)은 호출부(키워드 등록 탭의 카테고리 입력란)에서
        받은 값을 그대로 쓴다. 값을 안 주면(빈 문자열) B열에서 "데이터가
        있는 마지막 행"의 값을 재사용한다(지식인·정책뉴스 프로그램과
        동일한 기존 규칙 — 완전히 새로 만들지는 않고 직전 값을 이어감).
    반환값은 실제 사용된 카테고리 값(로그 표시용).

    ✅ [2026-09-29] category에 titles와 같은 길이의 list를 주면 제목마다
    다른 값(게시판 번호/이름)을 그대로 기록한다. 이 경우에는 '직전 값
    재사용'을 하지 않는다 - 빈 문자열(미분류)은 B열을 빈칸으로 둔다."""
    path = get_keyword_excel_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if os.path.exists(path):
        wb = load_workbook(path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Keywords"
        ws["A1"] = "키워드"
        ws["B1"] = "카테고리"
        ws["C1"] = "상태"

    per_title = isinstance(category, (list, tuple))
    if per_title:
        if len(category) != len(titles):
            raise ValueError("titles와 카테고리 목록의 길이가 다릅니다.")
        cats = [str(c).strip() if c not in (None, "") else "" for c in category]
        used_category = ", ".join(sorted({c for c in cats if c}))
    else:
        cats = None
        used_category = category.strip() if category and category.strip() else ""
        if not used_category:
            for r in range(ws.max_row, 1, -1):
                v = ws.cell(row=r, column=2).value
                if v not in (None, ""):
                    used_category = str(v)
                    break

    write_row = ws.max_row + 1 if ws.max_row >= 1 else 2
    for idx, title in enumerate(titles):
        ws.cell(row=write_row, column=1, value=title)
        ws.cell(row=write_row, column=2, value=(cats[idx] if per_title else used_category))
        # C열(상태)은 의도적으로 비워둔다 — 메인 포스팅 프로그램이 채움
        write_row += 1

    wb.save(path)
    wb.close()

    # ✅ [2026-09-05] 통합 키워드 파일 dual-write - 원본 파일에 실제로 쓴
    # 값(title 원문 그대로, 카테고리)을 통합 파일에도 그대로 추가한다.
    # 통합 경로가 비어있거나 모듈이 없으면 조용히 건너뛴다(이 서브프로그램
    # 자체의 등록 흐름은 이미 위에서 끝났으므로 절대 영향받지 않음).
    if HAS_UNIFIED_MODULE:
        unified_path = get_unified_keyword_excel_path()
        if unified_path:
            ok, msg = append_titles_to_unified_keyword_excel(
                unified_path, titles, (cats if per_title else used_category), "복지로")
            if not ok:
                print(f"[통합 키워드 파일] {msg}")

    return used_category


# ============================================================
# 인포그래픽 프롬프트 생성
#   중앙부처/지자체 스키마가 달라(예: tgtrDtlCn ↔ sprtTrgtCn) 표시용으로
#   정규화한다. slctCritCn(선정기준)/alwServCn(혜택내용)은 두 API가 공통으로
#   쓰는 필드명이라 그대로 사용.
# ============================================================
def _extract_contact_info(detail: dict, source: str) -> str:
    """문의처(대표 연락처) 정보를 원문에서 뽑는다. 이 필드가 프롬프트에
    빠져 있으면 초안작성 프롬프트가 요구하는 "문의처" 소제목을 쓸 근거
    데이터 자체가 없어진다 — 실제로 발견된 버그. 중앙부처/지자체 API
    스키마가 달라 필드명이 다르므로 둘 다 시도한다. inqplCtadrList는
    dict 하나로 오는 경우도, list로 여러 건 오는 경우도 있어 둘 다
    처리한다."""
    contacts = []
    raw = detail.get("inqplCtadrList")
    items = raw if isinstance(raw, list) else ([raw] if isinstance(raw, dict) else [])
    for it in items:
        if not isinstance(it, dict):
            continue
        name = it.get("wlfareInfoReldNm") or it.get("servSeDetailNm") or ""
        num = it.get("wlfareInfoReldCn") or it.get("servSeDetailLink") or ""
        if num:
            contacts.append(f"{name}: {num}" if name else num)
    rprs = detail.get("rprsCtadr", "")
    if rprs and not any(rprs in c for c in contacts):
        contacts.append(f"대표문의처: {rprs}")
    return " / ".join(contacts)


def _extract_homepage_info(detail: dict) -> str:
    """관련 홈페이지(inqplHmpgReldList) 정보를 원문에서 뽑는다.
    2026-08-19 발견된 문제: 이 필드가 지금까지 어떤 프롬프트 빌더에도
    실리지 않고 있었다 — 첨부 서식자료가 없거나 부실한 서비스라도,
    이 필드에 담긴 "이 서비스를 관장하는 공식 누리집" 링크만 있으면
    LLM이 직접 열어(web_fetch) 정보를 보강할 수 있는데 그 기회 자체가
    프롬프트에서 원천적으로 막혀 있었다. inqplCtadrList와 마찬가지로
    dict 하나로 오는 경우도, list로 여러 건 오는 경우도 있어 둘 다
    처리한다. 지자체 스키마는 이 필드가 없거나 형태가 다를 수 있어
    존재하는 값만 최대한 관대하게 뽑는다."""
    links = []
    raw = detail.get("inqplHmpgReldList")
    items = raw if isinstance(raw, list) else ([raw] if isinstance(raw, dict) else [])
    for it in items:
        if not isinstance(it, dict):
            continue
        name = it.get("wlfareInfoReldNm") or it.get("servSeDetailNm") or ""
        url = it.get("wlfareInfoReldCn") or it.get("servSeDetailLink") or ""
        if url and url.startswith("http"):
            links.append(f"{name} {url}".strip() if name else url)
    return " / ".join(links)


def _fmt_ymd_korean(raw: str) -> str:
    """[Ver9.32] "20260315" → "2026년 3월 15일". 형식이 다르거나 비어 있으면 빈 문자열."""
    d = _parse_yyyymmdd(raw or "")
    return f"{d.year}년 {d.month}월 {d.day}일" if d else ""


def _format_date_lines(detail: dict, source: str) -> list:
    """[Ver9.32 신규] 프롬프트에 넣을 날짜 줄. 프롬프트를 API로 실행하면 모델이 오늘 날짜를
    모르므로, 연도가 없거나 상대적인 날짜("올해", "이달")를 쓰면 과거·미래가 뒤바뀌어
    표기됐다(정책뉴스에서 확인된 문제). 그래서 모델이 날짜를 계산하지 않도록 프로그램이
    연도까지 확정된 값만 넘긴다.
      - 작성 기준일: 이 프롬프트를 복사한 날(프로그램 시계) — "최근 개정" 검색 연도 기준
      - 기준연도(crtrYr)·최종 수정일(lastModYmd)·시행 시작/종료일(enfcBgngYmd/enfcEndYmd):
        API 원문에 값이 있을 때만
    프롬프트(초안작성 V7·2차각색 V4 등)는 이 줄에 있는 날짜만 기준일로 쓰도록 되어 있다."""
    today = datetime.date.today()
    lines = [f"작성 기준일: {today.year}년 {today.month}월 {today.day}일 (프로그램이 넣은 오늘 날짜)"]
    if source == "허브":
        return lines
    yr = str(detail.get("crtrYr", "") or "").strip()
    if re.fullmatch(r"\d{4}", yr):
        lines.append(f"기준연도(원문): {yr}년")
    for key, label in (("lastModYmd", "최종 수정일(원문)"),
                       ("enfcBgngYmd", "시행 시작일(원문)"),
                       ("enfcEndYmd", "시행 종료일(원문)")):
        v = _fmt_ymd_korean(str(detail.get(key, "") or ""))
        if v:
            lines.append(f"{label}: {v}")
    return lines


def _format_service_origin_block(detail: dict, source: str) -> list:
    """[v7.20 신규] "## 서비스 원문 (...)" 아래에 들어갈 줄들을 만든다.
    build_value_judgment_package/build_prescreening_value_combo_package/
    build_draft_prompt_package/build_final_adaptation_prompt_package/
    build_claude_second_stage_prompt_package 5곳이 전부 이 조립을
    거의 그대로 반복하고 있었어서(source=="허브" 분기를 5곳에 따로
    넣으면 하나라도 놓치기 쉬움) 공통 헬퍼로 뽑았다. "서비스명:" 줄은
    호출부가 이미 먼저 append하므로 여기 포함하지 않는다."""
    lines = []
    if source == "허브":
        # 허브(종합) 항목은 bokjiro API 필드가 없다 — 사람이
        # create_hub_service()로 직접 넣은 raw_text(여러 서비스를 종합한
        # 원고 전체)를 그대로 싣는다. 지원대상/선정기준 등으로 도로
        # 쪼개지 않는다 — 애초에 사람이 이미 종합 판단을 마친 글이므로.
        lines.append(f"원문:\n{detail.get('raw_text', '')}")
        lines.extend(_format_date_lines(detail, source))   # [Ver9.32]
        return lines
    fields = _normalize_detail_for_prompt(detail, source)
    lines.append(f"지원대상: {fields['target']}")
    lines.append(f"선정기준: {fields['criteria']}")
    lines.append(f"지원내용/혜택: {fields['benefit']}")
    lines.append(f"신청방법: {fields['apply_method']}")
    if fields["region"]:
        lines.append(f"지역: {fields['region']}")
    lines.append(f"지원주기: {detail.get('sprtCycNm', '')}")
    if fields["contact"]:
        lines.append(f"문의처: {fields['contact']}")
    if fields["homepage"]:
        lines.append(f"관련 홈페이지: {fields['homepage']}")
    lines.extend(_format_date_lines(detail, source))   # [Ver9.32]
    return lines


def _normalize_detail_for_prompt(detail: dict, source: str) -> dict:
    if source == "지자체":
        target = detail.get("sprtTrgtCn", "")
        apply_method = detail.get("aplyMtdCn", "")
        region = " ".join(x for x in [detail.get("ctpvNm", ""), detail.get("sggNm", "")] if x)
    else:
        target = detail.get("tgtrDtlCn", "")
        apply_method = ""
        forms = detail.get("applmetList", [])
        if isinstance(forms, dict):
            forms = [forms]
        for f in forms:
            if f.get("servSeDetailLink"):
                apply_method = f["servSeDetailLink"]
                break
        region = ""
    return {
        "target": target,
        "criteria": detail.get("slctCritCn", ""),
        "benefit": detail.get("alwServCn", ""),
        "apply_method": apply_method,
        "region": region,
        "contact": _extract_contact_info(detail, source),
        "homepage": _extract_homepage_info(detail),
    }


def extract_core_keyword_from_value_judgment(text: str) -> str:
    """가치판단 결과 텍스트에서 "핵심 키워드: ..." 줄을 찾아 값만 뽑는다.
    가치판단 프롬프트 [2단계] 출력 형식("핵심 키워드: (1개)")을 그대로
    따른다. 못 찾으면 빈 문자열을 돌려준다(호출부에서 다른 값으로
    대체)."""
    if not text:
        return ""
    m = re.search(r"핵심\s*키워드\s*[:：]\s*(.+)", text)
    return m.group(1).strip() if m else ""


def build_infographic_prompt(serv_id: str, serv_nm: str, fallback_keyword: str = "") -> str:
    """인포그래픽 기획 프롬프트(프롬프트 C')를 만든다.

    이 프롬프트는 원문(API 데이터)이 아니라 "완성된 최종 글"(2차
    각색/최종각색 결과)을 분석해서 썸네일·인포그래픽을 기획하는 방식으로
    설계되어 있다 — 그래서 detail.json의 원문 필드 대신, 저장해둔
    최종각색 결과 전체와(있으면) 가치판단 단계의 핵심 키워드를 입력값으로
    넣는다. 최종각색 결과가 저장되어 있지 않으면 만들 수 없으므로
    ValueError를 발생시킨다(호출부에서 안내 메시지로 처리)."""
    final_text = get_final_adaptation_text_for_use(serv_id, serv_nm)
    if not final_text:
        raise ValueError(
            f"'{serv_nm}'에는 저장된 최종각색 결과가 없습니다.\n\n"
            f"이 인포그래픽 프롬프트는 완성된 최종 글(2차 각색 결과)을 "
            f"분석해서 기획하는 방식이라, 먼저 4)포스팅 관리 탭 STEP 4에서 최종각색 "
            f"프롬프트 복사 → 최종각색 결과 저장을 진행해야 합니다."
        )

    keyword = (
        extract_core_keyword_from_value_judgment(get_stage_output(serv_id, "value_judgment"))
        or fallback_keyword
        or serv_nm
    )

    instructions = get_prompt_infographic_instructions()

    input_section = f"""[아래는 실제 입력값입니다]

## 최종각색 결과(2차 각색 완성본) 전체

{final_text}

## 가치판단 단계의 핵심 키워드 1개

{keyword}
"""
    return f"{instructions}\n\n{input_section}"


# ============================================================
# 2단계 키워드 리서치 — 2-A(자동완성) / 2-B(검색광고 API 검색량) /
# 2-C(블로그 검색 결과 제목 분석)
#   여기서 만든 데이터는 사람이 매번 검색하는 대신, 아래 가치판단
#   프롬프트에 "이미 확인된 자료"로 실어서 LLM에 넘긴다. LLM이 직접
#   검색하지 않고 이 데이터를 해석만 하도록 설계했다(속도/안정성 목적).
# ============================================================
RESEARCH_CACHE_FILE_NAME = "keyword_research.json"


def get_research_cache_path() -> str:
    return os.path.join(DATA_DIR, RESEARCH_CACHE_FILE_NAME)


def load_research_cache() -> dict:
    path = get_research_cache_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_research_cache(cache: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_research_cache_path(), "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def get_cached_research(keyword: str):
    return load_research_cache().get(keyword)


def set_cached_research(keyword: str, data: dict):
    cache = load_research_cache()
    cache[keyword] = data
    save_research_cache(cache)


# ------------------------------------------------------------------
# 2-A. 네이버 자동완성 (인증 불필요, 사실상 무제한)
# ------------------------------------------------------------------
def fetch_naver_autocomplete(keyword: str) -> list:
    """검색창 자동완성 목록. 개수가 많을수록 검색량이 많다는 신호로 쓴다
    (블랙키위 실측으로 상관관계 확인됨: 디딤돌대출 11개 vs 이주배경청소년 2개)."""
    url = "https://ac.search.naver.com/nx/ac"
    params = {
        "q": keyword, "con": 0, "frm": "nv", "ans": 2, "r_format": "json",
        "r_enc": "UTF-8", "r_unicode": 0, "t_koreng": 1, "run": 2, "rev": 4,
        "q_enc": "UTF-8", "st": 100,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    suggestions = []
    for group in data.get("items", []):
        for entry in group:
            if entry and entry[0]:
                suggestions.append(entry[0])
    return suggestions


# ------------------------------------------------------------------
# 2-B. 네이버 검색광고 API 연관키워드 (월간검색량, 경쟁정도) — HMAC 서명 필요
# ------------------------------------------------------------------
def _naver_ad_signature(timestamp: str, method: str, uri: str, secret_key: str) -> str:
    import hmac
    import hashlib
    import base64
    message = f"{timestamp}.{method}.{uri}"
    digest = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def fetch_naver_ad_related_keywords(keyword: str, api_key: str, secret_key: str, customer_id: str) -> dict:
    """네이버 검색광고 API 연관키워드 조회 (무료 제공). PC/모바일 월간검색량,
    경쟁정도를 돌려준다. 인증정보가 없으면 호출하지 않고 None을 반환하도록
    호출부에서 미리 체크한다.

    주의: hintKeywords 파라미터는 띄어쓰기가 있으면 400 Bad Request를
    반환한다(이 API의 알려진 제약) — 그래서 공백을 제거한 값으로 요청하고,
    화면에는 원래 키워드 그대로 보여준다."""
    uri = "/keywordstool"
    timestamp = str(int(time.time() * 1000))
    signature = _naver_ad_signature(timestamp, "GET", uri, secret_key)
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key,
        "X-Customer": str(customer_id),
        "X-Signature": signature,
    }
    keyword_no_space = keyword.replace(" ", "")
    params = {"hintKeywords": keyword_no_space, "showDetail": 1}
    resp = requests.get(f"https://api.searchad.naver.com{uri}", headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    for item in data.get("keywordList", []):
        if item.get("relKeyword", "").replace(" ", "") == keyword_no_space:
            return item
    # 정확히 일치하는 항목이 없으면 첫 번째 결과(가장 유사한 연관키워드)를 대신 반환
    items = data.get("keywordList", [])
    return items[0] if items else {}


# ------------------------------------------------------------------
# 2-C. 네이버 오픈API 블로그검색으로 상위 제목 수집 + 포화도 분석
# ------------------------------------------------------------------
def _strip_html_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "")


def fetch_naver_blog_search(keyword: str, client_id: str, client_secret: str, display: int = 30) -> list:
    """오픈API 블로그검색(sort=sim). 실제 블로그탭 화면 순서와 100% 일치하진
    않지만, 제목 텍스트 코퍼스를 빠르게 대량으로 모으는 용도로는 충분하다.
    반환: [{"title":.., "link":.., "bloggerlink":.., "postdate":..}, ...]"""
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params = {"query": keyword, "display": min(display, 100), "sort": "sim"}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    items = []
    for item in data.get("items", []):
        items.append({
            "title": _strip_html_tags(item.get("title", "")),
            "link": item.get("link", ""),
            "bloggerlink": item.get("bloggerlink", ""),
            "postdate": item.get("postdate", ""),
        })
    return items


# 실용가이드형 신호 vs PR/뉴스형 신호 (제목 텍스트 기반 휴리스틱 분류 —
# 100% 정확하진 않지만 1차 필터로는 충분하고, 애매한 것만 최종적으로
# 사람이 상위 10개 원문 제목을 보고 판단하면 된다)
_GUIDE_SIGNAL_WORDS = ["총정리", "완벽정리", "가이드", "신청방법", "조건", "혜택",
                        "한도", "자격", "총정리", "정리", "총평", "비교", "후기", "체크리스트"]
_PR_SIGNAL_WORDS = ["개최", "협약", "성과", "브리핑", "추진", "출범", "간담회",
                     "참석", "위원회", "정책 마련", "제고", "포럼", "행사"]


def classify_blog_title(title: str) -> str:
    guide_hit = any(w in title for w in _GUIDE_SIGNAL_WORDS)
    pr_hit = any(w in title for w in _PR_SIGNAL_WORDS)
    if guide_hit and not pr_hit:
        return "실용가이드형"
    if pr_hit and not guide_hit:
        return "PR/뉴스형"
    if guide_hit and pr_hit:
        return "혼합"
    return "미상"


def extract_title_combinations(titles: list, base_keyword: str, top_n: int = 8) -> list:
    """제목에서 base_keyword와 연도 숫자를 뗀 나머지를 토큰화해서, 자주 붙는
    조합(포화된 표현) 빈도를 센다. 반환: [(단어, 등장횟수), ...] 빈도 높은 순."""
    from collections import Counter
    counter = Counter()
    base_norm = re.sub(r"\s+", "", base_keyword)
    for title in titles:
        cleaned = re.sub(r"(19|20)\d{2}년?", "", title)
        cleaned = cleaned.replace(base_keyword, "").replace(base_norm, "")
        tokens = re.split(r"[\s|/\-,·・\[\]()]+", cleaned)
        for tok in tokens:
            tok = tok.strip()
            if len(tok) >= 2 and not tok.isdigit():
                counter[tok] += 1
    return counter.most_common(top_n)


def run_keyword_research(keyword: str, log_fn=None) -> dict:
    """2-A/B/C를 전부 실행해서 결과를 하나로 합친다. API 키가 없는 항목은
    건너뛰고 skipped 사유를 남긴다(있는 데이터만으로도 가치판단 가능하도록)."""
    log_fn = log_fn or (lambda msg: None)
    keys = get_research_api_keys()
    result = {
        "keyword": keyword,
        "researched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "autocomplete": [],
        "ad_data": None,
        "ad_skipped_reason": "",
        "blog_titles": [],
        "blog_skipped_reason": "",
        "top10_classification": {},
        "combinations": [],
    }

    # 2-A
    try:
        result["autocomplete"] = fetch_naver_autocomplete(keyword)
        log_fn(f"  [2-A] 자동완성 {len(result['autocomplete'])}개 확인")
    except Exception as e:
        log_fn(f"  [2-A] 자동완성 조회 실패: {e}")

    # 2-B
    if keys["naver_ad_api_key"] and keys["naver_ad_secret_key"] and keys["naver_ad_customer_id"]:
        try:
            result["ad_data"] = fetch_naver_ad_related_keywords(
                keyword, keys["naver_ad_api_key"], keys["naver_ad_secret_key"], keys["naver_ad_customer_id"]
            )
            log_fn(f"  [2-B] 검색광고 API 조회 완료")
        except Exception as e:
            result["ad_skipped_reason"] = str(e)
            log_fn(f"  [2-B] 검색광고 API 조회 실패: {e}")
    else:
        result["ad_skipped_reason"] = "API 인증정보 미설정 (설정 탭에서 등록)"

    # 2-C
    if keys["naver_openapi_client_id"] and keys["naver_openapi_client_secret"]:
        try:
            blog_items = fetch_naver_blog_search(
                keyword, keys["naver_openapi_client_id"], keys["naver_openapi_client_secret"], display=30
            )
            result["blog_titles"] = blog_items
            titles = [b["title"] for b in blog_items]

            top10 = titles[:10]
            rest = titles[10:]
            top10_types = [classify_blog_title(t) for t in top10]
            result["top10_classification"] = {
                "실용가이드형": top10_types.count("실용가이드형"),
                "PR/뉴스형": top10_types.count("PR/뉴스형"),
                "혼합": top10_types.count("혼합"),
                "미상": top10_types.count("미상"),
                "전체건수": len(titles),
                "상위10개제목": top10,
                "11~30위제목": rest,
            }
            result["combinations"] = extract_title_combinations(titles, keyword)
            log_fn(f"  [2-C] 블로그 검색결과 {len(titles)}건 수집, "
                   f"상위10개 중 실용가이드형 {result['top10_classification']['실용가이드형']}건")
        except Exception as e:
            result["blog_skipped_reason"] = str(e)
            log_fn(f"  [2-C] 블로그 검색 실패: {e}")
    else:
        result["blog_skipped_reason"] = "네이버 오픈API 인증정보 미설정 (설정 탭에서 등록)"

    return result


# [Ver10.02] 제목의 구분 쉼표. "1,200만 원"처럼 숫자 사이에 낀 천 단위 쉼표는 구분 쉼표로 보지 않는다.
_TITLE_COMMA_RE = re.compile(r"(?<!\d)[,，、]|[,，、](?!\d)")

# [Ver10.06] 통합 V9 제목 앞부분의 작은따옴표 속마음 후킹(정책뉴스 Ver10.06 policy_title_hook과 같음).
TITLE_HOOK_VISIBLE_LEN = 25
_TITLE_HOOK_RE = re.compile(r"['‘’\"“”][^'‘’\"“”,，]{1,20}['‘’\"“”](?:\s*(?:\.{2,}|…))?")

def tchk_title_hook(title: str):
    """제목 첫 쉼표 앞의 작은따옴표 후킹 (문구, 끝 위치). 없으면 ("", -1)."""
    t = (title or "").strip()
    m = _TITLE_COMMA_RE.search(t)
    front = t[:m.start()] if m else t
    h = _TITLE_HOOK_RE.search(front)
    if not h:
        return "", -1
    return h.group(0), h.end()

def tchk_strip_title_hook(text: str) -> str:
    """검색·점수용: 따옴표 후킹을 빼고 공백을 정리한다(후킹이 없으면 그대로)."""
    out = _TITLE_HOOK_RE.sub(" ", text or "")
    return re.sub(r"\s+", " ", out).strip()

def tchk_split_title_front(title: str) -> str:
    """[Ver9.19 신규, Ver9.29 주석 갱신] 제목의 "앞 핵심구"를 자른다. 프롬프트A V17 제목 구조가
    "[메인 + 서브 + 변화], [롱테일 + 세부사항]"이므로(V16은 "[본문 핵심 키워드 + 변화], [서브 키워드]")
    첫 콤마 앞이 앞 핵심구다. 콤마가 없으면 앞 30자 안쪽(어절 단위)으로 자른다."""
    t = (title or "").strip().rstrip("?？!！. ").strip()
    m = _TITLE_COMMA_RE.search(t)
    if m:
        # [Ver10.06] 앞부분의 작은따옴표 속마음 후킹은 검색어가 아니므로 빼고 메인·서브만 쓴다.
        front = tchk_strip_title_hook(t[:m.start()])
        if len(front) >= 4:
            return front
    t = tchk_strip_title_hook(t)
    if len(t) <= 30:
        return t
    cut = t[:30]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp >= 8 else cut).strip()

def tchk_split_title_back(title: str) -> str:
    """[Ver9.26 신규] 제목의 첫 쉼표 뒤 구절(뒷구). 쉼표가 없거나 4자 미만이면 빈 문자열.
    앞구(tchk_split_title_front)는 선점용이라 검색이 거의 없고 실제 유입은 뒷구가 받는다."""
    t = (title or "").strip().rstrip("?？!！. ").strip()
    m = _TITLE_COMMA_RE.search(t)
    if not m:
        return ""
    back = t[m.end():].strip()
    return back if len(back) >= 4 else ""

def parse_value_judgment_title_candidates(text: str) -> list:
    """[v7.17 신규, v7.19에서 형식 갱신, v7.21에서 헤더 매칭 완화]
    가치판단(또는 사전스크리닝+가치판단 통합) 프롬프트의 [2-A단계]
    제목 후보 섹션에서 후보를 뽑는다. 최대 4개. 반환값은
    [{"title": str, "intro": str}, ...] — intro는 "도입부 첫 문장
    지시" 한 줄(없으면 빈 문자열).

    가치판단 V4에서 출력 형식이 번호 목록("1. .../2. .../(선택) 3. ...")
    에서 정책뉴스의 [도입부 연결 지시]를 이식한 후보별 블록
    ("[후보 N]\\n제목: ...\\n도입부 첫 문장 지시: ...")으로 바뀌었다.
    이 함수는 새 블록 형식을 먼저 시도하고, 못 찾으면(구버전 가치판단
    결과가 저장돼 있는 경우 등) 예전 번호 목록 형식으로 폴백한다 —
    intro는 이 경우 항상 빈 문자열이 된다(구버전 출력엔 애초에 그
    정보가 없으므로).

    [v7.21 수정] 헤더 앵커가 "## 제목 후보"만 인식해, 프롬프트가
    지시한 출력 형식("## 제목 후보")과 실제 Claude 응답("[2-A단계]
    제목 후보" — 프롬프트 안의 섹션 제목을 그대로 헤더로 써버린 경우)
    이 어긋나면 후보를 통째로 못 찾는 문제가 실사용 사례로 확인됨.
    "##"·"[2-A단계]"(뒤에 "생성"이 붙어도) 등 흔한 변형을 전부
    허용하도록 앵커를 완화했다 — 정확한 헤더 문구 대신 "그 줄에
    '제목'과 '후보'가 순서대로 있는가"만으로 섹션 시작을 찾는다."""
    m = re.search(
        r"^[ \t]*(?:#{1,3}\s*)?(?:\[[^\]]*\]\s*)?제목\s*후보(?:\s*생성)?[ \t]*$"
        r"\n(.*?)(?:\n\s*\n\s*[─-]|\n\s*\n##|\Z)",
        text, re.S | re.M,
    )
    if not m:
        return []
    block = m
    body = block.group(1)

    # 새 블록 형식: "[후보 N]" 헤더 아래 "제목:"·"도입부 첫 문장 지시:" 줄
    cand_blocks = re.split(r"\n(?=\s*(?:\(?선택\)?\s*)?\[\s*후보\s*\d+\s*\])", body)
    candidates = []
    for cb in cand_blocks:
        if not re.search(r"\[\s*후보\s*\d+\s*\]", cb):
            continue
        m_title = re.search(r"제목\s*[:：]\s*(.+)", cb)
        if not m_title:
            continue
        title = m_title.group(1).strip().strip("`\"'").strip()
        m_intro = re.search(r"도입부\s*첫\s*문장\s*지시\s*[:：]\s*(.+)", cb)
        intro = m_intro.group(1).strip() if m_intro else ""
        # [Ver9.30] 가치판단 V8 후보 블록의 "롱테일 축:"·"선택 근거:" 줄(없으면 빈 문자열)
        m_lt = re.search(r"롱테일\s*축\s*[:：]\s*(.+)", cb)
        m_rs = re.search(r"선택\s*근거\s*[:：]\s*(.+)", cb)
        if title and title not in [c["title"] for c in candidates]:
            candidates.append({"title": title, "intro": intro,
                               "longtail": m_lt.group(1).strip() if m_lt else "",
                               "reason": m_rs.group(1).strip() if m_rs else ""})
    if candidates:
        return candidates[:4]

    # 구버전 폴백: 번호 목록 형식 ("1. .../2. .../(선택) 3. ...")
    for line in body.splitlines():
        line = line.strip()
        m = re.match(r"^(?:\(?선택\)?\s*)?\d+[.\)]\s*(.+)$", line)
        if m:
            title = m.group(1).strip().strip("`\"'").strip()
            if title and title not in [c["title"] for c in candidates]:
                candidates.append({"title": title, "intro": "", "longtail": "", "reason": ""})
    return candidates[:4]


# [v7.17 신규] 서비스별로 확정된 제목을 저장 — 확정되면 build_draft_
# prompt_package()가 초안작성 프롬프트에 "## 확정된 제목" 섹션으로
# 함께 실어 보내고, 초안작성 프롬프트 V4는 이게 있으면 그대로 받아써서
# 스스로 새 제목을 짓지 않는다(정책뉴스 A→B 관계와 동일).
CONFIRMED_TITLE_FILE_NAME = "confirmed_titles.json"


def get_confirmed_title_path() -> str:
    return os.path.join(DATA_DIR, CONFIRMED_TITLE_FILE_NAME)


def load_confirmed_titles() -> dict:
    path = get_confirmed_title_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_confirmed_title(serv_id: str, title: str, intro: str = ""):
    data = load_confirmed_titles()
    data[serv_id] = {
        "title": title,
        "intro": intro,
        "confirmed_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_confirmed_title_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_confirmed_title(serv_id: str):
    d = load_confirmed_titles().get(serv_id)
    return d["title"] if d else None


def get_confirmed_title_intro(serv_id: str) -> str:
    """[v7.19 신규] 확정된 제목과 함께 저장된 "도입부 첫 문장 지시"를
    반환한다. 없으면(구버전에 저장된 확정 제목이거나, 확정 당시
    가치판단 결과에 지시가 없었던 경우) 빈 문자열."""
    d = load_confirmed_titles().get(serv_id)
    return d.get("intro", "") if d else ""


def extract_research_request_keywords(text: str) -> str:
    """[v7.18 신규, v7.4의 parse_value_judgment_keyword_candidates()를
    대체] 가치판단(또는 사전스크리닝+가치판단 통합) 결과에서 "재조사
    요청 키워드: ..." 줄만 뽑아 콤마로 이어붙인 문자열 하나로 돌려준다
    (research_keyword_var에 그대로 넣을 수 있는 형태). 0-1단계 조합형
    케이스와 2단계 둘 다에서 나올 수 있어 두 번 등장할 수 있으므로
    전부 훑어 중복 없이 합친다.

    [v7.4→v7.18 정정] 이전엔 이 자리에 "핵심 키워드"·"참고용 키워드
    후보"까지 모아 정책뉴스 STEP4처럼 라디오버튼+자동 사전체크로
    고르게 했었는데, 정책뉴스 STEP1.5(키워드 리서치) 자체엔 그런
    후보 선택 UI가 없다는 지적을 받고 정정했다 — A가 이미 특정해서
    요청한 키워드라 사람이 여러 후보 중 고를 일이 없으므로, 재조사
    요청 키워드만 그대로 채워 넣으면 충분하다. 후보를 실측 검색해
    등급 매기는 구조는 정책뉴스에서도 제목(STEP4)에만 있어, 그건
    parse_value_judgment_title_candidates()로 별도 유지한다."""
    parts = []
    for m in re.finditer(r"재조사\s*요청\s*키워드\s*:[ \t]*([^\n]*)", text):
        line = m.group(1).strip()
        # [Ver10.10] 통합 V13: 라벨 아래 작은 코드블럭에 콤마 한 줄. 예전 같은 줄 형식도 읽는다.
        if not line or line.startswith("```"):
            b = re.match(r"\s*```[^\n]*\n(.*?)\n\s*```", text[m.end():], re.S)
            if not b:
                continue
            line = " ".join(b.group(1).split("\n"))
        for p in re.split(r"[,/]", line):
            p = p.strip().strip("`\"'").strip()
            p = re.sub(r"\s*\(재조사\s*필요\)\s*", "", p).strip()
            if p and p not in parts:
                parts.append(p)
    return ", ".join(parts)


def format_research_for_prompt(research: dict, original_name: str = "") -> str:
    """리서치 결과를 가치판단 프롬프트에 그대로 붙여넣을 텍스트 블록으로 변환.

    original_name(서비스 원문의 정식 명칭)을 함께 받아, 검색량 확보를
    위해 사용자가 정책명을 축약/변형해서 리서치한 경우(예: "건강보험
    면제 지원" -> "건강보험 면제") 검색 키워드가 원본 서비스명과 다르다는
    사실과 그 이유를 명시적으로 알려준다. 이 설명이 없으면 LLM이 왜
    키워드가 서비스명과 다른지(오타인지, 별개 항목인지) 헷갈릴 수 있어
    v5.9에서 추가함(사용자 피드백: "오리지널 키워드와 검색한 키워드
    정보 둘 다 주는 게 좋겠지?")."""
    keyword = research.get("keyword", "")
    lines = [f"### 키워드: {keyword}  (조사 시각: {research['researched_at']})"]
    if original_name and keyword and original_name.strip() != keyword.strip():
        lines.append(
            f"  ※ 원본 서비스명은 \"{original_name}\"이며, 검색량이 잘 안 잡히는 "
            f"긴 정책명 특성상 핵심만 남긴 \"{keyword}\"로 리서치했습니다. "
            f"아래 리서치 데이터는 같은 정책에 대한 것이니 참고해 판단해주세요."
        )
    lines.append("")

    lines.append("**[2-A] 자동완성 결과**")
    if research["autocomplete"]:
        lines.append(f"- {len(research['autocomplete'])}개: " + ", ".join(research["autocomplete"][:15]))
    else:
        lines.append("- (자동완성 없음 또는 조회 실패 — 검색량이 거의 없다는 신호일 수 있음)")
    lines.append("")

    lines.append("**[2-B] 검색광고 API 검색량**")
    ad = research.get("ad_data")
    if ad:
        pc = ad.get("monthlyPcQcCnt", "?")
        mobile = ad.get("monthlyMobileQcCnt", "?")
        comp = ad.get("compIdx", "?")
        lines.append(f"- 월간검색량 PC {pc} / 모바일 {mobile}, 경쟁정도 {comp}")
    else:
        lines.append(f"- 미확인 ({research.get('ad_skipped_reason', '사유 불명')})")
    lines.append("")

    lines.append("**[2-C] 블로그 검색결과 상위 제목 분석**")
    cls = research.get("top10_classification")
    if cls:
        lines.append(
            f"- 전체 검색결과 {cls['전체건수']}건 중 상위 10개 분류: "
            f"실용가이드형 {cls['실용가이드형']} / PR·뉴스형 {cls['PR/뉴스형']} / "
            f"혼합 {cls['혼합']} / 미상 {cls['미상']}"
        )
        lines.append("- 상위 10개 제목 원문:")
        for i, t in enumerate(cls["상위10개제목"], 1):
            lines.append(f"  {i}. {t}")
        if research.get("combinations"):
            combo_str = ", ".join(f"{w}({c}회)" for w, c in research["combinations"])
            lines.append(f"- 자주 등장하는 제목 조합(포화 표현): {combo_str}")
    else:
        lines.append(f"- 미확인 ({research.get('blog_skipped_reason', '사유 불명')})")
    lines.append("")

    return "\n".join(lines)


def run_keyword_research_multi(keywords: list, log_fn=None) -> list:
    """[v6.9 신규] 콤마로 구분해 입력한 키워드 후보 여러 개를 각각
    run_keyword_research()로 실행해 리스트로 반환한다(정책뉴스 프로그램
    Ver8.16에서 착안). 정식명과 약칭이 함께 쓰이는 서비스(예: "국민취업
    지원제도" vs "국취제")가 있어, 어느 표현이 실제로 더 많이 검색되는지
    나란히 비교하고 싶을 때 쓴다.

    복지로는 이미 research_map(키워드 -> 리서치 결과 dict)이 여러 개의
    항목을 자연스럽게 받는 범용 구조로 설계돼 있어(build_value_judgment_
    package 등 모든 builder가 research_map.items()를 순회), 정책뉴스처럼
    별도의 "is_multi" 래핑 구조나 전용 포맷 함수가 필요 없다 — 이 함수가
    반환한 결과를 키워드별로 set_cached_research()에 개별 저장하기만
    하면, 기존 research_map 조립 로직이 그대로 여러 항목을 처리한다."""
    log_fn = log_fn or (lambda msg: None)
    results = []
    for kw in keywords:
        log_fn(f"── '{kw}' 리서치 시작 ──")
        results.append(run_keyword_research(kw, log_fn=log_fn))
    return results


def format_research_summary_only(items: list) -> str:
    """[v7.0 신규, 정책뉴스 Ver8.22에서 이식] run_keyword_research_multi()의
    결과에서 "검색량·자동완성"만 뽑아 키워드별 블록으로 정리한다.
    가치판단 프롬프트에 붙는 format_research_for_prompt()(블로그 상위
    제목 분석 등 풀 데이터 포함)와는 완전히 별개 용도 — 이건 추가 키워드
    검색(다른 소재 아이디어를 찾을 때 등)에 바로 붙여넣기 위한 간단
    요약이다. 맨 하단에 조회한 키워드만 콤마로 구분해 나열하는 줄도
    추가 — 다른 검색창 등에 키워드만 빠르게 붙여넣고 싶을 때 쓴다."""
    if not items:
        return ""
    blocks = []
    for r in items:
        kw = r.get("keyword", "")
        ad = r.get("ad_data")
        if ad:
            search_line = (f"- 검색량: PC {ad.get('monthlyPcQcCnt','?')} / "
                            f"모바일 {ad.get('monthlyMobileQcCnt','?')}")
        else:
            search_line = f"- 검색량: 미확인 ({r.get('ad_skipped_reason','사유 불명')})"
        autocomplete = r.get("autocomplete") or []
        if autocomplete:
            auto_line = "- 자동완성: " + ", ".join(autocomplete)
        else:
            auto_line = "- 자동완성: 없음 또는 조회 실패"
        blocks.append(f"[{kw}]\n{search_line}\n{auto_line}")

    kw_list = ", ".join(r.get("keyword", "") for r in items if r.get("keyword"))
    if kw_list:
        blocks.append(f"키워드: {kw_list}")

    return "\n\n".join(blocks)


# ============================================================
# 가치판단 프롬프트 (정책뉴스/지식인 프로그램의 0~3단계 구조를 복지로
# 데이터에 맞게 이식. 차이점: 이 프로그램은 LLM이 직접 검색하지 않고,
# 위에서 미리 수집한 2-A/B/C 리서치 데이터를 "이미 확인된 자료"로 받아
# 해석만 한다.)
# ============================================================


def list_attachment_files(folder: str) -> list:
    """서비스 폴더 안의 attachments/ 하위 파일 목록을 돌려준다. 없으면 빈 리스트."""
    attach_dir = os.path.join(folder, "attachments")
    if not os.path.isdir(attach_dir):
        return []
    return sorted(f for f in os.listdir(attach_dir) if os.path.isfile(os.path.join(attach_dir, f)))


# [v7.13 신규] _refresh_posting_tree()가 행마다 list_attachment_files()
# (os.listdir + 파일마다 os.path.isfile)를 매번 다시 돌던 게, 같은
# shared_rows를 쓰는 listing_tree/history_tree엔 없는 실제 디스크 I/O라
# 포스팅 관리 탭만 유독 느린 원인이었다(사용자 리포트: "포스팅관리탭의
# 리스트만 늦게 나왔어"). attachments 폴더의 mtime이 그대로면(=파일이
# 추가/삭제된 적 없으면) 다시 os.listdir()하지 않고 캐시를 그대로
# 쓴다 — os.path.getmtime() 한 번(가벼운 stat 호출)으로 변경 여부만
# 확인하므로, 사용자가 탐색기에서 파일을 직접 넣고 빼도 정확하다.
_ATTACH_COUNT_CACHE = {}  # folder -> (attachments_dir_mtime_또는_None, count)


def get_attachment_count_cached(folder: str) -> int:
    attach_dir = os.path.join(folder, "attachments")
    try:
        mtime = os.path.getmtime(attach_dir)
    except OSError:
        mtime = None
    cached = _ATTACH_COUNT_CACHE.get(folder)
    if cached is not None and cached[0] == mtime:
        return cached[1]
    count = len(list_attachment_files(folder))
    _ATTACH_COUNT_CACHE[folder] = (mtime, count)
    return count


def format_attachments_for_prompt(attachments: list) -> str:
    if attachments:
        lines = [f"## 첨부 서식자료 ({len(attachments)}건)\n",
                 "아래 파일이 자료 폴더의 attachments 폴더에 있습니다. 이 대화에 함께 "
                 "업로드했다면 반드시 읽고 내용을 반영해주세요. 아직 업로드하지 않았다면, "
                 "'📂 공식자료 폴더 열기' 버튼으로 폴더를 열어 파일을 끌어다 올려주신 뒤 "
                 "다시 요청해주세요."]
        for fn in attachments:
            lines.append(f"- {fn}")
        return "\n".join(lines)
    return ("## 첨부 서식자료\n\n"
            "이 서비스는 첨부 서식자료가 없습니다. 원문(지원대상/선정기준/혜택/신청방법)"
            "만으로 정보가 부족하면, 아래 지시문의 웹검색 보강 절차를 따라주세요.")


def _read_excel_titles_raw(path: str) -> list:
    """[Ver9.30] 키워드 엑셀(A열 "키워드" = 제목, 헤더 제외)의 제목을 원문 그대로 읽는다.
    통합 키워드 엑셀도 같은 스키마다. 파일이 없거나 못 읽으면 빈 리스트."""
    if not path or not HAS_OPENPYXL or not os.path.exists(path):
        return []
    try:
        wb = load_workbook(path, read_only=True)
        ws = wb.active
        out = [str(row[0]).strip() for row in ws.iter_rows(min_row=2, values_only=True)
               if row and row[0] not in (None, "")]
        wb.close()
        return out
    except Exception as e:
        print(f"[발행 이력] 엑셀 읽기 실패({path}): {e}")
        return []


def build_publish_history_note(exclude_serv_id: str = "") -> str:
    """[Ver9.30 신규] 가치판단 V8 [선택 입력](자기잠식 확인)용 발행 이력 블록.
    같은 블로그에 정책뉴스 글도 올라가므로, 복지로 확정 제목(confirmed_titles.json, 이번
    서비스 제외)과 키워드 엑셀·통합 키워드 엑셀(정책뉴스 등 다른 프로그램 글 포함)의 등록
    제목을 중복 없이 모은다. 모은 제목이 없으면 빈 문자열."""
    seen, lines = set(), []

    def add(title, src, date=""):
        t = (title or "").strip()
        key = normalize_keyword_for_match(t)
        if not t or key in seen:
            return
        seen.add(key)
        lines.append(f"- {t} ({src}{', ' + date if date else ''})")

    try:
        for sid, d in load_confirmed_titles().items():
            if sid != exclude_serv_id and isinstance(d, dict):
                add(d.get("title", ""), "복지로 확정", str(d.get("confirmed_at", ""))[:10])
    except Exception as e:
        print(f"[발행 이력] 확정 제목 읽기 실패: {e}")
    for t in _read_excel_titles_raw(get_keyword_excel_path()):
        add(t, "키워드 엑셀")
    for t in _read_excel_titles_raw(get_unified_keyword_excel_path()):
        add(t, "통합 키워드 엑셀")
    if not lines:
        return ""
    return ("## 발행 이력 — 자기잠식 확인용\n"
            f"(같은 블로그의 기존 글 제목 {len(lines)}건 — 복지로 확정 제목 + 키워드 엑셀 + 통합 키워드 "
            "엑셀(정책뉴스 등 다른 프로그램 글 포함). 프롬프트 [선택 입력] 참고)\n"
            + "\n".join(lines) + "\n")


def build_value_judgment_package(detail: dict, source: str, research_map: dict, attachments: list = None,
                                  serv_id: str = "") -> str:
    """서비스 원문 + 키워드 리서치 데이터 + 첨부파일 유무 + (있으면) ⓪
    사전스크리닝 결과 + 프롬프트를 하나로 묶어, Claude 웹에 그대로
    붙여넣을 수 있는 텍스트를 만든다. 프롬프트 본문은 PROMPT_DIR의 외부
    .md 파일에서 읽어온다."""
    parts = [get_prompt_value_judgment()]

    parts.append(f"## 서비스 원문 ({source})\n")
    parts.append(f"서비스명: {detail.get('servNm', '')}")
    parts.extend(_format_service_origin_block(detail, source))
    parts.append("")

    parts.append(format_attachments_for_prompt(attachments or []))
    parts.append("")

    if serv_id:
        parts.append(format_previous_stage_for_prompt("prescreening", serv_id))
        parts.append("")

    history = build_publish_history_note(serv_id)   # [Ver9.30] 자기잠식 확인용
    if history:
        parts.append(history)

    parts.append("## 키워드 리서치 데이터\n")
    if not research_map:
        parts.append("(아직 리서치를 실행하지 않았습니다 — '키워드 리서치 실행' 버튼을 먼저 눌러주세요)")
    else:
        for kw, research in research_map.items():
            parts.append(format_research_for_prompt(research, detail.get('servNm', '')))

    return "\n".join(parts)


def build_quick_judgment_package(detail: dict, source: str, attachments: list = None) -> str:
    """[Ver10.08] STEP 1 빠른 판정 = 짧은 프롬프트 + 서비스 원문 + 첨부파일 이름만(PDF·리서치·블로그 없음)."""
    parts = [get_prompt_quick_judgment_instructions()]
    parts.append(f"## 서비스 원문 ({source})\n")
    parts.append(f"서비스명: {detail.get('servNm', '')}")
    parts.extend(_format_service_origin_block(detail, source))
    parts.append("")
    if attachments:
        parts.append(f"## 첨부파일 이름 ({len(attachments)}건 — 이 단계에서는 올리지 않습니다)\n")
        parts.extend(f"- {fn}" for fn in attachments)
    else:
        parts.append("## 첨부파일 이름\n\n(첨부파일 없음)")
    return "\n".join(parts)


def parse_quick_judgment(text: str) -> dict:
    """[Ver10.08] 빠른 판정 결과에서 판정·돈 갈래·이유·필요 자료·리서치 키워드 줄을 읽는다.
    판정은 "진행"/"보류"/""(못 찾음), keywords는 콤마로 이은 한 줄("-"면 빈 문자열)."""
    def line(label):
        m = re.search(rf"^[ \t>*-]*{label}\s*:\s*(.+)$", text or "", re.M)
        return m.group(1).strip() if m else ""
    v = line("판정")
    verdict = "보류" if ("보류" in v and "진행" not in v) else ("진행" if ("진행" in v and "보류" not in v) else "")
    kws = split_keyword_line(_keyword_block(text or "", "리서치 키워드"))
    return {"verdict": verdict, "money": line("돈 갈래"), "reason": line("이유"),
            "attach": line("첨부 서식자료"), "blog": line("경쟁 블로그"), "keywords": ", ".join(kws)}


def check_source_line(text: str) -> list:
    """[Ver10.08] 최종 원고의 "출처:" 줄 점검. 없거나 블로그 주소·블로그 출처가 섞이면 경고 문장을 돌려준다."""
    lines = [ln for ln in (text or "").splitlines() if re.match(r"^\s*출처\s*:", ln)]
    if not lines:
        return ["\"출처:\" 줄이 없습니다 — 공식기관 출처가 반드시 있어야 합니다(2차각색 V10은 해시태그 앞에 한 줄)."]
    warns = []
    for ln in lines:
        if re.search(r"blog\.naver|m\.blog|tistory|cafe\.naver|cafe\.daum|brunch\.co|velog|블로그\s*[「(]", ln):
            warns.append(f"출처 줄에 블로그가 들어 있습니다 — 공식기관 자료만 출처로 씁니다:\n  {ln.strip()[:150]}")
        if re.search(r"(?:https?://)?[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}/\S", ln):  # [Ver10.13] 주소 앞부분을 떼도 잡게
            warns.append(f"출처 줄에 전체 주소가 있습니다 — 도메인까지만 씁니다:\n  {ln.strip()[:150]}")
    if "### 근거 출처" in (text or ""):
        warns.append("원고에 \"### 근거 출처\" 목록이 남아 있습니다 — 2차각색이 출처 줄로 바꿨어야 합니다.")
    return warns


# [Ver10.13] 본문 주소의 https://·http://·www. 를 뗀다 — 네이버 에디터는 "www."나 "http"로 시작하는
# 주소를 치면 자동으로 링크로 바꾸고 미리보기 카드를 늦게 끼워 넣어 줄이 깨진다(실제 사례:
# "www.lh.or.kr" 뒤 띄어쓰기가 사라지고 카드가 다음 주소 중간에 들어감). 하이퍼링크는 넣지 않는다(사용자).
_URL_PREFIX_PAT = re.compile(r"\b(?:https?://(?:www\.)?|www\.)(?=[A-Za-z0-9-]+\.[A-Za-z])", re.I)


def strip_url_prefixes(text: str) -> tuple:
    """본문 주소에서 https://·http://·www. 를 떼고 (새 본문, 뗀 곳 수)를 돌려준다."""
    return _URL_PREFIX_PAT.subn("", text or "")


def split_keyword_line(raw: str) -> list:
    """[Ver10.08] 키워드 여러 개를 하나씩 나눈다 — 콤마뿐 아니라 / · | 、 줄바꿈·목록 기호로 나눠 와도
    키워드 묶음 한 줄이 통째로 검색되지 않게 한다(연탄쿠폰 사례: "/"로 나뉜 줄이 한 키워드로 검색됨)."""
    kws = []
    for k in re.split(r"[,，/／·ㆍ|｜、;\n]", raw or ""):
        k = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", k)
        k = k.strip().strip("()（）[]`\"'“”‘’").strip()
        if k and k != "-" and k not in kws:
            kws.append(k)
    return kws


def _keyword_block(text: str, label: str) -> str:
    """"라벨: 값" 줄의 값. 값이 비고 다음 줄들이 목록(- 키워드)이면 그 목록까지 이어 붙인다."""
    m = re.search(rf"^[ \t>*-]*{label}[ \t]*:[ \t]*(.*)$", text, re.M)
    if not m:
        return ""
    val = m.group(1).strip()
    if val:
        return val
    out = []
    for ln in text[m.end():].splitlines()[1:]:
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+\S", ln):
            out.append(ln)
        elif ln.strip():
            break
    return "\n".join(out)


def strip_outer_code_fence(text: str) -> str:
    """[Ver10.08] 복사한 답이 ``` 코드블럭째면 바깥 울타리만 벗긴다(안쪽 내용은 그대로)."""
    t = (text or "").strip()
    m = re.match(r"^```[^\n]*\n(.*)\n```$", t, re.S)
    return m.group(1).strip() if m else t


def extract_research_request_block_keywords(text: str) -> str:
    """[Ver10.08] "## 키워드 리서치 요청" 아래 작은 코드블럭의 콤마 키워드 한 줄을 읽는다."""
    m = re.search(r"##\s*키워드 리서치 요청(.*)", text or "", re.S)
    if not m:
        return ""
    body = m.group(1)
    cb = re.search(r"```[^\n]*\n(.*?)\n?```", body, re.S)
    return ", ".join(split_keyword_line(cb.group(1).strip() if cb else ""))


def pick_competitor_blog_links(research, exclude_ids: list, n: int) -> list:
    """[Ver10.08] 리서치의 블로그 검색 결과(오픈API, 정확도순)에서 네이버 블로그 글 주소를 앞에서부터
    n개 고른다. 내 블로그(exclude_ids)와 같은 블로거의 두 번째 글은 뺀다. research에 리스트를 주면
    메인 키워드 결과부터 차례로 본다(메인 결과가 모자라면 다음 키워드 결과로 채움)."""
    out, seen = [], set()
    items = []
    for r in (research if isinstance(research, list) else [research]):
        items.extend((r or {}).get("blog_titles", []) or [])
    for it in items:
        link = (it.get("link") or "").strip()
        m = re.search(r"blog\.naver\.com/([^/?#]+)", link)
        if not m:
            continue
        bid = m.group(1).lower()
        if bid in exclude_ids or bid in seen:
            continue
        seen.add(bid)
        out.append(link)
        if len(out) >= n:
            break
    return out


def count_competitor_blogs(text: str) -> int:
    """경쟁 블로그 칸의 글 수 — "### 블로그 N" 머리줄 수(직접 붙여넣어 머리줄이 없으면 1)."""
    if not (text or "").strip():
        return 0
    return len(re.findall(r"^### 블로그 \d+", text, re.M)) or 1


def build_prescreening_value_combo_package(detail: dict, source: str, serv_id: str,
                                            research_map: dict, attachments: list = None,
                                            quick_judgment: str = "", competitor_blogs: str = "",
                                            include_origin: bool = True) -> str:
    """STEP 2 본 분석 = 통합(Claude) 프롬프트 + 빠른 판정 결과 + 원문 + 첨부파일 안내 + 키워드
    리서치 데이터 + 경쟁 블로그 샘플. 결과 형식이 가치판단 결과와 같아 "가치판단 결과 저장"으로 저장한다.

    [Ver10.08] 빠른 판정을 한 대화창에 이어 붙일 때는 include_origin=False로 원문을 뺀다(그 대화에
    이미 있음 — 통합 V11이 앞서 받은 원문을 쓴다). 경쟁 블로그 칸에 내용이 있으면 본문 그대로
    "## 경쟁 블로그 샘플 (N개)"로 붙여, 파일을 따로 첨부하지 않아도 [사전 스캔 절차] B가 돈다."""
    parts = [get_prompt_prescreening_value_combo_instructions()]

    if quick_judgment.strip():
        parts.append("## 빠른 판정 결과 (STEP 1)\n")
        parts.append(quick_judgment.strip())
        parts.append("")

    if include_origin:
        parts.append(f"## 서비스 원문 ({source})\n")
        parts.append(f"서비스명: {detail.get('servNm', '')}")
        parts.extend(_format_service_origin_block(detail, source))
    else:
        parts.append(f"(서비스 원문은 이 대화의 빠른 판정 때 보낸 것을 그대로 씁니다 — "
                     f"서비스명: {detail.get('servNm', '')})")
    parts.append("")

    parts.append(format_attachments_for_prompt(attachments or []))
    parts.append("")
    if not competitor_blogs.strip():
        parts.append("(참고) 경쟁 블로그 샘플은 이번 자료에 없습니다. 같은 키워드 상위 블로그 MD를 이 대화에 "
                     "첨부했다면 [사전 스캔 절차] B를 수행하고, 없으면 건너뜁니다.")
        parts.append("")

    history = build_publish_history_note(serv_id)   # [Ver9.30] 자기잠식 확인용
    if history:
        parts.append(history)

    parts.append("## 키워드 리서치 데이터\n")
    if not research_map:
        parts.append("(아직 리서치를 실행하지 않았습니다 — '키워드 리서치 실행' 버튼을 먼저 눌러주세요)")
    else:
        for kw, research in research_map.items():
            parts.append(format_research_for_prompt(research, detail.get('servNm', '')))

    if competitor_blogs.strip():
        parts.append("")
        parts.append(f"## 경쟁 블로그 샘플 ({count_competitor_blogs(competitor_blogs)}개)\n")
        parts.append("같은 키워드로 검색했을 때 상위 노출되는 블로그 글입니다(블로그 스크랩 본문 그대로). "
                     "**글 구성 참고용입니다 — 사실 근거·출처로 쓰지 않습니다.** [사전 스캔 절차] B대로 구성 "
                     "방식만 분석하고, 블로그의 숫자·사실은 인용하지 않으며, 공식 출처가 부족한 부분을 블로그로 "
                     "채우지 않습니다([공식 출처 확인]).\n")
        parts.append(competitor_blogs.strip())

    return "\n".join(parts)


def build_prescreening_prompt_package(row: dict, attachments: list = None, instructions_text: str = None) -> str:
    """⓪ 사전스크리닝 프롬프트 + 첨부파일 안내를 하나로 묶는다. 이 단계는
    detail.json의 텍스트 필드가 아니라 PDF 원문(공식 첨부자료 PDF +
    경쟁 블로그 샘플 MD)을 Gemini/Claude 대화창에 직접 첨부해서 분석하는
    방식이라, 여기서는 "어떤 파일을 챙겨서 첨부해야 하는지" 안내만 자료로
    함께 붙인다(원문 텍스트 자체는 넣지 않음). instructions_text를 넘기면
    그 프롬프트 문구를 쓴다(현재는 Gemini 전용 버전이 이 방식으로 호출).
    안 넘기면 Gemini용 문구로 폴백한다(v6.2: Perplexity 전용 경로는 첨부파일
    분석 제약으로 실사용이 불편하다는 피드백에 따라 제거했다 — 작업 A/B
    내용 자체는 그대로이며 출력 규율 문구만 다른 버전들이라, 안내 조립
    로직은 이 함수 하나로 계속 공유한다)."""
    parts = [instructions_text if instructions_text is not None else get_prompt_prescreening_gemini_instructions()]

    parts.append(f"## 첨부해야 할 파일 안내 — {row.get('servNm', '')}\n")
    attach_list = attachments if attachments is not None else list_attachment_files(row.get("folder", ""))
    if attach_list:
        parts.append(f"- 공식 첨부자료 PDF({len(attach_list)}건, attachments 폴더 — "
                      f"'📎 첨부파일 폴더 열기'로 열어 이 대화에 업로드):")
        for fn in attach_list:
            parts.append(f"  - {fn}")
    else:
        parts.append("- 이 서비스는 attachments 폴더에 공식 첨부자료가 없습니다. "
                      "원문(지원대상/선정기준/혜택/신청방법)만으로는 [작업 A]를 진행할 "
                      "자료가 부족할 수 있으니, 사업안내/지침 PDF를 직접 구해 첨부하는 걸 권장합니다.")
    # [Ver9.31] Gemini용 프롬프트는 확장자로 작업을 나눈다(PDF = 작업 A 공식 자료,
    # MD = 작업 B 경쟁 블로그). 예전 안내대로 블로그를 PDF로 붙이면 작업 A로 섞였다.
    parts.append("- 경쟁 블로그 샘플 MD(2~5개 정도, 같은 키워드로 검색했을 때 상위 노출되는 "
                  "블로그 글 — '블로그 스크랩' 탭에 URL을 넣어 .md로 저장한 파일)도 함께 "
                  "첨부해주세요. 블로그를 PDF로 첨부하면 공식 자료(작업 A)로 섞이니 MD로 첨부합니다.")

    return "\n".join(parts)


def build_draft_prompt_package(detail: dict, source: str, research_map: dict, attachments: list,
                                serv_id: str = "") -> str:
    """초안 작성 프롬프트 + 원문 + 첨부파일 안내 + 리서치 데이터 + (있으면)
    가치판단 결과를 하나로 묶는다. build_value_judgment_package와 구조는
    비슷하지만 프롬프트 본문이 다르다(가치판단이 아니라 실제 글 초안
    작성용). 가치판단 결과를 함께 넘기는 이유: 다른 대화창/다른 AI에서
    이 프롬프트를 이어받아도 앞 단계에서 이미 정리된 강조 포인트·핵심
    키워드·경쟁강도 판단을 처음부터 다시 하지 않고 이어서 쓸 수 있게
    하기 위함."""
    parts = [get_prompt_draft_instructions()]

    parts.append(f"## 서비스 원문 ({source})\n")
    parts.append(f"서비스명: {detail.get('servNm', '')}")
    parts.extend(_format_service_origin_block(detail, source))
    parts.append("")

    parts.append(format_attachments_for_prompt(attachments or []))
    parts.append("")

    # [v7.17 신규, v7.19에서 도입부 지시 추가] 가치판단 [2-A단계]에서
    # 만든 제목 후보 중 코드에서 확정한 게 있으면, 초안작성 프롬프트
    # V5가 그대로 받아써서 쓰도록 맨 앞쪽(원문 바로 다음)에 눈에 띄게
    # 넣는다. 도입부 첫 문장 지시가 함께 저장돼 있다면(가치판단 V4
    # 이후 결과에서 확정한 경우) 같은 섹션에 한 줄 더 실어 보낸다 —
    # 초안작성 V5가 이 줄이 있으면 서론 화두를 스스로 추론하지 않고
    # 그대로 따르도록 되어 있다(없으면 기존처럼 스스로 추론).
    if serv_id:
        confirmed_title = get_confirmed_title(serv_id)
        if confirmed_title:
            block = f"## 확정된 제목 (그대로 사용 — 다시 짓지 않음)\n\n{confirmed_title}\n"
            confirmed_intro = get_confirmed_title_intro(serv_id)
            if confirmed_intro:
                block += f"\n도입부 첫 문장 지시: {confirmed_intro}\n"
            parts.append(block)

    if serv_id:
        parts.append(format_previous_stage_for_prompt("value_judgment", serv_id))
        parts.append("")

    parts.append("## 키워드 리서치 데이터\n")
    if not research_map:
        parts.append("(리서치 없음)")
    else:
        for kw, research in research_map.items():
            parts.append(format_research_for_prompt(research, detail.get('servNm', '')))

    return "\n".join(parts)


# ============================================================
# 최종각색(2차 각색) 프롬프트 — GPT용, 복지정책 블로그 스타일
#   1차 초안(build_draft_prompt_package 결과를 실행한 결과물)에 페르소나와
#   네이버 블로그 발행 형식을 입혀 실제 발행용 글로 다듬는 마지막 각색
#   단계. GPT로 실행하는 것을 전제로 문구를 튜닝했다 — GPT는 완곡한
#   지시("~하지 않도록 주의")보다 명확한 MUST/금지 규칙에 더 잘 반응하고,
#   "더 친절하게" 다듬으려다 원문에 없는 내용을 일반화·추가하는 경향이
#   있어(실제 사례: 1~3순위 선정기준을 하나로 뭉뚱그리거나, 원문에 없는
#   대상자 유형을 새로 추가) 이를 막는 규칙을 특히 강하게 명시한다.
# ============================================================


def build_final_adaptation_prompt_package(detail: dict, source: str, serv_id: str,
                                           research_map: dict = None) -> str:
    """최종각색 프롬프트 + 원문 + (있으면) 초안 결과를 하나로 묶는다.
    1차 초안 결과를 반드시 함께 넘겨야 이 단계가 "처음부터 다시 쓰기"가
    아니라 "1차 초안을 각색하기"가 된다."""
    parts = [get_prompt_final_adaptation_instructions()]

    parts.append(f"## 서비스 원문 ({source})\n")
    parts.append(f"서비스명: {detail.get('servNm', '')}")
    parts.extend(_format_service_origin_block(detail, source))
    parts.append("")

    parts.append(format_previous_stage_for_prompt("draft", serv_id))
    parts.append("")

    if research_map:
        parts.append("## 키워드 리서치 데이터\n")
        for kw, research in research_map.items():
            parts.append(format_research_for_prompt(research, detail.get('servNm', '')))

    return "\n".join(parts)


def build_claude_second_stage_prompt_package(detail: dict, source: str, serv_id: str,
                                              research_map: dict = None) -> str:
    """🧩 통합 프롬프트에서 분리한 "2차 각색(Claude)" 프롬프트 + 원문 +
    (있으면) 1차 초안 결과를 하나로 묶는다. build_final_adaptation_
    prompt_package(GPT용)와 입력 구성이 완전히 동일 — 프롬프트 지시문만
    다르다(Claude가 검증·각색을 수행하도록 쓰인 문구)."""
    parts = [get_prompt_claude_second_stage_instructions()]

    parts.append(f"## 서비스 원문 ({source})\n")
    parts.append(f"서비스명: {detail.get('servNm', '')}")
    parts.extend(_format_service_origin_block(detail, source))
    parts.append("")

    parts.append(format_previous_stage_for_prompt("draft", serv_id))
    parts.append("")

    if research_map:
        parts.append("## 키워드 리서치 데이터\n")
        for kw, research in research_map.items():
            parts.append(format_research_for_prompt(research, detail.get('servNm', '')))

    return "\n".join(parts)


# ============================================================
# GUI
# ============================================================
def strip_trailing_punct_for_filename(text: str) -> str:
    """이미지 파일명으로 바로 쓰기 위해 복사하는 제목에서, 끝에 붙은
    물음표·느낌표·말줄임표 등 특수문자를 제거한다(정책뉴스 프로그램의
    _strip_trailing_punct_for_filename과 동일). "~할까요?"처럼 문장이
    물음표로 끝나는 소제목이 많은데, 그대로 복사하면 이미지 파일 저장
    시 매번 지워야 해서 불편해서 추가된 기능."""
    return re.sub(r'[?!.…~"\'“”‘’]+\s*$', '', text or '').strip()


# ══════════════════════════════════════════════════════════
# [Ver10.07 신규] 코드 카드(선택 기능) — "그림은 AI, 글자는 코드"
# ──────────────────────────────────────────────────────────
# 기존 인포그래픽 흐름(프롬프트C 복사 → GPT가 이미지 전체를 그림)은 그대로 두고,
# 원할 때만 쓰는 추가 경로다. 정책뉴스·복지로 프로그램에 같은 코드가 들어 있다.
#   1) 카드용 프롬프트(정책 C V18 / 복지로 ⑦ V7)를 본문과 함께 복사 → AI 답변
#   2) AI 답변(썸네일 장면 프롬프트 + 마지막 JSON 설계도)을 붙여넣거나
#      글 폴더의 "_카드작업" 폴더에 넣는다(답변 파일 .txt/.md/.json)
#   3) 퍼플렉시티 등에서 그린 글자 없는 배경 그림을 고르거나 "_카드작업"에 넣는다
#   4) "카드 만들기" → Naver_blog_SVG Card_images/cards/make_cards.py 실행 → 결과 PNG를
#      제목·소제목 이름(분할은 _1·_2)으로 바꿔 MD 폴더에 넣는다. 그래서 이후
#      키워드 등록·포스팅 프로그램은 지금처럼 이미지를 찾는다.
# make_cards.py·icons.py·fonts는 Naver_blog_SVG Card_images 쪽에서 관리하며 여기서 고치지 않는다.
# ══════════════════════════════════════════════════════════
CARD_WORK_SUBFOLDER = "_카드작업"
CARD_SCENE_BASENAME = "00_thumbnail_scene"
CARD_BACKUP_SUBFOLDER = "_이전이미지"
CARD_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
CARD_ANSWER_EXTS = (".txt", ".md", ".json")
CARD_ANSWER_FILENAME = "AI답변.txt"
CARD_SPEC_FILENAME = "spec.json"
CARD_WIN_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
]
_CARD_FENCE_RE = re.compile(r"^[ \t]*```([^\n`]*)\n(.*?)^[ \t]*```[ \t]*$", re.M | re.S)


_CARD_INVISIBLE_RE = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")


def card_json_loads(raw: str):
    """설계도 JSON 읽기. claude.ai 화면에서 복사하면 눈에 안 보이는 글자가 섞일 때가 있다 —
    줄바꿈 없는 공백(NBSP)·폭 없는 공백이 쉼표 뒤에 들어가면 "Expecting property name"이 난다.
    그래서 ① 그런 글자를 보통 공백으로 바꿔 읽고, 안 되면 ② 굽은 따옴표(“”)를 곧은 따옴표로,
    ③ 닫는 괄호 앞 쉼표를 지워 차례로 다시 읽는다. 끝내 안 되면 오류 위치 앞뒤 글자를 함께 알려 준다.
    반환: (dict 또는 None, 오류 문구)"""
    text = _CARD_INVISIBLE_RE.sub("", raw or "")
    text = text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2007", " ").replace("\u3000", " ")
    tries = [text,
             text.replace("\u201c", '"').replace("\u201d", '"'),
             re.sub(r",\s*([}\]])", r"\1", text.replace("\u201c", '"').replace("\u201d", '"'))]
    first_err = None
    for t in tries:
        try:
            return json.loads(t, strict=False), ""
        except Exception as e:
            if first_err is None:
                first_err = e
    pos = getattr(first_err, "pos", None)
    where = ""
    if isinstance(pos, int):
        where = f" — 그 자리: {text[max(0, pos - 25):pos]!r} ▶ {text[pos:pos + 15]!r}"
    return None, f"{first_err}{where}"


def card_parse_answer(text: str):
    """AI 답변에서 (썸네일 장면 프롬프트, JSON 설계도 dict, 오류 문구)를 꺼낸다.
    - 설계도: 맨 마지막 ```json 코드블럭. 없으면 "{"로 시작하는 마지막 코드블럭,
      그것도 없으면 답변 전체가 JSON인지 본다(spec.json 파일을 그대로 넣은 경우).
    - 장면 프롬프트: "파일명 식별자: 00_thumbnail_scene" 줄 바로 위 코드블럭 안 문장."""
    text = (text or "").replace("\r\n", "\n")
    blocks = [(m.group(1).strip().lower(), m.group(2), m.start(), m.end())
              for m in _CARD_FENCE_RE.finditer(text)]
    raw = None
    for lang, body, _, _ in reversed(blocks):
        if lang == "json":
            raw = body
            break
    if raw is None:
        for _, body, _, _ in reversed(blocks):
            if body.lstrip().startswith("{"):
                raw = body
                break
    if raw is None and text.strip().startswith("{"):
        raw = text
    scene = ""
    m = re.search(r"파일명\s*식별자\s*[:：]\s*" + re.escape(CARD_SCENE_BASENAME), text)
    if m:
        before = [b for b in blocks if b[3] <= m.start()]
        if before:
            scene = before[-1][1].strip()
    if raw is None:
        return scene, None, "JSON 설계도 코드블럭이 없습니다"
    spec, err = card_json_loads(raw)
    if err:
        return scene, None, f"JSON 문법 오류: {err}"
    if not isinstance(spec, dict) or not isinstance(spec.get("images"), list) or not spec["images"]:
        return scene, None, "JSON에 images 목록이 없습니다"
    for img in spec["images"]:
        if not isinstance(img, dict) or not img.get("file") or not img.get("layout"):
            return scene, None, "images 항목에 file·layout이 빠진 것이 있습니다"
    return scene, spec, ""


def card_md_headings(md_text: str):
    """MD에서 (제목, [소제목...])을 뽑는다(# 제목 1개, ## 소제목 — ###는 제외)."""
    title, subs = "", []
    for line in (md_text or "").split("\n"):
        s = line.strip()
        if s.startswith("# ") and not title:
            title = s[2:].strip()
        elif s.startswith("## ") and not s.startswith("### "):
            subs.append(s[3:].strip())
    return title, subs


def _card_norm(text: str) -> str:
    return re.sub(r"[\s\W_]+", "", text or "")


def card_match_images(spec: dict, md_text: str):
    """설계도 이미지마다 MD 안의 대상(제목/소제목)을 찾는다.
    반환: [{"file", "kind": "썸네일"|"소제목"|"", "target": 원문 또는 "", "part": n 또는 0, "note"}]
    - 썸네일(layout thumbnail 또는 file 00_thumbnail) → # 제목
    - 그 밖 → heading 값. 끝의 "(1/2)"는 분할 번호, 그 밖의 괄호 꼬리·"— …" 꼬리는 떼고
      소제목과 글자(공백·기호 제외)가 같으면 연결, 아니면 비슷한 정도 0.75 이상인 가장 가까운 것.
      못 찾으면 target ""(매칭 안 됨 — 결과는 _카드작업/out에만 남는다).
    - 같은 소제목에 이미지가 2장 이상이면 순서대로 _1, _2 …를 붙인다."""
    title, subs = card_md_headings(md_text)
    norm_subs = [(_card_norm(s), s) for s in subs]
    out = []
    for img in spec.get("images", []):
        f = str(img.get("file", ""))
        if img.get("layout") == "thumbnail" or f.startswith("00_thumbnail"):
            out.append({"file": f, "kind": "썸네일", "target": title, "part": 0,
                        "note": "" if title else "MD에 # 제목 없음"})
            continue
        h = str(img.get("heading") or "").strip()
        part = 0
        pm = re.search(r"\(\s*(\d+)\s*/\s*\d+\s*\)\s*$", h)
        if pm:
            part = int(pm.group(1))
            h = h[:pm.start()].strip()
        h = re.sub(r"\s*[—–]\s.*$", "", h).strip()
        h_core = re.sub(r"\s*\([^()]*\)\s*$", "", h).strip() or h
        target, note = "", ""
        for cand in (h, h_core):
            nc = _card_norm(cand)
            hit = next((s for n, s in norm_subs if nc and n == nc), "")
            if hit:
                target = hit
                break
        if not target and h_core:
            best, best_r = "", 0.0
            for n, s in norm_subs:
                r = difflib.SequenceMatcher(None, _card_norm(h_core), n).ratio()
                if r > best_r:
                    best, best_r = s, r
            if best_r >= 0.75:
                target, note = best, f"비슷한 소제목으로 연결({best_r:.0%})"
        if not target:
            note = f"소제목을 찾지 못함: {h or '(heading 없음)'}"
        out.append({"file": f, "kind": "소제목" if target else "", "target": target,
                    "part": part, "note": note})
    # 같은 대상에 여러 장 → 분할 번호(설계도에 번호가 없거나 겹치면 순서대로)
    groups = {}
    for m in out:
        if m["kind"] == "소제목":
            groups.setdefault(m["target"], []).append(m)
    for ms in groups.values():
        if len(ms) == 1:
            ms[0]["part"] = 0
        elif sorted(m["part"] for m in ms) != list(range(1, len(ms) + 1)):
            for i, m in enumerate(ms, 1):
                m["part"] = i
    return out


def card_find_background(work_dir: str, md_folder: str):
    """썸네일 배경 그림을 찾는다: _카드작업(원본 이미지 폴더) 안의 가장 최근 그림(이름 무관, 슬롯 slot_* 제외)
    → 없으면 MD 폴더의 00_thumbnail_scene.*."""
    cands = []
    if os.path.isdir(work_dir):
        for fn in os.listdir(work_dir):
            p = os.path.join(work_dir, fn)
            if (os.path.isfile(p) and fn.lower().endswith(CARD_IMAGE_EXTS)
                    and not fn.lower().startswith("slot_")):
                cands.append(p)
    if cands:
        return max(cands, key=os.path.getmtime)
    for ext in CARD_IMAGE_EXTS:
        p = os.path.join(md_folder, CARD_SCENE_BASENAME + ext)
        if os.path.isfile(p):
            return p
    return None

def card_find_answer_file(work_dir: str):
    """_카드작업 폴더에 넣어 둔 AI 답변 파일(가장 최근 .txt/.md/.json, spec.json 포함)."""
    if not os.path.isdir(work_dir):
        return None
    cands = [os.path.join(work_dir, fn) for fn in os.listdir(work_dir)
             if fn.lower().endswith(CARD_ANSWER_EXTS) and os.path.isfile(os.path.join(work_dir, fn))]
    return max(cands, key=os.path.getmtime) if cands else None


def card_chrome_path(cfg_value: str = "") -> str:
    """설정의 크롬 경로 → 없으면 Windows 기본 설치 위치 → 그래도 없으면 ""(Playwright 기본 크롬)."""
    v = (cfg_value or "").strip().strip('"')
    if v and os.path.isfile(v):
        return v
    if sys.platform.startswith("win"):
        for p in CARD_WIN_CHROME_PATHS:
            if p and os.path.isfile(p):
                return p
    return ""


def card_render(tool_dir: str, spec_path: str, chrome_path: str = "", only=None):
    """make_cards.py를 별도 파이썬으로 실행한다. 반환 (성공 여부, 출력 문구)."""
    script = os.path.join(tool_dir, "cards", "make_cards.py")
    if not os.path.isfile(script):
        return False, f"make_cards.py가 없습니다: {script}\n(설정 탭의 Naver_blog_SVG Card_images 폴더를 확인하세요)"
    if getattr(sys, "frozen", False):
        return False, "exe로 실행 중이라 카드 만들기를 쓸 수 없습니다(.py로 실행하세요)."
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if chrome_path:
        env["CHROME_PATH"] = chrome_path
    else:
        env.pop("CHROME_PATH", None)
    py = sys.executable
    if py.lower().endswith("pythonw.exe"):
        alt = py[:-len("pythonw.exe")] + "python.exe"
        if os.path.isfile(alt):
            py = alt
    kw = {}
    if sys.platform.startswith("win"):
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW — 검은 창이 뜨지 않게
    try:
        r = subprocess.run([py, script, spec_path] + list(only or []), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=env,
                           cwd=os.path.dirname(script), timeout=600, **kw)
    except Exception as e:
        return False, f"실행 실패: {e}"
    log = ((r.stdout or "") + ("\n" + r.stderr if r.stderr else "")).strip()
    if r.returncode != 0 and "No module named 'playwright'" in log:
        log = ("Playwright가 설치되어 있지 않습니다. 명령 프롬프트에서 한 번만 실행하세요:\n"
               "  pip install playwright\n(크롬이 없으면 이어서: python -m playwright install chromium)\n\n" + log)
    return r.returncode == 0, log


def card_install(work_dir: str, matches, md_folder: str, name_fn):
    """_카드작업/out/의 PNG를 MD 폴더에 제목·소제목 이름으로 넣는다.
    같은 이름(또는 _숫자 분할본)의 기존 그림은 _카드작업/_이전이미지/로 옮긴 뒤 넣는다
    (분할본이 남아 있으면 포스팅 프로그램이 그쪽을 먼저 집기 때문).
    반환 (넣은 [(파일, 새 이름)], 매칭 안 된 [파일], 옮긴 기존 그림 수, 결과 없음 [파일])."""
    out_dir = os.path.join(work_dir, "out")
    placed, unmatched, missing, moved = [], [], [], 0
    backup = os.path.join(work_dir, CARD_BACKUP_SUBFOLDER)
    cleared = set()
    for m in matches:
        src = os.path.join(out_dir, m["file"] + ".png")
        if not os.path.isfile(src):
            missing.append(m["file"])
            continue
        if not m["target"]:
            unmatched.append(m["file"])
            continue
        base = name_fn(m["target"])
        if not base:
            unmatched.append(m["file"])
            continue
        if base not in cleared:
            cleared.add(base)
            pat = re.compile(r"^" + re.escape(base) + r"(_\d+)?\.(png|jpe?g|webp)$", re.I)
            for fn in os.listdir(md_folder):
                if pat.match(fn) and os.path.isfile(os.path.join(md_folder, fn)):
                    os.makedirs(backup, exist_ok=True)
                    dst = os.path.join(backup, fn)
                    if os.path.exists(dst):
                        stem, ext = os.path.splitext(fn)
                        dst = os.path.join(backup, f"{stem}_{time.strftime('%H%M%S')}{ext}")
                    shutil.move(os.path.join(md_folder, fn), dst)
                    moved += 1
        name = f"{base}_{m['part']}.png" if m["part"] else f"{base}.png"
        shutil.copy2(src, os.path.join(md_folder, name))
        placed.append((m["file"], name))
    return placed, unmatched, moved, missing


def card_count_existing(matches, md_folder: str, name_fn) -> int:
    """card_install이 _이전이미지로 옮길 기존 그림 수(확인창 안내용)."""
    bases = {name_fn(m["target"]) for m in matches if m.get("target")}
    bases.discard("")
    n = 0
    for fn in (os.listdir(md_folder) if os.path.isdir(md_folder) else []):
        for base in bases:
            if re.match(r"^" + re.escape(base) + r"(_\d+)?\.(png|jpe?g|webp)$", fn, re.I):
                n += 1
                break
    return n


def card_prepare_spec(spec: dict, work_dir: str, background_path):
    """설계도를 _카드작업/spec.json으로 저장한다. 배경 그림이 있으면 _카드작업으로 가져와
    썸네일 항목의 background 값을 그 파일 이름으로 맞춘다(webp·jpg도 그대로 쓴다)."""
    os.makedirs(work_dir, exist_ok=True)
    bg_name = ""
    if background_path:
        if os.path.abspath(os.path.dirname(background_path)) == os.path.abspath(work_dir):
            bg_name = os.path.basename(background_path)   # 원본 이미지 폴더에 있는 그림은 이름 그대로
        else:
            bg_name = CARD_SCENE_BASENAME + os.path.splitext(background_path)[1].lower()
            shutil.copy2(background_path, os.path.join(work_dir, bg_name))
    for img in spec.get("images", []):
        if img.get("layout") == "thumbnail" and bg_name:
            img["background"] = bg_name
    path = os.path.join(work_dir, CARD_SPEC_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    return path, bg_name


def extract_infographic_title_list(final_text: str) -> list:
    """최종각색 결과에서 썸네일(# 제목) + 소제목(## 제목) 목록을 뽑는다.
    정책뉴스 프로그램의 _generate_title_list와 동일한 파싱 규칙 —
    ### 이하는 소제목으로 치지 않는다(### 문단 안 소소제목까지 다
    잡으면 목록이 너무 길어짐)."""
    items = []
    lines = final_text.split("\n")
    h1 = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            h1 = stripped[2:].strip()
            break
    if not h1:
        h1 = extract_title_from_final_text(final_text)
    if h1:
        items.append(("썸네일", h1))
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            items.append(("소제목", stripped[3:].strip()))
    return items


def get_infographic_status_path() -> str:
    return os.path.join(DATA_DIR, "infographic_status.json")


def load_infographic_status() -> dict:
    """servId -> {인덱스(str): 이미지 생성 완료 여부(bool)}. 🖼 인포그래픽
    작업 탭의 체크박스 상태를 저장해서, 같은 서비스를 다시 열어도
    어디까지 만들었는지 기억하게 한다."""
    path = get_infographic_status_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_infographic_status(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_infographic_status_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_unresolved_related_lcgv_ids(row: dict, rows_by_id: dict = None) -> list:
    """이 중앙부처 행과 이름이 유사한 지자체 행들 중, 아직 패스/보류/
    포스팅완료로 정리되지 않은 servId 목록을 돌려준다. 중앙부처를
    포스팅완료로 확정하거나 키워드 등록에 올리기 전에 "지자체 중복 건을
    깜빡 잊지 않았는지" 확인하는 두 곳(⑧ 완료 처리, 📤 키워드 등록)에서
    공통으로 쓴다."""
    if rows_by_id is None:
        rows_by_id = {r["servId"]: r for r in build_listing_rows()}
    related_ids = row.get("related_lcgv_ids", [])
    return [
        sid for sid in related_ids
        if rows_by_id.get(sid, {}).get("posting_status", "") not in ("⏭ 패스", "⏸ 보류", PROTECTED_STATUS)
    ]


# ============================================================
# 블로그 스크랩 함수 — naver_blog_scraper.py(독립 프로그램) 이식. [Ver10.08] 탭은 삭제, 자료 자동 준비·STEP 1 주소 스크랩이 쓴다.
#   ⓪ 사전스크리닝(Gemini)이 "경쟁 블로그 샘플"로 참조할 상위노출
#   블로그 게시글을 URL만으로 마크다운(.md)으로 저장해두는 용도. 외부
#   모듈 파일로 분리하지 않고, 이 프로그램 안에 함수/클래스를 그대로
#   심었다(요청사항) — 별도 .py 파일 배포/경로 관리 없이 이 GUI
#   하나만으로 동작하게 하기 위함. 원본 프로그램의 로직은 그대로 두고
#   (마크다운 변환 휴리스틱 등 손대지 않음), 저장 폴더 기본값만 이
#   프로그램의 WORK_DIR 하위로 맞췄다.
# ============================================================
BLOG_SCRAP_SUBTITLE_FONT_SIZE_THRESHOLD = 19  # 소제목 판단 최소 폰트 크기(se-fsXX, px)
BLOG_SCRAP_SUBTITLE_MAX_LENGTH = 60           # 소제목 판단 최대 글자 수


def blog_scrap_default_output_dir() -> str:
    """스크랩 결과 기본 저장 폴더 — 원본 독립 프로그램은 실행 위치 기준
    "naver_blog_md"였지만, 이 프로그램에 이식하면서 WORK_DIR 하위로
    바꿔 다른 산출물(final_posts 등)과 같은 작업폴더 안에 모이게 했다."""
    return os.path.join(WORK_DIR, "naver_blog_scrap_md")


def blog_scrap_to_mobile_url(url: str) -> str:
    """PC 버전 blog.naver.com URL을 모바일 버전으로 변환."""
    url = url.strip()
    parsed = urlparse(url)
    if "m.blog.naver.com" in parsed.netloc:
        return url
    if "blog.naver.com" in parsed.netloc:
        return url.replace("blog.naver.com", "m.blog.naver.com")
    raise ValueError(f"네이버 블로그 URL이 아닙니다: {url}")


def blog_scrap_sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "", name).strip()
    return (name[:100] if len(name) > 100 else name) or "untitled"


def blog_scrap_get_safe_temp_base() -> str:
    """한글(비-ASCII) 사용자 계정명이 포함된 시스템 TEMP 경로를 피하기
    위한 ASCII 전용 임시 폴더 기준 경로(윈도우에서 --user-data-dir 경로에
    한글이 섞이면 크롬이 'session not created: chrome not reachable' 오류로
    아예 실행되지 않는 경우가 있어서 원본 프로그램에 이미 반영돼 있던
    대응 — 그대로 유지)."""
    if sys.platform == "win32":
        base = "C:\\temp\\naver_blog_scrap_profiles"
    else:
        base = "/tmp/naver_blog_scrap_profiles"
    os.makedirs(base, exist_ok=True)
    return base


def blog_scrap_build_driver():
    """헤드리스 크롬 드라이버 생성(임시 프로필로 세션 격리 — 이 프로그램의
    다른 크롬 자동화(블로그 순위체크, 네이버 검색 열기)와 동일한 "매번 새
    임시 프로필" 원칙)."""
    safe_base = blog_scrap_get_safe_temp_base()
    temp_profile = tempfile.mkdtemp(prefix="profile_", dir=safe_base)

    options = SeleniumChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,2000")
    options.add_argument(f"--user-data-dir={temp_profile}")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver._temp_profile_dir = temp_profile
    return driver


def blog_scrap_cleanup_driver(driver):
    temp_profile = getattr(driver, "_temp_profile_dir", None)
    try:
        driver.quit()
    finally:
        if temp_profile and os.path.exists(temp_profile):
            shutil.rmtree(temp_profile, ignore_errors=True)


def blog_scrap_extract_title(driver, wait) -> str:
    title_selectors = [
        "div.se-module.se-module-text.se-title-text",
        "h3.se_textarea",
        "div.htitle",
        "h2.htitle",
    ]
    for sel in title_selectors:
        try:
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            title = el.text.strip()
            if title:
                return title
        except TimeoutException:
            continue
    return driver.title.split(": 네이버 블로그")[0].strip()


def blog_scrap_extract_font_size(cls: str, style: str) -> int:
    m = re.search(r"se-fs(\d+)", cls)
    if m:
        return int(m.group(1))
    m2 = re.search(r"font-size:\s*(\d+)px", style)
    if m2:
        return int(m2.group(1))
    return 15  # 네이버 기본 본문 폰트 크기


def blog_scrap_is_bold_span(cls: str, style: str) -> bool:
    return "se-bold" in cls or "font-weight:bold" in style.replace(" ", "") \
        or "font-weight:700" in style.replace(" ", "")


def blog_scrap_paragraph_to_markdown(p_element):
    """하나의 se-text-paragraph를 마크다운 텍스트로 변환.
    return: (markdown_text, is_subtitle)"""
    spans = p_element.find_elements(By.CSS_SELECTOR, "span")
    if not spans:
        text = p_element.text.strip()
        return text, False

    parts = []
    max_font_size = 0
    any_bold = False
    plain_text_len = 0

    for span in spans:
        span_text = span.text
        if not span_text:
            continue
        cls = span.get_attribute("class") or ""
        style = span.get_attribute("style") or ""
        bold = blog_scrap_is_bold_span(cls, style)
        font_size = blog_scrap_extract_font_size(cls, style)
        max_font_size = max(max_font_size, font_size)
        plain_text_len += len(span_text)

        if bold:
            any_bold = True
            parts.append(f"**{span_text}**")
        else:
            parts.append(span_text)

    full_text = "".join(parts).strip()
    if not full_text:
        return "", False

    is_subtitle = (
        (max_font_size >= BLOG_SCRAP_SUBTITLE_FONT_SIZE_THRESHOLD or any_bold)
        and plain_text_len <= BLOG_SCRAP_SUBTITLE_MAX_LENGTH
        and max_font_size >= BLOG_SCRAP_SUBTITLE_FONT_SIZE_THRESHOLD
    )
    return full_text, is_subtitle


def blog_scrap_parse_text_component(comp) -> str:
    paragraphs = comp.find_elements(
        By.CSS_SELECTOR, "p.se-text-paragraph, div.se-text-paragraph"
    )
    if not paragraphs:
        return comp.text.strip()

    lines = []
    for p in paragraphs:
        text, is_subtitle = blog_scrap_paragraph_to_markdown(p)
        if not text:
            lines.append("")
            continue
        lines.append(f"## {text}" if is_subtitle else text)

    # 연속 빈 줄 정리
    result, prev_blank = [], False
    for line in lines:
        if line == "":
            if prev_blank:
                continue
            prev_blank = True
        else:
            prev_blank = False
        result.append(line)
    return "\n".join(result).strip("\n")


def blog_scrap_parse_quote_component(comp) -> str:
    text = comp.text.strip()
    if not text:
        return ""
    return "\n".join(f"> {line}" for line in text.split("\n") if line.strip())


def blog_scrap_parse_table_component(comp) -> str:
    rows = comp.find_elements(By.CSS_SELECTOR, "table tr")
    if not rows:
        return ""

    table_rows = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "th, td")
        cell_texts = [(c.text.strip().replace("\n", " ") or " ") for c in cells]
        if cell_texts:
            table_rows.append(cell_texts)
    if not table_rows:
        return ""

    col_count = max(len(r) for r in table_rows)
    for r in table_rows:
        while len(r) < col_count:
            r.append(" ")

    md = ["| " + " | ".join(table_rows[0]) + " |",
          "| " + " | ".join(["---"] * col_count) + " |"]
    for r in table_rows[1:]:
        md.append("| " + " | ".join(r) + " |")
    return "\n".join(md)


def blog_scrap_parse_image_component(comp) -> str:
    try:
        img = comp.find_element(By.CSS_SELECTOR, "img")
        src = img.get_attribute("data-lazy-src") or img.get_attribute("src") or ""
        if src and not src.startswith("data:"):
            return f"![이미지]({src})"
    except NoSuchElementException:
        pass
    return ""


def blog_scrap_parse_content_blocks(driver) -> str:
    """se-main-container 내부 컴포넌트를 순회하며 전체 본문 마크다운 생성."""
    try:
        container = driver.find_element(By.CSS_SELECTOR, "div.se-main-container")
    except NoSuchElementException:
        # 구버전 에디터 - 서식 없이 텍스트만 추출
        try:
            legacy = driver.find_element(By.CSS_SELECTOR, "div#postViewArea, div.post_ct")
            return legacy.text.strip()
        except NoSuchElementException:
            raise RuntimeError("본문을 찾을 수 없습니다.")

    components = container.find_elements(By.CSS_SELECTOR, ":scope > div.se-component")
    if not components:
        return container.text.strip()

    md_blocks = []
    for comp in components:
        classes = comp.get_attribute("class") or ""
        try:
            if "se-quotation" in classes:
                block = blog_scrap_parse_quote_component(comp)
            elif "se-table" in classes:
                block = blog_scrap_parse_table_component(comp)
            elif "se-image" in classes:
                block = blog_scrap_parse_image_component(comp)
            elif "se-horizontalLine" in classes:
                block = "---"
            elif "se-text" in classes:
                block = blog_scrap_parse_text_component(comp)
            else:
                block = comp.text.strip()
        except Exception:
            block = ""

        if block:
            md_blocks.append(block)

    return "\n\n".join(md_blocks)


def blog_scrap_scrape_post(driver, url: str) -> dict:
    mobile_url = blog_scrap_to_mobile_url(url)
    driver.get(mobile_url)
    wait = WebDriverWait(driver, 10)

    title = blog_scrap_extract_title(driver, wait)
    content_md = blog_scrap_parse_content_blocks(driver)
    if not content_md.strip():
        raise RuntimeError("본문을 찾을 수 없습니다.")

    return {"title": title, "content": content_md, "url": url}


def blog_scrap_save_as_md(post: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename = blog_scrap_sanitize_filename(post["title"])
    filepath = os.path.join(output_dir, f"{filename}.md")

    base_filepath = filepath
    idx = 2
    while os.path.exists(filepath):
        filepath = base_filepath.replace(".md", f"_{idx}.md")
        idx += 1

    md_content = (
        f"# {post['title']}\n\n"
        f"- 원본 URL: {post['url']}\n"
        f"- 수집 일시: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"---\n\n"
        f"{post['content']}\n"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    return filepath


class WelfareCollectorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # 위젯을 다 구성하기 전까지는 화면에 표시하지 않는다 — withdraw()로
        # 창을 숨긴 상태에서 title/geometry/위젯구성을 전부 마친 뒤 마지막에
        # deiconify()로 한 번에 띄우면, 내용 없는 빈 창이 잠깐 보였다가
        # 메인 창으로 바뀌는 현상(초기 렌더링 중간 상태 노출)이 사라진다.
        self.withdraw()

        self.title("복지로 정책 수집한 후 Claude로 각색 및 인포그래픽 설계하는 프로그램_2026-10-16_Ver 10.13")

        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = None

        self._missing_prompt_files_at_startup = check_prompt_files_status()  # 자동 생성하지 않고 점검만

        self._build_widgets()
        self._load_saved_key()
        # [v7.13 재원복] v7.12에서 동기(_refresh_status())로 되돌렸는데,
        # 사용자가 실제로 원했던 건 "창 자체가 느려지는 것"이 아니라
        # "4)포스팅 관리 탭 목록만 유독 늦게 나오는 것"의 해결이었다는
        # 게 명확해짐("포스팅 관리탭의 리스트만 늦게 나왔어... 이제
        # 첫 프로그램 시작시도 느려... 그럼 구방식 회귀한거아냐?").
        # 원인은 build_listing_rows() 자체가 아니라(그건 이미 백그라운드
        # 스레드에서 돎), 그 결과로 3개 트리(listing/posting/history)를
        # 채우는 _apply_status_result()가 메인 스레드에서 동기 실행되는
        # 부분에 있었다 — _refresh_posting_tree()만 행마다
        # list_attachment_files()(폴더 os.listdir)를 도는 실제 디스크
        # I/O가 있어서, 같은 shared_rows를 쓰는데도 포스팅 탭만 유독
        # 느렸던 것(아래 get_attachment_count_cached()로 별도 수정).
        # 그래서 창을 빨리 띄우는 이점은 유지하려고 비동기 호출로
        # 다시 되돌린다.
        self._refresh_status_startup_async()
        self._refresh_ig_service_list()
        self._refresh_keyword_reg_preview()
        self.after(150, self._poll_log_queue)
        if self._missing_prompt_files_at_startup:
            # 로그창이 뜬 뒤에 안내되도록 약간 지연 — _poll_log_queue가 먼저 돌기 시작해야 함
            self.after(300, self._warn_missing_prompt_files)
        # 현재 공인 IP 라벨을 조용히 갱신(팝업 없음) — 네트워크 호출이라
        # 창이 다 뜬 뒤로 살짝 늦춰서 시작 속도에 영향 안 주게 한다.
        self.after(800, self._refresh_ip_label)

        # 위젯 구성이 모두 끝난 뒤에 크기를 확정하고 중앙 배치 -> 그제서야 표시.
        # PanedWindow 분할 비율(로그 영역 확대)도 창이 실제로 그려진 뒤에만
        # 정확히 계산되므로 deiconify 이후로 예약한다.
        self._center_window(1440, 980)
        self._apply_ui_theme()
        self.deiconify()
        self.after(50, self._apply_initial_sash_position)

    def _apply_ui_theme(self):
        """화면 디자인(ui_theme.py, 정책뉴스와 공용) — 겉모습만 바꾼다. 파일이 없거나 오류가 나면 지금 모습 그대로."""
        def key_chip():
            return ("설정됨", "green") if self.key_var.get().strip() else ("필요", "red")

        def openai_chip():
            return ("설정됨", "green") if self.settings_openai_key_var.get().strip() else ("안 씀", "gray")

        def prompt_chip():
            missing = self._missing_prompt_files_at_startup
            return (f"{len(missing)}개 없음", "red") if missing else ("정상", "green")
        try:
            import ui_theme
            ui_theme.apply(self, self.notebook, "복지로 관리", "복지 서비스 → 블로그 원고",
                           accent="#0F766E", accent2="#C9A227",
                           chips=[("공공데이터 키", key_chip), ("프롬프트 파일", prompt_chip),
                                  ("OpenAI 키(문단 정리)", openai_chip)], widen=False)
            # 창이 뜨기 전에 왼쪽 메뉴 폭만큼 넓혀 둔다(뜬 뒤에 넓히면 한 번 깜빡인다)
            self._center_window(1440 + ui_theme.SIDEBAR_W, 980)
        except Exception as e:
            print(f"[디자인] 적용 안 함(지금 모습으로 실행): {e}")

    def _apply_initial_sash_position(self):
        """분할창(main_paned)의 경계선 초기 위치를 위쪽 65% 지점으로 잡는다.
        로그 영역이 처음부터 넉넉하게 보이도록 하기 위함 — 이후에는 사용자가
        직접 드래그해 원하는 비율로 자유롭게 조절 가능하다."""
        try:
            self.update_idletasks()
            total_h = self.main_paned.winfo_height()
            if total_h > 100:
                self.main_paned.sashpos(0, int(total_h * 0.65))
        except tk.TclError:
            pass

    def _on_notebook_tab_changed(self, event=None):
        """탭을 옮길 때마다 그 탭에 맞는 sash 비율로 자동 재조정한다
        (_tab_top_ratio 참고 — 4)포스팅 관리 등 그리드가 중요한 탭은
        작업 영역을 크게, ①② 수집 탭은 로그가 중요하니 기존 비율 유지)."""
        try:
            self.update_idletasks()
            total_h = self.main_paned.winfo_height()
            if total_h <= 100:
                return
            selected = self.notebook.select()
            ratio = self._tab_top_ratio.get(selected, self._tab_default_top_ratio)
            self.main_paned.sashpos(0, int(total_h * ratio))
        except tk.TclError:
            pass

    def _center_window(self, width: int, height: int):
        """창을 화면 정중앙에 배치한다. 화면보다 창이 크면 화면 크기에 맞춰
        줄이고, 멀티 모니터 등으로 화면 크기를 못 가져오는 예외적인 경우엔
        조용히 넘어가고 기본 위치(geometry 지정 없이 OS가 정하는 위치)로
        띄운다 — 창이 아예 안 뜨는 것보다는 낫기 때문."""
        try:
            self.update_idletasks()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            width = min(width, screen_w)
            height = min(height, screen_h)
            x = (screen_w - width) // 2
            y = (screen_h - height) // 2 - 30
            self.geometry(f"{width}x{height}+{x}+{y}")
        except tk.TclError:
            self.geometry(f"{width}x{height}")

    # ---------------- 위젯 구성 ----------------
    def _build_widgets(self):
        pad = {"padx": 8, "pady": 6}

        # 인증키 입력은 v3.1부터 8)설정 탭으로 이동했다(예전엔 상단에
        # 항상 떠 있었는데, 다른 탭 작업 중에도 계속 자리를 차지해서
        # 화면이 좁아 보인다는 피드백). self.key_var/self.show_key_var
        # 위젯 자체는 설정 탭 쪽에서 만들며, 실제 값(StringVar)은
        # 여전히 이 인스턴스 전역에서 API 호출 시 그대로 참조된다.

        # 탭 스타일 (정책뉴스 프로그램과 동일한 방식) — 글자를 키우고,
        # 선택된 탭은 진한 파란색 글자로 눈에 띄게 구분한다. ttk 테마에
        # 따라 배경색 변경이 일부 플랫폼에서 잘 안 먹는 경우가 있어서,
        # 글자색+굵기를 같이 줘서 어떤 환경에서도 확실히 구분되게 한다.
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("맑은 고딕", 11, "bold"), padding=[10, 4])
        # [Ver9.04 추가] 설정탭 저장 버튼용 — 눈에 잘 띄도록 굵고 살짝 크게
        style.configure("Save.TButton", font=("맑은 고딕", 11, "bold"))
        style.map("TNotebook.Tab",
                  foreground=[("selected", "#0000FF"), ("!selected", "black")])

        # 화면을 위(작업 탭)/아래(로그) 두 구역으로 나누는 수직 분할 창.
        # 로그창이 항상 작게 고정되던 문제를 해결하기 위해, 사용자가 마우스로
        # 경계선(sash)을 드래그해 로그 영역을 원하는 만큼 키우거나 줄일 수
        # 있게 한다. 초기 비율은 _apply_initial_sash_position()에서 위쪽
        # 65% / 아래쪽 35%로 잡아 기존보다 로그 세로 폭을 크게 확보한다.
        main_paned = ttk.PanedWindow(self, orient="vertical")
        main_paned.pack(fill="both", expand=True, **pad)
        self.main_paned = main_paned

        tabs_container = ttk.Frame(main_paned)
        bottom_container = ttk.Frame(main_paned)
        main_paned.add(tabs_container, weight=3)
        main_paned.add(bottom_container, weight=2)

        # 중앙부처 / 지자체 / 리스트업 탭
        notebook = ttk.Notebook(tabs_container)
        notebook.pack(fill="both", expand=True)

        central_tab = ttk.Frame(notebook)
        lcgv_tab = ttk.Frame(notebook)
        listing_tab = ttk.Frame(notebook)
        posting_tab = ttk.Frame(notebook)
        infographic_tab = ttk.Frame(notebook)
        keyword_reg_tab = ttk.Frame(notebook)
        history_tab = ttk.Frame(notebook)
        settings_tab = ttk.Frame(notebook)
        notebook.add(central_tab, text="🏛 1)중앙부처복지서비스")
        notebook.add(lcgv_tab, text="🏘 2)지자체복지서비스")
        notebook.add(listing_tab, text="📋 3)리스트업")
        notebook.add(posting_tab, text="📝 4)포스팅 관리")
        notebook.add(infographic_tab, text="🖼 5)인포그래픽 작성")
        notebook.add(keyword_reg_tab, text="📤 6)키워드 등록")
        notebook.add(history_tab, text="📊 7)포스팅 이력관리")
        notebook.add(settings_tab, text="⚙️ 8)설정")
        self.notebook = notebook
        self.settings_tab = settings_tab
        self.infographic_tab = infographic_tab
        self.keyword_reg_tab = keyword_reg_tab

        # 탭별로 화면 위(작업 영역)/아래(로그) 분할 비율을 다르게 자동 적용.
        # 4)포스팅 관리처럼 그리드를 많이 봐야 하는 탭에서는 로그 영역이
        # 항상 똑같이 35%를 차지해 그리드가 6행 정도밖에 안 보이던 문제를
        # 해결 — 탭을 옮길 때마다 그 탭에 맞는 비율로 sash 위치를 자동
        # 재조정한다. 수집 로그를 실시간으로 지켜봐야 하는 ①②(중앙부처/
        # 지자체)만 기존처럼 로그 영역을 넉넉히(35%) 남기고, 나머지 탭은
        # 작업 영역을 훨씬 크게(로그는 하단에 조금만) 잡는다. 탭을 옮긴
        # 뒤에도 사용자가 직접 드래그하면 그 탭에 있는 동안은 원하는 대로
        # 자유롭게 조절 가능 — 다른 탭으로 갔다가 돌아오면 다시 그 탭의
        # 기본 비율로 리셋된다.
        self._tab_top_ratio = {
            str(central_tab): 0.65,
            str(lcgv_tab): 0.65,
            str(posting_tab): 0.90,
        }
        self._tab_default_top_ratio = 0.82  # 위 딕셔너리에 없는 나머지 탭 기본값
        notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed)

        # ---- 중앙부처 탭 ----
        filter_frame = ttk.LabelFrame(central_tab, text="목록조회 필터 (선택)")
        filter_frame.pack(fill="x", padx=6, pady=6)

        ttk.Label(filter_frame, text="생애주기").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.life_var = tk.StringVar(value="")
        life_combo = ttk.Combobox(
            filter_frame, textvariable=self.life_var, width=12, state="readonly",
            values=[f"{k}:{v}" for k, v in LIFE_CYCLE_CODES.items()]
        )
        life_combo.current(0)
        life_combo.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(filter_frame, text="관심주제").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.theme_var = tk.StringVar(value="")
        theme_combo = ttk.Combobox(
            filter_frame, textvariable=self.theme_var, width=14, state="readonly",
            values=[f"{k}:{v}" for k, v in INTEREST_THEME_CODES.items()]
        )
        theme_combo.current(0)
        theme_combo.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(filter_frame, text="검색어").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.search_var = tk.StringVar(value="")
        ttk.Entry(filter_frame, textvariable=self.search_var, width=20).grid(
            row=0, column=5, padx=6, pady=6
        )

        central_btn_frame = ttk.Frame(central_tab)
        central_btn_frame.pack(fill="x", padx=6, pady=6)

        self.btn_list = ttk.Button(central_btn_frame, text="① 목록조회 시작", command=self._on_start_list)
        self.btn_list.pack(side="left", padx=4)

        self.btn_detail = ttk.Button(central_btn_frame, text="② 상세조회 시작", command=self._on_start_detail)
        self.btn_detail.pack(side="left", padx=4)

        self.download_files_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            central_btn_frame, text="공식자료(첨부 서식파일) 같이 받기", variable=self.download_files_var
        ).pack(side="left", padx=8)

        ttk.Label(central_tab, text=f"※ 일일 한도 - 목록조회 {DAILY_QUOTA_LIST}건 / 상세조회 {DAILY_QUOTA_DETAIL}건",
                  foreground="#666").pack(anchor="w", padx=6, pady=(0, 6))

        # ---- 지자체 탭 ----
        lcgv_filter_frame = ttk.LabelFrame(lcgv_tab, text="목록조회 필터 (선택)")
        lcgv_filter_frame.pack(fill="x", padx=6, pady=6)

        ttk.Label(lcgv_filter_frame, text="생애주기").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.lcgv_life_var = tk.StringVar(value="")
        lcgv_life_combo = ttk.Combobox(
            lcgv_filter_frame, textvariable=self.lcgv_life_var, width=12, state="readonly",
            values=[f"{k}:{v}" for k, v in LIFE_CYCLE_CODES.items()]
        )
        lcgv_life_combo.current(0)
        lcgv_life_combo.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(lcgv_filter_frame, text="가구상황").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.lcgv_household_var = tk.StringVar(value="")
        lcgv_household_combo = ttk.Combobox(
            lcgv_filter_frame, textvariable=self.lcgv_household_var, width=14, state="readonly",
            values=[f"{k}:{v}" for k, v in HOUSEHOLD_SITUATION_CODES.items()]
        )
        lcgv_household_combo.current(0)
        lcgv_household_combo.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(lcgv_filter_frame, text="관심주제").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.lcgv_theme_var = tk.StringVar(value="")
        lcgv_theme_combo = ttk.Combobox(
            lcgv_filter_frame, textvariable=self.lcgv_theme_var, width=14, state="readonly",
            values=[f"{k}:{v}" for k, v in INTEREST_THEME_CODES.items()]
        )
        lcgv_theme_combo.current(0)
        lcgv_theme_combo.grid(row=0, column=5, padx=6, pady=6)

        ttk.Label(lcgv_filter_frame, text="시도명").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.lcgv_ctpv_var = tk.StringVar(value="")
        ttk.Entry(lcgv_filter_frame, textvariable=self.lcgv_ctpv_var, width=12).grid(
            row=1, column=1, padx=6, pady=6
        )

        ttk.Label(lcgv_filter_frame, text="시군구명").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.lcgv_sgg_var = tk.StringVar(value="")
        ttk.Entry(lcgv_filter_frame, textvariable=self.lcgv_sgg_var, width=12).grid(
            row=1, column=3, padx=6, pady=6
        )

        ttk.Label(lcgv_filter_frame, text="검색어").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        self.lcgv_search_var = tk.StringVar(value="")
        ttk.Entry(lcgv_filter_frame, textvariable=self.lcgv_search_var, width=14).grid(
            row=1, column=5, padx=6, pady=6
        )

        lcgv_btn_frame = ttk.Frame(lcgv_tab)
        lcgv_btn_frame.pack(fill="x", padx=6, pady=6)

        self.btn_lcgv_list = ttk.Button(
            lcgv_btn_frame, text="③ 지자체 목록조회 시작", command=self._on_start_lcgv_list
        )
        self.btn_lcgv_list.pack(side="left", padx=4)

        self.btn_lcgv_detail = ttk.Button(
            lcgv_btn_frame, text="④ 지자체 상세조회 시작", command=self._on_start_lcgv_detail
        )
        self.btn_lcgv_detail.pack(side="left", padx=4)

        self.lcgv_download_files_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            lcgv_btn_frame, text="공식자료(첨부 서식파일) 같이 받기", variable=self.lcgv_download_files_var
        ).pack(side="left", padx=8)

        ttk.Label(lcgv_tab,
                  text=f"※ 일일 한도 - 목록조회 {DAILY_QUOTA_LCGV_LIST}건 / 상세조회 {DAILY_QUOTA_LCGV_DETAIL}건",
                  foreground="#666").pack(anchor="w", padx=6, pady=(0, 6))

        # ---- 리스트업 탭 (전체 현황: 총 몇건 중 몇건 수집, 오늘 신규 등) ----
        listing_tab.columnconfigure(0, weight=1)
        listing_tab.rowconfigure(2, weight=1)

        lfilter_f = ttk.Frame(listing_tab)
        lfilter_f.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        ttk.Label(lfilter_f, text="출처:").pack(side="left")
        self.listing_source_var = tk.StringVar(value="전체")
        ttk.Combobox(
            lfilter_f, textvariable=self.listing_source_var, width=10, state="readonly",
            values=["전체", "중앙부처", "지자체"]
        ).pack(side="left", padx=(4, 12))
        self.listing_source_var.trace_add("write", lambda *a: self._refresh_listing_tree())

        ttk.Label(lfilter_f, text="상태:").pack(side="left")
        self.listing_status_var = tk.StringVar(value="전체")
        status_combo = ttk.Combobox(
            lfilter_f, textvariable=self.listing_status_var, width=12, state="readonly",
            values=["전체", "미수집만", "오늘 신규만"]
        )
        status_combo.pack(side="left", padx=(4, 12))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_listing_tree())

        ttk.Label(lfilter_f, text="🔍 검색(서비스명):").pack(side="left", padx=(8, 4))
        self.listing_search_var = tk.StringVar(value="")
        listing_search_entry = ttk.Entry(lfilter_f, textvariable=self.listing_search_var, width=24)
        listing_search_entry.pack(side="left")
        listing_search_entry.bind("<Return>", lambda e: self._refresh_listing_tree())
        ttk.Button(lfilter_f, text="검색", command=self._refresh_listing_tree).pack(side="left", padx=(4, 0))
        ttk.Button(lfilter_f, text="✕", width=3,
                   command=lambda: (self.listing_search_var.set(""), self._refresh_listing_tree())
                   ).pack(side="left", padx=(2, 0))

        ttk.Label(lfilter_f, text="정렬:").pack(side="left", padx=(12, 4))
        self.listing_sort_var = tk.StringVar(value="우선순위 높은순")
        listing_sort_combo = ttk.Combobox(
            lfilter_f, textvariable=self.listing_sort_var, width=14, state="readonly",
            values=["우선순위 높은순", "최초발견일 최신순", "서비스명"]
        )
        listing_sort_combo.pack(side="left")
        listing_sort_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_listing_tree())

        listing_btn_f = ttk.Frame(listing_tab)
        listing_btn_f.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        ttk.Button(listing_btn_f, text="🔄 새로고침", command=self._refresh_listing_tree).pack(side="left")
        ttk.Button(listing_btn_f, text="📊 엑셀 내보내기", command=self._export_listing).pack(side="left", padx=(8, 0))
        ttk.Button(listing_btn_f, text="📋 선택 서비스명 복사",
                   command=self._copy_selected_listing_name).pack(side="left", padx=(8, 0))
        # [v7.15 신규] build_listing_rows()의 퍼지 매칭(v7.9)은 기본
        # 새로고침에서는 건너뛰도록 바꿨다(첫 스캔 속도 때문 — 자세한
        # 배경은 v7.15 changelog 참고). "이름은 다르지만 사실상 같은
        # 정책"까지 잡고 싶을 때만 이 버튼으로 한 번 켜서 돈다.
        ttk.Button(listing_btn_f, text="🔁 중복 정책 재검사(느림, 이름 유사까지 확인)",
                   command=self._recheck_similar_policies).pack(side="left", padx=(8, 0))
        # [v7.16 신규] 버튼을 눌러도 화면에 아무 변화가 없어 뭘 하는지
        # 알기 어렵다는 리포트 반영 — 키워드 리서치 상태 표시
        # (research_status_var)와 동일한 패턴으로 진행/완료를 눈에
        # 띄게 표시한다.
        self.similar_recheck_status_var = tk.StringVar(value="")
        ttk.Label(listing_btn_f, textvariable=self.similar_recheck_status_var,
                  foreground="#1565C0", font=("맑은 고딕", 9, "bold")).pack(side="left", padx=(8, 0))

        self.listing_count_var = tk.StringVar(value="")
        ttk.Label(listing_btn_f, textvariable=self.listing_count_var,
                  foreground="darkblue", font=("맑은 고딕", 9, "bold")).pack(side="right")

        cols = ("우선순위", "출처", "서비스명", "서비스ID", "연관정책", "수집상태", "최초발견일")
        self.listing_tree = ttk.Treeview(listing_tab, columns=cols, show="headings", height=18)
        widths = [70, 70, 560, 130, 110, 90, 110]
        for col, w in zip(cols, widths):
            self.listing_tree.heading(col, text=col)
            self.listing_tree.column(col, width=w, anchor="w")

        listing_vsb = ttk.Scrollbar(listing_tab, orient="vertical", command=self.listing_tree.yview)
        self.listing_tree.configure(yscrollcommand=listing_vsb.set)
        self.listing_tree.grid(row=2, column=0, sticky="nsew", padx=(6, 0), pady=(0, 6))
        listing_vsb.grid(row=2, column=1, sticky="ns", pady=(0, 6))

        self.listing_tree.tag_configure("new_today", background="#FFF9C4")
        self.listing_tree.tag_configure("not_downloaded", foreground="gray")
        self.listing_tree.tag_configure("excluded", foreground="#B00020")

        # ---- 포스팅 관리 탭 ----
        # [v7.2 신규] 콘텐츠(트리+키워드 리서치+작업 순서 ⓪~⑧ 버튼들+
        # 기타 관리)가 창 높이보다 길어지면 아래쪽 버튼들이 화면 밖으로
        # 밀려 안 보이는 문제가 있었다(이 탭 하나에 위젯이 특히 많이
        # 몰려 있음) — 정책뉴스 서브프로그램 TAB2(분석준비)와 동일한
        # 스크롤 캔버스 패턴을 그대로 이식. 아래부터는 posting_tab이
        # 아니라 이 스크롤 프레임(pt) 위에 그린다 — posting_tab 자체는
        # notebook에 이미 등록된 바깥 탭 프레임이므로 그대로 두고, 그
        # 안에 캔버스+스크롤바를 깔고 실제 콘텐츠는 캔버스 위의 내부
        # 프레임(pt)에 얹는다.
        posting_tab.rowconfigure(0, weight=1)
        posting_tab.columnconfigure(0, weight=1)

        pt_canvas = tk.Canvas(posting_tab, highlightthickness=0)
        pt_vscroll = ttk.Scrollbar(posting_tab, orient="vertical", command=pt_canvas.yview)
        pt_canvas.configure(yscrollcommand=pt_vscroll.set)
        pt_canvas.grid(row=0, column=0, sticky="nsew")
        pt_vscroll.grid(row=0, column=1, sticky="ns")

        pt = ttk.Frame(pt_canvas)
        pt_f_id = pt_canvas.create_window((0, 0), window=pt, anchor="nw")

        def _pt_on_f_configure(event):
            pt_canvas.configure(scrollregion=pt_canvas.bbox("all"))
        pt.bind("<Configure>", _pt_on_f_configure)

        def _pt_on_canvas_configure(event):
            pt_canvas.itemconfig(pt_f_id, width=event.width)
        pt_canvas.bind("<Configure>", _pt_on_canvas_configure)

        def _pt_on_mousewheel(event):
            pt_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _pt_bind_wheel(event):
            pt_canvas.bind_all("<MouseWheel>", _pt_on_mousewheel)

        def _pt_unbind_wheel(event):
            pt_canvas.unbind_all("<MouseWheel>")

        pt_canvas.bind("<Enter>", _pt_bind_wheel)
        pt_canvas.bind("<Leave>", _pt_unbind_wheel)

        pt.columnconfigure(0, weight=1)
        pt.rowconfigure(3, weight=1)

        # 포스팅완료 보호 안내
        pwarn_f = tk.Frame(pt, bg="#FFF3CD", padx=8, pady=5)
        pwarn_f.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(6, 4))
        tk.Label(pwarn_f,
                 text="⚠️  실제 네이버 포스팅은 별도 프로그램에서 진행합니다. 여기서는 포스팅을 마친 자료를 "
                      "'📤 포스팅완료'로 표시해 중복 작업을 막는 용도로만 씁니다. 포스팅완료는 다른 상태로 되돌릴 수 없습니다.",
                 bg="#FFF3CD", fg="#856404", font=("맑은 고딕", 9, "bold"),
                 wraplength=900, justify="left").pack(side="left")

        # [Ver10.08] 자리 예약 안내 → 작업 순서 한 줄 안내(가치판단 기준은 STEP 1 빠른 판정이 맡는다)
        pplaceholder_f = tk.Frame(pt, bg="#EEF2FF", padx=8, pady=5)
        pplaceholder_f.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        tk.Label(pplaceholder_f,
                 text="순서: 목록에서 서비스 선택 → STEP 1 포스팅 가치 빠른 판단 → STEP 2 본 분석 → "
                      "STEP 3 제목 확정 → STEP 4 초안 작성 → 최종각색 → 5)인포그래픽 작성 → 6)키워드 등록. "
                      "작업 중 그만둘 글은 목록 아래 '⏭ 이 글 패스'.",
                 bg="#EEF2FF", fg="#3730A3", font=("맑은 고딕", 9),
                 wraplength=900, justify="left").pack(side="left")

        pfilter_f = ttk.Frame(pt)
        pfilter_f.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))

        ttk.Label(pfilter_f, text="출처:").pack(side="left")
        self.posting_source_var = tk.StringVar(value="중앙부처")
        ttk.Combobox(
            pfilter_f, textvariable=self.posting_source_var, width=10, state="readonly",
            values=["전체", "중앙부처", "지자체", "허브"]
        ).pack(side="left", padx=(4, 12))
        self.posting_source_var.trace_add("write", lambda *a: self._refresh_posting_tree())
        ttk.Button(pfilter_f, text="➕ 허브(종합) 항목 추가",
                   command=self._open_add_hub_service_dialog).pack(side="left", padx=(0, 6))

        ttk.Label(pfilter_f, text="상태:").pack(side="left")
        self.posting_status_filter_var = tk.StringVar(value="패스 제외(기본)")
        posting_status_combo = ttk.Combobox(
            pfilter_f, textvariable=self.posting_status_filter_var, width=16, state="readonly",
            values=["전체", "작업중만", "패스 제외(기본)", "수집완료만"] + POSTING_STATUS_LIST
        )
        posting_status_combo.pack(side="left", padx=(4, 12))
        posting_status_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_posting_tree())

        ttk.Label(pfilter_f, text="🔍 검색(서비스명):").pack(side="left", padx=(8, 4))
        self.posting_search_var = tk.StringVar(value="")
        posting_search_entry = ttk.Entry(pfilter_f, textvariable=self.posting_search_var, width=22)
        posting_search_entry.pack(side="left")
        posting_search_entry.bind("<Return>", lambda e: self._refresh_posting_tree())
        ttk.Button(pfilter_f, text="검색", command=self._refresh_posting_tree).pack(side="left", padx=(4, 0))
        ttk.Button(pfilter_f, text="✕", width=3,
                   command=lambda: (self.posting_search_var.set(""), self._refresh_posting_tree())
                   ).pack(side="left", padx=(2, 0))

        ttk.Label(pfilter_f, text="정렬:").pack(side="left", padx=(12, 4))
        self.posting_sort_var = tk.StringVar(value="우선순위 높은순")
        posting_sort_combo = ttk.Combobox(
            pfilter_f, textvariable=self.posting_sort_var, width=14, state="readonly",
            values=["우선순위 높은순", "최초발견일 최신순", "서비스명"]
        )
        posting_sort_combo.pack(side="left")
        posting_sort_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_posting_tree())

        cols2 = ("우선순위", "출처", "서비스명", "서비스ID", "연관정책", "공식자료", "포스팅상태", "최초발견일")
        self.posting_tree = ttk.Treeview(pt, columns=cols2, show="headings", height=14)
        widths2 = [70, 70, 440, 130, 110, 60, 150, 110]
        for col, w in zip(cols2, widths2):
            self.posting_tree.heading(col, text=col)
            self.posting_tree.column(col, width=w, anchor="w")

        posting_vsb = ttk.Scrollbar(pt, orient="vertical", command=self.posting_tree.yview)
        self.posting_tree.configure(yscrollcommand=posting_vsb.set)
        self.posting_tree.grid(row=3, column=0, sticky="nsew", padx=(6, 0), pady=(0, 6))
        posting_vsb.grid(row=3, column=1, sticky="ns", pady=(0, 6))

        # [v7.7 버그 수정] 위 pt_canvas의 "<Enter>일 때 bind_all"
        # 방식은 캔버스 전체(트리 포함) 어디서나 휠 = 페이지 스크롤로
        # 잡는다. 그런데 트리(목록)는 행이 14개 초과면 자기 자신의
        # 세로 스크롤이 필요한 위젯인데, bind_all이 항상 이겨서 트리
        # 위에서 휠을 굴려도 트리는 안 움직이고 페이지 전체만 스크롤
        # 되는 문제가 있었다(사용자 리포트: "목록그리드안에서 스크롤
        # 하면 왜 전체가 다 스크롤돼"). 트리 위에 마우스가 있는 동안만
        # 페이지 스크롤(bind_all)을 잠깐 풀고 휠을 트리 자신의
        # yview_scroll로 돌려, 트리를 벗어나면 다시 페이지 스크롤로
        # 되돌린다.
        def _tree_on_mousewheel(event):
            self.posting_tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _tree_bind_wheel(event):
            pt_canvas.unbind_all("<MouseWheel>")
            self.posting_tree.bind("<MouseWheel>", _tree_on_mousewheel)

        def _tree_unbind_wheel(event):
            self.posting_tree.unbind("<MouseWheel>")
            pt_canvas.bind_all("<MouseWheel>", _pt_on_mousewheel)

        self.posting_tree.bind("<Enter>", _tree_bind_wheel)
        self.posting_tree.bind("<Leave>", _tree_unbind_wheel)

        self.posting_tree.tag_configure("published", background="#A5D6A7")  # 📤 포스팅완료 — 가장 진한 연두(확실히 끝난 상태)
        self.posting_tree.tag_configure("waiting", background="#E8F5E9")  # 🟢 포스팅대기 — 옅은 연두(완료보다는 한 단계 약하게)
        self.posting_tree.tag_configure("in_progress", background="#FFF3B0")  # 가치판단대기~인포그래픽준비중까지는 동일 노랑(작업중)
        self.posting_tree.tag_configure("pass", background="#F5F5F5", foreground="gray")
        self.posting_tree.tag_configure("excluded", foreground="#B00020")
        self.posting_tree.bind("<<TreeviewSelect>>", lambda e: self._on_posting_select())

        # [Ver10.08] 작업 순서대로 STEP 1~5. Claude 대화창 하나에서 붙여넣기 세 번으로 본 분석까지 간다:
        # 빠른 판정 복사 → (답 복사) 판정 읽기 = 키워드 리서치·경쟁 블로그 스크랩 자동 → 본 분석 복사 →
        # (답 복사) 결과 읽기. AI가 자료·키워드를 요청하면 "결과 읽어 저장"이 알아서 안내한다.
        # 자동 준비 결과와 실패 때 고치는 버튼은 STEP 1 안에 있다.
        def _next_hint(parent, text):
            ttk.Label(parent, text=text, foreground="gray").pack(side="left", padx=(8, 0), pady=6)

        # [Ver10.08] "기타 관리" 칸을 없애고 버튼을 쓰는 자리로 옮겼다(사용자: 각자 필요한 위치에).
        # 목록 도구(새로고침·엑셀·건수)는 목록 바로 아래.
        list_bar = ttk.Frame(pt)
        list_bar.grid(row=4, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        ttk.Button(list_bar, text="🔄 새로고침", command=self._refresh_posting_tree).pack(side="left")
        ttk.Button(list_bar, text="📊 포스팅 이력 엑셀 저장",
                   command=self._export_posting_history).pack(side="left", padx=(6, 0))
        ttk.Button(list_bar, text="📁 자료 폴더 열기",
                   command=self._open_selected_posting_folder).pack(side="left", padx=(6, 0))
        # [Ver10.09] 예전 STEP 5 상태 콤보 대신 — 검토하다 그만둘 글만 여기서 패스(정책뉴스 "이 글 패스"와 같은 컨셉).
        # 나머지 상태는 단계 버튼이 자동으로 바꾸고, 포스팅대기·완료는 6)키워드 등록·7)이력관리가 맡는다.
        ttk.Button(list_bar, text="⏭ 이 글 패스",
                   command=self._pass_selected_posting).pack(side="left", padx=(16, 0))
        self.posting_count_var = tk.StringVar(value="")
        ttk.Label(list_bar, textvariable=self.posting_count_var,
                  foreground="darkblue", font=("맑은 고딕", 9, "bold")).pack(side="left", padx=(12, 0))

        # ---- STEP 1 빠른 판정·자료 준비 ----
        # [Ver10.08] 버튼 이름 규칙(사용자): 📋 = 클립보드로 복사 — "자료+프롬프트"는 서비스 자료까지,
        # "프롬프트"는 지시문만, (새창)/(현재창)은 붙여넣을 Claude 대화창. 💾 … 저장(메모리값) = Claude 답을
        # 복사해 둔 클립보드(메모리값)에서 읽어 저장. "공식자료" = 복지로 첨부 서식자료(사업안내·신청서 등).
        # 자동 준비 결과(리서치·경쟁 블로그)와 실패했을 때 손으로 고치는 버튼은 STEP 1 안에 둔다 —
        # 예전 접힌 "수동 보조" 칸은 실패해도 어디로 가야 할지 안 보였다(사용자 지적).
        quick_f = ttk.LabelFrame(pt, text="STEP 1 — 포스팅 가치 빠른 판단")
        quick_f.grid(row=5, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        quick_f.columnconfigure(0, weight=1)
        # 줄 1 — 복사
        quick_row = ttk.Frame(quick_f)
        quick_row.grid(row=0, column=0, sticky="ew")
        ttk.Button(quick_row, text="📋 원문자료 + 프롬프트 복사",
                   command=self._copy_quick_judgment_prompt).pack(side="left", padx=(6, 4), pady=(6, 2))
        _next_hint(quick_row, "→ Claude 새 대화창에 붙여넣기")
        # 줄 2 — 저장(+ 자료 자동 준비)
        quick_save_row = ttk.Frame(quick_f)
        quick_save_row.grid(row=1, column=0, sticky="ew")
        ttk.Button(quick_save_row, text="💾 판정결과 저장(메모리값 자동저장)",
                   command=lambda: self._read_clipboard_result("quick_judgment")).pack(
            side="left", padx=(6, 6), pady=(2, 4))
        _next_hint(quick_save_row, "Claude 답을 복사한 뒤 누르기 → 진행이면 키워드 리서치·경쟁 블로그 수집이 자동으로 시작됩니다")
        # [Ver10.10] 결과는 "결과:" 두 줄(판정·자동 수집)만 보이고, 다시 하는 줄은 실패했을 때만 나타난다.
        # 경쟁 블로그 본문·주소 칸은 "보기"를 눌러야 펼친다(사용자: 결과 글이 버튼보다 많아 헷갈림).
        self.quick_status_var = tk.StringVar(value="")
        ttk.Label(quick_f, textvariable=self.quick_status_var, foreground="#1565C0",
                  font=("맑은 고딕", 9, "bold"), wraplength=1100, justify="left").grid(
            row=2, column=0, sticky="w", padx=6, pady=(0, 2))
        self.auto_prep_status_var = tk.StringVar(value="")
        ttk.Label(quick_f, textvariable=self.auto_prep_status_var, foreground="#0D6E0D",
                  font=("맑은 고딕", 9, "bold"), wraplength=1100, justify="left").grid(
            row=3, column=0, sticky="w", padx=6, pady=(0, 4))


        # 경쟁 블로그 — 한 줄 요약 + 보기. 0개(실패)면 직접 고르는 줄이 저절로 펼쳐진다.
        blog_f = ttk.Frame(quick_f)
        blog_f.grid(row=5, column=0, sticky="ew", padx=6, pady=(4, 6))
        blog_f.columnconfigure(0, weight=1)
        blog_bar = ttk.Frame(blog_f)
        blog_bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(blog_bar, text="경쟁 블로그:").pack(side="left")
        self.competitor_blog_info_var = tk.StringVar(value="")
        ttk.Label(blog_bar, textvariable=self.competitor_blog_info_var,
                  foreground="#1565C0").pack(side="left", padx=(4, 8))
        self.blog_view_btn = ttk.Button(blog_bar, text="보기", width=6,
                                        command=lambda: self._show_blog_panel(not self._blog_panel_open))
        self.blog_view_btn.pack(side="left")
        ttk.Label(blog_bar, text="(글 구성 참고용 — 없어도 STEP 2로 가도 됩니다)",
                  foreground="gray").pack(side="left", padx=(8, 0))
        # 펼치는 칸: 직접 고르기(블로그탭 열기 → 주소 → 스크랩) + 본문
        self.blog_panel_f = blog_panel = ttk.Frame(blog_f)
        blog_panel.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        blog_panel.columnconfigure(1, weight=1)
        # 직접 고를 때 — 검색 키워드 칸의 첫 키워드(메인)로 블로그탭을 연다.
        ttk.Button(blog_panel, text="🔍 블로그탭 열기(메인 키워드)",
                   command=self._open_blog_tab_with_main_keyword).grid(row=0, column=0, sticky="nw", padx=(0, 6))
        self.competitor_url_text = tk.Text(blog_panel, height=2, wrap="none", font=("맑은 고딕", 9))
        self.competitor_url_text.grid(row=0, column=1, sticky="ew")
        ttk.Button(blog_panel, text="🕸 주소 스크랩해서 채우기",
                   command=self._scrape_competitor_urls).grid(row=0, column=2, sticky="n", padx=(6, 0))
        ttk.Label(blog_panel, text="↑ 고른 글 주소를 한 줄에 하나씩", foreground="gray").grid(
            row=1, column=1, sticky="w")
        ttk.Button(blog_panel, text="지우기",
                   command=self._clear_competitor_blogs).grid(row=2, column=0, sticky="nw", pady=(4, 0))
        self.competitor_blog_text = scrolledtext.ScrolledText(blog_panel, wrap="word", height=6,
                                                              font=("맑은 고딕", 9))
        self.competitor_blog_text.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(4, 0))
        self.competitor_blog_text.bind("<FocusOut>", lambda e: self._save_competitor_blogs())
        self._competitor_blog_serv = None   # 칸에 지금 들어 있는 글의 서비스(서비스별로 따로 저장)
        self._blog_panel_open = True
        self._show_blog_panel(False)

        # ---- STEP 2 본 분석 ----
        main_f = ttk.LabelFrame(pt, text="STEP 2 — 가치판단 · 제목 후보 (공식자료 확인)")
        main_f.grid(row=6, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        main_f.columnconfigure(0, weight=1)
        # 줄 1 — 본 분석 복사(+ 공식자료 올리기)
        main_row = ttk.Frame(main_f)
        main_row.grid(row=0, column=0, sticky="ew")
        ttk.Button(main_row, text="📋 판정결과·키워드 리서치 + 프롬프트 복사",
                   command=lambda: self._copy_main_analysis_prompt(same_chat=True)).pack(
            side="left", padx=(6, 4), pady=(6, 2))
        ttk.Button(main_row, text="📂 공식자료 폴더 열기",
                   command=self._open_selected_attachments_folder).pack(side="left", padx=(0, 4), pady=(6, 2))
        _next_hint(main_row, "→ 빠른 판단을 한 대화창에 붙여넣고, 팝업이 말한 공식자료를 올리기")

        # 줄 2 — 키워드 리서치(정책뉴스 STEP 1.5와 같은 줄, 늘 보임). [Ver10.10] 리서치하는 곳은 여기 한 곳:
        # STEP 1 판정결과 저장 때 이 칸의 키워드로 자동 리서치, Claude가 다시 요청하면 가치판단 저장이 그 키워드로
        # 바꿔 리서치하고 "AI에게 결과 전달" 내용을 클립보드에 넣는다. 직접 고쳐 실행해도 된다.
        kw_f = ttk.LabelFrame(main_f, text="키워드 리서치 — STEP 1 저장 때 자동 실행 · Claude가 다시 요청하면 그 키워드로 자동 실행 · 직접 고쳐 실행해도 됨", padding=4)
        kw_f.grid(row=1, column=0, sticky="ew", padx=6, pady=(4, 2))
        kw_f.columnconfigure(1, weight=1)
        ttk.Label(kw_f, text="검색 키워드:").grid(row=0, column=0, sticky="w")
        # [v6.9] 콤마(,)로 구분하면 여러 키워드를 한 번에 리서치한다.
        self.research_keyword_var = tk.StringVar(value="")
        ttk.Entry(kw_f, textvariable=self.research_keyword_var).grid(row=0, column=1, sticky="ew", padx=(5, 4))
        ttk.Button(kw_f, text="✖ 입력 지우기",
                   command=self._clear_research_keyword).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(kw_f, text="🔍 키워드 리서치 실행",
                   command=lambda: self._run_keyword_research("prep")).grid(row=0, column=3)
        # [v7.0, 정책뉴스 Ver8.22에서 이식] 캐시와 별도로 바로 조회해 팝업.
        ttk.Button(kw_f, text="🔍 검색량·자동완성 조회",
                   command=lambda: self._show_research_summary_popup("prep")).grid(row=0, column=4, padx=(8, 0))
        ttk.Button(kw_f, text="📋 AI에게 결과 전달",
                   command=lambda: self._copy_research_reply_for_posting("prep")).grid(row=0, column=5, padx=(8, 0))
        self.research_status_var = tk.StringVar(value="")
        ttk.Label(kw_f, textvariable=self.research_status_var, foreground="#1565C0",
                  wraplength=1000, justify="left").grid(row=1, column=1, columnspan=5, sticky="w", pady=(2, 0))
        # 예전 "AI 요청 키워드" 칸은 이 칸으로 합쳤다 — 옛 이름으로 부르는 코드도 같은 칸을 쓴다.
        self.ai_kw_var = self.research_keyword_var
        self.ai_kw_status_var = self.research_status_var
        self._auto_keywords = ""   # STEP 1 자동 리서치 키워드(본 분석·초안 복사에 함께 넣음)

        # 줄 3 — 결과 저장
        main_save_row = ttk.Frame(main_f)
        main_save_row.grid(row=2, column=0, sticky="ew")
        ttk.Button(main_save_row, text="💾 가치판단 저장(메모리값 자동저장)",
                   command=lambda: self._read_clipboard_result("value_judgment")).pack(
            side="left", padx=(6, 6), pady=(4, 6))
        _next_hint(main_save_row, "Claude 답을 복사한 뒤 누르기 — 결과면 저장 → STEP 3, 자료·키워드 리서치 요청이면 할 일을 알려 줌")

        # [v7.17 신규, 정책뉴스 STEP4에서 이식 — 이번엔 제목에 올바르게
        # 적용] 지난 버전(v7.4)에서는 "후보추천"을 키워드 쪽에 잘못
        # 이식했었다(재조사 요청 키워드는 이미 별도 확정 절차가 있어
        # 후보 개념이 아님 — 사용자 지적으로 정정). 정책뉴스 STEP4가
        # 실제로 하는 일은 "AI가 낸 제목 후보 여러 개를 실측 검색해
        # 등급 매기고 사람이 확정"이므로, 그 컨셉을 제목에 적용한다.
        #
        # 복지로 초안작성 프롬프트는 제목을 그 자리에서 1개로 즉시
        # 확정하는 구조라(정책뉴스 A처럼 후보 나열 구조가 아님) 이걸
        # 후보 나열형으로 통째로 바꾸는 대신, "초안은 사실상 최종각색과
        # 거의 같다(초안에 페르소나만 입혀 각색)"는 점에 착안해 가치
        # 판단 프롬프트 V3([2-A단계], 같은 날 신설)가 핵심 키워드 확정
        # 직후 제목 후보까지 내도록 했다 — 정책뉴스의 "A(전략+제목)→
        # B(글쓰기, 제목 그대로 받아씀)" 관계를 "가치판단(키워드+제목)→
        # 초안작성(제목 그대로 받아씀, V4로 같이 개정)"에 대응시켰다.
        # 여기서 확정한 제목은 confirmed_titles.json에 저장되고,
        # build_draft_prompt_package()가 "③ 초안작성 프롬프트 복사"를
        # 누를 때 자동으로 함께 실어 보낸다.
        # [Ver10.08] STEP 3으로 — 본 분석 바로 아래(실행 순서대로).
        titlecand_f = ttk.LabelFrame(pt, text="STEP 3 — 제목 확정 (확정한 제목은 STEP 4 초안에 그대로 전달)")
        titlecand_f.grid(row=8, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        titlecand_f.columnconfigure(1, weight=1)

        ttk.Button(titlecand_f, text="📋 제목 후보 불러오기",
                   command=self._extract_title_candidates_for_posting).grid(
            row=0, column=0, columnspan=5, sticky="w", padx=6, pady=(6, 2))
        ttk.Label(titlecand_f,
                  text="가치판단을 저장한 뒤 누르면 후보가 채워집니다. 본문 적합도를 먼저 보고, "
                       "필요하면 🔍 블로그·🔍 앞구(첫 쉼표 앞)·🔍 뒷구(첫 쉼표 뒤)로 직접 확인한 뒤 라디오버튼으로 "
                       "확정하면 STEP 4 초안 복사 때 이 제목이 자동으로 함께 실려서 초안이 이 제목을 그대로 씁니다.",
                  foreground="gray", wraplength=880, justify="left").grid(
            row=1, column=0, columnspan=5, sticky="w", padx=6, pady=(0, 6))

        self.title_cand_choice = tk.StringVar(value="")
        self.title_cand_label_vars = [tk.StringVar(value="") for _ in range(4)]
        self.title_cand_texts = ["" for _ in range(4)]
        # [v7.19 신규] 후보별 "도입부 첫 문장 지시"를 title_cand_texts와
        # 같은 인덱스로 별도 보관 — 라벨에는 안 띄우고(화면이 너무
        # 길어짐), 확정 시 save_confirmed_title()에 함께 넘기는 용도.
        self.title_cand_intros = ["" for _ in range(4)]
        self.title_cand_manual_var = tk.StringVar(value="")
        self.title_cand_reasons = ["" for _ in range(4)]
        self.title_cand_choice.trace_add("write", lambda *_a: self._on_title_cand_choice())

        titlecand_rows_f = ttk.Frame(titlecand_f)
        titlecand_rows_f.grid(row=2, column=0, columnspan=5, sticky="ew", padx=6)
        titlecand_rows_f.columnconfigure(1, weight=1)
        for i in range(4):
            ttk.Radiobutton(titlecand_rows_f, text="선택",
                             variable=self.title_cand_choice, value=str(i)).grid(
                row=i, column=0, sticky="w", pady=2)
            ttk.Label(titlecand_rows_f, textvariable=self.title_cand_label_vars[i],
                      wraplength=560, justify="left").grid(
                row=i, column=1, sticky="w", padx=(4, 4))
            ttk.Button(titlecand_rows_f, text="🔍 블로그",
                       command=lambda idx=i: self._open_naver_search_title_candidate(idx, blog=True)
                       ).grid(row=i, column=2, padx=(0, 2))
            # [Ver10.08] 🔍 통합 → 📋 제목 복사(정책뉴스 Ver10.09와 같음)
            ttk.Button(titlecand_rows_f, text="📋 제목 복사",
                       command=lambda idx=i: self._copy_candidate_title(idx)
                       ).grid(row=i, column=3, padx=(0, 2))
            ttk.Button(titlecand_rows_f, text="🔍 앞구",
                       command=lambda idx=i: self._open_naver_search_title_candidate(idx, front=True)
                       ).grid(row=i, column=4, padx=(0, 2))
            ttk.Button(titlecand_rows_f, text="🔍 뒷구",
                       command=lambda idx=i: self._open_naver_search_title_candidate(idx, back=True)
                       ).grid(row=i, column=5, padx=(0, 8))

        titlecand_manual_f = ttk.Frame(titlecand_f)
        titlecand_manual_f.grid(row=3, column=0, columnspan=5, sticky="ew", padx=6, pady=(4, 0))
        ttk.Radiobutton(titlecand_manual_f, text="직접 입력",
                         variable=self.title_cand_choice, value="manual").pack(side="left")
        ttk.Entry(titlecand_manual_f, textvariable=self.title_cand_manual_var, width=50).pack(
            side="left", padx=(4, 4), fill="x", expand=True)
        # [Ver9.32] 직접 입력 제목 글자수 — 후보 4개 라벨의 "(OO자)"와 같은 기준
        self.title_manual_len_var = tk.StringVar(value="(0자)")
        ttk.Label(titlecand_manual_f, textvariable=self.title_manual_len_var, width=9).pack(
            side="left", padx=(0, 6))
        self.title_cand_manual_var.trace_add("write", lambda *_a: self._update_title_manual_len())
        ttk.Button(titlecand_manual_f, text="🔍 블로그",
                   command=lambda: self._open_naver_search_title_manual(blog=True)).pack(
            side="left", padx=(0, 2))
        ttk.Button(titlecand_manual_f, text="📋 제목 복사",
                   command=self._copy_manual_title).pack(side="left", padx=(0, 2))
        ttk.Button(titlecand_manual_f, text="🔍 앞구",
                   command=lambda: self._open_naver_search_title_manual(front=True)).pack(side="left", padx=(0, 2))
        ttk.Button(titlecand_manual_f, text="🔍 뒷구",
                   command=lambda: self._open_naver_search_title_manual(back=True)).pack(side="left", padx=(0, 8))

        titlecand_action_f = ttk.Frame(titlecand_f)
        titlecand_action_f.grid(row=5, column=0, columnspan=5, sticky="w", padx=6, pady=(8, 6))
        ttk.Button(titlecand_action_f, text="✅ 최종 확정",
                   command=self._confirm_title_candidate).pack(side="left", padx=(0, 8))
        ttk.Button(titlecand_action_f, text="🗑 확정 취소",
                   command=self._clear_confirmed_title).pack(side="left", padx=(0, 8))
        self.title_cand_status_var = tk.StringVar(value="")
        ttk.Label(titlecand_action_f, textvariable=self.title_cand_status_var,
                  foreground="darkgreen", font=("맑은 고딕", 9, "bold")).pack(side="left")

        # ---- STEP 4 초안·최종각색 ----
        # [Ver9.30] GPT용 최종각색 경로는 폐기 — Claude 2차 각색 하나만 쓴다.
        write_f = ttk.LabelFrame(pt, text="STEP 4 — 초안 작성 → 최종각색")
        write_f.grid(row=9, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        # 초안: 복사 줄 → 저장 줄, 최종각색: 복사 줄 → 저장 줄
        draft_row = ttk.Frame(write_f)
        draft_row.pack(fill="x")
        ttk.Label(draft_row, text="초안", width=7).pack(side="left", padx=(6, 0))
        ttk.Button(draft_row, text="📋 확정제목 + 프롬프트 복사",
                   command=self._copy_draft_prompt_only).pack(side="left", padx=(0, 4), pady=(6, 2))
        _next_hint(draft_row, "→ 가치판단을 한 대화창에 붙여넣기")
        draft_save_row = ttk.Frame(write_f)
        draft_save_row.pack(fill="x")
        ttk.Label(draft_save_row, text="", width=7).pack(side="left", padx=(6, 0))
        ttk.Button(draft_save_row, text="💾 초안 저장(메모리값 자동저장)",
                   command=lambda: self._read_clipboard_result("draft")).pack(side="left", padx=(0, 6), pady=(2, 6))
        _next_hint(draft_save_row, "Claude 답을 복사한 뒤 누르기 — 자료 요청·정보 부족 판정이면 저장하지 않고 안내")

        final_row = ttk.Frame(write_f)
        final_row.pack(fill="x")
        ttk.Label(final_row, text="최종각색", width=7).pack(side="left", padx=(6, 0))
        # [Ver10.10] 같은 대화창용(자료를 다시 보내지 않아 한도 절약 — 정책뉴스 "간소화 복사")을 되살림
        ttk.Button(final_row, text="📋 프롬프트 복사",
                   command=self._copy_claude_second_stage_prompt_only).pack(side="left", padx=(0, 4), pady=(4, 2))
        ttk.Button(final_row, text="📋 초안 + 프롬프트 복사",
                   command=self._copy_claude_second_stage_prompt).pack(side="left", padx=(0, 4), pady=(4, 2))
        _next_hint(final_row, "프롬프트 복사 = 초안을 쓴 같은 대화창에 이어서(자료 중복 없이 한도 절약) / 초안 + = 새 대화창")
        final_save_row = ttk.Frame(write_f)
        final_save_row.pack(fill="x")
        ttk.Label(final_save_row, text="", width=7).pack(side="left", padx=(6, 0))
        ttk.Button(final_save_row, text="💾 최종각색 저장(메모리값 자동저장)",
                   command=lambda: self._read_clipboard_result("final_adaptation")).pack(
            side="left", padx=(0, 4), pady=(2, 6))
        ttk.Button(final_save_row, text="📝 최종원고(.md) 폴더 열기",
                   command=self._open_final_posts_folder).pack(side="left", padx=(0, 6), pady=(2, 6))
        _next_hint(final_save_row, "확인 창(제목·출처 점검, 문단 정리)에서 저장")
        # [Ver10.09] 예전 STEP 5(상태 콤보 + 포스팅 전 확인)를 없애고, 포스팅 전 확인은 최종각색 바로 아래로,
        # 다음 단계는 정책뉴스처럼 "→ 인포그래픽으로 이동" 버튼으로.
        final_check_row = ttk.Frame(write_f)
        final_check_row.pack(fill="x")
        ttk.Label(final_check_row, text="", width=7).pack(side="left", padx=(6, 0))
        ttk.Label(final_check_row, text="포스팅 전 확인:").pack(side="left", pady=(0, 6))
        # [v7.0, 정책뉴스 TAB4 '제목 검색'에서 이식] 최종각색 제목이 이미 선점됐는지 — 비로그인 새 창.
        ttk.Button(final_check_row, text="🔍 제목 블로그검색",
                   command=self._open_naver_blog_search_for_title).pack(side="left", padx=(4, 4), pady=(0, 6))
        ttk.Button(final_check_row, text="📋 제목 복사",
                   command=self._copy_final_title).pack(side="left", padx=(0, 4), pady=(0, 6))
        ttk.Button(final_check_row, text="🔗 연관 정책 확인",
                   command=self._show_related_policies_popup_for_posting).pack(side="left", padx=(0, 16), pady=(0, 6))
        ttk.Button(final_check_row, text="→ 인포그래픽으로 이동",
                   command=self._goto_infographic_tab).pack(side="left", pady=(0, 6))


        # ---- 인포그래픽 작성 탭 ----
        # 정책뉴스 프로그램 TAB4의 "썸네일·소제목 제목 목록" 방식을 그대로
        # 이식 — 완성된 글에서 제목들을 자동으로 뽑아 항목별 "복사" 버튼을
        # 붙여둔다. GPT에서 이미지를 생성할 때 이 버튼으로 정확한 텍스트를
        # 바로 복사해 파일명으로 쓸 수 있어서, 매번 본문에서 소제목을 찾아
        # 직접 타이핑하던 불편함이 없어진다.
        infographic_tab.columnconfigure(0, weight=1)
        infographic_tab.rowconfigure(2, weight=1)

        ig_top_f = ttk.Frame(infographic_tab)
        ig_top_f.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))
        ttk.Label(ig_top_f, text="대상 서비스:").pack(side="left")
        self.ig_service_var = tk.StringVar(value="")
        self.ig_service_combo = ttk.Combobox(ig_top_f, textvariable=self.ig_service_var,
                                              width=70, state="readonly")
        self.ig_service_combo.pack(side="left", padx=(6, 8))
        self.ig_service_combo.bind("<<ComboboxSelected>>", lambda e: (self._generate_infographic_title_list(),
                                                                     self._card_show_folder()))
        ttk.Button(ig_top_f, text="🔄 대상 목록 새로고침",
                   command=self._refresh_ig_service_list).pack(side="left", padx=(0, 8))
        ttk.Button(ig_top_f, text="📁 최종각색된 MD파일이 저장된 폴더 열기",
                   command=self._open_ig_service_folder).pack(side="left")

        # [Ver10.08] 인포그래픽 프롬프트 복사를 4)포스팅 관리 탭에서 이 탭으로 옮겼다(정책뉴스처럼
        # 인포그래픽은 이 탭에서). 위 "대상 서비스"를 기준으로 복사한다.
        ig_prompt_f = ttk.Frame(infographic_tab)
        ig_prompt_f.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        ttk.Button(ig_prompt_f, text="📋 프롬프트 복사",
                   command=self._copy_infographic_prompt_only).pack(side="left")
        ttk.Button(ig_prompt_f, text="📋 최종원고 + 프롬프트 복사",
                   command=self._copy_infographic_prompt).pack(side="left", padx=(4, 0))
        ttk.Label(ig_prompt_f,
                  text="프롬프트 복사 = 최종각색을 쓴 같은 대화창에 이어서(한도 절약) / 최종원고 + = 새 대화창. "
                       "아래 목록은 선택한 서비스의 최종각색 결과에서 제목(썸네일)과 소제목을 자동으로 뽑습니다. "
                       "GPT에서 이미지를 만들 때 [복사] 버튼으로 정확한 텍스트를 파일명으로 바로 쓰세요. "
                       "왼쪽 체크박스는 '이미지 생성 완료' 표시용입니다.",
                  foreground="gray", wraplength=760, justify="left").pack(side="left", padx=(12, 0))

        ig_list_f = ttk.LabelFrame(infographic_tab, text="제목 목록")
        ig_list_f.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))
        ig_list_f.columnconfigure(0, weight=1)
        ig_list_f.rowconfigure(0, weight=1)

        ig_canvas = tk.Canvas(ig_list_f, highlightthickness=0)
        ig_scrollbar = ttk.Scrollbar(ig_list_f, orient="vertical", command=ig_canvas.yview)
        self.ig_title_list_frame = ttk.Frame(ig_canvas)
        self.ig_title_list_frame.bind(
            "<Configure>", lambda e: ig_canvas.configure(scrollregion=ig_canvas.bbox("all")))
        ig_canvas.create_window((0, 0), window=self.ig_title_list_frame, anchor="nw")
        ig_canvas.configure(yscrollcommand=ig_scrollbar.set)
        ig_canvas.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        ig_scrollbar.grid(row=0, column=1, sticky="ns", pady=6)

        ig_bottom_f = ttk.Frame(infographic_tab)
        ig_bottom_f.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 8))
        ttk.Button(ig_bottom_f, text="🔄 제목 목록 새로고침 (본문에서 자동 추출)",
                   command=self._generate_infographic_title_list).pack(side="left")
        self.ig_progress_var = tk.StringVar(value="이미지 매칭: 0/0 완료")
        ttk.Label(ig_bottom_f, textvariable=self.ig_progress_var,
                  foreground="darkblue", font=("맑은 고딕", 9, "bold")).pack(side="right")

        self.ig_title_vars = []  # 체크박스 BooleanVar 목록(진행률 계산용)

        # [Ver10.07 신규] 코드 카드(선택) — 체크를 켤 때만 펼쳐진다(기존 목록·버튼은 그대로).
        self._build_card_panel(infographic_tab, 4)

        # [Ver10.09] 정책뉴스 4)탭 "포스팅 완료 처리"와 같은 자리 — 인포그래픽까지 끝나면 6)키워드 등록으로.
        # 🟢 포스팅대기는 6)키워드 등록에서 등록할 때 바뀐다.
        ig_done_f = ttk.LabelFrame(infographic_tab, text="인포그래픽 완료")
        ig_done_f.grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 8))
        ttk.Button(ig_done_f, text="✅ 인포그래픽 완료 → 6)키워드 등록으로 이동",
                   command=self._goto_keyword_reg_tab).pack(side="left", padx=6, pady=6)
        ttk.Label(ig_done_f, text="6)키워드 등록에서 등록하면 🟢 포스팅대기로 바뀌고 포스팅 프로그램 폴더로 넘어갑니다.",
                  foreground="gray").pack(side="left", padx=(8, 0))

        # ---- 키워드 등록 탭 ----
        # 정책뉴스 프로그램 "📤 8.메인 포스팅용 키워드 등록" 탭과 동일한
        # 개념 — final_posts 폴더(제목별 하위폴더, 여러 개 있을 수 있음)를
        # 스캔해서 이미 등록된 것/신규를 구분하고, "등록" 시 (1) 원본을
        # 백업 폴더로 이동 (2) 백업본을 메인 포스팅 프로그램이 읽는 공용
        # 폴더로 복사 (3) 키워드 엑셀에 제목 추가 (4) 포스팅상태를
        # 포스팅완료로 확정한다. 이 버튼을 누르는 순간이 진짜 "확정"
        # 시점이다(그 전 단계인 🟢포스팅대기까지는 언제든 되돌릴 수 있음).
        keyword_reg_tab.columnconfigure(0, weight=1)
        keyword_reg_tab.rowconfigure(2, weight=1)

        self.kw_reg_info_label = ttk.Label(
            keyword_reg_tab, justify="left", foreground="gray",
            text=(f"최종원고 폴더: {FINAL_POSTS_DIR}\n"
                  f"백업 폴더(등록 후 원본 이동): {FINAL_POSTS_BACKUP_DIR}\n"
                  f"메인 포스팅 프로그램 공용 폴더: {POSTING_MD_FOLDER}\n"
                  f"키워드 엑셀: {get_keyword_excel_path()}\n"
                  f"※ 백업 폴더의 파일은 프로그램이 자동으로 지우지 않습니다 — "
                  f"실제 포스팅 확인 후 사람이 수동으로 삭제하세요."))
        self.kw_reg_info_label.grid(row=0, column=0, sticky="w", padx=6, pady=(6, 6))

        kw_btn_f = ttk.Frame(keyword_reg_tab)
        kw_btn_f.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        # [Ver10.12] 정책뉴스 6)키워드 등록과 같은 줄: 날짜 선택 · 🔄 폴더 새로고침 · 상태 필터.
        # 복지로 final_posts는 날짜 폴더가 없어서, 날짜 = 글 폴더 MD 파일을 저장한 날(_list_final_post_folders).
        # 필터는 이미 읽어 둔 kw_reg_items를 걸러 보여 주기만 한다(폴더를 다시 읽지 않음).
        ttk.Label(kw_btn_f, text="날짜 선택:").pack(side="left")
        self.kw_reg_date_var = tk.StringVar(value="전체")
        self.kw_reg_date_combo = ttk.Combobox(kw_btn_f, textvariable=self.kw_reg_date_var,
                                              state="readonly", width=12, values=["전체"])
        self.kw_reg_date_combo.pack(side="left", padx=(6, 6))
        self.kw_reg_date_combo.bind("<<ComboboxSelected>>", lambda e: self._render_kw_reg_tree())
        ttk.Button(kw_btn_f, text="🔄 폴더 새로고침",
                   command=self._refresh_keyword_reg_preview).pack(side="left", padx=(0, 8))
        ttk.Label(kw_btn_f, text="상태 필터:").pack(side="left", padx=(8, 4))
        self.kw_reg_filter_var = tk.StringVar(value="전체")
        kw_filter_combo = ttk.Combobox(kw_btn_f, textvariable=self.kw_reg_filter_var,
                                       values=["전체", "신규", "이미 등록됨"], width=12, state="readonly")
        kw_filter_combo.pack(side="left")
        kw_filter_combo.bind("<<ComboboxSelected>>", lambda e: self._render_kw_reg_tree())
        self.kw_reg_summary_var = tk.StringVar(value="")
        ttk.Label(kw_btn_f, textvariable=self.kw_reg_summary_var,
                  font=("맑은 고딕", 9, "bold")).pack(side="left", padx=(10, 0))

        # ✅ [2026-09-29] 게시판 설정 엑셀이 있으면 카테고리 입력란 대신 게시판
        # 콤보 + "선택 항목에 적용" 버튼을 쓴다(제목마다 게시판이 다르므로 일괄
        # 입력란으로는 부족함). 설정이 없으면 예전 입력란 방식 그대로.
        self.kw_category_var = tk.StringVar(value=get_default_keyword_category())
        self._board_cfg_reg = load_board_cfg()
        self.kw_reg_board_manual = {}   # {제목: 직접 지정한 게시판 이름}
        if self._board_cfg_reg.get("ok"):
            ttk.Label(kw_btn_f, text="게시판:").pack(side="left", padx=(16, 4))
            self.kw_board_var = tk.StringVar(value="")
            ttk.Combobox(kw_btn_f, textvariable=self.kw_board_var, state="readonly", width=20,
                         values=board_mod.board_labels(self._board_cfg_reg)).pack(side="left")
            ttk.Button(kw_btn_f, text="선택 항목에 적용",
                       command=self._apply_kw_reg_board).pack(side="left", padx=(6, 0))
            ttk.Label(kw_btn_f, text="(표에서 항목을 고른 뒤 적용 · '기타(미분류)'는 직접 지정을 해제)",
                      foreground="gray").pack(side="left", padx=(6, 0))
        else:
            ttk.Label(kw_btn_f, text="카테고리:").pack(side="left", padx=(16, 4))
            ttk.Entry(kw_btn_f, textvariable=self.kw_category_var, width=14).pack(side="left")
            ttk.Label(kw_btn_f, text="(비워두면 엑셀의 직전 카테고리를 그대로 씁니다)",
                      foreground="gray").pack(side="left", padx=(6, 0))

        kw_tree_f = ttk.Frame(keyword_reg_tab)
        kw_tree_f.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))
        kw_tree_f.columnconfigure(0, weight=1)
        kw_tree_f.rowconfigure(0, weight=1)
        kw_cols = ("상태", "제목", "파일수", "게시판")
        self.kw_reg_tree = ttk.Treeview(kw_tree_f, columns=kw_cols, show="headings",
                                         height=16, selectmode="extended")
        for c, w in zip(kw_cols, (90, 600, 70, 210)):
            self.kw_reg_tree.heading(c, text=c)
            self.kw_reg_tree.column(c, width=w, anchor="w")
        self.kw_reg_tree.tag_configure("registered", foreground="gray")
        self.kw_reg_tree.tag_configure("new", foreground="black")
        kw_vsb = ttk.Scrollbar(kw_tree_f, orient="vertical", command=self.kw_reg_tree.yview)
        self.kw_reg_tree.configure(yscrollcommand=kw_vsb.set)
        self.kw_reg_tree.grid(row=0, column=0, sticky="nsew")
        kw_vsb.grid(row=0, column=1, sticky="ns")

        kw_action_f = ttk.Frame(keyword_reg_tab)
        kw_action_f.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 8))
        ttk.Button(kw_action_f, text="✅ 등록 (선택 시 선택 항목만 / 미선택 시 화면에 보이는 신규 전체)",
                   command=self._process_keyword_registration).pack(side="left")
        self.kw_reg_result_var = tk.StringVar(value="")
        ttk.Label(keyword_reg_tab, textvariable=self.kw_reg_result_var,
                  foreground="darkgreen", wraplength=1100, justify="left").grid(
            row=4, column=0, sticky="w", padx=6, pady=(0, 8))

        # ---- 포스팅 이력관리 탭 ----
        # "🟢 포스팅대기 / 📤 포스팅완료 / 🗑️ 포스팅후삭제" 세 상태만 모아
        # 보여준다. 키워드 등록까지 마친 뒤 "실제로 네이버에 포스팅
        # 완료했다"고 표시하려고 매번 ④ 탭으로 돌아가 필터를 다시 만지는
        # 게 불편하다는 피드백으로 신설 — 여기서 바로 대기→완료 전환,
        # 완료→포스팅후삭제(실제 삭제 반영) 전환을 끝낼 수 있다.
        history_tab.columnconfigure(0, weight=1)
        history_tab.rowconfigure(2, weight=1)

        ttk.Label(
            history_tab,
            text="포스팅대기 / 포스팅완료 / 포스팅후삭제 상태만 모아 보여줍니다. "
                 "여기서 바로 완료 처리하거나, 블로그에서 실제로 삭제한 글을 정리할 수 있습니다.",
            foreground="gray", wraplength=1100, justify="left"
        ).grid(row=0, column=0, sticky="w", padx=6, pady=(6, 6))

        hist_filter_f = ttk.Frame(history_tab)
        hist_filter_f.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        ttk.Label(hist_filter_f, text="출처:").pack(side="left")
        self.history_source_var = tk.StringVar(value="전체")
        ttk.Combobox(hist_filter_f, textvariable=self.history_source_var, width=10, state="readonly",
                     values=["전체", "중앙부처", "지자체"]).pack(side="left", padx=(4, 12))
        self.history_source_var.trace_add("write", lambda *a: self._refresh_history_tree())

        # 검색(서비스명/서비스ID) — 자료가 쌓일수록 스크롤만으로 찾기 어려워질
        # 것에 대비해 리스트업 탭과 동일한 검색 UI 패턴을 그대로 적용.
        ttk.Label(hist_filter_f, text="🔍 검색(서비스명/ID):").pack(side="left", padx=(0, 4))
        self.history_search_var = tk.StringVar(value="")
        history_search_entry = ttk.Entry(hist_filter_f, textvariable=self.history_search_var, width=24)
        history_search_entry.pack(side="left")
        history_search_entry.bind("<Return>", lambda e: self._refresh_history_tree())
        ttk.Button(hist_filter_f, text="검색", command=self._refresh_history_tree).pack(side="left", padx=(4, 0))
        ttk.Button(hist_filter_f, text="✕", width=3,
                   command=lambda: (self.history_search_var.set(""), self._refresh_history_tree())
                   ).pack(side="left", padx=(2, 12))

        ttk.Button(hist_filter_f, text="🔄 새로고침", command=self._refresh_history_tree).pack(side="left")
        self.history_count_var = tk.StringVar(value="")
        ttk.Label(hist_filter_f, textvariable=self.history_count_var,
                  foreground="darkblue", font=("맑은 고딕", 9, "bold")).pack(side="left", padx=(12, 0))

        hist_tree_f = ttk.Frame(history_tab)
        hist_tree_f.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))
        hist_tree_f.columnconfigure(0, weight=1)
        hist_tree_f.rowconfigure(0, weight=1)
        hist_cols = ("출처", "서비스명", "서비스ID", "포스팅상태", "최종수정일")
        self.history_tree = ttk.Treeview(hist_tree_f, columns=hist_cols, show="headings", height=18)
        for c, w in zip(hist_cols, (70, 560, 130, 130, 130)):
            self.history_tree.heading(c, text=c)
            self.history_tree.column(c, width=w, anchor="w")
        self.history_tree.tag_configure("waiting", background="#E8F5E9")
        self.history_tree.tag_configure("published", background="#A5D6A7")
        self.history_tree.tag_configure("deleted", background="#F5F5F5", foreground="gray")
        hist_vsb = ttk.Scrollbar(hist_tree_f, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=hist_vsb.set)
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        hist_vsb.grid(row=0, column=1, sticky="ns")

        hist_btn_f = ttk.Frame(history_tab)
        hist_btn_f.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 8))
        ttk.Button(hist_btn_f, text="✅ 선택 항목 포스팅완료로 변경",
                   command=self._history_mark_published).pack(side="left")
        ttk.Button(hist_btn_f, text="🗑️ 포스팅완료 삭제 처리 (블로그에서 실제 삭제한 경우)",
                   command=self._history_mark_deleted).pack(side="left", padx=(8, 0))

        # [Ver10.08] 5)블로그 스크랩 탭 삭제 — 경쟁 블로그는 판정 읽기 때 자동 스크랩, 직접 고를 때는
        # 4)포스팅 관리 STEP 1의 주소 칸에서 스크랩한다(blog_scrap_* 함수는 그대로 쓴다).

        # ---- 설정 탭 ----
        # 항목이 많아 창을 아무리 키워도 잘리는 문제가 있어, 스크롤 가능한
        # 캔버스로 감쌌다(5)인포그래픽 작성 탭의 제목 목록과 동일한 패턴).
        # 실제 위젯은 settings_tab이 아니라 그 안의 settings_inner에 넣는다.
        settings_canvas = tk.Canvas(settings_tab, highlightthickness=0)
        settings_scrollbar = ttk.Scrollbar(settings_tab, orient="vertical", command=settings_canvas.yview)
        settings_inner = ttk.Frame(settings_canvas)
        settings_inner.bind(
            "<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
        settings_canvas_window = settings_canvas.create_window((0, 0), window=settings_inner, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        # 내부 프레임 폭을 캔버스 폭에 맞춰 늘려줘야 grid columnspan이 탭 전체 폭을 씀
        settings_canvas.bind(
            "<Configure>", lambda e: settings_canvas.itemconfig(settings_canvas_window, width=e.width))
        settings_canvas.pack(side="left", fill="both", expand=True)
        settings_scrollbar.pack(side="right", fill="y")

        def _on_settings_mousewheel(event):
            settings_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        settings_canvas.bind("<Enter>", lambda e: settings_canvas.bind_all("<MouseWheel>", _on_settings_mousewheel))
        settings_canvas.bind("<Leave>", lambda e: settings_canvas.unbind_all("<MouseWheel>"))

        settings_inner.columnconfigure(1, weight=1)

        ttk.Label(settings_inner,
                  text="경로를 바꾸고 싶을 때만 사용 — 비워두면 기본 위치, 실행파일 바로 아래 폴더면 폴더명만 저장(다른 PC에서도 안전).",
                  foreground="gray", justify="left").grid(row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(10, 6))

        srow = 1
        ttk.Label(settings_inner, text="작업폴더:", font=("맑은 고딕", 9, "bold")).grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_workdir_var = tk.StringVar(value=WORK_DIR)
        ttk.Entry(settings_inner, textvariable=self.settings_workdir_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_dir(self.settings_workdir_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="포스팅 키워드 엑셀 파일:", font=("맑은 고딕", 9, "bold")).grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_keyword_var = tk.StringVar(value=get_keyword_excel_path())
        ttk.Entry(settings_inner, textvariable=self.settings_keyword_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_excel_file(self.settings_keyword_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="포스팅 이력 엑셀 파일:", font=("맑은 고딕", 9, "bold")).grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_history_var = tk.StringVar(value=get_posting_history_excel_path())
        ttk.Entry(settings_inner, textvariable=self.settings_history_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_excel_file(self.settings_history_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        # ✅ [2026-09-05] 통합 키워드 파일 - 복지로/정책뉴스를 한 블로그에서
        # 같이 운영하기 위한 통합관리 모듈용 설정. 비워두면(기본값) 지금처럼
        # 이 서브프로그램 단독 동작에 전혀 영향이 없다.
        ttk.Label(settings_inner, text="통합 키워드 엑셀 파일(선택):", font=("맑은 고딕", 9, "bold")).grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_unified_keyword_var = tk.StringVar(value=get_unified_keyword_excel_path())
        ttk.Entry(settings_inner, textvariable=self.settings_unified_keyword_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_excel_file(self.settings_unified_keyword_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        # ✅ [2026-09-29] 게시판 설정 엑셀(선택) - 세부 주제 게시판 목록·판정 키워드·서비스명 매핑표.
        ttk.Label(settings_inner, text="게시판 설정 엑셀(선택):", font=("맑은 고딕", 9, "bold")).grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_board_config_var = tk.StringVar(value=load_config().get("board_config_path", ""))
        ttk.Entry(settings_inner, textvariable=self.settings_board_config_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=self._browse_board_config).grid(row=srow, column=2, padx=6, pady=2)
        srow += 1
        ttk.Label(settings_inner,
                  text="비워두면 프로그램 폴더의 Naver_blog_게시판설정.xlsx를 사용하고, 그 파일도 없으면 예전 카테고리 입력란 방식으로 동작합니다. "
                       "경로를 바꾼 뒤에는 프로그램을 다시 시작해야 6)키워드 등록 탭에 반영됩니다.",
                  foreground="gray", wraplength=900, justify="left").grid(
            row=srow, column=1, sticky="w", padx=6, pady=(0, 4))
        srow += 1

        ttk.Label(settings_inner,
                  text="⚠️ 작업폴더 경로를 바꾸면 새 위치에 기존 데이터가 없을 시 처음부터 재수집됩니다 — 옮기려면 저장 전 탐색기에서 폴더를 직접 이동하세요.",
                  foreground="#B00020", justify="left").grid(
            row=srow, column=0, columnspan=3, sticky="w", padx=6, pady=(6, 4))
        srow += 1

        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(4, 6))
        srow += 1

        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(4, 6))
        srow += 1

        # 네이버 접속 IP 확인 — 정책뉴스/메인 오토포스팅 프로그램과 완전히
        # 동일한 env.txt(Naver_blog_env_config/env.txt, BASE_DIR 기준)를
        # 공유한다. 여기서 바꾸면 다른 서브프로그램에도 즉시 반영되고,
        # 그 반대도 마찬가지다. 복지로 자체는 아직 브라우저로 네이버에
        # 접속하는 기능이 없지만, 나중에 추가될 때(예: 정책뉴스처럼 크롬
        # 프로필 공유) 이 설정을 그대로 재사용하도록 미리 이식해둔다.
        # 자주 확인하는 항목이라 위쪽에 배치(키워드 리서치 API처럼
        # "한 번 설정하면 안 건드리는" 항목과는 반대 성격).
        ip_frame = ttk.LabelFrame(settings_inner, text="네이버 접속 IP 확인 (다른 서브프로그램과 설정 공유)")
        ip_frame.grid(row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(0, 6))
        srow += 1

        ip_row1 = ttk.Frame(ip_frame)
        ip_row1.pack(fill="x", padx=8, pady=(6, 3))
        ttk.Label(ip_row1, text="Base IP:").pack(side="left")
        self.base_ip_var = tk.StringVar(value=get_env_value("base_ip", ""))
        ttk.Entry(ip_row1, textvariable=self.base_ip_var, width=18).pack(side="left", padx=(5, 5))
        ttk.Button(ip_row1, text="💾 저장", command=self._save_base_ip).pack(side="left", padx=(0, 15))
        ttk.Label(ip_row1, text="현재 IP:").pack(side="left")
        self.label_current_ip = ttk.Label(ip_row1, text="(미확인)", foreground="blue")
        self.label_current_ip.pack(side="left", padx=(5, 15))
        ttk.Button(ip_row1, text="🔍 지금 확인", command=self._manual_ip_check).pack(side="left")

        ip_row2 = ttk.Frame(ip_frame)
        ip_row2.pack(fill="x", padx=8, pady=(2, 2))
        self.network_mode_var = tk.StringVar(value=get_env_value("network_mode", "public"))
        ttk.Radiobutton(ip_row2, text="공인IP 모드 (현재IP = Base IP 이어야 통과)",
                        variable=self.network_mode_var, value="public",
                        command=self._on_network_mode_change).pack(side="left", padx=(0, 15))
        ttk.Radiobutton(ip_row2, text="테더링 모드 (현재IP ≠ Base IP 이어야 통과)",
                        variable=self.network_mode_var, value="tethering",
                        command=self._on_network_mode_change).pack(side="left")

        ttk.Label(ip_frame,
                  text="※ 이 설정은 다른 서브프로그램(정책뉴스·지식인·메인 오토포스팅 등)과 같은 파일"
                       "(Naver_blog_env_config/env.txt)을 공유합니다. 어느 쪽에서 바꿔도 양쪽에 즉시 반영됩니다.",
                  foreground="gray", justify="left", wraplength=1000).pack(anchor="w", padx=8, pady=(2, 4))

        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(4, 6))
        srow += 1

        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(4, 6))
        srow += 1


        ttk.Label(settings_inner, text="프롬프트 파일 (메모장으로 자유롭게 수정 가능 — 프로그램 재시작 불필요)",
                  font=("맑은 고딕", 9, "bold")).grid(row=srow, column=0, columnspan=3, sticky="w", padx=6, pady=(0, 4))
        srow += 1

        cfg_now = load_config()

        # [Ver10.08] STEP 1 빠른 판정 프롬프트
        ttk.Label(settings_inner, text="STEP 1 빠른판정 프롬프트 파일명 (Claude):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_prompt_quick_var = tk.StringVar(
            value=cfg_now.get("prompt_quick_judgment_file", _DEFAULT_CONFIG["prompt_quick_judgment_file"]))
        ttk.Entry(settings_inner, textvariable=self.settings_prompt_quick_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_prompt_file(self.settings_prompt_quick_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        # [Ver10.08] 판정 읽기 뒤 경쟁 블로그 자동 스크랩
        ttk.Label(settings_inner, text="경쟁 블로그 자동 스크랩 개수 / 뺄 내 블로그 아이디:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        auto_blog_f = ttk.Frame(settings_inner)
        auto_blog_f.grid(row=srow, column=1, sticky="w", padx=6, pady=2)
        self.settings_auto_blog_count_var = tk.StringVar(value=str(cfg_now.get("auto_blog_count", 3)))
        ttk.Spinbox(auto_blog_f, from_=0, to=5, width=4,
                    textvariable=self.settings_auto_blog_count_var).pack(side="left")
        ttk.Label(auto_blog_f, text="개 (0이면 안 함)   내 블로그 아이디(콤마 구분):").pack(side="left", padx=(4, 4))
        self.settings_my_blog_ids_var = tk.StringVar(value=cfg_now.get("my_blog_ids", _DEFAULT_CONFIG["my_blog_ids"]))
        ttk.Entry(auto_blog_f, textvariable=self.settings_my_blog_ids_var, width=24).pack(side="left")
        srow += 1

        ttk.Label(settings_inner, text="STEP 2 본 분석(사전스크리닝+가치판단 통합) 프롬프트 파일명 (Claude):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_prompt_prescreening_combo_var = tk.StringVar(
            value=cfg_now.get("prompt_prescreening_value_combo_file",
                               _DEFAULT_CONFIG["prompt_prescreening_value_combo_file"]))
        ttk.Entry(settings_inner, textvariable=self.settings_prompt_prescreening_combo_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_prompt_file(self.settings_prompt_prescreening_combo_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        # [Ver10.06 신규] ⑥ 최종각색 저장 창의 "📱 문단 정리(GPT)"에만 쓰는 OpenAI API 키.
        ttk.Label(settings_inner, text="OpenAI API 키 (문단 정리용, 비우면 건너뜀):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_openai_key_var = tk.StringVar(value=cfg_now.get("openai_api_key", ""))
        ttk.Entry(settings_inner, textvariable=self.settings_openai_key_var, show="*").grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="초안작성 프롬프트 파일명:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_prompt_draft_var = tk.StringVar(
            value=cfg_now.get("prompt_draft_file", _DEFAULT_CONFIG["prompt_draft_file"]))
        ttk.Entry(settings_inner, textvariable=self.settings_prompt_draft_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_prompt_file(self.settings_prompt_draft_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        # [Ver9.30] "최종각색 프롬프트 파일명 (GPT용)" 설정 줄 삭제 — GPT용 최종각색 프롬프트 폐기.

        ttk.Label(settings_inner, text="인포그래픽 프롬프트 파일명:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_prompt_info_var = tk.StringVar(
            value=cfg_now.get("prompt_infographic_file", _DEFAULT_CONFIG["prompt_infographic_file"]))
        ttk.Entry(settings_inner, textvariable=self.settings_prompt_info_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_prompt_file(self.settings_prompt_info_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        # [Ver10.07 신규] 코드 카드(선택) — 카드용 ⑦ 프롬프트, Naver_blog_SVG Card_images 폴더, 크롬 경로
        ttk.Label(settings_inner, text="카드용 ⑦ 프롬프트 파일명 (코드 카드, 선택):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_prompt_card_var = tk.StringVar(
            value=cfg_now.get("prompt_infographic_card_file", _DEFAULT_CONFIG["prompt_infographic_card_file"]))
        ttk.Entry(settings_inner, textvariable=self.settings_prompt_card_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_prompt_file(self.settings_prompt_card_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1
        ttk.Label(settings_inner, text="Naver_blog_SVG Card_images 폴더 (코드 카드):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_card_tool_var = tk.StringVar(value=cfg_now.get("card_tool_dir", "Naver_blog_SVG Card_images"))
        ttk.Entry(settings_inner, textvariable=self.settings_card_tool_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_dir(self.settings_card_tool_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1
        ttk.Label(settings_inner, text="크롬 경로 (코드 카드, 선택 — 비우면 기본 설치 위치):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_card_chrome_var = tk.StringVar(value=cfg_now.get("card_chrome_path", ""))
        ttk.Entry(settings_inner, textvariable=self.settings_card_chrome_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="2차 각색 프롬프트 파일명 (Claude용, 1차 초안 검증·각색 전용):").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_prompt_claude2_var = tk.StringVar(
            value=cfg_now.get("prompt_claude_second_stage_file", _DEFAULT_CONFIG["prompt_claude_second_stage_file"]))
        ttk.Entry(settings_inner, textvariable=self.settings_prompt_claude2_var).grid(
            row=srow, column=1, sticky="ew", padx=6, pady=2)
        ttk.Button(settings_inner, text="찾기",
                   command=lambda: self._browse_prompt_file(self.settings_prompt_claude2_var)).grid(
            row=srow, column=2, padx=6, pady=2)
        srow += 1

        ttk.Button(settings_inner, text="📂 프롬프트 폴더 열기 (메모장으로 편집)",
                   command=lambda: self._open_folder(PROMPT_DIR)).grid(
            row=srow, column=0, columnspan=2, sticky="w", padx=6, pady=(0, 6))
        srow += 1

        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(4, 6))
        srow += 1

        ttk.Label(settings_inner, text="공공데이터포털 인증키 (복지로 API — 필수)",
                  font=("맑은 고딕", 9, "bold")).grid(row=srow, column=0, columnspan=3, sticky="w", padx=6, pady=(0, 4))
        srow += 1

        ttk.Label(settings_inner, text="인증키:").grid(row=srow, column=0, sticky="w", padx=6, pady=2)
        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(settings_inner, textvariable=self.key_var, show="*")
        key_entry.grid(row=srow, column=1, sticky="ew", padx=6, pady=2)

        key_btns_f = ttk.Frame(settings_inner)
        key_btns_f.grid(row=srow, column=2, sticky="w", padx=6, pady=2)
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_btns_f, text="표시", variable=self.show_key_var,
            command=lambda: key_entry.config(show="" if self.show_key_var.get() else "*")
        ).pack(side="left")
        ttk.Button(key_btns_f, text="저장", command=self._on_save_key).pack(side="left", padx=(6, 0))
        srow += 1

        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(4, 6))
        srow += 1

        ttk.Label(settings_inner, text="2단계 키워드 리서치 API (모두 선택사항 — 없으면 해당 항목만 건너뜁니다. 최초 1회 설정 후엔 거의 안 건드리는 항목이라 맨 아래로 뺌)",
                  font=("맑은 고딕", 9, "bold"), wraplength=1000).grid(row=srow, column=0, columnspan=3, sticky="w", padx=6, pady=(0, 4))
        srow += 1

        api_keys = get_research_api_keys()

        ttk.Label(settings_inner, text="네이버 오픈API - Client ID:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_openapi_id_var = tk.StringVar(value=api_keys["naver_openapi_client_id"])
        ttk.Entry(settings_inner, textvariable=self.settings_openapi_id_var).grid(
            row=srow, column=1, columnspan=2, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="네이버 오픈API - Client Secret:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_openapi_secret_var = tk.StringVar(value=api_keys["naver_openapi_client_secret"])
        ttk.Entry(settings_inner, textvariable=self.settings_openapi_secret_var, show="*").grid(
            row=srow, column=1, columnspan=2, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="(developers.naver.com에서 애플리케이션 등록 후 발급 — 2-C 블로그 제목 분석에 사용)",
                  foreground="gray").grid(row=srow, column=1, columnspan=2, sticky="w", padx=6, pady=(0, 4))
        srow += 1

        ttk.Label(settings_inner, text="네이버 검색광고 API Key:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_ad_key_var = tk.StringVar(value=api_keys["naver_ad_api_key"])
        ttk.Entry(settings_inner, textvariable=self.settings_ad_key_var).grid(
            row=srow, column=1, columnspan=2, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="네이버 검색광고 Secret Key:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_ad_secret_var = tk.StringVar(value=api_keys["naver_ad_secret_key"])
        ttk.Entry(settings_inner, textvariable=self.settings_ad_secret_var, show="*").grid(
            row=srow, column=1, columnspan=2, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="네이버 검색광고 Customer ID:").grid(
            row=srow, column=0, sticky="w", padx=6, pady=2)
        self.settings_ad_customer_var = tk.StringVar(value=api_keys["naver_ad_customer_id"])
        ttk.Entry(settings_inner, textvariable=self.settings_ad_customer_var).grid(
            row=srow, column=1, columnspan=2, sticky="ew", padx=6, pady=2)
        srow += 1

        ttk.Label(settings_inner, text="(searchad.naver.com > 도구 > API 사용관리에서 발급 — 2-B 검색량 조회에 사용)",
                  foreground="gray").grid(row=srow, column=1, columnspan=2, sticky="w", padx=6, pady=(0, 6))
        srow += 1

        # [Ver9.04 이동] 저장 버튼을 IP 설정 섹션 직후(탭 중간)에서 이
        # 설정탭의 맨 마지막으로 옮겼다 — 원래 위치는 그 아래로 프롬프트
        # 파일 경로·인증키·리서치 API 섹션이 더 있어서 눈에 잘 안 띄고,
        # 아래쪽 항목을 바꾼 뒤 다시 위로 스크롤해야 하는 문제가 있었다.
        ttk.Separator(settings_inner, orient="horizontal").grid(
            row=srow, column=0, columnspan=3, sticky="ew", padx=6, pady=(8, 6))
        srow += 1

        ttk.Button(settings_inner, text="💾 설정 저장 (이 탭 전체)",
                   command=self._save_path_settings, style="Save.TButton").grid(
            row=srow, column=0, columnspan=3, pady=(4, 4))
        srow += 1
        self.settings_saved_var = tk.StringVar(value="")
        ttk.Label(settings_inner, textvariable=self.settings_saved_var, foreground="darkgreen").grid(
            row=srow, column=0, columnspan=3, pady=(0, 12))
        srow += 1

        # 공통 실행 제어 (중지 / 새로고침 / 폴더열기)
        common_btn_frame = ttk.Frame(self)
        common_btn_frame.pack(fill="x", **pad)

        self.btn_stop = ttk.Button(common_btn_frame, text="■ 중지", command=self._on_stop, state="disabled")
        self.btn_stop.pack(side="left", padx=4)

        ttk.Button(common_btn_frame, text="상태 새로고침", command=self._refresh_status).pack(side="left", padx=4)

        ttk.Button(common_btn_frame, text="데이터 폴더 열기(중앙부처)",
                   command=lambda: self._open_folder(SERVICES_DIR)).pack(side="right", padx=4)
        ttk.Button(common_btn_frame, text="데이터 폴더 열기(지자체)",
                   command=lambda: self._open_folder(SERVICES_DIR_LCGV)).pack(side="right", padx=4)
        ttk.Button(common_btn_frame, text="📁 작업폴더 열기",
                   command=lambda: self._open_folder(WORK_DIR)).pack(side="right", padx=4)

        # 상태 표시 영역 (분할창 하단 구역 안, 로그 위쪽에 고정 배치)
        status_frame = ttk.LabelFrame(bottom_container, text="진행 현황")
        status_frame.pack(fill="x", padx=8, pady=(8, 4))

        self.status_label = ttk.Label(status_frame, text="-", justify="left")
        self.status_label.pack(anchor="w", padx=8, pady=6)

        self.progress = ttk.Progressbar(status_frame, mode="determinate")
        self.progress.pack(fill="x", padx=8, pady=(0, 8))

        # 로그 영역 — 화면 공간을 최대한 활용하도록 분할창 하단 구역 전체를
        # 채운다(높이는 사용자가 sash를 드래그해 자유롭게 조절 가능).
        log_frame = ttk.LabelFrame(bottom_container, text="로그")
        log_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", state="disabled", height=20)
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)

    # ---------------- 인증키 ----------------
    def _load_saved_key(self):
        key = load_service_key()
        if key:
            self.key_var.set(key)
            self._log("저장된 인증키를 불러왔습니다.")
        else:
            self._log("인증키가 없습니다. data.go.kr 마이페이지의 '일반 인증키'를 입력 후 [저장]을 눌러주세요.")

    def _on_save_key(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("입력 필요", "인증키를 입력해주세요.")
            return
        save_service_key(key)
        self._log(f"✓ 인증키 저장 완료 ({os.path.basename(CONFIG_PATH)})")

    # ---------------- 네이버 접속 IP 확인 (정책뉴스 프로그램과 동일 이식) ----------------
    def _save_base_ip(self):
        """Base IP 저장 버튼 — env.txt 갱신(다른 서브프로그램과 공유)."""
        ip = self.base_ip_var.get().strip()
        update_env_value("base_ip", ip)
        messagebox.showinfo("저장 완료", f"Base IP가 저장되었습니다.\n{ip if ip else '(비워서 저장 - 체크 비활성)'}")

    def _refresh_ip_label(self):
        """IP 라벨만 조용히 갱신(팝업 없음) — 프로그램 시작 후 자동 호출용."""
        current_ip = get_current_public_ip()
        if hasattr(self, "label_current_ip"):
            self.label_current_ip.config(text=current_ip if current_ip else "조회 실패")
        return current_ip

    def _manual_ip_check(self):
        """지금 확인 버튼 — 현재 IP 조회 및 Base IP와 비교."""
        base_ip = get_env_value("base_ip", "").strip()
        current_ip = self._refresh_ip_label()

        if not base_ip:
            messagebox.showinfo("IP 상태 확인", "Base IP가 설정되어 있지 않아 비교할 수 없습니다.\n먼저 Base IP를 입력하고 저장해주세요.")
            return
        if current_ip is None:
            messagebox.showwarning("IP 상태 확인", "공인 IP 조회에 실패했습니다.\n인터넷 연결을 확인해주세요.")
            return

        mode = get_env_value("network_mode", "public")
        mode_label = "공인IP 모드" if mode == "public" else "테더링 모드"
        ok = (current_ip == base_ip) if mode == "public" else (current_ip != base_ip)

        if ok:
            messagebox.showinfo("IP 상태 확인", f"✅ 정상입니다.\n\n모드: {mode_label}\nBase IP: {base_ip}\n현재 IP: {current_ip}")
        else:
            reason = "집 네트워크가 아닙니다." if mode == "public" else "테더링이 되어 있지 않습니다."
            messagebox.showwarning("IP 상태 확인", f"⛔ 불일치 감지!\n\n모드: {mode_label}\nBase IP: {base_ip}\n현재 IP: {current_ip}\n\n{reason}")

    def _on_network_mode_change(self):
        """네트워크 모드 라디오버튼 변경 시 env.txt 즉시 갱신."""
        update_env_value("network_mode", self.network_mode_var.get())

    def _check_ip_before_naver_open(self) -> bool:
        """네이버(브라우저)를 열기 전에 IP를 확인한다. 막아야 하면 True를
        반환(호출부에서 이후 진행을 중단해야 함). Base IP가 비어 있으면
        체크 자체를 하지 않는다. 복지로는 아직 이 함수를 실제로 호출하는
        곳이 없다(브라우저로 네이버에 접속하는 기능이 아직 없음) — 나중에
        추가될 때 정책뉴스 프로그램과 동일한 방식으로 바로 쓸 수 있도록
        미리 이식해둔 것."""
        base_ip = get_env_value("base_ip", "").strip()
        if not base_ip:
            return False  # base_ip 미설정이면 체크 안 함

        current_ip = get_current_public_ip()
        if current_ip is None:
            messagebox.showerror(
                "IP 조회 실패",
                "⛔ 공인 IP 조회에 실패했습니다.\n\n인터넷 연결을 확인해주세요."
            )
            return True

        mode = get_env_value("network_mode", "public")
        if mode == "public":
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

    # ---------------- 실행 버튼 핸들러 ----------------
    def _on_start_list(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("인증키 필요", "먼저 인증키를 입력하고 저장해주세요.")
            return
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("실행 중", "이미 작업이 실행 중입니다.")
            return

        life_code = self.life_var.get().split(":")[0] if self.life_var.get() else ""
        theme_code = self.theme_var.get().split(":")[0] if self.theme_var.get() else ""
        search_wrd = self.search_var.get().strip()

        self.stop_event.clear()
        self._set_running(True)
        self._log("=== 목록조회 시작 ===")

        def task():
            try:
                collect_list_all(
                    key, self._log, self.stop_event,
                    life_code=life_code, theme_code=theme_code, search_wrd=search_wrd,
                )
            finally:
                self.log_queue.put(("__DONE__", None))

        self.worker_thread = threading.Thread(target=task, daemon=True)
        self.worker_thread.start()

    def _on_start_detail(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("인증키 필요", "먼저 인증키를 입력하고 저장해주세요.")
            return
        if not os.path.exists(LIST_OUTPUT_FILE):
            messagebox.showwarning("목록 필요", "먼저 ①목록조회를 실행해서 services_list.json을 만들어주세요.")
            return
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("실행 중", "이미 작업이 실행 중입니다.")
            return

        self.stop_event.clear()
        self._set_running(True)
        download_files = self.download_files_var.get()
        self._log(f"=== 상세조회 시작 (공식자료 {'포함' if download_files else '제외'}) ===")

        def task():
            try:
                collect_detail_all(key, self._log, self.stop_event, download_files=download_files)
            finally:
                self.log_queue.put(("__DONE__", None))

        self.worker_thread = threading.Thread(target=task, daemon=True)
        self.worker_thread.start()

    def _on_stop(self):
        self.stop_event.set()
        self._log("중지 요청을 보냈습니다. 진행 중인 호출이 끝나면 정지합니다...")

    def _on_start_lcgv_list(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("인증키 필요", "먼저 인증키를 입력하고 저장해주세요.")
            return
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("실행 중", "이미 작업이 실행 중입니다.")
            return

        life_code = self.lcgv_life_var.get().split(":")[0] if self.lcgv_life_var.get() else ""
        household_code = self.lcgv_household_var.get().split(":")[0] if self.lcgv_household_var.get() else ""
        theme_code = self.lcgv_theme_var.get().split(":")[0] if self.lcgv_theme_var.get() else ""
        ctpv_nm = self.lcgv_ctpv_var.get().strip()
        sgg_nm = self.lcgv_sgg_var.get().strip()
        search_wrd = self.lcgv_search_var.get().strip()

        self.stop_event.clear()
        self._set_running(True)
        self._log("=== 지자체 목록조회 시작 ===")

        def task():
            try:
                collect_lcgv_list_all(
                    key, self._log, self.stop_event,
                    life_code=life_code, theme_code=theme_code, household_code=household_code,
                    ctpv_nm=ctpv_nm, sgg_nm=sgg_nm, search_wrd=search_wrd,
                )
            finally:
                self.log_queue.put(("__DONE__", None))

        self.worker_thread = threading.Thread(target=task, daemon=True)
        self.worker_thread.start()

    def _on_start_lcgv_detail(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("인증키 필요", "먼저 인증키를 입력하고 저장해주세요.")
            return
        if not os.path.exists(LIST_OUTPUT_FILE_LCGV):
            messagebox.showwarning("목록 필요", "먼저 ③지자체 목록조회를 실행해주세요.")
            return
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("실행 중", "이미 작업이 실행 중입니다.")
            return

        self.stop_event.clear()
        self._set_running(True)
        download_files = self.lcgv_download_files_var.get()
        self._log(f"=== 지자체 상세조회 시작 (공식자료 {'포함' if download_files else '제외'}) ===")

        def task():
            try:
                collect_lcgv_detail_all(key, self._log, self.stop_event, download_files=download_files)
            finally:
                self.log_queue.put(("__DONE__", None))

        self.worker_thread = threading.Thread(target=task, daemon=True)
        self.worker_thread.start()

    def _set_running(self, running: bool):
        state_run = "disabled" if running else "normal"
        state_stop = "normal" if running else "disabled"
        self.btn_list.config(state=state_run)
        self.btn_detail.config(state=state_run)
        self.btn_lcgv_list.config(state=state_run)
        self.btn_lcgv_detail.config(state=state_run)
        self.btn_stop.config(state=state_stop)

    # ---------------- 로그 / 상태 ----------------
    def _log(self, msg: str):
        self.log_queue.put(("LOG", msg))

    def _poll_log_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "LOG":
                    self.log_text.config(state="normal")
                    self.log_text.insert("end", payload + "\n")
                    self.log_text.see("end")
                    self.log_text.config(state="disabled")
                elif kind == "__DONE__":
                    self._set_running(False)
                    self._refresh_status()
                elif kind == "RESEARCH_DONE":
                    # [v6.9] payload가 콤마 다중 리서치 시 키워드 리스트로 온다
                    # (단일 키워드였던 기존 문자열 payload도 그대로 처리).
                    # [v6.9.1] 캐시 파일을 한 번만 읽어 재사용(get_cached_research
                    # 반복 호출로 인한 중복 파일 I/O 방지 — 위 research_map
                    # 조립부와 동일한 이유).
                    self._research_running = False
                    _sv = self._kw_vars(getattr(self, "_research_which", "prep"))[1]
                    keywords = payload if isinstance(payload, list) else [payload]
                    _cache_now = load_research_cache()
                    done = [kw for kw in keywords if kw in _cache_now]
                    if len(keywords) == 1:
                        cached = _cache_now.get(keywords[0])
                        _sv.set(
                            f"✅ 리서치 완료 ({cached['researched_at']})" if cached else "❌ 리서치 실패"
                        )
                    elif len(done) == len(keywords):
                        _sv.set(f"✅ 리서치 완료 ({len(keywords)}건 비교 가능)")
                    elif done:
                        _sv.set(f"⚠ 일부만 완료 ({len(done)}/{len(keywords)}건)")
                    else:
                        _sv.set("❌ 리서치 실패")
                    # [Ver10.08] AI가 요청한 키워드였으면 답변을 바로 클립보드에 넣는다
                    if getattr(self, "_research_then_reply", False):
                        self._research_then_reply = False
                        if done:
                            self._copy_research_reply_for_posting("ai")
                            messagebox.showinfo(
                                "키워드 리서치 결과 복사됨",
                                "AI가 요청한 키워드를 리서치해 결과를 클립보드에 넣었습니다.\n\n"
                                "1) 가치판단을 하던 같은 대화창에 Ctrl+V로 붙여넣기\n"
                                "2) Claude 새 답을 복사해 '💾 가치판단 저장(메모리값 자동저장)' 다시 누르기")
                        else:
                            self.ai_kw_status_var.set("❌ 요청 키워드 리서치 실패 — 이 줄의 '🔍 키워드 리서치 실행'을 다시 누르세요(설정 탭의 API 키 확인)")
                elif kind == "AUTO_PREP_DONE":   # [Ver10.08] 판정 읽기 뒤 자료 자동 준비
                    self._on_auto_prep_done(payload)
                elif kind == "RESEARCH_SUMMARY_DONE":
                    # [v7.0 추가, 정책뉴스 Ver8.22에서 이식] "🔍 검색량·
                    # 자동완성 조회" 버튼의 백그라운드 조회 완료 콜백 —
                    # 위 RESEARCH_DONE(캐시 저장용)과 달리 캐시에는 저장하지
                    # 않고, 결과가 오는 즉시 팝업으로 바로 띄운다.
                    self._research_summary_running = False
                    self._kw_vars(getattr(self, "_summary_which", "prep"))[1].set("")
                    self._open_research_summary_popup(payload)
        except queue.Empty:
            pass
        self.after(150, self._poll_log_queue)

    def _refresh_status(self):
        """상태 표시 + 3개 트리(listing/posting/history) 새로고침 — 동기
        버전. 버튼 클릭 등 사용자가 직접 요청한 새로고침에서 쓴다.
        [Ver9.04] 파일 I/O 부분(_compute_status_and_rows)과 위젯 갱신
        부분(_apply_status_result)을 분리했다 — 시작 시에는 I/O 부분만
        백그라운드 스레드로 돌리기 위함(_refresh_status_startup_async
        참고). 이 함수 자체(동기 호출)의 동작은 기존과 동일하다.
        """
        self._apply_status_result(self._compute_status_and_rows())

    def _compute_status_and_rows(self):
        """디스크 I/O(트래픽 조회 + build_listing_rows() 전체 스캔)만
        수행하고 위젯은 건드리지 않는다 — 백그라운드 스레드에서 안전하게
        돌릴 수 있도록 분리했다(v9.04, 시작 속도 개선). 반환값을 메인
        스레드에서 _apply_status_result()에 넘겨야 실제로 위젯이
        갱신된다."""
        list_used, detail_used, lcgv_list_used, lcgv_detail_used = get_quota_status()

        total, detail_done = 0, 0
        if os.path.exists(LIST_OUTPUT_FILE):
            with open(LIST_OUTPUT_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
            total = len(items)
            detail_done = sum(
                1 for item in items
                if os.path.exists(os.path.join(
                    service_folder_path(item["servId"], item.get("servNm", "")), "detail.json"
                ))
            )

        lcgv_total, lcgv_detail_done = 0, 0
        if os.path.exists(LIST_OUTPUT_FILE_LCGV):
            with open(LIST_OUTPUT_FILE_LCGV, "r", encoding="utf-8") as f:
                lcgv_items = json.load(f)
            lcgv_total = len(lcgv_items)
            lcgv_detail_done = sum(
                1 for item in lcgv_items
                if os.path.exists(os.path.join(
                    SERVICES_DIR_LCGV,
                    f"{sanitize_folder_name(item.get('servNm', ''))}_{item['servId']}",
                    "detail.json",
                ))
            )

        # listing/posting/history 세 트리 모두 build_listing_rows() 전체
        # 스캔이 필요하므로, 여기서 한 번만 계산해 세 함수가 공유하게
        # 한다(안 그러면 이 한 번의 호출 안에서도 같은 무거운 스캔이
        # 여러 번 일어난다).
        shared_rows = build_listing_rows()

        return {
            "list_used": list_used, "detail_used": detail_used,
            "lcgv_list_used": lcgv_list_used, "lcgv_detail_used": lcgv_detail_used,
            "total": total, "detail_done": detail_done,
            "lcgv_total": lcgv_total, "lcgv_detail_done": lcgv_detail_done,
            "shared_rows": shared_rows,
        }

    def _apply_status_result(self, r):
        """_compute_status_and_rows()의 결과로 실제 위젯(상태 라벨/
        진행바/3개 트리)을 갱신한다 — 반드시 메인(Tk) 스레드에서
        호출해야 한다(v9.04, self.after(0, ...)를 통해서만 백그라운드
        스레드 결과와 연결할 것)."""
        self.status_label.config(
            text=(
                f"[중앙부처] 트래픽 - 목록: {r['list_used']}/{DAILY_QUOTA_LIST}  상세: {r['detail_used']}/{DAILY_QUOTA_DETAIL}"
                f"   |   수집 - 전체 {r['total']}건 / 완료 {r['detail_done']}건\n"
                f"[지자체]   트래픽 - 목록: {r['lcgv_list_used']}/{DAILY_QUOTA_LCGV_LIST}  "
                f"상세: {r['lcgv_detail_used']}/{DAILY_QUOTA_LCGV_DETAIL}"
                f"   |   수집 - 전체 {r['lcgv_total']}건 / 완료 {r['lcgv_detail_done']}건"
            )
        )
        combined_total = max(r["total"] + r["lcgv_total"], 1)
        self.progress["maximum"] = combined_total
        self.progress["value"] = r["detail_done"] + r["lcgv_detail_done"]

        shared_rows = r["shared_rows"]
        if hasattr(self, "listing_tree"):
            self._refresh_listing_tree(shared_rows)
        if hasattr(self, "posting_tree"):
            self._refresh_posting_tree(shared_rows)
        if hasattr(self, "history_tree"):
            self._refresh_history_tree(shared_rows)

    def _refresh_status_startup_async(self):
        """__init__ 전용(v9.04) — 무거운 전체 스캔(build_listing_rows())을
        백그라운드 스레드로 돌려서, 창이 그 시간 내내 안 뜨는 문제를
        없앤다. 트리에는 우선 "불러오는 중…" 표시만 넣어두고, 스레드가
        끝나면 self.after(0, ...)로 메인 스레드에서 실제 데이터를 채운다.
        (실제 총 계산 시간 자체가 줄어드는 건 아니고, 그동안 창이 정상
        표시되고 다른 조작이 가능해지는 체감 개선이다.)"""
        for tree_name in ("listing_tree", "posting_tree", "history_tree"):
            tree = getattr(self, tree_name, None)
            if tree is None:
                continue
            for item in tree.get_children():
                tree.delete(item)
            n_cols = len(tree["columns"]) if tree["columns"] else 1
            tree.insert("", "end", values=("불러오는 중…",) + ("",) * (n_cols - 1))

        def _worker():
            try:
                result = self._compute_status_and_rows()
            except Exception as e:
                self.after(0, lambda e=e: self._log(f"⚠️ 시작 시 상태 갱신 실패: {e}"))   # [Ver9.30] e를 람다에 묶음
                return
            self.after(0, lambda: self._apply_status_result(result))

        threading.Thread(target=_worker, daemon=True).start()

    # ---------------- 리스트업 ----------------
    def _get_visible_listing_rows(self, all_rows: list = None) -> list:
        rows = all_rows if all_rows is not None else build_listing_rows()

        source = self.listing_source_var.get() if hasattr(self, "listing_source_var") else "전체"
        if source != "전체":
            rows = [r for r in rows if r["source"] == source]

        status = self.listing_status_var.get() if hasattr(self, "listing_status_var") else "전체"
        if status == "미수집만":
            rows = [r for r in rows if not r["downloaded"]]
        elif status == "오늘 신규만":
            rows = [r for r in rows if r["is_new_today"]]

        search = self.listing_search_var.get().strip().lower() if hasattr(self, "listing_search_var") else ""
        if search:
            rows = [r for r in rows if search in r["servNm"].lower()]

        sort_label = self.listing_sort_var.get() if hasattr(self, "listing_sort_var") else "우선순위 높은순"
        return sort_rows(rows, sort_label)

    def _refresh_listing_tree(self, all_rows: list = None):
        if not hasattr(self, "listing_tree"):
            return
        self.listing_tree.delete(*self.listing_tree.get_children())
        # 성능: build_listing_rows()는 중앙부처+지자체 전체 목록을 파일에서
        # 읽고 detail.json 존재 확인·지자체 중복정책 대조(추가 JSON 읽기)까지
        # 하는 무거운 함수라, 아래에서 "표시용 필터링"과 "전체 통계 집계"에
        # 각각 따로 부르면 같은 작업을 두 번 하게 된다. 한 번만 불러서
        # 재사용한다(2026-08-19: 시작 시 GUI가 늦게 뜨는 문제의 원인 중
        # 하나로 확인됨 — 이 함수 하나가 초기화 시퀀스에서만 6~7번
        # 중복 호출되고 있었음). all_rows를 미리 계산해 넘겨받으면(예:
        # _refresh_status에서 listing/posting이 같은 결과를 공유할 때)
        # 그마저도 다시 계산하지 않는다.
        if all_rows is None:
            all_rows = build_listing_rows()
        rows = self._get_visible_listing_rows(all_rows)

        if not rows:
            search = self.listing_search_var.get().strip() if hasattr(self, "listing_search_var") else ""
            msg = f"🔍 '{search}'에 해당하는 결과가 없습니다" if search else "표시할 항목이 없습니다 (먼저 목록조회를 실행하세요)"
            self.listing_tree.insert("", "end", values=("", "", msg, "", "", "", ""))
        else:
            for r in rows:
                if r["excluded"]:
                    tag = "excluded"
                elif r["is_new_today"]:
                    tag = "new_today"
                elif not r["downloaded"]:
                    tag = "not_downloaded"
                else:
                    tag = ""
                if r["source"] == "중앙부처":
                    n = len(r.get("related_lcgv_ids", []))
                    related_col = f"🔗 지자체 {n}건" if n else ""
                else:
                    related_col = f"🔁 중앙부처 있음({r['match_confidence']})" if r.get("matched_central_id") else ""
                self.listing_tree.insert(
                    "", "end", iid=r["servId"],
                    values=(
                        format_priority_score(r), r["source"], r["servNm"], r["servId"],
                        related_col,
                        "완료" if r["downloaded"] else "미수집",
                        r["first_seen_date"],
                    ),
                    tags=(tag,),
                )

        # all_rows는 함수 상단에서 이미 계산했으므로 재사용(중복 호출 제거)
        total = len(all_rows)
        downloaded = sum(1 for r in all_rows if r["downloaded"])
        new_today = sum(1 for r in all_rows if r["is_new_today"])
        self.listing_count_var.set(
            f"전체 {total}건 중 수집완료 {downloaded}건 / 미수집 {total - downloaded}건 / 오늘 신규 {new_today}건"
            f"  (표시 중 {len(rows)}건)"
        )

    def _copy_selected_listing_name(self):
        """리스트업 트리에서 선택한 행의 서비스명(제목)만 클립보드에 복사한다."""
        sel = self.listing_tree.selection()
        if not sel:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        values = self.listing_tree.item(sel[0], "values")
        # 컬럼 순서: 우선순위, 출처, 서비스명, 서비스ID, 수집상태, 최초발견일
        serv_nm = values[2] if len(values) > 2 else ""
        if not serv_nm:
            messagebox.showwarning("알림", "복사할 서비스명이 없습니다.")
            return
        self.clipboard_clear()
        self.clipboard_append(serv_nm)
        self._log(f"📋 서비스명 복사 완료: {serv_nm}")

    def _recheck_similar_policies(self):
        """[v7.15 신규] build_listing_rows(include_fuzzy=True)로 퍼지
        매칭까지 포함해 한 번 더 전체 스캔한다. 기본 새로고침(트리
        클릭, 시작 스캔 등)에서는 이 비용을 아예 안 치르도록 바꿨으니
        (v7.15 changelog 참고), "이름은 다르지만 사실상 같은 정책"까지
        잡고 싶을 때 이 버튼으로 명시적으로 돌린다. 항목이 많으면
        시간이 걸릴 수 있어 백그라운드 스레드로 실행하고, 끝나면 그
        결과로 3개 트리(목록/포스팅관리/이력관리)를 한 번에 새로고침
        한다."""
        if getattr(self, "_similar_recheck_running", False):
            messagebox.showinfo("실행 중", "이미 재검사가 진행 중입니다.")
            return
        self._similar_recheck_running = True
        self.similar_recheck_status_var.set("⏳ 작업중... (이름 유사 매칭 포함 전체 스캔)")
        self._log("🔁 중복 정책 재검사(이름 유사까지 포함) 시작 — 항목이 많으면 시간이 걸릴 수 있습니다.")

        def task():
            try:
                rows = build_listing_rows(include_fuzzy=True)
            except Exception as e:
                def fail(e=e):   # [Ver9.30] except 블록이 끝나면 e가 사라지므로 기본값으로 묶음
                    self._similar_recheck_running = False
                    self.similar_recheck_status_var.set(f"❌ 작업 실패: {e}")
                    self._log(f"✗ 중복 정책 재검사 실패: {e}")
                self.after(0, fail)
                return

            def done():
                self._similar_recheck_running = False
                if hasattr(self, "listing_tree"):
                    self._refresh_listing_tree(rows)
                if hasattr(self, "posting_tree"):
                    self._refresh_posting_tree(rows)
                if hasattr(self, "history_tree"):
                    self._refresh_history_tree(rows)
                self.similar_recheck_status_var.set("✅ 작업완료")
                self._log("✅ 중복 정책 재검사 완료 — 결과는 \"관련정책\" 열에 반영됐습니다.")
            self.after(0, done)

        threading.Thread(target=task, daemon=True).start()

    def _get_selected_listing_row(self):
        sel = self.listing_tree.selection()
        if not sel:
            return None
        sid = sel[0]
        for r in build_listing_rows():
            if r["servId"] == sid:
                return r
        return None

    def _show_related_policies_popup_for_posting(self):
        """포스팅 관리 탭에서 선택한 항목 기준으로 연관 정책 팝업을 연다
        (실제 패스 처리 관리는 리스트업이 아니라 포스팅 관리 탭에서 하는
        게 맞다는 판단 — 리스트업은 "연관정책" 컬럼으로 눈에 띄게
        보여주기만 하고, 처리 액션은 여기 버튼 하나로 통일)."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        self._show_related_policies_popup(row)

    def _show_related_policies_popup(self, row=None):
        """선택한 항목의 연관 정책(중앙부처↔지자체 매칭)을 보여주는 팝업.
        - 중앙부처 항목을 선택했다면: 매칭된 지자체 항목들을 체크박스
          목록으로 보여주고, 검토 후 체크한 항목을 일괄 "⏭ 패스" 처리할
          수 있게 한다 — 중앙부처를 먼저 포스팅완료 처리하기 전에, 중복
          지자체 건들을 한 번에 정리해두려는 목적.
        - 지자체 항목을 선택했다면: 매칭된 중앙부처 항목 1건의 현재
          상태만 보여준다(정보 확인용, 지자체 작업 중 "이미 중앙부처가
          처리됐는지" 바로 확인 가능).
        row를 직접 넘기면(예: 포스팅완료 처리 직후 자동으로 띄우는 경우)
        listing_tree 선택 상태와 무관하게 그 row 기준으로 연다."""
        if row is None:
            row = self._get_selected_listing_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return

        all_rows = build_listing_rows()
        by_id = {r["servId"]: r for r in all_rows}

        dialog = tk.Toplevel(self)
        dialog.transient(self)

        if row["source"] == "중앙부처":
            related_ids = row.get("related_lcgv_ids", [])
            dialog.title(f"연관 지자체 정책 — {row['servNm']}")
            dialog.geometry("820x480")

            if not related_ids:
                ttk.Label(dialog, text="연관된(이름이 유사한) 지자체 정책이 없습니다.",
                          padding=16).pack()
                ttk.Button(dialog, text="닫기", command=dialog.destroy).pack(pady=(0, 12))
                return

            ttk.Label(
                dialog,
                text=f"'{row['servNm']}'(중앙부처)와 이름이 유사한 지자체 정책 {len(related_ids)}건입니다.\n"
                     f"중복이 확실한 항목만 체크한 뒤 '⏭ 선택 항목 패스 처리'를 누르세요. "
                     f"(포스팅완료 항목은 보호되어 체크할 수 없습니다)",
                padding=(12, 10), justify="left",
            ).pack(anchor="w")

            list_container = ttk.Frame(dialog)
            list_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

            canvas = tk.Canvas(list_container, highlightthickness=0)
            scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
            inner = ttk.Frame(canvas)
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            check_vars = {}
            related_rows = sorted(
                (by_id[sid] for sid in related_ids if sid in by_id),
                key=lambda r: r["servNm"],
            )
            for r in related_rows:
                protected = r["posting_status"] == PROTECTED_STATUS
                var = tk.BooleanVar(value=False)
                line = ttk.Frame(inner)
                line.pack(fill="x", pady=2)
                cb = ttk.Checkbutton(line, variable=var, state=("disabled" if protected else "normal"))
                cb.pack(side="left", padx=(4, 8))
                status_disp = r["posting_status"] or "🆕 신규"
                confidence_disp = f"[{r['match_confidence']}]" if r["match_confidence"] else ""
                label_text = f"{r['servNm']}  {confidence_disp}  ·  {status_disp}  ·  " \
                             f"{'수집됨' if r['downloaded'] else '미수집'}"
                fg = "#B00020" if protected else None
                lbl = ttk.Label(line, text=label_text, foreground=fg)
                lbl.pack(side="left")
                if not protected:
                    check_vars[r["servId"]] = var

            def _apply_pass():
                targets = [sid for sid, var in check_vars.items() if var.get()]
                if not targets:
                    messagebox.showwarning("알림", "체크된 항목이 없습니다.", parent=dialog)
                    return
                done = 0
                for sid in targets:
                    r = by_id.get(sid)
                    if not r:
                        continue
                    ok, _ = set_posting_status(sid, "⏭ 패스", r["servNm"], r["source"])
                    if ok:
                        done += 1
                self._log(f"⏭ 연관 지자체 {done}건 패스 처리 완료 (기준: {row['servNm']})")
                self._refresh_listing_tree()
                self._refresh_posting_tree()
                dialog.destroy()

            btn_f = ttk.Frame(dialog)
            btn_f.pack(fill="x", padx=12, pady=(0, 12))

            def _set_all_checks(value: bool):
                for var in check_vars.values():
                    var.set(value)

            def _toggle_select_all():
                # 체크 안 된 항목이 하나라도 있으면 전체선택, 전부 체크돼
                # 있으면 전체해제(같은 버튼이 상황에 따라 토글) — 포스팅완료로
                # 보호된 항목(check_vars에 애초에 안 들어있음)은 건드리지 않는다.
                any_unchecked = any(not var.get() for var in check_vars.values())
                _set_all_checks(any_unchecked)

            def _select_all_and_pass():
                # "전체선택하여 패스"는 토글이 아니라 항상 "전체 체크 후 즉시
                # 패스 처리"로 동작해야 한다 — 우연히 이미 전부 체크된
                # 상태에서 눌러도 전체해제로 잘못 동작하면 안 되므로, 토글
                # 함수를 재사용하지 않고 항상 True로 강제 선택한다. 체크박스를
                # 하나씩 확인할 필요가 없는 대신, 실수로 전부 패스되는 사고를
                # 막기 위해 실행 직전 한 번 더 확인한다.
                if not check_vars:
                    return
                if not messagebox.askyesno(
                    "전체선택하여 패스",
                    f"연관 지자체 정책 {len(check_vars)}건을 검토 없이 모두 "
                    f"'⏭ 패스' 처리합니다.\n\n계속할까요?",
                    parent=dialog,
                ):
                    return
                _set_all_checks(True)
                _apply_pass()

            ttk.Button(btn_f, text="☑ 전체선택하여 패스", command=_select_all_and_pass).pack(side="left")
            ttk.Button(btn_f, text="전체선택/해제", command=_toggle_select_all).pack(
                side="left", padx=(8, 0))
            ttk.Button(btn_f, text="⏭ 선택 항목 패스 처리", command=_apply_pass).pack(side="right")
            ttk.Button(btn_f, text="닫기", command=dialog.destroy).pack(side="right", padx=(0, 8))

        else:  # 지자체 항목 선택 — 매칭된 중앙부처 1건 정보만 보여줌
            central_id = row.get("matched_central_id", "")
            dialog.title(f"연관 중앙부처 정책 — {row['servNm']}")
            dialog.geometry("560x220")

            central_row = by_id.get(central_id)
            if not central_row:
                ttk.Label(dialog, text="이름이 일치하는 중앙부처 정책을 찾지 못했습니다.",
                          padding=16).pack()
                ttk.Button(dialog, text="닫기", command=dialog.destroy).pack(pady=(0, 12))
                return

            status_disp = central_row["posting_status"] or "🆕 신규"
            info = (
                f"중앙부처 정책명: {central_row['servNm']}\n"
                f"매칭 신뢰도: {row['match_confidence']}\n"
                f"수집 상태: {'수집됨' if central_row['downloaded'] else '미수집'}\n"
                f"포스팅 상태: {status_disp}\n\n"
                f"중앙부처가 이미 포스팅완료라면, 이 지자체 건은 보통 패스 처리해도 됩니다."
            )
            ttk.Label(dialog, text=info, padding=16, justify="left").pack(anchor="w")

            def _pass_this():
                ok, _ = set_posting_status(row["servId"], "⏭ 패스", row["servNm"], row["source"])
                if ok:
                    self._log(f"⏭ 패스 처리 완료: {row['servNm']}")
                    self._refresh_listing_tree()
                    self._refresh_posting_tree()
                    dialog.destroy()
                else:
                    messagebox.showwarning("알림", "패스 처리에 실패했습니다.", parent=dialog)

            btn_f = ttk.Frame(dialog)
            btn_f.pack(fill="x", padx=12, pady=(0, 12))
            if row["posting_status"] != PROTECTED_STATUS:
                ttk.Button(btn_f, text="⏭ 이 지자체 정책 패스 처리", command=_pass_this).pack(side="right")
            ttk.Button(btn_f, text="닫기", command=dialog.destroy).pack(side="right", padx=(0, 8))

    def _export_listing(self):
        rows = self._get_visible_listing_rows()
        if not rows:
            messagebox.showwarning("알림", "내보낼 항목이 없습니다.")
            return
        default_name = f"복지서비스_리스트업_{datetime.date.today().isoformat()}.xlsx"
        os.makedirs(WORK_DIR, exist_ok=True)
        save_path = filedialog.asksaveasfilename(
            initialdir=WORK_DIR, initialfile=default_name, defaultextension=".xlsx",
            filetypes=[("Excel 파일", "*.xlsx")],
        )
        if not save_path:
            return

        while True:
            ok, result = export_listing_xlsx(rows, save_path)
            if ok:
                messagebox.showinfo("완료", f"엑셀 내보내기 완료:\n{result}")
                return
            if "openpyxl" in str(result):
                messagebox.showerror("오류", result)
                return
            retry = messagebox.askretrycancel(
                "엑셀 저장 실패",
                f"엑셀 내보내기에 실패했습니다.\n\n{result}\n\n"
                f"엑셀에서 파일을 완전히 닫은 뒤 [다시 시도]를 눌러주세요."
            )
            if not retry:
                return

    # ---------------- 포스팅 관리 ----------------
    def _get_visible_posting_rows(self, all_rows: list = None) -> list:
        source_rows = all_rows if all_rows is not None else build_listing_rows()
        rows = [r for r in source_rows if r["downloaded"]]  # 상세미수집 건은 대상 아님

        source = self.posting_source_var.get() if hasattr(self, "posting_source_var") else "전체"
        if source != "전체":
            rows = [r for r in rows if r["source"] == source]

        status_filter = self.posting_status_filter_var.get() if hasattr(self, "posting_status_filter_var") else "전체"
        if status_filter == "작업중만":
            rows = [r for r in rows if r["posting_status"] in IN_PROGRESS_STATUSES]
        elif status_filter == "패스 제외(기본)":
            # 패스/보류/포스팅완료/포스팅대기만 제외 — 🆕 신규도 그대로 보여야
            # 새로 추가된 항목을 놓치지 않고 바로 작업을 시작할 수 있다.
            rows = [r for r in rows if r["posting_status"] not in DEFAULT_FILTER_EXCLUDED_STATUSES]
        elif status_filter == "수집완료만":
            pass  # 이미 downloaded만 필터링됨
        elif status_filter != "전체":
            rows = [r for r in rows if r["posting_status"] == status_filter]

        search = self.posting_search_var.get().strip().lower() if hasattr(self, "posting_search_var") else ""
        if search:
            rows = [r for r in rows if search in r["servNm"].lower()]

        sort_label = self.posting_sort_var.get() if hasattr(self, "posting_sort_var") else "우선순위 높은순"
        return sort_rows(rows, sort_label)

    def _refresh_posting_tree(self, all_rows: list = None):
        if not hasattr(self, "posting_tree"):
            return
        # 새로고침 전 선택 상태를 기억해뒀다가 아래에서 복원한다 — 하단 버튼으로
        # 상태변경/결과저장 등을 하면 그때마다 _refresh_posting_tree가 불려서
        # 그리드가 통째로 delete/insert되는데, 이 복원이 없으면 매번 선택이
        # 풀려 사용자가 다시 그리드에서 항목을 클릭해야 했다.
        _prev_selection = self.posting_tree.selection()
        _prev_focus = self.posting_tree.focus()
        self.posting_tree.delete(*self.posting_tree.get_children())
        # 성능: _refresh_listing_tree와 동일한 이유로 한 번만 불러서 재사용.
        if all_rows is None:
            all_rows = build_listing_rows()
        rows = self._get_visible_posting_rows(all_rows)

        if not rows:
            self.posting_tree.insert("", "end", values=("", "", "표시할 항목이 없습니다", "", "", "", "", ""))
        else:
            for r in rows:
                status = r["posting_status"]
                tag = ""
                if r["excluded"]:
                    tag = "excluded"
                elif "포스팅완료" in status:
                    tag = "published"
                elif "패스" in status:
                    tag = "pass"
                elif "포스팅대기" in status:
                    tag = "waiting"
                elif status not in ("", POSTING_STATUS_LIST[0]):
                    # 🆕신규/포스팅완료/포스팅대기/패스/보류(위에서 이미 처리됨)를 제외한
                    # 나머지(가치판단대기~인포그래픽준비중)는 전부 "작업중" 단계이므로
                    # 노랑으로 표시. 인덱스 하드코딩 대신 이렇게 판별해야 나중에 단계가
                    # 추가/변경돼도 안전하다.
                    tag = "in_progress"
                attach_count = get_attachment_count_cached(r["folder"])
                attach_display = f"📎{attach_count}" if attach_count else "-"
                if r["source"] == "중앙부처":
                    n = len(r.get("related_lcgv_ids", []))
                    related_display = f"🔗 지자체 {n}건" if n else "-"
                else:
                    related_display = f"🔁 중앙있음({r['match_confidence']})" if r.get("matched_central_id") else "-"
                self.posting_tree.insert(
                    "", "end", iid=r["servId"],
                    values=(format_priority_score(r), r["source"], r["servNm"], r["servId"],
                            related_display, attach_display, status, r["first_seen_date"]),
                    tags=(tag,),
                )

        # 선택 복원 — 새로고침 후에도 목록에 남아있는 servId면 그대로 재선택하고
        # 포커스/스크롤 위치도 맞춰준다. 필터가 바뀌어 항목이 목록에서 아예
        # 사라진 경우에는 복원할 수 없으므로 자연스럽게 선택 없음 상태가 된다.
        _existing_ids = set(self.posting_tree.get_children())
        _restore = [iid for iid in _prev_selection if iid in _existing_ids]
        if _restore:
            self.posting_tree.selection_set(_restore)
            _focus_id = _prev_focus if _prev_focus in _existing_ids else _restore[0]
            self.posting_tree.focus(_focus_id)
            self.posting_tree.see(_focus_id)

        all_downloaded = [r for r in all_rows if r["downloaded"]]  # 위에서 계산한 all_rows 재사용
        published = sum(1 for r in all_downloaded if r["posting_status"] == PROTECTED_STATUS)
        self.posting_count_var.set(
            f"수집완료 전체 {len(all_downloaded)}건 중 포스팅완료 {published}건  (표시 중 {len(rows)}건)"
        )

    def _open_add_hub_service_dialog(self):
        """[v7.20 신규] "➕ 허브(종합) 항목 추가" 버튼 핸들러. 여러 서비스를
        사람이 직접 종합해서 쓸 원고를 붙여넣으면 create_hub_service()로
        새 servId를 만들고, 그 즉시 포스팅관리 목록에 "수집완료" 상태로
        나타난다(중앙부처/지자체와 똑같이 ①가치판단→②초안작성→③최종각색
        파이프라인을 그대로 탈 수 있음) — bokjiro API 재동기화로 지워지지
        않는 별도 저장소(services_list_hub.json)를 쓴다."""
        dlg = tk.Toplevel(self)
        dlg.title("허브(종합) 항목 추가")
        dlg.geometry("640x520")
        dlg.transient(self)

        ttk.Label(dlg, text="서비스명(제목 소재로 쓰일 이름 — 예: \"아동수당 관련 제도 종합\")").pack(
            anchor="w", padx=10, pady=(10, 2))
        nm_var = tk.StringVar(value="")
        ttk.Entry(dlg, textvariable=nm_var, width=70).pack(fill="x", padx=10)

        ttk.Label(
            dlg,
            text="원문(여러 서비스의 공식 안내를 직접 종합해서 붙여넣으세요 — "
                 "가치판단 프롬프트가 \"## 서비스 원문\"으로 그대로 받습니다):",
            wraplength=600, justify="left",
        ).pack(anchor="w", padx=10, pady=(10, 2))
        text_widget = tk.Text(dlg, wrap="word", font=("맑은 고딕", 9))
        text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        btn_f = ttk.Frame(dlg)
        btn_f.pack(fill="x", padx=10, pady=(0, 10))

        def on_save():
            nm = nm_var.get().strip()
            raw_text = text_widget.get("1.0", "end").strip()
            if not nm:
                messagebox.showwarning("알림", "서비스명을 입력하세요.", parent=dlg)
                return
            if not raw_text:
                messagebox.showwarning("알림", "원문을 입력하세요.", parent=dlg)
                return
            serv_id = create_hub_service(nm, raw_text)
            self._log(f"➕ 허브(종합) 항목 추가: {nm} ({serv_id})")
            self.posting_source_var.set("허브")  # 방금 만든 항목이 바로 보이도록 필터도 전환
            self._refresh_posting_tree()
            dlg.destroy()

        ttk.Button(btn_f, text="저장", command=on_save).pack(side="right")
        ttk.Button(btn_f, text="취소", command=dlg.destroy).pack(side="right", padx=(0, 8))

    def _get_selected_posting_row(self):
        sel = self.posting_tree.selection()
        if not sel:
            return None
        sid = sel[0]
        for r in build_listing_rows():
            if r["servId"] == sid:
                return r
        return None

    def _on_posting_select(self):
        row = self._get_selected_posting_row()
        if row is None:
            return
        # v5.8: _refresh_posting_tree()는 상태변경/프롬프트 복사·저장 등
        # 거의 모든 액션 뒤에 "선택 복원"을 위해 selection_set()을 다시
        # 호출하는데, Tkinter는 선택된 행이 그대로여도 <<TreeviewSelect>>를
        # 재발생시킨다. 예전에는 이 재선택마다 무조건 키워드 입력창을
        # 서비스명 전체로 되돌려써서, 사용자가 검색량이 잘 안 잡히는 긴
        # 정책명을 직접 줄여 입력해도(예: "건강보험 면제 지원" ->
        # "건강보험 면제") 바로 다음 버튼 클릭 한 번에 조용히 원래 전체
        # 이름으로 되돌아가버리는 문제가 있었음 — 그 상태로 프롬프트를
        # 만들면 get_cached_research()가 되돌아간 전체 이름으로 캐시를
        # 조회해서, 방금 축약 키워드로 만들어둔 리서치 결과와 매치가 안 돼
        # "리서치 미실행"/검색량 없음으로 보이는 원인이었다(사용자 리포트).
        # 실제로 "다른 서비스로 선택이 바뀐 경우"에만 키워드칸을 초기화
        # 하도록 servId를 비교해 같은 행 재선택은 그냥 건너뛴다.
        if getattr(self, "_last_posting_select_id", None) == row["servId"]:
            return
        self._last_posting_select_id = row["servId"]
        if row.get("excluded"):
            self._log(f"❌ [{row['servNm']}] 우선순위 계산에서 제외됨 — 사유: {row['exclude_reason']}")
        if hasattr(self, "research_keyword_var"):
            # [Ver10.08] 빠른 판정 결과가 있으면 그 "리서치 키워드"로, 없으면 서비스명으로 채운다.
            quick = get_stage_output(row["servId"], "quick_judgment")
            qj = parse_quick_judgment(quick) if quick else {}
            kw = qj.get("keywords") or row["servNm"]
            self.research_keyword_var.set(kw)
            self._auto_keywords = kw
            cached = get_cached_research((split_keyword_line(kw) or [""])[0])
            if cached:
                self.research_status_var.set(f"✓ 리서치 완료 ({cached['researched_at']})")
            else:
                self.research_status_var.set("리서치 미실행")
            self._show_quick_judgment_status(qj)
        if hasattr(self, "auto_prep_status_var"):
            self.auto_prep_status_var.set("")
        self._load_competitor_blogs_for_row(row)   # [Ver10.08] 경쟁 블로그 칸(서비스별)
        self._show_blog_panel(False)   # [Ver10.10] 경쟁 블로그 칸은 접고 시작

    def _pass_selected_posting(self):
        """[Ver10.09] 목록 아래 "⏭ 이 글 패스" — 검토하다 그만둘 글(여러 개 선택 가능)을 패스로 둔다.
        예전 STEP 5 상태 콤보를 대신한다. 패스·보류한 글을 다시 하려면 STEP 1 복사를 누르면 묻는다."""
        sel_ids = self.posting_tree.selection()
        if not sel_ids:
            messagebox.showwarning("알림", "먼저 목록에서 패스할 글을 선택하세요.")
            return
        names = [(self.posting_tree.item(i, "values") or [None, None, i])[2] for i in sel_ids[:3]]
        more = f" 외 {len(sel_ids) - 3}건" if len(sel_ids) > 3 else ""
        if not messagebox.askyesno("이 글 패스",
                f"{len(sel_ids)}건을 '⏭ 패스'로 둡니다.\n({', '.join(str(n) for n in names)}{more})\n\n"
                "저장된 판정·초안 등은 그대로 남습니다. 다시 하려면 그 글을 골라 STEP 1 복사를 누르세요."):
            return
        self._apply_posting_status_change("⏭ 패스")

    def _goto_infographic_tab(self):
        """[Ver10.09] STEP 4 "→ 인포그래픽으로 이동" — 지금 고른 글을 대상 서비스로 맞추고 5)탭으로."""
        self._refresh_ig_service_list()
        row = self._get_selected_posting_row()
        if row is not None:
            for key, r in getattr(self, "_ig_service_rows", {}).items():
                if r["servId"] == row["servId"]:
                    self.ig_service_var.set(key)
                    self._generate_infographic_title_list()
                    self._card_show_folder()
                    break
        self.notebook.select(self.infographic_tab)

    def _goto_keyword_reg_tab(self):
        """[Ver10.09] 5)탭 "인포그래픽 완료 → 6)키워드 등록으로 이동"."""
        self._refresh_keyword_reg_preview()
        self.notebook.select(self.keyword_reg_tab)

    def _apply_posting_status_change(self, new_status: str):
        """[Ver10.09] "⏭ 이 글 패스"가 쓴다(예전 STEP 5 "적용"). 그리드에서 여러 항목을 다중선택해도
        기존에는 첫 번째 선택 항목에만 적용됐던 문제를 고쳐, 선택된 항목
        전부에 상태변경을 적용한다. 선택이 1건뿐이면 기존과 동일하게
        동작(중앙부처+포스팅완료 시 연관 지자체 미처리 확인 팝업 등).
        2건 이상 선택된 경우에는 항목마다 팝업을 띄우면 너무 번거로우므로,
        연관 지자체 미처리로 막힌 건은 조용히 건너뛰고 마지막에 결과를
        요약해서 보여준다."""
        sel_ids = self.posting_tree.selection()
        if not sel_ids:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        rows_by_id = {r["servId"]: r for r in build_listing_rows()}
        rows = [rows_by_id[sid] for sid in sel_ids if sid in rows_by_id]
        if not rows:
            return

        if len(rows) == 1:
            row = rows[0]
            if row["source"] == "중앙부처" and new_status == PROTECTED_STATUS:
                unresolved = get_unresolved_related_lcgv_ids(row, rows_by_id)
                if unresolved:
                    if messagebox.askyesno(
                        "⚠️ 연관 지자체 정책 미처리",
                        f"'{row['servNm']}'과 이름이 유사한 지자체 정책 중 아직 처리되지 "
                        f"않은 항목이 {len(unresolved)}건 있어 포스팅완료로 바꿀 수 "
                        f"없습니다.\n\n지금 연관 정책을 확인하시겠습니까?"
                    ):
                        self._show_related_policies_popup(row)
                    return
            ok, reason = set_posting_status(row["servId"], new_status, row["servNm"], row["source"])
            if not ok:
                messagebox.showwarning("⚠️ 포스팅완료 보호", reason)
                return
            # [v7.8 버그 수정] "⏭ 패스" 처리 직후 _refresh_posting_tree()가
            # 같은 행을 다시 selection_set()으로 복원하는데, _on_posting_
            # select()는 "같은 servId면 재선택은 건너뛴다"는 가드가 있어서
            # (v6.x, 문서 위쪽 주석 참고) 이 경우엔 그 가드에 걸려 검색
            # 키워드 칸이 초기화되지 않았다(사용자 리포트: "이 글 패스하고
            # 새 글 시작 버튼 클릭시 검색키워드의 인풋박스가 초기화 안돼").
            # 패스는 "이 항목은 끝, 다음으로"라는 의도가 분명한 액션이므로
            # 여기서 명시적으로 비워주고, _last_posting_select_id도 지워
            # 다음 선택 때 확실히 새로 채워지게 한다.
            if new_status == "⏭ 패스":
                if hasattr(self, "research_keyword_var"):
                    self.research_keyword_var.set("")
                if hasattr(self, "research_status_var"):
                    self.research_status_var.set("")
                self._last_posting_select_id = None
            self._refresh_posting_tree()
            self._refresh_listing_tree()
            return

        # ---- 다중선택(2건 이상) ----
        changed, blocked, failed = [], [], []
        for row in rows:
            if row["source"] == "중앙부처" and new_status == PROTECTED_STATUS:
                unresolved = get_unresolved_related_lcgv_ids(row, rows_by_id)
                if unresolved:
                    blocked.append(row)
                    continue
            ok, reason = set_posting_status(row["servId"], new_status, row["servNm"], row["source"])
            if ok:
                changed.append(row)
            else:
                failed.append((row, reason))

        if new_status == "⏭ 패스" and changed:
            if hasattr(self, "research_keyword_var"):
                self.research_keyword_var.set("")
            if hasattr(self, "research_status_var"):
                self.research_status_var.set("")
            self._last_posting_select_id = None
        self._refresh_posting_tree()
        self._refresh_listing_tree()

        lines = [f"✅ {len(changed)}건 상태 변경 완료 → {new_status}"]
        if blocked:
            names = ", ".join(r["servNm"] for r in blocked[:5])
            more = f" 외 {len(blocked) - 5}건" if len(blocked) > 5 else ""
            lines.append(f"⚠️ 연관 지자체 미처리로 건너뜀: {len(blocked)}건 ({names}{more})")
        if failed:
            names = ", ".join(r["servNm"] for r, _ in failed[:5])
            more = f" 외 {len(failed) - 5}건" if len(failed) > 5 else ""
            lines.append(f"❌ 변경 실패: {len(failed)}건 ({names}{more})")
        summary = "\n".join(lines)
        self._log(summary.replace("\n", " / "))
        if blocked or failed:
            messagebox.showinfo("완료 처리 결과", summary)

    def _check_research_api_keys(self) -> bool:
        """2-B/2-C에 필요한 API 인증정보가 다 있는지 확인. 빠진 게 있으면
        팝업으로 안내하고 설정 탭으로 이동시킨 뒤 False를 반환한다.
        (더 이상 "미확인 (설정 탭에서 등록)" 문구를 결과에 섞어 내보내지
        않고, 애초에 실행을 막아서 항상 완전한 데이터로만 진행하도록 함)"""
        keys = get_research_api_keys()
        missing = []
        if not (keys["naver_ad_api_key"] and keys["naver_ad_secret_key"] and keys["naver_ad_customer_id"]):
            missing.append("네이버 검색광고 API (2-B 검색량 조회)")
        if not (keys["naver_openapi_client_id"] and keys["naver_openapi_client_secret"]):
            missing.append("네이버 오픈API (2-C 블로그 제목 분석)")

        if missing:
            messagebox.showwarning(
                "API 설정 필요",
                "다음 API 인증정보가 아직 설정되지 않았습니다:\n\n"
                + "\n".join(f"- {m}" for m in missing)
                + "\n\n'8)설정' 탭에서 먼저 등록한 뒤 다시 시도해주세요."
            )
            if hasattr(self, "notebook") and hasattr(self, "settings_tab"):
                self.notebook.select(self.settings_tab)
            return False
        return True

    def _warn_missing_prompt_files(self):
        """시작 시 프롬프트 .md 파일이 없으면 로그에 안내한다. 코드에
        내장 기본값이 없으므로(순수 외부 파일 관리 방식), 파일을 채워
        넣기 전까지는 해당 프롬프트 복사 버튼을 눌러도 오류가 난다는
        점을 미리 알려주기 위함."""
        for label, path in self._missing_prompt_files_at_startup:
            self._log(f"⚠ {label} 프롬프트 파일 없음: {path}  (이 .md 파일을 채워 넣어야 해당 단계 프롬프트 복사 가능)")
        self._log(f"📂 프롬프트 폴더: {PROMPT_DIR}")

    def _clear_research_keyword(self):
        """[Ver9.32 신규] 검색 키워드 칸과 리서치 상태 문구만 비운다. 리서치 캐시는 지우지 않는다."""
        self.research_keyword_var.set("")
        if hasattr(self, "research_status_var"):
            self.research_status_var.set("")

    def _update_title_manual_len(self):
        """[Ver9.32 신규] 직접 입력 제목 칸의 글자수(공백 포함, 앞뒤 공백 제외). 후보 라벨의 "(OO자)"와
        같은 기준이고, 60자(TITLE_MAX_LEN)를 넘으면 ⚠️를 붙인다."""
        if not hasattr(self, "title_manual_len_var"):
            return
        n = len(self.title_cand_manual_var.get().strip())
        self.title_manual_len_var.set(f"({n}자)" + (" ⚠️" if n > TITLE_MAX_LEN else ""))

    def _kw_vars(self, which: str = "prep"):
        """[Ver10.08] 키워드 칸 두 개 — "prep" = STEP 1 자동준비 키워드, "ai" = STEP 2 AI 요청 키워드.
        (키워드 칸 StringVar, 그 아래 상태 줄 StringVar)"""
        if which == "ai" and hasattr(self, "ai_kw_var"):
            return self.ai_kw_var, self.ai_kw_status_var
        return self.research_keyword_var, self.research_status_var

    def _all_research_keywords(self, row) -> list:
        """본 분석·초안·최종각색 복사에 넣을 리서치 키워드 — 자동준비 키워드 + AI 요청 키워드(중복 제외)."""
        # [Ver10.10] 칸이 하나로 합쳐졌으므로 STEP 1 자동 리서치 키워드 + 지금 칸의 키워드(Claude 재요청 등)
        kws = split_keyword_line(getattr(self, "_auto_keywords", ""))
        kws += [k for k in split_keyword_line(self.research_keyword_var.get()) if k not in kws]
        return kws or [row["servNm"]]

    def _run_keyword_research(self, which: str = "prep"):
        kv, sv = self._kw_vars(which)
        keyword = kv.get().strip()
        if not keyword:
            messagebox.showwarning("알림", "검색 키워드를 입력하세요 (항목을 선택하면 서비스명이 자동으로 채워집니다).")
            return
        if not self._check_research_api_keys():
            return
        if getattr(self, "_research_running", False):
            messagebox.showinfo("실행 중", "이미 리서치가 진행 중입니다.")
            return

        # [v6.9] 콤마(,)로 구분하면 여러 키워드 후보를 한 번에 리서치한다
        # (예: 정식명/약칭 비교). 콤마 없이 하나만 입력하면 기존과 동일하게
        # 동작한다(하위 호환).
        keywords = split_keyword_line(keyword)
        if not keywords:
            messagebox.showwarning("알림", "검색 키워드를 입력하세요.")
            return

        self._research_running = True
        self._research_which = which
        sv.set(f"⏳ 리서치 시작중... (키워드 {len(keywords)}개)")
        self._log(f"🔍 키워드 리서치 시작: {', '.join(keywords)}")

        def task():
            try:
                results = run_keyword_research_multi(keywords, log_fn=self._log)
                for kw, research in zip(keywords, results):
                    set_cached_research(kw, research)
            except Exception as e:
                self._log(f"✗ 리서치 실패: {e}")
            finally:
                self.log_queue.put(("RESEARCH_DONE", keywords))

        threading.Thread(target=task, daemon=True).start()

    def _copy_research_reply_for_posting(self, which: str = "ai"):
        """[v7.2 신규, 정책뉴스 Ver9.09 "📋 A에게 결과 전달"에서 이식]
        위 "🔍 키워드 리서치 실행"으로 캐시된 결과를, AI가 프롬프트
        실행 중 특정 키워드의 검색량·자동완성을 요청했을 때 그대로
        붙여넣어 돌려줄 수 있는 답변 형식으로 정리해 클립보드에
        복사한다.

        [정책뉴스와의 캐시 구조 차이에 유의해 이식함] 정책뉴스는
        콤마로 묶인 여러 키워드를 "원본 문자열 전체"를 캐시 키로 묶어
        저장하지만(cached["is_multi"]/cached["items"]), 복지로의
        set_cached_research()/_run_keyword_research()는 콤마로 나눈
        키워드 "각각"을 개별 키로 저장한다(그대로가 기존 캐시 구조이며
        이번에 바꾸지 않음). 그래서 여기서는 정책뉴스의 cached["is_multi"]
        분기를 그대로 가져오지 않고, 복지로 방식에 맞게 검색 키워드
        칸의 콤마 구분 키워드를 각각 조회해 이어붙인다."""
        kv, sv = self._kw_vars(which)
        raw = kv.get().strip()
        if not raw:
            messagebox.showwarning("알림", "요청 키워드 칸이 비어 있습니다.\nAI가 요청한 키워드를 먼저 붙여넣고 '키워드 리서치 실행'을 누르세요.")
            return

        keywords = split_keyword_line(raw)
        if not keywords:
            messagebox.showwarning("알림", "검색 키워드를 입력하세요.")
            return

        cache = load_research_cache()
        missing = [kw for kw in keywords if kw not in cache]
        if missing:
            messagebox.showwarning(
                "리서치 결과 없음",
                "다음 키워드는 아직 리서치 결과가 없습니다:\n" + ", ".join(missing) +
                "\n\n먼저 '🔍 키워드 리서치 실행'을 눌러 조회하세요."
            )
            return

        blocks = [format_research_for_prompt(cache[kw]) for kw in keywords]
        body = "\n---\n".join(blocks) if len(blocks) > 1 else blocks[0]

        content = f"아래는 요청하신 키워드의 실측 결과입니다.\n\n{body}"
        self.clipboard_clear()
        self.clipboard_append(content)
        sv.set("✅ 키워드 리서치 결과를 클립보드에 넣었습니다 → 같은 대화창에 붙여넣고, Claude 새 답을 복사해 "
               "'💾 가치판단 저장(메모리값 자동저장)' 다시 누르기")
        self._log(f"📋 AI에게 리서치 결과 전달용 복사 완료: {', '.join(keywords)}")

    # ──────────────────────────────────────────────────────
    # [v7.17 신규, v7.18에서 설명 갱신] 📝 제목 후보 확정.
    # [Ver10.09] 제목 사전체크(헤드리스 크롬 자동 검색·강중약 판정)는 효과가 없어 삭제(사용자).
    # v7.4~v7.16까지는 이 자리에 라디오버튼+4행+자동 사전체크를 쓰는
    # "🔑 키워드 후보 확정" 패널이 따로 있었으나, 정책뉴스 STEP1.5(키워드
    # 리서치)엔 그런 후보 선택 UI가 없다는 지적을 받아 v7.18에서
    # 제거하고 위 "🔍 키워드 리서치" 프레임의 버튼 하나(재조사 요청
    # 키워드 자동 채우기)로 단순화했다 — 정책뉴스에서도 후보를 실측
    # 검색해 등급 매기는 구조는 제목(STEP4)에만 있고, 이 titlecand_f가
    # 바로 그 역할이다. 확정 결과는 research_keyword_var가 아니라
    # confirmed_titles.json에 저장돼 ③ 초안작성 프롬프트에 자동으로
    # 실려 나간다.
    # ──────────────────────────────────────────────────────

    def _extract_title_candidates_for_posting(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return

        text = get_stage_output(row["servId"], "value_judgment")
        if not text:
            text = get_stage_output(row["servId"], "prescreening")
        if not text:
            messagebox.showwarning(
                "가치판단 결과 없음",
                "저장된 가치판단 결과가 없습니다.\n"
                "먼저 STEP 2 본 분석을 실행하고 '💾 가치판단 저장(메모리값 자동저장)'으로 저장하세요."
            )
            return

        candidates = parse_value_judgment_title_candidates(text)
        if not candidates:
            messagebox.showinfo(
                "제목 후보 없음",
                "가치판단 결과에서 \"## 제목 후보\" 섹션을 찾지 못했습니다.\n"
                "핵심 키워드가 아직 \"(재조사 필요)\" 상태라 [2-A단계]를 건너뛰었을 수 있습니다 — "
                "먼저 키워드 리서치를 마치고 핵심 키워드를 확정지은 뒤 가치판단 결과를 다시 저장하세요."
            )

        for i in range(4):
            if i < len(candidates):
                c = candidates[i]
                self.title_cand_texts[i] = c["title"]
                self.title_cand_intros[i] = c.get("intro", "")
                self.title_cand_reasons[i] = c.get("reason", "")
                self.title_cand_label_vars[i].set(f"({len(c['title'])}자) {c['title']}")
            else:
                self.title_cand_texts[i] = ""
                self.title_cand_intros[i] = ""
                self.title_cand_reasons[i] = ""
                self.title_cand_label_vars[i].set("")
        self.title_cand_choice.set(str(0)) if candidates else self.title_cand_choice.set("")
        if candidates:
            self.title_cand_status_var.set(
                f"제목 후보 {len(candidates)}개 추출 완료 — 본문 적합도를 먼저 보고, "
                f"필요하면 🔍로 확인한 뒤 확정하세요.")
        self._log(f"📝 제목 후보 {len(candidates)}개 추출: {row['servNm']}")

    def _on_title_cand_choice(self):
        """[Ver9.30] 후보 라디오버튼을 고르면 가치판단이 남긴 "선택 근거"를 상태줄에 보여 준다."""
        choice = self.title_cand_choice.get()
        if not choice or choice == "manual":
            return
        try:
            idx = int(choice)
        except ValueError:
            return
        reason = self.title_cand_reasons[idx] if idx < len(self.title_cand_reasons) else ""
        if reason and hasattr(self, "title_cand_status_var"):
            self.title_cand_status_var.set(f"[{idx+1}] 선택 근거: {reason}")

    def _title_search_query(self, title, front=False, back=False):
        if front:
            return tchk_split_title_front(title)
        if back:
            return tchk_split_title_back(title) or title
        return title

    def _open_naver_search_title_candidate(self, idx, blog=True, front=False, back=False):
        title = self.title_cand_texts[idx] if idx < len(self.title_cand_texts) else ""
        if not title:
            messagebox.showwarning("알림", "이 자리에는 추출된 후보가 없습니다.")
            return
        if self._check_ip_before_naver_open():
            return
        q = self._title_search_query(title, front, back)
        open_naver_search_in_chrome(q, blog_only=True)
        what = "앞구" if front else ("뒷구" if back else "블로그")
        self._log(f"🌐 제목 후보 검색 열기({what}): {q}")

    def _open_naver_search_title_manual(self, blog=True, front=False, back=False):
        title = self.title_cand_manual_var.get().strip()
        if not title:
            messagebox.showwarning("알림", "직접 입력 칸에 검색할 제목을 입력하세요.")
            return
        if self._check_ip_before_naver_open():
            return
        q = self._title_search_query(title, front, back)
        open_naver_search_in_chrome(q, blog_only=True)
        what = "앞구" if front else ("뒷구" if back else "블로그")
        self._log(f"🌐 직접 입력 제목 검색 열기({what}): {q}")

    def _confirm_title_candidate(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        choice = self.title_cand_choice.get()
        if not choice:
            messagebox.showwarning("알림", "먼저 후보를 하나 선택하세요(라디오버튼).")
            return
        if choice == "manual":
            title = self.title_cand_manual_var.get().strip()
            # [v7.19] 직접 입력한 제목에는 가치판단이 낸 도입부 지시가
            # 없다 — 초안작성은 지시가 없으면 스스로 화두를 추론하는
            # 폴백을 이미 갖고 있으므로 빈 문자열로 저장해도 안전하다.
            intro = ""
            # [Ver9.30] 직접 고친 제목도 가치판단 V8 [제목 형식 규칙]으로 한 번 점검한다.
            tv = validate_title(title)
            if title and tv["warnings"]:
                msg = "직접 입력한 제목에 다음 사항이 확인됩니다:\n\n" + "\n".join(
                    f"• {w}" for w in tv["warnings"])
                if not messagebox.askyesno("제목 점검 결과", msg + "\n\n그래도 이 제목으로 확정하시겠습니까?"):
                    return
        else:
            idx = int(choice)
            title = self.title_cand_texts[idx] if idx < len(self.title_cand_texts) else ""
            intro = self.title_cand_intros[idx] if idx < len(self.title_cand_intros) else ""
        if not title:
            messagebox.showwarning("알림", "선택한 후보에 제목이 없습니다.")
            return
        save_confirmed_title(row["servId"], title, intro)
        self.title_cand_status_var.set(f"✅ 확정: \"{title}\" — STEP 4 초안 복사 때 자동 전달됩니다.")
        self._log(f"✅ 제목 확정: {row['servNm']} → {title}")

    def _clear_confirmed_title(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        data = load_confirmed_titles()
        if row["servId"] in data:
            del data[row["servId"]]
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(get_confirmed_title_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        self.title_cand_status_var.set("확정 취소됨 — 초안작성 시 다시 직접 짓습니다.")
        self._log(f"🗑 제목 확정 취소: {row['servNm']}")

    def _show_research_summary_popup(self, which: str = "prep"):
        """[v7.0 신규, 정책뉴스 Ver8.22에서 이식] "🔍 키워드 리서치 실행"
        (가치판단 프롬프트 자동 첨부용, 캐시에 저장)과는 완전히 별도로
        동작한다 — 클릭 즉시 검색 키워드 입력창의 키워드로 자체적으로
        리서치를 실행하고, 끝나면 바로 팝업으로 검색량·자동완성 결과만
        보여준다(캐시를 공유하지 않으므로 어느 버튼을 먼저 눌러도 서로
        영향 없음). 기존 _run_keyword_research와 동일하게 백그라운드
        스레드 + log_queue 폴링 방식을 쓴다(GUI가 멈추지 않도록)."""
        kv, sv = self._kw_vars(which)
        keyword = kv.get().strip()
        if not keyword:
            messagebox.showwarning("알림", "검색 키워드를 입력하세요 (항목을 선택하면 서비스명이 자동으로 채워집니다).")
            return
        if not self._check_research_api_keys():
            return
        if getattr(self, "_research_summary_running", False):
            messagebox.showinfo("실행 중", "이미 검색량·자동완성 조회가 진행 중입니다.")
            return

        keywords = split_keyword_line(keyword)
        if not keywords:
            messagebox.showwarning("알림", "검색 키워드를 입력하세요.")
            return

        self._research_summary_running = True
        self._summary_which = which
        sv.set(f"⏳ 검색량·자동완성 조회 중... (후보 {len(keywords)}개)")
        self._log(f"🔍 검색량·자동완성 조회 시작: {', '.join(keywords)}")

        def task():
            try:
                items = run_keyword_research_multi(keywords, log_fn=self._log)
            except Exception as e:
                items = []
                self._log(f"✗ 검색량·자동완성 조회 실패: {e}")
            self.log_queue.put(("RESEARCH_SUMMARY_DONE", items))

        threading.Thread(target=task, daemon=True).start()

    def _open_research_summary_popup(self, items: list):
        """[v7.0 신규, 정책뉴스 Ver8.22에서 이식] _show_research_summary_popup()의
        백그라운드 조회가 끝난 뒤 _poll_log_queue가 호출하는 팝업 표시부.
        메인창 위치와 무관하게 항상 "화면(모니터)" 기준 정중앙에 뜬다."""
        if not items:
            messagebox.showwarning("알림", "조회 결과가 없습니다(API 키 미설정이거나 조회 실패).")
            return

        summary = format_research_summary_only(items)

        top = tk.Toplevel(self)
        top.title("검색량·자동완성 결과")

        pw, ph = 560, 480
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        px = (sw - pw) // 2
        py = (sh - ph) // 2
        top.geometry(f"{pw}x{ph}+{px}+{py}")
        top.transient(self)
        top.grab_set()

        ttk.Label(top, text="키워드별 검색량·자동완성",
                  font=("맑은 고딕", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        ttk.Label(top, text="다른 곳에 붙여넣을 수 있도록 결과만 간단히 모았습니다. "
                             "맨 아래에 조회한 키워드만 콤마로 나열되어 있습니다. "
                             "키워드를 바꿔 다시 조회한 뒤 이 버튼을 다시 눌러 비교할 수 있습니다.",
                  foreground="gray", wraplength=530, justify="left").pack(
            anchor="w", padx=12, pady=(0, 8))

        text_f = ttk.Frame(top)
        text_f.pack(fill="both", expand=True, padx=12)
        text_box = tk.Text(text_f, wrap="word", font=("맑은 고딕", 9))
        vsb = ttk.Scrollbar(text_f, orient="vertical", command=text_box.yview)
        text_box.configure(yscrollcommand=vsb.set)
        text_box.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")
        text_box.insert("1.0", summary)

        def _copy():
            self.clipboard_clear()
            self.clipboard_append(summary)
            self._log("📋 검색량·자동완성 결과 복사 완료")

        btn_f = ttk.Frame(top)
        btn_f.pack(fill="x", padx=12, pady=(8, 12))
        ttk.Button(btn_f, text="📋 복사하기", command=_copy).pack(side="left")
        ttk.Button(btn_f, text="닫기", command=top.destroy).pack(side="right")

    def _copy_value_judgment_prompt(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        if not self._check_research_api_keys():
            return
        detail_path = os.path.join(row["folder"], "detail.json")
        if not os.path.exists(detail_path):
            messagebox.showerror("오류", "detail.json을 찾을 수 없습니다. 상세조회를 먼저 실행하세요.")
            return
        with open(detail_path, "r", encoding="utf-8") as f:
            detail = json.load(f)

        # [v6.9] 콤마(,)로 구분해 여러 키워드를 리서치했다면, 캐시에 실제로
        # 있는 항목만 모아 research_map을 구성한다(research_map은 원래도
        # 여러 항목을 받는 범용 구조 — build_*_package가 그대로 처리한다).
        keywords = self._all_research_keywords(row)   # [Ver10.08] 자동준비 + AI 요청 키워드
        # [v6.9.1] get_cached_research()는 호출마다 캐시 파일 전체를
        # 디스크에서 읽으므로, 키워드마다 두 번씩 부르지 않고 한 번만
        # 읽어 재사용한다(콤마 다중 키워드일수록 절약 효과가 커짐).
        _research_cache_now = load_research_cache()
        research_map = {kw: _research_cache_now[kw] for kw in keywords if kw in _research_cache_now}
        keyword = keywords[0]
        if not research_map:
            if not messagebox.askyesno(
                "리서치 없음",
                f"'{', '.join(keywords)}'로 아직 키워드 리서치를 실행하지 않았습니다.\n"
                f"리서치 데이터 없이 원문만으로 프롬프트를 복사할까요?\n"
                f"(먼저 '🔍 키워드 리서치 실행'을 누르시는 걸 권장합니다)"
            ):
                return

        attachments = list_attachment_files(row["folder"])
        try:
            package = build_value_judgment_package(detail, row["source"], research_map, attachments,
                                                     serv_id=row["servId"])
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(package)
        self._log(f"📋 가치판단 프롬프트 복사 완료: {row['servNm']} (첨부 {len(attachments)}건)")

        self._show_attachment_reminder_popup(
            row, attachments,
            note_extra="첨부가 없거나 부실해도 원문에 관련 홈페이지가 있으면 Claude가 직접 열어 "
                        "보강을 시도하지만, 첨부 서식자료가 있다면 함께 올려주는 편이 더 정확합니다. "
                        "⓪ 사전스크리닝 결과를 저장해 두었다면 자동으로 함께 반영됩니다.")

        if advance_posting_status(row["servId"], "🔎 가치판단대기", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_value_judgment_prompt_only(self):
        """① 가치판단 프롬프트 "문구만" 클립보드에 복사한다(원문·첨부·
        리서치·이전단계 결과 없이). 같은 대화창에서 이미 자료를 준
        상태에서 프롬프트 지시문만 다시 필요할 때 쓰는 용도. 그리드에서
        항목이 선택돼 있으면 "+자료 복사" 버튼과 동일하게 포스팅 상태도
        함께 넘겨준다 — 문구만 복사했다고 해서 그 단계 작업을 안 하는 게
        아니라 그냥 자료를 안 붙였을 뿐이므로, 상태는 똑같이 진행돼야
        진행 현황이 그리드에 정확히 반영된다."""
        try:
            prompt = get_prompt_value_judgment()
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        row = self._get_selected_posting_row()
        if row is None:
            self._log("📋 가치판단 프롬프트(문구만) 복사 완료")
            return
        self._log(f"📋 가치판단 프롬프트(문구만) 복사 완료: {row['servNm']}")
        if advance_posting_status(row["servId"], "🔎 가치판단대기", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _load_selected_detail(self, row):
        """선택 항목의 detail.json을 읽는다. 없으면 안내 후 None."""
        detail_path = os.path.join(row["folder"], "detail.json")
        if not os.path.exists(detail_path):
            messagebox.showerror("오류", "detail.json을 찾을 수 없습니다. 상세조회를 먼저 실행하세요.")
            return None
        with open(detail_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── [Ver10.08] STEP 1 빠른 판정 ──
    def _copy_quick_judgment_prompt(self):
        """빠른 판정 프롬프트 + 원문 + 첨부파일 이름만 복사(PDF·리서치·블로그 없음)."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        # [Ver10.09] 상태 콤보가 없어졌으므로, 패스·보류한 글을 다시 하려면 여기서 묻고 되살린다.
        if row.get("posting_status") in ("⏭ 패스", "⏸ 보류"):
            if not messagebox.askyesno("다시 작업",
                    f"'{row['servNm']}'은(는) '{row['posting_status']}' 상태입니다.\n다시 작업할까요?"):
                return
            set_posting_status(row["servId"], "🔎 가치판단대기", row["servNm"], row["source"])
        detail = self._load_selected_detail(row)
        if detail is None:
            return
        attachments = list_attachment_files(row["folder"])
        try:
            package = build_quick_judgment_package(detail, row["source"], attachments)
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(package)
        self._log(f"📋 빠른 판정 프롬프트 복사 완료: {row['servNm']} (공식자료 이름 {len(attachments)}건)")
        messagebox.showinfo(
            "빠른 판정 복사 완료",
            f"'{row['servNm']}' 빠른 판정 프롬프트를 복사했습니다.\n\n"
            "Claude 새 대화창에 붙여넣기만 하세요 — 이 단계에서는 공식자료를 올리지 않습니다.\n"
            "답 코드블럭을 복사한 뒤 STEP 1 '💾 판정결과 저장(메모리값 자동저장)'을 누르세요.")
        if advance_posting_status(row["servId"], "🔎 가치판단대기", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _show_quick_judgment_status(self, qj):
        """빠른 판정 결과를 STEP 1 상태 줄에 보여 준다(판정·필요 자료)."""
        if not hasattr(self, "quick_status_var"):
            return
        if not qj or not qj.get("verdict"):
            self.quick_status_var.set("")
            return
        head = "✅ 진행" if qj["verdict"] == "진행" else "⏸ 보류"
        text = f"빠른 판정: {head}" + (f" — {qj['reason']}" if qj.get("reason") else "")
        if qj["verdict"] == "진행":
            text += (f"\n공식자료 올리기: {qj.get('attach') or '(표시 없음)'}"
                     f"\n경쟁 블로그: {qj.get('blog') or '(표시 없음)'}")
        self.quick_status_var.set(text)

    def _after_quick_judgment_saved(self, row, content):
        """빠른 판정 저장 뒤: 보류면 확인 후 "⏸ 보류", 진행이면 리서치 키워드를 채우고 자료 자동 준비를 시작한다."""
        qj = parse_quick_judgment(content)
        self._show_quick_judgment_status(qj)
        if qj["verdict"] == "보류":
            if messagebox.askyesno(
                    "빠른 판정: 보류",
                    f"'{row['servNm']}' 빠른 판정이 '보류'입니다.\n이유: {qj['reason'] or '(없음)'}\n\n"
                    f"포스팅 상태를 '⏸ 보류'로 바꿀까요?"):
                ok, reason = set_posting_status(row["servId"], "⏸ 보류", row["servNm"], row["source"])
                if ok:
                    self._log(f"⏸ 빠른 판정 보류 → 상태 변경: {row['servNm']}")
                    self._refresh_posting_tree()
                    self._refresh_listing_tree()
                else:
                    messagebox.showwarning("상태 변경 안 됨", reason)
            return
        if qj["verdict"] != "진행":
            messagebox.showwarning(
                "판정 줄 없음",
                "저장은 했지만 결과에서 \"판정: 진행/보류\" 줄을 찾지 못했습니다.\n"
                "빠른 판정 답변의 코드블럭 전체를 붙여넣었는지 확인하세요.")
            return
        if qj["keywords"]:
            self.research_keyword_var.set(qj["keywords"])
            self._log(f"📋 빠른 판정 리서치 키워드 자동 채우기: {qj['keywords']}")
        self._start_auto_prep(row, qj)

    # ── [Ver10.08] 클립보드에서 바로 읽기(STEP 1 ②, STEP 2 ④) ──
    def _read_clipboard_result(self, stage_key: str):
        """Claude 답을 복사한 뒤 누르면 저장창 없이 클립보드에서 바로 읽는다.
        빠른 판정: "판정:" 줄이 있으면 저장 → 보류/진행 처리(진행이면 자료 자동 준비).
        본 분석: AI가 자료를 요청했으면 첨부 폴더를 열어 안내(저장하지 않음), 키워드 실측을 요청했으면
        리서치를 돌려 답변을 클립보드에 넣고, 결과면 저장한다. 알아볼 수 없으면 기존 붙여넣기 창을 연다."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        try:
            text = self.clipboard_get()
        except tk.TclError:
            text = ""
        text = strip_outer_code_fence(text)
        label = STAGE_RESULT_LABELS.get(stage_key, stage_key)
        if not text.strip():
            messagebox.showinfo("클립보드 비어 있음", "Claude 답을 먼저 복사하세요.\n(직접 붙여넣으려면 열리는 창에 넣으세요)")
            self._paste_and_save_stage_result(stage_key)
            return

        if stage_key == "quick_judgment":
            if not parse_quick_judgment(text)["verdict"]:
                messagebox.showinfo("판정 줄 없음", "클립보드에서 \"판정: 진행/보류\" 줄을 찾지 못했습니다.\n"
                                    "빠른 판정 답의 코드블럭을 복사했는지 확인하세요. 열리는 창에 직접 붙여넣어도 됩니다.")
                self._paste_and_save_stage_result(stage_key)
                return
            set_stage_output(row["servId"], stage_key, text)
            self._log(f"📥 {label} 저장 완료(클립보드): {row['servNm']} ({len(text)}자)")
            self._after_quick_judgment_saved(row, text)
            return

        if stage_key == "final_adaptation":
            # 최종각색은 제목·출처 점검과 문단 정리가 있는 확인 창으로 — 클립보드 내용을 채워 연다
            self._paste_and_save_stage_result(stage_key, prefill=text)
            return

        if stage_key == "draft":
            if re.search(r"^\s*##\s*(첨부파일 필요|핵심 키워드 확정 필요)", text, re.M):
                attach = list_attachment_files(row["folder"])
                msg = ("AI가 자료를 요청했습니다(저장하지 않음).\n\n" + text.strip()[:700]
                       + "\n\n요청한 파일을 같은 대화창에 올리고 \"올렸습니다\"라고 보낸 뒤, 새 답을 복사해 다시 초안 저장을 누르세요.")
                if attach and messagebox.askyesno("자료 요청", msg + "\n\n지금 공식자료 폴더를 열까요?"):
                    self._open_folder(os.path.join(row["folder"], "attachments"))
                elif not attach:
                    messagebox.showwarning("자료 요청", msg)
                return
            if re.search(r"^\s*##\s*정보 부족 판정", text, re.M):
                messagebox.showwarning("정보 부족", "AI가 공식 정보가 부족해 초안을 쓰지 않았습니다(저장하지 않음).\n\n"
                                       + text.strip()[:700] + "\n\n공식자료를 더 구할 수 없으면 목록 아래 '⏭ 이 글 패스'로 넘기세요.")
                return
            if not re.search(r"^\s*#{2,3}\s*(초안|제목|서론|본문)", text, re.M):
                messagebox.showinfo("결과 형식 아님", "클립보드 내용이 초안 결과로 보이지 않습니다.\n열리는 창에 직접 붙여넣어 저장하세요.")
                self._paste_and_save_stage_result(stage_key)
                return
            set_stage_output(row["servId"], stage_key, text)
            self._log(f"📥 {label} 저장 완료(클립보드): {row['servNm']} ({len(text)}자)")
            messagebox.showinfo("초안 저장", f"초안을 저장했습니다({len(text):,}자).\n다음: 최종각색 '📋 초안 + 프롬프트 복사'")
            return

        # 본 분석 — 자료 요청
        if re.search(r"^\s*##\s*(자료 요청|첨부파일 확인 필요|첨부파일 필요)", text, re.M):
            attach = list_attachment_files(row["folder"])
            msg = ("AI가 공식 자료를 요청했습니다(저장하지 않음).\n\n" + text.strip()[:700]
                   + "\n\n요청한 파일을 같은 대화창에 올리고 \"올렸습니다\"라고 보낸 뒤, 새 답을 복사해 다시 '💾 가치판단 저장(메모리값 자동저장)'을 누르세요.")
            if attach:
                if messagebox.askyesno("자료 요청", msg + "\n\n지금 공식자료 폴더를 열까요?"):
                    self._open_folder(os.path.join(row["folder"], "attachments"))
            else:
                messagebox.showwarning("자료 요청", msg + "\n\n이 서비스에는 받아 둔 공식자료가 없습니다 — "
                                       "공식 자료를 구할 수 없으면 목록 아래 '⏭ 이 글 패스'로 넘기세요.")
            self._log(f"📎 AI 자료 요청(공식 출처 확인): {row['servNm']}")
            return

        # 본 분석 — 키워드 실측 요청
        if re.search(r"^\s*##\s*키워드 리서치 요청", text, re.M):
            kws = extract_research_request_block_keywords(text)
            if not kws:
                messagebox.showinfo("키워드 없음", "AI의 키워드 요청에서 키워드 줄을 찾지 못했습니다.\n"
                                    "STEP 2 '검색 키워드' 칸에 직접 넣고 '🔍 키워드 리서치 실행' → '📋 AI에게 결과 전달'을 쓰세요.")
                return
            self.ai_kw_var.set(kws)
            self._run_research_then_reply(kws)
            return

        if not re.search(r"판정\s*:|##\s*제목 후보|##\s*공식 출처 목록|재조사\s*요청\s*키워드", text):
            messagebox.showinfo("결과 형식 아님", "클립보드 내용이 본 분석 결과로 보이지 않습니다.\n열리는 창에 직접 붙여넣어 저장하세요.")
            self._paste_and_save_stage_result(stage_key)
            return
        set_stage_output(row["servId"], stage_key, text)
        self._log(f"📥 {label} 저장 완료(클립보드): {row['servNm']} ({len(text)}자)")
        qj = parse_quick_judgment(text)
        if "보류" in (qj.get("verdict") or "") or re.search(r"판정\s*:\s*보류", text):
            if messagebox.askyesno("본 분석: 보류", f"'{row['servNm']}' 본 분석 판정이 '보류'입니다.\n"
                                   f"포스팅 상태를 '⏸ 보류'로 바꿀까요?"):
                ok, reason = set_posting_status(row["servId"], "⏸ 보류", row["servNm"], row["source"])
                if ok:
                    self._refresh_posting_tree()
                    self._refresh_listing_tree()
                else:
                    messagebox.showwarning("상태 변경 안 됨", reason)
            return
        rekw = extract_research_request_keywords(text)
        if rekw:
            self.ai_kw_var.set(rekw)
            self._log(f"📋 재조사 요청 키워드: {rekw}")
            self._run_research_then_reply(rekw)
            return
        self.auto_prep_status_var.set("✅ 본 분석 결과 저장 — 다음: STEP 3 '📋 제목 후보 불러오기'")

    def _run_research_then_reply(self, keywords: str):
        """AI가 요청한 키워드를 리서치하고, 끝나면 "AI에게 결과 전달" 답변을 클립보드에 넣는다."""
        if not self._check_research_api_keys():
            return
        self._research_then_reply = True
        self.ai_kw_status_var.set(f"⏳ AI가 요청한 키워드 리서치 중: {keywords} — 끝나면 결과를 클립보드에 넣습니다")
        self._run_keyword_research("ai")

    # ── [Ver10.08] 판정 읽기 뒤 자료 자동 준비(키워드 리서치 + 경쟁 블로그 스크랩) ──
    def _start_auto_prep(self, row, qj):
        keywords = split_keyword_line(qj.get("keywords") or row["servNm"])
        if getattr(self, "_auto_prep_running", False):
            messagebox.showinfo("실행 중", "자료 자동 준비가 이미 진행 중입니다.")
            return
        if hasattr(self, "research_keyword_var"):
            self.research_keyword_var.set(", ".join(keywords))   # [Ver10.10] 빈 칸으로 남던 것 고침
            self._auto_keywords = ", ".join(keywords)
        if not self._check_research_api_keys():
            self.auto_prep_status_var.set("⚠ API 설정이 없어 키워드 리서치를 못 했습니다 — 설정 탭에서 API 키를 넣고 "
                                          "'💾 판정결과 저장(메모리값 자동저장)'을 다시 누르세요")
            return
        want_blog = not (qj.get("blog") or "").strip().startswith("불필요")
        cfg = load_config()
        try:
            n_blog = max(0, min(5, int(cfg.get("auto_blog_count", 3))))
        except (TypeError, ValueError):
            n_blog = 3
        if not HAS_SELENIUM:
            want_blog = False
        exclude = [x.strip().lower() for x in str(cfg.get("my_blog_ids", "")).split(",") if x.strip()]
        self._auto_prep_running = True
        self.auto_prep_status_var.set(f"⏳ 자동 수집 중 — 키워드 리서치 {len(keywords)}개"
                                      + (f" → 경쟁 블로그 {n_blog}개 스크랩" if want_blog and n_blog else "")
                                      + " (1~3분)")
        self._log(f"⏳ 자료 자동 준비 시작: {row['servNm']} — {', '.join(keywords)}")
        out_dir = os.path.join(row["folder"], "competitor_blogs_md")

        def task():
            files, errors = [], []
            diag = {}
            try:
                results = run_keyword_research_multi(keywords, log_fn=self._log)
                for kw, research in zip(keywords, results):
                    set_cached_research(kw, research)
                links = pick_competitor_blog_links(results or [], exclude, n_blog) if want_blog else []
                diag["per_kw"] = [(k, len((r or {}).get("blog_titles") or [])) for k, r in zip(keywords, results or [])]
                diag["search_hits"] = sum(n for _k, n in diag["per_kw"])
                diag["blog_skipped"] = next((r.get("blog_skipped_reason") for r in (results or [])
                                             if r and r.get("blog_skipped_reason")), "")
                diag["links"] = len(links)
                if links:
                    driver = None
                    try:
                        driver = blog_scrap_build_driver()
                        for url in links:
                            try:
                                post = blog_scrap_scrape_post(driver, url)
                                files.append(blog_scrap_save_as_md(post, out_dir))
                                self._log(f"  📰 경쟁 블로그 스크랩: {post.get('title', '')[:40]}")
                            except Exception as e:
                                errors.append(f"{url} — {e}")
                            time.sleep(1)
                    finally:
                        if driver:
                            blog_scrap_cleanup_driver(driver)
            except Exception as e:
                errors.append(str(e))
            self.log_queue.put(("AUTO_PREP_DONE", {"row": row, "keywords": keywords, "files": files,
                                                   "errors": errors, "want_blog": want_blog, "qj": qj,
                                                   "diag": diag}))

        threading.Thread(target=task, daemon=True).start()

    def _on_auto_prep_done(self, p):
        self._auto_prep_running = False
        row, files = p["row"], p["files"]
        cache = load_research_cache()
        done = [k for k in p["keywords"] if k in cache]
        if files:
            blocks = []
            for i, path in enumerate(files, 1):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        body = f.read().strip()
                except OSError as e:
                    body = f"(읽기 실패: {e})"
                blocks.append(f"### 블로그 {i} — {os.path.basename(path)}\n\n{body}")
            text = "\n\n".join(blocks)
            if getattr(self, "_competitor_blog_serv", None) and self._competitor_blog_serv.get("servId") == row["servId"]:
                self.competitor_blog_text.delete("1.0", "end")
                self.competitor_blog_text.insert("1.0", text)
                self._save_competitor_blogs()
            else:
                try:
                    with open(self._competitor_blog_path(row), "w", encoding="utf-8") as f:
                        f.write(text + "\n")
                except OSError as e:
                    p["errors"].append(str(e))
        if p.get("manual"):
            self._update_competitor_blog_info()
            if not files:
                self.competitor_blog_info_var.set("❌ 스크랩 못 함 — 주소를 확인하세요")
            self._log(f"📰 경쟁 블로그 직접 스크랩 끝: {len(files)}개" + (f" (실패 {len(p['errors'])}건)" if p["errors"] else ""))
            return
        if hasattr(self, "research_status_var"):
            self.research_status_var.set(f"✅ 리서치 완료 ({len(done)}/{len(p['keywords'])}건)" if done else "❌ 리서치 실패")
        diag = p.get("diag", {})
        lines = []
        if diag.get("per_kw"):
            lines.append("블로그 검색: " + " · ".join(f"'{k}' {n}건" for k, n in diag["per_kw"]))
        if done:
            lines.append(f"✅ 키워드 리서치 {len(done)}/{len(p['keywords'])}개 완료")
        else:
            lines.append("❌ 키워드 리서치 실패 → STEP 2 키워드 리서치 줄의 '🔍 키워드 리서치 실행'을 누르세요(설정 탭의 API 키 확인)")
        if not p["want_blog"]:
            lines.append("경쟁 블로그 건너뜀(" + ("selenium 없음" if not HAS_SELENIUM else "빠른판정: 불필요") + ")")
        elif files:
            lines.append(f"✅ 경쟁 블로그 {len(files)}개 스크랩")
        else:
            if diag.get("blog_skipped"):
                why = f"블로그 검색을 못 함({diag['blog_skipped'][:60]})"
            elif not diag.get("search_hits"):
                why = "리서치 키워드로 블로그 검색 결과가 0건"
            elif not diag.get("links"):
                why = f"검색 결과 {diag['search_hits']}건 중 쓸 수 있는 네이버 블로그 글이 없음(내 블로그·중복 제외)"
            else:
                why = f"{diag['links']}개 스크랩 실패(" + (p["errors"][0][:60] if p["errors"] else "원인 미상") + ")"
            lines.append(f"⚠ 경쟁 블로그 0개 — {why}. 넣고 싶으면 아래 '🔍 블로그탭 열기'로 글을 골라 주소 칸에 넣고 "
                         f"'🕸 주소 스크랩해서 채우기'. 넣지 않아도 됩니다")
            self._show_blog_panel(True)
        nxt = "→ 다음: STEP 2 '📋 판정결과·키워드 리서치 + 프롬프트 복사'" if done else "→ 리서치를 다시 실행한 뒤 STEP 2"
        if done and (p["qj"].get("attach") or "").strip().startswith("필요"):
            nxt += " — 공식자료를 대화창에 올려야 합니다(STEP 2 복사 때 폴더를 엽니다)"
        msg = "자동 수집: " + " · ".join(lines) + "\n" + nxt
        self.auto_prep_status_var.set(msg)
        self._log(f"✅ 자료 자동 준비 끝: {row['servNm']}" + (f" (오류 {len(p['errors'])}건: {p['errors'][0][:80]})" if p["errors"] else ""))

    def _autofill_research_request_keywords(self, content):
        """[Ver10.08] 가치판단(본 분석) 결과에 "재조사 요청 키워드:"가 있으면 저장할 때 검색 키워드 칸에 채운다
        (예전 "📋 가치판단 재조사 요청 키워드 자동 채우기" 버튼 대신)."""
        keywords = extract_research_request_keywords(content)
        if not keywords:
            return
        self.ai_kw_var.set(keywords)
        self.ai_kw_status_var.set(f"📋 재조사 요청 키워드 채움: {keywords} — '🔍 키워드 리서치 실행' 후 "
                                     f"'📋 AI에게 결과 전달'로 돌려주세요")
        self._log(f"📋 가치판단 재조사 요청 키워드 자동 채우기: {keywords}")

    # ── [Ver10.08] 경쟁 블로그 칸(STEP 1, 서비스별 저장) ──
    def _competitor_blog_path(self, row):
        return os.path.join(row.get("folder", ""), "competitor_blogs.md")

    def _save_competitor_blogs(self):
        """칸 내용을 지금 서비스 폴더에 저장한다(비우면 파일을 지운다)."""
        row = getattr(self, "_competitor_blog_serv", None)
        if not row or not row.get("folder") or not hasattr(self, "competitor_blog_text"):
            return
        text = self.competitor_blog_text.get("1.0", "end").strip()
        path = self._competitor_blog_path(row)
        try:
            if text:
                os.makedirs(row["folder"], exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text + "\n")
            elif os.path.exists(path):
                os.remove(path)
        except OSError as e:
            self._log(f"⚠ 경쟁 블로그 저장 실패: {e}")
        self._update_competitor_blog_info()

    # ── [Ver10.10] 실패했을 때만 보이는 줄 / 경쟁 블로그 "보기" ──
    def _show_blog_panel(self, show: bool):
        """경쟁 블로그 직접 고르기 줄 + 본문 칸을 펼치거나 접는다."""
        if not hasattr(self, "blog_panel_f"):
            return
        self._blog_panel_open = bool(show)
        if show:
            self.blog_panel_f.grid()
        else:
            self.blog_panel_f.grid_remove()
        self.blog_view_btn.config(text="닫기" if show else "보기")

    def _load_competitor_blogs_for_row(self, row):
        """서비스를 바꾸면 이전 서비스 칸을 저장하고 새 서비스 것을 채운다."""
        if not hasattr(self, "competitor_blog_text"):
            return
        self._save_competitor_blogs()
        self._competitor_blog_serv = row
        text = ""
        path = self._competitor_blog_path(row)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
            except OSError:
                text = ""
        self.competitor_blog_text.delete("1.0", "end")
        if text:
            self.competitor_blog_text.insert("1.0", text)
        self._update_competitor_blog_info()

    def _update_competitor_blog_info(self):
        if not hasattr(self, "competitor_blog_info_var"):
            return
        text = self.competitor_blog_text.get("1.0", "end").strip()
        n = count_competitor_blogs(text)
        self.competitor_blog_info_var.set(f"{n}개 · {len(text):,}자 (본 분석 복사에 들어감)" if n else "비어 있음")

    def _open_blog_tab_with_main_keyword(self):
        """[Ver10.08] 검색 키워드 칸의 첫 키워드(메인)로 네이버 블로그탭을 비로그인 새 창으로 연다 —
        상위 블로그 글 주소를 골라 STEP 1 주소 칸에 넣는 용도."""
        kw = (split_keyword_line(self.research_keyword_var.get()) or [""])[0]
        if not kw:
            messagebox.showwarning("알림", "검색 키워드 칸이 비어 있습니다. 먼저 항목을 선택하거나 키워드를 입력하세요.")
            return
        if self._check_ip_before_naver_open():
            return  # IP 불일치 등으로 차단 — 게이트 함수 안에서 이미 안내함
        ok = open_naver_search_in_chrome(kw, blog_only=True)
        if ok:
            self._log(f"🔍 블로그탭 열기(비로그인 새 창): {kw}")
        else:
            self._log(f"⚠️ 크롬을 찾지 못해 기본 브라우저로 열었습니다(비로그인 보장 안 됨): {kw}")

    def _clear_competitor_blogs(self):
        if not hasattr(self, "competitor_blog_text"):
            return
        self.competitor_blog_text.delete("1.0", "end")
        self._save_competitor_blogs()

    def _scrape_competitor_urls(self):
        """[Ver10.08] STEP 1 주소 칸(한 줄에 하나)에 넣은 블로그 글을 스크랩해 경쟁 블로그 칸을 채운다.
        자동으로 고른 글이 마음에 안 들 때 쓴다(예전 5)블로그 스크랩 탭 대신). 서비스 폴더
        competitor_blogs_md/에 저장하고, 칸 내용은 이번에 스크랩한 글로 바꾼다."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        if not HAS_SELENIUM:
            messagebox.showerror("오류", "selenium 패키지가 설치되어 있지 않습니다.\n"
                                          "터미널에서 'pip install selenium'을 실행한 뒤 다시 시도하세요.")
            return
        if getattr(self, "_auto_prep_running", False):
            messagebox.showinfo("실행 중", "자료 준비·스크랩이 이미 진행 중입니다.")
            return
        urls = []
        for ln in self.competitor_url_text.get("1.0", "end").splitlines():
            u = ln.strip()
            if re.match(r"https?://", u) and u not in urls:
                urls.append(u)
        if not urls:
            messagebox.showwarning("알림", "스크랩할 블로그 글 주소를 한 줄에 하나씩 넣으세요.")
            return
        if getattr(self, "_competitor_blog_serv", None) is None or \
                self._competitor_blog_serv.get("servId") != row["servId"]:
            self._load_competitor_blogs_for_row(row)
        self._auto_prep_running = True
        self.competitor_blog_info_var.set(f"⏳ {len(urls)}개 스크랩 중...")
        out_dir = os.path.join(row["folder"], "competitor_blogs_md")

        def task():
            files, errors = [], []
            driver = None
            try:
                driver = blog_scrap_build_driver()
                for url in urls:
                    try:
                        post = blog_scrap_scrape_post(driver, url)
                        files.append(blog_scrap_save_as_md(post, out_dir))
                        self._log(f"  📰 경쟁 블로그 스크랩: {post.get('title', '')[:40]}")
                    except Exception as e:
                        errors.append(f"{url} — {e}")
                    time.sleep(1)
            except Exception as e:
                errors.append(str(e))
            finally:
                if driver:
                    blog_scrap_cleanup_driver(driver)
            self.log_queue.put(("AUTO_PREP_DONE", {"row": row, "keywords": [], "files": files, "errors": errors,
                                                   "want_blog": True, "qj": {}, "manual": True}))

        threading.Thread(target=task, daemon=True).start()

    def _copy_main_analysis_prompt(self, same_chat: bool = True):
        """통합 프롬프트(V11) + 빠른 판정 결과 + 리서치 + 첨부 안내 + 경쟁 블로그를 복사한다.
        same_chat=True(기본)는 빠른 판정을 한 대화창에 이어 붙이는 복사라 원문을 뺀다.
        결과 저장은 "💾 가치판단 결과 저장"."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        if not self._check_research_api_keys():
            return
        detail = self._load_selected_detail(row)
        if detail is None:
            return
        quick = get_stage_output(row["servId"], "quick_judgment")
        if same_chat and not quick:
            if not messagebox.askyesno(
                    "빠른 판정 결과 없음",
                    "저장된 빠른 판정 결과가 없습니다 — 이어 붙일 대화창이 없을 수 있습니다.\n\n"
                    "서비스 원문까지 넣어 새 대화창용으로 복사할까요?"):
                return
            same_chat = False

        # [v6.9] 콤마(,)로 구분해 여러 키워드를 리서치했다면, 캐시에 실제로 있는 항목만 모은다.
        keywords = self._all_research_keywords(row)   # [Ver10.08] 자동준비 + AI 요청 키워드
        _research_cache_now = load_research_cache()
        research_map = {kw: _research_cache_now[kw] for kw in keywords if kw in _research_cache_now}
        if not research_map:
            if not messagebox.askyesno(
                "리서치 없음",
                f"'{', '.join(keywords)}'로 아직 키워드 리서치를 실행하지 않았습니다.\n"
                f"리서치 데이터 없이 복사할까요? (AI가 먼저 키워드 실측을 요청합니다)\n"
                f"(STEP 1 '💾 판정결과 저장(메모리값 자동저장)'을 먼저 하시는 걸 권장합니다)"
            ):
                return

        self._save_competitor_blogs()
        blogs = ""
        if getattr(self, "_competitor_blog_serv", None) and \
                self._competitor_blog_serv.get("servId") == row["servId"]:
            blogs = self.competitor_blog_text.get("1.0", "end").strip()
        attachments = list_attachment_files(row["folder"])
        try:
            package = build_prescreening_value_combo_package(
                detail, row["source"], row["servId"], research_map, attachments,
                quick_judgment=quick, competitor_blogs=blogs, include_origin=not same_chat)
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(package)
        n_blog = count_competitor_blogs(blogs)
        how = "이어서(원문 생략)" if same_chat else "새 대화창용 전체"
        self._log(f"📋 본 분석 프롬프트 복사 완료({how}): {row['servNm']} "
                  f"(공식자료 {len(attachments)}건, 경쟁 블로그 {n_blog}개)")

        qj = parse_quick_judgment(quick) if quick else {}
        notes = []
        if qj.get("attach"):
            notes.append(f"빠른판정 — 공식자료 올리기: {qj['attach']}")
        if n_blog:
            notes.append(f"경쟁 블로그 {n_blog}개는 복사본에 본문으로 들어갔습니다 — 따로 올리지 않아도 됩니다.")
        else:
            notes.append("경쟁 블로그는 이번 복사본에 없습니다"
                         + (f"(빠른 판정 — 경쟁 블로그: {qj['blog']})" if qj.get("blog") else "")
                         + ". 넣으려면 STEP 1 주소 칸에서 스크랩한 뒤 다시 복사하세요(없어도 됩니다).")
        notes.append("빠른 판단을 한 같은 대화창에 붙여넣으세요." if same_chat else "Claude 새 대화창에 붙여넣으세요(원문 포함).")
        self._show_attachment_reminder_popup(row, attachments, note_extra="\n".join(notes))

        if advance_posting_status(row["servId"], "🔎 가치판단대기", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_prescreening_value_combo_prompt_only(self):
        """⓪+①(Claude 올인원) 프롬프트 "문구만" 클립보드에 복사한다
        (원문·첨부·리서치 없이). _copy_value_judgment_prompt_only와
        동일한 이유로, 그리드에서 항목이 선택돼 있으면 포스팅 상태도
        함께 진행시킨다."""
        try:
            prompt = get_prompt_prescreening_value_combo_instructions()
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        row = self._get_selected_posting_row()
        if row is None:
            self._log("📋 본 분석(통합) 프롬프트(문구만) 복사 완료")
            return
        self._log(f"📋 본 분석(통합) 프롬프트(문구만) 복사 완료: {row['servNm']}")
        if advance_posting_status(row["servId"], "🔎 가치판단대기", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _show_attachment_reminder_popup(self, row: dict, attach_list: list, note_extra: str = ""):
        """사전스크리닝/가치판단처럼 첨부파일 누락이 특히 치명적인
        단계에서, 프롬프트 복사 직후 "실제로 대화창에 첨부했는지"를
        팝업으로 한 번 더 확인시킨다. 파일 목록을 눈으로 보여주고,
        원하면 그 자리에서 첨부파일 폴더까지 열어준다 — 사용자가 매번
        "📎 첨부파일 폴더 열기" 버튼을 따로 찾아 누르지 않아도 되게
        하기 위함(누락 실수 방지가 목적이므로, 확인 동선을 최대한
        짧게 만든다)."""
        lines = [f"'{row.get('servNm', '')}' 프롬프트를 클립보드에 복사했습니다."]
        lines.append("")
        if attach_list:
            lines.append(f"공식자료 {len(attach_list)}건이 있습니다 — 붙여넣기 전에 필요한 파일을 "
                          f"대화창에 올렸는지 확인하세요:")
            for fn in attach_list:
                lines.append(f"  · {fn}")
        else:
            lines.append("이 서비스는 받아 둔 공식자료가 없습니다.")
        if note_extra:
            lines.append("")
            lines.append(note_extra)
        lines.append("")
        lines.append("지금 공식자료 폴더를 열까요? (파일을 대화창에 끌어다 올린 뒤 프롬프트를 붙여넣으세요)")
        if messagebox.askyesno("공식자료 확인", "\n".join(lines)):
            attach_dir = os.path.join(row.get("folder", ""), "attachments")
            self._open_folder(attach_dir)

    def _copy_draft_prompt(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        detail_path = os.path.join(row["folder"], "detail.json")
        if not os.path.exists(detail_path):
            messagebox.showerror("오류", "detail.json을 찾을 수 없습니다. 상세조회를 먼저 실행하세요.")
            return
        with open(detail_path, "r", encoding="utf-8") as f:
            detail = json.load(f)

        # [v6.9] 콤마(,)로 구분해 여러 키워드를 리서치했다면, 캐시에 실제로
        # 있는 항목만 모아 research_map을 구성한다(research_map은 원래도
        # 여러 항목을 받는 범용 구조 — build_*_package가 그대로 처리한다).
        keywords = self._all_research_keywords(row)   # [Ver10.08] 자동준비 + AI 요청 키워드
        # [v6.9.1] get_cached_research()는 호출마다 캐시 파일 전체를
        # 디스크에서 읽으므로, 키워드마다 두 번씩 부르지 않고 한 번만
        # 읽어 재사용한다(콤마 다중 키워드일수록 절약 효과가 커짐).
        _research_cache_now = load_research_cache()
        research_map = {kw: _research_cache_now[kw] for kw in keywords if kw in _research_cache_now}
        keyword = keywords[0]

        attachments = list_attachment_files(row["folder"])
        if not attachments:
            if not messagebox.askyesno(
                "첨부파일 없음",
                f"'{row['servNm']}'에는 첨부 서식자료가 없습니다.\n"
                f"원문만으로는 초안이 빈약할 수 있습니다 — 프롬프트에 웹검색 보강 지침이 "
                f"포함되니 진행하면 Claude가 필요시 검색으로 채워줍니다.\n\n계속할까요?"
            ):
                return

        try:
            package = build_draft_prompt_package(detail, row["source"], research_map, attachments,
                                                  serv_id=row["servId"])
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(package)
        has_vj = bool(get_stage_output(row["servId"], "value_judgment"))
        vj_note = "" if has_vj else " (⚠ 저장된 가치판단 결과 없음 — 원문만으로 진행)"
        self._log(f"✍️ 초안 작성 프롬프트 복사 완료: {row['servNm']} (공식자료 {len(attachments)}건){vj_note}")

        if advance_posting_status(row["servId"], "📝 초안작성중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_draft_prompt_only(self):
        """③ 초안 작성 프롬프트 문구만 복사한다. 항목이 선택돼 있으면
        "+자료 복사"와 동일하게 상태도 함께 진행시킨다."""
        try:
            prompt = get_prompt_draft_instructions()
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        row = self._get_selected_posting_row()
        # [Ver10.10] 이어 쓸 가치판단 결과가 없으면 원문·공식자료까지 넣은 새 대화창용으로 복사한다
        if row is not None and not get_stage_output(row["servId"], "value_judgment"):
            self._copy_draft_prompt()
            return
        # [Ver10.08] 같은 대화창용이라도 확정 제목은 이 프로그램에만 있으므로 함께 넣는다(나머지 자료는 앞 대화에 있음)
        if row is not None and get_confirmed_title(row["servId"]):
            block = f"\n\n## 확정된 제목 (그대로 사용 — 다시 짓지 않음)\n\n{get_confirmed_title(row['servId'])}\n"
            intro = get_confirmed_title_intro(row["servId"])
            if intro:
                block += f"\n도입부 첫 문장 지시: {intro}\n"
            prompt += block + "\n(서비스 원문·공식자료·본 분석 결과는 이 대화의 앞부분 것을 그대로 씁니다.)"
        self.clipboard_clear()
        self.clipboard_append(prompt)
        if row is None:
            self._log("📋 초안 작성 프롬프트(문구만) 복사 완료")
            return
        self._log(f"📋 초안 작성 프롬프트(문구만) 복사 완료: {row['servNm']}")
        if advance_posting_status(row["servId"], "📝 초안작성중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_final_adaptation_prompt(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        detail_path = os.path.join(row["folder"], "detail.json")
        if not os.path.exists(detail_path):
            messagebox.showerror("오류", "detail.json을 찾을 수 없습니다. 상세조회를 먼저 실행하세요.")
            return
        with open(detail_path, "r", encoding="utf-8") as f:
            detail = json.load(f)

        if not get_stage_output(row["servId"], "draft"):
            if not messagebox.askyesno(
                "초안 결과 없음",
                f"'{row['servNm']}'에는 저장된 초안 결과가 없습니다.\n"
                f"1차 초안 없이 최종각색 프롬프트를 복사하면, 원문만 보고 처음부터 "
                f"다시 판단해야 해서 각색 품질이 떨어질 수 있습니다.\n\n"
                f"먼저 STEP 4 초안 복사 버튼으로 초안을 만들고, "
                f"'💾 초안 저장(메모리값 자동저장)'으로 저장하는 걸 권장합니다.\n\n"
                f"그래도 계속할까요?"
            ):
                return

        # [v6.9] 콤마(,)로 구분해 여러 키워드를 리서치했다면, 캐시에 실제로
        # 있는 항목만 모아 research_map을 구성한다(research_map은 원래도
        # 여러 항목을 받는 범용 구조 — build_*_package가 그대로 처리한다).
        keywords = self._all_research_keywords(row)   # [Ver10.08] 자동준비 + AI 요청 키워드
        # [v6.9.1] get_cached_research()는 호출마다 캐시 파일 전체를
        # 디스크에서 읽으므로, 키워드마다 두 번씩 부르지 않고 한 번만
        # 읽어 재사용한다(콤마 다중 키워드일수록 절약 효과가 커짐).
        _research_cache_now = load_research_cache()
        research_map = {kw: _research_cache_now[kw] for kw in keywords if kw in _research_cache_now}
        keyword = keywords[0]

        try:
            package = build_final_adaptation_prompt_package(detail, row["source"], row["servId"], research_map)
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(package)
        self._log(f"✒️ 최종각색 프롬프트 복사 완료: {row['servNm']}")

        if advance_posting_status(row["servId"], "✒️ 최종각색중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_final_adaptation_prompt_only(self):
        """⑤ 최종각색 프롬프트 문구만 복사한다. 항목이 선택돼 있으면
        "+자료 복사"와 동일하게 상태도 함께 진행시킨다."""
        try:
            prompt = get_prompt_final_adaptation_instructions()
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        row = self._get_selected_posting_row()
        if row is None:
            self._log("📋 최종각색 프롬프트(문구만) 복사 완료")
            return
        self._log(f"📋 최종각색 프롬프트(문구만) 복사 완료: {row['servNm']}")
        if advance_posting_status(row["servId"], "✒️ 최종각색중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_claude_second_stage_prompt(self):
        """🩹 2차 각색(Claude) 프롬프트+자료를 복사한다. 🧩 통합 프롬프트의
        [2단계: 검증·각색] 부분만 분리한 버전 — 입력값 구성은 ⑤ GPT
        최종각색과 완전히 동일(원문+1차 초안 결과+리서치), 프롬프트
        지시문만 Claude용으로 다르다."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        detail_path = os.path.join(row["folder"], "detail.json")
        if not os.path.exists(detail_path):
            messagebox.showerror("오류", "detail.json을 찾을 수 없습니다. 상세조회를 먼저 실행하세요.")
            return
        with open(detail_path, "r", encoding="utf-8") as f:
            detail = json.load(f)

        if not get_stage_output(row["servId"], "draft"):
            if not messagebox.askyesno(
                "초안 결과 없음",
                f"'{row['servNm']}'에는 저장된 초안 결과가 없습니다.\n"
                f"이 프롬프트는 1차 초안을 검증·각색만 하는 단계라, 초안 없이 "
                f"복사하면 각색할 대상 자체가 없습니다.\n\n"
                f"먼저 STEP 4에서 초안을 만들고, "
                f"'💾 초안 저장(메모리값 자동저장)'으로 저장하는 걸 권장합니다.\n\n"
                f"그래도 계속할까요?"
            ):
                return

        # [v6.9] 콤마(,)로 구분해 여러 키워드를 리서치했다면, 캐시에 실제로
        # 있는 항목만 모아 research_map을 구성한다(research_map은 원래도
        # 여러 항목을 받는 범용 구조 — build_*_package가 그대로 처리한다).
        keywords = self._all_research_keywords(row)   # [Ver10.08] 자동준비 + AI 요청 키워드
        # [v6.9.1] get_cached_research()는 호출마다 캐시 파일 전체를
        # 디스크에서 읽으므로, 키워드마다 두 번씩 부르지 않고 한 번만
        # 읽어 재사용한다(콤마 다중 키워드일수록 절약 효과가 커짐).
        _research_cache_now = load_research_cache()
        research_map = {kw: _research_cache_now[kw] for kw in keywords if kw in _research_cache_now}
        keyword = keywords[0]

        try:
            package = build_claude_second_stage_prompt_package(detail, row["source"], row["servId"], research_map)
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(package)
        self._log(f"🩹 2차 각색(Claude) 프롬프트 복사 완료: {row['servNm']}")

        if advance_posting_status(row["servId"], "✒️ 최종각색중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_claude_second_stage_prompt_only(self):
        """🩹 2차 각색(Claude) 프롬프트 문구만 복사한다. 항목이 선택돼
        있으면 "+자료 복사"와 동일하게 상태도 함께 진행시킨다."""
        try:
            prompt = get_prompt_claude_second_stage_instructions()
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        row = self._get_selected_posting_row()
        if row is None:
            self._log("📋 2차 각색(Claude) 프롬프트(문구만) 복사 완료")
            return
        self._log(f"📋 2차 각색(Claude) 프롬프트(문구만) 복사 완료: {row['servNm']}")
        if advance_posting_status(row["servId"], "✒️ 최종각색중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _paste_and_save_stage_result(self, stage_key: str, prefill: str = ""):
        """이전 단계(가치판단/초안/최종각색) 실행 결과를 사람이 다른
        대화창/다른 AI에서 복사해와 여기 붙여넣으면, 다음 단계 프롬프트를
        만들 때 자동으로 포함되도록 저장한다."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        label = STAGE_RESULT_LABELS.get(stage_key, stage_key)

        dialog = tk.Toplevel(self)
        dialog.title(f"{label} 붙여넣기 저장 — {row['servNm']}")
        dialog.geometry("700x500")
        dialog.transient(self)

        ttk.Label(dialog, text=f"'{row['servNm']}'의 {label}을(를) 아래에 붙여넣고 저장하세요.",
                  padding=8).pack(anchor="w")

        text_widget = scrolledtext.ScrolledText(dialog, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        existing = prefill or get_stage_output(row["servId"], stage_key)   # [Ver10.08] 클립보드 내용 우선
        if existing:
            text_widget.insert("1.0", existing)

        btn_f = ttk.Frame(dialog)
        btn_f.pack(fill="x", padx=8, pady=(0, 8))

        # [Ver10.06 신규] ⑥ 최종각색 저장 전 모바일 문단 정리(GPT) — 기본 꺼짐. 켜 두면 저장을 누를 때
        # 먼저 기준 글자 수를 넘는 문단만 나눠 이 창의 본문칸에 반영한다(para_reflow_with_gpt 참고).
        para = {"on": None, "limit": None, "info": None, "done": None, "pending": False, "token": 0}
        if stage_key == "final_adaptation":
            _pcfg = load_config()
            para["on"] = tk.BooleanVar(value=bool(_pcfg.get("para_reflow_on", False)))
            try:
                _plimit = int(_pcfg.get("para_reflow_limit", PARA_REFLOW_DEFAULT_LIMIT))
            except (TypeError, ValueError):
                _plimit = PARA_REFLOW_DEFAULT_LIMIT
            para["limit"] = tk.IntVar(value=_plimit)
            para["info"] = tk.StringVar(value="")

            def _para_toggle():
                c = load_config()
                c["para_reflow_on"] = bool(para["on"].get())
                save_config(c)
                if not para["on"].get():
                    para["token"] += 1
                    para["pending"] = False
                    para["info"].set("")

            def _para_limit_saved(*_):
                try:
                    v = int(para["limit"].get())
                except (tk.TclError, ValueError):
                    return
                c = load_config()
                c["para_reflow_limit"] = v
                save_config(c)

            ttk.Checkbutton(btn_f, text="📱 문단 정리(GPT)", variable=para["on"],
                            command=_para_toggle).pack(side="left")
            ttk.Spinbox(btn_f, from_=80, to=400, increment=10, width=4,
                        textvariable=para["limit"]).pack(side="left", padx=(2, 0))
            ttk.Label(btn_f, text="자 넘으면").pack(side="left", padx=(2, 8))
            para["limit"].trace_add("write", _para_limit_saved)
            ttk.Label(dialog, textvariable=para["info"], foreground="#1D5C5A",
                      padding=(8, 0)).pack(anchor="w", before=btn_f)

        def _para_gate(content: str) -> bool:
            """저장해도 되면 True. 문단 정리를 시작했으면 False(끝나면 반영·재저장)."""
            if stage_key != "final_adaptation" or not para["on"].get():
                return True
            if para["pending"]:
                messagebox.showinfo("문단 정리 중", "문단 정리가 끝나면 본문칸에 반영됩니다. 잠시 뒤 다시 저장하세요.",
                                    parent=dialog)
                return False
            if para["done"] is not None and para["done"] == content:
                return True
            key = (load_config().get("openai_api_key") or "").strip()
            if not key:
                para["info"].set("📱 문단 정리: OpenAI API 키가 없어 건너뜀(설정 탭에서 입력) — 원본 그대로 저장")
                return True
            try:
                limit = min(400, max(80, int(para["limit"].get())))
            except (tk.TclError, ValueError):
                limit = PARA_REFLOW_DEFAULT_LIMIT
            para["token"] += 1
            token = para["token"]
            para["pending"] = True
            para["info"].set(f"⏳ 문단 정리 중({limit}자 넘는 문단)... 끝나면 본문칸에 반영")

            def _apply(res):
                if token != para["token"] or not dialog.winfo_exists():
                    return
                para["pending"] = False
                new_text, msg = res
                if text_widget.get("1.0", "end").strip() != content:
                    para["info"].set("📱 문단 정리: 그 사이 본문이 바뀌어 결과를 버림 — 다시 저장을 누르세요")
                    return
                if new_text is None:
                    para["done"] = content
                    para["info"].set(f"📱 문단 정리: {msg}")
                    _do_save()
                    return
                text_widget.delete("1.0", "end")
                text_widget.insert("1.0", new_text)
                para["done"] = new_text.strip()
                para["info"].set(f"📱 {msg} — 본문칸을 확인한 뒤 다시 \"💾 저장\"을 누르세요")

            def _worker():
                try:
                    import openai
                    client = openai.OpenAI(api_key=key)
                    res = para_reflow_with_gpt(client, content, limit)
                except Exception as e:
                    res = (None, f"GPT 오류로 원본 유지({str(e)[:60]})")
                dialog.after(0, lambda: _apply(res))

            threading.Thread(target=_worker, daemon=True).start()
            return False

        def _do_save():
            content = text_widget.get("1.0", "end").strip()
            if not content:
                messagebox.showwarning("알림", "저장할 내용이 없습니다.", parent=dialog)
                return
            if not _para_gate(content):   # [Ver10.06] 저장 전 문단 정리
                return

            if stage_key == "final_adaptation":
                # [Ver10.13] 주소의 https://·www. 를 떼어 본문칸에도 반영한다(네이버 자동 링크 방지).
                content, _url_n = strip_url_prefixes(content)
                if _url_n:
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", content)
                    self._log(f"🔗 주소 {_url_n}곳에서 https://·www. 를 뗐습니다(네이버 자동 링크 방지)")
                    messagebox.showinfo("주소 정리", f"주소 {_url_n}곳에서 https://·www. 를 뗐습니다.\n"
                                        "네이버가 링크·미리보기 카드로 바꿔 줄이 깨지는 것을 막기 위해서입니다.",
                                        parent=dialog)
                # 정규화(불릿 변환)까지 반영된 뒤의 제목으로 충돌을 확인해야
                # 하므로, 저장 직전에 normalize된 텍스트 기준으로 먼저 검사한다.
                normalized_preview = normalize_markdown_bullets(content.strip())
                title, filename, conflict_serv_id = check_final_post_title_conflict(
                    row["servId"], normalized_preview, row["servNm"]
                )

                # [v7.2 신규] 제목 길이(60자 절대 상한)·핵심 숫자 개수(1개
                # 제한)·호객형 수식어·물음표 종결 점검. 정책뉴스 서브프로그램의
                # validate_title() 저장 직전 확인 패턴을 그대로 이식.
                tv = validate_title(title)
                if tv["warnings"]:
                    msg = "제목에 다음 사항이 확인됩니다:\n\n" + "\n".join(
                        f"• {w}" for w in tv["warnings"])
                    if not messagebox.askyesno(
                            "제목 점검 결과", msg + "\n\n그래도 저장을 진행하시겠습니까?",
                            parent=dialog):
                        return

                # [Ver10.08] 출처 줄 점검 — 공식기관 출처가 반드시 있어야 하고 블로그는 출처가 아니다.
                src_warn = check_source_line(normalized_preview)
                if src_warn:
                    if not messagebox.askyesno(
                            "출처 점검 결과", "\n".join(f"• {w}" for w in src_warn)
                            + "\n\n그래도 저장을 진행하시겠습니까?", parent=dialog):
                        return

                if conflict_serv_id:
                    conflict_row = next(
                        (r for r in build_listing_rows() if r["servId"] == conflict_serv_id), None
                    )
                    conflict_desc = conflict_row["servNm"] if conflict_row else conflict_serv_id
                    if not messagebox.askyesno(
                        "⚠️ 제목 중복",
                        f"제목 '{title}'은(는) 이미 다른 서비스('{conflict_desc}')가 저장한 "
                        f"최종원고 파일명과 같습니다.\n\n"
                        f"그대로 저장하면 그 서비스의 최종원고 파일이 이 내용으로 "
                        f"덮어써집니다. 계속하시겠습니까?\n\n"
                        f"(계속하지 않으려면 취소 후 제목을 다르게 고쳐서 다시 붙여넣으세요.)",
                        parent=dialog,
                    ):
                        return

            set_stage_output(row["servId"], stage_key, content)  # normalize_markdown_bullets는 이 안에서 자동 적용됨
            if stage_key == "final_adaptation":
                # 최종각색 결과는 stage_outputs.json(프롬프트 이어붙이기용)과는
                # 별개로, 제목을 파일명으로 한 .md 파일로도 저장한다 —
                # 실제 발행/보관용 산출물이 필요하기 때문.
                saved_text = get_stage_output(row["servId"], "final_adaptation")
                md_path = save_final_adaptation_markdown(row["servId"], row["servNm"], saved_text)
                self._log(f"📥 {label} 저장 완료: {row['servNm']} ({len(content)}자) → {md_path}")
            else:
                self._log(f"📥 {label} 저장 완료: {row['servNm']} ({len(content)}자)")
            dialog.destroy()
            # [Ver10.08] 빠른 판정: 보류면 상태 변경 확인, 진행이면 리서치 키워드 채움.
            # 본 분석: "재조사 요청 키워드:"가 있으면 검색 키워드 칸에 채움.
            if stage_key == "quick_judgment":
                self._after_quick_judgment_saved(row, content)
            elif stage_key == "value_judgment":
                self._autofill_research_request_keywords(content)

        ttk.Button(btn_f, text="💾 저장", command=_do_save).pack(side="right")
        ttk.Button(btn_f, text="취소", command=dialog.destroy).pack(side="right", padx=(0, 8))
        # 붙여넣기 편의를 위해 텍스트 영역에 바로 포커스
        text_widget.focus_set()

    # ---------------- 인포그래픽 작성 탭 ----------------
    def _refresh_ig_service_list(self):
        """최종각색 결과가 저장되어 있는 서비스 중, 아직 인포그래픽
        작업이 남아있는 것만 콤보박스에 채운다. 포스팅대기·포스팅완료·
        포스팅후삭제·패스·보류 상태는 이미 작업이 끝났거나 더 이상
        진행할 필요가 없는 상태이므로 제외한다(계속 섞여 나오면 매번
        지나간 항목을 걸러가며 찾아야 해서 불편함).

        v5.7: 기존에는 build_listing_rows()(중앙부처+지자체 전체 수천
        건을 순회하며 detail.json 존재 확인·중복정책 대조·우선순위
        점수까지 계산)를 그대로 갖다 썼는데, 이 탭은 servId/servNm/
        source 3개 필드만 쓰므로 완전히 과한 연산이었음 — 탭 전환이
        느리다는 사용자 리포트로 발견. get_infographic_candidate_rows()
        (stage_outputs.json + posting_status.json 2개 파일만 읽음)로
        교체해 최종각색 결과가 저장된 건(보통 수십~수백 건)만 바로
        추림."""
        done_or_skipped = {"🟢 포스팅대기", PROTECTED_STATUS, DELETED_STATUS, "⏭ 패스", "⏸ 보류"}
        items = [
            r for r in get_infographic_candidate_rows()
            if r["posting_status"] not in done_or_skipped
        ]
        items.sort(key=lambda r: r["servNm"])
        self._ig_service_rows = {f"[{r['source']}] {r['servNm']} ({r['servId']})": r for r in items}
        self.ig_service_combo["values"] = list(self._ig_service_rows.keys())
        if not items:
            self.ig_service_var.set("")
            for w in self.ig_title_list_frame.winfo_children():
                w.destroy()
            self.ig_progress_var.set("이미지 매칭: 0/0 완료 (대상 없음 — 먼저 최종각색 결과를 저장하세요)")
            return
        if self.ig_service_var.get() not in self._ig_service_rows:
            self.ig_service_var.set(list(self._ig_service_rows.keys())[0])
        self._generate_infographic_title_list()

    # ── [Ver10.07 신규] 5)인포그래픽 작성: 코드 카드(선택) ──
    def _build_card_panel(self, parent, row):
        """기존 STEP은 그대로 두고, 체크를 켤 때만 보이는 코드 카드 칸. 위에서 아래로 ①→④ 순서."""
        wrap = ttk.Frame(parent)
        wrap.grid(row=row, column=0, sticky="ew", pady=(6, 0))
        wrap.columnconfigure(0, weight=1)
        self.card_panel_on = tk.BooleanVar(value=bool(load_config().get("card_panel_on", False)))
        ttk.Checkbutton(wrap, text="🧩 코드 카드 (선택) — 썸네일 배경 그림만 AI로, 글자·소제목 인포그래픽은 코드로 만들기",
                        variable=self.card_panel_on, command=self._toggle_card_panel).grid(row=0, column=0, sticky="w")
        body = ttk.LabelFrame(wrap, text="코드 카드 — ①부터 ④까지 순서대로", padding=6)
        self._card_body = body
        body.columnconfigure(0, weight=1)

        # ① 프롬프트 복사 → Claude
        r1 = ttk.Frame(body)
        r1.grid(row=0, column=0, sticky="ew")
        ttk.Button(r1, text="① 📋 카드 자료+프롬프트(새창)",
                   command=lambda: self._copy_card_prompt(False)).pack(side="left", padx=(0, 6))
        ttk.Button(r1, text="① 📋 카드 프롬프트(현재창 — 최종각색을 쓴 대화창)",
                   command=lambda: self._copy_card_prompt(True)).pack(side="left", padx=(0, 6))
        ttk.Label(r1, text="→ Claude에 붙여넣기. 답변의 장면 프롬프트 블럭은 퍼플렉시티로, 맨 끝 JSON 블럭은 ②로", foreground="gray").pack(side="left")
        self.card_copy_status = ttk.Label(r1, text="", foreground="darkgreen")
        self.card_copy_status.pack(side="left", padx=(8, 0))

        # ② Claude 답변 전체 붙여넣기
        r2 = ttk.Frame(body)
        r2.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(r2, text="② Claude 답변의 JSON 블럭을 아래 칸에 붙여넣으세요 (답변 전체를 넣어도 됩니다)").pack(side="left")
        ttk.Button(r2, text="지우기", command=self._card_clear_answer).pack(side="right")
        ttk.Button(r2, text="② 클립보드 내용 붙여넣기", command=self._card_paste_answer).pack(side="right", padx=(0, 6))
        self.card_answer_text = scrolledtext.ScrolledText(body, height=4, wrap="word", font=("맑은 고딕", 9))
        self.card_answer_text.grid(row=2, column=0, sticky="ew", pady=(2, 0))

        # ③ 퍼플렉시티/GPT 그림 선택
        r4 = ttk.Frame(body)
        r4.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(r4, text="③ 퍼플렉시티/GPT 그림 선택…", command=self._card_pick_background).pack(side="left", padx=(0, 6))
        ttk.Button(r4, text="📁 카드 작업폴더 열기", command=self._card_open_work).pack(side="left", padx=(0, 8))
        self.card_bg_var = tk.StringVar(value="퍼플렉시티 그림: 없음")
        ttk.Label(r4, textvariable=self.card_bg_var).pack(side="left")

        # ④ 카드 만들기
        r5 = ttk.Frame(body)
        r5.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.card_make_btn = ttk.Button(r5, text="④ 카드 만들기 → MD 폴더에 넣기",
                                        command=lambda: self._card_make(None))
        self.card_make_btn.pack(side="left", padx=(0, 6))
        ttk.Button(r5, text="썸네일만 다시 만들기", command=lambda: self._card_make(["00_thumbnail"])).pack(side="left")
        # 만든 카드를 바로 확인하도록 같은 줄에도 둔다(위 "대상 서비스" 줄의 버튼과 같은 동작 — 사용자 요청)
        ttk.Button(r5, text="📁 최종각색된 MD파일이 저장된 폴더 열기",
                   command=self._open_ig_service_folder).pack(side="left", padx=(6, 0))
        self.card_status_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.card_status_var, foreground="#1F3A5F",
                  wraplength=1000, justify="left").grid(row=6, column=0, sticky="w", pady=(6, 0))

        # 작은 안내: 글 폴더 · _카드작업 폴더
        r7 = ttk.Frame(body)
        r7.grid(row=7, column=0, sticky="ew", pady=(6, 0))
        self.card_folder_var = tk.StringVar(value="")
        ttk.Label(r7, textvariable=self.card_folder_var, foreground="gray").pack(side="left")
        ttk.Label(body, foreground="gray", justify="left", text=(
            "· 글 폴더 = 위에서 고른 서비스의 final_posts 폴더(MD와 완성 이미지가 들어가는 곳) — 맨 위 '📁 최종각색된 MD파일이 저장된 폴더 열기'로 확인.\n"
            "· ③은 고른 그림을 카드 작업폴더(글 폴더 안 _카드작업)에 복사합니다. 내려받은 그림을 그 폴더에 직접 넣어도 되고, "
            "④는 그 폴더의 가장 최근 그림을 씁니다.\n"
            "· ②를 비워 두면 카드 작업폴더에 넣어 둔 JSON·답변 파일(.json/.txt/.md)을 읽습니다.")).grid(row=8, column=0, sticky="w", pady=(2, 0))

        self._toggle_card_panel(save=False)

    def _card_clear_answer(self):
        self.card_answer_text.delete("1.0", "end")
        self.card_status_var.set("")

    def _card_show_folder(self):
        """작은 안내 줄의 글 폴더 표시를 지금 기준으로 갱신한다."""
        folder = self._card_md_folder(ask=False)
        self.card_folder_var.set(f"글 폴더: {folder}" if folder else "글 폴더: (아직 없음 — 위에서 서비스를 고르고, 4)포스팅 관리 STEP 6 최종각색 결과를 먼저 저장하세요)")

    def _toggle_card_panel(self, save=True):
        if self.card_panel_on.get():
            self._card_body.grid(row=1, column=0, sticky="ew", pady=(2, 0))
            self._card_show_folder()
        else:
            self._card_body.grid_remove()
        if save:
            cfg = load_config()
            cfg["card_panel_on"] = bool(self.card_panel_on.get())
            save_config(cfg)

    def _card_md_folder(self, ask=True) -> str:
        """카드를 넣을 글 폴더 = 위에서 고른 서비스의 final_posts/{제목}/ (키워드 등록이 읽는 곳 그대로)."""
        row = self._get_selected_ig_row()
        if row is not None:
            text = get_final_adaptation_text_for_use(row["servId"], row["servNm"])
            title = extract_title_from_final_text(text) or row["servNm"]
            folder = get_final_post_folder(title)
            if os.path.isdir(folder) and any(fn.endswith(".md") for fn in os.listdir(folder)):
                return folder
        if ask:
            messagebox.showwarning("글 폴더 없음", "위에서 대상 서비스를 고르세요.\n"
                                   "최종각색 MD가 아직 없으면 4)포스팅 관리 STEP 6 최종각색 결과를 먼저 저장하세요.")
        return ""

    def _card_work_dir(self, md_folder: str) -> str:
        return os.path.join(md_folder, CARD_WORK_SUBFOLDER)

    def _card_open_work(self):
        folder = self._card_md_folder()
        if not folder:
            return
        work = self._card_work_dir(folder)
        os.makedirs(work, exist_ok=True)
        self._open_folder(work)

    def _card_paste_answer(self):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            text = ""
        if not text.strip():
            messagebox.showinfo("알림", "클립보드가 비어 있습니다.")
            return
        self.card_answer_text.delete("1.0", "end")
        self.card_answer_text.insert("1.0", text)
        scene, spec, err = card_parse_answer(text)
        n = len(spec["images"]) if spec else 0
        if err:
            self.card_status_var.set(f"⚠ 붙여넣은 내용에서 설계도를 읽지 못했습니다: {err}")
        else:
            notes = spec.get("notes") if isinstance(spec.get("notes"), dict) else {}
            extra = "".join(f" / {lab}: {notes[k]}" for k, lab in (("omitted", "생략"), ("icons_needed", "아이콘 추가 필요"))
                            if notes.get(k))
            self.card_status_var.set(f"✅ ② 완료 — 이미지 {n}장 설계도{extra}. 다음: ③ 퍼플렉시티/GPT 그림 선택")

    def _card_pick_background(self):
        """③ 내려받은 퍼플렉시티/GPT 그림을 골라 카드 작업폴더(_카드작업)에 바로 복사한다."""
        folder = self._card_md_folder()
        if not folder:
            return
        # 퍼플렉시티 그림은 보통 다운로드 폴더에 저장되므로 거기서 연다.
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        path = filedialog.askopenfilename(title="③ 퍼플렉시티/GPT 그림 선택 (글자 없는 그림)",
                                          initialdir=downloads if os.path.isdir(downloads) else os.path.expanduser("~"),
                                          filetypes=[("이미지", "*.png *.jpg *.jpeg *.webp"), ("모든 파일", "*.*")])
        if not path:
            return
        work = self._card_work_dir(folder)
        os.makedirs(work, exist_ok=True)
        dst = os.path.join(work, os.path.basename(path))
        if os.path.abspath(path) != os.path.abspath(dst):
            shutil.copy(path, dst)   # copy2가 아니라 copy — 지금 시각으로 저장돼 "가장 최근 그림"이 된다
        else:
            os.utime(dst, None)
        self.card_bg_var.set(f"퍼플렉시티 그림: {os.path.basename(path)}")
        self.card_status_var.set("✅ ③ 완료 — 카드 작업폴더에 복사했습니다. 다음: ④ 카드 만들기")

    def _copy_card_prompt(self, simplified: bool):
        cfg = load_config()
        key = "prompt_infographic_card_file"
        fname = cfg.get(key) or _DEFAULT_CONFIG[key]
        prompt = load_prompt_file(fname, PROMPT_DIR)
        if not prompt:
            messagebox.showwarning("프롬프트 없음", "카드용 ⑦ 프롬프트 파일이 없습니다.\n설정 탭에서 확인하세요.\n"
                                   f"(찾는 위치: {os.path.join(PROMPT_DIR, fname)})")
            return
        last_shape = cfg.get("card_last_shape", "") or "없음"
        if simplified:
            body = ("## 최종각색 결과(2차 각색 완성본) 전체\n\n"
                    "바로 위 최종각색 결과를 그대로 사용해주세요(다시 붙여넣지 않습니다).\n\n"
                    "## 가치판단 단계의 핵심 키워드 1개\n\n(바로 위 대화의 가치판단 결과 참고)\n")
        else:
            row = self._get_selected_ig_row()
            if row is None:
                messagebox.showwarning("알림", "먼저 위에서 대상 서비스를 선택하세요.")
                return
            final_text = get_final_adaptation_text_for_use(row["servId"], row["servNm"])
            if not final_text:
                messagebox.showwarning("알림", f"'{row['servNm']}'에는 저장된 최종각색 결과가 없습니다.")
                return
            keyword = (extract_core_keyword_from_value_judgment(get_stage_output(row["servId"], "value_judgment"))
                       or row["servNm"])
            body = (f"## 최종각색 결과(2차 각색 완성본) 전체\n\n{final_text}\n\n"
                    f"## 가치판단 단계의 핵심 키워드 1개\n\n{keyword}\n")
        content = (f"{prompt}\n\n[아래는 실제 입력값입니다]\n\n{body}\n"
                   f"## 모드\n\n웹\n\n## 직전 글의 썸네일 shape\n\n{last_shape}\n")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.card_copy_status.config(text="✅ 복사 완료 — Claude에 Ctrl+V, 답변이 나오면 ②")
        self.after(5000, lambda: self.card_copy_status.config(text=""))
        self._log("📋 카드용 ⑦ 프롬프트 복사" + (" (프롬프트만)" if simplified else ""))

    def _card_make(self, only):
        folder = self._card_md_folder()
        if not folder:
            return
        self._card_show_folder()
        md_files = [fn for fn in os.listdir(folder) if fn.endswith(".md")]
        if not md_files:
            messagebox.showwarning("MD 없음", f"글 폴더에 .md 파일이 없습니다.\n{folder}")
            return
        md_name = os.path.basename(folder) + ".md"
        md_path = os.path.join(folder, md_name if md_name in md_files else md_files[0])
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        work = self._card_work_dir(folder)
        os.makedirs(work, exist_ok=True)

        answer = self.card_answer_text.get("1.0", "end").strip()
        source = "붙여넣은 답변"
        if answer:
            with open(os.path.join(work, CARD_ANSWER_FILENAME), "w", encoding="utf-8") as f:
                f.write(answer)
        else:
            # [2026-10-15] ② 칸이 비었을 때(프로그램을 다시 켠 뒤 등) 예전에는 _카드작업의 지난 답변 파일을
            # 말없이 읽어 새 답이 반영되지 않았다. 이제 ① 클립보드에 읽을 수 있는 설계도가 있으면 그걸 쓰고,
            # ② 없을 때만 지난 답변 파일을 쓸지 날짜를 보여 주고 묻는다.
            try:
                clip = self.clipboard_get()
            except tk.TclError:
                clip = ""
            if clip.strip() and not card_parse_answer(clip)[2]:
                answer, source = clip.strip(), "클립보드의 답변"
                self.card_answer_text.insert("1.0", answer)
                with open(os.path.join(work, CARD_ANSWER_FILENAME), "w", encoding="utf-8") as f:
                    f.write(answer)
            else:
                ans_path = card_find_answer_file(work)
                if not ans_path:
                    messagebox.showwarning("답변 없음", "② 칸에 Claude 답변의 JSON 블럭을 붙여넣어 주세요.\n"
                                           "(Claude 답을 복사한 뒤 '② 클립보드 내용 붙여넣기')")
                    return
                when = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(ans_path)))
                if not messagebox.askyesno("지난 답변을 쓸까요?",
                        f"② 칸이 비어 있습니다. 이 글의 지난 답변 파일이 있습니다:\n"
                        f"{os.path.basename(ans_path)} ({when} 저장)\n\n"
                        "이 지난 답변으로 카드를 만들까요?\n"
                        "새 답이면 '아니요'를 누르고, Claude 답을 복사해 '② 클립보드 내용 붙여넣기' 후 ④를 누르세요."):
                    return
                with open(ans_path, "r", encoding="utf-8") as f:
                    answer = f.read()
                source = f"지난 답변 파일 {os.path.basename(ans_path)} ({when})"
        scene, spec, err = card_parse_answer(answer)
        if err:
            # [2026-10-15] Claude에게 고친 답을 받아 복사만 하고 ④를 누르면 ② 칸의 옛 답을 계속 읽었다
            # (같은 오류 반복). 칸의 답이 틀렸고 클립보드에 읽을 수 있는 설계도가 있으면 그걸 쓴다.
            try:
                clip = self.clipboard_get()
            except tk.TclError:
                clip = ""
            c_scene, c_spec, c_err = card_parse_answer(clip) if clip.strip() else ("", None, "빈 클립보드")
            if not c_err:
                self.card_answer_text.delete("1.0", "end")
                self.card_answer_text.insert("1.0", clip)
                with open(os.path.join(work, CARD_ANSWER_FILENAME), "w", encoding="utf-8") as f:
                    f.write(clip.strip())
                scene, spec, err, source = c_scene or scene, c_spec, "", "클립보드의 고친 답변"
        if err:
            req = ("JSON 설계도를 코드블럭 하나로 다시 출력해줘" if "코드블럭이 없" in err
                   else f"JSON 문법만 고쳐서 코드블럭 하나로 다시 출력해줘 (오류: {err})")
            self.clipboard_clear()
            self.clipboard_append(req)
            messagebox.showwarning("설계도 오류", f"{source}: {err}\n\n다시 요청할 문구를 클립보드에 복사했습니다:\n{req}\n\n"
                                   "→ Claude 대화창에 붙여넣기 → 고친 답을 복사한 뒤 '④ 카드 만들기'를 다시 누르면 "
                                   "클립보드의 고친 답을 읽습니다.")
            return
        spec.setdefault("series", "welfare")

        bg = card_find_background(work, folder)
        has_thumb = any(i.get("layout") == "thumbnail" for i in spec["images"])
        if has_thumb and not bg and (not only or "00_thumbnail" in only):
            if not messagebox.askyesno("배경 그림 없음",
                    "썸네일에 쓸 퍼플렉시티 그림이 없습니다('③ 퍼플렉시티/GPT 그림 선택'으로 고르세요).\n"
                    "배경 없이 썸네일을 만들까요?"):
                return
        spec_path, bg_name = card_prepare_spec(spec, work, bg)
        matches = card_match_images(spec, md_text)
        if only:
            matches = [m for m in matches if m["file"] in only]
        chrome = card_chrome_path(load_config().get("card_chrome_path", ""))
        tool = self._card_tool_dir()
        self.card_make_btn.config(state="disabled")
        self.card_status_var.set(f"⏳ 카드 만드는 중… ({len(matches)}장, 설계도: {source})")

        def worker():
            res = card_render(tool, spec_path, chrome, only)
            self.after(0, lambda: self._card_after_render(res, work, folder, spec, matches))
        threading.Thread(target=worker, daemon=True).start()

    def _card_tool_dir(self) -> str:
        v = (load_config().get("card_tool_dir") or "Naver_blog_SVG Card_images").strip()
        path = v if os.path.isabs(v) else os.path.join(str(BASE_DIR), v)
        old_path = os.path.join(str(BASE_DIR), "blog-images")   # 받은 원래 폴더 이름 — 이름을 안 바꿨으면 그쪽을 쓴다
        if not os.path.isdir(path) and os.path.isdir(old_path):
            return old_path
        return path

    def _card_name(self, text: str) -> str:
        """기존 이미지 파일명 규칙(5)인포그래픽 작성의 [복사] 버튼 문구 + Windows 금지 문자 제거)."""
        return re.sub(r'[\\/:*?"<>|]', "", strip_trailing_punct_for_filename(text)).strip()

    def _card_after_render(self, res, work, folder, spec, matches):
        self.card_make_btn.config(state="normal")
        ok, log = res
        if not ok:
            self.card_status_var.set("❌ 카드 만들기 실패 — 오류 창 참고")
            messagebox.showerror("카드 만들기 실패", log[-1500:] or "알 수 없는 오류")
            return
        thumb = next((i for i in spec["images"] if i.get("layout") == "thumbnail"), None)
        if thumb and thumb.get("shape"):
            cfg = load_config()
            cfg["card_last_shape"] = thumb["shape"]
            save_config(cfg)
        n_old = card_count_existing(matches, folder, self._card_name)
        lines = []
        for m in matches:
            if m["target"]:
                nm = self._card_name(m["target"]) + (f"_{m['part']}" if m["part"] else "") + ".png"
                lines.append(f"  · {m['file']} → {nm}" + (f"  ({m['note']})" if m["note"] else ""))
            else:
                lines.append(f"  · {m['file']} → (매칭 안 됨: {m['note']})")
        msg = (f"카드 {len(matches)}장을 만들었습니다. 글 폴더에 이렇게 넣습니다:\n\n" + "\n".join(lines[:20])
               + (f"\n  … 외 {len(lines) - 20}장" if len(lines) > 20 else "")
               + (f"\n\n같은 이름의 기존 그림 {n_old}개는 _카드작업/{CARD_BACKUP_SUBFOLDER}로 옮깁니다." if n_old else "")
               + "\n\n진행할까요? ('아니오'면 결과는 _카드작업/out에만 남습니다)")
        if not messagebox.askyesno("MD 폴더에 넣기", msg):
            self.card_status_var.set(f"결과는 {os.path.join(work, 'out')}에만 있습니다(MD 폴더에 넣지 않음).")
            return
        placed, unmatched, moved, missing = card_install(work, matches, folder, self._card_name)
        note = f"✅ {len(placed)}장을 글 폴더에 넣었습니다"
        if moved:
            note += f" · 기존 그림 {moved}개는 {CARD_BACKUP_SUBFOLDER}로 이동"
        if unmatched:
            note += f" · 매칭 안 됨 {len(unmatched)}장({', '.join(unmatched)})은 _카드작업/out에만 있음 — 직접 넣으세요"
        if missing:
            note += f" · 결과 없음 {len(missing)}장({', '.join(missing)})"
        self.card_status_var.set(note)
        self._open_folder(folder)

    def _get_selected_ig_row(self):
        key = self.ig_service_var.get()
        return getattr(self, "_ig_service_rows", {}).get(key)

    def _open_ig_service_folder(self):
        row = self._get_selected_ig_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 대상 서비스를 선택하세요.")
            return
        text = get_final_adaptation_text_for_use(row["servId"], row["servNm"])
        title = extract_title_from_final_text(text) or row["servNm"]
        folder = get_final_post_folder(title)
        os.makedirs(folder, exist_ok=True)
        self._open_folder(folder)

    def _generate_infographic_title_list(self):
        """선택한 서비스의 최종각색 결과에서 썸네일(제목)+소제목을 뽑아
        체크박스+복사버튼 목록으로 그린다(정책뉴스 프로그램의
        _generate_title_list와 동일한 방식)."""
        row = self._get_selected_ig_row()
        for w in self.ig_title_list_frame.winfo_children():
            w.destroy()
        self.ig_title_vars = []
        if row is None:
            self.ig_progress_var.set("이미지 매칭: 0/0 완료")
            return

        final_text = get_final_adaptation_text_for_use(row["servId"], row["servNm"])
        if not final_text:
            self.ig_progress_var.set("이미지 매칭: 0/0 완료 (최종각색 결과 없음)")
            return

        items = extract_infographic_title_list(final_text)
        if not items:
            ttk.Label(self.ig_title_list_frame, text="본문에서 제목을 찾을 수 없습니다.").grid(row=0, column=0, sticky="w")
            self.ig_progress_var.set("이미지 매칭: 0/0 완료")
            return

        saved_status = load_infographic_status().get(row["servId"], {})

        for i, (kind, title) in enumerate(items):
            row_f = ttk.Frame(self.ig_title_list_frame)
            row_f.grid(row=i, column=0, sticky="ew", pady=2)
            row_f.columnconfigure(2, weight=1)

            done_var = tk.BooleanVar(value=bool(saved_status.get(str(i), False)))
            self.ig_title_vars.append(done_var)

            cb = ttk.Checkbutton(row_f, variable=done_var)
            cb.grid(row=0, column=0, padx=(4, 4))

            badge_color = "#1F4E78" if kind == "썸네일" else "#2E7D32"
            badge_lbl = tk.Label(row_f, text=f" {kind} ", bg=badge_color, fg="white",
                                  font=("맑은 고딕", 8, "bold"), padx=4)
            badge_lbl.grid(row=0, column=1, padx=(0, 6))

            title_lbl = tk.Label(row_f, text=title, anchor="w", font=("맑은 고딕", 9),
                                  wraplength=750, justify="left")
            title_lbl.grid(row=0, column=2, sticky="ew")

            fname_hint = "thumbnail" if kind == "썸네일" else f"infographic_{i:02d}"
            fname_lbl = tk.Label(row_f, text=fname_hint, anchor="w", font=("맑은 고딕", 8), fg="gray")
            fname_lbl.grid(row=0, column=3, padx=(6, 6))

            copy_text = strip_trailing_punct_for_filename(title)

            def _copy(copy_text=copy_text):
                self.clipboard_clear()
                self.clipboard_append(copy_text)
                self._log(f"📋 인포그래픽 제목 복사: {copy_text[:40]}")
            copy_btn = ttk.Button(row_f, text="복사", width=6, command=_copy)
            copy_btn.grid(row=0, column=4)

            # 체크(=이 제목은 인포그래픽을 그리지 않기로 함) 상태를 실제로
            # 줄 전체 비활성화로 반영 — 복사 버튼을 눌러 그릴 대상이 아닌
            # 제목을 실수로 복사하지 못하도록 막고, 라벨도 회색으로 흐리게
            # 표시해 시각적으로도 "이 줄은 대상 아님"이 바로 보이게 한다.
            def apply_row_state(checked, title_lbl=title_lbl, fname_lbl=fname_lbl,
                                 badge_lbl=badge_lbl, copy_btn=copy_btn):
                copy_btn.configure(state="disabled" if checked else "normal")
                title_lbl.configure(fg="#B0B0B0" if checked else "black")
                fname_lbl.configure(fg="#C8C8C8" if checked else "gray")
                badge_lbl.configure(bg="#BDBDBD" if checked else badge_color)

            apply_row_state(done_var.get())

            def make_toggle(serv_id=row["servId"], var=done_var, apply_state=apply_row_state):
                def _toggle():
                    self._save_ig_image_status(serv_id)
                    apply_state(var.get())
                    done_count = sum(1 for v in self.ig_title_vars if v.get())
                    self.ig_progress_var.set(f"이미지 매칭: {done_count}/{len(self.ig_title_vars)} 완료")
                return _toggle

            cb.configure(command=make_toggle())

        done_count = sum(1 for v in self.ig_title_vars if v.get())
        self.ig_progress_var.set(f"이미지 매칭: {done_count}/{len(items)} 완료")

    def _save_ig_image_status(self, serv_id: str):
        data = load_infographic_status()
        data[serv_id] = {str(i): v.get() for i, v in enumerate(self.ig_title_vars)}
        save_infographic_status(data)

    # ---------------- 키워드 등록 탭 ----------------
    def _list_final_post_folders(self) -> list:
        """final_posts 아래의 제목별 하위폴더 목록을
        [{title, folder, file_count}] 형태로 돌려준다."""
        if not os.path.isdir(FINAL_POSTS_DIR):
            return []
        items = []
        for name in sorted(os.listdir(FINAL_POSTS_DIR)):
            folder = os.path.join(FINAL_POSTS_DIR, name)
            if not os.path.isdir(folder):
                continue
            try:
                files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            except OSError:
                files = []
            # 날짜 = MD를 저장한 날(카드·그림을 나중에 넣어도 바뀌지 않게 MD 기준, 없으면 폴더)
            md = [f for f in files if f.lower().endswith(".md")]
            try:
                ts = max(os.path.getmtime(os.path.join(folder, f)) for f in md) if md else os.path.getmtime(folder)
                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except (OSError, ValueError):
                date = ""
            items.append({"title": name, "folder": folder, "file_count": len(files), "date": date})
        return items

    _BOARD_SRC_LABEL = {"manual": "직접", "map": "매핑", "prompt": "A판정", "rule": "규칙", "etc": ""}

    def _decide_kw_reg_boards(self):
        """[2026-09-29] 각 항목의 게시판을 (직접 지정 > 서비스명 매핑표 > 키워드 규칙 >
        미분류) 순으로 정해 it["board"]에 저장한다. 제목(폴더명) → servId → 서비스명을
        역으로 찾아 매핑표 조회에 쓴다. 게시판 설정이 없으면 아무것도 안 한다."""
        cfg = load_board_cfg()
        if not (getattr(self, "_board_cfg_reg", {}).get("ok") and cfg.get("ok")):
            return
        try:
            index = load_final_posts_index()
            status_map = load_posting_status()
        except Exception:
            index, status_map = {}, {}
        manual = getattr(self, "kw_reg_board_manual", {})
        for it in getattr(self, "kw_reg_items", []):
            if it.get("registered"):
                it["board"] = None
                continue
            sid = index.get(it["title"], "")
            serv_nm = status_map.get(sid, {}).get("servNm", "") if sid else ""
            it["serv_nm"] = serv_nm
            it["board"] = board_mod.decide_board(
                cfg, title=it["title"], serv_nm=serv_nm,
                manual_name=manual.get(it["title"], ""))

    def _apply_kw_reg_board(self):
        """[2026-09-29] 표에서 고른 항목들의 게시판을 콤보 값으로 직접 지정한다.
        '기타(미분류)'를 고르면 직접 지정을 해제하고 자동 판정으로 되돌린다."""
        cfg = load_board_cfg()
        sel = self.kw_reg_tree.selection()
        if not sel:
            messagebox.showinfo("알림", "표에서 게시판을 바꿀 항목을 먼저 선택하세요.")
            return
        label = self.kw_board_var.get().strip()
        if not label:
            messagebox.showinfo("알림", "적용할 게시판을 콤보에서 먼저 고르세요.")
            return
        b = board_mod.board_from_label(cfg, label)
        for iid in sel:
            if b is None:
                self.kw_reg_board_manual.pop(iid, None)
            else:
                self.kw_reg_board_manual[iid] = b["name"]
        self._refresh_keyword_reg_preview()

    def _refresh_keyword_reg_preview(self):
        items = self._list_final_post_folders()
        registered = load_registered_keyword_titles()
        for it in items:
            it["registered"] = normalize_keyword_for_match(it["title"]) in registered

        self.kw_reg_items = items
        self._decide_kw_reg_boards()   # [2026-09-29] 게시판 자동 판정
        dates = sorted({it["date"] for it in items if it.get("date")}, reverse=True)
        self.kw_reg_date_combo["values"] = ["전체"] + dates
        if self.kw_reg_date_var.get() not in (["전체"] + dates):
            self.kw_reg_date_var.set("전체")
        self._render_kw_reg_tree()

    def _kw_reg_visible_items(self) -> list:
        """날짜 선택·상태 필터에 맞는 항목(화면에 보이는 것)."""
        d = self.kw_reg_date_var.get()
        st = self.kw_reg_filter_var.get()
        out = []
        for it in getattr(self, "kw_reg_items", []):
            if d and d != "전체" and it.get("date") != d:
                continue
            if st == "신규" and it["registered"]:
                continue
            if st == "이미 등록됨" and not it["registered"]:
                continue
            out.append(it)
        return out

    def _render_kw_reg_tree(self):
        items = getattr(self, "kw_reg_items", [])
        shown = self._kw_reg_visible_items()
        for i in self.kw_reg_tree.get_children():
            self.kw_reg_tree.delete(i)
        for it in shown:
            status_label = "이미 등록됨" if it["registered"] else "신규"
            tag = "registered" if it["registered"] else "new"
            bd = it.get("board")
            if bd is None:
                board_txt = ""
            elif bd.get("name"):
                src = self._BOARD_SRC_LABEL.get(bd.get("source", ""), "")
                board_txt = f"{bd['name']} ({src}{bd.get('conf', '')})"
            else:
                board_txt = "미분류 (직접 지정 필요)"
            # v6.5: 등록 시 "선택 항목만 등록"을 지원하려면 선택된 트리
            # 행이 어떤 item인지 역으로 찾아야 하므로, iid를 title로
            # 명시해둔다(listing_tree가 servId를 iid로 쓰는 것과 동일한
            # 패턴). title은 final_posts 아래 폴더명 그대로라 고유함.
            self.kw_reg_tree.insert("", "end", iid=it["title"],
                                     values=(status_label, it["title"], it["file_count"], board_txt), tags=(tag,))

        new_count = sum(1 for it in items if not it["registered"])
        reg_count = sum(1 for it in items if it["registered"])
        summary = f"총 {len(items)}건 (신규 {new_count} / 이미 등록됨 {reg_count})"
        if len(shown) != len(items):
            summary += f" · 표시 {len(shown)}건"
        self.kw_reg_summary_var.set(summary)

    def _process_keyword_registration(self):
        """신규 항목을 등록한다: ① final_posts/{제목}/ 를 백업 폴더로
        이동 ② 백업본을 POSTING_MD_FOLDER/{제목}/ 로 복사(메인 포스팅
        프로그램이 읽어갈 위치) ③ 키워드 엑셀에 제목 추가(카테고리는
        입력란 값, 비우면 마지막 값 재사용, 상태는 비움) ④ 포스팅상태를
        🟢 포스팅대기로 자동 전환(단, 이미 📤포스팅완료/🗑️포스팅후삭제인
        건은 건드리지 않음 — 보호 로직은 set_posting_status가 알아서
        막아준다).

        v6.5: 지금까지는 트리에서 몇 건을 선택하든 무시하고 항상 신규
        전체를 일괄 등록했음(사용자 리포트로 확인). 그리드에서 선택된
        행이 있으면 그 항목만 등록하고, 아무것도 선택하지 않았으면
        기존과 동일하게 신규 전체를 등록한다(기존 동작과 완전히 호환).
        선택 항목 중 "이미 등록됨" 상태가 섞여 있으면 그 건은 조용히
        제외한다(다시 등록할 필요가 없으므로).

        지자체 연관 정책 미처리 여부는 여기서 확인하지 않는다 — 그 체크는
        "포스팅완료로 전환하는 시점"에만 적용된다(4)포스팅 관리 탭 STEP 7 완료 처리,
        7)포스팅 이력관리 탭). 키워드 등록은 지자체 연관 여부와 무관하게
        진행한다."""
        items = getattr(self, "kw_reg_items", None)
        if items is None:
            self._refresh_keyword_reg_preview()
            items = self.kw_reg_items

        selected_titles = set(self.kw_reg_tree.selection())
        if selected_titles:
            new_items = [it for it in items if it["title"] in selected_titles and not it["registered"]]
            scope_label = f"선택 {len(new_items)}건"
        else:
            # [Ver10.12] 날짜·상태 필터로 걸러 보이는 신규만(필터가 "전체"면 예전과 같이 신규 전체)
            new_items = [it for it in self._kw_reg_visible_items() if not it["registered"]]
            scope_label = (f"신규 전체 {len(new_items)}건" if len(self._kw_reg_visible_items()) == len(items)
                           else f"화면에 보이는 신규 {len(new_items)}건")

        if not new_items:
            messagebox.showinfo(
                "알림",
                "등록할 신규 항목이 없습니다." if not selected_titles
                else "선택한 항목 중 등록할 신규 항목이 없습니다(이미 등록됨만 선택된 것 같습니다)."
            )
            return

        if not HAS_OPENPYXL:
            messagebox.showerror("오류", "openpyxl이 설치되어 있지 않습니다.")
            return

        # ✅ [2026-09-29] 게시판 모드: 제목마다 정해진 게시판 값을 B열에 기록한다.
        board_mode = bool(getattr(self, "_board_cfg_reg", {}).get("ok"))
        cat_by_title = {}
        if board_mode:
            bcfg = load_board_cfg()
            counts, unassigned = {}, []
            for it in new_items:
                bname = (it.get("board") or {}).get("name", "")
                cat_by_title[it["title"]] = board_mod.cell_value(bcfg, bname) if bname else ""
                key = bname or "미분류"
                counts[key] = counts.get(key, 0) + 1
                if not bname:
                    unassigned.append(it["title"])
            category_display = "게시판별 배정 — " + ", ".join(f"{k} {v}건" for k, v in counts.items())
            if unassigned:
                preview_u = "\n".join(f"  · {t[:40]}" for t in unassigned[:10])
                if len(unassigned) > 10:
                    preview_u += f"\n  … 외 {len(unassigned) - 10}건"
                if not messagebox.askyesno(
                    "게시판 미분류",
                    f"게시판이 정해지지 않은 항목이 {len(unassigned)}건 있습니다:\n\n{preview_u}\n\n"
                    f"이대로 등록하면 키워드 엑셀 B열이 빈칸으로 들어갑니다.\n"
                    f"'아니오'를 눌러 표에서 게시판을 직접 지정한 뒤 다시 등록하는 것을 권장합니다.\n\n"
                    f"그래도 등록하시겠습니까?"
                ):
                    return
        else:
            category_display = self.kw_category_var.get().strip() or "(비워둠 → 엑셀의 직전 카테고리 재사용)"
        if not messagebox.askyesno(
            "확인",
            f"{scope_label}을 등록합니다.\n\n"
            f"· 카테고리: {category_display}\n"
            f"· 키워드 엑셀에 제목 추가\n"
            f"· 원본을 백업 폴더로 이동: {FINAL_POSTS_BACKUP_DIR}\n"
            f"· 백업본을 메인 포스팅 프로그램 폴더로 복사: {POSTING_MD_FOLDER}\n"
            f"· 포스팅상태를 🟢 포스팅대기로 자동 전환\n\n"
            f"계속하시겠습니까?"
        ):
            return

        final_posts_index = load_final_posts_index()
        rows_by_id = {r["servId"]: r for r in build_listing_rows()}

        registered_titles = []
        skipped = []
        status_changed = []
        board_saved = 0   # [2026-09-29 2차] 상태 DB에 게시판 값을 기록한 건수

        os.makedirs(FINAL_POSTS_BACKUP_DIR, exist_ok=True)
        os.makedirs(POSTING_MD_FOLDER, exist_ok=True)

        # 지자체 연관 정책 미처리 체크는 여기서 하지 않는다 — 그 체크는
        # "포스팅완료로 전환하는 시점"(4)포스팅 관리 탭 STEP 7 완료 처리 / 7)포스팅 이력관리
        # 탭)에만 적용되어야 한다. 키워드 등록은 지자체 연관 여부와
        # 무관하게 진행한다.
        for it in new_items:
            title = it["title"]
            src = it["folder"]
            backup_dest = os.path.join(FINAL_POSTS_BACKUP_DIR, title)
            posting_dest = os.path.join(POSTING_MD_FOLDER, title)
            try:
                if os.path.isdir(backup_dest):
                    shutil.rmtree(backup_dest)
                shutil.move(src, backup_dest)
                if os.path.isdir(posting_dest):
                    shutil.rmtree(posting_dest)
                shutil.copytree(backup_dest, posting_dest)
            except OSError as e:
                skipped.append(f"{title} (파일 이동 실패: {e})")
                continue

            registered_titles.append(title)

            # 포스팅상태를 🟢 포스팅대기로 자동 전환. servId를 못 찾거나
            # (final_posts_index 누락 등), 이미 📤포스팅완료/🗑️포스팅후삭제로
            # 보호된 건은 set_posting_status가 알아서 거부하므로 조용히
            # 건너뛴다 — 파일 이동/엑셀 등록 자체는 이미 끝났으니 등록
            # 결과에는 영향 없음.
            serv_id = final_posts_index.get(title, "")
            row = rows_by_id.get(serv_id) if serv_id else None
            if row:
                ok, _reason = set_posting_status(
                    row["servId"], "🟢 포스팅대기", row["servNm"], row["source"]
                )
                if ok:
                    status_changed.append(title)
            # [2026-09-29 2차] 게시판 값을 포스팅 상태 DB에도 기록(설정이 있을 때만)
            if board_mode and serv_id:
                if set_posting_board(serv_id, board_mod.record_fields(bcfg, it.get("board"))):
                    board_saved += 1

        last_category = ""
        if registered_titles:
            if board_mode:
                append_titles_to_keyword_excel(
                    registered_titles, [cat_by_title.get(t, "") for t in registered_titles])
                last_category = category_display.replace("게시판별 배정 — ", "")
            else:
                last_category = append_titles_to_keyword_excel(registered_titles, self.kw_category_var.get())
                self.kw_category_var.set(last_category)  # 실제 반영된 값으로 갱신(다음 등록 때도 이어서 보이게)
                save_last_used_keyword_category(last_category)  # config.json에도 저장(재시작 후에도 유지)

        skip_note = ("\n\n건너뛴 항목:\n" + "\n".join(skipped)) if skipped else ""
        board_note = f" · 게시판 DB 기록 {board_saved}건" if board_mode else ""
        result_msg = (
            f"✅ {len(registered_titles)}건 등록 완료(카테고리='{last_category}') · "
            f"🟢 포스팅대기 전환 {len(status_changed)}건{board_note} · "
            f"건너뜀 {len(skipped)}건{skip_note}"
        )
        self.kw_reg_result_var.set(result_msg)
        self._log(
            f"📤 키워드 등록 완료: {len(registered_titles)}건 "
            f"(포스팅대기 전환 {len(status_changed)}건, 건너뜀 {len(skipped)}건)"
        )
        messagebox.showinfo("완료", result_msg)

        self._refresh_keyword_reg_preview()
        self._refresh_posting_tree()
        self._refresh_listing_tree()

    # ---------------- 포스팅 이력관리 탭 ----------------
    def _refresh_history_tree(self, all_rows: list = None):
        """🟢포스팅대기 / 📤포스팅완료 / 🗑️포스팅후삭제 상태인 항목만
        모아서 보여준다. 검색어가 있으면 서비스명/서비스ID에 부분일치하는
        항목만 추가로 필터링한다(자료가 많아졌을 때 스크롤 없이 바로
        찾기 위함 — 리스트업 탭 검색과 동일한 방식).

        v6.3: all_rows를 받으면(_refresh_status가 이미 계산해둔 공유
        build_listing_rows() 결과) 재사용하고, 없으면(단독 호출 시) 직접
        계산한다 — _refresh_listing_tree/_refresh_posting_tree와 동일한
        패턴. 이전에는 항상 이 함수 안에서 build_listing_rows()를 새로
        불러, 시작 시 _refresh_status()가 이미 한 번 계산해둔 것과 별개로
        무거운 전체 스캔이 한 번 더(중복으로) 일어나고 있었음."""
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        target_statuses = ("🟢 포스팅대기", PROTECTED_STATUS, DELETED_STATUS)
        source_filter = self.history_source_var.get() if hasattr(self, "history_source_var") else "전체"
        search = self.history_search_var.get().strip().lower() if hasattr(self, "history_search_var") else ""

        base_rows = all_rows if all_rows is not None else build_listing_rows()
        rows = [r for r in base_rows if r["posting_status"] in target_statuses]
        if source_filter != "전체":
            rows = [r for r in rows if r["source"] == source_filter]
        if search:
            rows = [r for r in rows
                    if search in r["servNm"].lower() or search in r["servId"].lower()]
        rows.sort(key=lambda r: (target_statuses.index(r["posting_status"]), r["servNm"]))

        if not rows:
            msg = f"🔍 '{search}'에 해당하는 결과가 없습니다" if search else "표시할 항목이 없습니다"
            self.history_tree.insert("", "end", values=("", msg, "", "", ""))
            self.history_count_var.set("0건")
            return

        for r in rows:
            status = r["posting_status"]
            if status == PROTECTED_STATUS:
                tag = "published"
            elif status == DELETED_STATUS:
                tag = "deleted"
            else:
                tag = "waiting"
            updated_at = load_posting_status().get(r["servId"], {}).get("updated_at", "")
            self.history_tree.insert(
                "", "end", iid=r["servId"],
                values=(r["source"], r["servNm"], r["servId"], status, updated_at),
                tags=(tag,),
            )

        counts = {s: sum(1 for r in rows if r["posting_status"] == s) for s in target_statuses}
        self.history_count_var.set(
            f"대기 {counts['🟢 포스팅대기']} · 완료 {counts[PROTECTED_STATUS]} · "
            f"삭제됨 {counts[DELETED_STATUS]} (총 {len(rows)}건)"
        )

    def _get_selected_history_row(self):
        sel = self.history_tree.selection()
        if not sel:
            return None
        sid = sel[0]
        for r in build_listing_rows():
            if r["servId"] == sid:
                return r
        return None

    def _get_selected_history_rows(self) -> list:
        """선택된 전체 행을 돌려준다(다중선택 지원). build_listing_rows()는
        한 번만 계산해 모든 선택 행이 공유한다."""
        sel_ids = self.history_tree.selection()
        if not sel_ids:
            return []
        rows_by_id = {r["servId"]: r for r in build_listing_rows()}
        return [rows_by_id[sid] for sid in sel_ids if sid in rows_by_id]

    def _history_mark_published(self):
        """선택한 🟢포스팅대기 항목을 📤포스팅완료로 바꾼다. 4)포스팅 관리 탭의 STEP 7
        완료 처리와 동일한 안전장치(중앙부처면 연관 지자체 미처리 여부
        선확인)를 그대로 적용한다.

        v6.4: 그리드가 selectmode="extended"라 Ctrl/Shift로 여러 줄을
        선택할 수 있는데도, 지금까지는 첫 번째 선택 항목만 처리하고
        나머지는 조용히 무시되고 있었음(사용자 리포트로 확인). ④ 탭의
        _apply_posting_status_change()와 동일한 패턴으로 다중선택 시
        전체를 순회하도록 수정 — 1건 선택 시 동작은 기존과 완전히
        동일(연관 지자체 미처리 시 팝업 후 중단), 2건 이상 선택 시에는
        건마다 팝업을 띄우면 번거로우므로 연관 지자체 미처리 건은
        조용히 건너뛰고 마지막에 결과를 요약해서 보여준다."""
        rows = self._get_selected_history_rows()
        if not rows:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return

        not_waiting = [r for r in rows if r["posting_status"] != "🟢 포스팅대기"]
        rows = [r for r in rows if r["posting_status"] == "🟢 포스팅대기"]
        if not rows:
            messagebox.showwarning("알림", "이 버튼은 '🟢 포스팅대기' 상태인 항목에만 사용합니다.")
            return

        if len(rows) == 1:
            row = rows[0]
            if row["source"] == "중앙부처":
                unresolved = get_unresolved_related_lcgv_ids(row)
                if unresolved:
                    if messagebox.askyesno(
                        "⚠️ 연관 지자체 정책 미처리",
                        f"'{row['servNm']}'과 이름이 유사한 지자체 정책 중 아직 처리되지 "
                        f"않은 항목이 {len(unresolved)}건 있어 포스팅완료로 바꿀 수 "
                        f"없습니다.\n\n지금 연관 정책을 확인하시겠습니까?"
                    ):
                        self._show_related_policies_popup(row)
                    return
            ok, reason = set_posting_status(row["servId"], PROTECTED_STATUS, row["servNm"], row["source"])
            if not ok:
                messagebox.showwarning("⚠️ 포스팅완료 보호", reason)
                return
            self._log(f"📤 포스팅완료로 변경: {row['servNm']}")
            self._refresh_history_tree()
            self._refresh_posting_tree()
            self._refresh_listing_tree()
            return

        # ---- 다중선택(2건 이상) ----
        rows_by_id = {r["servId"]: r for r in build_listing_rows()}
        changed, blocked, failed = [], [], []
        for row in rows:
            if row["source"] == "중앙부처":
                unresolved = get_unresolved_related_lcgv_ids(row, rows_by_id)
                if unresolved:
                    blocked.append(row)
                    continue
            ok, reason = set_posting_status(row["servId"], PROTECTED_STATUS, row["servNm"], row["source"])
            if ok:
                changed.append(row)
            else:
                failed.append((row, reason))

        self._refresh_history_tree()
        self._refresh_posting_tree()
        self._refresh_listing_tree()

        lines = [f"✅ {len(changed)}건 포스팅완료로 변경"]
        if blocked:
            names = ", ".join(r["servNm"] for r in blocked[:5])
            more = f" 외 {len(blocked) - 5}건" if len(blocked) > 5 else ""
            lines.append(f"⚠️ 연관 지자체 미처리로 건너뜀: {len(blocked)}건 ({names}{more})")
        if failed:
            names = ", ".join(r["servNm"] for r, _ in failed[:5])
            more = f" 외 {len(failed) - 5}건" if len(failed) > 5 else ""
            lines.append(f"❌ 변경 실패: {len(failed)}건 ({names}{more})")
        if not_waiting:
            lines.append(f"⏭ '🟢 포스팅대기' 상태가 아니어서 제외: {len(not_waiting)}건")
        summary = "\n".join(lines)
        self._log(summary.replace("\n", " / "))
        if blocked or failed or not_waiting:
            messagebox.showinfo("포스팅완료 처리 결과", summary)

    def _history_mark_deleted(self):
        """선택한 📤포스팅완료 항목을, 실제로 네이버 블로그에서 글을
        삭제한 경우에 한해 "🗑️ 포스팅후삭제"로 바꾼다. 되돌릴 수 없는
        성격의 작업은 아니지만(다시 포스팅완료로 되돌리는 것은 자유),
        실수 방지를 위해 반드시 두 번 확인한다. "🆕 신규"로 되돌리지
        않는 이유는 재작성을 유도하지 않기 위함 — stage_outputs 등
        기존 데이터는 그대로 보존된다."""
        row = self._get_selected_history_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        if row["posting_status"] != PROTECTED_STATUS:
            messagebox.showwarning("알림", "이 버튼은 '📤 포스팅완료' 상태인 항목에만 사용합니다.")
            return

        if not messagebox.askyesno(
            "블로그에서 실제로 삭제했습니까?",
            f"'{row['servNm']}'\n\n"
            f"이 기능은 실제로 네이버 블로그에서 글을 삭제한 경우에만 "
            f"사용합니다. 상태가 '🗑️ 포스팅후삭제'로 바뀌며, 저장된 "
            f"프롬프트 결과·최종원고 등 다른 데이터는 그대로 남습니다("
            f"다시 새로 작성하도록 신규로 되돌리지 않습니다).\n\n"
            f"정말로 블로그에서 삭제하셨습니까?"
        ):
            return
        if not messagebox.askyesno(
            "다시 한번 확인합니다",
            f"'{row['servNm']}'을(를) '🗑️ 포스팅후삭제'로 표시합니다.\n"
            f"이 작업을 진행할까요?"
        ):
            return

        mark_post_deleted_from_blog(row["servId"], row["servNm"], row["source"])
        self._log(f"🗑️ 포스팅후삭제로 표시: {row['servNm']}")
        self._refresh_history_tree()
        self._refresh_posting_tree()
        self._refresh_listing_tree()

    def _copy_infographic_prompt(self):
        """[Ver10.08] 5)인포그래픽 작성 탭의 "대상 서비스" 기준으로 복사한다(예전엔 포스팅 관리 탭 선택 기준)."""
        row = self._get_selected_ig_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 대상 서비스를 선택하세요.")
            return

        try:
            prompt = build_infographic_prompt(row["servId"], row["servNm"])
        except ValueError as e:
            messagebox.showerror("최종각색 결과 필요", str(e))
            return
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        self._log(f"📋 인포그래픽 프롬프트 복사 완료: {row['servNm']}")

        if advance_posting_status(row["servId"], "🎨 인포그래픽준비중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _copy_infographic_prompt_only(self):
        """인포그래픽 프롬프트 문구만 복사한다. 대상 서비스가 선택돼 있으면
        "+자료 복사"와 동일하게 상태도 함께 진행시킨다."""
        try:
            prompt = get_prompt_infographic_instructions()
        except PromptFileMissingError as e:
            messagebox.showerror("프롬프트 파일 없음", str(e))
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        row = self._get_selected_ig_row()
        if row is None:
            self._log("📋 인포그래픽 프롬프트(문구만) 복사 완료")
            return
        self._log(f"📋 인포그래픽 프롬프트(문구만) 복사 완료: {row['servNm']}")
        if advance_posting_status(row["servId"], "🎨 인포그래픽준비중", row["servNm"], row["source"]):
            self._refresh_posting_tree()

    def _open_selected_posting_folder(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        self._open_folder(row["folder"])

    def _open_selected_attachments_folder(self):
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return
        attach_dir = os.path.join(row["folder"], "attachments")
        if not list_attachment_files(row["folder"]):
            messagebox.showinfo("공식자료 없음", f"'{row['servNm']}'에는 받아 둔 공식자료가 없습니다.")
            return
        self._open_folder(attach_dir)

    def _open_final_posts_folder(self):
        """최종각색 결과(.md)가 저장되는 폴더를 연다. 특정 서비스 선택
        여부와 무관하게 폴더 전체를 연다 — 여러 건을 한 번에 확인할 때 씀."""
        os.makedirs(FINAL_POSTS_DIR, exist_ok=True)
        self._open_folder(FINAL_POSTS_DIR)

    def _get_selected_final_title(self):
        """[v7.0 추가, 정책뉴스 TAB4 '제목 검색' 버튼에서 이식] 현재
        포스팅 관리 탭에서 선택된 항목의 저장된 최종각색 결과에서 제목을
        추출해 돌려준다. 선택 항목이 없거나 저장된 최종각색 결과가 없거나
        제목(# 헤딩)을 못 찾으면 안내 팝업을 띄우고 None을 반환한다."""
        row = self._get_selected_posting_row()
        if row is None:
            messagebox.showwarning("알림", "먼저 항목을 선택하세요.")
            return None
        final_text = get_final_adaptation_text_for_use(row["servId"], row["servNm"])
        if not final_text:
            messagebox.showwarning(
                "알림",
                f"'{row['servNm']}'에는 저장된 최종각색 결과가 없습니다.\n\n"
                f"먼저 4)포스팅 관리 탭 STEP 6에서 최종각색 프롬프트 복사 → 최종각색 결과 저장을 진행하세요."
            )
            return None
        title = extract_title_from_final_text(final_text)
        if not title:
            messagebox.showwarning("알림", "저장된 최종각색 결과에서 제목(# 제목)을 찾지 못했습니다.")
            return None
        return title

    def _open_naver_blog_search_for_title(self):
        """[v7.0 신규, 정책뉴스 TAB4 '🔍 블로그' 버튼에서 이식] 선택 항목의
        최종각색 제목으로 네이버 블로그 탭 검색을 연다 — 같은 제목의 글이
        이미 있는지(제목 선점 여부) 확인하는 용도. 매번 새 임시 프로필로
        열려 항상 비로그인 상태."""
        title = self._get_selected_final_title()
        if not title:
            return
        if self._check_ip_before_naver_open():
            return
        ok = open_naver_search_in_chrome(title, blog_only=True)
        if ok:
            self._log(f"🔍 제목 블로그검색(비로그인 새 창): {title}")
        else:
            self._log(f"⚠️ 크롬을 찾지 못해 기본 브라우저로 열었습니다(비로그인 보장 안 됨): {title}")

    def _copy_title_text(self, title: str):
        """[Ver10.08] 제목을 그대로 클립보드에 복사한다(통합검색 버튼 자리 — 정책뉴스 Ver10.09와 같음)."""
        self.clipboard_clear()
        self.clipboard_append(title)
        messagebox.showinfo("복사 완료", f"제목을 복사했습니다.\n\n{title}")

    def _copy_candidate_title(self, idx):
        title = self.title_cand_texts[idx] if idx < len(self.title_cand_texts) else ""
        if not title:
            messagebox.showwarning("알림", "이 자리에는 추출된 후보가 없습니다.")
            return
        self._copy_title_text(title)

    def _copy_manual_title(self):
        title = self.title_cand_manual_var.get().strip()
        if not title:
            messagebox.showwarning("알림", "직접 입력 칸에 제목을 먼저 입력하세요.")
            return
        self._copy_title_text(title)

    def _copy_final_title(self):
        """선택 항목의 최종각색 제목 복사(예전 "🔍 제목 통합검색" 자리)."""
        title = self._get_selected_final_title()
        if title:
            self._copy_title_text(title)

    def _export_posting_history(self):
        """포스팅 이력 엑셀을 고정 경로(Naver_blog_복지로_posting_history.xlsx)에
        저장한다. 필터와 무관하게 수집완료된 전체 자료를 기준으로 저장해야
        외부 포스팅 프로그램이 언제나 같은 위치에서 전체 이력을 읽을 수 있다."""
        rows = [r for r in build_listing_rows() if r["downloaded"]]
        if not rows:
            messagebox.showwarning("알림", "내보낼 항목이 없습니다.")
            return
        save_path = get_posting_history_excel_path()

        while True:
            ok, result = export_posting_status_xlsx(rows, save_path)
            if ok:
                self._log(f"📊 포스팅 이력 엑셀 저장 완료: {result}")
                messagebox.showinfo("완료", f"포스팅 이력 엑셀 저장 완료:\n{result}")
                return
            if "openpyxl" in str(result):
                messagebox.showerror("오류", result)
                return
            retry = messagebox.askretrycancel(
                "엑셀 저장 실패",
                f"엑셀 저장에 실패했습니다.\n\n{result}\n\n"
                f"엑셀에서 파일을 완전히 닫은 뒤 [다시 시도]를 눌러주세요."
            )
            if not retry:
                return

    # ---------------- 설정 ----------------
    def _browse_dir(self, var: tk.StringVar):
        cur = var.get()
        init = cur if (cur and os.path.exists(cur)) else BASE_DIR
        path = filedialog.askdirectory(initialdir=init)
        if path:
            var.set(path)

    def _browse_board_config(self):
        """[2026-09-29] 게시판 설정 엑셀 선택(기존 파일만 선택 가능)."""
        cur = self.settings_board_config_var.get().strip()
        init_dir = os.path.dirname(cur) if cur and os.path.dirname(cur) else BASE_DIR
        init_dir = init_dir if os.path.exists(init_dir) else BASE_DIR
        path = filedialog.askopenfilename(
            title="게시판 설정 엑셀 선택", initialdir=init_dir,
            filetypes=[("엑셀 파일", "*.xlsx"), ("모든 파일", "*.*")])
        if path:
            self.settings_board_config_var.set(path)

    def _browse_excel_file(self, var: tk.StringVar):
        """엑셀 파일 경로 선택. 기존 파일을 고르거나, 없으면 새 위치를 지정한다
        (정책뉴스 프로그램의 _browse_keyword_excel과 동일한 방식 — 절대경로
        그대로 저장, 반드시 작업폴더 안에 있어야 하는 건 아니라서)."""
        cur = var.get()
        init_dir = os.path.dirname(cur) if cur and os.path.dirname(cur) else WORK_DIR
        init_dir = init_dir if os.path.exists(init_dir) else BASE_DIR
        path = filedialog.askopenfilename(
            title="엑셀 파일 선택", initialdir=init_dir,
            filetypes=[("엑셀 파일", "*.xlsx"), ("모든 파일", "*.*")],
        )
        if not path:
            path = filedialog.asksaveasfilename(
                title="엑셀 파일 위치 지정 (새 파일)", initialdir=init_dir,
                defaultextension=".xlsx", filetypes=[("엑셀 파일", "*.xlsx")],
            )
        if path:
            var.set(path)

    def _browse_prompt_file(self, var: tk.StringVar):
        """프롬프트 파일 선택. 정책뉴스 프로그램과 동일하게 PROMPT_DIR 기준
        파일명만 저장한다(절대경로가 아님) — 작업폴더가 옮겨져도 같이 따라가게."""
        path = filedialog.askopenfilename(
            title="프롬프트 파일 선택",
            initialdir=PROMPT_DIR if os.path.exists(PROMPT_DIR) else BASE_DIR,
            filetypes=[("마크다운/텍스트", "*.md *.txt"), ("모든 파일", "*.*")],
        )
        if path:
            var.set(os.path.basename(path))

    def _save_path_settings(self):
        cfg = load_config()
        cfg["work_dir"] = _to_stored_dir(self.settings_workdir_var.get().strip())
        cfg["keyword_excel_path"] = self.settings_keyword_var.get().strip()
        cfg["posting_history_excel_path"] = self.settings_history_var.get().strip()
        cfg["unified_keyword_excel_path"] = self.settings_unified_keyword_var.get().strip()
        cfg["board_config_path"] = self.settings_board_config_var.get().strip()  # [2026-09-29]
        cfg["naver_openapi_client_id"] = self.settings_openapi_id_var.get().strip()
        cfg["naver_openapi_client_secret"] = self.settings_openapi_secret_var.get().strip()
        cfg["naver_ad_api_key"] = self.settings_ad_key_var.get().strip()
        cfg["naver_ad_secret_key"] = self.settings_ad_secret_var.get().strip()
        cfg["naver_ad_customer_id"] = self.settings_ad_customer_var.get().strip()
        cfg["prompt_prescreening_value_combo_file"] = self.settings_prompt_prescreening_combo_var.get().strip() or _DEFAULT_CONFIG["prompt_prescreening_value_combo_file"]
        cfg["prompt_quick_judgment_file"] = self.settings_prompt_quick_var.get().strip() or _DEFAULT_CONFIG["prompt_quick_judgment_file"]
        try:
            cfg["auto_blog_count"] = max(0, min(5, int(self.settings_auto_blog_count_var.get())))
        except (TypeError, ValueError):
            cfg["auto_blog_count"] = _DEFAULT_CONFIG["auto_blog_count"]
        cfg["my_blog_ids"] = self.settings_my_blog_ids_var.get().strip()
        cfg["openai_api_key"] = self.settings_openai_key_var.get().strip()   # [Ver10.06]
        cfg["prompt_draft_file"] = self.settings_prompt_draft_var.get().strip() or _DEFAULT_CONFIG["prompt_draft_file"]
        cfg["prompt_claude_second_stage_file"] = self.settings_prompt_claude2_var.get().strip() or _DEFAULT_CONFIG["prompt_claude_second_stage_file"]
        cfg["prompt_infographic_file"] = self.settings_prompt_info_var.get().strip() or _DEFAULT_CONFIG["prompt_infographic_file"]
        # [Ver10.07] 코드 카드(선택)
        cfg["prompt_infographic_card_file"] = self.settings_prompt_card_var.get().strip() or _DEFAULT_CONFIG["prompt_infographic_card_file"]
        cfg["card_tool_dir"] = self.settings_card_tool_var.get().strip() or "Naver_blog_SVG Card_images"
        cfg["card_chrome_path"] = self.settings_card_chrome_var.get().strip().strip('"')
        save_config(cfg)

        # 즉시 반영 — 재시작 없이 새 경로를 바로 쓰도록 전역 경로들을 재계산
        apply_work_dir_from_config()
        os.makedirs(WORK_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        missing = check_prompt_files_status()  # 파일명을 바꿨다면 새 경로에 파일이 있는지 재점검(자동 생성은 안 함)
        if missing:
            names = ", ".join(label for label, _ in missing)
            self._log(f"⚠ 프롬프트 파일 없음: {names} — 해당 .md 파일을 프롬프트 폴더에 직접 채워 넣어야 합니다.")

        # 입력창 표시값도 실제 해석된 절대경로로 다시 맞춰준다
        self.settings_workdir_var.set(WORK_DIR)
        self.settings_keyword_var.set(get_keyword_excel_path())
        self.settings_history_var.set(get_posting_history_excel_path())
        self.settings_unified_keyword_var.set(get_unified_keyword_excel_path())

        self.settings_saved_var.set(f"저장 완료 ({datetime.datetime.now().strftime('%H:%M:%S')})")
        self._log(f"⚙️ 설정 저장 완료 — 작업폴더: {WORK_DIR}")
        self._refresh_status()

    def _open_folder(self, path):
        # [Ver10.12] 작업 폴더가 "./…" 상대 경로여도 탐색기가 열리게 절대 경로로, 실패하면 말없이 넘어가지 않고 안내
        path = os.path.abspath(path)
        os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)  # Windows
        except OSError as e:
            messagebox.showerror("폴더 열기 실패", f"폴더를 열 수 없습니다:\n{path}\n\n{e}")
        except AttributeError:
            import subprocess
            import sys
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])


if __name__ == "__main__":
    app = WelfareCollectorGUI()
    app.mainloop()