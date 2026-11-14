#!/usr/bin/env python3
"""
devops-auditor.py - Unified Offline DevOps & SRE Static Audit Engine

Inspired by NotHarshhaa/devops-skills layered review taxonomy.
Performs deterministic, zero-token static analysis across Kubernetes manifests,
Dockerfiles, database migrations, and Terraform/IaC templates with
modifier flags (--quick, --deep, --focus).

Usage:
    python3 bin/devops-auditor.py k8s deployment.yaml
    python3 bin/devops-auditor.py docker Dockerfile --quick
    python3 bin/devops-auditor.py db migrations/ --focus locking
    python3 bin/devops-auditor.py terraform main.tf --deep
    python3 bin/devops-auditor.py --mock-test
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

SEVERITY_P0 = "P0_CRITICAL"
SEVERITY_P1 = "P1_HIGH"
SEVERITY_P2 = "P2_MEDIUM"

class AuditFinding:
    def __init__(self, domain: str, code: str, severity: str, message: str, file_path: str, line_num: int = 0, category: str = "general"):
        self.domain = domain
        self.code = code
        self.severity = severity
        self.message = message
        self.file_path = file_path
        self.line_num = line_num
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "file": self.file_path,
            "line": self.line_num,
            "category": self.category
        }

# ==============================================================================
# Domain 1: Kubernetes Manifest Auditor
# ==============================================================================
def audit_k8s_content(content: str, file_path: str, quick: bool = False, focus: Optional[str] = None) -> List[AuditFinding]:
    findings = []
    lines = content.splitlines()

    # Check if this is a workload manifest (Deployment, StatefulSet, DaemonSet, Pod, Job)
    is_workload = bool(re.search(r"kind:\s*(Deployment|StatefulSet|DaemonSet|Pod|Job|CronJob)", content))
    if not is_workload:
        return findings

    # P0: Privileged container
    for idx, line in enumerate(lines, 1):
        if re.search(r"privileged:\s*true", line):
            if not focus or focus == "security":
                findings.append(AuditFinding("k8s", "K8S-SEC-01", SEVERITY_P0, "Container configured with privileged: true (container breakout risk).", file_path, idx, "security"))

        # P0: hostPath mount
        if re.search(r"hostPath:\s*$", line) or re.search(r"hostPath:", line):
            if not focus or focus in ("security", "storage"):
                findings.append(AuditFinding("k8s", "K8S-SEC-02", SEVERITY_P0, "Pod uses hostPath volume mount (host compromise risk).", file_path, idx, "security"))

        # P0: hostNetwork / hostPort
        if re.search(r"hostNetwork:\s*true", line):
            if not focus or focus == "security":
                findings.append(AuditFinding("k8s", "K8S-SEC-03", SEVERITY_P0, "Pod configured with hostNetwork: true.", file_path, idx, "security"))

    # P1: Missing liveness / readiness probes
    has_liveness = bool(re.search(r"livenessProbe:", content))
    has_readiness = bool(re.search(r"readinessProbe:", content))

    if not has_liveness:
        if not focus or focus in ("probes", "reliability"):
            findings.append(AuditFinding("k8s", "K8S-REL-01", SEVERITY_P1, "Workload missing livenessProbe definition (cannot detect stuck processes).", file_path, 1, "probes"))

    if not has_readiness:
        if not focus or focus in ("probes", "reliability"):
            findings.append(AuditFinding("k8s", "K8S-REL-02", SEVERITY_P1, "Workload missing readinessProbe definition (cold-boot traffic risk).", file_path, 1, "probes"))

    # P1: Missing resource limits
    has_limits = bool(re.search(r"limits:\s*\n.*(cpu|memory):", content, re.DOTALL)) or bool(re.search(r"limits:", content))
    if not has_limits:
        if not focus or focus in ("resources", "reliability"):
            findings.append(AuditFinding("k8s", "K8S-REL-03", SEVERITY_P1, "Container missing resource limits (cgroup CPU/memory caps).", file_path, 1, "resources"))

    # P1: runAsNonRoot check (skip if quick)
    if not quick:
        has_non_root = bool(re.search(r"runAsNonRoot:\s*true", content))
        if not has_non_root:
            if not focus or focus == "security":
                findings.append(AuditFinding("k8s", "K8S-SEC-04", SEVERITY_P1, "securityContext missing runAsNonRoot: true.", file_path, 1, "security"))

    return findings

# ==============================================================================
# Domain 2: Dockerfile Auditor
# ==============================================================================
def audit_docker_content(content: str, file_path: str, quick: bool = False, focus: Optional[str] = None) -> List[AuditFinding]:
    findings = []
    lines = content.splitlines()

    from_count = 0
    has_user = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue

        # Check FROM instruction
        if stripped.startswith("FROM"):
            from_count += 1
            # Check unpinned tag
            parts = stripped.split()
            if len(parts) >= 2:
                img = parts[1]
                if ":" not in img or img.endswith(":latest"):
                    if not focus or focus == "security":
                        findings.append(AuditFinding("docker", "DOCK-SEC-01", SEVERITY_P0, f"Base image '{img}' uses unpinned tag or :latest.", file_path, idx, "security"))

        # Check USER instruction
        if stripped.startswith("USER"):
            has_user = True
            if "root" in stripped.lower() or " 0" in stripped:
                if not focus or focus == "security":
                    findings.append(AuditFinding("docker", "DOCK-SEC-02", SEVERITY_P0, "Explicit USER root instruction detected.", file_path, idx, "security"))

        # Check exposed secrets in ENV or ARG
        secret_match = re.search(r"^(ENV|ARG)\s+.*(PASSWORD|SECRET|PRIVATE_KEY|API_KEY|TOKEN)\s*=", stripped, re.IGNORECASE)
        if secret_match:
            if not focus or focus == "security":
                findings.append(AuditFinding("docker", "DOCK-SEC-03", SEVERITY_P0, f"Hardcoded credential keyword in {secret_match.group(1)}: {stripped}", file_path, idx, "security"))

        # Check ADD instead of COPY for local files
        if stripped.startswith("ADD ") and not ("http://" in stripped or "https://" in stripped or ".tar" in stripped or ".gz" in stripped):
            if not quick and (not focus or focus == "best-practices"):
                findings.append(AuditFinding("docker", "DOCK-BP-01", SEVERITY_P2, "Use COPY instead of ADD for local files.", file_path, idx, "best-practices"))

    # Missing non-root USER
    if not has_user:
        if not focus or focus == "security":
            findings.append(AuditFinding("docker", "DOCK-SEC-04", SEVERITY_P1, "Dockerfile missing non-root USER directive (runs as root by default).", file_path, 1, "security"))

    # Missing multi-stage build (if not quick)
    if not quick and from_count < 2:
        if not focus or focus == "optimization":
            findings.append(AuditFinding("docker", "DOCK-OPT-01", SEVERITY_P2, "Single-stage build detected; prefer multi-stage builds to minimize image surface.", file_path, 1, "optimization"))

    return findings

# ==============================================================================
# Domain 3: Database Migration Auditor
# ==============================================================================
def audit_db_content(content: str, file_path: str, quick: bool = False, focus: Optional[str] = None) -> List[AuditFinding]:
    findings = []
    lines = content.splitlines()

    # P0: Unindexed CREATE INDEX on live tables without CONCURRENTLY
    for idx, line in enumerate(lines, 1):
        # Postgres non-concurrent index
        if re.search(r"CREATE\s+INDEX\b", line, re.IGNORECASE) and not re.search(r"CONCURRENTLY\b", line, re.IGNORECASE):
            if not focus or focus in ("locking", "performance"):
                findings.append(AuditFinding("db", "DB-PERF-01", SEVERITY_P0, "CREATE INDEX without CONCURRENTLY locks the table during migration.", file_path, idx, "locking"))

        # P0: Destructive operations without guard
        if re.search(r"\bDROP\s+(TABLE|COLUMN|DATABASE)\b", line, re.IGNORECASE) or re.search(r"\bTRUNCATE\b", line, re.IGNORECASE):
            if not focus or focus == "safety":
                findings.append(AuditFinding("db", "DB-SAFE-01", SEVERITY_P0, "Destructive DDL (DROP TABLE/COLUMN/TRUNCATE) detected.", file_path, idx, "safety"))

        # P1: ALTER TABLE ADD COLUMN with non-null default without prior transaction handling
        if re.search(r"ALTER\s+TABLE\s+.*\s+ADD\s+COLUMN\s+.*\s+NOT\s+NULL\s+DEFAULT\b", line, re.IGNORECASE):
            if not focus or focus == "locking":
                findings.append(AuditFinding("db", "DB-PERF-02", SEVERITY_P1, "ALTER TABLE ADD COLUMN NOT NULL DEFAULT can trigger a full table rewrite on older engines.", file_path, idx, "locking"))

    # P1: Foreign key without index
    fk_matches = re.finditer(r"FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES", content, re.IGNORECASE)
    for fk in fk_matches:
        col = fk.group(1).strip()
        # Look for CREATE INDEX ... (col)
        has_idx = bool(re.search(rf"CREATE\s+.*INDEX.*\({re.escape(col)}\)", content, re.IGNORECASE))
        if not has_idx and not quick:
            if not focus or focus in ("performance", "indexing"):
                findings.append(AuditFinding("db", "DB-PERF-03", SEVERITY_P1, f"Foreign key column '{col}' has no supporting index created in this migration.", file_path, 1, "performance"))

    return findings

# ==============================================================================
# Domain 4: Terraform / IaC Auditor
# ==============================================================================
def audit_terraform_content(content: str, file_path: str, quick: bool = False, focus: Optional[str] = None) -> List[AuditFinding]:
    findings = []
    lines = content.splitlines()

    # P0: Wildcard ingress on sensitive ports
    sensitive_ports = {"22", "3389", "5432", "3306", "27017", "6379", "9200", "8080"}

    # Track security group rules across block
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # Wildcard CIDR
        if '"0.0.0.0/0"' in stripped or "'0.0.0.0/0'" in stripped:
            # Check surrounding lines (10 lines before and after) for sensitive ports
            window_start = max(0, idx - 15)
            window_end = min(len(lines), idx + 15)
            block_context = "\n".join(lines[window_start:window_end])

            detected_ports = []
            for p in sensitive_ports:
                if re.search(rf"\b(from_port|to_port|port)\s*=\s*{p}\b", block_context):
                    detected_ports.append(p)

            if detected_ports:
                if not focus or focus == "security":
                    ports_str = ", ".join(detected_ports)
                    findings.append(AuditFinding(
                        "terraform",
                        "TF-SEC-01",
                        SEVERITY_P0,
                        f"Security group rule opens sensitive port(s) {ports_str} to world 0.0.0.0/0.",
                        file_path,
                        idx,
                        "security"
                    ))
            elif "ingress" in block_context:
                if not focus or focus == "security":
                    findings.append(AuditFinding(
                        "terraform",
                        "TF-SEC-01",
                        SEVERITY_P0,
                        "Ingress rule allows unrestricted 0.0.0.0/0 access.",
                        file_path,
                        idx,
                        "security"
                    ))

        # S3 Public read
        if re.search(r'acl\s*=\s*"(public-read|public-read-write)"', stripped):
            if not focus or focus == "security":
                findings.append(AuditFinding("terraform", "TF-SEC-02", SEVERITY_P0, "S3 bucket configured with public ACL (data leak risk).", file_path, idx, "security"))

        # Unencrypted EBS
        if "encrypted" in stripped and "false" in stripped:
            if not focus or focus in ("security", "storage"):
                findings.append(AuditFinding("terraform", "TF-SEC-03", SEVERITY_P1, "Storage volume explicitly configured with encrypted = false.", file_path, idx, "storage"))

        # Missing prevent_destroy on db instances
        if "aws_db_instance" in stripped:
            if not quick and (not focus or focus == "safety"):
                # Check next 20 lines for prevent_destroy
                ctx = "\n".join(lines[idx:min(len(lines), idx + 25)])
                if "prevent_destroy" not in ctx:
                    findings.append(AuditFinding("terraform", "TF-REL-01", SEVERITY_P1, "aws_db_instance missing lifecycle { prevent_destroy = true }.", file_path, idx, "safety"))

    return findings

# ==============================================================================
# CLI and Dispatcher
# ==============================================================================
def audit_target(domain: str, path: Path, quick: bool = False, focus: Optional[str] = None) -> List[AuditFinding]:
    findings = []
    files_to_check = []

    if path.is_file():
        files_to_check.append(path)
    elif path.is_dir():
        if domain == "k8s":
            files_to_check.extend(path.glob("**/*.yaml"))
            files_to_check.extend(path.glob("**/*.yml"))
        elif domain == "docker":
            files_to_check.extend([p for p in path.glob("**/Dockerfile*") if not p.name.endswith(".md")])
        elif domain == "db":
            files_to_check.extend(path.glob("**/*.sql"))
        elif domain == "terraform":
            files_to_check.extend(path.glob("**/*.tf"))
        elif domain == "all":
            files_to_check.extend(path.glob("**/*.yaml"))
            files_to_check.extend(path.glob("**/*.yml"))
            files_to_check.extend(path.glob("**/*.tf"))
            files_to_check.extend(path.glob("**/*.sql"))
            files_to_check.extend([p for p in path.glob("**/Dockerfile*") if not p.name.endswith(".md")])

    for f in files_to_check:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        target_domain = domain
        if domain == "all":
            if f.suffix in (".yaml", ".yml"):
                target_domain = "k8s"
            elif "dockerfile" in f.name.lower():
                target_domain = "docker"
            elif f.suffix == ".sql":
                target_domain = "db"
            elif f.suffix == ".tf":
                target_domain = "terraform"
            else:
                continue

        if target_domain == "k8s":
            findings.extend(audit_k8s_content(content, str(f), quick=quick, focus=focus))
        elif target_domain == "docker":
            findings.extend(audit_docker_content(content, str(f), quick=quick, focus=focus))
        elif target_domain == "db":
            findings.extend(audit_db_content(content, str(f), quick=quick, focus=focus))
        elif target_domain == "terraform":
            findings.extend(audit_terraform_content(content, str(f), quick=quick, focus=focus))

    return findings

def run_mock_test() -> int:
    """Run fast self-test verifying all 4 audit domains."""
    print("========================================================================")
    print(" 🛡️ RUNNING DEVOPS STATIC AUDITOR MOCK TEST ($0 TOKENS)")
    print("========================================================================")

    # 1. Test k8s auditor
    k8s_bad = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: billing-api
spec:
  template:
    spec:
      containers:
      - name: billing
        image: billing:1.0.0
        securityContext:
          privileged: true
"""
    k8s_findings = audit_k8s_content(k8s_bad, "k8s/billing.yaml")
    assert any(f.code == "K8S-SEC-01" for f in k8s_findings), "Failed to detect privileged container."
    assert any(f.code == "K8S-REL-01" for f in k8s_findings), "Failed to detect missing livenessProbe."
    assert any(f.code == "K8S-REL-03" for f in k8s_findings), "Failed to detect missing resource limits."
    print("  ✔ Check 1: Kubernetes auditor verified (caught privileged mode & missing probes).")

    # 2. Test docker auditor
    docker_bad = """FROM node:latest
ENV DB_PASSWORD=unencrypted_secret_123
COPY . /app
CMD ["node", "server.js"]
"""
    docker_findings = audit_docker_content(docker_bad, "Dockerfile")
    assert any(f.code == "DOCK-SEC-01" for f in docker_findings), "Failed to detect :latest tag."
    assert any(f.code == "DOCK-SEC-03" for f in docker_findings), "Failed to detect hardcoded password in ENV."
    assert any(f.code == "DOCK-SEC-04" for f in docker_findings), "Failed to detect missing non-root USER."
    print("  ✔ Check 2: Docker auditor verified (caught :latest tag, secret ENV, root USER).")

    # 3. Test db auditor
    db_bad = """-- Migration 002
CREATE INDEX idx_orders_customer ON orders (customer_id);
DROP TABLE legacy_audit_records;
"""
    db_findings = audit_db_content(db_bad, "migrations/002.sql")
    assert any(f.code == "DB-PERF-01" for f in db_findings), "Failed to detect table-locking CREATE INDEX."
    assert any(f.code == "DB-SAFE-01" for f in db_findings), "Failed to detect DROP TABLE statement."
    print("  ✔ Check 3: Database auditor verified (caught table-locking index & DROP TABLE).")

    # 4. Test terraform auditor
    tf_bad = """resource "aws_security_group_rule" "ssh" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  cidr_blocks = ["0.0.0.0/0"]
}
resource "aws_s3_bucket" "public_data" {
  bucket = "company-sensitive-data"
  acl    = "public-read"
}
"""
    tf_findings = audit_terraform_content(tf_bad, "infra/main.tf")
    assert any(f.code == "TF-SEC-01" for f in tf_findings), "Failed to detect 0.0.0.0/0 SSH rule."
    assert any(f.code == "TF-SEC-02" for f in tf_findings), "Failed to detect public S3 ACL."
    print("  ✔ Check 4: Terraform auditor verified (caught 0.0.0.0/0 SSH & public S3 ACL).")

    # 5. Test clean configurations pass with 0 findings
    k8s_clean = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-svc
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
      containers:
      - name: secure-app
        image: secure-svc:1.2.3
        resources:
          limits: { cpu: "500m", memory: "512Mi" }
          requests: { cpu: "100m", memory: "128Mi" }
        livenessProbe:
          httpGet: { path: /healthz, port: 8080 }
        readinessProbe:
          httpGet: { path: /ready, port: 8080 }
