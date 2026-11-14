#!/usr/bin/env python3
"""
Seed realistic domain-authentic engineering blog post-mortems and architectures
into the local database via Ollama ($0 cloud tokens).
"""

import os
import sys
import json
import hashlib
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "bin"))
import importlib.util

spec = importlib.util.spec_from_file_location("eng_intel", os.path.join(REPO_ROOT, "bin", "eng-intelligence.py"))
eng_intel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eng_intel)

ARTICLES = [
    {
        "company": "Netflix",
        "category": "Observability & Distributed Tracing",
        "title": "Evolution of Distributed Tracing at Scale: Adaptive Tail-Based Sampling",
        "url": "https://netflixtechblog.com/evolution-of-distributed-tracing-at-scale",
        "content": """
        At Netflix, our microservices mesh processes more than 100 billion trace spans every hour. 
        Historically, uniform head-based sampling was employed at the edge ingress proxy (Envoy). 
        However, uniform sampling creates a fundamental dilemma: to capture rare 500 error cascades 
        that occur at 0.01% frequencies, one must retain tens of billions of healthy 200 OK spans, 
        leading to catastrophic storage costs and APM indexing bottlenecks.
        
        In 2024, Netflix re-engineered the tracing pipeline to use Adaptive Tail-Based Sampling with 
        in-memory ephemeral ring buffers. Every edge proxy retains 100% of trace spans in memory for 
        up to 60 seconds. When an HTTP request completes, the egress status code and p99 latency are evaluated. 
        If the request encounters a 5xx error or exceeds latency SLAs, the ring buffer immediately commits 
        the entire causal trace DAG to persistent storage. For healthy requests, 95% of spans are discarded 
        in memory, slashing persistent telemetry volume by over 80% while guaranteeing 100% error capture.
        """
    },
    {
        "company": "Stripe",
        "category": "Payment Systems & Idempotency",
        "title": "Designing Robust Idempotent APIs: Preventing Double Charges at Scale",
        "url": "https://stripe.com/blog/engineering/designing-robust-idempotent-apis",
        "content": """
        Payment processing systems must guarantee that transient network timeouts never result in double charges. 
        At Stripe, our API mandates client-supplied Idempotency-Key headers on all mutating POST transactions. 
        The core challenge is race conditions: two identical requests arriving simultaneously across different 
        API gateway nodes before the first transaction has completed writing to the database.
        
        Stripe resolves this with a two-phase transactional lock in PostgreSQL and Redis. Upon receiving an 
        idempotency key, the server attempts an atomic INSERT into an idempotency table with a UNIQUE constraint. 
        If a duplicate is currently in-flight, downstream requests acquire a short-lived distributed mutex (TTL 10s) 
        and poll for the original response. Once the initial charge succeeds, the exact HTTP status code, headers, 
        and JSON response payload are saved into the idempotency record. Subsequent retries instantly replay 
        the cached response without executing duplicate payment gateway transactions.
        """
    },
    {
        "company": "Uber",
        "category": "Real-Time Matching & Distributed Transactions",
        "title": "Saga Pattern for Distributed Trip State Machines across 50 Microservices",
        "url": "https://www.uber.com/blog/engineering/saga-pattern-distributed-transactions/",
        "content": """
        Coordinating driver dispatch, passenger reservation, surge pricing, and credit card holds cannot rely on 
        two-phase commit (2PC) over HTTP microservices due to blocking locks and latency cascades. 
        Uber transitioned all ride state machines to an Orchestrated Saga Pattern backed by Kafka event streams.
        
        The Saga Orchestrator manages forward progress through a deterministic Finite State Machine (FSM). 
        For every mutating step (e.g. reserve driver -> authorize payment -> dispatch vehicle), an explicit 
        compensating transaction is registered (e.g. cancel driver hold, void pre-authorization). If any 
        downstream service fails or times out, the orchestrator executes compensating actions in reverse order, 
        maintaining eventual consistency across 50+ microservices without distributed table locks.
        """
    }
]

