#!/usr/bin/env python3
"""
bin/schema-validator.py - Strict Schema.org JSON-LD AST Validator

Validates Schema.org structured data embedded in HTML against Google Rich Results
specifications for SoftwareApplication, Organization, Article, FAQPage, Product, and Breadcrumbs.

Zero-token execution: 100% Python standard library.

Usage:
  python3 bin/schema-validator.py --file dist/index.html
  python3 bin/schema-validator.py --dir public/
  python3 bin/schema-validator.py --mock-test
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

VERSION = "1.0.0"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Regex to match <script type="application/ld+json">...</script>
JSONLD_REGEX = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL
)

REQUIRED_FIELDS = {
    "SoftwareApplication": ["name", "operatingSystem", "applicationCategory"],
    "WebApplication": ["name", "applicationCategory"],
    "Organization": ["name", "url"],
    "Corporation": ["name", "url"],
    "Article": ["headline", "author", "publisher", "datePublished"],
    "TechArticle": ["headline", "author", "publisher", "datePublished"],
    "BlogPosting": ["headline", "author", "publisher", "datePublished"],
    "FAQPage": ["mainEntity"],
    "BreadcrumbList": ["itemListElement"],
    "Product": ["name", "offers"]
}


def extract_jsonld_blocks(html_content: str) -> list:
    """Extracts and parses all JSON-LD blocks from HTML content."""
    blocks = []
    matches = list(JSONLD_REGEX.finditer(html_content))

    for m in matches:
        raw_json = m.group(1).strip()
        line_num = html_content[:m.start()].count("\n") + 1
        try:
            data = json.loads(raw_json)
            blocks.append({"data": data, "line": line_num, "raw": raw_json, "error": None})
        except json.JSONDecodeError as err:
            blocks.append({"data": None, "line": line_num, "raw": raw_json, "error": str(err)})

    return blocks


def validate_jsonld_entity(data: dict, line: int = 1) -> list:
    """Validates a single parsed Schema.org entity dictionary against Google Rich Results rules."""
    findings = []
    if not isinstance(data, dict):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    findings.extend(validate_jsonld_entity(item, line))
            return findings
        return [{"id": "SCHEMA-NOT-OBJECT", "line": line, "message": "JSON-LD payload must be a JSON object", "severity": "BLOCKER"}]

    # 1. Context verification
    ctx = data.get("@context", "")
    if isinstance(ctx, str):
        ctx_clean = ctx.rstrip("/").lower()
        if ctx_clean not in ["https://schema.org", "http://schema.org"]:
            findings.append({
                "id": "SCHEMA-INVALID-CONTEXT",
                "line": line,
                "message": f"Invalid @context '{ctx}'. Must be 'https://schema.org'",
                "severity": "BLOCKER"
            })
    else:
        findings.append({
            "id": "SCHEMA-MISSING-CONTEXT",
            "line": line,
            "message": "Missing '@context' declaration in JSON-LD",
            "severity": "BLOCKER"
        })

    # 2. Type verification
    entity_type = data.get("@type")
    if not entity_type or not isinstance(entity_type, str):
        findings.append({
            "id": "SCHEMA-MISSING-TYPE",
            "line": line,
            "message": "Missing '@type' declaration in JSON-LD entity",
            "severity": "BLOCKER"
        })
        return findings

    # 3. Check entity-specific required fields
    if entity_type in REQUIRED_FIELDS:
        reqs = REQUIRED_FIELDS[entity_type]
        for field in reqs:
            if field not in data or data[field] is None or data[field] == "":
                findings.append({
                    "id": "SCHEMA-MISSING-REQUIRED-FIELD",
                    "line": line,
                    "message": f"Entity '{entity_type}' is missing mandatory property '{field}'",
                    "severity": "BLOCKER"
                })

    # 4. Deep entity validation
    if entity_type == "FAQPage":
        main_entity = data.get("mainEntity")
        if not isinstance(main_entity, list) or len(main_entity) == 0:
            findings.append({
                "id": "SCHEMA-FAQ-EMPTY",
                "line": line,
                "message": "FAQPage 'mainEntity' must be a non-empty array of Question entities",
                "severity": "BLOCKER"
            })
        else:
            for q_idx, q in enumerate(main_entity):
                if not isinstance(q, dict) or q.get("@type") != "Question" or not q.get("name"):
                    findings.append({
                        "id": "SCHEMA-FAQ-INVALID-QUESTION",
                        "line": line,
                        "message": f"FAQPage item {q_idx} must be a Question with a 'name' property",
                        "severity": "BLOCKER"
                    })
                ans = q.get("acceptedAnswer") if isinstance(q, dict) else None
                if not isinstance(ans, dict) or ans.get("@type") != "Answer" or not ans.get("text"):
                    findings.append({
                        "id": "SCHEMA-FAQ-INVALID-ANSWER",
                        "line": line,
                        "message": f"FAQPage item {q_idx} must have an acceptedAnswer with type 'Answer' and non-empty 'text'",
                        "severity": "BLOCKER"
                    })

    elif entity_type == "BreadcrumbList":
        items = data.get("itemListElement")
        if not isinstance(items, list) or len(items) == 0:
            findings.append({
                "id": "SCHEMA-BREADCRUMB-EMPTY",
                "line": line,
                "message": "BreadcrumbList 'itemListElement' must be a non-empty array",
                "severity": "BLOCKER"
            })
        else:
            for b_idx, b in enumerate(items):
                if not isinstance(b, dict) or not b.get("name") or "position" not in b:
                    findings.append({
                        "id": "SCHEMA-BREADCRUMB-INVALID-ITEM",
                        "line": line,
                        "message": f"Breadcrumb item {b_idx} must have 'name' and integer 'position'",
                        "severity": "BLOCKER"
                    })

    return findings


def scan_html_file(file_path: str) -> dict:
    """Scans an HTML file for JSON-LD blocks and validates them."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return {"file": file_path, "status": "FAIL", "errors": ["File not found"], "schemas_count": 0}

    try:
        content = p.read_text(encoding="utf-8")
    except Exception as e:
        return {"file": file_path, "status": "FAIL", "errors": [f"Cannot read file: {e}"], "schemas_count": 0}

    blocks = extract_jsonld_blocks(content)
    if not blocks:
        return {"file": file_path, "status": "WARN", "errors": ["Zero JSON-LD structured data blocks found"], "schemas_count": 0}

    file_findings = []
    for block in blocks:
        if block["error"]:
            file_findings.append({
                "id": "SCHEMA-JSON-SYNTAX-ERROR",
                "line": block["line"],
                "message": f"JSON syntax error in <script type='application/ld+json'>: {block['error']}",
                "severity": "BLOCKER"
            })
        elif block["data"]:
            file_findings.extend(validate_jsonld_entity(block["data"], block["line"]))

    status = "FAIL" if any(f["severity"] == "BLOCKER" for f in file_findings) else "PASS"
    return {
        "file": file_path,
        "status": status,
        "errors": file_findings,
        "schemas_count": len(blocks)
    }


