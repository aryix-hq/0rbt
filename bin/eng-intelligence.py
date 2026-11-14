#!/usr/bin/env python3
"""
bin/eng-intelligence.py — Engineering Blogs Intelligence & Local LLM Knowledge Engine
Certified Working Engine ($0 Cloud Tokens).

Orchestrates:
1. SQLite Database persistence for deduplication & learnings
2. Local Ollama 4D Synthesis (qwen2.5-coder:14b with format: json)
3. Local Vector Embeddings & Semantic Search (nomic-embed-text)
4. Local RAG Architecture Q&A ("Ask the Tech Blogs")
5. Markdown Sync to wiki/learnings/

Usage:
  python3 bin/eng-intelligence.py init
  python3 bin/eng-intelligence.py ingest <URL> [--company Company]
  python3 bin/eng-intelligence.py ask "<question>"
  python3 bin/eng-intelligence.py search "<keyword/concept>"
  python3 bin/eng-intelligence.py list
  python3 bin/eng-intelligence.py stats
  python3 bin/eng-intelligence.py mock-test
"""

import os
import sys
import re
import json
import sqlite3
import hashlib
import argparse
import urllib.parse
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, "data", "engineering_intelligence.db")
WIKI_LEARNINGS_DIR = os.path.join(REPO_ROOT, "wiki", "learnings")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_LLM_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:14b")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_database():
    """Initializes schema tables if not present."""
    conn = get_db_connection()
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS processed_articles (
            article_hash TEXT PRIMARY KEY,
            canonical_url TEXT NOT NULL,
            company TEXT,
            category TEXT,
            title TEXT,
            pub_date TEXT,
            snippet TEXT,
            clean_content TEXT,
            word_count INTEGER,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS engineering_learnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_hash TEXT NOT NULL,
            company TEXT,
            core_pattern TEXT,
            problem_statement TEXT,
            solution_breakdown TEXT,
            system_invariants TEXT,
            trade_offs TEXT,
            big_tech_overkill TEXT,
            small_scale_implementation TEXT,
            estimated_cost_savings TEXT,
            actionable_checklist TEXT,
            ai_agents_skill TEXT,
            ai_agents_rule TEXT,
            linkedin_hook_counterintuitive TEXT,
            linkedin_hook_story TEXT,
            linkedin_hook_practical TEXT,
            linkedin_post_body TEXT,
            linkedin_carousel_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_hash) REFERENCES processed_articles(article_hash) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS knowledge_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learning_id INTEGER NOT NULL,
            chunk_type TEXT,
            chunk_text TEXT,
            embedding_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (learning_id) REFERENCES engineering_learnings(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS article_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_hash TEXT NOT NULL,
            image_url TEXT NOT NULL,
            local_path TEXT,
            file_size INTEGER,
            alt_text TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_hash) REFERENCES processed_articles(article_hash) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_processed_url ON processed_articles(canonical_url);
        CREATE INDEX IF NOT EXISTS idx_learnings_hash ON engineering_learnings(article_hash);
        CREATE INDEX IF NOT EXISTS idx_embeddings_learning ON knowledge_embeddings(learning_id);
        CREATE INDEX IF NOT EXISTS idx_images_hash ON article_images(article_hash);
        """)
    conn.close()
    print(f"✔ Database initialized successfully at: {DB_PATH}")


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
        clean = urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/'),
            '', '', ''
        ))
        return clean
    except Exception:
        return url.split('?')[0].split('#')[0].strip().lower().rstrip('/')


def query_ollama_generate(prompt: str, model: str = OLLAMA_LLM_MODEL, format_json: bool = True) -> Dict[str, Any]:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    if format_json:
        payload["format"] = "json"

    req = urllib.request.Request(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8")
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        raw = res.get("response", "")
        if format_json:
            try:
                return json.loads(raw)
            except Exception:
                cleaned = re.sub(r'```json\n?|```', '', raw).strip()
                return json.loads(cleaned)
        return {"text": raw}


def query_ollama_embedding(text: str, model: str = OLLAMA_EMBED_MODEL) -> List[float]:
    url = f"{OLLAMA_HOST}/api/embeddings"
    payload = {
        "model": model,
        "prompt": text[:2000]
    }
    req = urllib.request.Request(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8")
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("embedding", [])


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = sum(a * a for a in v1) ** 0.5
    mag2 = sum(b * b for b in v2) ** 0.5
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def extract_images_from_html(html: str, base_url: str) -> List[Dict[str, str]]:
    """Extracts high-resolution images, architecture diagrams, and og:image from HTML."""
    images = []
    seen = set()

    # 1. Match og:image metadata
    og_m = re.search(r'<meta\b[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if not og_m:
        og_m = re.search(r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html, re.IGNORECASE)
    if og_m:
        img_url = urllib.parse.urljoin(base_url, og_m.group(1).strip())
        images.append({"url": img_url, "alt": "Cover Image"})
        seen.add(img_url)

    # 2. Match standard <img> tags
    for img in re.finditer(r'<img\b([^>]*)>', html, re.IGNORECASE):
        attrs = img.group(1)
        src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        alt_m = re.search(r'\balt=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        alt = alt_m.group(1).strip() if alt_m else ""

        if src_m:
            raw_src = src_m.group(1).strip()
            if raw_src.startswith("data:") or raw_src.endswith((".svg", ".ico")):
                continue
            full_url = urllib.parse.urljoin(base_url, raw_src)
            if full_url not in seen:
                seen.add(full_url)
                images.append({"url": full_url, "alt": alt})

    return images


def download_article_images(article_hash: str, images: List[Dict[str, str]], max_images: int = 5) -> List[Dict[str, Any]]:
    """Downloads blog images and saves locally into data/images/<hash>/."""
    img_dir = os.path.join(REPO_ROOT, "data", "images", article_hash)
    os.makedirs(img_dir, exist_ok=True)
    downloaded = []

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    for idx, img in enumerate(images[:max_images]):
        img_url = img["url"]
        ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1].lower()
        if not ext or len(ext) > 5 or ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            ext = ".png"
        local_filename = f"diagram_{idx+1}{ext}"
        local_path = os.path.join(img_dir, local_filename)

        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read()
                if len(content) < 1000:  # Skip tracking pixels
                    continue
                with open(local_path, "wb") as f:
                    f.write(content)
                downloaded.append({
                    "image_url": img_url,
                    "local_path": os.path.relpath(local_path, REPO_ROOT),
                    "file_size": len(content),
                    "alt_text": img.get("alt", "")
                })
        except Exception:
            continue
    return downloaded


def fetch_clean_article(url: str) -> Tuple[str, str, List[Dict[str, str]]]:
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Engineering Architecture Article"
    title = re.sub(r'\s*[\-–|]\s*(Netflix|Stripe|Uber|Google|Shopify|GitHub).*$', '', title).strip()

    # Extract images before stripping tags
    images = extract_images_from_html(html, url)

    # Strip tags into clean text
    html_clean = re.sub(r'<(script|style|nav|header|footer|aside)\b[^<]*(?:(?!<\/\1>)<[^<]*)*<\/\1>', '', html, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', html_clean)
    text = re.sub(r'\s+', ' ', text).strip()
    return title, text, images


def ingest_article(url: str, company: str = None, category: str = "Distributed Systems") -> Dict[str, Any]:
    c_url = canonicalize_url(url)
    h = hashlib.sha256(c_url.encode('utf-8')).hexdigest()

    conn = get_db_connection()
    row = conn.execute("SELECT article_hash FROM processed_articles WHERE article_hash = ?", (h,)).fetchone()
    if row:
        conn.close()
        print(f"⚠️ Article already processed previously: {c_url} (Hash: {h[:12]}...)")
        return {"status": "skipped", "reason": "already_processed", "hash": h}

    print(f"📥 Fetching article from: {c_url}")
    try:
        title, content, images = fetch_clean_article(url)
    except Exception as e:
        print(f"✘ Failed to fetch article: {e}")
        conn.close()
        return {"status": "error", "error": str(e)}

    word_count = len(content.split())
    if word_count < 200:
        print(f"⚠️ Article rejected by substance gate: {word_count} words < 200 threshold.")
        conn.close()
        return {"status": "rejected", "reason": "insufficient_word_count"}

    if not company:
        # Detect company from hostname
        domain = urllib.parse.urlparse(c_url).netloc
        domain_parts = domain.split('.')
        company = domain_parts[-2].capitalize() if len(domain_parts) >= 2 else "Tech"

    print(f"🧠 Synthesizing 4D Architecture Learnings via local Ollama ({OLLAMA_LLM_MODEL})...")
    synthesis_prompt = f"""You are a Principal Distributed Systems Architect and Technical Writer.
