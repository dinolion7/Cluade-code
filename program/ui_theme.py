# -*- coding: utf-8 -*-
"""
ui_theme.py — 복지로·정책뉴스 관리 프로그램 공용 화면 디자인 (2026-10-15)

[하는 일] 프로그램이 화면을 다 만든 뒤 apply()를 한 번 부르면 겉모습만 바꾼다.
  - 위쪽 탭 줄을 숨기고 왼쪽 메뉴로 보여 준다(탭은 그대로 있어 기존 탭 이동 코드가 그대로 동작).
  - 위쪽 머리줄: 프로그램 이름 + 상태 점(빨강 필요 / 주황 확인 전 / 초록 정상 / 회색 안 씀).
  - 단계 칸(LabelFrame)은 흰 카드, 바탕은 연회색, 칸 제목은 대표색.
  - 버튼 색은 이름 첫 글자로 정한다: 📋 복사 파랑 · 💾 저장 초록 · ✅ 확정 대표색 · ⏭ 패스 회색.

[반드시 지킬 규칙]
  - 버튼이 하는 일·글자·배치는 건드리지 않는다. 색·글꼴·테두리만 바꾼다.
  - 이 파일이 없거나 apply()에서 오류가 나도 프로그램은 지금 모습으로 실행된다(부르는 쪽 try,
    apply 안에서도 단계마다 실패를 삼킨다).
  - 프로그램이 원래 쓰던 스타일(Copy.TButton·Info.TLabel 등)은 그 스타일을 이어받은 새 이름으로
    색만 더한다(글꼴·굵기는 원래 것).
"""

import re
import tkinter as tk
from tkinter import ttk

FONT = "맑은 고딕"
PAGE = "#E9EDF3"      # 바탕(카드와 구분되게 조금 진하게)
CARD = "#FFFFFF"      # 카드
LINE = "#C3CCD8"      # 테두리
TEXT = "#111827"     # 본문 글자(거의 검정 — 흐리면 안 보임)
SUB = "#46505C"      # 보조 글자(안내·설명)
SIDE = "#1E2A44"      # 왼쪽 메뉴
SIDE_SEL = "#2F6FB0"
SIDE_TEXT = "#DCE3EE"
SIDE_DIM = "#8EA0BC"
ROLE_COLORS = {"Copy": "#2F6FB0", "Save": "#1F8A5B", "Pass": "#8A94A3"}  # Ok는 대표색
DOT = {"red": "#D64545", "orange": "#E08A1E", "green": "#1F9D55", "gray": "#9AA5B4"}
SIDEBAR_W = 190
# 밝은 바탕에서 흐리게 보이는 안내 글자색 → SUB로 바꾼다(글자만, 색 이름 그대로 비교)
LIGHT_GRAYS = {"gray", "grey", "darkgray", "darkgrey", "#777777", "#777", "#808080", "#888888", "#888",
               "#999999", "#999", "#8a8a8a", "#7f7f7f", "#a0a0a0", "#aaaaaa", "#666666", "#666", "#6b7684"}


def _walk(w):
    stack = [w]
    while stack:
        x = stack.pop()
        yield x
        try:
            stack.extend(x.winfo_children())
        except tk.TclError:
            pass


def _safe(fn):
    """한 단계가 실패해도 나머지 디자인과 프로그램은 계속 가게 한다."""
    try:
        fn()
        return True
    except Exception as e:  # noqa: BLE001 — 디자인은 동작보다 중요하지 않다
        print(f"[디자인] 일부 적용 안 함: {e}")
        return False


