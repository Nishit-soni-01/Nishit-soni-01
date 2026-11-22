#!/usr/bin/env python3
"""Render animated GitHub README SVG cards. STATIC=1 disables all motion."""

from __future__ import annotations

import base64
import html
import json
import os
import shutil
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths & Environment Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
OUT = Path(os.getenv("OUTPUT_DIR", ROOT / "cards"))
DATA = Path(os.getenv("PROFILE_DATA", ROOT / "contributions.json"))
STATIC = os.getenv("STATIC", "0") == "1"
FONT_FILE = os.getenv("FONT_FILE", "")
PORTRAIT = os.getenv("PORTRAIT", "")

# Theme palette: near-black, warm white, electric neon yellow.
BG = "#050505"
FG = "#F7F7E8"
GREEN = "#DFFF00"
MUTED = "#B8B89F"
BORDER = "#3A3A20"
PANEL = "#10110A"
FONT = "Roboto"

# ---------------------------------------------------------------------------
# Profile & Featured Projects Data
# ---------------------------------------------------------------------------

PROFILE = {
    "name": "NISHIT SONI.",
    "line": "I build intelligent systems and digital experiences that solve real-world problems.",
    "role": "AI/ML ENGINEER  ✳  SOFTWARE DEVELOPER  ✳  DATA SCIENCE",
    "portfolio": "https://nishvay-portfolio-v2.vercel.app/",
    "linkedin": "https://www.linkedin.com/",
    "leetcode": "https://leetcode.com/",
    "resume": os.getenv(
        "RESUME_URL",
        "https://github.com/Nishit-soni-01/Nishit-soni-01/raw/main/Nishit_Soni_Resume.pdf",
    ),
}

REPOS = [
    (
        "Cloudinary Studio",
        "Media workspace for uploading, optimizing, transforming images/videos & background removal.",
        "Next.js · Cloudinary · Prisma · PostgreSQL · Clerk",
        "https://cloudinary-saas-teal.vercel.app/",
    ),
    (
        "InvoiceFlow AI",
        "AI-powered invoicing, customer & payment tracking, PDF generation and Gemini insights.",
        "Next.js · Gemini AI · Database · Email Integration",
        "https://invoiceflow-ai-self.vercel.app/",
    ),
    (
        "AI-Powered Predictive Maintenance",
        "ML telemetry pipeline and Streamlit dashboard predicting grid & motor failures early.",
        "Python · Scikit-learn · Random Forest · Pandas · Streamlit",
        "https://github.com/Nishit-soni-01/AI-Powered-Predictive-Maintenance-for-Electrical-Systems",
    ),
    (
        "VideoTube Backend API",
        "RESTful video hosting API with JWT auth, Cloudinary media pipelines & MongoDB aggregations.",
        "Node.js · Express.js · MongoDB · JWT · Cloudinary",
        "https://github.com/Nishit-soni-01/videtube-backend",
    ),
    (
        "T-Shirt Sales Analysis Dashboard",
        "Power BI dashboard analyzing retail sales, DAX-modeled margins, costs, profits & discounts.",
        "Power BI · DAX · Data Analytics · Data Visualization",
        "https://github.com/Nishit-soni-01/T-Shirt-Sales-Analysis-Dashboard-with-Power-BI",
    ),
]

# ---------------------------------------------------------------------------
# SVG & Font Helpers
# ---------------------------------------------------------------------------


def esc(value: object) -> str:
    """Escape text/attributes for safe XML/SVG output."""
    return html.escape(str(value), quote=True)


