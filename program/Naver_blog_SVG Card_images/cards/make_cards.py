"""
정책뉴스 카드 이미지 생성기 (V18)
설계도 JSON(클로드가 MD를 분석해 프롬프트 C로 만든 것)을 읽어 PNG를 만듭니다.

레이아웃 13종
    thumbnail                       썸네일(장면 이미지 + 타이틀)
    rows, list, checks, grid        숫자 강조 / 목록 / 체크리스트 / 그리드
    compare, before_after, split    비교 / 전후 비교 / 분할 흐름
    steps, badges, timeline         절차 / 배지 행 / 타임라인
    table, bento                    계산표 / 벤토
공통 옵션
    card_tone: "ivory"(기본) / "pastel"(카드 바탕을 연두·노랑·분홍·하늘로 순환)
    icon_style: "circle"(기본, 아이콘 뒤 파스텔 원) / "plain"
    footers: [{"tone": good|info|point|danger|unknown, "icon", "text", "note"}]  하단 카드(여러 장 가능)
    이미지 슬롯: 아이콘 자리에 "image": "파일명.png" 를 주면 설계도 폴더의 그림을 넣음(없으면 아이콘으로 대체)

준비 (최초 1회):
    pip install playwright
    playwright install chromium
실행:
    python make_cards.py examples/생계비계좌_spec.json   → examples/out/ 에 PNG 저장
"""
import json
import os
import sys
from html import escape
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from icons import icon as svg_icon, CIRCLES  # noqa: E402

SIZE = 1080

# ============================================================
# 1. 색
# ============================================================
C = {
    "bg": "#F6F1E7", "card": "#FBF8F1", "line": "#e6dfd2",
    "navy": "#1F3A5F", "ink": "#2B2B2B", "white": "#ffffff", "gray": "#4a4a4a",
    "green": "#2E9E6B", "orange": "#E8A33D", "red": "#E05A47", "blue": "#3a76c4",
}
C.update({"amber": C["orange"], "coral": C["red"], "charcoal": C["ink"], "gold": "#C9A227", "teal": "#1D5C5A"})

# 시리즈별 메인 색(main: 타이틀 바·썸네일 영역)과 포인트 색(point: 번호 원·화살표 등)
#   policy  = 정책뉴스: 딥 네이비 + 그린
#   welfare = 복지로:   딥 틸 + 골드 (+ 타이틀 바 왼쪽 골드 띠, 썸네일 시리즈 배지)
SERIES = {
    "policy":  {"main": "#1F3A5F", "point": "#2E9E6B", "chip_after": "#c6e5cb"},
    "welfare": {"main": "#1D5C5A", "point": "#C9A227", "chip_after": "#efe1b0"},
}
POLICY_NAVY = C["navy"]
C.update({"point": SERIES["policy"]["point"], "chip_after": SERIES["policy"]["chip_after"]})

# 카드 바탕 톤: (바탕, 테두리)
TONES = {
    "ivory": ("#FBF8F1", "#e6dfd2"), "green": ("#ecf6e8", "#cfe5c8"), "yellow": ("#fdf4de", "#f1dfb0"),
    "pink": ("#fbebe6", "#f0cfc6"), "blue": ("#e7f1fb", "#c9dcef"), "gray": ("#eeeeee", "#d6d6d6"),
    "good": ("#eef7ea", "#bfdcb6"), "info": ("#e7f1fb", "#c3d8ee"), "point": ("#fff5d9", "#f3d38a"),
    "danger": ("#fdf0ee", "#e8836f"), "unknown": ("#fdf0ee", "#e8836f"), "bad": ("#fdf1ee", "#f0b0a3"),
    "plain": ("#FBF8F1", "#e6dfd2"),
}
PASTEL = ["green", "yellow", "pink", "blue"]
BADGE = {"amber": "#f9d98c", "green": "#bfe3c4", "blue": "#cfe3f6", "gray": "#e3e3e3", "coral": "#f6c3b8"}

# 렌더 중 상태 (아이콘 원 색 순번, 스타일, 설계도 폴더)
STATE = {"circle": 0, "style": "circle", "dir": Path("."), "series": "policy"}


# ============================================================
# 2. 작은 부품
# ============================================================
def rich(parts, default="ink"):
    """글자 조각 [["글자","색"],...] 또는 문자열 → HTML (\\n 줄바꿈)"""
    if not parts:
        return ""
    if isinstance(parts, str):
        parts = [[parts, default]]
    return "".join(f'<span style="color:{C.get(c, c)}">{escape(t).replace(chr(10), "<br>")}</span>'
                   for t, c in parts)


def ic(name, cls="ic"):
    """아이콘 div (icon_style이 circle이면 파스텔 원을 순서대로 깜)"""
    circle = None
    if STATE["style"] == "circle":
        circle = CIRCLES[STATE["circle"] % len(CIRCLES)]
        STATE["circle"] += 1
    svg = svg_icon(name, circle)
    if STATE["series"] == "welfare":
        svg = svg.replace("#1f9d57", C["gold"]).replace("#2E9E6B", C["gold"])
    return f'<div class="{cls}">{svg}</div>'


def pic(item, cls="ic", default_icon="info"):
    """이미지 슬롯이 있고 파일이 있으면 그림, 아니면 아이콘"""
    img = item.get("image") if isinstance(item, dict) else None
    if img:
        p = (STATE["dir"] / img)
        if p.exists():
            return f'<div class="{cls} slot"><img src="{p.resolve().as_uri()}"></div>'
    name = item.get("icon", default_icon) if isinstance(item, dict) else default_icon
    return ic(name, cls)


