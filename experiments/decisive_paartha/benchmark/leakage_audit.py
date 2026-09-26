"""
Benchmark Leakage Audit Tool for Paartha Decisive Experiment.
Statically analyzes all system and tool source files to ensure ZERO benchmark leakage.
Verifies that runtime code does not contain hardcoded task keywords, entity lists, or task IDs.
"""

import os
import re
from typing import Dict, List, Any, Tuple

FORBIDDEN_KEYWORDS = [
    # Domain A column/entity names
    "freight_cost", "transit_hours", "weight_kg", "shipment_id",
    "'central'", "'north'", "'south'", '"central"', '"north"', '"south"',
    # Domain B column/entity names
    "absorbance_nm", "temp_kelvin", "quantum_noise", "probe_id",
    "'alpha'", "'beta'", "'gamma'", '"alpha"', '"beta"', '"gamma"',
    # Task IDs & Benchmark Scenario strings
    "task_l1", "task_l2", "task_l3", "t_exp",
    "spectroscopy", "vacuum chamber", "cargo weight"
]

def run_leakage_audit(systems_dir: str) -> Dict[str, Any]:
    findings = []
    files_scanned = 0

    for root, _, files in os.walk(systems_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            filepath = os.path.join(root, f)
            files_scanned += 1
            
            with open(filepath, "r", encoding="utf-8") as sfile:
                content = sfile.read()
                lines = content.splitlines()

            for line_idx, line in enumerate(lines, 1):
                clean_line = line.strip().lower()
                # Skip comments and docstrings
                if clean_line.startswith("#") or clean_line.startswith('"""') or clean_line.startswith("'''"):
                    continue
                
                for kw in FORBIDDEN_KEYWORDS:
                    if kw in clean_line:
                        findings.append({
                            "file": os.path.basename(filepath),
                            "line_number": line_idx,
                            "keyword": kw,
                            "line_snippet": line.strip()
                        })

    verdict = "PASSED_CLEAN" if len(findings) == 0 else "FAILED_LEAKAGE_DETECTED"
    return {
        "verdict": verdict,
        "files_scanned": files_scanned,
        "total_leakages": len(findings),
        "details": findings
    }

if __name__ == "__main__":
    import json
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    systems_dir = os.path.abspath(os.path.join(curr_dir, "..", "systems"))
    tools_dir = os.path.abspath(os.path.join(curr_dir, "..", "tools"))
    res_sys = run_leakage_audit(systems_dir)
    res_tools = run_leakage_audit(tools_dir)
    total_leaks = res_sys["total_leakages"] + res_tools["total_leakages"]
    verdict = "PASSED_CLEAN" if total_leaks == 0 else "FAILED_LEAKAGE_DETECTED"
    print(json.dumps({"verdict": verdict, "systems": res_sys, "tools": res_tools}, indent=2))

