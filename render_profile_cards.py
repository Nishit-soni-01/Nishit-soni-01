#!/usr/bin/env python3
"""Render animated GitHub README SVG cards. STATIC=1 disables all motion."""
from __future__ import annotations
import base64, html, json, os, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = Path(os.getenv('OUTPUT_DIR', ROOT / 'cards'))
DATA = Path(os.getenv('PROFILE_DATA', ROOT / 'contributions.json'))
STATIC = os.getenv('STATIC', '0') == '1'
FONT_FILE = os.getenv('FONT_FILE', '')
PORTRAIT = os.getenv('PORTRAIT', '')
# Updated palette: near-black, warm white, electric neon yellow.
BG, FG, GREEN, MUTED = '#050505', '#F7F7E8', '#DFFF00', '#B8B89F'
BORDER, PANEL, FONT = '#3A3A20', '#10110A', 'Roboto'
PROFILE = {
 'name':'NISHIT SONI.',
 'line':'I build intelligent systems and digital experiences that solve real-world problems.',
 'role':'AI/ML ENGINEER  ✳  SOFTWARE DEVELOPER  ✳  DATA SCIENCE',
 'portfolio':'https://nishvay-portfolio-v2.vercel.app/',
 'linkedin':'https://www.linkedin.com/', 'leetcode':'https://leetcode.com/'
}
REPOS = [
 ('Sentinel-AI: Real-Time Fraud Mitigation Engine','Cost-sensitive fraud detection for highly imbalanced financial data.','Python · AWS · Docker · Machine Learning','https://github.com/Nishit-soni-01'),
 ('Algerian Forest Fire Predictor','A predictive web application forecasting the Fire Weather Index.','Python · Flask · Ridge Regression · AWS','https://github.com/Nishit-soni-01'),
 ('E-commerce Sales Analysis Dashboard','Business intelligence dashboard for sales, profit and product insights.','Power BI · DAX · Data Analytics','https://github.com/Nishit-soni-01'),
 ('Personal Portfolio & Showcase Engine','A responsive portfolio for full-stack, AI/ML and data projects.','Next.js · React · Tailwind CSS','https://github.com/Nishit-soni-01')]

def esc(v): return html.escape(str(v), quote=True)

def font_rule():
    if not FONT_FILE: return ''
    src = Path(FONT_FILE)
    if not src.is_file() or not shutil.which('pyftsubset'):
        print('FONT_FILE or pyftsubset missing; using Roboto/Arial fallback.')
        return ''
    OUT.mkdir(parents=True, exist_ok=True)
    woff = OUT / 'profile-font.woff'
    chars = 'NISHIT SONI AI ML ENGINEER SOFTWARE DEVELOPER DATA SCIENCE PORTFOLIO LINKEDIN LEETCODE CONTRIBUTIONS ACTIVE DAYS CURRENT STREAK BUSIEST DAY PROJECTS EXPLORE MY WORK SMALL STEPS MEANINGFUL PROGRESS'
    for r in REPOS: chars += ''.join(r[:3])
    subprocess.run(['pyftsubset', str(src), f'--text={chars}', '--flavor=woff', f'--output-file={woff}', '--layout-features=*'], check=True)
    b64 = base64.b64encode(woff.read_bytes()).decode('ascii')
    return f'@font-face{{font-family:{FONT};src:url(data:font/woff;base64,{b64}) format(woff);font-weight:100 900;}}'

FONT_CSS = font_rule()
def doc(w, h, body):
    if STATIC:
        motion = '.enter{opacity:1;transform:none}.glow{opacity:1}'
    else:
        motion = '''@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
        @keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}
        .enter{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}.glow{animation:pulse 2.8s ease-in-out infinite}'''
    reduced = '''@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}animate,animateTransform,set{display:none!important}.enter{opacity:1;transform:none}.glow{opacity:1}}'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<title>Nishit Soni GitHub profile card</title><style>{FONT_CSS}{motion}{reduced}text{{font-family:Roboto,Arial,sans-serif}}.fg{{fill:{FG}}}.muted{{fill:{MUTED}}}.green{{fill:{GREEN}}}</style>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="2" fill="{BG}" stroke="{BORDER}"/><rect x="1" y="1" width="{w-2}" height="4" fill="{GREEN}"/>{body}</svg>'''

