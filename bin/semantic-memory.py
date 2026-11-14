#!/usr/bin/env python3
"""
AI-AGENTS LOCAL ML SEMANTIC MEMORY ENGINE
==============================================================================
Provides local, zero-cloud-token ($0) vector embeddings and semantic search
across project research notes (wiki/research/), implementation plans (wiki/plans/),
architecture decision records (wiki/adr/), defect records (wiki/defects/),
release runbooks (wiki/releases/), and institutional rules.

Primary Backend:
  Local Ollama embeddings via 'nomic-embed-text' (768-dim, 8k context)
Defensive Fallback:
  Built-in TF-IDF vector space model (zero external pip dependencies)

Usage:
  bin/semantic-memory.py index [--project-dir DIR]
  bin/semantic-memory.py query "<search-concept>" [--top-k 5] [--category CAT] [--json]
  bin/semantic-memory.py status
==============================================================================
"""

import os
import sys
import json
import sqlite3
import struct
import math
import argparse
import re
import urllib.request
import urllib.error
from datetime import datetime

# ANSI Colors
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"

OLLAMA_EMBED_URL = os.environ.get("OLLAMA_EMBED_URL", "http://127.0.0.1:11434/api/embeddings")
EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")


def resolve_repo_root():
    if os.environ.get("AI_AGENTS_PROJECT_DIR") and os.path.exists(os.environ["AI_AGENTS_PROJECT_DIR"]):
        return os.path.abspath(os.environ["AI_AGENTS_PROJECT_DIR"])

    cwd = os.path.abspath(os.getcwd())
    if os.path.exists(os.path.join(cwd, ".agents")) or os.path.exists(os.path.join(cwd, ".git")) or os.path.exists(os.path.join(cwd, "wiki")):
        return cwd

    script_path = os.path.abspath(__file__)
    # Resolve symlinks
    while os.path.islink(script_path):
        script_path = os.readlink(script_path)
        if not os.path.isabs(script_path):
            script_path = os.path.join(os.path.dirname(script_path), script_path)
    return os.path.dirname(os.path.dirname(script_path))


