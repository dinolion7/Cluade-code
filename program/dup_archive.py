"""dup_archive.py — 과거에 올린 글(보관소 MD)과 새 글을 본문 전체로 비교한다. 정책뉴스·복지로 공용.

[파일·폴더]
  보관소: 정책뉴스 작업폴더/final_posts_backup/{제목}/{MD}, 복지로 작업폴더/final_posts_backup/{제목}/{제목}.md
  색인: 각 보관소 폴더 안 _dup_index.json(글마다 파일 수정시각·제목·단어·글자묶음·소제목). 바뀐 글만 다시 계산.

[반드시 지킬 규칙]
  - API를 쓰지 않는다(PC 안에서만 계산). 판정("중복이다")은 하지 않고, 겹친 과거 글과 겹친 내용을 보여 준다
    (같은 내용을 두 번 쓴 실제 예가 아직 없어 기준값을 못 정함 — docs/dup_check_concept.md).
  - 두 신호를 같이 본다: 주제 겹침(단어 TF-IDF, 내 글 전체에 흔한 말은 점수가 낮아짐)과
    문장 겹침(4글자 묶음). 소제목 단위로 어디가 겹쳤는지도 돌려준다.
  - 보관소가 없거나 읽기 실패해도 예외를 내지 않는다(빈 결과).

[버전] V1 (2026-10-16) — 비교·색인·팝업(check_and_ask)
"""
import json
import math
import os
import re

INDEX_NAME = "_dup_index.json"
INDEX_VER = 1
GRAM = 4
SHORT_CHARS = 300        # 이보다 짧으면(뉴스 제목 등) "말이 얼마나 들어 있나"로 본다
NOTE_TOPIC, NOTE_BODY, NOTE_SHORT = 0.15, 0.10, 0.5   # 팝업 기준(샘플: 관계없는 글 2~5%, 같은 정책 다른 각도 13~20%)

_TOKEN_PAT = re.compile(r"[가-힣A-Za-z0-9.%㎡]{2,}")
_STRIP_PAT = re.compile(r"[*_`>|\[\]#:~\-]")


def _body_lines(md: str):
    """제목(# )·해시태그 줄·출처 줄을 뺀 본문 줄."""
    out = []
    for ln in (md or "").splitlines():
        s = ln.strip()
        if not s or s.startswith("# ") or s.startswith("출처"):
            continue
        words = s.split()
        if words and sum(w.startswith("#") for w in words) * 2 >= len(words) and not s.startswith("##"):
            continue
        out.append(s)
    return out


def _title(md: str) -> str:
    for ln in (md or "").splitlines():
        if ln.startswith("# "):
            return ln[2:].strip()
    return ""


def _clean(text: str) -> str:
    return _STRIP_PAT.sub(" ", text)


def _grams(text: str) -> set:
    s = re.sub(r"\s+", "", _clean(text))
    return {s[i:i + GRAM] for i in range(len(s) - GRAM + 1)}


def _tokens(text: str) -> list:
    return [t.strip(".") for t in _TOKEN_PAT.findall(_clean(text)) if len(t.strip(".")) >= 2]


def _sections(md: str) -> list:
    """[(소제목, 본문)] — 첫 소제목 앞은 "도입부"."""
    secs, head, buf = [], "도입부", []
    for s in _body_lines(md):
        if s.startswith("## "):
            if buf:
                secs.append((head, " ".join(buf)))
            head, buf = s[3:].strip(), []
        else:
            buf.append(s)
    if buf:
        secs.append((head, " ".join(buf)))
    return secs


def analyze(md: str) -> dict:
    body = " ".join(_body_lines(md))
    tf = {}
    for t in _tokens(body):
        tf[t] = tf.get(t, 0) + 1
    return {
        "title": _title(md),
        "tf": tf,
        "grams": sorted(_grams(body)),
        "sections": [[h, sorted(_grams(b))] for h, b in _sections(md)],
    }


def _iter_md(root: str):
    if not root or not os.path.isdir(root):
        return
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(".md"):
                yield os.path.join(dirpath, fn)


