"""
아이콘 라이브러리 (모두 viewBox 0 0 220 170, 남색 외곽선 + 연한 면 + 바닥 그림자)

이름 규칙
    "bus"                  → 기본 아이콘
    "calendar"             → 달력 (파랑 머리, 칸 1개 강조)
    "calendar_red:2"       → 빨강 머리, 연속 2칸 강조
    "calendar_green:even"  → 초록 머리, 짝수 칸 무늬 / ":odd" 홀수 칸 무늬 / ":5" 연속 5칸
    머리 색: blue(기본), red, green, orange

icon(name, circle=None) 으로 SVG 문자열을 얻는다. circle에 색을 주면 뒤에 파스텔 원을 깐다.
"""
NAVY = "#1F3A5F"
GREEN = "#2E9E6B"
AMBER = "#E8A33D"
CORAL = "#E05A47"
BLUE = "#3a76c4"
BLUE_L = "#cfe0f3"
BLUE_LL = "#e6eff9"
LINE = "#b9c4d2"
S = f'stroke="{NAVY}" stroke-width="5" stroke-linejoin="round"'

# 아이콘 뒤 파스텔 원 색 (순서대로 돌려 씀)
CIRCLES = ["#dff0dc", "#fdeec8", "#dcebf8", "#f9e0d9", "#e9e2f5"]


def burst(x, y, color=AMBER, flip=False):
    """강조용 짧은 선 3개"""
    s = -1 if flip else 1
    return (f'<g stroke="{color}" stroke-width="6" stroke-linecap="round">'
            f'<line x1="{x}" y1="{y}" x2="{x - 14 * s}" y2="{y - 16}"/>'
            f'<line x1="{x + 8 * s}" y1="{y + 8}" x2="{x + 24 * s}" y2="{y + 2}"/>'
            f'<line x1="{x - 6 * s}" y1="{y + 4}" x2="{x - 22 * s}" y2="{y - 2}"/></g>')


def lines(x, y, widths, step=16, h=7, color=LINE):
    return "".join(f'<rect x="{x}" y="{y + i * step}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}"/>'
                   for i, w in enumerate(widths))


def check_badge(cx, cy, r=24):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}" stroke="#fff" stroke-width="4"/>'
            f'<path d="M{cx - r * .45} {cy} L{cx - r * .1} {cy + r * .35} L{cx + r * .45} {cy - r * .3}" '
            f'fill="none" stroke="#fff" stroke-width="{r * .28}" stroke-linecap="round" stroke-linejoin="round"/>')


# ------------------------------------------------------------
# 달력: 머리 색 + 강조 칸 (15칸 = 5열 x 3행)
# ------------------------------------------------------------
CAL_HEAD = {"blue": BLUE, "red": "#ef6b5e", "green": GREEN, "orange": "#f0a032"}
CAL_HL = {"blue": "#9cc3ec", "red": "#f3a79d", "green": "#7fcf9f", "orange": "#f6c477"}


def calendar(head="blue", mode="1"):
    hc, hl = CAL_HEAD.get(head, BLUE), CAL_HL.get(head, "#9cc3ec")
    if mode == "even":
        on = {i for i in range(15) if i % 2 == 1}
    elif mode == "odd":
        on = {i for i in range(15) if i % 2 == 0}
    elif mode.isdigit():
        n = max(1, min(int(mode), 10))
        start = 6 if n <= 4 else 5
        on = set(range(start, start + n))
    else:
        on = {9}
    symbol = ""
    if mode == "sun":           # 여름: 해
        on, symbol = set(), (f'<circle cx="114" cy="101" r="17" fill="#f5b21b"/>' +
            "".join(f'<line x1="114" y1="74" x2="114" y2="80" stroke="#f5b21b" stroke-width="5" stroke-linecap="round" transform="rotate({a} 114 101)"/>' for a in range(0, 360, 45)))
    elif mode == "snow":        # 겨울: 눈송이
        on, symbol = set(), "".join(f'<line x1="114" y1="76" x2="114" y2="126" stroke="#3a76c4" stroke-width="6" stroke-linecap="round" transform="rotate({a} 114 101)"/>'
                                     f'<path d="M106 84 L114 92 L122 84" fill="none" stroke="#3a76c4" stroke-width="4" stroke-linecap="round" transform="rotate({a} 114 101)"/>' for a in (0, 60, 120, 180, 240, 300))
    cells = "" if symbol else "".join(
        f'<rect x="{58 + (i % 5) * 23}" y="{72 + (i // 5) * 22}" width="17" height="15" rx="3" '
        f'fill="{hl if i in on else "#e6e6e6"}"/>' for i in range(15))
    rings = "".join(f'<circle cx="{x}" cy="30" r="8" fill="none" stroke="{NAVY}" stroke-width="5"/>'
                    for x in (80, 104, 128, 152))
    return (f'<path d="M40 142 L58 44 H176 L192 142 Z" fill="#d5dde8"/>'
            f'<rect x="44" y="34" width="140" height="112" rx="10" fill="#fff" {S}/>'
            f'<path d="M49 36 H179 Q182 36 182 40 V60 H46 V40 Q46 36 49 36 Z" fill="{hc}"/>'
            f'{rings}{cells}{symbol}')