def tone_style(tone):
    bg, line = TONES.get(tone, TONES["ivory"])
    return f'background:{bg};border-color:{line}'


def card_tone(spec, i, explicit=None):
    if explicit:
        return tone_style(explicit)
    if spec.get("card_tone") == "pastel":
        return tone_style(PASTEL[i % len(PASTEL)])
    return ""


def title_bar(parts):
    return f'<div class="title"><div class="fit">{rich(parts, "white")}</div></div>'


ARROW_DOWN = ('<div class="arrow-down"><svg viewBox="0 0 40 30"><path d="M14 0 H26 V12 H36 L20 28 L4 12 H14 Z" '
              'fill="#6f86a8"/></svg></div>')
DOT_LINK = '<div class="link"><span></span><i></i></div>'
FOOT_ICON = {"good": "check", "info": "info", "danger": "warning_triangle", "unknown": "warning_triangle"}


def footers(s):
    """하단 카드 목록. 예전 키(alert, conclusion, footer)도 받아 줌"""
    items = list(s.get("footers", []))
    if s.get("alert"):
        a = s["alert"]
        items.append({"tone": "point", "icon": a.get("icon", "warning"), "text": a["text"]})
    if s.get("conclusion"):
        cc = s["conclusion"]
        items.append({"tone": "point", **cc} if isinstance(cc, dict) else {"tone": "point", "text": cc})
    if s.get("footer"):
        items.append({"tone": "good", **s["footer"]})
    out = []
    for f in items:
        tone = f.get("tone", "good")
        name = f.get("icon", FOOT_ICON.get(tone))
        text = f["text"]
        if tone == "unknown" and isinstance(text, str):
            text = [[text, "coral"]]
        icon_html = (ic(name, "ic foot-ic") + '<div class="vline"></div>') if name else ""
        note = f'<div class="note2">{escape(f["note"])}</div>' if f.get("note") else ""
        align = "left" if icon_html else "center"
        out.append(f'<div class="card foot" style="{tone_style(tone)}">{icon_html}'
                   f'<div class="foot-tx"><div class="fit mid {align}">{rich(text)}</div>{note}</div></div>')
    return "".join(out)


def page(s, main):
    return title_bar(s["title"]) + f'<div class="main">{main}</div>' + footers(s)


def textblock(it, align="left"):
    """head(큰) / text(보통) / sub(작은) 3단 글"""
    h = f'<div class="tx-h fit">{rich(it["head"])}</div>' if it.get("head") else ""
    m = f'<div class="tx-m fit">{rich(it["text"])}</div>' if it.get("text") else ""
    sb = f'<div class="tx-s fit">{rich(it["sub"], "gray")}</div>' if it.get("sub") else ""
    return f'<div class="tb {align}">{h}{m}{sb}</div>'


# ============================================================
# 3. 레이아웃
# ============================================================
def layout_rows(s):
    """숫자 강조형: 아이콘 + (작은 말 / 큰 숫자 / 보조 설명)"""
    rows = "".join(f'''<div class="card row" style="{card_tone(s, i)}">{ic(r["icon"], "ic lg")}
        <div class="tx">{f'<div class="small fit">{rich(r["small"])}</div>' if r.get("small") else ""}
        <div class="big fit">{rich(r["big"])}</div>
        {f'<div class="sub fit">{rich(r["sub"], "gray")}</div>' if r.get("sub") else ""}</div></div>'''
                   for i, r in enumerate(s["rows"]))
    return page(s, rows)


def layout_list(s):
    """목록형: 아이콘 + 큰 글(+작은 설명) 행 3~5개"""
    rows = "".join(f'''<div class="card row" style="{card_tone(s, i, it.get("tone"))}">{pic(it, "ic md")}
        {textblock({"head": it["text"], "sub": it.get("sub")})}</div>''' for i, it in enumerate(s["items"]))
    return page(s, rows)


def layout_checks(s):
    """체크리스트형
    기본: 체크 + 아이콘 + 가운데 글 / align "left": 왼쪽 정렬 3단 글(head·text·sub)
    numbered: true → 체크 대신 번호(모두 그린)"""
    left = s.get("align") == "left" or s.get("numbered")
    rows = []
    for i, it in enumerate(s["items"]):
        mark = (f'<div class="num sm" style="background:{C["point"]}">{i + 1}</div>' if s.get("numbered")
                else ic("check", "ic xs"))
        if left:
            body = textblock(it if it.get("head") else {"head": it["text"], "sub": it.get("sub")})
            rows.append(f'<div class="card row" style="{card_tone(s, i)}">{mark}<div class="vline"></div>'
                        f'{body}{pic(it, "ic md")}</div>')
        else:
            rows.append(f'<div class="card row" style="{card_tone(s, i)}">{mark}{pic(it, "ic sm")}'
                        f'<div class="fit mid center">{rich(it["text"])}</div></div>')
    return page(s, "".join(rows))


def layout_grid(s):
    """그리드형: 아이콘 + 이름 칸 4~6개 (3=3, 4=2+2, 5=3+2, 6=3+3)"""
    items = s["items"]
    n = len(items)
    split = {3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3]}.get(n, [n])
    rows, k = [], 0
    for cnt in split:
        cells = "".join(f'''<div class="card cell" style="{card_tone(s, k + j)}">{pic(it, "ic cell-ic")}
            <div class="fit mid center">{rich(it["text"])}</div>
            {f'<div class="tx-s center">{rich(it["sub"], "gray")}</div>' if it.get("sub") else ""}</div>'''
                        for j, it in enumerate(items[k:k + cnt]))
        rows.append(f'<div class="grid-row">{cells}</div>')
        k += cnt
    return page(s, "".join(rows))


