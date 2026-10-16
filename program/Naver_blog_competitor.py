# -*- coding: utf-8 -*-
"""Naver_blog_competitor.py — 🏁 경쟁 블로그 관리(V1, 2026-10-16) — 정책뉴스·복지로 관리 프로그램 공용.

[하는 일] 경쟁 블로그를 등록하고 블로그마다 게시글을 모아 관리한다.
  · 주소 칸에 블로그 주소(blog.naver.com/아이디)를 넣으면 블로그를, 게시글 주소를 넣으면 그 블로그 아래에
    게시글을 등록한다(블로그가 없으면 같이 등록). 등록할 때 정보를 모은다.
  · 트리: 블로그 ▸ 게시글. 고르면 오른쪽에 상세 정보, 비고(메모)를 적어 저장.
  · 블로그 정보: 블로그명·닉네임·개설일(못 찾으면 가장 오래된 글 날짜)·오늘/전체 방문자·이웃 수·전체 글 수·카테고리 목록.
  · 게시글 정보: 제목·작성일·카테고리. "📄 MD 파일 추출"로 본문을 MD로(이미지는 링크만).
[파일·폴더] 두 프로그램 옆(BASE_DIR)
  Naver_blog_경쟁블로그/Naver_blog_competitor_blogs.json   목록(두 프로그램이 같이 씀 — 저장할 때마다 다시 읽어 합침)
  Naver_blog_경쟁블로그/{블로그명}_{아이디}/{게시글 제목}.md  추출한 MD
  Naver_blog_경쟁블로그/Naver_blog_수집기록/                   마지막 수집 때 네이버가 준 원본(못 찾은 칸을 고칠 때 본다)
[반드시 지킬 규칙]
  · 로그인 없이: 수집은 쿠키 없는 요청, MD 추출은 매번 새 임시 프로필의 화면 없는 크롬, 열기는 각 프로그램의
    비로그인 임시 프로필 크롬. 셋 다 각 프로그램의 Base IP 확인을 먼저 거친다.
  · 못 찾은 값은 비워 두고 "못 찾음"으로 보여 준다(짐작해 채우지 않음).
[이런 경우 이렇게]
  · 칸이 "못 찾음" → Naver_blog_수집기록/ 안 해당 블로그 파일을 보면 네이버가 실제로 준 내용이 있다(파서 고칠 때 씀).
"""
import datetime
import json
import math
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from html import unescape
from urllib.parse import urlparse, parse_qs, unquote

DIR_NAME = "Naver_blog_경쟁블로그"
DATA_NAME = "Naver_blog_competitor_blogs.json"
LOG_DIR_NAME = "Naver_blog_수집기록"
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
UA_PC = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
NOT_FOUND = "못 찾음"

BLOG_FIELDS = [("url", "블로그 주소"), ("blog_name", "블로그명"), ("nickname", "닉네임"),
               ("open_date", "개설일"), ("today_visitors", "오늘 방문자"), ("total_visitors", "전체 방문자"),
               ("neighbors", "이웃 수"), ("post_count", "전체 글 수")]
POST_FIELDS = [("url", "게시글 주소"), ("title", "제목"), ("date", "작성일"), ("category", "카테고리")]


# ------------------------------------------------------------------
# 주소 읽기
# ------------------------------------------------------------------
def parse_url(text: str):
    """(blog_id, log_no 또는 "") — 네이버 블로그 주소가 아니면 (None, None)."""
    s = (text or "").strip()
    if not s:
        return None, None
    if not re.match(r"https?://", s):
        s = "https://" + s
    u = urlparse(s)
    host = u.netloc.lower()
    if not host.endswith("blog.naver.com"):
        return None, None
    q = parse_qs(u.query)
    blog_id = (q.get("blogId") or [""])[0]
    log_no = (q.get("logNo") or [""])[0]
    parts = [p for p in u.path.split("/") if p]
    if not blog_id and parts and not parts[0].lower().endswith((".naver", ".nhn")):
        blog_id = parts[0]
        if len(parts) > 1 and parts[1].isdigit():
            log_no = parts[1]
    if not blog_id or not re.fullmatch(r"[A-Za-z0-9_\-]+", blog_id):
        return None, None
    return blog_id, (log_no if log_no.isdigit() else "")


def blog_url(blog_id):
    return f"https://blog.naver.com/{blog_id}"


def post_url(blog_id, log_no):
    return f"https://blog.naver.com/{blog_id}/{log_no}"