def font_rule() -> str:
    """Optionally subset and embed a custom font as a WOFF data URI."""
    if not FONT_FILE:
        return ""

    src = Path(FONT_FILE)
    if not src.is_file() or not shutil.which("pyftsubset"):
        print("FONT_FILE or pyftsubset missing; using Roboto/Arial fallback.")
        return ""

    OUT.mkdir(parents=True, exist_ok=True)
    woff = OUT / "profile-font.woff"
    chars = (
        "NISHIT SONI AI ML ENGINEER SOFTWARE DEVELOPER DATA SCIENCE "
        "PORTFOLIO LINKEDIN LEETCODE CONNECT WITH ME EXPLORE MY WORK "
        "DOWNLOAD RESUME CONTRIBUTIONS ACTIVE DAYS CURRENT STREAK "
        "BUSIEST DAY PROJECTS SMALL STEPS MEANINGFUL PROGRESS"
    )
    for repo in REPOS:
        chars += "".join(repo[:3])

    subprocess.run(
        [
            "pyftsubset",
            str(src),
            f"--text={chars}",
            "--flavor=woff",
            f"--output-file={woff}",
            "--layout-features=*",
        ],
        check=True,
    )
    b64 = base64.b64encode(woff.read_bytes()).decode("ascii")
    return (
        f"@font-face{{font-family:{FONT};"
        f"src:url(data:font/woff;base64,{b64}) format(woff);font-weight:100 900;}}"
    )


FONT_CSS = font_rule()


def doc(width: int, height: int, body: str) -> str:
    """Wrap card body content in a complete SVG document."""
    if STATIC:
        motion = (
            ".enter{opacity:1;transform:none}"
            ".glow{opacity:1}"
            ".floaty{transform:none}"
            ".bar-sweep{stroke-dashoffset:0}"
        )
    else:
        motion = """@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
        @keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}
        @keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
        @keyframes sweep{from{stroke-dashoffset:800}to{stroke-dashoffset:0}}
        .enter{animation:rise .75s cubic-bezier(.2,.8,.2,1) both}
        .glow{animation:pulse 2.4s ease-in-out infinite}
        .floaty{animation:floaty 3.2s ease-in-out infinite}
        .bar-sweep{stroke-dasharray:800;animation:sweep 1.1s ease-out both}"""

    reduced = (
        "@media(prefers-reduced-motion:reduce){"
        "*,*::before,*::after{animation:none!important;transition:none!important}"
        "animate,animateTransform,set{display:none!important}"
        ".enter{opacity:1;transform:none}.glow{opacity:1}"
        ".floaty{transform:none}.bar-sweep{stroke-dashoffset:0}}"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">\n'
        f"<title>Nishit Soni GitHub profile card</title>"
        f"<style>{FONT_CSS}{motion}{reduced}"
        f"text{{font-family:Roboto,Arial,sans-serif}}"
        f".fg{{fill:{FG}}}.muted{{fill:{MUTED}}}.green{{fill:{GREEN}}}</style>\n"
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="2" fill="{BG}" stroke="{BORDER}"/>'
        f'<rect class="glow" x="1" y="1" width="{width - 2}" height="4" fill="{GREEN}"/>'
        f"{body}</svg>"
    )


def save(name: str, svg: str) -> None:
    """Write an SVG string to the output directory."""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# Card Generators
# ---------------------------------------------------------------------------


def hero() -> None:
    portrait = ""
    if PORTRAIT and Path(PORTRAIT).is_file():
        p = Path(PORTRAIT)
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        portrait = (
            '<defs><clipPath id="avatar"><circle cx="690" cy="115" r="65"/></clipPath></defs>'
            f'<image x="625" y="50" width="130" height="130" clip-path="url(#avatar)" '
            f'preserveAspectRatio="xMidYMid slice" xlink:href="data:{mime};base64,{b64}"/>'
            f'<circle class="glow" cx="690" cy="115" r="67" fill="none" stroke="{GREEN}" stroke-width="3"/>'
        )

    body = (
        f'<g class="enter">'
        f'<text x="42" y="50" class="green" font-size="12" letter-spacing="3">HELLO, WELCOME TO MY GITHUB</text>'
        f'<text x="40" y="111" class="fg" font-size="43" font-weight="900">{esc(PROFILE["name"])}</text>'
        f'<text x="42" y="153" class="muted" font-size="16">{esc(PROFILE["line"])}</text>'
        f'<text x="42" y="202" class="green glow" font-size="12" letter-spacing="1.4">{esc(PROFILE["role"])}</text>'
        f"</g>{portrait}"
        f'<path class="bar-sweep" d="M42 246H758" stroke="{BORDER}"/>'
        f'<g class="enter" style="animation-delay:.35s">'
        f'<text x="42" y="278" class="muted" font-size="11">BASED IN INDIA · CREATING WITH PURPOSE</text>'
        f'<text x="758" y="278" text-anchor="end" class="green" font-size="11">01 / INTRODUCTION</text>'
        f"</g>"
    )
    save("01-hero.svg", doc(800, 300, body))


