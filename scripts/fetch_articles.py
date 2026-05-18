#!/usr/bin/env python3
"""
Science of Wellness — Weekly Article Curator
Runs every Friday at noon UTC via GitHub Actions.
Finds top recent wellness articles on the web and generates article pages
in the site's style using Claude AI with live web search.
"""

import anthropic
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

ROOT = Path(__file__).parent.parent
ARTICLES_DIR = ROOT / "articles"
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "articles.json"

TODAY = datetime.utcnow().strftime("%Y-%m-%d")
YEAR = datetime.utcnow().strftime("%Y")
MONTH_YEAR = datetime.utcnow().strftime("%B %Y")

# ---------------------------------------------------------------------------
# Topic definitions — one article per topic per week = 6 articles/week
# ---------------------------------------------------------------------------
TOPICS = [
    {
        "id": "wim-hof",
        "name": "Wim Hof Method & Cold Therapy",
        "display": "Cold Therapy · Breathwork",
        "queries": "Wim Hof cold exposure cold therapy ice bath science research study 2024 2025",
        "gradient": "linear-gradient(135deg, #041428 0%, #0A3A80 60%, #2A7AB8 100%)",
        "related": [
            ("breathwork.html", "Breathwork: Ancient Technology →"),
            ("sound-healing.html", "Sound Healing →"),
            ("human-garage.html", "Human Garage →"),
        ],
    },
    {
        "id": "breathwork",
        "name": "Breathwork & Pranayama",
        "display": "Breathwork · Polyvagal Theory · HRV",
        "queries": "breathwork pranayama polyvagal HRV heart rate variability nervous system science 2024 2025",
        "gradient": "linear-gradient(135deg, #020810 0%, #0A2A4A 40%, #1A6B8B 100%)",
        "related": [
            ("wim-hof.html", "Wim Hof Method →"),
            ("sound-healing.html", "Sound Healing →"),
            ("mdma-therapy.html", "MDMA Therapy →"),
        ],
    },
    {
        "id": "sound-healing",
        "name": "Sound Healing & Vibrational Medicine",
        "display": "Sound Medicine · Cymatics · Frequencies",
        "queries": "sound healing binaural beats singing bowls cymatics vibrational medicine research 2024 2025",
        "gradient": "linear-gradient(135deg, #100500 0%, #5A2A05 40%, #C9A84C 100%)",
        "related": [
            ("breathwork.html", "Breathwork →"),
            ("wim-hof.html", "Wim Hof Method →"),
            ("human-garage.html", "Human Garage →"),
        ],
    },
    {
        "id": "iboga",
        "name": "Iboga & Plant Medicine",
        "display": "Plant Medicine · Ibogaine · Neuroscience",
        "queries": "ibogaine iboga plant medicine psychedelic therapy addiction treatment clinical research 2024 2025",
        "gradient": "linear-gradient(135deg, #010805 0%, #0A4018 60%, #2FAF50 100%)",
        "related": [
            ("mdma-therapy.html", "MDMA Therapy →"),
            ("breathwork.html", "Breathwork Integration →"),
            ("human-garage.html", "Human Garage →"),
        ],
    },
    {
        "id": "mdma-therapy",
        "name": "MDMA-Assisted Therapy & Psychedelic Medicine",
        "display": "Psychedelic Therapy · PTSD · Trauma",
        "queries": "MDMA therapy PTSD trauma psilocybin psychedelic medicine clinical trial research 2024 2025",
        "gradient": "linear-gradient(135deg, #0D0418 0%, #3A0870 50%, #B060F0 100%)",
        "related": [
            ("iboga.html", "Iboga: Plant Medicine →"),
            ("breathwork.html", "Breathwork Integration →"),
            ("sound-healing.html", "Sound Healing →"),
        ],
    },
    {
        "id": "human-garage",
        "name": "Fascia, Somatic Healing & Body Intelligence",
        "display": "Fascial Science · Somatic Healing · Tensegrity",
        "queries": "fascia research somatic healing connective tissue bodywork tensegrity TRE nervous system 2024 2025",
        "gradient": "linear-gradient(135deg, #0D0603 0%, #3A1A08 35%, #B05A28 100%)",
        "related": [
            ("breathwork.html", "Breathwork: Vagus Nerve →"),
            ("sound-healing.html", "Sound & the Body →"),
            ("wim-hof.html", "Wim Hof Method →"),
        ],
    },
]