def load_archive(series: str, root: str) -> list:
    """보관소 한 곳을 읽어 글 목록을 돌려준다(색인 캐시 사용·갱신)."""
    docs = []
    if not root or not os.path.isdir(root):
        return docs
    idx_path = os.path.join(root, INDEX_NAME)
    try:
        with open(idx_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
        if cache.get("ver") != INDEX_VER:
            cache = {}
    except Exception:
        cache = {}
    items = cache.get("items", {})
    new_items, changed = {}, False
    for path in _iter_md(root):
        rel = os.path.relpath(path, root)
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        it = items.get(rel)
        if not it or it.get("mtime") != mtime:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    md = f.read()
            except Exception:
                continue
            it = analyze(md)
            it["mtime"] = mtime
            changed = True
        new_items[rel] = it
        docs.append({"series": series, "path": path, "date": mtime, **it})
    if changed or set(new_items) != set(items):
        try:
            with open(idx_path, "w", encoding="utf-8") as f:
                json.dump({"ver": INDEX_VER, "items": new_items}, f, ensure_ascii=False)
        except Exception:
            pass
    return docs


def _norm_title(t: str) -> str:
    return re.sub(r"[\s'\"‘’“”,.?!·]", "", t or "")


def compare(md: str, archives: list, top: int = 5, exclude_title: str = "") -> list:
    """새 글(md)을 보관소들([(시리즈, 폴더)])의 과거 글과 비교한다.
    돌려주는 값(점수 높은 순, 아무것도 안 겹치면 빈 목록):
      {series, title, path, date, topic(0~1 단어 겹침), body(0~1 글자 겹침),
       shared_terms[겹친 핵심어], shared_sections[(새 소제목, 과거 소제목, 겹침)]}"""
    docs = []
    for series, root in archives:
        try:
            docs.extend(load_archive(series, root))
        except Exception:
            continue
    ex = _norm_title(exclude_title)
    if ex:
        docs = [d for d in docs if _norm_title(d["title"]) != ex]
    if not docs:
        return []
    new = analyze(md)
    n = len(docs) + 1
    df = {}
    for d in docs + [new]:
        for t in d["tf"]:
            df[t] = df.get(t, 0) + 1

    def vec(tf):
        return {t: c * math.log((n + 1) / (df.get(t, 0) + 0.5)) for t, c in tf.items()}

    def norm(v):
        return math.sqrt(sum(x * x for x in v.values())) or 1.0

    nv = vec(new["tf"])
    nn = norm(nv)
    short = len(" ".join(_body_lines(md))) < SHORT_CHARS
    ng = set(new["grams"])
    nsecs = [(h, set(g)) for h, g in new["sections"]]
    out = []
    for d in docs:
        dv = vec(d["tf"])
        if short:
            # 제목 한 줄처럼 짧은 글: 그 말들이 과거 글에 얼마나 들어 있는지(드문 말일수록 무겁게)
            topic = sum(nv[t] for t in nv if t in dv) / (sum(nv.values()) or 1.0)
        else:
            topic = sum(nv[t] * dv.get(t, 0) for t in nv) / (nn * norm(dv))
        dg = set(d["grams"])
        body = len(ng & dg) / (len(ng | dg) or 1)
        if (topic < 0.3) if short else (topic < 0.08 and body < 0.06):
            continue
        shared = sorted((t for t in nv if t in dv), key=lambda t: -(nv[t] * dv[t]))[:8]
        secs = []
        for h, g in nsecs:
            best, bh = 0.0, ""
            for ph, pg in d["sections"]:
                pg = set(pg)
                if not g or not pg:
                    continue
                r = len(g & pg) / min(len(g), len(pg))
                if r > best:
                    best, bh = r, ph
            if best >= 0.35:
                secs.append((h, bh, round(best, 2)))
        out.append({"series": d["series"], "title": d["title"], "path": d["path"], "date": d["date"],
                    "topic": round(topic, 3), "body": round(body, 3), "short": short,
                    "shared_terms": shared, "shared_sections": secs})
    out.sort(key=lambda r: -(r["topic"] + r["body"]))
    return out[:top]


def notable(results: list) -> list:
    """팝업에 올릴 만큼 겹친 글만."""
    return [r for r in results
            if (r["topic"] >= NOTE_SHORT if r.get("short") else (r["topic"] >= NOTE_TOPIC or r["body"] >= NOTE_BODY))]


def archive_counts(archives: list) -> str:
    parts = []
    for series, root in archives:
        n = sum(1 for _ in _iter_md(root)) if root and os.path.isdir(root) else 0
        parts.append(f"{series} {n}개")
    return ", ".join(parts)


def report(results: list) -> str:
    """사람이 읽는 결과 문장(팝업용)."""
    if not results:
        return "과거에 올린 글 가운데 겹치는 글이 없습니다."
    lines = []
    for r in results:
        import datetime as _dt
        day = _dt.datetime.fromtimestamp(r["date"]).strftime("%Y-%m-%d")
        lines.append(f"[{r['series']}] {r['title']}  ({day})")
        if r.get("short"):
            lines.append(f"   제목 말 겹침 {round(r['topic'] * 100)}%")
        else:
            lines.append(f"   주제 겹침 {round(r['topic'] * 100)}% · 문장 겹침 {round(r['body'] * 100)}%")
        if r["shared_terms"]:
            lines.append("   겹친 핵심어: " + ", ".join(r["shared_terms"][:6]))
        for h, ph, v in r["shared_sections"][:4]:
            lines.append(f"   겹친 소제목: 「{h}」 ↔ 「{ph}」 {round(v * 100)}%")
    return "\n".join(lines)


def open_folder(path: str):
    import subprocess
    import sys
    folder = os.path.abspath(os.path.dirname(path))
    try:
        if sys.platform.startswith("win"):
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception:
        pass


def check_and_ask(parent, md: str, archives: list, stage: str, stop_label: str,
                  exclude_title: str = "") -> str:
    """비교해서 겹친 과거 글이 있으면 창을 띄워 묻는다.
    돌려주는 값: "go"(겹친 글 없음·계속 작성) / "stop"(stop_label 버튼). 오류가 나면 "go"(작업을 막지 않음)."""
    try:
        res = notable(compare(md, archives, exclude_title=exclude_title))
    except Exception:
        return "go"
    if not res:
        return "go"
    import tkinter as tk
    from tkinter import ttk
    ans = {"v": "go"}
    win = tk.Toplevel(parent)
    win.title(f"과거 글 중복 확인 — {stage}")
    try:
        if parent.winfo_viewable():
            win.transient(parent)
    except Exception:
        pass
    ttk.Label(win, text=f"내가 전에 올린 글 가운데 겹치는 글이 {len(res)}개 있습니다. "
                        "같은 내용이면 새로 쓰지 말고 기존 글을 고치는 쪽을 생각해 보세요.",
              wraplength=760, justify="left").pack(anchor="w", padx=14, pady=(12, 4))
    txt = tk.Text(win, width=100, height=min(24, 4 + 5 * len(res)), wrap="word")
    txt.insert("1.0", report(res) + f"\n\n(비교한 보관소: {archive_counts(archives)})")
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True, padx=14, pady=4)
    row = ttk.Frame(win)
    row.pack(fill="x", padx=14, pady=(4, 12))

    def done(v):
        ans["v"] = v
        win.destroy()
    ttk.Button(row, text="계속 작성", command=lambda: done("go")).pack(side="left")
    ttk.Button(row, text="📂 기존 글 열기", command=lambda: open_folder(res[0]["path"])).pack(side="left", padx=8)
    ttk.Button(row, text=stop_label, command=lambda: done("stop")).pack(side="right")
    win.protocol("WM_DELETE_WINDOW", lambda: done("go"))
    win.grab_set()
    parent.wait_window(win)
    return ans["v"]