def tiles() -> None:
    items = [
        ("PORTFOLIO", "Explore my work", PROFILE["portfolio"]),
        ("LINKEDIN", "Connect professionally", PROFILE["linkedin"]),
        ("LEETCODE", "Problem-solving journey", PROFILE["leetcode"]),
    ]
    for i, (name, sub, url) in enumerate(items, 1):
        pulse = (
            ""
            if STATIC
            else f'<animate attributeName="opacity" values="0.45;1;0.45" dur="2.2s" begin="{i * .2:.2f}s" repeatCount="indefinite"/>'
        )
        drift = (
            ""
            if STATIC
            else f'<animateTransform attributeName="transform" type="translate" values="0,0;3,-3;0,0" dur="2.4s" begin="{i * .2:.2f}s" repeatCount="indefinite"/>'
        )
        body = (
            f'<a class="enter" style="animation-delay:{i * .16:.2f}s" xlink:href="{esc(url)}">'
            f'<rect x="1" y="1" width="258" height="116" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<text x="20" y="34" class="green" font-size="10">0{i} / CONNECT</text>'
            f'<text x="20" y="68" class="fg" font-size="20" font-weight="800">{name}</text>'
            f'<text x="20" y="94" class="muted" font-size="11">{sub}</text>'
            f'<text x="235" y="35" text-anchor="end" class="green" font-size="18">{pulse}{drift}↗</text>'
            f"</a>"
        )
        save(f"02-tile-{i}.svg", doc(260, 118, body))


def connect_card() -> None:
    items = [
        ("PORTFOLIO", "Explore my work", PROFILE["portfolio"]),
        ("LINKEDIN", "Connect professionally", PROFILE["linkedin"]),
        ("LEETCODE", "Problem-solving journey", PROFILE["leetcode"]),
    ]
    cards = []
    for i, (name, sub, url) in enumerate(items):
        x = 38 + i * 246
        delay = 0.2 + i * 0.15
        pulse = (
            ""
            if STATIC
            else f'<animate attributeName="opacity" values="0.45;1;0.45" dur="2.2s" begin="{i * .25:.2f}s" repeatCount="indefinite"/>'
        )
        arrow_move = (
            ""
            if STATIC
            else f'<animateTransform attributeName="transform" type="translate" values="0,0;3,-3;0,0" dur="2.2s" begin="{i * .25:.2f}s" repeatCount="indefinite"/>'
        )
        cards.append(
            f'<a class="enter" style="animation-delay:{delay:.2f}s" xlink:href="{esc(url)}">'
            f'<g class="floaty" style="animation-delay:{i * .35:.2f}s">'
            f'<rect x="{x}" y="74" width="232" height="106" rx="2" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<text x="{x + 18}" y="102" class="green" font-size="10" letter-spacing="1.4">0{i + 1} / LINK</text>'
            f'<text x="{x + 214}" y="103" text-anchor="end" class="green" font-size="16">{pulse}{arrow_move}↗</text>'
            f'<text x="{x + 18}" y="135" class="fg" font-size="18" font-weight="800">{esc(name)}</text>'
            f'<text x="{x + 18}" y="160" class="muted" font-size="11">{esc(sub)}</text>'
            f"</g></a>"
        )

    body = (
        f'<g class="enter">'
        f'<text x="38" y="38" class="fg" font-size="22" font-weight="900">CONNECT WITH ME.</text>'
        f'<text x="762" y="38" text-anchor="end" class="green glow" font-size="10" letter-spacing="1.5">CHANNELS</text>'
        f'<path class="bar-sweep" d="M38 55H762" stroke="{BORDER}"/>'
        f"</g>{''.join(cards)}"
    )
    save("02-connect.svg", doc(800, 202, body))