# ---------------------------------------------------------------------------
# Shared HTML fragments
# ---------------------------------------------------------------------------
NAV_HTML = """  <nav class="nav scrolled" id="nav">
    <a href="../index.html" class="nav-logo">
      <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <circle cx="18" cy="18" r="8" stroke="#C9A84C" stroke-width="1"/>
        <circle cx="26" cy="18" r="8" stroke="#C9A84C" stroke-width="1"/>
        <circle cx="22" cy="11.07" r="8" stroke="#C9A84C" stroke-width="1"/>
        <circle cx="14" cy="11.07" r="8" stroke="#C9A84C" stroke-width="1"/>
        <circle cx="10" cy="18" r="8" stroke="#C9A84C" stroke-width="1"/>
        <circle cx="14" cy="24.93" r="8" stroke="#C9A84C" stroke-width="1"/>
        <circle cx="22" cy="24.93" r="8" stroke="#C9A84C" stroke-width="1"/>
      </svg>
      Science of Wellness
    </a>
    <ul class="nav-links">
      <li><a href="../index.html">Home</a></li>
      <li><a href="../index.html#topics">Topics</a></li>
      <li><a href="../index.html#articles">Articles</a></li>
      <li><a href="../index.html#newsletter" class="nav-cta">Begin Journey</a></li>
    </ul>
  </nav>"""


def footer_html():
    return f"""  <footer style="background:var(--deep-night);padding:2rem 5%;border-top:1px solid rgba(201,168,76,0.1);">
    <div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
      <a href="../index.html" style="font-family:var(--font-sacred);color:var(--gold);font-size:0.85rem;letter-spacing:0.2em;">← Back to Science of Wellness</a>
      <p style="color:rgba(250,244,232,0.25);font-size:0.78rem;margin:0;">© {YEAR} Science of Wellness · Educational content only</p>
    </div>
  </footer>"""


# ---------------------------------------------------------------------------
# Data tracking (avoid republishing the same article)
# ---------------------------------------------------------------------------
def load_published():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"articles": [], "published_titles": [], "last_run": None}


def save_published(data):
    DATA_DIR.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:70]