def save(name, svg):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(svg, encoding='utf-8')

def hero():
    portrait = ''
    if PORTRAIT and Path(PORTRAIT).is_file():
        p = Path(PORTRAIT); mime = 'image/png' if p.suffix.lower()=='.png' else 'image/jpeg'
        b64 = base64.b64encode(p.read_bytes()).decode('ascii')
        portrait = f'<defs><clipPath id="avatar"><circle cx="690" cy="115" r="65"/></clipPath></defs><image x="625" y="50" width="130" height="130" clip-path="url(#avatar)" preserveAspectRatio="xMidYMid slice" xlink:href="data:{mime};base64,{b64}"/><circle cx="690" cy="115" r="67" fill="none" stroke="{GREEN}" stroke-width="3"/>'
    body = f'''<g class="enter"><text x="42" y="50" class="green" font-size="12" letter-spacing="3">HELLO, WELCOME TO MY GITHUB</text><text x="40" y="111" class="fg" font-size="43" font-weight="900">{esc(PROFILE['name'])}</text><text x="42" y="153" class="muted" font-size="16">{esc(PROFILE['line'])}</text><text x="42" y="202" class="green" font-size="12" letter-spacing="1.4">{esc(PROFILE['role'])}</text></g>{portrait}<path d="M42 246H758" stroke="{BORDER}"/><text x="42" y="278" class="muted" font-size="11">BASED IN INDIA · CREATING WITH PURPOSE</text><text x="758" y="278" text-anchor="end" class="green" font-size="11">01 / INTRODUCTION</text>'''
    save('01-hero.svg', doc(800,300,body))

def tiles():
    items=[('PORTFOLIO','Explore my work',PROFILE['portfolio']),('LINKEDIN','Connect professionally',PROFILE['linkedin']),('LEETCODE','Problem-solving journey',PROFILE['leetcode'])]
    for i,(name,sub,url) in enumerate(items,1):
        body=f'''<a class="enter" style="animation-delay:{i*.18:.2f}s" xlink:href="{esc(url)}"><rect x="1" y="1" width="258" height="116" fill="{PANEL}" stroke="{BORDER}"/><text x="20" y="34" class="green" font-size="10">0{i} / CONNECT</text><text x="20" y="68" class="fg" font-size="20" font-weight="800">{name}</text><text x="20" y="94" class="muted" font-size="11">{sub}</text><text x="235" y="35" text-anchor="end" class="green" font-size="18">↗</text></a>'''
        save(f'02-tile-{i}.svg',doc(260,118,body))

def about_card():
    body=f'''<g class="enter"><text x="38" y="42" class="green" font-size="11" letter-spacing="2.5">A LITTLE ABOUT ME</text><text x="38" y="86" class="fg" font-size="25" font-weight="900">CURIOUS BY NATURE. BUILDER BY CHOICE.</text><text x="38" y="128" class="muted" font-size="14">I'm Nishit Soni, an aspiring AI/ML Engineer and Software Developer.</text><text x="38" y="157" class="muted" font-size="14">I enjoy building intelligent systems, data-driven solutions and full-stack</text><text x="38" y="186" class="muted" font-size="14">experiences that solve real-world problems.</text><path d="M38 213H762" stroke="{BORDER}"/><text x="38" y="245" class="green" font-size="11" letter-spacing="1.2">AI / MACHINE LEARNING</text><text x="290" y="245" class="green" font-size="11" letter-spacing="1.2">DATA SCIENCE</text><text x="500" y="245" class="green" font-size="11" letter-spacing="1.2">FULL-STACK DEVELOPMENT</text></g>'''
    save('05-about.svg',doc(800,275,body))