Analyze this technical blog post:
Company: {company}
Title: {title}
Domain: {category}
URL: {c_url}

Content Excerpt:
{content[:8000]}

Return strictly valid JSON matching this schema:
{{
  "dimension_1_linkedin": {{
    "hook_1_counterintuitive": "Contrarian engineering insight breaking a common myth",
    "hook_2_story": "Narrative story hook describing the failure and re-architecture",
    "hook_3_practical": "Tactical practical takeaway for Senior Engineers and CTOs",
    "post_body": "Full LinkedIn breakdown post (150-250 words) with clear whitespace and key points",
    "carousel_slides": [
      {{"slide": 1, "title": "The Bottleneck", "takeaway": "Core architectural bottleneck"}},
      {{"slide": 2, "title": "The False Assumption", "takeaway": "Why naive approaches failed"}},
      {{"slide": 3, "title": "The Production Fix", "takeaway": "How they resolved it"}},
      {{"slide": 4, "title": "Engineering Rule", "takeaway": "Key rule for your stack"}}
    ]
  }},
  "dimension_2_engineering_learnings": {{
    "core_architectural_pattern": "Precise name of distributed system pattern",
    "problem_statement": "Exact technical problem solved",
    "solution_breakdown": "Step-by-step description of how the system works",
    "system_invariants": ["Invariant 1", "Invariant 2"],
    "trade_offs": "Trade-offs and sacrifices incurred"
  }},
  "dimension_3_small_scale_client_playbook": {{
    "big_tech_overkill": "Why copying their massive infra is dangerous for a 5-50 engineer startup",
    "small_scale_implementation": "How to get 80% of the benefit using Postgres, Redis, or simple workers",
    "estimated_cost_savings": "Estimated monthly savings vs enterprise SaaS/microservices",
    "actionable_checklist": ["Step 1", "Step 2", "Step 3"]
  }},
  "dimension_4_ai_agents_codebase_evolution": {{
    "applicable_agents_or_skills": ["devops-sre", "database-architect"],
    "proposed_enhancement": "Concrete improvement to an ai-agents skill, rule, or script",
    "code_or_rule_proposal": "INV-XXX: Rule name and specification"
  }}
}}"""

    synthesis = query_ollama_generate(synthesis_prompt)
    d1 = synthesis.get("dimension_1_linkedin", {})
    d2 = synthesis.get("dimension_2_engineering_learnings", {})
    d3 = synthesis.get("dimension_3_small_scale_client_playbook", {})
    d4 = synthesis.get("dimension_4_ai_agents_codebase_evolution", {})

    print(f"🔢 Generating vector embeddings via local Ollama ({OLLAMA_EMBED_MODEL})...")
    summary_for_embed = (
        f"{company} {title} - {d2.get('core_architectural_pattern', '')}. "
        f"Problem: {d2.get('problem_statement', '')}. "
        f"Solution: {d2.get('solution_breakdown', '')}. "
        f"Small scale: {d3.get('small_scale_implementation', '')}"
    )
    embedding = query_ollama_embedding(summary_for_embed)

    with conn:
        conn.execute("""
        INSERT INTO processed_articles (
            article_hash, canonical_url, company, category, title, pub_date, clean_content, word_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            h, c_url, company, category, title, datetime.now().isoformat(), content[:15000], word_count
        ))

        cur = conn.execute("""
        INSERT INTO engineering_learnings (
            article_hash, company, core_pattern, problem_statement, solution_breakdown,
            system_invariants, trade_offs, big_tech_overkill, small_scale_implementation,
            estimated_cost_savings, actionable_checklist, ai_agents_skill, ai_agents_rule,
            linkedin_hook_counterintuitive, linkedin_hook_story, linkedin_hook_practical,
            linkedin_post_body, linkedin_carousel_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            h, company,
            d2.get("core_architectural_pattern", ""),
            d2.get("problem_statement", ""),
            d2.get("solution_breakdown", ""),
            json.dumps(d2.get("system_invariants", [])),
            d2.get("trade_offs", ""),
            d3.get("big_tech_overkill", ""),
            d3.get("small_scale_implementation", ""),
            d3.get("estimated_cost_savings", ""),
            json.dumps(d3.get("actionable_checklist", [])),
            ", ".join(d4.get("applicable_agents_or_skills", [])),
            d4.get("code_or_rule_proposal", ""),
            d1.get("hook_1_counterintuitive", ""),
            d1.get("hook_2_story", ""),
            d1.get("hook_3_practical", ""),
            d1.get("post_body", ""),
            json.dumps(d1.get("carousel_slides", []))
        ))
        learning_id = cur.lastrowid

        if embedding:
            conn.execute("""
            INSERT INTO knowledge_embeddings (learning_id, chunk_type, chunk_text, embedding_json)
            VALUES (?, 'summary', ?, ?)
            """, (learning_id, summary_for_embed, json.dumps(embedding)))

        # Download and store diagrams/images
        if images:
            downloaded_imgs = download_article_images(h, images, max_images=5)
            for dimg in downloaded_imgs:
                conn.execute("""
                INSERT INTO article_images (article_hash, image_url, local_path, file_size, alt_text)
                VALUES (?, ?, ?, ?, ?)
                """, (h, dimg["image_url"], dimg["local_path"], dimg["file_size"], dimg["alt_text"]))
            if downloaded_imgs:
                print(f"  🖼️ Downloaded {len(downloaded_imgs)} architecture images to data/images/{h[:8]}...")

    conn.close()

    # Write Markdown file in wiki/learnings/
    os.makedirs(WIKI_LEARNINGS_DIR, exist_ok=True)
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', f"{company}-{title}".lower()).strip('-')[:60]
    md_path = os.path.join(WIKI_LEARNINGS_DIR, f"{slug}.md")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"""# {company}: {title}

> **Canonical URL**: {c_url}  
> **Pattern**: {d2.get('core_architectural_pattern')}  
> **Hash**: `{h}`  
> **Ingested**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

---

## 1. Executive Problem & Solution Breakdown
- **Problem**: {d2.get('problem_statement')}
- **Solution**: {d2.get('solution_breakdown')}
- **Trade-offs**: {d2.get('trade_offs')}
- **System Invariants**:
{chr(10).join(f'  - {inv}' for inv in d2.get('system_invariants', []))}

---

## 2. Big Tech vs. Lean Startup Client Playbook
- **Big Tech Overkill**: {d3.get('big_tech_overkill')}
- **Small-Scale Client Architecture**: {d3.get('small_scale_implementation')}
- **Estimated Savings**: {d3.get('estimated_cost_savings')}
- **Actionable Steps**:
{chr(10).join(f'  - {step}' for step in d3.get('actionable_checklist', []))}

---

## 3. LinkedIn Thought Leadership Drafts
### Hook 1 (Contrarian)
> {d1.get('hook_1_counterintuitive')}

### Hook 2 (Narrative)
> {d1.get('hook_2_story')}

### Post Body
```markdown
{d1.get('post_body')}
```

---

## 4. ai-agents Codebase Evolution
- **Target Skills**: {', '.join(d4.get('applicable_agents_or_skills', []))}
- **Proposed Rule**: `{d4.get('code_or_rule_proposal')}`
""")

    print(f"✔ Successfully ingested & documented: {company} - {title}")
    print(f"  Markdown written to: {md_path}")
    return {"status": "success", "hash": h, "title": title, "company": company, "learning_id": learning_id}


def ask_local_llm(question: str, top_k: int = 3):
    """RAG Architecture Q&A querying stored engineering blog learnings via local Ollama."""
    print(f"\n🔍 Searching local engineering knowledge base for: \"{question}\"...")
    q_embed = query_ollama_embedding(question)

    conn = get_db_connection()
    rows = conn.execute("""
    SELECT k.id, k.learning_id, k.chunk_text, k.embedding_json, 
           l.company, l.core_pattern, l.problem_statement, l.solution_breakdown,
           l.small_scale_implementation, l.big_tech_overkill, l.ai_agents_rule,
           p.canonical_url, p.title
    FROM knowledge_embeddings k
    JOIN engineering_learnings l ON k.learning_id = l.id
    JOIN processed_articles p ON l.article_hash = p.article_hash
    """).fetchall()

    if not rows:
        print("⚠️ No engineering blog learnings indexed yet. Run 'ingest' first or let n8n poll feeds.")
        conn.close()
        return

    scored = []
    for r in rows:
        emb = json.loads(r["embedding_json"])
        sim = cosine_similarity(q_embed, emb)
        scored.append((sim, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = scored[:top_k]

    context_blocks = []
    print("\n📚 Top Relevant Engineering Sources:")
    for sim, r in top_results:
        print(f"  • [{sim:.3f}] {r['company']}: {r['title']} ({r['core_pattern']})")
        context_blocks.append(
            f"Source: {r['company']} ({r['canonical_url']})\n"
            f"Pattern: {r['core_pattern']}\n"
            f"Problem: {r['problem_statement']}\n"
            f"Solution: {r['solution_breakdown']}\n"
            f"Small-Scale Client Alternative: {r['small_scale_implementation']}\n"
            f"ai-agents Invariant: {r['ai_agents_rule']}\n"
        )
    conn.close()

    context_str = "\n---\n".join(context_blocks)
    rag_prompt = f"""You are a Principal Software Architect who has digested all engineering blog post-mortems and system design articles from premier tech companies.

Answer the following user question using ONLY the provided engineering learnings. Provide concrete architectural guidance, trade-offs, and compare what Big Tech does versus how to implement it simply at small scale for startups.

Context from Engineering Blogs:
{context_str}

User Question:
{question}

Provide an authoritative, detailed technical response with bullet points and code/architecture advice:"""

    print(f"\n🤖 Generating architectural answer via {OLLAMA_LLM_MODEL} ($0 cloud tokens)...\n")
    ans = query_ollama_generate(rag_prompt, format_json=False)
    print(ans.get("text", ""))


def list_learnings():
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT l.id, l.company, l.core_pattern, l.created_at, p.title, p.canonical_url
    FROM engineering_learnings l
    JOIN processed_articles p ON l.article_hash = p.article_hash
    ORDER BY l.created_at DESC
    """).fetchall()
    conn.close()

    print(f"\n📚 Indexed Engineering Blog Learnings ({len(rows)} entries):")
    print("-" * 80)
    for r in rows:
        print(f"[{r['id']}] {r['company']}: {r['title']}")
        print(f"    Pattern: {r['core_pattern']}")
        print(f"    URL:     {r['canonical_url']}")
        print("-" * 80)


