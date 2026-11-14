#!/usr/bin/env python3
"""
Test Suite: Zero-Mock Test for Autonomous Engineering Blog Intelligence Pipeline
Runs end-to-end invariant validation on feed registry, deduplication, substance gating,
n8n workflow structure, and 4D synthesis schemas.
"""

import sys
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_pipeline():
    test_script = os.path.join(REPO_ROOT, "bin", "test-blog-pipeline.py")
    res = subprocess.run([sys.executable, test_script], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0, f"Pipeline tests failed:\n{res.stdout}\n{res.stderr}"

if __name__ == "__main__":
    test_pipeline()
    print("All pipeline tests passed via pytest/unittest runner.")