def about_card() -> None:
    body = (
        f'<g class="enter">'
        f'<text x="38" y="42" class="green" font-size="11" letter-spacing="2.5">A LITTLE ABOUT ME</text>'
        f'<text x="38" y="86" class="fg" font-size="25" font-weight="900">CURIOUS BY NATURE. BUILDER BY CHOICE.</text>'
        f'<text x="38" y="128" class="muted" font-size="14">I\'m Nishit Soni, an aspiring AI/ML Engineer and Software Developer.</text>'
        f'<text x="38" y="157" class="muted" font-size="14">I enjoy building intelligent systems, data-driven solutions and full-stack</text>'
        f'<text x="38" y="186" class="muted" font-size="14">experiences that solve real-world problems.</text>'
        f'<path class="bar-sweep" d="M38 213H762" stroke="{BORDER}"/>'
        f'<text x="38" y="245" class="green glow" font-size="11" letter-spacing="1.2">AI / MACHINE LEARNING</text>'
        f'<text x="290" y="245" class="green glow" style="animation-delay:.4s" font-size="11" letter-spacing="1.2">DATA SCIENCE</text>'
        f'<text x="500" y="245" class="green glow" style="animation-delay:.8s" font-size="11" letter-spacing="1.2">FULL-STACK DEVELOPMENT</text>'
        f"</g>"
    )
    save("05-about.svg", doc(800, 275, body))


def tech_stack_card() -> None:
    groups = [
        ("LANGUAGES", "Python  /  JavaScript  /  Java  /  C  /  C++  /  R  /  SQL", 88),
        ("FRONTEND & BACKEND", "React  /  Redux Toolkit  /  Node.js  /  Express  /  Next.js  /  Tailwind CSS", 128),
        ("AI / ML & DATA", "TensorFlow  /  PyTorch  /  Scikit-learn  /  Pandas  /  NumPy  /  NLP  /  CNN", 168),
        ("DATABASES, CLOUD & TOOLS", "PostgreSQL  /  MySQL  /  MongoDB  /  AWS  /  Azure  /  Docker  /  Git", 208),
    ]
    rows = []
    for idx, (label, items, y) in enumerate(groups):
        delay = 0.18 + idx * 0.14
        rows.append(
            f'<g class="enter" style="animation-delay:{delay:.2f}s">'
            f'<text x="38" y="{y}" class="green" font-size="10" letter-spacing="1.8">{esc(label)}</text>'
            f'<text x="260" y="{y}" class="fg" font-size="13">{esc(items)}</text>'
            f"</g>"
        )

    body = (
        f'<g class="enter">'
        f'<text x="38" y="38" class="fg" font-size="24" font-weight="900">TOOLS I BUILD WITH.</text>'
        f'<text x="762" y="38" text-anchor="end" class="green glow" font-size="10" letter-spacing="1.5">MY TECH STACK</text>'
        f'<path class="bar-sweep" d="M38 57H762" stroke="{BORDER}"/>'
        f"</g>{''.join(rows)}"
        f'<g class="enter" style="animation-delay:.74s">'
        f'<path class="bar-sweep" d="M38 239H762" stroke="{BORDER}"/>'
        f'<text x="38" y="267" class="muted" font-size="10">ALWAYS LEARNING. ALWAYS BUILDING.</text>'
        f"</g>"
    )
    save("06-tech-stack.svg", doc(800, 290, body))