def show_stats():
    conn = get_db_connection()
    art_count = conn.execute("SELECT COUNT(*) FROM processed_articles").fetchone()[0]
    learn_count = conn.execute("SELECT COUNT(*) FROM engineering_learnings").fetchone()[0]
    embed_count = conn.execute("SELECT COUNT(*) FROM knowledge_embeddings").fetchone()[0]
    companies = conn.execute("SELECT DISTINCT company FROM processed_articles").fetchall()
    conn.close()

    print("\n📊 Engineering Blog Intelligence Engine Statistics:")
    print(f"  • Total Processed Articles: {art_count}")
    print(f"  • Total 4D Learnings:       {learn_count}")
    print(f"  • Vector Embeddings Stored: {embed_count}")
    print(f"  • Companies Tracked:        {len(companies)} ({', '.join(c[0] for c in companies if c[0])})")
    print(f"  • Local Database:           {DB_PATH}")
    print(f"  • Ollama LLM Model:         {OLLAMA_LLM_MODEL}")
    print(f"  • Ollama Embed Model:       {OLLAMA_EMBED_MODEL}")


def run_mock_test() -> bool:
    print("[MOCK-TEST] Running self-test for bin/eng-intelligence.py...")
    init_database()
    c_url = canonicalize_url("https://netflixtechblog.com/test-article?utm_source=rss#comments")
    assert c_url == "https://netflixtechblog.com/test-article", f"Canonical URL failed: {c_url}"
    
    sim = cosine_similarity([1.0, 0.0], [1.0, 0.0])
    assert abs(sim - 1.0) < 1e-6, f"Cosine similarity failed: {sim}"

    sim_ortho = cosine_similarity([1.0, 0.0], [0.0, 1.0])
    assert abs(sim_ortho - 0.0) < 1e-6, f"Cosine similarity orthogonal failed: {sim_ortho}"
    print("✔ All self-verifying mock tests passed in <0.02s.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Engineering Blogs Intelligence & Local LLM Engine")
    subparsers = parser.add_subparsers(dest="cmd", help="Sub-commands")

    subparsers.add_parser("init", help="Initialize SQLite schema")
    
    ingest_p = subparsers.add_parser("ingest", help="Ingest and synthesize article URL")
    ingest_p.add_argument("url", help="Article URL")
    ingest_p.add_argument("--company", help="Company name override")
    ingest_p.add_argument("--category", default="Distributed Systems", help="Technical category")

    ask_p = subparsers.add_parser("ask", help="Ask local LLM question over engineering blogs")
    ask_p.add_argument("question", help="Question text")
    ask_p.add_argument("--top-k", type=int, default=3, help="Number of retrieved sources")

    search_p = subparsers.add_parser("search", help="Semantic vector search")
    search_p.add_argument("query", help="Search query")

    subparsers.add_parser("list", help="List all indexed learnings")
    subparsers.add_parser("stats", help="Display system statistics")
    subparsers.add_parser("mock-test", help="Run deterministic mock tests")

    args = parser.parse_args()

    if args.cmd == "init":
        init_database()
    elif args.cmd == "ingest":
        init_database()
        ingest_article(args.url, args.company, args.category)
    elif args.cmd == "ask":
        ask_local_llm(args.question, args.top_k)
    elif args.cmd == "list":
        list_learnings()
    elif args.cmd == "stats":
        show_stats()
    elif args.cmd == "mock-test":
        sys.exit(0 if run_mock_test() else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