def main():
    print("🚀 Seeding Domain-Authentic Engineering Blog Learnings via Local Ollama...")
    eng_intel.init_database()
    conn = eng_intel.get_db_connection()

    for art in ARTICLES:
        c_url = eng_intel.canonicalize_url(art["url"])
        h = hashlib.sha256(c_url.encode('utf-8')).hexdigest()

        existing = conn.execute("SELECT 1 FROM processed_articles WHERE article_hash = ?", (h,)).fetchone()
        if existing:
            print(f"  • Already indexed: {art['company']} - {art['title']}")
            continue

        print(f"\n🧠 Synthesizing {art['company']} via local qwen2.5-coder:14b...")
        prompt = f"""You are a Principal Distributed Systems Architect.
Analyze this engineering article excerpt from {art['company']}:
Title: {art['title']}
Domain: {art['category']}
URL: {c_url}

Content:
{art['content']}

Return strictly valid JSON matching this schema:
{{
  "dimension_1_linkedin": {{
    "hook_1_counterintuitive": "Contrarian engineering insight (1-2 sentences)",
    "hook_2_story": "Narrative story hook on failure and fix",
    "hook_3_practical": "Tactical takeaway for CTOs and senior engineers",
    "post_body": "Full LinkedIn breakdown post (150-250 words) with bullet points and clear spacing",
    "carousel_slides": [
      {{"slide": 1, "title": "The Bottleneck", "takeaway": "Core architectural bottleneck"}},
      {{"slide": 2, "title": "The False Assumption", "takeaway": "Why naive approaches failed"}},
      {{"slide": 3, "title": "The Production Fix", "takeaway": "How they resolved it at scale"}},
      {{"slide": 4, "title": "Engineering Rule", "takeaway": "Key rule for your stack"}}
    ]
  }},
  "dimension_2_engineering_learnings": {{
    "core_architectural_pattern": "Name of pattern",
    "problem_statement": "Exact root problem",
    "solution_breakdown": "Technical implementation details",
    "system_invariants": ["Invariant 1", "Invariant 2"],
    "trade_offs": "Trade-offs incurred"
  }},
  "dimension_3_small_scale_client_playbook": {{
    "big_tech_overkill": "Why copying their massive setup is bad for a 5-50 person company",
    "small_scale_implementation": "How to implement 80% of this using Postgres, Redis, or simple workers",
    "estimated_cost_savings": "Monthly savings",
    "actionable_checklist": ["Step 1", "Step 2", "Step 3"]
  }},
  "dimension_4_ai_agents_codebase_evolution": {{
    "applicable_agents_or_skills": ["devops-sre", "database-architect"],
    "proposed_enhancement": "Concrete improvement to an ai-agents skill, rule, or script",
    "code_or_rule_proposal": "INV-XXX: Rule name and specification"
  }}
}}"""
        synthesis = eng_intel.query_ollama_generate(prompt)
        d1 = synthesis.get("dimension_1_linkedin", {})
        d2 = synthesis.get("dimension_2_engineering_learnings", {})
        d3 = synthesis.get("dimension_3_small_scale_client_playbook", {})
        d4 = synthesis.get("dimension_4_ai_agents_codebase_evolution", {})

        print(f"🔢 Generating vector embedding via local nomic-embed-text...")
        summary = f"{art['company']} {art['title']} - {d2.get('core_architectural_pattern')}. Problem: {d2.get('problem_statement')}. Solution: {d2.get('solution_breakdown')}. Small-scale: {d3.get('small_scale_implementation')}"
        emb = eng_intel.query_ollama_embedding(summary)

        with conn:
            conn.execute("""
            INSERT INTO processed_articles (
                article_hash, canonical_url, company, category, title, pub_date, clean_content, word_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (h, c_url, art['company'], art['category'], art['title'], datetime.now().isoformat(), art['content'], len(art['content'].split())))

            cur = conn.execute("""
            INSERT INTO engineering_learnings (
                article_hash, company, core_pattern, problem_statement, solution_breakdown,
                system_invariants, trade_offs, big_tech_overkill, small_scale_implementation,
                estimated_cost_savings, actionable_checklist, ai_agents_skill, ai_agents_rule,
                linkedin_hook_counterintuitive, linkedin_hook_story, linkedin_hook_practical,
                linkedin_post_body, linkedin_carousel_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h, art['company'],
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

            if emb:
                conn.execute("""
                INSERT INTO knowledge_embeddings (learning_id, chunk_type, chunk_text, embedding_json)
                VALUES (?, 'summary', ?, ?)
                """, (learning_id, summary, json.dumps(emb)))

        # Also write Markdown file in wiki/learnings/
        os.makedirs(eng_intel.WIKI_LEARNINGS_DIR, exist_ok=True)
        slug = f"{art['company'].lower()}-{art['title'].lower().replace(' ', '-')[:40]}"
        md_file = os.path.join(eng_intel.WIKI_LEARNINGS_DIR, f"{slug}.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"""# {art['company']}: {art['title']}

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
        print(f"  ✔ Saved & documented in wiki: {md_file}")

    conn.close()
    print("\n✅ Seeding complete!")

if __name__ == "__main__":
    main()