def layout_compare(s):
    """비교형: 좌우 2열
    열: label(칩), head(큰 글), body, note(작은 줄), icon 또는 image, tone(good·bad·plain·green·yellow·blue·pink·gray·danger)
    icon_position: "bottom"(기본) / "top" """
    top = s.get("icon_position") == "top"

    def col(c, i):
        tone = c.get("tone") or (PASTEL[i] if s.get("card_tone") == "pastel" else "plain")
        label = f'<div class="chip">{escape(c["label"])}</div>' if c.get("label") else ""
        body = f'<hr><div class="body">{rich(c["body"])}</div>' if c.get("body") else ""
        note = f'<div class="note2">{escape(c["note"])}</div>' if c.get("note") else ""
        p = pic(c, "ic col-ic")
        inner = (f'{label}{p}<div class="head">{rich(c["head"])}</div>{body}{note}' if top
                 else f'{label}<div class="head">{rich(c["head"])}</div>{body}{note}{p}')
        return f'<div class="col{" top" if top else ""}" style="{tone_style(tone)}">{inner}</div>'
    return page(s, f'<div class="cols">{col(s["left"], 0)}{col(s["right"], 1)}</div>')


def layout_before_after(s):
    """전/후 비교형: 기존(회색) → 앞으로(연두), 열 사이 큰 화살표
    left/right: label, text, sub, icon 또는 image"""
    def col(c, tone, chip):
        sub = f'<div class="tx-s center">{rich(c["sub"], "gray")}</div>' if c.get("sub") else ""
        return (f'<div class="col ba" style="{tone_style(tone)}"><div class="chip" style="background:{chip}">'
                f'{escape(c["label"])}</div><div class="head">{rich(c["text"])}</div>{sub}{pic(c, "ic col-ic")}</div>')
    arrow = ('<div class="ba-arrow"><svg viewBox="0 0 60 80"><path d="M0 22 H30 V0 L60 40 L30 80 V58 H0 Z" '
             f'fill="{C["point"]}" opacity=".85"/></svg></div>')
    return page(s, f'<div class="cols">{col(s["left"], "gray", "#d9d9d9")}{arrow}'
                   f'{col(s["right"], "green", C["chip_after"])}</div>')


def layout_split(s):
    def box(b):
        color = C.get(b["color"], C["navy"])
        return f'''<div class="card sbox" style="border-color:{color}">
            <div class="label" style="background:{color}">{escape(b["label"])}</div>
            {pic(b, "ic md")}<div class="mid center">{rich(b["text"])}</div></div>'''
    src = s["source"]
    arrows = f'''<svg class="fork" viewBox="0 0 1000 120">
        <path d="M500 0 V40 Q500 60 470 60 H260 Q230 60 230 90 V110" fill="none" stroke="{C['point']}" stroke-width="10" stroke-linecap="round"/>
        <path d="M500 40 Q500 60 530 60 H740 Q770 60 770 90 V110" fill="none" stroke="{C['blue']}" stroke-width="10" stroke-linecap="round"/>
        <polygon points="214,96 246,96 230,120" fill="{C['point']}"/><polygon points="754,96 786,96 770,120" fill="{C['blue']}"/></svg>'''
    note = f'<div class="note">{escape(s["note"])}</div>' if s.get("note") else ""
    return page(s, f'''<div class="card source">{ic(src["icon"], "ic sm")}<div class="mid">{escape(src["text"])}</div></div>
      {arrows}<div class="split">{box(s["left"])}{box(s["right"])}</div>{note}''')


def layout_steps(s):
    """절차형
    numbered: true → 번호 원(첫 단계 그린, num_color "green"이면 모두 그린) + 왼쪽 정렬 글 + 오른쪽 아이콘
    align: "left" → 왼쪽 정렬 글 + 오른쪽 아이콘
    단계: highlight(노란 강조) / tone "danger"(코럴 경고) / sub(작은 줄)"""
    numbered = s.get("numbered")
    left = numbered or s.get("align") == "left"
    items = []
    for i, st in enumerate(s["steps"]):
        if i:
            items.append({"none": '<div class="gap"></div>', "dots": DOT_LINK}.get(s.get("connector"), ARROW_DOWN))
        danger = st.get("tone") == "danger"
        tone = "danger" if danger else ("point" if st.get("highlight") else st.get("tone"))
        style = card_tone(s, i, tone)
        name = st.get("icon", "warning_triangle" if danger else "document")
        if left or danger:
            text = textblock({"head": st["text"], "sub": st.get("sub")})
        else:
            text = f'<div class="fit mid center">{rich(st["text"])}</div>'
        if numbered:
            color = C["point"] if (i == 0 or s.get("num_color") in ("green", "point", "gold")) else C["navy"]
            body = f'<div class="num" style="background:{color}">{i + 1}</div><div class="vline"></div>{text}{pic({**st, "icon": name}, "ic sm")}'
        elif danger:
            body = f'{ic(name, "ic sm")}<div class="vline"></div>{text}'
        elif left:
            body = f'{text}{pic({**st, "icon": name}, "ic sm")}'
        else:
            body = f'{pic({**st, "icon": name}, "ic sm")}{text}'
        items.append(f'<div class="card step" style="{style}">{body}</div>')
    return page(s, f'<div class="tight">{"".join(items)}</div>')


