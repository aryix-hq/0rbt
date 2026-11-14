# Contributing to 0rbt

Thank you for your interest in contributing to **0rbt**! We are building the open-source engineering architecture intelligence pipeline, dataset, and specialized decision model (`aryix/0rbt-architect`) to help engineers and AI coding assistants build outage-proof distributed systems.

---

## 🌟 How You Can Contribute

1. **Add New Engineering Blog Feeds**:
   - Add new verified tech blogs to `config/engineering_blogs_registry.json`.
   - Ensure the feed URL returns valid RSS/Atom/JSON XML.
2. **Improve Historical Crawlers**:
   - Enhance `bin/crawl-historical-archives.py` with sitemap or archive scrapers for platforms like Medium, Ghost, WordPress, Substack, or custom engineering sites.
3. **Enhance Invariant & Anti-Pattern Rules**:
   - Add verified distributed system invariants discovered in recent major outages.
4. **Dataset & Model Evaluation Benchmarks**:
   - Contribute challenging architectural dilemma questions to our evaluation harness.

---

## 🛠 Local Setup & Development

```bash
# 1. Clone your fork
git clone https://github.com/aryix-hq/0rbt.git
cd 0rbt

# 2. Verify dependencies (Python 3.10+, SQLite3)
python3 --version

# 3. Pull required local Ollama models (free, local inference)
ollama pull qwen2.5-coder:14b
ollama pull nomic-embed-text

# 4. Run test suites
python3 bin/test-blog-pipeline.py
python3 bin/local-code-reviewer.py --strict
```

---

## 📋 Pull Request Guidelines

1. **Strict PR Mandate**:
   - Direct pushes to `main` are strictly prohibited.
   - All contributions must originate from a descriptive feature branch (`feat/new-blog-source`, `fix/dedup-hash`, `refactor/scraper`).
2. **Zero Plaintext Secrets**:
   - Never commit API keys, private tokens, or credentials.
   - Run `./bin/audit-secrets.sh` before committing.
3. **Deterministic Review Gate**:
   - Every PR is evaluated using `bin/two-axis-reviewer.py --base main` verifying both standards/invariants and specification coverage.

---

## 📜 Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to `opensource@aryix.com`.