# ------------------------------------------------------------------
# 저장(두 프로그램이 같이 쓴다 — 저장할 때마다 파일을 다시 읽어 그 블로그만 바꾼다)
# ------------------------------------------------------------------
class Store:
    def __init__(self, base_dir):
        self.dir = os.path.join(base_dir, DIR_NAME)
        self.path = os.path.join(self.dir, DATA_NAME)
        self.log_dir = os.path.join(self.dir, LOG_DIR_NAME)
        self._lock = threading.Lock()

    def load(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d.get("blogs", {}) if isinstance(d, dict) else {}
        except Exception:
            return {}

    def update(self, blog_id, fn):
        """fn(blog dict) → 그 블로그만 바꿔 저장. fn이 None을 돌려주면 그 블로그를 지운다."""
        with self._lock:
            blogs = self.load()
            cur = blogs.get(blog_id) or {"blog_id": blog_id, "url": blog_url(blog_id), "posts": {}}
            new = fn(cur)
            if new is None:
                blogs.pop(blog_id, None)
            else:
                blogs[blog_id] = new
            os.makedirs(self.dir, exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"ver": 1, "blogs": blogs}, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
            return new

    def md_dir(self, blog):
        name = re.sub(r'[\\/:*?"<>|]', "", blog.get("blog_name") or "").strip()[:40]
        return os.path.join(self.dir, f"{name}_{blog['blog_id']}" if name else blog["blog_id"])


# ------------------------------------------------------------------
# 수집(쿠키 없는 요청 = 비로그인). 네이버가 준 원본은 수집기록 폴더에 남긴다.
# ------------------------------------------------------------------
def _session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": UA_MOBILE, "Accept-Language": "ko-KR,ko;q=0.9"})
    return s


def _get(s, url, log_dir, log_name, referer=None, ua=None):
    h = {}
    if referer:
        h["Referer"] = referer
    if ua:
        h["User-Agent"] = ua
    r = s.get(url, headers=h, timeout=15)
    text = r.text
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, log_name + ".txt"), "w", encoding="utf-8") as f:
            f.write(f"{url}\nHTTP {r.status_code}\n\n{text[:300000]}")
    except Exception:
        pass
    r.raise_for_status()
    return text


def _json(text):
    t = (text or "").strip()
    t = re.sub(r"^\)\]\}',?\s*", "", t)
    try:
        return json.loads(t)
    except Exception:
        return json.loads(t.replace("\\'", "'"))


def _result(j):
    return j.get("result") if isinstance(j, dict) and isinstance(j.get("result"), dict) else j


def _pick(d, *keys):
    for k in keys:
        v = d.get(k) if isinstance(d, dict) else None
        if v not in (None, ""):
            return v
    return None


def _find_date_key(d):
    """블로그 정보 안에 개설일로 보이는 칸(open·create·regist + date·ymd·time)이 있으면 그 값."""
    if not isinstance(d, dict):
        return None
    for k, v in d.items():
        if re.search(r"(open|creat|regist)", k, re.I) and re.search(r"(date|ymd|time|dt)", k, re.I) and v:
            return _fmt_date(v)
    return None


def _fmt_date(v):
    """밀리초·초·'2026. 10. 16.'·'20261016' → '2026-10-16'. 모르면 글자 그대로."""
    try:
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit() and len(v) >= 10):
            n = int(v)
            if n > 10 ** 11:
                n //= 1000
            return datetime.datetime.fromtimestamp(n).strftime("%Y-%m-%d")
        s = str(v).strip()
        m = re.search(r"(\d{4})[.\-/]\s*(\d{1,2})[.\-/]\s*(\d{1,2})", s) or re.fullmatch(r"(\d{4})(\d{2})(\d{2})", s)
        if m:
            return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        if re.search(r"(초|분|시간)\s*전|방금", s):
            return datetime.date.today().isoformat()
        return s
    except Exception:
        return str(v)


def _num(v):
    try:
        return int(str(v).replace(",", "").strip())
    except Exception:
        return None