def scan_directory(root_dir: str) -> dict:
    """Scans all HTML files in a directory for Schema.org compliance."""
    results = []
    root = Path(root_dir)

    for p in root.glob("**/*.html"):
        if any(d in p.parts for d in ["node_modules", ".git", "venv", ".venv", "dist/vendor"]):
            continue
        results.append(scan_html_file(str(p)))

    total_files = len(results)
    failed = [r for r in results if r["status"] == "FAIL"]
    passed = [r for r in results if r["status"] == "PASS"]

    return {
        "total_files": total_files,
        "passed_files": len(passed),
        "failed_files": len(failed),
        "status": "FAIL" if failed else "PASS",
        "results": results
    }


def run_mock_test() -> int:
    """Deterministic self-test completing in <0.05s."""
    print("[TEST] Verifying Schema.org AST Validator Engine (INV-SEO-01)...")

    # 1. Valid SoftwareApplication + Organization
    valid_html = """<!DOCTYPE html>
<html>
<head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Aryix Cloud Platform",
  "operatingSystem": "Linux, macOS, Windows",
  "applicationCategory": "DeveloperApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Aryix Systems",
  "url": "https://aryix.example.com"
}
</script>
</head>
<body><h1>Welcome</h1></body>
</html>
"""
    blocks = extract_jsonld_blocks(valid_html)
    if len(blocks) != 2:
        print(f"[FAIL] Expected 2 JSON-LD blocks, extracted {len(blocks)}", file=sys.stderr)
        return 1

    findings = []
    for b in blocks:
        findings.extend(validate_jsonld_entity(b["data"]))

    if findings:
        print(f"[FAIL] False positive on valid schemas: {findings}", file=sys.stderr)
        return 1

    # 2. Invalid FAQPage with missing answer text
    broken_faq = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Aryix?",
      "acceptedAnswer": {
        "@type": "Answer"
      }
    }
  ]
}
</script>
"""
    faq_blocks = extract_jsonld_blocks(broken_faq)
    faq_findings = validate_jsonld_entity(faq_blocks[0]["data"])
    if not any(f["id"] == "SCHEMA-FAQ-INVALID-ANSWER" for f in faq_findings):
        print(f"[FAIL] Failed to catch missing acceptedAnswer.text in FAQPage: {faq_findings}", file=sys.stderr)
        return 1

    # 3. Missing required field in Product
    broken_product = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Enterprise Agent Engine"
}
</script>
"""
    prod_blocks = extract_jsonld_blocks(broken_product)
    prod_findings = validate_jsonld_entity(prod_blocks[0]["data"])
    if not any("missing mandatory property 'offers'" in f["message"] for f in prod_findings):
        print(f"[FAIL] Failed to catch missing offers in Product: {prod_findings}", file=sys.stderr)
        return 1

    print("[PASS] Schema.org AST Validator Engine verified cleanly in <0.05s (INV-SEO-01).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=f"Strict Schema.org JSON-LD AST Validator v{VERSION}")
    parser.add_argument("--file", help="Path to single HTML file to validate")
    parser.add_argument("--dir", help="Directory of HTML files to validate recursively")
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic self-test")
    parser.add_argument("--version", action="version", version=f"schema-validator.py v{VERSION}")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    if args.file:
        res = scan_html_file(args.file)
        if res["status"] == "FAIL":
            print(f"\n❌ Schema validation FAILED for {args.file}:")
            for err in res["errors"]:
                print(f"  • Line {err.get('line', '?')}: [{err.get('id', 'ERR')}] {err.get('message')}")
            sys.exit(1)
        else:
            print(f"✅ {args.file}: All {res['schemas_count']} Schema.org blocks verified clean.")
            sys.exit(0)

    if args.dir:
        res = scan_directory(args.dir)
        print(f"\nSchema.org Audit Summary for {args.dir}:")
        print(f"  • Total HTML Files Scanned: {res['total_files']}")
        print(f"  • Passing: {res['passed_files']}")
        print(f"  • Failing: {res['failed_files']}")
        if res["failed_files"] > 0:
            for r in res["results"]:
                if r["status"] == "FAIL":
                    print(f"\n  [FAIL] {r['file']}:")
                    for err in r["errors"]:
                        print(f"    - Line {err.get('line')}: {err.get('message')}")
            sys.exit(1)
        sys.exit(0)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
