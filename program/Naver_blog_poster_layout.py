# -*- coding: utf-8 -*-
"""
Naver_blog_poster_layout.py — 포스팅 프로그램(blog_poster.py) 화면 배치·디자인 (2026-10-15)

[하는 일] 프로그램이 화면을 다 만든 뒤 apply(gui)를 한 번 부르면 겉모습과 자리만 바꾼다.
  - 위쪽 탭 줄 → 왼쪽 메뉴(기능별 묶음). 흩어져 있던 칸을 기능별 화면(페이지)으로 다시 놓는다.
  - 색·카드는 Naver_blog_ui_theme.py(복지로·정책뉴스와 같은 디자인).

[반드시 지킬 규칙]
  - 위젯을 새로 만들거나 지우지 않는다. 이미 있는 칸을 다른 자리에 "놓기만" 한다(grid in_).
    버튼이 하는 일·글자·설정값 변수·포스팅 엔진(NaverBlogPoster)은 건드리지 않는다.
  - Tk 규칙상 칸은 자기 부모(원래 탭) 안에서만 옮길 수 있다 → 원래 탭이 달라도 메뉴는 기능별로 묶는다
    (메뉴를 누르면 그 칸이 있는 탭을 고르고 해당 페이지를 보여 준다).
  - 칸을 찾지 못하면(프로그램 화면이 바뀌었으면) 아무것도 옮기지 않고 색만 입힌다. 이 파일이 없거나
    오류가 나면 부르는 쪽(try)이 지금 화면으로 실행한다.
  - 옮긴 칸은 lift()로 새 페이지 위에 올린다(안 하면 페이지에 가려진다).
"""

import tkinter as tk
from tkinter import ttk

import Naver_blog_ui_theme as ui_theme
from Naver_blog_ui_theme import CARD, PAGE, LINE, SIDE, SIDE_SEL, SIDE_TEXT, SIDE_DIM, SUB, TEXT, DOT, FONT, _safe

ACCENT = "#3B4BA8"      # 포스팅 프로그램 대표색(정책뉴스 네이비·복지로 틸과 구분)
ACCENT2 = "#F2A93B"
SIDEBAR_W = 200

# 메뉴: (묶음, [(메뉴 이름, 탭 키, 페이지 키 또는 None)])
MENU = [
    ("실행", [("▶  포스팅 실행", "tab1", "run")]),
    ("계정·환경", [("👤  계정·네트워크", "tab1", "account")]),
    ("글 꾸미기", [("✏️  소제목·본문 서식", "tab2", "body"),
                ("🏷  로고·마무리 문구", "tab2", "logo"),
                ("🔤  폰트·이미지 ALT", "tab2", "font"),
                ("🔗  내부링크·동영상", "tab1", "tail"),
                ("▦  표 설정", "table", None)]),
    ("이미지·썸네일", [("🖼  썸네일 위치·제목 강조", "tab1", "thumb"),
                  ("🎨  썸네일 글자색", "tab2", "thumbcolor"),
                  ("🧩  썸네일 모드·프레임", "tab5", None),
                  ("🔁  썸네일 재생성", "rethumb", None)]),
    ("점검", [("🔎  블로그 누락 확인", "tab6", None)]),
    ("API 자동화 (보류)", [("AI 모델 및 프롬프트", "tab3", None),
                        ("외부 프롬프트", "ext", None)]),
]

# 옛 탭 이름을 가리키던 안내 문구 → 새 메뉴 이름 (글자만 바꿈)
HINT_REPLACE = [("[포스팅 스타일] 탭", "[썸네일 글자색] 메뉴"),
                ("[썸네일 설정] 탭", "[썸네일 모드·프레임] 메뉴"),
                ("[기본 설정] 탭", "[썸네일 위치·제목 강조] 메뉴")]


class LayoutError(Exception):
    pass


def _text(w):
    try:
        return str(w.cget("text"))
    except tk.TclError:
        return ""


def _first_label(w):
    """줄(프레임) 안 첫 글자 — 줄을 알아보는 이름표."""
    for c in w.winfo_children():
        t = _text(c).strip()
        if t:
            return t
    return ""