def get_db_path(repo_root):
    mem_dir = os.path.join(repo_root, ".agents", "memory")
    os.makedirs(mem_dir, exist_ok=True)
    return os.path.join(mem_dir, "vector_store.db")


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS document_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_path TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding_type TEXT NOT NULL,
        embedding BLOB NOT NULL,
        mtime REAL NOT NULL,
        indexed_at TEXT NOT NULL,
        UNIQUE(source_path, chunk_index)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_category ON document_chunks(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_source ON document_chunks(source_path);")
    conn.commit()
    return conn


def get_ollama_embedding(text, model=EMBED_MODEL, timeout=10):
    """Fetches dense vector embedding from local Ollama instance."""
    payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_EMBED_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("embedding")
    except Exception:
        return None


# ==============================================================================
# DEFENSIVE FALLBACK: Pure Python TF-IDF Vector Space Model
# ==============================================================================
def tokenize(text):
    return re.findall(r"\b[A-Za-z0-9_-]{2,}\b", text.lower())


def compute_tfidf_vector(text, vocab):
    tokens = tokenize(text)
    if not tokens:
        return [0.0] * len(vocab)
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    vec = []
    for term in vocab:
        tf = freq.get(term, 0) / len(tokens)
        vec.append(tf)
    # Normalize L2
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def cosine_similarity(vec1, vec2):
    if len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def pack_vector(vec):
    return struct.pack(f"{len(vec)}f", *vec)


def unpack_vector(blob):
    count = len(blob) // 4
    return list(struct.unpack(f"{count}f", blob))


# ==============================================================================
# CHUNKING & DOCUMENT INGESTION
# ==============================================================================
def chunk_markdown(content, chunk_size=1000, overlap=150):
    """Splits markdown into coherent heading sections or overlapping windows."""
    sections = re.split(r"(?=\n#{1,3}\s+)", content)
    chunks = []
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        if len(sec) <= chunk_size:
            chunks.append(sec)
        else:
            # Sub-chunk long sections with overlap
            words = sec.split()
            current = []
            current_len = 0
            for w in words:
                current.append(w)
                current_len += len(w) + 1
                if current_len >= chunk_size:
                    chunks.append(" ".join(current))
                    # Retain overlap words
                    overlap_words = current[-int(overlap / 6):] if len(current) > 20 else []
                    current = overlap_words
                    current_len = sum(len(x) + 1 for x in current)
            if current:
                chunks.append(" ".join(current))
    return chunks


def extract_title(content, fallback_filename):
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return os.path.basename(fallback_filename)


def determine_category(rel_path):
    lower = rel_path.lower()
    if "wiki/research/" in lower:
        return "research"
    elif "wiki/plans/" in lower:
        return "plan"
    elif "wiki/adr/" in lower:
        return "adr"
    elif "wiki/defects/" in lower:
        return "defect"
    elif "wiki/releases/" in lower:
        return "release"
    elif "wiki/features/" in lower:
        return "feature"
    elif "skills/osint/" in lower:
        return "osint"
    elif "skills/bughunter/" in lower:
        return "bughunt"
    elif "skills/offensive/" in lower:
        return "offensive"
    elif "skills/" in lower:
        return "skill"
    elif "memory/" in lower or "rules/" in lower:
        return "rule"
    return "general"


def collect_documents(repo_root):
    targets = []
    patterns = [
        ("wiki/research", "*.md"),
        ("wiki/plans", "*.md"),
        ("wiki/adr", "*.md"),
        ("wiki/defects", "*.md"),
        ("wiki/releases", "*.md"),
        ("wiki/features", "*.md"),
        ("wiki", "*.md"),
        ("memory/global", "*.md"),
        ("rules", "*.md"),
        ("skills/osint", "*.md"),
        ("skills/bughunter", "*.md"),
        ("skills/offensive", "*.md"),
        ("skills", "*.md"),
    ]
    for rel_dir, ext in patterns:
        abs_dir = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(abs_dir):
            continue
        for root, _, files in os.walk(abs_dir):
            for file in files:
                if file.endswith(".md"):
                    abs_file = os.path.join(root, file)
                    rel_file = os.path.relpath(abs_file, repo_root)
                    # Deduplicate: Skip flat symlink/directories skills/offensive-*, skills/osint-*, skills/bughunter-* to avoid duplicate chunks
                    if rel_file.startswith("skills/offensive-") or rel_file.startswith("skills/osint-") or rel_file.startswith("skills/bughunter-"):
                        continue
                    targets.append((abs_file, rel_file))
    return sorted(list(set(targets)))


# ==============================================================================
# COMMANDS: INDEX & QUERY
# ==============================================================================
def cmd_index(repo_root):
    db_path = get_db_path(repo_root)
    conn = init_db(db_path)
    cur = conn.cursor()

    print(f"{BLUE}{BOLD}=============================================================================={NC}")
    print(f"{BLUE}{BOLD}         AI-AGENTS LOCAL ML SEMANTIC MEMORY INDEXER                           {NC}")
    print(f"{BLUE}{BOLD}=============================================================================={NC}")
    print(f"Repository Root : {repo_root}")
    print(f"Vector Database : {db_path}")

    # Check Ollama availability
    ollama_available = False
    test_vec = get_ollama_embedding("test probe")
    if test_vec is not None:
        ollama_available = True
        print(f"Embedding Engine: {GREEN}Ollama '{EMBED_MODEL}' ({len(test_vec)} dims) [Active]{NC}")
    else:
        print(f"Embedding Engine: {YELLOW}Built-in TF-IDF Fallback (Ollama embedding service not responding){NC}")

    documents = collect_documents(repo_root)
    print(f"Discovered Files: {BOLD}{len(documents)}{NC} markdown records across wiki & rules.\n")

    indexed_count = 0
    skipped_count = 0

    for abs_path, rel_path in documents:
        try:
            mtime = os.path.getmtime(abs_path)
            # Check existing mtime in DB
            cur.execute("SELECT mtime FROM document_chunks WHERE source_path = ? LIMIT 1", (rel_path,))
            row = cur.fetchone()
            if row and abs(row[0] - mtime) < 0.001:
                skipped_count += 1
                continue

            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            if not content.strip():
                continue

            # Delete old chunks for updated file
            cur.execute("DELETE FROM document_chunks WHERE source_path = ?", (rel_path,))

            chunks = chunk_markdown(content)
            title = extract_title(content, rel_path)
            category = determine_category(rel_path)
            timestamp = datetime.utcnow().isoformat() + "Z"

            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                emb = None
                emb_type = "ollama"
                if ollama_available:
                    emb = get_ollama_embedding(chunk)

                if emb is None:
                    # Fallback token hashing vector (256 bins)
                    emb_type = "hash_tfidf"
                    tokens = tokenize(chunk)
                    vec = [0.0] * 256
                    for t in tokens:
                        h = hash(t) % 256
                        vec[h] += 1.0
                    norm = math.sqrt(sum(x * x for x in vec))
                    if norm > 0:
                        vec = [x / norm for x in vec]
                    emb = vec

                blob = pack_vector(emb)
                cur.execute("""
                INSERT OR REPLACE INTO document_chunks 
                (source_path, chunk_index, category, title, content, embedding_type, embedding, mtime, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (rel_path, idx, category, title, chunk, emb_type, blob, mtime, timestamp))

            indexed_count += 1
            sys.stdout.write(f"\r  Indexed: {GREEN}{rel_path}{NC} ({len(chunks)} chunks)               ")
            sys.stdout.flush()

        except Exception as e:
            print(f"\n{RED}[ERROR] Failed indexing {rel_path}: {e}{NC}")

    conn.commit()
    conn.close()

    print(f"\n\n{GREEN}[SUCCESS]{NC} Indexing complete!")
    print(f"  - Newly/Re-Indexed Files : {BOLD}{indexed_count}{NC}")
    print(f"  - Unmodified (Up to date): {BOLD}{skipped_count}{NC}")
    print(f"  - Vector Store Location  : {CYAN}{db_path}{NC}\n")


def cmd_query(repo_root, query_text, top_k=5, filter_category=None, as_json=False):
    db_path = get_db_path(repo_root)
    if not os.path.exists(db_path):
        if as_json:
            print(json.dumps({"error": "Vector database not initialized. Run 'ai-agents memory index' first."}))
        else:
            print(f"{RED}[ERROR]{NC} Vector database not found. Run {CYAN}ai-agents memory index{NC} first.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Retrieve all chunks
    if filter_category:
        cur.execute("SELECT source_path, chunk_index, category, title, content, embedding_type, embedding FROM document_chunks WHERE category = ?", (filter_category,))
    else:
        cur.execute("SELECT source_path, chunk_index, category, title, content, embedding_type, embedding FROM document_chunks")
    rows = cur.fetchall()

    if not rows:
        if as_json:
            print(json.dumps([]))
        else:
            print(f"{YELLOW}[NOTICE] No document chunks found in database.{NC}")
        conn.close()
        return

    # Check dominant embedding type in DB
    primary_type = rows[0][5]

    # Generate query embedding
    query_vec = None
    if primary_type == "ollama":
        query_vec = get_ollama_embedding(query_text)

    if query_vec is None:
        # Fallback query embedding
        tokens = tokenize(query_text)
        vec = [0.0] * 256
        for t in tokens:
            h = hash(t) % 256
            vec[h] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        query_vec = vec

    scored_results = []
    for source_path, chunk_idx, cat, title, content, emb_type, blob in rows:
        chunk_vec = unpack_vector(blob)
        sim = cosine_similarity(query_vec, chunk_vec)
        scored_results.append({
            "source_path": source_path,
            "chunk_index": chunk_idx,
            "category": cat,
            "title": title,
            "similarity": round(sim, 4),
            "content": content
        })

    conn.close()

    scored_results.sort(key=lambda x: x["similarity"], reverse=True)
    top_results = scored_results[:top_k]

    if as_json:
        print(json.dumps(top_results, indent=2))
        return

    print(f"\n{BLUE}{BOLD}=============================================================================={NC}")
    print(f"{BLUE}{BOLD}         SEMANTIC MEMORY SEARCH RESULTS ({len(top_results)} matches)                     {NC}")
    print(f"{BLUE}{BOLD}=============================================================================={NC}")
    print(f"Query: \"{BOLD}{query_text}{NC}\"\n")

    for rank, res in enumerate(top_results, 1):
        score_color = GREEN if res["similarity"] >= 0.70 else (YELLOW if res["similarity"] >= 0.50 else NC)
        print(f"{BOLD}#{rank} [{res['category'].upper()}]{NC} {CYAN}{res['source_path']}{NC} (Score: {score_color}{res['similarity']:.4f}{NC})")
        print(f"   {BOLD}Title:{NC} {res['title']}")
        # First 3 lines preview
        preview_lines = [line.strip() for line in res["content"].splitlines() if line.strip()][:3]
        preview = " ".join(preview_lines)
        if len(preview) > 180:
            preview = preview[:180] + "..."
        print(f"   {preview}\n")


def cmd_status(repo_root):
    db_path = get_db_path(repo_root)
    if not os.path.exists(db_path):
        print(f"{YELLOW}Vector store not initialized. Run 'ai-agents memory index' to create.{NC}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT source_path) FROM document_chunks")
    total_chunks, total_docs = cur.fetchone()

    cur.execute("SELECT category, COUNT(*) FROM document_chunks GROUP BY category")
    by_cat = cur.fetchall()
    conn.close()

    print(f"{BOLD}Semantic Vector Store Status:{NC}")
    print(f"  Location      : {db_path}")
    print(f"  Total Docs    : {total_docs}")
    print(f"  Total Chunks  : {total_chunks}")
    print(f"  By Category   :")
    for cat, cnt in by_cat:
        print(f"    - {cat:<12}: {cnt} chunks")


def main():
    parser = argparse.ArgumentParser(description="AI-Agents Local ML Semantic Memory Engine")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # index
    index_parser = subparsers.add_parser("index", help="Index wiki and institutional documents into vector store")
    index_parser.add_argument("--project-dir", default=None, help="Root directory of target project")

    # query
    query_parser = subparsers.add_parser("query", help="Semantic similarity search across indexed memory")
    query_parser.add_argument("query", help="Natural language search prompt")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    query_parser.add_argument("--category", default=None, help="Filter by category (research, plan, adr, defect, release, rule)")
    query_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    query_parser.add_argument("--project-dir", default=None, help="Root directory of target project")

    # status
    status_parser = subparsers.add_parser("status", help="Show vector store status and statistics")
    status_parser.add_argument("--project-dir", default=None, help="Root directory of target project")

    args = parser.parse_args()
    repo_root = args.project_dir or resolve_repo_root()

    if args.subcommand == "index":
        cmd_index(repo_root)
    elif args.subcommand == "query":
        cmd_query(repo_root, args.query, top_k=args.top_k, filter_category=args.category, as_json=args.json)
    elif args.subcommand == "status":
        cmd_status(repo_root)


if __name__ == "__main__":
    main()