def collect_blog(blog_id, log_dir) -> dict:
    """블로그 정보. 돌려주는 dict에 'notes'(어디서 못 가져왔는지)가 들어 있다."""
    s = _session()
    out, notes = {"blog_id": blog_id, "url": blog_url(blog_id)}, []
    ref = f"https://m.blog.naver.com/{blog_id}"
    pre = f"{blog_id}_"

    # 1) 블로그 정보: 이름·닉네임·방문자·이웃
    info = {}
    try:
        info = _result(_json(_get(s, f"https://m.blog.naver.com/rego/BlogInfo.naver?blogId={blog_id}",
                                  log_dir, pre + "1_BlogInfo", referer=ref)))
    except Exception as e:
        notes.append(f"블로그 정보(BlogInfo): {e}")
    out["blog_name"] = _pick(info, "blogName", "blogTitle", "title")
    out["nickname"] = _pick(info, "nickName", "displayNickName", "userNickName", "nickname")
    out["today_visitors"] = _num(_pick(info, "dayVisitorCount", "todayVisitorCount", "visitorCountToday"))
    out["total_visitors"] = _num(_pick(info, "totalVisitorCount", "visitorCountTotal"))
    out["neighbors"] = _num(_pick(info, "subscriberCount", "buddyCount", "neighborCount"))
    out["open_date"] = _find_date_key(info)
    if out["open_date"]:
        out["open_date_note"] = "블로그 정보"

    # 2) 이름이 없으면 PC 첫 화면 제목에서
    if not out["blog_name"]:
        try:
            html = _get(s, blog_url(blog_id), log_dir, pre + "2_main", ua=UA_PC)
            m = re.search(r"<title>\s*([^<]+?)\s*(?::\s*네이버 블로그)?\s*</title>", html)
            if m and m.group(1).strip() not in ("네이버 블로그", ""):
                out["blog_name"] = m.group(1).strip()
        except Exception as e:
            notes.append(f"블로그 첫 화면: {e}")

    # 3) 오늘 방문자가 없으면 방문자 그래프(XML, 날짜별) 마지막 날
    if out["today_visitors"] is None:
        try:
            xml = _get(s, f"https://blog.naver.com/NVisitorgp4Ajax.naver?blogId={blog_id}", log_dir,
                       pre + "3_visitor", ua=UA_PC, referer=blog_url(blog_id))
            cnts = re.findall(r'id="(\d{8})"\s+cnt="(\d+)"', xml)
            if cnts:
                out["today_visitors"] = int(sorted(cnts)[-1][1])
        except Exception as e:
            notes.append(f"방문자 그래프: {e}")

    # 4) 카테고리 목록
    cats = []
    try:
        cj = _result(_json(_get(s, f"https://m.blog.naver.com/rego/CategoryList.naver?blogId={blog_id}",
                                log_dir, pre + "4_CategoryList", referer=ref)))
        lst = _pick(cj, "mylogCategoryList", "categoryList", "categories") or []
        for c in lst:
            if not isinstance(c, dict) or c.get("divisionLine"):
                continue
            name = _pick(c, "categoryName", "name")
            if not name:
                continue
            cats.append({"name": str(name), "count": _num(_pick(c, "postCnt", "postCount", "count")),
                         "child": bool(c.get("childCategory") or c.get("parentCategoryNo"))})
    except Exception as e:
        notes.append(f"카테고리 목록(CategoryList): {e}")
    out["categories"] = cats

    # 5) 전체 글 수·가장 오래된 글(개설일 대신)
    total = None
    try:
        t = _get(s, f"https://blog.naver.com/PostTitleListAsync.naver?blogId={blog_id}&viewdate=&currentPage=1"
                    f"&categoryNo=0&parentCategoryNo=&countPerPage=30", log_dir, pre + "5_PostList_p1",
                 ua=UA_PC, referer=blog_url(blog_id))
        total = _num(_pick(_json(t), "totalCount"))
        if total and not out["open_date"]:
            last = max(1, math.ceil(total / 30))
            t2 = _get(s, f"https://blog.naver.com/PostTitleListAsync.naver?blogId={blog_id}&viewdate="
                         f"&currentPage={last}&categoryNo=0&parentCategoryNo=&countPerPage=30", log_dir,
                      pre + "5_PostList_last", ua=UA_PC, referer=blog_url(blog_id))
            lst = _pick(_json(t2), "postList") or []
            if lst:
                d = _fmt_date(_pick(lst[-1], "addDate"))
                if d:
                    out["open_date"] = d
                    out["open_date_note"] = "가장 오래된 글 날짜(개설일 대신)"
    except Exception as e:
        notes.append(f"글 목록(PostTitleListAsync): {e}")
    if total is None:
        try:
            pj = _result(_json(_get(s, f"https://m.blog.naver.com/api/blogs/{blog_id}/post-list?categoryNo=0"
                                       f"&itemCount=30&page=1", log_dir, pre + "6_api_post_list", referer=ref)))
            total = _num(_pick(pj, "totalCount"))
        except Exception as e:
            notes.append(f"글 목록(api post-list): {e}")
    if total is None and cats:
        top = [c["count"] for c in cats if not c["child"] and c["count"] is not None]
        if top:
            total = sum(top)
            notes.append("전체 글 수: 카테고리 글 수를 더한 값(비공개 글은 빠질 수 있음)")
    out["post_count"] = total
    out["notes"] = notes
    out["collected_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return out


def collect_post(blog_id, log_no, log_dir) -> dict:
    s = _session()
    out, notes = {"log_no": log_no, "url": post_url(blog_id, log_no)}, []
    pre = f"{blog_id}_{log_no}_"
    html = ""
    try:
        html = _get(s, f"https://m.blog.naver.com/PostView.naver?blogId={blog_id}&logNo={log_no}",
                    log_dir, pre + "1_mobile", referer=f"https://m.blog.naver.com/{blog_id}")
    except Exception as e:
        notes.append(f"모바일 글 화면: {e}")
    pc = ""
    try:
        pc = _get(s, f"https://blog.naver.com/PostView.naver?blogId={blog_id}&logNo={log_no}"
                     f"&redirect=Dlog&widgetTypeCall=true&directAccess=false", log_dir, pre + "2_pc",
                  ua=UA_PC, referer=blog_url(blog_id))
    except Exception as e:
        notes.append(f"PC 글 화면: {e}")

    def first(patterns, *texts):
        for t in texts:
            for p in patterns:
                m = re.search(p, t or "", re.S)
                if m:
                    v = re.sub(r"<[^>]+>", "", m.group(1))
                    v = re.sub(r"\s+", " ", unescape(v)).strip()
                    if v:
                        return v
        return None

    out["title"] = first([r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"',
                          r'class="[^"]*se-title-text[^"]*"[^>]*>(.*?)</div>',
                          r'class="[^"]*pcol1[^"]*"[^>]*>(.*?)</'], html, pc)
    date = first([r'class="[^"]*blog_date[^"]*"[^>]*>(.*?)</',
                  r'class="[^"]*se_publishDate[^"]*"[^>]*>(.*?)</',
                  r'class="[^"]*date[^"]*"[^>]*>\s*(\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.[^<]*)<'], html, pc)
    out["date"] = _fmt_date(date) if date else None
    out["category"] = first([r'class="[^"]*blog_category[^"]*"[^>]*>(.*?)</(?:a|span|div)>',
                             r'class="[^"]*blog2_series[^"]*"[^>]*>.*?<a[^>]*>(.*?)</a>',
                             r'"categoryName"\s*:\s*"([^"]+)"'], html, pc)
    out["notes"] = notes
    out["collected_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return out


# ------------------------------------------------------------------
# MD 추출 — 매번 새 임시 프로필의 화면 없는 크롬(비로그인). 복지로 프로그램 blog_scrap_* 와 같은 방식, 이미지는 링크만.
# ------------------------------------------------------------------
SUBTITLE_FONT = 19
SUBTITLE_MAX = 60


def _driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    base = "C:\\temp\\naver_blog_scrap_profiles" if sys.platform == "win32" else os.path.join(
        tempfile.gettempdir(), "naver_blog_scrap_profiles")
    os.makedirs(base, exist_ok=True)
    prof = tempfile.mkdtemp(prefix="profile_", dir=base)
    o = Options()
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
              "--window-size=1280,2000", f"--user-data-dir={prof}", f"user-agent={UA_PC}"):
        o.add_argument(a)
    d = webdriver.Chrome(options=o)
    d._temp_profile_dir = prof
    return d


def _quit(d):
    p = getattr(d, "_temp_profile_dir", None)
    try:
        d.quit()
    finally:
        if p:
            shutil.rmtree(p, ignore_errors=True)


def _para_md(p):
    from selenium.webdriver.common.by import By
    spans = p.find_elements(By.CSS_SELECTOR, "span")
    if not spans:
        return p.text.strip(), False
    parts, mx, bold_any, n = [], 0, False, 0
    for sp in spans:
        t = sp.text
        if not t:
            continue
        cls = sp.get_attribute("class") or ""
        st = (sp.get_attribute("style") or "").replace(" ", "")
        bold = "se-bold" in cls or "font-weight:bold" in st or "font-weight:700" in st
        m = re.search(r"se-fs(\d+)", cls) or re.search(r"font-size:(\d+)px", st)
        fs = int(m.group(1)) if m else 15
        mx, n = max(mx, fs), n + len(t)
        bold_any = bold_any or bold
        parts.append(f"**{t}**" if bold else t)
    text = "".join(parts).strip()
    return text, bool(text) and mx >= SUBTITLE_FONT and n <= SUBTITLE_MAX


def _content_md(d):
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    try:
        box = d.find_element(By.CSS_SELECTOR, "div.se-main-container")
    except NoSuchElementException:
        try:
            return d.find_element(By.CSS_SELECTOR, "div#postViewArea, div.post_ct").text.strip()
        except NoSuchElementException:
            raise RuntimeError("본문을 찾지 못했습니다.")
    blocks = []
    for comp in box.find_elements(By.CSS_SELECTOR, ":scope > div.se-component"):
        cls = comp.get_attribute("class") or ""
        try:
            if "se-quotation" in cls:
                b = "\n".join(f"> {x}" for x in comp.text.strip().split("\n") if x.strip())
            elif "se-table" in cls:
                rows = [[(c.text.strip().replace("\n", " ") or " ") for c in r.find_elements(By.CSS_SELECTOR, "th, td")]
                        for r in comp.find_elements(By.CSS_SELECTOR, "table tr")]
                rows = [r for r in rows if r]
                if rows:
                    w = max(len(r) for r in rows)
                    rows = [r + [" "] * (w - len(r)) for r in rows]
                    b = "\n".join(["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * w) + " |"]
                                  + ["| " + " | ".join(r) + " |" for r in rows[1:]])
                else:
                    b = ""
            elif "se-image" in cls:
                b = ""
                for img in comp.find_elements(By.CSS_SELECTOR, "img")[:1]:
                    src = img.get_attribute("data-lazy-src") or img.get_attribute("src") or ""
                    if src and not src.startswith("data:"):
                        b = f"![이미지]({src})"
            elif "se-horizontalLine" in cls:
                b = "---"
            elif "se-text" in cls:
                lines = []
                for p in comp.find_elements(By.CSS_SELECTOR, "p.se-text-paragraph, div.se-text-paragraph"):
                    t, sub = _para_md(p)
                    lines.append(f"## {t}" if sub else t)
                b = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip("\n")
            else:
                b = comp.text.strip()
        except Exception:
            b = ""
        if b:
            blocks.append(b)
    return "\n\n".join(blocks) or box.text.strip()


def extract_md(blog_id, log_no, out_dir, title_hint="") -> str:
    """게시글 본문을 MD로 저장하고 파일 경로를 돌려준다."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    d = _driver()
    try:
        d.get(f"https://m.blog.naver.com/{blog_id}/{log_no}")
        wait = WebDriverWait(d, 10)
        title = ""
        for sel in ("div.se-module.se-module-text.se-title-text", "h3.se_textarea", "div.htitle", "h2.htitle"):
            try:
                title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel))).text.strip()
                if title:
                    break
            except Exception:
                continue
        title = title or title_hint or d.title.split(": 네이버 블로그")[0].strip() or log_no
        body = _content_md(d)
        if not body.strip():
            raise RuntimeError("본문이 비어 있습니다.")
    finally:
        _quit(d)
    os.makedirs(out_dir, exist_ok=True)
    name = re.sub(r'[\\/:*?"<>|]', "", title).strip()[:100] or log_no
    path = os.path.join(out_dir, f"{name}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n- 원본 URL: {post_url(blog_id, log_no)}\n"
                f"- 수집 일시: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{body}\n")
    return path


def open_in_temp_chrome(url) -> bool:
    """새 임시 프로필(비로그인) 크롬으로 연다. 크롬을 못 찾으면 기본 브라우저(비로그인 보장 안 됨)."""
    import subprocess
    cands = []
    if sys.platform.startswith("win"):
        for env, sub in (("PROGRAMFILES", r"C:\Program Files"), ("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                         ("LOCALAPPDATA", "")):
            cands.append(os.path.join(os.environ.get(env, sub), "Google", "Chrome", "Application", "chrome.exe"))
    else:
        cands += [shutil.which(n) or "" for n in ("google-chrome", "chromium", "chromium-browser")]
    chrome = next((c for c in cands if c and os.path.exists(c)), "")
    if not chrome:
        import webbrowser
        webbrowser.open(url)
        return False
    prof = tempfile.mkdtemp(prefix="naver_search_profile_")
    subprocess.Popen([chrome, f"--user-data-dir={prof}", "--no-first-run", "--no-default-browser-check",
                      "--new-window", url])
    return True


# ------------------------------------------------------------------
# 창
# ------------------------------------------------------------------
def open_window(parent, base_dir, ip_blocked=None, open_url=None):
    """ip_blocked() → True면 네이버 접속을 멈춘다(각 프로그램의 Base IP 확인).
    open_url(url) → 비로그인 임시 프로필 크롬으로 연다(IP 확인 포함). 없으면 IP 확인 뒤 open_in_temp_chrome."""
    import tkinter as tk
    from tkinter import ttk, messagebox
    try:
        from Naver_blog_blog_sync import center_window
    except Exception:
        def center_window(w, width, height, over=None):
            sw, sh = w.winfo_screenwidth(), w.winfo_screenheight()
            w.geometry(f"{width}x{height}+{max(0, (sw - width) // 2)}+{max(0, (sh - height) // 2 - 20)}")

    store = Store(base_dir)
    ip_blocked = ip_blocked or (lambda: False)
    own_open = open_url is not None   # 프로그램이 준 열기 함수는 IP 확인을 스스로 한다(정책뉴스)
    open_url = open_url or open_in_temp_chrome

    win = tk.Toplevel(parent)
    win.withdraw()
    win.title("🏁 경쟁 블로그 관리")
    center_window(win, 1240, 780)

    top = tk.Frame(win)
    top.pack(fill="x", padx=12, pady=(12, 4))
    tk.Label(top, text="블로그·게시글 주소:").pack(side="left")
    url_var = tk.StringVar()
    ent = ttk.Entry(top, textvariable=url_var, width=70)
    ent.pack(side="left", padx=6)
    status = tk.StringVar(value="블로그 주소(blog.naver.com/아이디)나 게시글 주소를 넣고 ➕ 등록을 누르세요.")
    tk.Label(win, textvariable=status, anchor="w", fg="#1d3a6e").pack(fill="x", padx=12)

    btns = tk.Frame(win)   # 트리 아래 버튼 줄 — 창 너비 전체(디자인 테마에서 버튼이 넓어져도 잘리지 않게)
    btns.pack(side="bottom", fill="x", padx=12, pady=(0, 12))
    pw = ttk.PanedWindow(win, orient="horizontal")
    pw.pack(fill="both", expand=True, padx=12, pady=6)
    left = ttk.Frame(pw)
    right = ttk.Frame(pw)
    pw.add(left, weight=3)
    pw.add(right, weight=2)

    tree = ttk.Treeview(left, columns=("info",), show="tree headings", selectmode="browse")
    tree.heading("#0", text="블로그 ▸ 게시글")
    tree.heading("info", text="정보")
    tree.column("#0", width=470)
    tree.column("info", width=200, anchor="w")
    vsb = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    ttk.Label(right, text="상세 정보").pack(anchor="w")
    detail = tk.Text(right, height=18, wrap="word")
    detail.pack(fill="both", expand=True)
    ttk.Label(right, text="비고(메모)").pack(anchor="w", pady=(8, 0))
    memo = tk.Text(right, height=6, wrap="word")
    memo.pack(fill="x")
    memo_btn = ttk.Button(right, text="💾 비고 저장")
    memo_btn.pack(anchor="e", pady=(4, 0))

    state = {"busy": False}

    def sel():
        s = tree.selection()
        if not s:
            return None, None
        iid = s[0]
        return (iid.split("|", 1) + [""])[:2] if "|" in iid else (iid, "")

    def fmt(v):
        return NOT_FOUND if v in (None, "", []) else (f"{v:,}" if isinstance(v, int) else str(v))

    def show():
        detail.config(state="normal")
        detail.delete("1.0", "end")
        memo.delete("1.0", "end")
        bid, lno = sel()
        blogs = store.load()
        b = blogs.get(bid) if bid else None
        if not b:
            detail.config(state="disabled")
            return
        lines = []
        if lno:
            p = b.get("posts", {}).get(lno, {})
            for k, label in POST_FIELDS:
                lines.append(f"{label}: {fmt(p.get(k))}")
            lines.append(f"MD 파일: {p.get('md_path') or '아직 추출 안 함'}")
            lines.append(f"수집한 날: {fmt(p.get('collected_at'))}")
            if p.get("notes"):
                lines += ["", "못 가져온 곳:"] + [f"  - {n}" for n in p["notes"]]
            memo.insert("1.0", p.get("memo", ""))
        else:
            for k, label in BLOG_FIELDS:
                v = fmt(b.get(k))
                if k == "open_date" and b.get("open_date_note") and b.get("open_date"):
                    v += f"  ({b['open_date_note']})"
                lines.append(f"{label}: {v}")
            cats = b.get("categories") or []
            lines.append(f"카테고리 목록: {len(cats)}개" if cats else f"카테고리 목록: {NOT_FOUND}")
            for c in cats:
                lines.append(f"  {'   └ ' if c.get('child') else '- '}{c['name']}"
                             + (f"  (글 {c['count']:,})" if isinstance(c.get("count"), int) else ""))
            lines.append(f"등록한 게시글: {len(b.get('posts', {}))}개")
            lines.append(f"수집한 날: {fmt(b.get('collected_at'))}")
            if b.get("notes"):
                lines += ["", "못 가져온 곳(Naver_blog_수집기록 폴더에 원본):"] + [f"  - {n}" for n in b["notes"]]
            memo.insert("1.0", b.get("memo", ""))
        detail.insert("1.0", "\n".join(lines))
        detail.config(state="disabled")

    def refresh(select=None):
        keep = select or (tree.selection()[0] if tree.selection() else None)
        tree.delete(*tree.get_children())
        blogs = store.load()
        for bid in sorted(blogs, key=lambda k: (blogs[k].get("blog_name") or k)):
            b = blogs[bid]
            name = b.get("blog_name") or bid
            if b.get("nickname"):
                name += f"  ({b['nickname']})"
            info = []
            if isinstance(b.get("today_visitors"), int):
                info.append(f"오늘 {b['today_visitors']:,}")
            if isinstance(b.get("post_count"), int):
                info.append(f"글 {b['post_count']:,}")
            tree.insert("", "end", iid=bid, text=name, values=(" · ".join(info),), open=True)
            posts = b.get("posts", {})
            for lno in sorted(posts, key=lambda k: posts[k].get("date") or "", reverse=True):
                p = posts[lno]
                tree.insert(bid, "end", iid=f"{bid}|{lno}", text=p.get("title") or lno,
                            values=(p.get("date") or "",))
        if keep and tree.exists(keep):
            tree.selection_set(keep)
            tree.see(keep)
        show()

    def run_bg(label, work, done):
        if state["busy"]:
            messagebox.showinfo("잠시만요", "앞의 작업이 끝난 뒤 다시 누르세요.", parent=win)
            return
        state["busy"] = True
        status.set(f"⏳ {label} 중…")
        box = {}

        def worker():
            try:
                box["r"] = work()
            except Exception as e:
                box["e"] = e

        th = threading.Thread(target=worker, daemon=True)
        th.start()

        def poll():
            if th.is_alive():
                win.after(200, poll)
                return
            state["busy"] = False
            if "e" in box:
                status.set(f"⚠ {label} 실패: {box['e']}")
                messagebox.showerror(label, f"{box['e']}", parent=win)
            else:
                done(box.get("r"))
        poll()

    def collect_and_save(bid, lno=""):
        """블로그 정보(+ 게시글 정보)를 모아 저장. 못 찾은 곳은 notes에."""
        info = collect_blog(bid, store.log_dir)
        pinfo = collect_post(bid, lno, store.log_dir) if lno else None

        def upd(b):
            posts = b.get("posts", {})
            memo_b = b.get("memo", "")
            # 이번에 못 찾은 칸은 지난 값을 남긴다(수집한 날·못 가져온 곳은 늘 새로)
            b.update({k: v for k, v in info.items() if v not in (None, "", []) or k in ("notes", "collected_at")})
            b["memo"], b["posts"] = memo_b, posts
            if pinfo:
                old = posts.get(lno, {})
                old.update({k: v for k, v in pinfo.items() if v not in (None, "") or k in ("notes", "collected_at")})
                posts[lno] = old
            return b
        store.update(bid, upd)
        return info, pinfo

    def report(res, bid, lno):
        info, pinfo = res
        miss = [label for k, label in BLOG_FIELDS if info.get(k) in (None, "", [])]
        if not info.get("categories"):
            miss.append("카테고리 목록")
        if pinfo:
            miss += [f"게시글 {label}" for k, label in POST_FIELDS if pinfo.get(k) in (None, "")]
        status.set("✅ 저장했습니다" + (f" — 못 찾은 칸: {', '.join(miss)} (Naver_blog_수집기록 폴더에 원본이 있습니다)"
                                      if miss else " — 모든 칸을 찾았습니다."))
        refresh(select=f"{bid}|{lno}" if lno else bid)

    def add():
        bid, lno = parse_url(url_var.get())
        if not bid:
            messagebox.showwarning("➕ 등록", "네이버 블로그 주소가 아닙니다.\n예) blog.naver.com/아이디  또는  "
                                   "blog.naver.com/아이디/글번호", parent=win)
            return
        if ip_blocked():
            return
        run_bg("정보 수집", lambda: collect_and_save(bid, lno),
               lambda r: (url_var.set(""), report(r, bid, lno)))

    def recollect():
        bid, lno = sel()
        if not bid:
            messagebox.showinfo("🔄 정보 다시 수집", "트리에서 블로그나 게시글을 먼저 고르세요.", parent=win)
            return
        if ip_blocked():
            return
        run_bg("정보 다시 수집", lambda: collect_and_save(bid, lno), lambda r: report(r, bid, lno))

    def do_md():
        bid, lno = sel()
        if not lno:
            messagebox.showinfo("📄 MD 파일 추출", "트리에서 게시글을 먼저 고르세요(블로그 아래 줄).", parent=win)
            return
        try:
            import selenium  # noqa: F401
        except Exception:
            messagebox.showerror("📄 MD 파일 추출", "selenium이 없습니다 — 명령 프롬프트에서 pip install selenium", parent=win)
            return
        if ip_blocked():
            return
        b = store.load().get(bid, {})
        out_dir = store.md_dir(b)
        hint = b.get("posts", {}).get(lno, {}).get("title") or ""

        def done(path):
            store.update(bid, lambda x: (x["posts"].setdefault(lno, {}).update(md_path=path), x)[1])
            status.set(f"✅ MD 저장: {path}")
            refresh(select=f"{bid}|{lno}")
        run_bg("MD 파일 추출", lambda: extract_md(bid, lno, out_dir, hint), done)

    def do_open():
        bid, lno = sel()
        if not bid:
            messagebox.showinfo("🌐 열기", "트리에서 블로그나 게시글을 먼저 고르세요.", parent=win)
            return
        if not own_open and ip_blocked():
            return
        open_url(post_url(bid, lno) if lno else blog_url(bid))

    def open_folder():
        bid, _ = sel()
        b = store.load().get(bid) if bid else None
        path = store.md_dir(b) if b else store.dir
        if not os.path.isdir(path):
            path = store.dir
        os.makedirs(path, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                os.startfile(os.path.abspath(path))
            else:
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("📂 MD 폴더 열기", f"{path}\n{e}", parent=win)

    def remove():
        bid, lno = sel()
        if not bid:
            return
        b = store.load().get(bid, {})
        what = (b.get("posts", {}).get(lno, {}).get("title") or lno) if lno else (b.get("blog_name") or bid)
        extra = "" if lno else f"\n이 블로그의 게시글 {len(b.get('posts', {}))}개도 목록에서 빠집니다."
        if not messagebox.askyesno("🗑 목록에서 빼기", f"{what}\n\n목록에서 뺄까요?{extra}\n(추출한 MD 파일은 지우지 않습니다)",
                                   parent=win):
            return
        if lno:
            store.update(bid, lambda x: (x["posts"].pop(lno, None), x)[1])
            refresh(select=bid)
        else:
            store.update(bid, lambda x: None)
            refresh()

    def save_memo():
        bid, lno = sel()
        if not bid:
            messagebox.showinfo("💾 비고 저장", "트리에서 블로그나 게시글을 먼저 고르세요.", parent=win)
            return
        text = memo.get("1.0", "end").rstrip()

        def upd(x):
            if lno:
                x["posts"].setdefault(lno, {})["memo"] = text
            else:
                x["memo"] = text
            return x
        store.update(bid, upd)
        status.set("✅ 비고를 저장했습니다.")

    ttk.Button(top, text="➕ 등록", command=add).pack(side="left")
    ent.bind("<Return>", lambda e: add())
    for txt, cmd in (("🔄 정보 다시 수집", recollect), ("📄 MD 파일 추출", do_md), ("🌐 열기", do_open),
                     ("📂 MD 폴더 열기", open_folder)):
        ttk.Button(btns, text=txt, command=cmd).pack(side="left", padx=(0, 6))
    ttk.Button(btns, text="🗑 목록에서 빼기", command=remove).pack(side="right")
    memo_btn.configure(command=save_memo)
    tree.bind("<<TreeviewSelect>>", lambda e: show())

    refresh()
    win.deiconify()
    win.lift()
    ent.focus_set()
    return win