def layout_badges(s):
    """배지 행: 왼쪽 배지(2027년·이후·장기 등) + 글 + 오른쪽 아이콘
    items: badge, badge_color(amber·green·blue·gray·coral), text, sub, icon
    connector: "dots"(기본) / "arrows" """
    link = ARROW_DOWN if s.get("connector") == "arrows" else DOT_LINK
    items = []
    for i, it in enumerate(s["items"]):
        if i:
            items.append(link)
        bc = BADGE.get(it.get("badge_color", "amber"), BADGE["amber"])
        items.append(f'''<div class="card step" style="{card_tone(s, i, it.get("tone"))}">
            <div class="badge" style="background:{bc}"><span class="fit">{escape(it["badge"])}</span></div>
            <div class="vline"></div>{textblock({"head": it["text"], "sub": it.get("sub")})}{pic(it, "ic sm")}</div>''')
    return page(s, f'<div class="tight">{"".join(items)}</div>')


def layout_timeline(s):
    """타임라인형
    기본: 날짜(앰버) + 내용 / stack: true → 라벨(그린) 위 + 큰 날짜(앰버) 아래
    항목 summary: true → 요약 행(큰 글 하나)"""
    items = []
    for i, ev in enumerate(s["events"]):
        style = card_tone(s, i, "point" if ev.get("highlight") else ev.get("tone"))
        if ev.get("summary"):
            body = f'{pic(ev, "ic sm") if ev.get("icon") else ""}<div class="fit mid center big2">{rich(ev["text"])}</div>'
        elif s.get("stack") == "date":
            body = (f'{pic(ev, "ic sm") if ev.get("icon") else ""}<div class="tb left">'
                    f'<div class="tl-date2 fit">{escape(ev["date"])}</div>'
                    f'<div class="tx-h fit">{rich("· " + ev["label"] if isinstance(ev.get("label"), str) else ev.get("label", ""))}</div></div>')
        elif s.get("stack"):
            body = (f'{pic(ev, "ic sm") if ev.get("icon") else ""}<div class="tb left">'
                    f'<div class="tx-h fit">{rich(ev.get("label", ""), "point")}</div>'
                    f'<div class="tl-date2 fit">{escape(ev["date"])}</div>'
                    f'{f"<div class=tx-s>{rich(ev.get(chr(115)+chr(117)+chr(98)), chr(103)+chr(114)+chr(97)+chr(121))}</div>" if ev.get("sub") else ""}</div>')
        else:
            body = (f'<div class="tl-date">{escape(ev["date"])}</div><div class="fit mid">{rich(ev["text"])}</div>'
                    f'{pic(ev, "ic tiny") if ev.get("icon") else ""}')
        items.append(f'<div class="tl-row"><div class="tl-dot"></div><div class="card tl-item" style="{style}">{body}</div></div>')
    return page(s, f'<div class="timeline">{"".join(items)}</div>')


def layout_table(s):
    """계산표형
    columns + rows(셀 목록) → 머리줄 있는 표 (header_color: "navy" 기본 / "charcoal")
    columns 없이 rows가 {"label","sub","value","highlight"} → 항목-금액 2열 표
    corner_icon: 표 오른쪽 아래 아이콘"""
    hl = s.get("highlight_row")
    head_bg = C["ink"] if s.get("header_color") == "charcoal" else C["navy"]
    if s.get("columns"):
        head = "<thead><tr>" + "".join(f'<th style="background:{head_bg}">{escape(c)}</th>' for c in s["columns"]) + "</tr></thead>"
        body = "".join(('<tr class="hl">' if i == hl else "<tr>") + "".join(f'<td>{rich(c)}</td>' for c in row) + "</tr>"
                       for i, row in enumerate(s["rows"]))
        table = f'<table>{head}<tbody>{body}</tbody></table>'
    else:
        body = ""
        for r in s["rows"]:
            sub = f'<div class="kv-sub">{escape(r["sub"])}</div>' if r.get("sub") else ""
            val = r["value"] if not isinstance(r["value"], str) else [[r["value"], "amber"]]
            body += (f'<tr class="{"hl" if r.get("highlight") else ""}"><td class="kv-l">'
                     f'<div class="kv-label">{rich(r["label"])}</div>{sub}</td><td class="kv-r"><div class="kvv">{rich(val)}</div></td></tr>')
        table = f'<table class="kv">{body}</table>'
    cap = f'<div class="caption">{escape(s["caption"])}</div>' if s.get("caption") else ""
    corner = ic(s["corner_icon"], "ic corner-ic") if s.get("corner_icon") else ""
    return page(s, f'<div class="card tablecard">{table}{cap}{corner}</div>')