def resume_card() -> None:
    btn_pulse = (
        ""
        if STATIC
        else '<animate attributeName="opacity" values="0.85;1;0.85" dur="2.4s" repeatCount="indefinite"/>'
    )
    arrow_down = (
        ""
        if STATIC
        else '<animateTransform attributeName="transform" type="translate" values="0,0;0,3;0,0" dur="1.8s" repeatCount="indefinite"/>'
    )
    body = (
        f'<g class="enter">'
        f'<text x="38" y="42" class="green" font-size="11" letter-spacing="2.2">CURRICULUM VITAE</text>'
        f'<text x="762" y="42" text-anchor="end" class="green glow" font-size="10" letter-spacing="1.5">RESUME</text>'
        f'<text x="38" y="84" class="fg" font-size="24" font-weight="900">DOWNLOAD RESUME.</text>'
        f'<text x="38" y="116" class="muted" font-size="13">Explore my experience, projects, education and technical skills in one place.</text>'
        f'<path class="bar-sweep" d="M38 140H762" stroke="{BORDER}"/>'
        f'<text x="38" y="168" class="green" font-size="11" letter-spacing="1.1">AI / ML · FULL-STACK · DATA SCIENCE</text>'
        f'<a xlink:href="{esc(PROFILE["resume"])}"><g class="floaty">'
        f'<rect x="572" y="148" width="190" height="36" rx="2" fill="{GREEN}">{btn_pulse}</rect>'
        f'<text x="667" y="171" text-anchor="middle" fill="#000000" font-size="11" font-weight="800">DOWNLOAD RESUME {arrow_down}↓</text>'
        f"</g></a></g>"
    )
    save("07-resume.svg", doc(800, 204, body))


def activity(d: dict) -> None:
    months = d.get("months", [])[-12:]
    maxv = max([int(x.get("total", 0)) for x in months] + [1])
    bars = []
    for i, m in enumerate(months):
        val = int(m.get("total", 0))
        h = max(3, 112 * val / maxv)
        x = 48 + i * 59
        y = 226 - h
        smil = (
            ""
            if STATIC
            else (
                f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".85s" begin="{i * .06:.2f}s" fill="freeze"/>'
                f'<animate attributeName="y" from="226" to="{y:.1f}" dur=".85s" begin="{i * .06:.2f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values=".75;1;.75" dur="3s" begin="{.9 + i * .08:.2f}s" repeatCount="indefinite"/>'
            )
        )
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="34" height="{h:.1f}" rx="2" fill="{GREEN}" opacity=".9">{smil}</rect>'
            f'<text x="{x + 17}" y="249" text-anchor="middle" class="muted" font-size="9">{esc(m.get("label", ""))}</text>'
        )

    total = int(d.get("total_contributions", 0))
    streak = int(d.get("streak", 0))
    active = int(d.get("active_days", 0))
    busiest = esc(d.get("busiest_day", "—"))

    body = (
        f'<g class="enter">'
        f'<text x="38" y="43" class="fg" font-size="23" font-weight="900">PROGRESS IN NUMBERS.</text>'
        f'<text x="760" y="42" text-anchor="end" class="green glow" font-size="11">{total:,} CONTRIBUTIONS</text>'
        f'<text x="42" y="78" class="green" font-size="16" font-weight="800">{streak}</text>'
        f'<text x="78" y="78" class="muted" font-size="10">CURRENT STREAK</text>'
        f'<text x="280" y="78" class="green" font-size="16" font-weight="800">{active}</text>'
        f'<text x="320" y="78" class="muted" font-size="10">ACTIVE DAYS</text>'
        f'<text x="520" y="78" class="green" font-size="16" font-weight="800">{busiest}</text>'
        f'<text x="630" y="78" class="muted" font-size="10">BUSIEST DAY</text>'
        f'<path class="bar-sweep" d="M42 92H758" stroke="{BORDER}"/>'
        f"</g>{''.join(bars)}"
        f'<g class="enter" style="animation-delay:.55s">'
        f'<text x="42" y="283" class="muted" font-size="10">MONTHLY CONTRIBUTIONS · LAST 12 MONTHS</text>'
        f'<text x="758" y="283" text-anchor="end" class="green" font-size="10">02 / ACTIVITY</text>'
        f"</g>"
    )
    save("03-activity.svg", doc(800, 300, body))