# ---------------------------------------------------------------------------
# Core: Claude researches the web and drafts the article
# ---------------------------------------------------------------------------
def research_and_draft(topic: dict, avoid_titles: list[str]) -> str:
    avoid_note = (
        f"Avoid articles similar to these already published titles: {', '.join(avoid_titles[-15:])}"
        if avoid_titles
        else "No prior articles to avoid yet."
    )

    prompt = f"""You are a senior wellness journalist and researcher for scienceofwellness.com —
a publication that bridges ancient healing wisdom with cutting-edge modern science.

Your task: Search the web and find the single most interesting, credible, and recent article,
study, or breakthrough related to **{topic['name']}** from the past 30 days (or past 90 days
if nothing recent). Prioritise peer-reviewed research, top universities, respected health media.

Search queries to try: "{topic['queries']}"

{avoid_note}

Selection criteria (ranked):
1. Scientific credibility and specificity — cite real studies, researchers, institutions
2. Novelty — something readers haven't seen; a surprising finding or new angle
3. Recency — newer is better
4. The article must have a clear "ancient wisdom meets modern science" angle

After finding the best source, write a COMPLETE, FULL article (minimum 800 words of body text)
for the site in this EXACT structured format between the delimiters:

===ARTICLE_START===
SLUG: [kebab-case-url-slug, max 60 chars, descriptive of the specific finding]
TITLE: [Full compelling article title]
META: [150-char meta description for SEO]
HERO: [2-line hero heading, use <br> for the line break]
LABEL: [Topic · Subtopic · Year, e.g. "Cold Therapy · Immunology · 2025"]
READ_TIME: [integer, estimated reading minutes]
DATE_LABEL: [e.g. "May 2025"]
SOURCE_URL: [direct URL to the source article/paper, or empty if not found]
SOURCE_NAME: [Publication or journal name]

LEAD_PARAGRAPH:
[A single gripping 2–3 sentence opening paragraph that goes inside <p class="article-lead">]

BODY:
[Full article HTML using ONLY these tags and classes — follow the structure precisely:]

<div class="article-section">
  <h2>Section Heading</h2>
  <p>Paragraph text...</p>
  <p>More paragraphs as needed...</p>

  [Use callout boxes wherever appropriate:]
  <div class="callout callout-science">
    <p class="callout-label">Research Note</p>
    <p>Specific study details, researcher names, journal, year, findings...</p>
  </div>

  <div class="callout callout-wisdom">
    <p class="callout-label">Ancient Wisdom</p>
    <p>Connection to traditional healing practice, indigenous knowledge, or spiritual tradition...</p>
  </div>

  <div class="callout callout-practice">
    <p class="callout-label">Practice</p>
    <p>How to apply this finding in daily life...</p>
  </div>

  <div class="callout callout-caution">
    <p class="callout-label">Important Note</p>
    <p>Safety information or nuance if needed...</p>
  </div>
</div>

[Add at least one pull quote somewhere in the body:]
<div class="pull-quote">
"A compelling quote from a researcher, practitioner, or ancient text"
<br><span style="font-size:0.85rem;opacity:0.7;">— Name, Title/Source</span>
</div>

[Write 4–6 sections. Be specific. Name real researchers. Cite real data. Connect to real traditions.]

SIDEBAR_BULLETS:
• [Key insight or data point 1]
• [Key insight or data point 2]
• [Key insight or data point 3]
• [Key insight or data point 4]
• [Key insight or data point 5]
• [Key insight or data point 6]

REFERENCES:
1. [Author(s) (Year). Title. Journal/Publication, volume(issue), pages or URL.]
2. [...]
3. [...]
===ARTICLE_END===

Be thorough. Write at least 800 words of body content. Make it educational, inspiring, and scientifically grounded."""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=10000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Collect all text blocks from the response
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)

    return "\n".join(text_parts)