# ------------------------------------------------------------
# 아이콘 본문 (그림자·원 배경은 icon()이 붙임)
# ------------------------------------------------------------
BODIES = {
    # --- 돈·금융 ---
    "passbook": f'''<g transform="rotate(-12 110 90)">
      <rect x="14" y="40" width="190" height="104" rx="12" fill="#fff" stroke="{NAVY}" stroke-width="6"/>
      <rect x="22" y="50" width="174" height="16" fill="{BLUE_L}"/><rect x="22" y="70" width="174" height="64" fill="{BLUE_LL}"/>
      <g stroke="#a9c4e6" stroke-width="2.5"><line x1="22" y1="86" x2="196" y2="86"/><line x1="22" y1="102" x2="196" y2="102"/>
      <line x1="22" y1="118" x2="196" y2="118"/><line x1="84" y1="50" x2="84" y2="134"/><line x1="146" y1="50" x2="146" y2="134"/></g></g>''',
    "milk": f'''
      <path d="M70 46 L92 22 H140 L162 46 V150 H70 Z" fill="#fff" {S}/>
      <path d="M92 22 L114 46 H70 Z M140 22 L162 46 H114 Z" fill="#e8eef5" {S}/>
      <path d="M70 92 Q94 76 116 92 T162 92 V150 H70 Z" fill="#5b8fd1"/>
      <path d="M114 46 V150" stroke="{NAVY}" stroke-width="3" opacity=".25"/>''',
    "calculator": f'''<g transform="rotate(-8 112 84)">
      <rect x="56" y="14" width="116" height="136" rx="16" fill="#e3e9f1" {S}/>
      <rect x="70" y="28" width="88" height="28" rx="5" fill="#6aa0d8"/>
      {"".join(f'<rect x="{70 + c * 23}" y="{66 + r * 24}" width="18" height="18" rx="4" fill="{"#f0a032" if (c == 3 and r >= 1) else "#7d8ea3"}"/>' for r in range(3) for c in range(4))}</g>''',
    "piggy_bank": f'''
      <ellipse cx="108" cy="96" rx="66" ry="48" fill="#f6b6c0" {S}/>
      <path d="M152 70 Q172 62 178 78 Q186 92 170 100" fill="#f6b6c0" {S}/>
      <ellipse cx="176" cy="92" rx="14" ry="12" fill="#f39aa8" {S}/>
      <circle cx="152" cy="82" r="5" fill="{NAVY}"/>
      <path d="M86 52 L96 34 L110 50" fill="#f39aa8" {S}/>
      <rect x="66" y="132" width="18" height="18" rx="5" fill="#f39aa8" {S}/><rect x="128" y="132" width="18" height="18" rx="5" fill="#f39aa8" {S}/>
      <rect x="92" y="52" width="34" height="8" rx="4" fill="{NAVY}"/>
      <circle cx="109" cy="28" r="16" fill="#f5c542" stroke="#c9961b" stroke-width="4"/>''',
    "wallet": f'''
      <rect x="34" y="40" width="130" height="34" rx="8" fill="#6aa0d8" {S} transform="rotate(-8 100 56)"/>
      <rect x="50" y="34" width="120" height="34" rx="8" fill="#f5c542" stroke="{NAVY}" stroke-width="5" transform="rotate(-4 110 50)"/>
      <rect x="26" y="58" width="168" height="90" rx="16" fill="#a8703f" stroke="#6e4422" stroke-width="5"/>
      <rect x="140" y="84" width="56" height="38" rx="12" fill="#8c5a30" stroke="#6e4422" stroke-width="5"/>
      <circle cx="160" cy="103" r="8" fill="#f5c542"/>''',
    "coins": f'''
      {"".join(f'<ellipse cx="{x}" cy="{y}" rx="40" ry="14" fill="#f5c542" stroke="#c9961b" stroke-width="5"/>' for x, y in ((80, 132), (80, 116), (80, 100), (146, 132), (146, 116)))}
      <circle cx="140" cy="58" r="30" fill="#f5c542" stroke="#c9961b" stroke-width="5"/>
      <text x="140" y="70" text-anchor="middle" font-size="34" font-weight="900" fill="#c9961b" font-family="sans-serif">₩</text>''',
    "card": f'''<g transform="rotate(-10 110 86)">
      <rect x="28" y="38" width="164" height="104" rx="14" fill="#5b8fd1" {S}/>
      <rect x="28" y="60" width="164" height="20" fill="{NAVY}"/>
      <rect x="44" y="96" width="36" height="26" rx="5" fill="#f5c542"/>
      {lines(96, 104, [70, 50], 14, 7, "#cfe0f3")}</g>''',
    "bank": f'''
      <polygon points="112,14 196,56 28,56" fill="#d6dfeb" {S}/>
      <rect x="36" y="56" width="152" height="12" fill="#c3cfde" stroke="{NAVY}" stroke-width="4"/>
      {"".join(f'<rect x="{50 + i * 40}" y="70" width="24" height="56" fill="#eef2f7" stroke="{NAVY}" stroke-width="4"/>' for i in range(4))}
      <rect x="30" y="126" width="164" height="12" fill="#c3cfde" stroke="{NAVY}" stroke-width="4"/>
      <rect x="22" y="138" width="180" height="10" fill="#b4c2d4" stroke="{NAVY}" stroke-width="4"/>''',

    # --- 서류 ---
    "document": f'''
      <path d="M62 18 H140 L172 50 V146 H62 Z" fill="#fff" {S}/>
      <path d="M140 18 V50 H172" fill="{BLUE_LL}" {S}/>{lines(80, 66, [74, 74, 64, 44], 18)}''',
    "doc_check": f'''
      <path d="M56 16 H134 L166 48 V144 H56 Z" fill="#fff" {S}/>
      <path d="M134 16 V48 H166" fill="{BLUE_LL}" {S}/>{lines(74, 62, [74, 60, 70, 40], 18)}{check_badge(160, 124, 28)}''',
    "doc_pen": f'''
      <rect x="44" y="20" width="100" height="128" rx="8" fill="#fff" {S}/>
      <rect x="44" y="20" width="16" height="128" rx="6" fill="#5b8fd1"/>{lines(72, 46, [56, 56, 44, 56], 18)}
      <g transform="rotate(35 150 100)"><rect x="138" y="30" width="24" height="96" rx="4" fill="#f5c542" {S}/>
      <path d="M138 126 L150 150 L162 126 Z" fill="#f2d7b0" {S}/><rect x="138" y="30" width="24" height="14" fill="#f39aa8" {S}/></g>''',
    "doc_stack": f'''
      <rect x="40" y="30" width="104" height="120" rx="8" fill="#cddcf0" {S}/>
      <rect x="58" y="22" width="104" height="120" rx="8" fill="#e3ecf8" {S}/>
      <rect x="76" y="14" width="104" height="120" rx="8" fill="#fff" {S}/>{lines(92, 38, [72, 72, 60, 72, 44], 17)}''',
    "doc_ban": f'''
      <path d="M48 18 H126 L158 50 V146 H48 Z" fill="#fff" {S}/>{lines(66, 62, [74, 60, 70, 40], 18)}
      <circle cx="156" cy="118" r="32" fill="#fff" stroke="{CORAL}" stroke-width="10"/>
      <line x1="134" y1="96" x2="178" y2="140" stroke="{CORAL}" stroke-width="10" stroke-linecap="round"/>''',
    "clipboard": f'''
      <rect x="58" y="22" width="108" height="128" rx="10" fill="#c99a62" {S}/>
      <rect x="70" y="36" width="84" height="104" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="3"/>
      <rect x="88" y="14" width="48" height="20" rx="6" fill="#b9c4d2" {S}/>
      {"".join(f'<rect x="80" y="{52 + i * 22}" width="12" height="12" rx="2" fill="none" stroke="{NAVY}" stroke-width="3"/>' for i in range(3))}
      {lines(98, 54, [44, 44, 44], 22)}''',
    "folder": f'''
      <path d="M30 40 H86 L100 54 H186 V140 H30 Z" fill="#f2c35a" {S}/>
      <rect x="58" y="34" width="100" height="70" rx="4" fill="#fff" stroke="#c9ced6" stroke-width="3" transform="rotate(4 108 70)"/>
      <path d="M22 72 H178 L190 142 H34 Z" fill="#f8d47a" {S}/>''',
    "stamp": f'''
      <path d="M40 128 L150 114 L188 146 L70 156 Z" fill="#f4f1ea" stroke="#d8d2c4" stroke-width="3"/>
      <ellipse cx="128" cy="34" rx="26" ry="22" fill="#c27a45" stroke="#8a5229" stroke-width="4"/>
      <path d="M118 52 Q112 80 104 96 H152 Q144 80 138 52 Z" fill="#c27a45" stroke="#8a5229" stroke-width="4"/>
      <rect x="84" y="94" width="88" height="34" rx="8" fill="{NAVY}"/><rect x="80" y="122" width="96" height="10" rx="3" fill="#2c4f7c"/>
      {burst(56, 50)}''',
    "envelope": f'''<g transform="rotate(-6 112 90)">
      <rect x="30" y="40" width="164" height="104" rx="10" fill="#fbf9f4" {S}/>
      <path d="M34 46 L112 104 L190 46" fill="none" stroke="{NAVY}" stroke-width="4"/>
      <path d="M34 140 L94 92 M190 140 L130 92" stroke="#9fb4cf" stroke-width="2.5"/></g>''',

    # --- 장소·건물 ---
    "house": f'''
      <ellipse cx="54" cy="110" rx="26" ry="34" fill="#7cc576"/><ellipse cx="170" cy="112" rx="24" ry="30" fill="#7cc576"/>
      <rect x="62" y="74" width="98" height="70" fill="#fdf3e1" {S}/>
      <path d="M48 80 L111 26 L174 80" fill="none" stroke="{NAVY}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
      <rect x="98" y="102" width="26" height="42" fill="#a8703f" stroke="{NAVY}" stroke-width="4"/>
      <rect x="132" y="92" width="20" height="20" fill="#9cc3ec" stroke="{NAVY}" stroke-width="3"/>
      <rect x="70" y="92" width="20" height="20" fill="#9cc3ec" stroke="{NAVY}" stroke-width="3"/>''',
    "facility": f'''
      <ellipse cx="34" cy="118" rx="18" ry="28" fill="#7cc576"/><ellipse cx="190" cy="118" rx="18" ry="28" fill="#7cc576"/>
      <rect x="44" y="54" width="136" height="90" fill="#fdf3e1" {S}/>
      <rect x="38" y="44" width="148" height="14" rx="3" fill="#e9875c" {S}/>
      {"".join(f'<rect x="{58 + c * 30}" y="{68 + r * 26}" width="20" height="16" fill="#9cc3ec" stroke="{NAVY}" stroke-width="3"/>' for r in range(2) for c in range(4))}
      <rect x="96" y="114" width="32" height="30" fill="#6aa0d8" stroke="{NAVY}" stroke-width="4"/>''',
    "shop": f'''
      <rect x="44" y="70" width="136" height="76" fill="#fdf3e1" {S}/>
      <path d="M36 44 H188 L196 74 H28 Z" fill="#fff" {S}/>
      {"".join(f'<path d="M{36 + i * 32} 44 H{52 + i * 32} L{56 + i * 32} 74 H{32 + i * 32} Z" fill="{CORAL}"/>' for i in range(5))}
      <rect x="58" y="88" width="50" height="36" fill="#9cc3ec" stroke="{NAVY}" stroke-width="4"/>
      <rect x="124" y="88" width="38" height="58" fill="#6aa0d8" stroke="{NAVY}" stroke-width="4"/>''',
    "school": f'''
      <rect x="40" y="64" width="144" height="80" fill="#fdf3e1" {S}/>
      <path d="M90 64 V40 H134 V64" fill="#fdf3e1" {S}/>
      <circle cx="112" cy="50" r="7" fill="#fff" stroke="{NAVY}" stroke-width="3"/>
      <line x1="112" y1="40" x2="112" y2="16" stroke="{NAVY}" stroke-width="4"/><path d="M112 16 H134 L128 23 L134 30 H112" fill="{CORAL}"/>
      {"".join(f'<rect x="{54 + c * 32}" y="78" width="20" height="18" fill="#9cc3ec" stroke="{NAVY}" stroke-width="3"/>' for c in range(4))}
      <rect x="98" y="108" width="28" height="36" fill="#a8703f" stroke="{NAVY}" stroke-width="4"/>''',
    "hospital": f'''
      <rect x="46" y="40" width="132" height="104" fill="#fff" {S}/>
      <rect x="90" y="18" width="44" height="30" fill="#fff" {S}/>
      <path d="M106 24 H118 V30 H124 V40 H118 V46 H106 V40 H100 V30 H106 Z" fill="{CORAL}"/>
      {"".join(f'<rect x="{60 + c * 30}" y="{60 + r * 26}" width="18" height="16" fill="#9cc3ec" stroke="{NAVY}" stroke-width="3"/>' for r in range(2) for c in range(4))}
      <rect x="96" y="112" width="32" height="32" fill="#6aa0d8" stroke="{NAVY}" stroke-width="4"/>''',

    # --- 교통·여행 ---
    "bus": f'''
      <rect x="20" y="38" width="184" height="94" rx="18" fill="#fff" {S}/>
      <rect x="20" y="98" width="184" height="12" fill="#6aa0d8"/>
      {"".join(f'<rect x="{32 + i * 34}" y="52" width="26" height="34" rx="4" fill="#3d5a80"/>' for i in range(4))}
      <rect x="168" y="52" width="26" height="44" rx="5" fill="#3d5a80"/>
      <circle cx="58" cy="134" r="16" fill="#3a3d42" stroke="#fff" stroke-width="4"/><circle cx="164" cy="134" r="16" fill="#3a3d42" stroke="#fff" stroke-width="4"/>''',
    "airplane": f'''<g transform="rotate(-14 110 86)">
      <path d="M28 86 Q28 74 46 74 H170 Q196 74 200 86 Q196 98 170 98 H46 Q28 98 28 86 Z" fill="#fff" {S}/>
      <path d="M96 76 L128 30 H146 L128 76 Z" fill="#6aa0d8" {S}/>
      <path d="M96 96 L128 142 H146 L128 96 Z" fill="#6aa0d8" {S}/>
      <path d="M40 76 L30 50 H44 L60 76 Z" fill="#6aa0d8" {S}/>
      {"".join(f'<circle cx="{70 + i * 16}" cy="84" r="4" fill="#6aa0d8"/>' for i in range(6))}</g>''',
    "suitcase": f'''
      <path d="M90 34 V18 H134 V34" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linejoin="round"/>
      <rect x="62" y="32" width="100" height="108" rx="14" fill="#f5b94a" {S}/>
      <line x1="90" y1="44" x2="90" y2="128" stroke="#d38f1f" stroke-width="5"/><line x1="134" y1="44" x2="134" y2="128" stroke="#d38f1f" stroke-width="5"/>
      <circle cx="80" cy="146" r="7" fill="{NAVY}"/><circle cx="144" cy="146" r="7" fill="{NAVY}"/>''',
    "map_pin": f'''
      <path d="M26 56 L80 40 L140 56 L196 40 V136 L140 152 L80 136 L26 152 Z" fill="#d6ecd2" {S}/>
      <path d="M80 40 V136 M140 56 V152" stroke="{NAVY}" stroke-width="3"/>
      <path d="M26 104 Q90 86 196 112" fill="none" stroke="#f5c542" stroke-width="6"/>
      <path d="M118 108 Q86 72 86 52 A32 32 0 0 1 150 52 Q150 72 118 108 Z" fill="{CORAL}" {S}/>
      <circle cx="118" cy="52" r="12" fill="#fff"/>''',
    "ticket": f'''<g transform="rotate(-10 110 86)">
      <path d="M24 46 H196 V72 A14 14 0 0 0 196 100 V126 H24 V100 A14 14 0 0 0 24 72 Z" fill="#5b8fd1" {S}/>
      <rect x="44" y="60" width="96" height="52" rx="6" fill="#fff"/>
      <path d="M50 106 L80 76 L100 94 L112 84 L134 106 Z" fill="#7cc576"/>
      <line x1="160" y1="52" x2="160" y2="120" stroke="#fff" stroke-width="4" stroke-dasharray="8 6"/></g>''',

    # --- 생활 ---
    "bed": f'''
      <rect x="28" y="40" width="26" height="104" rx="6" fill="#a8703f" {S}/>
      <rect x="166" y="78" width="26" height="66" rx="6" fill="#a8703f" {S}/>
      <rect x="50" y="90" width="120" height="34" rx="6" fill="#fff" {S}/>
      <rect x="92" y="84" width="80" height="42" rx="8" fill="#5b8fd1" {S}/>
      <rect x="56" y="72" width="40" height="22" rx="10" fill="#fff" {S}/>''',
    "meal": f'''
      <ellipse cx="110" cy="96" rx="80" ry="22" fill="#5a5f66" {S}/>
      <path d="M30 96 Q34 146 110 146 Q186 146 190 96 Z" fill="#3a3d42" {S}/>
      <path d="M44 92 Q60 72 84 80 Q100 64 122 76 Q146 66 162 82 Q178 84 178 94" fill="#f2c35a"/>
      <circle cx="110" cy="80" r="16" fill="#fff"/><circle cx="110" cy="80" r="8" fill="#f5b21b"/>
      <path d="M58 88 L80 84 M140 86 L162 90" stroke="#7cc576" stroke-width="8" stroke-linecap="round"/>''',
    "phone": f'''
      <path d="M44 76 Q44 40 110 40 Q176 40 176 76 L162 86 L144 68 H76 L58 86 Z" fill="{NAVY}" {S}/>
      <rect x="54" y="80" width="112" height="66" rx="14" fill="{NAVY}" {S}/>
      <rect x="80" y="88" width="60" height="16" rx="4" fill="#9cc3ec"/>
      {"".join(f'<circle cx="{88 + c * 22}" cy="{116 + r * 16}" r="5" fill="#fff"/>' for r in range(2) for c in range(3))}''',
    "smartphone": f'''
      <rect x="66" y="14" width="84" height="146" rx="16" fill="{NAVY}" {S}/>
      <rect x="74" y="28" width="68" height="112" rx="6" fill="#e6eff9"/>
      <rect x="82" y="40" width="44" height="22" rx="10" fill="#6aa0d8"/><rect x="92" y="70" width="44" height="22" rx="10" fill="#7cc576"/>
      <circle cx="108" cy="150" r="4" fill="#fff"/>''',
    "laptop": f'''
      <rect x="44" y="26" width="132" height="90" rx="8" fill="#5b6b80" {S}/>
      <rect x="54" y="36" width="112" height="70" rx="3" fill="#cfe0f3"/>
      <path d="M24 122 H196 L186 140 H34 Z" fill="#b9c4d2" {S}/>
      <rect x="76" y="44" width="58" height="56" fill="#fff"/>{lines(84, 54, [42, 42, 30], 14, 6)}''',
    "monitor": f'''
      <rect x="30" y="20" width="160" height="106" rx="10" fill="{NAVY}" {S}/>
      <rect x="42" y="32" width="136" height="82" rx="4" fill="#5b8fd1"/>
      <circle cx="110" cy="73" r="26" fill="none" stroke="#fff" stroke-width="5"/>
      <path d="M84 73 H136 M110 47 Q96 73 110 99 Q124 73 110 47" fill="none" stroke="#fff" stroke-width="4"/>
      <rect x="98" y="126" width="24" height="16" fill="#b9c4d2"/><rect x="72" y="140" width="76" height="10" rx="4" fill="#b9c4d2" {S}/>''',
    "clock": f'''
      <circle cx="110" cy="84" r="62" fill="#fff" {S}/>
      <path d="M110 84 L110 22 A62 62 0 0 1 164 54 Z" fill="#f6c477" opacity=".8"/>
      {"".join(f'<line x1="110" y1="30" x2="110" y2="38" stroke="{NAVY}" stroke-width="5" transform="rotate({a} 110 84)"/>' for a in range(0, 360, 30))}
      <line x1="110" y1="84" x2="110" y2="46" stroke="{NAVY}" stroke-width="7" stroke-linecap="round"/>
      <line x1="110" y1="84" x2="140" y2="96" stroke="{NAVY}" stroke-width="7" stroke-linecap="round"/>
      <circle cx="110" cy="84" r="7" fill="{NAVY}"/>''',

    # --- 개념 ---
    "ai": f'''
      <rect x="54" y="30" width="112" height="112" rx="18" fill="{NAVY}" {S}/>
      {"".join(f'<line x1="{x}" y1="16" x2="{x}" y2="30" stroke="{NAVY}" stroke-width="6"/><line x1="{x}" y1="142" x2="{x}" y2="156" stroke="{NAVY}" stroke-width="6"/>' for x in (82, 110, 138))}
      {"".join(f'<line x1="40" y1="{y}" x2="54" y2="{y}" stroke="{NAVY}" stroke-width="6"/><line x1="166" y1="{y}" x2="180" y2="{y}" stroke="{NAVY}" stroke-width="6"/>' for y in (58, 86, 114))}
      <text x="110" y="104" text-anchor="middle" font-size="50" font-weight="900" fill="#fff" font-family="sans-serif">AI</text>''',
    "gear": f'''
      <g transform="translate(96 86)">{"".join(f'<rect x="-11" y="-62" width="22" height="24" rx="4" fill="#4a6688" transform="rotate({a})"/>' for a in range(0, 360, 45))}
      <circle r="44" fill="#4a6688" {S}/><circle r="18" fill="#fff" {S}/></g>
      <g transform="translate(166 126)">{"".join(f'<rect x="-6" y="-32" width="12" height="14" rx="3" fill="#7fa3cf" transform="rotate({a})"/>' for a in range(0, 360, 60))}
      <circle r="22" fill="#7fa3cf" stroke="{NAVY}" stroke-width="4"/><circle r="8" fill="#fff"/></g>''',
    "robot": f'''
      <line x1="110" y1="14" x2="110" y2="32" stroke="{NAVY}" stroke-width="6"/><circle cx="110" cy="12" r="8" fill="{CORAL}"/>
      <rect x="50" y="32" width="120" height="82" rx="28" fill="#fff" {S}/>
      <rect x="66" y="48" width="88" height="48" rx="18" fill="{NAVY}"/>
      <path d="M86 70 Q92 62 98 70 M122 70 Q128 62 134 70" fill="none" stroke="#7fe0c0" stroke-width="5" stroke-linecap="round"/>
      <path d="M98 82 Q110 90 122 82" fill="none" stroke="#7fe0c0" stroke-width="5" stroke-linecap="round"/>
      <rect x="70" y="114" width="80" height="34" rx="12" fill="#fff" {S}/><circle cx="110" cy="130" r="7" fill="#6aa0d8"/>''',
    "wifi": f'''
      {"".join(f'<path d="M{110 - r} {120 - r * .55} Q110 {120 - r * 1.25} {110 + r} {120 - r * .55}" fill="none" stroke="{BLUE}" stroke-width="12" stroke-linecap="round"/>' for r in (30, 58, 86))}
      <circle cx="110" cy="122" r="12" fill="{BLUE}"/>''',
    "chart": f'''
      <rect x="34" y="20" width="152" height="128" rx="10" fill="#fff" {S}/>
      {"".join(f'<rect x="{56 + i * 32}" y="{126 - h}" width="22" height="{h}" rx="3" fill="{c}"/>' for i, (h, c) in enumerate(((34, "#9cc3ec"), (56, "#6aa0d8"), (46, "#9cc3ec"), (84, BLUE))))}
      <path d="M52 92 L86 72 L118 80 L170 34" fill="none" stroke="{GREEN}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M154 32 L172 32 L170 50" fill="none" stroke="{GREEN}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>''',
    "magnifier": f'''
      <path d="M48 20 H126 L150 44 V142 H48 Z" fill="#fff" {S}/>{lines(64, 52, [64, 52, 64, 40], 18)}
      <circle cx="138" cy="104" r="32" fill="#e6eff9" fill-opacity=".85" stroke="{NAVY}" stroke-width="9"/>
      <line x1="162" y1="128" x2="190" y2="156" stroke="{NAVY}" stroke-width="14" stroke-linecap="round"/>''',
    "shield": f'''
      <path d="M110 16 L172 38 V86 Q172 132 110 156 Q48 132 48 86 V38 Z" fill="#5b8fd1" {S}/>
      <path d="M110 30 L160 48 V86 Q160 122 110 142 Z" fill="#7fa9dc"/>
      <path d="M100 58 H120 V76 H138 V96 H120 V114 H100 V96 H82 V76 H100 Z" fill="#fff"/>''',
    "person": f'''
      <circle cx="110" cy="56" r="30" fill="#f6d2b8" {S}/>
      <path d="M80 50 Q84 22 110 24 Q138 22 140 50 Q130 36 110 38 Q92 36 80 50 Z" fill="#5a3e2b"/>
      <path d="M50 152 Q52 98 110 98 Q168 98 170 152 Z" fill="#7fa9dc" {S}/>''',
    "people": f'''
      <circle cx="74" cy="60" r="24" fill="#f6d2b8" {S}/><path d="M30 150 Q32 102 74 102 Q116 102 118 150 Z" fill="#7fa9dc" {S}/>
      <circle cx="150" cy="58" r="26" fill="#f6d2b8" {S}/><path d="M104 150 Q106 100 150 100 Q194 100 196 150 Z" fill="#7cc576" {S}/>
      <circle cx="112" cy="94" r="18" fill="#f6d2b8" {S}/><path d="M82 154 Q84 120 112 120 Q140 120 142 154 Z" fill="#f5b94a" {S}/>''',
    "heart_pulse": f'''
      <path d="M110 150 Q30 96 34 58 Q40 22 76 24 Q98 26 110 48 Q122 26 144 24 Q180 22 186 58 Q190 96 110 150 Z" fill="#f28b82" {S}/>
      <path d="M40 82 H82 L94 62 L110 104 L124 72 L134 82 H180" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>''',
    "info": f'''
      <circle cx="110" cy="84" r="60" fill="#5b8fd1"/>
      <circle cx="110" cy="54" r="10" fill="#fff"/><rect x="100" y="72" width="20" height="56" rx="10" fill="#fff"/>''',
    "megaphone": f'''
      <path d="M44 66 H82 L156 30 V140 L82 104 H44 Z" fill="#f5b94a" {S}/>
      <rect x="56" y="104" width="24" height="40" rx="6" fill="#f5b94a" {S}/>
      {burst(190, 60, CORAL, flip=True)}''',
    "exchange": f'''
      <path d="M50 52 H130 V30 L178 66 L130 102 V80 H50 Z" fill="{GREEN}" stroke="#1e7d48" stroke-width="4" stroke-linejoin="round"/>
      <path d="M170 98 H96 V76 L48 112 L96 148 V126 H170 Z" fill="{BLUE}" stroke="#285b9a" stroke-width="4" stroke-linejoin="round"/>
      {burst(32, 50)}''',
    "warning": f'''
      <circle cx="122" cy="84" r="58" fill="{CORAL}"/>
      <rect x="114" y="46" width="16" height="50" rx="8" fill="#fff"/><circle cx="122" cy="114" r="9" fill="#fff"/>{burst(48, 66)}''',
    "warning_triangle": f'''
      <path d="M112 18 Q120 18 125 26 L196 140 Q200 150 190 152 H34 Q24 150 28 140 L99 26 Q104 18 112 18 Z" fill="{CORAL}"/>
      <rect x="104" y="54" width="16" height="56" rx="8" fill="#fff"/><circle cx="112" cy="130" r="10" fill="#fff"/>
      {burst(178, 40, CORAL, flip=True)}''',
    "check": f'''
      <circle cx="112" cy="88" r="54" fill="#1f9d57"/>
      <path d="M86 88 L104 106 L140 70" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
      {burst(160, 38, "#1f9d57", flip=True)}''',
    "ban": f'''
      <circle cx="110" cy="84" r="56" fill="#fff" stroke="{CORAL}" stroke-width="16"/>
      <line x1="72" y1="46" x2="148" y2="122" stroke="{CORAL}" stroke-width="16" stroke-linecap="round"/>''',
}