def repos() -> None:
    for i, (name, desc, stack, url) in enumerate(REPOS, 1):
        delay = 0.2 + i * 0.14
        btn_pulse = (
            ""
            if STATIC
            else f'<animate attributeName="opacity" values="0.85;1;0.85" dur="2.4s" begin="{i * .2:.2f}s" repeatCount="indefinite"/>'
        )
        body = (
            f'<g class="enter" style="animation-delay:{delay:.2f}s">'
            f'<text x="30" y="39" class="green" font-size="10" letter-spacing="2">FEATURED PROJECT / {i:02d}</text>'
            f'<text x="30" y="84" class="fg" font-size="23" font-weight="900">{esc(name)}</text>'
            f'<text x="30" y="122" class="muted" font-size="13">{esc(desc)}</text>'
            f'<path class="bar-sweep" d="M30 151H770" stroke="{BORDER}"/>'
            f'<text x="30" y="184" class="green" font-size="11">{esc(stack)}</text>'
            f'<a xlink:href="{esc(url)}"><g class="floaty" style="animation-delay:{i * .25:.2f}s">'
            f'<rect x="610" y="197" width="160" height="38" fill="{GREEN}">{btn_pulse}</rect>'
            f'<text x="690" y="221" text-anchor="middle" fill="#000000" font-size="11" font-weight="800">EXPLORE PROJECT ↗</text>'
            f"</g></a></g>"
        )
        save(f"04-repo-{i:02d}.svg", doc(800, 260, body))


def contribution_graph(d: dict) -> None:
    days = d.get("calendar", d.get("days", []))[-371:]
    maxv = max([int(x.get("count", 0)) for x in days] + [1])
    palette = ["#17180D", "#505A00", "#899900", "#B7D900", GREEN]
    squares = []

    for i, day in enumerate(days):
        col, row = divmod(i, 7)
        count = int(day.get("count", 0))
        level = 0 if count == 0 else min(4, max(1, round(4 * count / maxv)))
        x, y = 42 + col * 13, 66 + row * 13
        shimmer = (
            ""
            if (STATIC or level == 0)
            else f'<animate attributeName="opacity" values="0.7;1;0.7" dur="2.8s" begin="{(i % 25) * 0.08:.2f}s" repeatCount="indefinite"/>'
        )
        squares.append(
            f'<rect class="enter" style="animation-delay:{min(i * .002, .7):.3f}s" '
            f'x="{x}" y="{y}" width="10" height="10" rx="1" fill="{palette[level]}">{shimmer}'
            f'<title>{esc(day.get("date", ""))}: {count} contributions</title></rect>'
        )

    body = (
        f'<g class="enter">'
        f'<text x="38" y="38" class="fg" font-size="22" font-weight="900">CONSISTENCY OVER TIME.</text>'
        f'<text x="760" y="38" text-anchor="end" class="green glow" font-size="10">GITHUB CONTRIBUTIONS</text>'
        f"</g>{''.join(squares)}"
        f'<g class="enter" style="animation-delay:.55s">'
        f'<text x="42" y="177" class="muted" font-size="10">LESS</text>'
        f'<g transform="translate(650 164)">'
        f'<rect width="10" height="10" fill="#151515"/>'
        f'<rect x="15" width="10" height="10" fill="#075C2C"/>'
        f'<rect x="30" width="10" height="10" fill="#008A3B"/>'
        f'<rect x="45" width="10" height="10" fill="#00B94B"/>'
        f'<rect x="60" width="10" height="10" fill="{GREEN}"/>'
        f"</g>"
        f'<text x="42" y="217" class="green glow" font-size="11">SMALL STEPS. MEANINGFUL PROGRESS.</text>'
        f"</g>"
    )
    save("99-contribution-graph.svg", doc(800, 240, body))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}. Fetch contribution data first.")

    d = json.loads(DATA.read_text(encoding="utf-8"))
    d.setdefault("months", [])
    d.setdefault("calendar", d.get("days", []))

    OUT.mkdir(parents=True, exist_ok=True)
    hero()
    tiles()
    connect_card()
    about_card()
    tech_stack_card()
    resume_card()
    activity(d)
    repos()
    contribution_graph(d)

    print(f'Rendered {len(list(OUT.glob("*.svg")))} cards in {OUT}; STATIC={int(STATIC)}')


if __name__ == "__main__":
    main()