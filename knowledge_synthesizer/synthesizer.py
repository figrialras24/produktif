"""
Autonomous Knowledge Synthesizer & Second Brain Engine
Fetches high-signal software engineering, systems, and AI discussions/repos,
synthesizes them into structured Obsidian Markdown notes, and renders an interactive dashboard.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from html import escape

VAULT_DIR = Path(__file__).resolve().parent / "vault"
DAILY_DIR = VAULT_DIR / "daily"
DASHBOARD_FILE = Path(__file__).resolve().parent / "dashboard.html"
INDEX_FILE = Path(__file__).resolve().parent / "index.html"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AntigravitySynthesizer/1.0"


def fetch_json(url: str, timeout: int = 10) -> dict | list | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"[WARN] Failed fetching {url}: {e}\n")
    return None


def fetch_hacker_news_signals(limit: int = 8) -> list[dict]:
    """Fetch high-scoring technical stories from Hacker News."""
    url = f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={limit * 2}"
    data = fetch_json(url)
    if not data or "hits" not in data:
        return []

    signals = []
    # Keywords that indicate high engineering/architecture signal
    keywords = ["architecture", "database", "distributed", "compiler", "linux", "ai", "llm", "performance", "system", "engine", "scale", "security", "design", "memory", "rust", "go", "python"]

    for item in data["hits"]:
        title = item.get("title") or item.get("story_title") or ""
        url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('objectID')}"
        points = item.get("points") or 0
        comments_count = item.get("num_comments") or 0

        # Calculate signal relevance
        text_lower = title.lower()
        matched_tags = [kw for kw in keywords if kw in text_lower]

        if points >= 50 or matched_tags:
            category = "Systems & Architecture" if any(k in matched_tags for k in ["architecture", "database", "distributed", "system", "engine", "scale"]) else \
                       "AI & Machine Learning" if any(k in matched_tags for k in ["ai", "llm"]) else \
                       "Engineering & Tools"

            signals.append({
                "source": "HackerNews",
                "title": title.strip(),
                "url": url,
                "score": points,
                "comments": comments_count,
                "discussion_url": f"https://news.ycombinator.com/item?id={item.get('objectID')}",
                "category": category,
                "tags": matched_tags or ["engineering", "tech-signal"],
                "author": item.get("author", "unknown"),
                "created_at": item.get("created_at", datetime.now(timezone.utc).isoformat())
            })
        if len(signals) >= limit:
            break

    return signals


def fetch_github_trending(limit: int = 6) -> list[dict]:
    """Fetch top trending developer repositories."""
    url = "https://api.github.com/search/repositories?q=stars:>1000+pushed:>2026-01-01&sort=updated&order=desc&per_page=15"
    data = fetch_json(url)
    if not data or "items" not in data:
        return []

    repos = []
    for repo in data["items"][:limit]:
        topics = repo.get("topics") or []
        lang = repo.get("language") or "Code"
        category = "Systems & Architecture" if any("system" in t or "database" in t for t in topics) else \
                   "AI & Machine Learning" if any("ai" in t or "llm" in t for t in topics) else \
                   "Open Source Infrastructure"

        repos.append({
            "source": "GitHub",
            "title": repo.get("full_name"),
            "url": repo.get("html_url"),
            "score": repo.get("stargazers_count", 0),
            "description": repo.get("description") or "No description provided.",
            "language": lang,
            "category": category,
            "tags": topics[:5] or [lang.lower()],
            "author": repo.get("owner", {}).get("login", "unknown"),
            "created_at": repo.get("updated_at", datetime.now(timezone.utc).isoformat())
        })
    return repos


def synthesize_technical_digest(signals: list[dict], repos: list[dict]) -> str:
    """Create structured Obsidian markdown entry."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = []
    md.append("---")
    md.append(f"date: {today_str}")
    md.append(f"generated_at: \"{timestamp}\"")
    md.append("type: second-brain-digest")
    md.append("tags:")
    md.append("  - daily-synthesis")
    md.append("  - software-engineering")
    md.append("  - technical-insights")
    md.append("---\n")

    md.append(f"# Daily Technical Knowledge Digest - {today_str}\n")
    md.append("> *Kurasi otomatis wawasan arsitektur, paper/diskusi teknis, dan open-source tools pilihan.*\n")

    # High signal discussions
    md.append("## 🧠 High-Signal Technical Discussions & Breakthroughs\n")
    for idx, item in enumerate(signals, 1):
        md.append(f"### {idx}. [{item['title']}]({item['url']})")
        md.append(f"- **Kategori:** `{item['category']}` | **Score:** {item['score']} pts | **Komentar:** [{item['comments']} diskusi]({item['discussion_url']})")
        md.append(f"- **Tags:** {', '.join([f'#{t}' for t in item['tags']])}")
        md.append(f"- **Actionable Insight:** Pelajari trade-off implementasi dan perdebatan teknis komunitas pada thread diskusi terkait.")
        md.append("")

    # High impact repositories
    md.append("## 🛠️ Trending Infrastructure & Architecture Repos\n")
    for idx, repo in enumerate(repos, 1):
        md.append(f"### {idx}. [{repo['title']}]({repo['url']})")
        md.append(f"- **Bahasa:** `{repo['language']}` | **Stars:** ⭐ {repo['score']:,} | **Domain:** `{repo['category']}`")
        md.append(f"- **Deskripsi:** {repo['description']}")
        if repo['tags']:
            md.append(f"- **Topics:** {', '.join([f'`{t}`' for t in repo['tags']])}")
        md.append(f"- **Takeaway Arsitektur:** Bedah cara codebase ini mendesain modularitas dan abstraction layer-nya.")
        md.append("")

    md.append("---\n*Generated autonomously by Antigravity Second Brain Engine.*")
    return "\n".join(md)