# 예전 이름 호환
ALIASES = {"desk_calendar": "calendar:1", "desk_calendar_red": "calendar_red:1"}

# 원 배경을 깔지 않는 아이콘 (자체가 원 모양)
NO_CIRCLE = {"check", "warning", "info", "ban"}


def icon(name, circle=None):
    """name → SVG. circle: 파스텔 원 색(None이면 원 없음)"""
    name = ALIASES.get(name, name)
    base, _, arg = name.partition(":")
    if base.startswith("calendar"):
        head = base.split("_", 1)[1] if "_" in base else "blue"
        body = calendar(head, arg or "1")
    else:
        body = BODIES.get(base)
        if body is None:
            body = BODIES["info"]          # 모르는 이름이면 i 아이콘으로 대체
    bg = (f'<circle cx="110" cy="86" r="80" fill="{circle}"/>'
          if circle and base not in NO_CIRCLE else "")
    shadow = '<ellipse cx="112" cy="156" rx="86" ry="9" fill="#000" opacity=".07"/>'
    return f'<svg viewBox="0 0 220 170" xmlns="http://www.w3.org/2000/svg">{bg}{shadow}{body}</svg>'


NAMES = sorted(list(BODIES) + ["calendar", "calendar_red", "calendar_green", "calendar_orange"])