def layout_bento(s):
    """벤토형: 왼쪽 큰 숫자 카드(hero) + 오른쪽 작은 카드 1~2개(side) + 그림 띠(band, 선택)
    hero: {"text": 큰 숫자 조각, "sub": 조각, "note": 문자열, "icon"/"image"}
    side: [{"icon", "text"}] / band: {"image": 파일} 또는 {"icon": 이름}"""
    h = s["hero"]
    hero_pic = pic(h, "ic md") if (h.get("icon") or h.get("image")) else ""
    hero = (f'<div class="card hero" style="{card_tone(s, 0, h.get("tone"))}">'
            f'<div class="hero-n fit">{rich(h["text"])}</div>'
            f'{f"<div class=tx-m>{rich(h.get(chr(115)+chr(117)+chr(98)))}</div>" if h.get("sub") else ""}'
            f'{f"<div class=tx-s>{escape(h.get(chr(110)+chr(111)+chr(116)+chr(101)))}</div>" if h.get("note") else ""}'
            f'{hero_pic}</div>')
    sides = "".join(f'<div class="card row" style="{card_tone(s, i + 1, it.get("tone"))}">{pic(it, "ic sm")}'
                    f'{textblock({"head": it["text"], "sub": it.get("sub")})}</div>' for i, it in enumerate(s.get("side", [])))
    band = ""
    if s.get("band"):
        b = s["band"]
        band = f'<div class="band">{pic(b, "band-pic", b.get("icon", "map_pin"))}</div>'
    if s.get("hero_position") == "top":
        return page(s, f'<div class="bento"><div class="bento-hero-top">{hero}</div><div class="bento-row">{sides}</div>{band}</div>')
    return page(s, f'<div class="bento"><div class="bento-top">{hero}<div class="bento-side">{sides}</div></div>{band}</div>')


def layout_thumbnail(s):
    """썸네일: 장면 이미지 + 남색 영역 + 타이틀
    shape: fade(아래로 흐려짐) / wave(곡선) / slant(대각선) / wall(장면 벽이 이미 남색 → 덮개 없이 살짝 어둡게)
    align: center(기본) / left"""
    lines = "".join(f'<div class="tl tl{i} fit">{rich(l, "white")}</div>' for i, l in enumerate(s["lines"]))
    shape = s.get("shape", "fade")
    navy = C["navy"]
    if shape == "wave":
        cover = (f'<svg class="cover" viewBox="0 0 1080 1080" preserveAspectRatio="none">'
                 f'<path d="M0 0 H1080 V448 C 860 520, 520 395, 0 478 Z" fill="{navy}"/></svg>')
    elif shape == "slant":
        cover = (f'<svg class="cover" viewBox="0 0 1080 1080" preserveAspectRatio="none">'
                 f'<path d="M0 0 H1080 V418 L0 512 Z" fill="{navy}"/></svg>')
    elif shape == "wall":
        cover = '<div class="shade-wall"></div>'
    else:
        cover = '<div class="shade"></div>'
    bg = s["background"]
    p = STATE["dir"] / bg
    url = p.resolve().as_uri() if p.exists() else bg
    align = "left" if s.get("align") == "left" else "center"
    badge = ""
    if s.get("badge"):
        default = "ribbon" if STATE["series"] == "welfare" else "pill"
        if s.get("badge_style", default) == "ribbon":
            badge = f'<div class="sbadge ribbon {align}"><span><b>{escape(s["badge"])}</b></span></div>'
        else:
            badge = f'<div class="sbadge {align}"><span>{escape(s["badge"])}</span></div>'
    top = " with-badge" if badge else ""
    if badge:
        if shape == "wall":   # 배지로 제목이 내려가면 배경에 남은 원본 글자 흔적이 비치므로 위쪽을 메인색으로 덮음
            cover = f'<div class="shade-wall" style="background:linear-gradient(180deg,{navy} 0%,{navy} 30%,rgba(0,0,0,0) 38%)"></div>'
        cover = f'<div class="cover-wrap">{cover}</div>'
    return f'''<div class="thumb" style="background-image:url('{url}')">{cover}{badge}
        <div class="tlines {align}{top}">{lines}</div></div>'''


LAYOUTS = {"rows": layout_rows, "list": layout_list, "checks": layout_checks, "grid": layout_grid,
           "compare": layout_compare, "before_after": layout_before_after, "split": layout_split,
           "steps": layout_steps, "badges": layout_badges, "timeline": layout_timeline,
           "table": layout_table, "bento": layout_bento, "thumbnail": layout_thumbnail}