# ---------------------------------------------------------------------------
# Parse Claude's structured output into an HTML file
# ---------------------------------------------------------------------------
def build_html(raw: str, topic: dict) -> tuple[str, str, str]:
    """Returns (slug, title, full_html)"""

    def extract(key, text, multiline=False):
        if multiline:
            pattern = rf"{key}:\s*\n([\s\S]+?)(?=\n[A-Z_]+:|===ARTICLE_END===|$)"
        else:
            pattern = rf"{key}:\s*(.+?)(?=\n)"
        m = re.search(pattern, text)
        return m.group(1).strip() if m else ""

    # Single-line fields
    slug_raw  = extract("SLUG", raw)
    title     = extract("TITLE", raw) or f"New {topic['name']} Research — {MONTH_YEAR}"
    meta      = extract("META", raw)
    hero      = extract("HERO", raw) or title
    label     = extract("LABEL", raw) or topic["display"]
    read_time = extract("READ_TIME", raw) or "8"
    date_lbl  = extract("DATE_LABEL", raw) or MONTH_YEAR
    src_url   = extract("SOURCE_URL", raw)
    src_name  = extract("SOURCE_NAME", raw)

    # Multi-line fields
    lead_m = re.search(r"LEAD_PARAGRAPH:\s*\n([\s\S]+?)(?=\nBODY:)", raw)
    lead   = lead_m.group(1).strip() if lead_m else ""

    body_m = re.search(r"BODY:\s*\n([\s\S]+?)(?=\nSIDEBAR_BULLETS:|===ARTICLE_END===)", raw)
    body   = body_m.group(1).strip() if body_m else ""

    sidebar_m = re.search(r"SIDEBAR_BULLETS:\s*\n([\s\S]+?)(?=\nREFERENCES:|===ARTICLE_END===)", raw)
    sidebar_raw = sidebar_m.group(1) if sidebar_m else ""
    sidebar_items = [
        line.lstrip("•- ").strip()
        for line in sidebar_raw.split("\n")
        if line.strip() and len(line.strip()) > 5
    ]
    sidebar_li = "\n".join(f"          <li>{item}</li>" for item in sidebar_items[:7])

    refs_m = re.search(r"REFERENCES:\s*\n([\s\S]+?)(?====ARTICLE_END===|$)", raw)
    refs_raw = refs_m.group(1) if refs_m else ""
    ref_lines = [l.strip() for l in refs_raw.split("\n") if l.strip() and len(l.strip()) > 15]
    refs_li = "\n".join(f"          <li>{ref}</li>" for ref in ref_lines[:6])

    # Source credit
    if src_name and src_url:
        source_credit = (
            f'<p style="font-size:0.8rem;color:#8B6914;margin-top:2rem;">'
            f'Source: <a href="{src_url}" target="_blank" rel="noopener noreferrer" '
            f'style="color:var(--amber);">{src_name}</a></p>'
        )
    elif src_name:
        source_credit = f'<p style="font-size:0.8rem;color:#8B6914;margin-top:2rem;">Source: {src_name}</p>'
    else:
        source_credit = ""

    # Related links
    related_links = "\n".join(
        f'        <a href="{href}">{text}</a>' for href, text in topic["related"]
    )

    # Final slug
    slug = slugify(slug_raw) if slug_raw else f"{topic['id']}-{TODAY}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta}">
  <title>{title} | Science of Wellness</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Cinzel:wght@400;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body class="article-page">
{NAV_HTML}

  <div class="article-hero">
    <div class="article-hero-bg" style="background: {topic['gradient']};"></div>
    <div class="article-hero-overlay"></div>
    <div class="article-hero-content">
      <p class="sacred-label">{label}</p>
      <h1>{hero}</h1>
      <div class="article-meta-bar">
        <span class="meta-item">{read_time} min read</span>
        <span class="meta-item">Science &amp; Tradition</span>
        <span class="meta-item">{date_lbl}</span>
      </div>
    </div>
  </div>

  <div class="article-layout">
    <main class="article-main">

      <p class="article-lead">{lead}</p>

      {body}

      {source_credit}

      <div class="references">
        <h4>References</h4>
        <ol>
{refs_li}
        </ol>
      </div>

    </main>

    <aside class="article-sidebar">
      <div class="sidebar-card">
        <h4>Key Insights</h4>
        <ul>
{sidebar_li}
        </ul>
      </div>

      <div class="sidebar-related sidebar-card">
        <h4>Related Articles</h4>
{related_links}
      </div>
    </aside>
  </div>

{footer_html()}

  <script src="../js/main.js"></script>
</body>
</html>"""

    return slug, title, html


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------
def main():
    print(f"Science of Wellness — Weekly Curator  [{TODAY}]")
    print("=" * 55)

    published = load_published()
    avoid_titles = published.get("published_titles", [])
    new_count = 0

    for topic in TOPICS:
        print(f"\n▶ {topic['name']}")
        try:
            raw = research_and_draft(topic, avoid_titles)

            if "===ARTICLE_START===" not in raw or "===ARTICLE_END===" not in raw:
                print("  ⚠  No structured output found — skipping.")
                continue

            # Only parse between the delimiters
            inner = raw.split("===ARTICLE_START===")[1].split("===ARTICLE_END===")[0]
            slug, title, html = build_html(inner, topic)

            filename = f"{slug}.html"
            filepath = ARTICLES_DIR / filename

            if filepath.exists():
                print(f"  ↩  Already exists: {filename}")
                continue

            filepath.write_text(html, encoding="utf-8")
            print(f"  ✓  Created: articles/{filename}")
            print(f"     {title}")

            avoid_titles.append(title)
            published.setdefault("articles", []).append(
                {
                    "topic": topic["id"],
                    "slug": slug,
                    "title": title,
                    "date": TODAY,
                    "file": f"articles/{filename}",
                }
            )
            new_count += 1

        except Exception as exc:
            print(f"  ✗  Error: {exc}")
            continue

    published["published_titles"] = avoid_titles[-200:]
    published["last_run"] = TODAY
    save_published(published)

    print(f"\n{'=' * 55}")
    print(f"Done — {new_count} new article(s) created.")
    return 0 if new_count >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