def tech_stack_card():
    groups = [
        (
            '01 / LANGUAGES',
            [
                'Python / JavaScript ES6+ / HTML5 / CSS3 / SQL / C / C++ / Java / R'
            ],
            103
        ),
        (
            '02 / WEB DEVELOPMENT',
            [
                'React / Redux Toolkit / Zustand / Node.js / Express / Flask',
                'Tailwind CSS / REST APIs / Custom Authentication / Particles.js'
            ],
            163
        ),
        (
            '03 / AI & MACHINE LEARNING',
            [
                'Regression / Classification / KNN / SVM / Naive Bayes / K-Means',
                'ANN / CNN / NLP / Reinforcement Learning / TensorFlow / PyTorch',
                'Scikit-learn / XGBoost / PCA / LDA / Cross-Validation / Grid Search'
            ],
            233
        ),
        (
            '04 / DATA & BI',
            [
                'Pandas / NumPy / Matplotlib / Seaborn',
                'Power BI / Tableau / DAX / Power Query / Advanced Excel'
            ],
            318
        ),
        (
            '05 / DATABASES & ORMs',
            [
                'PostgreSQL / MySQL / SQLite / SQL Server / BigQuery / NeonDB',
                'MongoDB / Mongoose / Prisma / Drizzle'
            ],
            388
        ),
        (
            '06 / CLOUD & DEVOPS',
            [
                'AWS EC2 / Elastic Beanstalk / Microsoft Azure / Snowflake',
                'Docker / Git / Custom VPS Deployment',
                'VS Code / Postman / Jupyter / LangChain / TensorFlow.js'
            ],
            458
        )
    ]

    rows = []

    for label, skills, y in groups:
        rows.append(
            f'<text x="38" y="{y}" class="green" '
            f'font-size="11" font-weight="bold" '
            f'letter-spacing="1.3">{esc(label)}</text>'
        )

        for index, skill in enumerate(skills):
            rows.append(
                f'<text x="250" y="{y + index * 20}" '
                f'class="fg" font-size="12">{esc(skill)}</text>'
            )

    separators = [125, 195, 280, 350, 420, 505]

    lines = ''.join(
        f'<path d="M38 {y}H762" stroke="{BORDER}"/>'
        for y in separators
    )

    body = f'''
    <g class="enter">
        <text x="38" y="45" class="fg"
              font-size="25" font-weight="900">
            MY TECH STACK.
        </text>

        <text x="762" y="43" text-anchor="end"
              class="green" font-size="11"
              font-weight="bold" letter-spacing="1.3">
            FULL-STACK / DATA / AI
        </text>

        <line x1="38" y1="65" x2="762" y2="65"
              stroke="{BORDER}"/>

        {''.join(rows)}
        {lines}

        <text x="38" y="545" class="muted" font-size="10">
            BUILDING APPLICATIONS. EXPLORING DATA. ENGINEERING INTELLIGENCE.
        </text>

        <text x="762" y="545" text-anchor="end"
              class="green" font-size="10">
            ALWAYS LEARNING.
        </text>
    </g>
    '''

    save('06-tech-stack.svg', doc(800, 590, body))

def activity(d):
    months=d.get('months',[])[-12:]; maxv=max([int(x.get('total',0)) for x in months]+[1]); bars=[]
    for i,m in enumerate(months):
        val=int(m.get('total',0)); h=max(3,112*val/maxv); x=48+i*59; y=226-h
        smil='' if STATIC else f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".8s" begin="{i*.07:.2f}s" fill="freeze"/>'
        bars.append(f'<rect x="{x}" y="{y:.1f}" width="34" height="{h:.1f}" rx="2" fill="{GREEN}" opacity=".9">{smil}</rect><text x="{x+17}" y="249" text-anchor="middle" class="muted" font-size="9">{esc(m.get("label",""))}</text>')
    total=int(d.get('total_contributions',0)); streak=int(d.get('streak',0)); active=int(d.get('active_days',0)); busiest=esc(d.get('busiest_day','—'))
    body=f'''<text x="38" y="43" class="fg" font-size="23" font-weight="900">PROGRESS IN NUMBERS.</text><text x="760" y="42" text-anchor="end" class="green" font-size="11">{total:,} CONTRIBUTIONS</text><text x="42" y="78" class="green" font-size="16" font-weight="800">{streak}</text><text x="78" y="78" class="muted" font-size="10">CURRENT STREAK</text><text x="280" y="78" class="green" font-size="16" font-weight="800">{active}</text><text x="320" y="78" class="muted" font-size="10">ACTIVE DAYS</text><text x="520" y="78" class="green" font-size="16" font-weight="800">{busiest}</text><text x="630" y="78" class="muted" font-size="10">BUSIEST DAY</text><path d="M42 92H758" stroke="{BORDER}"/>{''.join(bars)}<text x="42" y="283" class="muted" font-size="10">MONTHLY CONTRIBUTIONS · LAST 12 MONTHS</text><text x="758" y="283" text-anchor="end" class="green" font-size="10">02 / ACTIVITY</text>'''
    save('03-activity.svg',doc(800,300,body))