# ============================================================
# 4. CSS (색은 $이름 으로 치환)
# ============================================================
CSS_T = Template("""
html,body{margin:0;width:${size}px;height:${size}px;overflow:hidden;background:$bg}
*{box-sizing:border-box}
body{font-family:'Noto Sans KR','Malgun Gothic',sans-serif;color:$ink;letter-spacing:-.03em}
.frame{width:${size}px;height:${size}px;padding:26px 28px;display:flex;flex-direction:column;gap:18px}
.title{background:$navy;border-radius:26px;height:178px;display:flex;align-items:center;justify-content:center;padding:0 40px;flex:none}
.title .fit{font-size:82px;font-weight:900;white-space:nowrap;line-height:1}
.main{flex:1;min-height:0;display:flex;flex-direction:column;gap:18px}
.tight{flex:1;min-height:0;display:flex;flex-direction:column}
.card{background:$card;border:3px solid $line;border-radius:24px;display:flex;align-items:center;
  padding:16px 30px;gap:24px;flex:1;min-height:0;min-width:0;overflow:hidden}
.ic{flex:none} .ic svg{width:100%;display:block} .ic.slot img{width:100%;height:100%;object-fit:cover;border-radius:18px;display:block}
.ic.lg{width:280px} .ic.md{width:200px} .ic.sm{width:170px} .ic.xs{width:120px} .ic.tiny{width:120px}
.tx{flex:1;min-width:0}
.small{font-size:72px;font-weight:900;line-height:1.1;white-space:nowrap}
.big{font-size:122px;font-weight:900;line-height:1.08;white-space:nowrap}
.sub{font-size:40px;font-weight:700;margin-top:8px;white-space:nowrap}
.mid{font-size:74px;font-weight:900;line-height:1.15;flex:1;min-width:0;white-space:nowrap}
.big2{font-size:84px}
.center{text-align:center} .left{text-align:left}
.tb{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;gap:6px}
.tx-h{font-size:80px;font-weight:900;line-height:1.15;white-space:nowrap}
.tx-m{font-size:58px;font-weight:800;line-height:1.2;white-space:nowrap}
.tx-s{font-size:40px;font-weight:700;line-height:1.25;white-space:nowrap;color:$gray}
.vline{width:3px;align-self:stretch;margin:12px 0;background:rgba(0,0,0,.09);flex:none}
.num{width:116px;height:116px;border-radius:50%;color:#fff;font-size:72px;font-weight:900;display:flex;
  align-items:center;justify-content:center;flex:none}
.num.sm{width:96px;height:96px;font-size:58px}
.gap{height:14px;flex:none}
.arrow-down{height:38px;display:flex;justify-content:center;flex:none;margin:-3px 0}
.arrow-down svg{width:38px;height:28px;margin-top:5px}
.link{height:34px;display:flex;flex-direction:column;align-items:center;flex:none}
.link span{width:5px;height:20px;background:$navy}
.link i{width:20px;height:20px;border-radius:50%;background:$navy;margin-top:-4px}
.badge{width:200px;align-self:stretch;margin:6px 0;border-radius:20px;display:flex;align-items:center;justify-content:center;
  flex:none;padding:0 14px} .badge span{font-size:66px;font-weight:900;white-space:nowrap}
.foot{flex:none;padding:18px 30px;min-height:120px}
.foot-ic{width:120px}
.foot-tx{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center}
.foot .mid{font-size:66px}
.note2{font-size:40px;font-weight:700;color:$gray;text-align:center;margin-top:6px;white-space:nowrap}
.cols{flex:1;min-height:0;display:flex;gap:20px;align-items:stretch}
.col{flex:1;min-width:0;border-radius:24px;border:3px solid;padding:26px 24px;display:flex;flex-direction:column;
  align-items:center;text-align:center;overflow:hidden}
.col .head{font-size:88px;font-weight:900;line-height:1.18;white-space:nowrap}
.col hr{width:90%;border:0;border-top:3px solid rgba(0,0,0,.08);margin:20px 0}
.col .body{font-size:62px;font-weight:900;line-height:1.3;white-space:nowrap}
.col-ic{width:280px;margin-top:auto} .col.top .col-ic{margin-top:0;margin-bottom:14px}
.col .note2{margin-top:14px}
.chip{background:#e3ecf6;border-radius:18px;padding:12px 10px;font-size:54px;font-weight:900;width:100%;
  margin-bottom:22px;white-space:nowrap}
.col.ba{padding:0 0 22px} .col.ba .chip{margin:0 0 22px;width:100%;border-radius:20px 20px 0 0;padding:18px 10px;font-size:56px}
.col.ba .head, .col.ba .tx-s{padding:0 22px}
.ba-arrow{flex:none;width:56px;align-self:center;margin:0 -14px;z-index:2} .ba-arrow svg{width:100%}
.grid-row{flex:1;min-height:0;display:flex;gap:18px}
.cell{flex-direction:column;justify-content:center;gap:10px;padding:16px}
.cell-ic{width:210px}
.cell .mid{flex:none;width:100%}
.source{flex:none;justify-content:center;padding:10px 30px}
.fork{width:100%;height:110px;flex:none;margin:-10px 0}
.split{flex:1;display:flex;gap:28px;min-height:0}
.sbox{flex-direction:column;justify-content:center;gap:10px;position:relative;padding-top:56px}
.label{position:absolute;top:-3px;left:-3px;right:-3px;height:66px;border-radius:24px 24px 0 0;color:#fff;
  font-size:40px;font-weight:900;display:flex;align-items:center;justify-content:center}
.note{text-align:center;font-size:38px;font-weight:700;color:$gray;flex:none}
.tablecard{flex:1;flex-direction:column;align-items:stretch;justify-content:center;padding:26px 30px;gap:14px;position:relative;overflow:visible}
table{width:100%;box-sizing:border-box;border-collapse:separate;border-spacing:0;font-size:56px;font-weight:800;text-align:center}
th{color:#fff;font-weight:900;padding:24px 10px;font-size:44px}
th:first-child{border-radius:14px 0 0 0} th:last-child{border-radius:0 14px 0 0}
td{padding:30px 10px;border-bottom:2px solid $line;white-space:nowrap}
tr.hl td{background:#eef7f1;font-weight:900}
.caption{font-size:30px;color:$gray;text-align:right}
table.kv{table-layout:fixed;border-collapse:separate;border-spacing:0;border:3px solid #c8d6e6;border-radius:18px;overflow:hidden}
table.kv td{padding:22px 28px;border-bottom:2px solid #dbe4ee}
table.kv tr:last-child td{border-bottom:0}
.kv-l{background:#eef3f8;text-align:left;border-right:2px solid #dbe4ee;width:50%;overflow:hidden}
.kv-r{overflow:hidden} .kvv{white-space:nowrap;display:inline-block}
.kv-label{font-size:60px;font-weight:900;white-space:nowrap}
.kv-sub{font-size:32px;font-weight:700;color:$gray;white-space:nowrap}
.kv-r{font-size:66px;font-weight:900;color:$orange;text-align:left;white-space:nowrap}
table.kv tr.hl .kv-label{color:$green}
.corner-ic{position:absolute;right:-22px;bottom:-56px;width:170px}
.timeline{flex:1;min-height:0;display:flex;flex-direction:column;gap:16px;position:relative;padding-left:46px}
.timeline:before{content:"";position:absolute;left:16px;top:20px;bottom:20px;width:6px;background:$navy;border-radius:3px}
.tl-row{flex:1;display:flex;align-items:center;position:relative;min-height:0}
.tl-dot{position:absolute;left:-47px;width:40px;height:40px;border-radius:50%;background:$orange;border:6px solid $bg}
.card.tl-item{height:100%;gap:26px;flex:1;min-width:0}
.tl-date{font-size:46px;font-weight:900;color:$orange;white-space:nowrap;flex:none;min-width:300px}
.tl-date2{font-size:88px;font-weight:900;color:$orange;white-space:nowrap;line-height:1.05}
.bento{flex:1;min-height:0;display:flex;flex-direction:column;gap:18px}
.bento-top{flex:1.3;min-height:0;display:flex;gap:18px}
.hero{flex:1.05;flex-direction:column;justify-content:center;align-items:flex-start;gap:6px}
.hero-n{font-size:200px;font-weight:900;line-height:1;white-space:nowrap}
.bento-hero-top{flex:1;min-height:0;display:flex} .bento-hero-top .hero{flex-direction:row;align-items:center;justify-content:space-between}
.bento-hero-top .hero-n{font-size:120px;line-height:1.1}
.bento-row{flex:1.1;min-height:0;display:flex;gap:18px} .bento-row .card{flex-direction:row;padding:16px 20px;gap:14px}
.bento-row .tx-h{font-size:72px} .bento-row .tx-s{white-space:normal;font-size:34px}
.bento-side{flex:1;min-width:0;display:flex;flex-direction:column;gap:18px}
.band{flex:1;min-height:0;border-radius:24px;overflow:hidden;display:flex;justify-content:center;align-items:center}
.band-pic{height:100%;width:100%;display:flex;justify-content:center} .band-pic svg{height:100%;width:auto}
.band-pic.slot img{width:100%;height:100%;object-fit:cover;border-radius:24px}
.col-ic, .cell-ic{flex:1;min-height:0;width:100%;display:flex;justify-content:center;align-items:flex-end;margin-top:auto}
.cell-ic{align-items:center}
.col-ic svg, .cell-ic svg{height:100%;width:auto;max-height:270px;max-width:100%}
.col.top .col-ic{flex:0 0 auto;height:230px;margin:0 0 14px}
.col-ic.slot img, .cell-ic.slot img{width:100%;height:100%;object-fit:cover;border-radius:18px}
.thumb{position:absolute;inset:0;background-size:cover;background-position:center bottom}
.cover{position:absolute;inset:0;width:100%;height:100%}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,$navy 0%,$navy 40%,color-mix(in srgb,$navy 85%,transparent) 45%,transparent 57%)}
.shade-wall{position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,40,74,.55) 0%,rgba(18,40,74,.3) 30%,rgba(18,40,74,0) 46%)}
.tlines{position:absolute;left:44px;right:44px;top:52px;font-weight:900;line-height:1.12;text-shadow:0 4px 14px rgba(0,0,0,.35)}
.tlines.with-badge{top:128px}
.cover-wrap{position:absolute;inset:0;transform:scaleY(1.17);transform-origin:top}
.sbadge{position:absolute;top:40px;left:0;right:0;display:flex;justify-content:center}
.sbadge.left{justify-content:flex-start;left:64px}
.sbadge span{border:5px solid $badge;border-radius:40px;padding:8px 34px;color:#fff;font-size:44px;font-weight:900;
  background:rgba(0,0,0,.12);white-space:nowrap}
.sbadge.ribbon span{border:0;border-radius:0;background:$badge;padding:5px;position:relative;
  clip-path:polygon(0 0,100% 0,96% 50%,100% 100%,0 100%,4% 50%)}
.sbadge.ribbon span b{display:block;background:$badgebg;padding:8px 52px;font-weight:900;
  clip-path:polygon(0 0,100% 0,96.4% 50%,100% 100%,0 100%,3.6% 50%)}
.tlines.center{text-align:center} .tlines.left{text-align:left;left:64px}
.tl{white-space:nowrap} .tl0{font-size:96px} .tl1{font-size:132px} .tl2{font-size:120px}
""")