def update_vault_index(daily_files: list[Path]):
    """Update master INDEX.md in vault."""
    index_path = VAULT_DIR / "INDEX.md"
    lines = [
        "# 📚 Knowledge Vault Master Index",
        "",
        "Koleksi ringkasan pengetahuan teknis, pola arsitektur, dan referensi sistem.",
        "",
        "## 🗓️ Catatan Harian (Daily Syntheses)",
        ""
    ]
    for p in sorted(daily_files, reverse=True):
        date_name = p.stem
        lines.append(f"- [[daily/{p.name}|{date_name}]] - Ringkasan Wawasan Teknis")

    lines.append("")
    lines.append("## 🏷️ Taksonomi Kategori")
    lines.append("- `#architecture` : Pola desain sistem terdistribusi & backend")
    lines.append("- `#performance` : Optimasi memory, latency, concurrency")
    lines.append("- `#ai-systems` : Rekayasa agentic workflow & model serving")
    lines.append("")

    index_path.write_text("\n".join(lines), encoding="utf-8")


def generate_interactive_dashboard(signals: list[dict], repos: list[dict]):
    """Render a standalone, modern dark-mode dashboard HTML."""
    today_str = datetime.now().strftime("%d %B %Y")
    now_time = datetime.now().strftime("%H:%M:%S")

    cards_hn = []
    for item in signals:
        tags_badges = "".join([f'<span class="badge">{escape(t)}</span>' for t in item["tags"]])
        cards_hn.append(f"""
        <div class="card">
            <div class="card-meta">
                <span class="source hn">HackerNews</span>
                <span class="score">▲ {item['score']} pts</span>
                <span class="category">{escape(item['category'])}</span>
            </div>
            <h3 class="card-title"><a href="{escape(item['url'])}" target="_blank">{escape(item['title'])}</a></h3>
            <div class="tags">{tags_badges}</div>
            <div class="card-footer">
                <a href="{escape(item['discussion_url'])}" target="_blank" class="link-btn">💬 {item['comments']} Komentar Diskusi</a>
            </div>
        </div>
        """)

    cards_repos = []
    for repo in repos:
        topics_badges = "".join([f'<span class="badge">{escape(t)}</span>' for t in repo["tags"]])
        cards_repos.append(f"""
        <div class="card">
            <div class="card-meta">
                <span class="source gh">GitHub</span>
                <span class="score">★ {repo['score']:,}</span>
                <span class="category">{escape(repo['language'])}</span>
            </div>
            <h3 class="card-title"><a href="{escape(repo['url'])}" target="_blank">{escape(repo['title'])}</a></h3>
            <p class="desc">{escape(repo['description'])}</p>
            <div class="tags">{topics_badges}</div>
            <div class="card-footer">
                <a href="{escape(repo['url'])}" target="_blank" class="link-btn">Inspect Codebase ↗</a>
            </div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Second Brain - Daily Technical Intelligence</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            --accent: #58a6ff;
            --accent-green: #3fb950;
            --accent-orange: #f0883e;
            --card-hover: #1f242c;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            padding: 32px 24px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            margin-bottom: 32px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{ font-size: 24px; font-weight: 700; color: #f0f6fc; display: flex; align-items: center; gap: 10px; }}
        .header-meta {{ color: var(--text-muted); font-size: 14px; }}
        .section-title {{
            font-size: 18px;
            margin: 28px 0 16px;
            color: #f0f6fc;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 16px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .card:hover {{
            background: var(--card-hover);
            border-color: var(--accent);
            transform: translateY(-2px);
        }}
        .card-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            margin-bottom: 10px;
        }}
        .source {{
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .source.hn {{ background: rgba(240, 136, 62, 0.15); color: var(--accent-orange); }}
        .source.gh {{ background: rgba(63, 185, 80, 0.15); color: var(--accent-green); }}
        .score {{ color: var(--accent); font-weight: 600; }}
        .category {{ color: var(--text-muted); margin-left: auto; }}
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 10px;
        }}
        .card-title a {{
            color: #f0f6fc;
            text-decoration: none;
        }}
        .card-title a:hover {{ color: var(--accent); }}
        .desc {{
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 12px;
            line-height: 1.45;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 14px;
        }}
        .badge {{
            background: rgba(110, 118, 129, 0.2);
            color: var(--text-muted);
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 12px;
        }}
        .card-footer {{
            padding-top: 12px;
            border-top: 1px solid rgba(48, 54, 61, 0.6);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .link-btn {{
            color: var(--accent);
            text-decoration: none;
            font-size: 12px;
            font-weight: 500;
        }}
        .link-btn:hover {{ text-decoration: underline; }}
        .actions-bar {{
            margin-top: 32px;
            padding: 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>⚡ Second Brain: Technical Intelligence</h1>
                <div class="header-meta">Curated via Antigravity Autonomous Synthesizer • {today_str}</div>
            </div>
            <div class="header-meta">Updated: {now_time} Local</div>
        </header>

        <div class="section-title">🔥 High-Signal Discussions & Architecture Topics</div>
        <div class="grid">
            {"".join(cards_hn)}
        </div>

        <div class="section-title">⚡ High-Impact Open Source Repos</div>
        <div class="grid">
            {"".join(cards_repos)}
        </div>

        <div class="actions-bar">
            <span>📁 Markdown Vault: <code>vault/daily/{datetime.now().strftime('%Y-%m-%d')}.md</code></span>
            <span>💡 Tip: Buka folder <code>vault/</code> di Obsidian untuk visual knowledge graph.</span>
        </div>
    </div>
</body>
</html>
"""
    DASHBOARD_FILE.write_text(html_content, encoding="utf-8")
    INDEX_FILE.write_text(html_content, encoding="utf-8")


def main():
    print("[1/4] Membuat folder Obsidian Vault...")
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    print("[2/4] Fetching sinyal teknis dari HackerNews & GitHub...")
    hn_signals = fetch_hacker_news_signals(limit=8)
    gh_repos = fetch_github_trending(limit=6)

    print(f"      Ditemukan {len(hn_signals)} diskusi teknis, {len(gh_repos)} repo arsitektur.")

    print("[3/4] Mengompilasi catatan harian Obsidian...")
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_file = DAILY_DIR / f"{today_str}.md"
    digest_md = synthesize_technical_digest(hn_signals, gh_repos)
    daily_file.write_text(digest_md, encoding="utf-8")

    all_daily = list(DAILY_DIR.glob("*.md"))
    update_vault_index(all_daily)

    print("[4/4] Merender interactive visual dashboard...")
    generate_interactive_dashboard(hn_signals, gh_repos)

    print("\n✅ Sintesis selesai!")
    print(f"   - Vault Entry : {daily_file}")
    print(f"   - Index Master: {VAULT_DIR / 'INDEX.md'}")
    print(f"   - Dashboard UI: {DASHBOARD_FILE}")


if __name__ == "__main__":
    main()