def repos():
    for i,(name,desc,stack,url) in enumerate(REPOS,1):
        delay=1.2+i*.45
        body=f'''<g class="enter" style="animation-delay:{delay:.2f}s"><text x="30" y="39" class="green" font-size="10" letter-spacing="2">FEATURED PROJECT / {i:02d}</text><text x="30" y="84" class="fg" font-size="23" font-weight="900">{esc(name)}</text><text x="30" y="122" class="muted" font-size="13">{esc(desc)}</text><path d="M30 151H770" stroke="{BORDER}"/><text x="30" y="184" class="green" font-size="11">{esc(stack)}</text><a xlink:href="{esc(url)}"><rect x="610" y="197" width="160" height="38" fill="{GREEN}"/><text x="690" y="221" text-anchor="middle" fill="#000000" font-size="11" font-weight="800">EXPLORE PROJECT ↗</text></a></g>'''
        save(f'04-repo-{i:02d}.svg',doc(800,260,body))

def contribution_graph(d):
    days=d.get('calendar',d.get('days',[]))[-371:]; maxv=max([int(x.get('count',0)) for x in days]+[1]); palette=['#17180D','#505A00','#899900','#B7D900',GREEN]; squares=[]
    for i,day in enumerate(days):
        col,row=divmod(i,7); count=int(day.get('count',0)); level=0 if count==0 else min(4,max(1,round(4*count/maxv))); x,y=42+col*13,66+row*13
        squares.append(f'<rect class="enter" style="animation-delay:{min(i*.002,.7):.3f}s" x="{x}" y="{y}" width="10" height="10" rx="1" fill="{palette[level]}"><title>{esc(day.get("date",""))}: {count} contributions</title></rect>')
    body=f'''<text x="38" y="38" class="fg" font-size="22" font-weight="900">CONSISTENCY OVER TIME.</text><text x="760" y="38" text-anchor="end" class="green" font-size="10">GITHUB CONTRIBUTIONS</text>{''.join(squares)}<text x="42" y="177" class="muted" font-size="10">LESS</text><g transform="translate(650 164)"><rect width="10" height="10" fill="#151515"/><rect x="15" width="10" height="10" fill="#075C2C"/><rect x="30" width="10" height="10" fill="#008A3B"/><rect x="45" width="10" height="10" fill="#00B94B"/><rect x="60" width="10" height="10" fill="{GREEN}"/></g><text x="42" y="217" class="green" font-size="11">SMALL STEPS. MEANINGFUL PROGRESS.</text>'''
    save('99-contribution-graph.svg',doc(800,240,body))

def main():
    if not DATA.exists(): raise SystemExit(f'Missing {DATA}. Fetch contribution data first.')
    d=json.loads(DATA.read_text(encoding='utf-8')); d.setdefault('months',[]); d.setdefault('calendar',d.get('days',[]))
    OUT.mkdir(parents=True,exist_ok=True); hero(); tiles(); about_card(); tech_stack_card(); activity(d); repos(); contribution_graph(d)
    print(f'Rendered {len(list(OUT.glob("*.svg")))} cards in {OUT}; STATIC={int(STATIC)}')
if __name__=='__main__': main()