def css():
    extra = ""
    if STATE["series"] == "welfare":
        # 타이틀 바 왼쪽 골드 세로 띠 (복지로 시리즈 표시)
        extra = (f".title{{position:relative;overflow:hidden}}"
                 f".title:before{{content:'';position:absolute;left:0;top:0;bottom:0;width:22px;background:{C['gold']}}}")
    return CSS_T.safe_substitute(size=SIZE, bg=C["bg"], ink=C["ink"], navy=C["navy"], card=C["card"], line=C["line"],
                                 gray=C["gray"], orange=C["orange"], green=C["green"], gold=C["gold"],
                                 badge=C["point"], badgebg=("#123f3e" if STATE["series"] == "welfare" else "#14294a")) + extra

FIT_JS = """
// 0) 행 카드 아이콘: 카드 높이에 맞춰 크기 계산 (아이콘이 카드를 밀어내지 않게)
document.querySelectorAll('.card.row > .ic, .card.step > .ic, .card.tl-item > .ic').forEach(i => {
  const h = i.parentElement.clientHeight - 30;
  const cap = i.closest('.bento-side') ? 130 : i.closest('.bento-row') ? 150 : (i.parentElement.querySelector('.badge, .num') ? 160 : (i.classList.contains('lg') ? 300 : 240));
  i.style.width = Math.max(70, Math.min(h * 220 / 170, cap)) + 'px';
});
const TXT = '.mid,.big,.small,.sub,.head,.body,.note2,.tx-h,.tx-m,.tx-s,.chip,.kv-label,.kv-r,.kv-sub,.hero-n,.tl-date2,.badge span,td,th';
// 1) 가로: 글자가 칸보다 넓으면 글자 크기를 줄임
function fitW(el){
  const box = el.parentElement, cs = getComputedStyle(box);
  const max = box.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  let fs = parseFloat(getComputedStyle(el).fontSize), n = 0;
  while (el.scrollWidth > Math.min(max, el.clientWidth || max) + 1 && fs > 18 && n++ < 80) { fs -= 2; el.style.fontSize = fs + 'px'; }
}
document.querySelectorAll('.fit, .mid, .chip, .kv-label, .kv-sub, .kvv, .head, .body, .note2').forEach(fitW);
// 2) 세로: 카드·열 안 내용이 넘치면 글자와 번호 원을 함께 조금씩 줄임
//    (2026-10-15) 예전엔 글자만 줄여서, 번호 원(116px)처럼 글자가 아닌 것 때문에 넘치면 글자가 최소
//    크기까지 줄었다. 이제 번호 원도 같이 줄이고, 한 번 줄여도 넘침이 줄지 않으면 멈춘다.
function shrink(scope, sel){
  scope.querySelectorAll(sel).forEach(t => { const f = parseFloat(getComputedStyle(t).fontSize); if (f > 20) t.style.fontSize = (f * .94) + 'px'; });
}
function shrinkNum(scope){
  scope.querySelectorAll('.num').forEach(nm => { const w = nm.offsetWidth; if (w > 56) {
    nm.style.width = nm.style.height = (w * .94) + 'px';
    nm.style.fontSize = (parseFloat(getComputedStyle(nm).fontSize) * .94) + 'px'; } });
}
function fitH(el, extra){
  let n = 0, prev = Infinity;
  while (el.scrollHeight > el.clientHeight + 1 && n++ < 40) {
    const over = el.scrollHeight - el.clientHeight;
    if (over >= prev) break;          // 줄여도 안 줄어듦 = 글자 탓이 아님 → 그만
    prev = over;
    shrink(el, TXT); shrinkNum(el);
    if (extra) extra.forEach(x => shrink(x, TXT));
  }
}
// 아래 안내 카드(.foot)는 높이가 고정이라 클수록 본문 칸이 좁아진다. 본문 칸이 넘치면 안내 카드 글자부터
// 줄인다(큰 글 44px·작은 줄 30px까지) — 안내 카드만 크고 본문이 작아지던 문제(2026-10-15)
const bodyCards = [...document.querySelectorAll('.main .card:not(.tablecard), .main .col')];
const bodyOver = () => bodyCards.some(c => c.scrollHeight > c.clientHeight + 1);
for (let k = 0; k < 30 && bodyOver(); k++) {
  let changed = false;
  document.querySelectorAll('.foot .mid, .foot .note2').forEach(t => {
    const f = parseFloat(getComputedStyle(t).fontSize), floor = t.classList.contains('note2') ? 30 : 44;
    if (f > floor) { t.style.fontSize = Math.max(floor, f * .94) + 'px'; changed = true; } });
  if (!changed) break;
}
document.querySelectorAll('.card:not(.tablecard), .col').forEach(c => fitH(c));
const main = document.querySelector('.main');
// 본문이 넘치면 아래 안내 카드(.foot) 글자도 같은 비율로 줄인다 — 안내 카드만 크고 본문이 작아지지 않게
if (main && !main.querySelector('.tablecard')) { main.style.overflow = 'hidden'; fitH(main, [...document.querySelectorAll('.foot')]); }
"""


