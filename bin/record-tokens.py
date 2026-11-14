#!/usr/bin/env python3
"""
AI-Agents Token & Cost Accounting Engine
Tracks tokens processed locally ($0) vs. in the cloud, calculating cumulative cost savings.
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Reference pricing (blended Gemini Flash / Pro rates per million tokens)
# Input: $0.15/1M, Output: $0.60/1M -> average ~$0.35/1M ($0.00000035/token)
PRICE_PER_TOKEN_USD = 0.00000035

def get_ledger_paths():
    local_path = os.path.join(os.getcwd(), ".agents", "memory", "token_ledger.json")
    global_path = os.path.expanduser("~/.gemini/config/ai_agents_token_ledger.json")
    return local_path, global_path

def load_ledger(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "local_tokens": 0,
        "cloud_tokens": 0,
        "saved_usd": 0.0,
        "by_tool": {},
        "by_model": {},
        "events": []
    }

def save_ledger(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Cap event history to 500 entries to avoid bloat
        if len(data.get("events", [])) > 500:
            data["events"] = data["events"][-500:]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[token-recorder] Warning: could not write to {path}: {e}", file=sys.stderr)

def record_tokens(tool, model, prompt_tokens, eval_tokens, is_cloud=False):
    total = prompt_tokens + eval_tokens
    saved_usd = 0.0 if is_cloud else round(total * PRICE_PER_TOKEN_USD, 6)
    
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": tool,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "eval_tokens": eval_tokens,
        "total_tokens": total,
        "is_cloud": is_cloud,
        "saved_usd": saved_usd
    }

    local_path, global_path = get_ledger_paths()
    for path in [local_path, global_path]:
        ledger = load_ledger(path)
        if is_cloud:
            ledger["cloud_tokens"] = ledger.get("cloud_tokens", 0) + total
        else:
            ledger["local_tokens"] = ledger.get("local_tokens", 0) + total
            ledger["saved_usd"] = round(ledger.get("saved_usd", 0.0) + saved_usd, 6)

        # Breakdown by tool
        ledger.setdefault("by_tool", {})
        ledger["by_tool"][tool] = ledger["by_tool"].get(tool, 0) + total

        # Breakdown by model
        ledger.setdefault("by_model", {})
        ledger["by_model"][model] = ledger["by_model"].get(model, 0) + total

        ledger.setdefault("events", []).append(event)
        save_ledger(path, ledger)

def print_summary(scope="both"):
    local_path, global_path = get_ledger_paths()
    local_data = load_ledger(local_path)
    global_data = load_ledger(global_path)

    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BOLD = "\033[1m"
    NC = "\033[0m"

    print(f"{CYAN}================================================================{NC}")
    print(f"{CYAN}{BOLD}   ANTIGRAVITY AI-AGENTS TOKEN & SAVINGS OBSERVER               {NC}")
    print(f"{CYAN}================================================================{NC}")

    def render_section(title, data):
        loc = data.get("local_tokens", 0)
        cld = data.get("cloud_tokens", 0)
        tot = loc + cld
        usd = data.get("saved_usd", 0.0)
        ratio = (loc / tot * 100) if tot > 0 else 0.0

        print(f"{BOLD}{title}:{NC}")
        print(f"  • {GREEN}Local LLM Processed ($0 Tokens){NC} : {BOLD}{loc:,}{NC} tokens ({ratio:.1f}% offloaded)")
        print(f"  • {YELLOW}Cloud LLM Tokens Used (Paid){NC}    : {BOLD}{cld:,}{NC} tokens")
        print(f"  • Total Tokens Processed         : {tot:,} tokens")
        print(f"  • {GREEN}Estimated Cost Saved{NC}            : {GREEN}{BOLD}${usd:,.4f} USD{NC}")

        by_tool = data.get("by_tool", {})
        if by_tool:
            print(f"  • Breakdown by Tool:")
            for t, count in sorted(by_tool.items(), key=lambda x: x[1], reverse=True):
                pct = (count / loc * 100) if loc > 0 else 0.0
                print(f"    - {t:<15}: {count:,} tokens ({pct:.1f}%)")

        by_model = data.get("by_model", {})
        if by_model:
            print(f"  • Breakdown by Model:")
            for m, count in sorted(by_model.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {m:<20}: {count:,} tokens")
        print()

    if scope in ("local", "both"):
        render_section("CURRENT PROJECT STATS (.agents/memory/token_ledger.json)", local_data)
    if scope in ("global", "both"):
        render_section("GLOBAL LIFETIME STATS (~/.gemini/config/ai_agents_token_ledger.json)", global_data)

    print(f"{CYAN}================================================================{NC}")

def main():
    parser = argparse.ArgumentParser(description="AI-Agents Token Recorder & Reporter")
    parser.add_argument("--record", action="store_true", help="Record token usage")
    parser.add_argument("--tool", default="generic", help="Tool name (local-coder, local-git, local-cmd)")
    parser.add_argument("--model", default="unknown", help="Model name (e.g. qwen2.5-coder:14b)")
    parser.add_argument("--prompt-tokens", type=int, default=0, help="Prompt token count")
    parser.add_argument("--eval-tokens", type=int, default=0, help="Eval/completion token count")
    parser.add_argument("--cloud", action="store_true", help="Mark as cloud usage")
    parser.add_argument("--summary", action="store_true", help="Print summary report")
    parser.add_argument("--scope", default="both", choices=["local", "global", "both"], help="Summary scope")
    parser.add_argument("--json", action="store_true", help="Output summary as JSON")

    args = parser.parse_args()

    if args.record:
        record_tokens(args.tool, args.model, args.prompt_tokens, args.eval_tokens, is_cloud=args.cloud)
    elif args.json:
        local_path, global_path = get_ledger_paths()
        res = {
            "local": load_ledger(local_path),
            "global": load_ledger(global_path)
        }
        print(json.dumps(res, indent=2))
    elif args.summary or len(sys.argv) == 1:
        print_summary(args.scope)

if __name__ == "__main__":
    main()