class _Theme:
    def __init__(self, root, notebook, title, subtitle, accent, accent2, chips):
        self.root = root
        self.nb = notebook
        self.title = title
        self.subtitle = subtitle
        self.accent = accent
        self.accent2 = accent2
        self.chips = chips or []
        self.done = set()          # 이미 색을 입힌 위젯 경로
        self.made_styles = set()
        self.pending = False
        self.style = ttk.Style(root)
        # 테마를 바꾸기 전 tk 기본 바탕색(Windows: SystemButtonFace) — 이 색인 위젯만 바꾼다
        probe = tk.Frame(root)
        self.tk_default_bg = str(probe.cget("background"))
        probe.destroy()

    # ---------------- 스타일 ----------------
    def setup_styles(self):
        s = self.style
        # 테마를 바꾸면 프로그램이 정해 둔 스타일(굵은 글씨·회색 안내 등)이 사라지므로 먼저 적어 두었다가 되살린다
        keep = {}
        names = {"Header.TLabel", "Info.TLabel", "Copy.TButton", "Save.TButton"}
        for w in _walk(self.root):
            try:
                st = str(w.cget("style"))
            except tk.TclError:
                continue
            if st:
                names.add(st)
        for name in names:
            try:
                keep[name] = (s.configure(name) or {}, s.map(name) or {})
            except tk.TclError:
                pass
        s.theme_use("clam")
        base = (FONT, 10)
        s.configure(".", background=PAGE, foreground=TEXT, font=base, bordercolor=LINE,
                    lightcolor=PAGE, darkcolor=PAGE, troughcolor="#E6EAF0")
        s.configure("TFrame", background=PAGE)
        s.configure("TLabel", background=PAGE, foreground=TEXT)
        s.configure("TLabelframe", background=CARD, bordercolor=LINE, relief="solid", borderwidth=1)
        s.configure("TLabelframe.Label", background=PAGE, foreground=self.accent, font=(FONT, 11, "bold"))
        s.configure("TButton", background=CARD, foreground=TEXT, bordercolor=LINE, lightcolor=CARD,
                    darkcolor=CARD, padding=(6, 3), relief="flat")
        s.map("TButton", background=[("disabled", "#F1F3F6"), ("active", "#EAF0F7")],
              foreground=[("disabled", "#7C8794")])
        s.configure("TCheckbutton", background=PAGE)
        s.configure("TRadiobutton", background=PAGE)
        s.map("TCheckbutton", background=[("active", PAGE)])
        s.map("TRadiobutton", background=[("active", PAGE)])
        s.configure("TEntry", fieldbackground="#FFFFFF", bordercolor=LINE, lightcolor="#FFFFFF", padding=3)
        s.configure("TCombobox", fieldbackground="#FFFFFF", bordercolor=LINE, lightcolor="#FFFFFF",
                    arrowsize=13, padding=2)
        s.map("TCombobox", fieldbackground=[("readonly", "#FFFFFF")],
              selectbackground=[("readonly", "#FFFFFF")], selectforeground=[("readonly", TEXT)])
        s.configure("TSpinbox", fieldbackground="#FFFFFF", bordercolor=LINE)
        s.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground=TEXT,
                    rowheight=26, bordercolor=LINE, font=base)
        s.configure("Treeview.Heading", background="#DFE5EE", foreground=TEXT, font=(FONT, 10, "bold"),
                    relief="flat", bordercolor=LINE)
        s.map("Treeview.Heading", background=[("active", "#E3E9F1")])
        s.map("Treeview", background=[("selected", "#D6E6F8")], foreground=[("selected", TEXT)])
        s.configure("TProgressbar", background=self.accent, troughcolor="#E6EAF0", bordercolor=LINE)
        s.configure("TPanedwindow", background=PAGE)
        s.configure("Sash", sashthickness=6, gripcount=0, background=PAGE)
        s.configure("TScrollbar", background="#E6EAF0", troughcolor=PAGE, bordercolor=PAGE,
                    arrowcolor=SUB, lightcolor="#E6EAF0", darkcolor="#E6EAF0")
        s.configure("TSeparator", background=LINE)
        # 프로그램이 정해 둔 스타일 되살리기(바탕색은 새 디자인 것으로)
        for name, (conf, mp) in keep.items():
            conf = {k: v for k, v in conf.items() if k not in ("background", "lightcolor", "darkcolor",
                                                                "bordercolor", "fieldbackground")}
            if name.startswith("TNotebook"):
                continue
            try:
                if conf:
                    s.configure(name, **conf)
                mp = {k: v for k, v in mp.items() if k != "background"}
                if mp:
                    s.map(name, **mp)
            except tk.TclError:
                pass
        s.configure("Header.TLabel", background=PAGE)
        s.configure("Info.TLabel", background=PAGE, foreground=SUB)
        s.layout("UiHidden.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
        self.root.configure(background=PAGE)

    def _derived(self, prefix, cur, kind):
        """원래 스타일(cur)을 이어받은 새 스타일 이름. 예: Card. + Info.TLabel"""
        base = cur if cur else kind
        name = f"{prefix}.{base}"
        if name not in self.made_styles:
            self.made_styles.add(name)
            s = self.style
            if prefix == "Card":
                s.configure(name, background=CARD)
                if kind in ("TCheckbutton", "TRadiobutton"):
                    s.map(name, background=[("active", CARD)])
            else:  # 버튼 역할 색
                col = self.accent if prefix == "UiOk" else ROLE_COLORS[prefix[2:]]
                kw = dict(background=col, foreground="#FFFFFF", bordercolor=col, lightcolor=col,
                          darkcolor=col)
                if not cur:
                    kw["font"] = (FONT, 10, "bold")
                s.configure(name, **kw)
                s.map(name, background=[("disabled", "#C9D2DE"), ("active", col)],
                      foreground=[("disabled", "#F4F6F9")])
        return name

    # ---------------- 위젯별 색 ----------------
    def _in_card(self, w):
        p = w.master
        while p is not None:
            try:
                cls = p.winfo_class()
            except tk.TclError:
                return False
            if cls == "TLabelframe":
                return True
            if cls in ("Toplevel", "Tk"):
                return False
            p = p.master
        return False

    def _darken_fg(self, w):
        """프로그램이 안내 글에 쓴 연한 회색(gray·#777 등)은 밝은 바탕에서 잘 안 보여 진한 회색으로."""
        try:
            fg = str(w.cget("foreground")).strip().lower()
        except tk.TclError:
            return
        if fg in LIGHT_GRAYS:
            w.configure(foreground=SUB)

    def _paint(self, w):
        cls = w.winfo_class()
        if cls in ("TLabel", "Label", "TCheckbutton", "Checkbutton", "Radiobutton", "TRadiobutton"):
            self._darken_fg(w)
        if cls in ("TFrame", "TLabel", "TCheckbutton", "TRadiobutton"):
            cur = str(w.cget("style"))
            if self._in_card(w) and not cur.startswith("Card."):
                w.configure(style=self._derived("Card", cur, cls))
        elif cls == "TButton":
            cur = str(w.cget("style"))
            if cur in ("", "TButton", "Copy.TButton", "Save.TButton"):
                t = str(w.cget("text")).lstrip()
                role = ("UiCopy" if t.startswith("📋") else "UiSave" if t.startswith("💾") else
                        "UiOk" if t.startswith("✅") else "UiPass" if t.startswith("⏭") else None)
                if role:
                    w.configure(style=self._derived(role, cur, "TButton"))
        elif cls in ("Frame", "Label", "Checkbutton", "Radiobutton", "Canvas", "Toplevel", "Message"):
            if str(w.cget("background")) == self.tk_default_bg:
                bg = CARD if self._in_card(w) else PAGE
                w.configure(background=bg)
                if cls in ("Checkbutton", "Radiobutton"):
                    w.configure(activebackground=bg, highlightbackground=bg)
        elif cls == "Text":
            w.configure(relief="flat", borderwidth=0, highlightthickness=1,
                        highlightbackground=LINE, highlightcolor=self.accent)
        elif cls == "Listbox":
            w.configure(relief="flat", borderwidth=0, highlightthickness=1,
                        highlightbackground=LINE, highlightcolor=self.accent)

    def paint_all(self, start=None):
        stack = [start or self.root]
        while stack:
            w = stack.pop()
            key = str(w)
            if key not in self.done:
                self.done.add(key)
                try:
                    self._paint(w)
                except tk.TclError:
                    pass
            try:
                stack.extend(w.winfo_children())
            except tk.TclError:
                pass

    def _on_map(self, _e=None):
        # 나중에 생기는 줄·팝업도 칠한다(한 번에 모아서)
        if self.pending:
            return
        self.pending = True

        def run():
            self.pending = False
            _safe(self.paint_all)
        self.root.after(120, run)

    # ---------------- 머리줄 · 왼쪽 메뉴 ----------------
    def build_frame(self):
        root = self.root
        slaves = root.pack_slaves()
        if not slaves or root.grid_slaves():
            raise RuntimeError("창 배치가 pack이 아니라 메뉴를 붙이지 않음")
        first = slaves[0]

        head = tk.Frame(root, background=CARD, height=52)
        head.pack(side="top", fill="x", before=first)
        head.pack_propagate(False)
        tk.Frame(root, background=LINE, height=1).pack(side="top", fill="x", before=first)
        tk.Frame(head, background=self.accent, width=6).pack(side="left", fill="y")
        tk.Label(head, text=self.title, font=(FONT, 14, "bold"), bg=CARD, fg=SIDE).pack(
            side="left", padx=(14, 8))
        tk.Label(head, text=self.subtitle, font=(FONT, 9), bg=CARD, fg=SUB).pack(side="left", pady=(6, 0))
        self.chip_labels = []
        for label, _fn in reversed(self.chips):
            chip = tk.Frame(head, bg=CARD, highlightthickness=1, highlightbackground=LINE)
            chip.pack(side="right", padx=(0, 10), pady=11)
            tk.Label(chip, text=label, font=(FONT, 9), bg=CARD, fg=SUB).pack(side="left", padx=(10, 4))
            dot = tk.Label(chip, text="●", font=(FONT, 9), bg=CARD, fg=DOT["gray"])
            dot.pack(side="left")
            val = tk.Label(chip, text="-", font=(FONT, 9, "bold"), bg=CARD, fg=TEXT)
            val.pack(side="left", padx=(3, 10), pady=3)
            self.chip_labels.append((_fn, dot, val))
        self.chip_labels.reverse()

        side = tk.Frame(root, background=SIDE, width=SIDEBAR_W)
        side.pack(side="left", fill="y", before=first)
        side.pack_propagate(False)
        tk.Frame(side, bg=self.accent2, height=4).pack(fill="x")
        tk.Label(side, text="작업 메뉴", font=(FONT, 9), bg=SIDE, fg=SIDE_DIM).pack(
            anchor="w", padx=18, pady=(14, 6))
        self.menu = []
        for i, tab in enumerate(self.nb.tabs()):
            txt = str(self.nb.tab(tab, "text"))
            b = tk.Label(side, text=txt, anchor="w", font=(FONT, 10), bg=SIDE, fg=SIDE_TEXT,
                         padx=12, pady=8, cursor="hand2")
            b.pack(fill="x", padx=8, pady=1)
            b.bind("<Button-1>", lambda e, t=tab: self.nb.select(t))
            b.bind("<Enter>", lambda e, b=b: self._hover(b, True))
            b.bind("<Leave>", lambda e, b=b: self._hover(b, False))
            self.menu.append((tab, b))
        ver = re.search(r"Ver\s*([0-9.]+)", str(root.title()))
        foot = f"{self.title} Ver{ver.group(1)}" if ver else self.title
        tk.Label(side, text=foot, font=(FONT, 8), bg=SIDE, fg=SIDE_DIM).pack(
            side="bottom", anchor="w", padx=18, pady=12)

        # 탭 줄 숨김 — 탭 자체는 남아 있어 nb.select()로 하는 기존 이동이 그대로 된다
        self.style.layout("UiHidden.TNotebook.Tab", [])
        self.style.configure("UiHidden.TNotebook", background=PAGE, borderwidth=0, tabmargins=0)
        self.nb.configure(style="UiHidden.TNotebook")
        self.nb.bind("<<NotebookTabChanged>>", lambda e: _safe(self.refresh_menu), add="+")
        self.refresh_menu()

    def _hover(self, b, on):
        cur = self.nb.select()
        for tab, lab in self.menu:
            if lab is b and str(tab) != str(cur):
                lab.configure(bg="#2A3A5C" if on else SIDE)

    def refresh_menu(self):
        cur = str(self.nb.select())
        for tab, b in self.menu:
            on = str(tab) == cur
            b.configure(bg=SIDE_SEL if on else SIDE, fg="#FFFFFF" if on else SIDE_TEXT,
                        font=(FONT, 10, "bold" if on else "normal"))

    def refresh_chips(self):
        for fn, dot, val in getattr(self, "chip_labels", []):
            try:
                text, color = fn()
            except Exception:  # noqa: BLE001
                text, color = "-", "gray"
            dot.configure(fg=DOT.get(color, color))
            val.configure(text=text)
        self.root.after(4000, lambda: _safe(self.refresh_chips))

    def widen(self):
        """왼쪽 메뉴 폭만큼 창을 넓힌다(화면을 넘지 않게) — 기존 화면이 좁아지지 않도록."""
        r = self.root
        r.update_idletasks()
        w, h = r.winfo_width(), r.winfo_height()
        if w < 200:
            return
        sw = r.winfo_screenwidth()
        new_w = min(w + SIDEBAR_W, sw - 20)
        if new_w > w:
            x = max(0, (sw - new_w) // 2)
            r.geometry(f"{new_w}x{h}+{x}+{max(0, r.winfo_y())}")


def apply(root, notebook, title, subtitle="", accent="#1F3A5F", accent2="#2E9E5B", chips=None, frame=True,
          widen=True):
    """화면을 다 만든 뒤 한 번 부른다. chips = [(이름, 함수)] — 함수는 (보일 글, 색 이름) 반환.
    색 이름: red(필요) / orange(확인 전) / green(정상) / gray(안 씀). 실패해도 예외를 내지 않는다.
    frame=False면 색·카드만 입히고 머리줄·왼쪽 메뉴는 부르는 쪽이 만든다(포스팅 프로그램 poster_layout.py).
    widen=False면 창 넓히기를 부르는 쪽이 창이 뜨기 전에 한다(뜬 뒤 넓히면 한 번 깜빡인다 — SIDEBAR_W만큼 넓힐 것)."""
    th = _Theme(root, notebook, title, subtitle, accent, accent2, chips)
    if not _safe(th.setup_styles):
        return None
    if frame:
        _safe(th.build_frame)
    _safe(th.paint_all)
    _safe(lambda: root.bind_all("<Map>", th._on_map, add="+"))
    if frame:
        _safe(th.refresh_chips)
        if widen:
            root.after(300, lambda: _safe(th.widen))
    return th
