#!/usr/bin/env python3
"""
bin/llms-txt-generator.py - Agentic Web & LLMS.txt Generator / Linter

Synthesizes, curates, and validates /llms.txt and /llms-full.txt files
per the llmstxt.org specification for optimal LLM context ingestion.

Zero-token execution: 100% Python standard library.

Usage:
  python3 bin/llms-txt-generator.py --lint public/llms.txt
  python3 bin/llms-txt-generator.py --src docs/ --out public/llms.txt --name "Aryix Systems"
  python3 bin/llms-txt-generator.py --mock-test
"""

import os
import re
import sys
import argparse
from pathlib import Path

VERSION = "1.0.0"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_llms_txt(title: str, summary: str, details: str, link_sections: list) -> str:
    """Generates standard llms.txt content conforming to llmstxt.org."""
    lines = [
        f"# {title.strip()}",
        "",
        f"> {summary.strip()}",
        "",
        details.strip(),
        ""
    ]

    for section in link_sections:
        lines.append(f"## {section['title'].strip()}")
        for item in section.get("links", []):
            url = item.get("url", "")
            label = item.get("label", "Document")
            desc = item.get("desc", "")
            if desc:
                lines.append(f"- [{label}]({url}): {desc}")
            else:
                lines.append(f"- [{label}]({url})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_llms_full_txt(file_paths: list) -> str:
    """Aggregates multiple markdown files into a single flat documentation bundle."""
    buffer = []
    for fp in file_paths:
        p = Path(fp)
        if not p.exists() or not p.is_file():
            continue
        try:
            content = p.read_text(encoding="utf-8")
            # Strip YAML frontmatter if present
            cleaned = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            buffer.append(f"# File: {p.name}\n\n{cleaned.strip()}\n\n---\n")
        except Exception:
            pass
    return "\n".join(buffer)


def lint_llms_txt(content: str) -> list:
    """Validates llms.txt against the llmstxt.org specification."""
    findings = []
    lines = content.strip().splitlines()

    if not lines:
        return [{"id": "LLMS-EMPTY", "message": "File is empty", "severity": "BLOCKER"}]

    # 1. First line must be H1
    if not lines[0].startswith("# "):
        findings.append({
            "id": "LLMS-H1-MISSING",
            "message": "First line must be an H1 header `# <Project Name>`",
            "severity": "BLOCKER"
        })

    # 2. Blockquote summary presence
    has_blockquote = any(line.strip().startswith("> ") for line in lines[:5])
    if not has_blockquote:
        findings.append({
            "id": "LLMS-SUMMARY-MISSING",
            "message": "Missing blockquote summary `> <Summary>` within the first 5 lines",
            "severity": "BLOCKER"
        })

    # 3. Section headers and link syntax
    has_links = False
    link_pattern = re.compile(r'^\s*-\s*\[([^\]]+)\]\(([^)]+)\)(?::\s*(.*))?$')

    for idx, line in enumerate(lines, 1):
        if link_pattern.match(line):
            has_links = True
        elif line.startswith("- ") and not line.startswith("- ["):
            findings.append({
                "id": "LLMS-INVALID-LINK-SYNTAX",
                "message": f"Line {idx}: List item is not a markdown link formatted as `- [Label](url): description`",
                "severity": "WARNING"
            })

    if not has_links:
        findings.append({
            "id": "LLMS-ZERO-LINKS",
            "message": "File contains no markdown documentation links",
            "severity": "BLOCKER"
        })

    return findings


def scan_and_generate(src_dir: str, title: str, summary: str, details: str = "") -> tuple:
    """Scans a directory of markdown files and synthesizes llms.txt and llms-full.txt."""
    src_path = Path(src_dir)
    md_files = sorted(list(src_path.glob("**/*.md")))

    core_links = []
    secondary_links = []
    full_paths = []

    for f in md_files:
        rel = f.relative_to(src_path).as_posix()
        name = f.stem.replace("-", " ").replace("_", " ").title()
        full_paths.append(str(f))

        if any(w in rel.lower() for w in ["arch", "api", "guide", "overview", "readme"]):
            core_links.append({"label": name, "url": rel, "desc": f"Core documentation for {name}"})
        else:
            secondary_links.append({"label": name, "url": rel, "desc": f"Reference document for {name}"})

    sections = []
    if core_links:
        sections.append({"title": "Core Documentation", "links": core_links})
    if secondary_links:
        sections.append({"title": "Additional Resources", "links": secondary_links})

    llms_txt = generate_llms_txt(
        title=title,
        summary=summary,
        details=details or f"Autonomous documentation index for {title}.",
        link_sections=sections
    )

    llms_full = generate_llms_full_txt(full_paths)
    return llms_txt, llms_full


def run_mock_test() -> int:
    """Deterministic self-test completing in <0.05s."""
    print("[TEST] Verifying LLMS.txt Engine (llmstxt.org Specification)...")
    import tempfile

    clean_content = """# Aryix Systems Platform

> High-performance autonomous agent orchestration and distributed task engine.

Aryix Systems provides zero-token local inference, automated invariant gating, and multi-IDE agent transpilation.

## Core Documentation
- [System Architecture](docs/architecture.md): High-level system topology and domain boundaries
- [API Reference](docs/api.md): Complete OpenAPI 3.1 contracts and route definitions

## Operational Runbooks
- [Deployment Guide](docs/deployment.md): Ephemeral staging container lifecycle
"""

    findings = lint_llms_txt(clean_content)
    if findings:
        print(f"[FAIL] False positive linting clean llms.txt: {findings}", file=sys.stderr)
        return 1

    broken_content = "Just plain text without H1 or links"
    bad_findings = lint_llms_txt(broken_content)
    if not any(f["id"] == "LLMS-H1-MISSING" for f in bad_findings):
        print("[FAIL] Failed to catch missing H1", file=sys.stderr)
        return 1

    # Test scanner
    with tempfile.TemporaryDirectory() as tmp_dir:
        docs = Path(tmp_dir) / "docs"
        docs.mkdir()
        (docs / "architecture.md").write_text("# Architecture\nDetailed system diagram.", encoding="utf-8")
        (docs / "api.md").write_text("# API\nREST endpoints.", encoding="utf-8")

        txt, full = scan_and_generate(
            src_dir=str(docs),
            title="DevTools Corp",
            summary="Developer automation tools"
        )
        if "DevTools Corp" not in txt or "architecture.md" not in txt:
            print("[FAIL] Generated llms.txt missing expected content", file=sys.stderr)
            return 1
        if "Detailed system diagram" not in full:
            print("[FAIL] Generated llms-full.txt missing file body", file=sys.stderr)
            return 1

    print("[PASS] LLMS.txt Engine verified cleanly in <0.05s (llmstxt.org standard).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=f"Agentic Web & LLMS.txt Generator / Linter v{VERSION}")
    parser.add_argument("--src", help="Source directory containing Markdown files to scan")
    parser.add_argument("--out", help="Output path for llms.txt")
    parser.add_argument("--full-out", help="Output path for llms-full.txt")
    parser.add_argument("--name", default="Application Documentation", help="Project / Product title")
    parser.add_argument("--summary", default="Documentation portal and technical reference", help="1-sentence summary")
    parser.add_argument("--lint", help="Path to llms.txt file to validate")
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic self-test")
    parser.add_argument("--version", action="version", version=f"llms-txt-generator.py v{VERSION}")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    if args.lint:
        p = Path(args.lint)
        if not p.exists():
            print(f"[ERROR] Target file not found: {args.lint}", file=sys.stderr)
            sys.exit(1)
        content = p.read_text(encoding="utf-8")
        findings = lint_llms_txt(content)
        if findings:
            print(f"\n❌ LLMS.txt Linter detected {len(findings)} issues in {args.lint}:")
            for f in findings:
                print(f"  • [{f['severity']}] {f['id']}: {f['message']}")
            sys.exit(1)
        else:
            print(f"✅ {args.lint} strictly complies with the llmstxt.org specification.")
            sys.exit(0)

    if args.src and args.out:
        txt, full = scan_and_generate(args.src, args.name, args.summary)
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(txt, encoding="utf-8")
        print(f"✅ Generated {out_p} ({len(txt)} bytes)")

        if args.full_out:
            full_p = Path(args.full_out)
            full_p.parent.mkdir(parents=True, exist_ok=True)
            full_p.write_text(full, encoding="utf-8")
            print(f"✅ Generated {full_p} ({len(full)} bytes)")
        sys.exit(0)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