def set_series(series):
    STATE["series"] = series if series in SERIES else "policy"
    pal = SERIES[STATE["series"]]
    C["navy"] = pal["main"]          # 메인 색 자리(타이틀 바·썸네일 영역·단계 이름)
    C["point"] = pal["point"]
    C["chip_after"] = pal["chip_after"]


def build_html(spec, font_css):
    STATE["circle"] = 0
    STATE["style"] = spec.get("icon_style", "circle")
    body = LAYOUTS[spec["layout"]](spec)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{font_css}"><style>{css()}</style></head>
<body><div class="frame">{body}</div><script>document.fonts.ready.then(()=>{{{FIT_JS} document.body.dataset.ready=1;}});</script></body></html>"""


def main(spec_path, only=None):
    spec_path = Path(spec_path).resolve()
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    STATE["dir"] = spec_path.parent
    set_series(data.get("series", "policy"))
    out_dir = spec_path.parent / "out"
    out_dir.mkdir(exist_ok=True)
    font_css = os.environ.get("FONT_CSS") or (HERE.parent / "fonts" / "local.css").resolve().as_uri()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"))
        page_ = b.new_page(viewport={"width": SIZE, "height": SIZE})
        for img in data["images"]:
            if only and img["file"] not in only:
                continue
            html_path = out_dir / f'{img["file"]}.html'
            html_path.write_text(build_html(img, font_css), encoding="utf-8")
            page_.goto(html_path.resolve().as_uri())
            page_.wait_for_selector("body[data-ready]")
            page_.screenshot(path=str(out_dir / f'{img["file"]}.png'))
            print("저장:", img["file"])
        b.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "examples" / "생계비계좌_spec.json", sys.argv[2:])
