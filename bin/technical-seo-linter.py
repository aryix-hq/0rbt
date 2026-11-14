#!/usr/bin/env python3
"""
bin/technical-seo-linter.py - Technical SEO & Heading Hierarchy Linter

Lints HTML documents for sequential heading hierarchy (no level skips),
single primary H1, canonical tags, OpenGraph protocols, and meta description bounds.

Zero-token execution: 100% Python standard library.

Usage:
  python3 bin/technical-seo-linter.py --file dist/index.html
  python3 bin/technical-seo-linter.py --dir public/
  python3 bin/technical-seo-linter.py --mock-test
"""

import os
import re
import sys
import argparse
from pathlib import Path

VERSION = "1.0.0"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Regex patterns for HTML head and headings
HEADING_REGEX = re.compile(r'<(h[1-6])(?:\s+[^>]*)?>(.*?)</\1>', re.IGNORECASE | re.DOTALL)
META_DESC_REGEX = re.compile(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', re.IGNORECASE)
META_DESC_REVERSE = re.compile(r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', re.IGNORECASE)
CANONICAL_REGEX = re.compile(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', re.IGNORECASE)
CANONICAL_REVERSE = re.compile(r'<link\s+[^>]*href=["\']([^"\']*)["\'][^>]*rel=["\']canonical["\']', re.IGNORECASE)
OG_TAG_REGEX = re.compile(r'<meta\s+[^>]*property=["\']og:([a-zA-Z0-9_\-]+)["\'][^>]*content=["\']([^"\']*)["\']', re.IGNORECASE)
OG_TAG_REVERSE = re.compile(r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:([a-zA-Z0-9_\-]+)["\']', re.IGNORECASE)
VIEWPORT_REGEX = re.compile(r'<meta\s+[^>]*name=["\']viewport["\']', re.IGNORECASE)


def lint_heading_hierarchy(html_content: str) -> list:
    """Validates heading hierarchy: single H1, and no level skips (e.g. H1 -> H3)."""
    findings = []
    matches = list(HEADING_REGEX.finditer(html_content))

    if not matches:
        return [{"id": "SEO-ZERO-HEADINGS", "line": 1, "message": "HTML document contains zero heading tags (h1-h6)", "severity": "BLOCKER"}]

    h1_count = 0
    prev_level = 0

    for m in matches:
        tag = m.group(1).lower()
        level = int(tag[1])
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        line_num = html_content[:m.start()].count("\n") + 1

        if level == 1:
            h1_count += 1
            if h1_count > 1:
                findings.append({
                    "id": "SEO-MULTIPLE-H1",
                    "line": line_num,
                    "message": f"Multiple <h1> tags detected on page (found '{text[:40]}'). Must have exactly one <h1>.",
                    "severity": "BLOCKER"
                })

        # Check level sequence: increasing level can increment by at most 1 (e.g. 1 -> 2, or 2 -> 3)
        if prev_level > 0 and level > prev_level + 1:
            findings.append({
                "id": "SEO-HEADING-SKIP",
                "line": line_num,
                "message": f"Heading level skipped from <h{prev_level}> directly to <h{level}> ('{text[:40]}'). Progression must be sequential.",
                "severity": "BLOCKER"
            })

        prev_level = level

    if h1_count == 0:
        findings.append({
            "id": "SEO-MISSING-H1",
            "line": 1,
            "message": "HTML document is missing primary <h1> tag",
            "severity": "BLOCKER"
        })

    return findings


def lint_metadata(html_content: str) -> list:
    """Validates meta description, canonical, viewport, and OpenGraph tags."""
    findings = []

    # 1. Viewport tag
    if not VIEWPORT_REGEX.search(html_content):
        findings.append({
            "id": "SEO-MISSING-VIEWPORT",
            "line": 1,
            "message": "Missing mobile viewport configuration tag (<meta name='viewport'>)",
            "severity": "WARNING"
        })

    # 2. Meta description
    desc_match = META_DESC_REGEX.search(html_content) or META_DESC_REVERSE.search(html_content)
    if not desc_match:
        findings.append({
            "id": "SEO-MISSING-META-DESC",
            "line": 1,
            "message": "Missing <meta name='description'> tag",
            "severity": "WARNING"
        })
    else:
        desc_text = desc_match.group(1).strip()
        length = len(desc_text)
        if length < 50:
            findings.append({
                "id": "SEO-META-DESC-TOO-SHORT",
                "line": 1,
                "message": f"Meta description is too short ({length} characters). Recommended: 50–160 chars.",
                "severity": "WARNING"
            })
        elif length > 160:
            findings.append({
                "id": "SEO-META-DESC-TOO-LONG",
                "line": 1,
                "message": f"Meta description exceeds optimal length ({length} characters). May truncate in SERPs.",
                "severity": "WARNING"
            })

    # 3. Canonical tag
    canon_match = CANONICAL_REGEX.search(html_content) or CANONICAL_REVERSE.search(html_content)
    if not canon_match or not canon_match.group(1).strip():
        findings.append({
            "id": "SEO-MISSING-CANONICAL",
            "line": 1,
            "message": "Missing canonical URL tag (<link rel='canonical' href='...'>)",
            "severity": "BLOCKER"
        })

    # 4. OpenGraph tags
    og_tags = set()
    for m in OG_TAG_REGEX.finditer(html_content):
        og_tags.add(m.group(1).lower())
    for m in OG_TAG_REVERSE.finditer(html_content):
        og_tags.add(m.group(2).lower())

    required_og = ["title", "description", "image", "url"]
    for tag in required_og:
        if tag not in og_tags:
            findings.append({
                "id": "SEO-MISSING-OG-TAG",
                "line": 1,
                "message": f"Missing OpenGraph tag 'og:{tag}' (<meta property='og:{tag}' content='...'>)",
                "severity": "WARNING"
            })

    return findings


def lint_html_document(html_content: str, file_path: str = "") -> dict:
    """Runs all technical SEO and heading hierarchy checks on an HTML document."""
    heading_findings = lint_heading_hierarchy(html_content)
    meta_findings = lint_metadata(html_content)
    all_findings = heading_findings + meta_findings

    blockers = [f for f in all_findings if f["severity"] == "BLOCKER"]
    warnings = [f for f in all_findings if f["severity"] == "WARNING"]

    status = "FAIL" if blockers else ("WARN" if warnings else "PASS")
    return {
        "file": file_path,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "total_issues": len(all_findings)
    }


def scan_file(file_path: str) -> dict:
    """Reads and lints an HTML file from disk."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return {"file": file_path, "status": "FAIL", "blockers": [{"id": "NOT-FOUND", "message": "File not found"}], "warnings": []}

    try:
        content = p.read_text(encoding="utf-8")
        return lint_html_document(content, file_path)
    except Exception as e:
        return {"file": file_path, "status": "FAIL", "blockers": [{"id": "READ-ERR", "message": str(e)}], "warnings": []}


def scan_directory(root_dir: str) -> dict:
    """Scans all HTML files in a directory."""
    results = []
    root = Path(root_dir)

    for p in root.glob("**/*.html"):
        if any(d in p.parts for d in ["node_modules", ".git", "venv", ".venv", "dist/vendor"]):
            continue
        results.append(scan_file(str(p)))

    failed = [r for r in results if r["status"] == "FAIL"]
    passed = [r for r in results if r["status"] == "PASS"]
    warned = [r for r in results if r["status"] == "WARN"]

    return {
        "total_files": len(results),
        "passed": len(passed),
        "warned": len(warned),
        "failed": len(failed),
        "status": "FAIL" if failed else "PASS",
        "results": results
    }


def run_mock_test() -> int:
    """Deterministic self-test completing in <0.05s."""
    print("[TEST] Verifying Technical SEO & Heading Linter (INV-SEO-02)...")

    # 1. Perfectly compliant HTML
    clean_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aryix Systems - Cloud Orchestration Platform</title>
<meta name="description" content="Aryix Systems delivers autonomous AI agent orchestration, real-time distributed telemetry, and zero-token local inference engines.">
<link rel="canonical" href="https://aryix.example.com/platform">
<meta property="og:title" content="Aryix Systems - Cloud Orchestration">
<meta property="og:description" content="Autonomous AI agent orchestration and zero-token local inference engines.">
<meta property="og:image" content="https://aryix.example.com/og.png">
<meta property="og:url" content="https://aryix.example.com/platform">
</head>
<body>
<h1>Aryix Systems Cloud Platform</h1>
<h2>Core Architecture</h2>
<p>High-level system topology and stateless compute tiers.</p>
<h3>Database Layer</h3>
<p>PostgreSQL relational persistence with row-level security.</p>
<h2>Deployment Strategy</h2>
<p>Ephemeral staging environments destroyed immediately after test attestation.</p>
</body>
</html>
"""
    res = lint_html_document(clean_html, "test_clean.html")
    if res["status"] != "PASS":
        print(f"[FAIL] False positive on compliant HTML: {res}", file=sys.stderr)
        return 1

    # 2. Heading skip: H1 -> H3
    skip_html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Valid meta description between 50 and 160 characters long for testing.">
<link rel="canonical" href="https://aryix.example.com">
<meta property="og:title" content="T"><meta property="og:description" content="D"><meta property="og:image" content="I"><meta property="og:url" content="U">
</head>
<body>
<h1>Main Header</h1>
<h3>Skipped Subheader Directly to H3</h3>
</body>
</html>
"""
    res_skip = lint_html_document(skip_html, "test_skip.html")
    if not any(b["id"] == "SEO-HEADING-SKIP" for b in res_skip["blockers"]):
        print(f"[FAIL] Failed to catch heading skip from H1 to H3: {res_skip}", file=sys.stderr)
        return 1

    # 3. Missing canonical tag
    no_canon = "<html><body><h1>Title</h1><h2>Subtitle</h2></body></html>"
    res_canon = lint_html_document(no_canon, "test_no_canon.html")
    if not any(b["id"] == "SEO-MISSING-CANONICAL" for b in res_canon["blockers"]):
        print(f"[FAIL] Failed to catch missing canonical tag: {res_canon}", file=sys.stderr)
        return 1

    print("[PASS] Technical SEO & Heading Linter verified cleanly in <0.05s (INV-SEO-02).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=f"Technical SEO & Heading Hierarchy Linter v{VERSION}")
    parser.add_argument("--file", help="Path to single HTML file to lint")
    parser.add_argument("--dir", help="Directory of HTML files to lint recursively")
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic self-test")
    parser.add_argument("--version", action="version", version=f"technical-seo-linter.py v{VERSION}")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    if args.file:
        res = scan_file(args.file)
        if res["status"] == "FAIL":
            print(f"\n❌ Technical SEO audit FAILED for {args.file}:")
            for b in res["blockers"]:
                print(f"  ⛔ Line {b.get('line', '?')}: [{b.get('id', 'ERR')}] {b.get('message')}")
            for w in res["warnings"]:
                print(f"  ⚠ Line {w.get('line', '?')}: [{w.get('id', 'WARN')}] {w.get('message')}")
            sys.exit(1)
        elif res["status"] == "WARN":
            print(f"\n⚠ Technical SEO audit passed with warnings for {args.file}:")
            for w in res["warnings"]:
                print(f"  ⚠ Line {w.get('line', '?')}: [{w.get('id', 'WARN')}] {w.get('message')}")
            sys.exit(0)
        else:
            print(f"✅ {args.file}: Technical SEO and heading hierarchy verified clean.")
            sys.exit(0)

    if args.dir:
        res = scan_directory(args.dir)
        print(f"\nTechnical SEO Audit Summary for {args.dir}:")
        print(f"  • Total HTML Files Scanned: {res['total_files']}")
        print(f"  • Passing: {res['passed']}")
        print(f"  • Warnings: {res['warned']}")
        print(f"  • Failing: {res['failed']}")
        if res["failed"] > 0:
            for r in res["results"]:
                if r["status"] == "FAIL":
                    print(f"\n  [FAIL] {r['file']}:")
                    for b in r["blockers"]:
                        print(f"    ⛔ Line {b.get('line', '?')}: {b.get('message')}")
            sys.exit(1)
        sys.exit(0)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