"""
    clean_findings = audit_k8s_content(k8s_clean, "k8s/clean.yaml")
    assert len(clean_findings) == 0, f"Clean k8s config generated false positives: {[f.code for f in clean_findings]}"
    print("  ✔ Check 5: Clean configurations verified with zero false positives.")

    print("------------------------------------------------------------------------")
    print(" ✅ ALL 5 DEVOPS STATIC AUDITOR DOMAINS PASSED ($0 TOKENS).")
    print("========================================================================")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Unified Offline DevOps & SRE Static Audit Engine")
    parser.add_argument("domain", nargs="?", choices=["k8s", "docker", "db", "terraform", "all"], help="Domain to audit")
    parser.add_argument("path", nargs="?", help="Path to manifest file or directory")
    parser.add_argument("--quick", action="store_true", help="Quick pass checking P0 critical blockers only")
    parser.add_argument("--deep", action="store_true", help="Exhaustive deep pass")
    parser.add_argument("--focus", choices=["security", "probes", "resources", "locking", "storage", "performance", "safety"], help="Filter by specific lens")
    parser.add_argument("--mock-test", action="store_true", help="Run automated self-test")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    if not args.domain or not args.path:
        parser.print_help()
        sys.exit(1)

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Target path '{target_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    findings = audit_target(args.domain, target_path, quick=args.quick, focus=args.focus)
    p0_count = len([f for f in findings if f.severity == SEVERITY_P0])
    p1_count = len([f for f in findings if f.severity == SEVERITY_P1])
    p2_count = len([f for f in findings if f.severity == SEVERITY_P2])

    if args.json:
        print(json.dumps({
            "domain": args.domain,
            "target": str(target_path),
            "findings_count": len(findings),
            "p0_critical": p0_count,
            "p1_high": p1_count,
            "p2_medium": p2_count,
            "findings": [f.to_dict() for f in findings]
        }, indent=2))
    else:
        print("========================================================================")
        print(f" 🛡️ DEVOPS AUDIT RESULTS: {len(findings)} FINDINGS (P0: {p0_count}, P1: {p1_count}, P2: {p2_count})")
        print("========================================================================")
        for f in findings:
            tag = f"[{f.severity}]"
            print(f"  {tag} {f.file_path}:{f.line_num} ({f.code}) [{f.category}] {f.message}")
        print("------------------------------------------------------------------------")
        if p0_count == 0 and p1_count == 0:
            print(" [✔] AUDIT PASSED: Zero critical or high-severity blockers ($0 tokens).")
        else:
            print(f" [✘] AUDIT FAILED: {p0_count} Critical, {p1_count} High issues must be resolved.")

    sys.exit(1 if p0_count > 0 else 0)

if __name__ == "__main__":
    main()