def _walk(w):
    stack = [w]
    while stack:
        x = stack.pop()
        yield x
        stack.extend(x.winfo_children())


class _Layout:
    def __init__(self, gui):
        self.gui = gui
        self.root = gui.root
        self.nb = gui.notebook
        self.th = None
        self.pages = {}        # (탭 키, 페이지 키) → 페이지 프레임
        self.tab_pages = {}    # 탭 키 → [페이지들]
        self.menu_labels = []  # (메뉴 라벨, 탭 키, 페이지 키)
        self.current = None

    # ---------- 찾기(옮기기 전에 전부 찾는다 — 하나라도 못 찾으면 옮기지 않음) ----------
    def find_tabs(self):
        g = self.gui
        tabs = {"tab1": g.tab1, "tab2": g.tab2, "tab3": g.tab3, "tab5": g.tab5, "tab6": g.tab6}
        by_text = {str(self.nb.tab(t, "text")).strip(): self.root.nametowidget(t) for t in self.nb.tabs()}
        for key, name in (("ext", "외부 프롬프트"), ("table", "표 설정"), ("rethumb", "썸네일 재생성")):
            if name not in by_text:
                raise LayoutError(f"탭 없음: {name}")
            tabs[key] = by_text[name]
        self.tabs = tabs

    def _child(self, parent, *, lf=None, row=None):
        for c in parent.winfo_children():
            if lf is not None and c.winfo_class() == "TLabelframe" and _text(c).startswith(lf):
                return c
            if row is not None and c.winfo_class() in ("TFrame", "Frame") and _first_label(c).startswith(row):
                return c
        raise LayoutError(f"칸 없음: {lf or row} ({parent})")

    def find_widgets(self):
        t1, t2 = self.tabs["tab1"], self.tabs["tab2"]
        f = {}
        f["account"] = self._child(t1, lf="계정 정보")
        f["auto"] = auto = self._child(t1, lf="자동 포스팅 설정")
        f["ip"] = self._child(t1, lf="네트워크 IP 체크")
        for k, txt in (("publish", "게시물 발행 방식"), ("time", "포스팅 가능 시간대"), ("progress", "진행률"),
                       ("sched", "예약발행 진행 상태"), ("content", "콘텐츠 작성 방식"), ("mdfolder", "마크다운 폴더"),
                       ("thumbpos", "썸네일 위치"), ("links", "하단에 내부링크"), ("video", "하단 동영상")):
            f[k] = self._child(auto, row=txt)
        f["emph"] = self._child(auto, lf="썸네일 타이틀 강조")
        # 파일 두 줄(라벨·입력칸·버튼이 auto_frame에 바로 있음): grid 0·1행
        files = {0: [], 1: []}
        for c in auto.winfo_children():
            if c.winfo_manager() == "grid":
                r = int(c.grid_info().get("row", -1))
                if r in files:
                    files[r].append(c)
        if len(files[0]) != 3 or len(files[1]) != 3:
            raise LayoutError("파일 선택 줄 모양이 다름")
        f["files"] = files
        # 포스팅 스타일 탭
        f["logo_lf"] = self._child(t2, lf="블로그 로고 설정")
        f["closing_lf"] = self._child(t2, lf="마무리 문구 설정")
        f["thumbcolor_lf"] = self._child(t2, lf="썸네일 글자색 설정")
        f["font_lf"] = self._child(t2, lf="블로그 포스팅에 사용할 폰트")
        f["alt_lf"] = self._child(t2, lf="이미지 ALT 텍스트 설정")
        for k, txt in (("logo_pos", "블로그 로고 텍스트 위치"), ("logo_style", "로고 스타일"),
                       ("logo_size", "로고 폰트 크기"), ("logo_color", "로고 색상"),
                       ("emoji", "소제목에 이모지"), ("quote", "소제목 인용구 스타일"), ("sticker", "스티커 사용 여부"),
                       ("bold_fg", "볼드체 글자색만"), ("bold_bg", "볼드체 배경색"),
                       ("emph_bg", "[[강조:]]"), ("caution_bg", "[[주의:]]")):
            f[k] = self._child(t2, row=txt)
        # 아래쪽: 키워드 목록·작업 로그(status_frame), 버튼 줄(button_frame)
        mf = self.nb.master
        status = [c for c in mf.winfo_children() if c.winfo_class() == "TFrame" and "키워드 목록" in
                  [_text(x) for x in c.winfo_children()]]
        if len(status) != 1:
            raise LayoutError("키워드 목록·작업 로그 칸 없음")
        f["status"] = status[0]
        f["buttons"] = self.gui.auto_button.master
        # 빠짐없이 옮기는지 확인 — 탭1·탭2·auto_frame의 모든 자식이 위에서 찾은 것이어야 한다
        used = {str(w) for k, w in f.items() if k not in ("files",)} | \
               {str(w) for r in files.values() for w in r}
        for parent in (t1, t2, auto):
            for c in parent.winfo_children():
                if str(c) not in used and c is not auto:
                    raise LayoutError(f"자리를 정하지 않은 칸: {c} {_first_label(c) or _text(c)}")
        self.w = f

    # ---------- 놓기 ----------
    def _page(self, tab_key, page_key, parent):
        p = ttk.Frame(parent, style="UiPage.TFrame", padding=(14, 10))
        self.th.done.add(str(p))
        self.pages[(tab_key, page_key)] = p
        self.tab_pages.setdefault(tab_key, []).append(p)
        p.columnconfigure(0, weight=1)
        return p

    def _card(self, page, title, row):
        c = ttk.LabelFrame(page, text=title, padding=(10, 6))
        self.th.done.add(str(c))
        c.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        c.columnconfigure(1, weight=1)
        return c

    def _put(self, w, container, row, col=0, colspan=3, sticky="w", **kw):
        w.grid(in_=container, row=row, column=col, columnspan=colspan, sticky=sticky,
               padx=kw.get("padx", 2), pady=kw.get("pady", 2))
        w.lift()

    def _put_card_row(self, w, card, row):
        self._put(w, card, row)
        self._card_paint(w)

    def _card_paint(self, w):
        """카드 안으로 옮긴 칸을 흰 바탕으로(원래 부모가 카드가 아니라 회색으로 칠해진 것)."""
        th = self.th
        for x in _walk(w):
            cls = x.winfo_class()
            try:
                if cls in ("TFrame", "TLabel", "TCheckbutton", "TRadiobutton"):
                    cur = str(x.cget("style"))
                    if not cur.startswith("Card."):
                        x.configure(style=th._derived("Card", cur, cls))
                elif cls in ("Frame", "Label", "Checkbutton", "Radiobutton", "Canvas", "Scale"):
                    if str(x.cget("background")) in (th.tk_default_bg, PAGE):
                        x.configure(background=CARD)
                        if cls in ("Checkbutton", "Radiobutton", "Scale"):
                            x.configure(highlightbackground=CARD)
                        if cls in ("Checkbutton", "Radiobutton"):
                            x.configure(activebackground=CARD)
            except tk.TclError:
                pass
            th.done.add(str(x))

    def build_pages(self):
        w, t1, t2 = self.w, self.tabs["tab1"], self.tabs["tab2"]
        auto = w["auto"]
        # 탭1: auto_frame을 탭 전체를 채우는 투명한 틀로 쓰고, 그 안에 페이지를 만든다
        #      (auto_frame 줄은 auto_frame 안에서만, 계정·IP 칸은 탭1 안에서만 옮길 수 있으므로)
        auto.configure(text="", style="UiPlain.TLabelframe", padding=0)
        auto.grid_configure(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
        t1.rowconfigure(0, weight=1)
        t1.columnconfigure(0, weight=1)
        for r in range(0, 20):
            auto.rowconfigure(r, weight=0)
        auto.rowconfigure(0, weight=1)
        auto.columnconfigure(0, weight=1)

        # ▶ 포스팅 실행
        run = self._page("tab1", "run", auto)
        c = self._card(run, "📁 파일·폴더", 0)
        for r, row in w["files"].items():
            lab, ent, btn = sorted(row, key=lambda x: int(x.grid_info()["column"]))
            self._put(lab, c, r, 0, 1)
            self._put(ent, c, r, 1, 1, sticky="ew")
            self._put(btn, c, r, 2, 1)
            for x in (lab, ent, btn):
                self._card_paint(x)
        self._put_card_row(w["mdfolder"], c, 2)
        c = self._card(run, "📝 콘텐츠 작성 방식", 1)
        self._put_card_row(w["content"], c, 0)
        c = self._card(run, "⏰ 발행 일정", 2)
        self._put_card_row(w["publish"], c, 0)
        self._put_card_row(w["time"], c, 1)
        c = self._card(run, "📊 진행", 3)
        self._put_card_row(w["progress"], c, 0)
        self._put_card_row(w["sched"], c, 1)
        self._put(w["status"], run, 4, sticky="ew", pady=(0, 0))

        # 👤 계정·네트워크
        acc = self._page("tab1", "account", auto)
        self._put(w["account"], acc, 0, sticky="ew", pady=(0, 10))
        self._put(w["ip"], acc, 1, sticky="ew")

        # 🔗 내부링크·동영상
        tail = self._page("tab1", "tail", auto)
        c = self._card(tail, "🔗 글 끝부분 — 내부링크·요약 동영상", 0)
        self._put_card_row(w["links"], c, 0)
        self._put_card_row(w["video"], c, 1)

        # 🖼 썸네일 위치·제목 강조
        th_page = self._page("tab1", "thumb", auto)
        c = self._card(th_page, "🖼 썸네일·소제목 이미지 배치", 0)
        self._put_card_row(w["thumbpos"], c, 0)
        self._put(w["emph"], th_page, 1, sticky="ew")

        # 탭2: 페이지는 탭2 바로 아래
        t2.rowconfigure(0, weight=1)
        t2.columnconfigure(0, weight=1)
        body = self._page("tab2", "body", t2)
        c = self._card(body, "✏️ 소제목", 0)
        for i, k in enumerate(("emoji", "quote", "sticker")):
            self._put_card_row(w[k], c, i)
        c = self._card(body, "🖍 본문 강조(볼드·강조·주의)", 1)
        for i, k in enumerate(("bold_fg", "bold_bg", "emph_bg", "caution_bg")):
            self._put_card_row(w[k], c, i)

        logo = self._page("tab2", "logo", t2)
        self._put(w["logo_lf"], logo, 0, sticky="ew", pady=(0, 10))
        c = self._card(logo, "🏷 로고 모양", 1)
        for i, k in enumerate(("logo_pos", "logo_style", "logo_size", "logo_color")):
            self._put_card_row(w[k], c, i)
        self._put(w["closing_lf"], logo, 2, sticky="ew")

        font = self._page("tab2", "font", t2)
        self._put(w["font_lf"], font, 0, sticky="ew", pady=(0, 10))
        self._put(w["alt_lf"], font, 1, sticky="ew")

        tc = self._page("tab2", "thumbcolor", t2)
        self._put(w["thumbcolor_lf"], tc, 0, sticky="ew")

        for (tab_key, _k), p in self.pages.items():
            p.grid(row=0, column=0, sticky="nsew")
            p.grid_remove()

        # 아래 버튼 줄: 실행 버튼은 왼쪽, 크롬 관리 버튼은 오른쪽 (같은 줄 안에서만 옮김)
        btn_frame = w["buttons"]
        btn_frame.grid_configure(sticky="ew", padx=10, pady=(6, 8))
        g = self.gui
        for b in (g.special_chrome_button, g.sync_chrome_button, g.clear_session_button):
            b.pack_configure(side=tk.RIGHT)
        # 순서: 오른쪽은 나중에 pack한 것이 안쪽 — 원래 순서대로 보이게 다시 쌓는다
        for b in (g.clear_session_button, g.sync_chrome_button, g.special_chrome_button):
            b.pack_forget()
            b.pack(side=tk.RIGHT, padx=4)

        # 옛 탭 이름 안내 → 새 메뉴 이름
        for x in _walk(self.root):
            if x.winfo_class() in ("TLabel", "Label"):
                t = _text(x)
                if t.startswith("※") and "] 탭" in t:
                    for a, b in HINT_REPLACE:
                        t = t.replace(a, b)
                    x.configure(text=t)

    # ---------- 머리줄 · 왼쪽 메뉴 ----------
    def build_frame(self):
        root, g = self.root, self.gui
        slaves = root.grid_slaves()
        for s in slaves:
            s.grid_configure(row=1, column=1)
        root.rowconfigure(0, weight=0)
        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=0, minsize=SIDEBAR_W)
        root.columnconfigure(1, weight=1)
        root.configure(padx=0, pady=0, background=PAGE)

        head = tk.Frame(root, background=CARD, height=52)
        head.grid(row=0, column=0, columnspan=2, sticky="ew")
        head.pack_propagate(False)
        tk.Frame(head, background=ACCENT, width=6).pack(side="left", fill="y")
        tk.Label(head, text="포스팅 관리", font=(FONT, 14, "bold"), bg=CARD, fg=SIDE).pack(side="left", padx=(14, 8))
        tk.Label(head, text="완성 MD → 네이버 블로그 발행", font=(FONT, 9), bg=CARD, fg=SUB).pack(
            side="left", pady=(6, 0))
        chips = [("네이버 아이디", lambda: ("입력됨", "green") if g.naver_id_entry.get().strip() else ("필요", "red")),
                 ("키워드 파일", lambda: self._path_chip(g.keyword_file_path.get())),
                 ("MD 폴더", lambda: self._path_chip(g.md_folder_path.get())),
                 ("휴먼 활동", lambda: ("켜짐", "green") if g.use_human_activity.get() else ("꺼짐", "gray"))]
        self.th.chip_labels = []
        for label, fn in reversed(chips):
            chip = tk.Frame(head, bg=CARD, highlightthickness=1, highlightbackground=LINE)
            chip.pack(side="right", padx=(0, 10), pady=11)
            tk.Label(chip, text=label, font=(FONT, 9), bg=CARD, fg=SUB).pack(side="left", padx=(10, 4))
            dot = tk.Label(chip, text="●", font=(FONT, 9), bg=CARD, fg=DOT["gray"])
            dot.pack(side="left")
            val = tk.Label(chip, text="-", font=(FONT, 9, "bold"), bg=CARD, fg=TEXT)
            val.pack(side="left", padx=(3, 10), pady=3)
            self.th.chip_labels.append((fn, dot, val))
        self.th.chip_labels.reverse()

        side = tk.Frame(root, background=SIDE, width=SIDEBAR_W)
        side.grid(row=1, column=0, sticky="ns")
        side.pack_propagate(False)
        tk.Frame(side, bg=ACCENT2, height=4).pack(fill="x")
        for group, items in MENU:
            tk.Label(side, text=group, font=(FONT, 8, "bold"), bg=SIDE, fg=SIDE_DIM).pack(
                anchor="w", padx=18, pady=(10, 2))
            for name, tab_key, page_key in items:
                b = tk.Label(side, text=name, anchor="w", font=(FONT, 10), bg=SIDE, fg=SIDE_TEXT,
                             padx=12, pady=5, cursor="hand2")
                b.pack(fill="x", padx=8, pady=0)
                b.bind("<Button-1>", lambda e, t=tab_key, p=page_key, b=b: self.show(t, p))
                b.bind("<Enter>", lambda e, b=b: b is not self.current and b.configure(bg="#2A3A5C"))
                b.bind("<Leave>", lambda e, b=b: b is not self.current and b.configure(bg=SIDE))
                self.menu_labels.append((b, tab_key, page_key))
        ver = ""
        try:
            import re
            m = re.search(r"Ver\s*([0-9.]+)", str(root.title()))
            ver = f"Ver{m.group(1)}" if m else ""
        except Exception:
            pass
        tk.Label(side, text=f"포스팅 관리 {ver}".strip(), font=(FONT, 8), bg=SIDE, fg=SIDE_DIM).pack(
            side="bottom", anchor="w", padx=18, pady=10)

        self.th.style.layout("UiHidden.TNotebook.Tab", [])
        self.th.style.configure("UiHidden.TNotebook", background=PAGE, borderwidth=0, tabmargins=0)
        self.th.style.layout("UiHidden.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
        self.nb.configure(style="UiHidden.TNotebook")
        self.nb.master.rowconfigure(0, weight=1)

    @staticmethod
    def _path_chip(p):
        import os
        p = (p or "").strip()
        if not p:
            return ("미지정", "red")
        return ("확인됨", "green") if os.path.exists(p) else ("경로 없음", "orange")

    def show(self, tab_key, page_key):
        self.nb.select(self.tabs[tab_key])
        for p in self.tab_pages.get(tab_key, []):
            p.grid_remove()
        if page_key:
            self.pages[(tab_key, page_key)].grid()
        for b, t, p in self.menu_labels:
            on = (t == tab_key and p == page_key)
            b.configure(bg=SIDE_SEL if on else SIDE, fg="#FFFFFF" if on else SIDE_TEXT,
                        font=(FONT, 10, "bold" if on else "normal"))
            if on:
                self.current = b

    def styles(self):
        s, g = self.th.style, self.gui
        # 포스팅 프로그램이 정해 둔 글꼴(나눔고딕 11 굵게)을 그대로 — 칸 크기가 바뀌지 않게
        for name in ("TLabel", "TEntry", "TButton"):
            s.configure(name, font=g.default_font)
        s.configure("Title.TLabel", font=g.title_font)
        s.configure("Big.TLabelframe.Label", font=(FONT, 11, "bold"), foreground=ACCENT, background=PAGE)
        s.configure("TLabelframe.Label", font=(FONT, 11, "bold"), foreground=ACCENT, background=PAGE)
        s.configure("UiPage.TFrame", background=PAGE)
        s.configure("UiPlain.TLabelframe", background=PAGE, borderwidth=0, relief="flat")
        s.configure("UiPlain.TLabelframe.Label", background=PAGE)

    def size_window(self):
        """창이 처음 뜨기 전에 크기를 정한다(뜬 뒤에 바꾸면 화면이 한 번 깜빡인다).
        아직 안 뜬 창은 winfo_width가 1이라, 각 칸이 원하는 크기(reqwidth)로 계산한다."""
        r = self.root
        r.update_idletasks()
        r.resizable(True, True)
        sw, sh = r.winfo_screenwidth(), r.winfo_screenheight()
        page_w = max([p.winfo_reqwidth() for p in self.pages.values()] + [0])
        need_w = max(r.winfo_reqwidth(), SIDEBAR_W + page_w + 60, 1100 + SIDEBAR_W) + 10
        need_h = max(r.winfo_reqheight() + 10, 990)
        new_w, new_h = min(need_w, sw - 10), min(need_h, sh - 80)
        r.geometry(f"{new_w}x{new_h}+{max(0, (sw - new_w) // 2)}+{max(0, (sh - 80 - new_h) // 2)}")


def apply(gui):
    """blog_poster.py의 NaverBlogGUI가 화면을 다 만든 뒤 한 번 부른다. 실패해도 예외를 내지 않는다."""
    lay = _Layout(gui)
    try:
        lay.find_tabs()
        lay.find_widgets()          # 옮기기 전에 전부 찾는다
        ok = True
    except Exception as e:  # noqa: BLE001
        print(f"[디자인] 칸 배치는 하지 않음(지금 배치 + 색만): {e}")
        ok = False
    lay.th = ui_theme.apply(gui.root, gui.notebook, "포스팅 관리", accent=ACCENT, accent2=ACCENT2,
                            frame=False)
    if lay.th is None:
        return None
    _safe(lay.styles)
    if not ok:
        return lay
    lay.build_pages()
    lay.build_frame()
    _safe(lay.th.refresh_chips)
    lay.show("tab1", "run")
    _safe(lay.size_window)          # 창이 뜨기 전에 — 뜬 뒤 크기를 바꾸면 깜빡인다
    return lay
