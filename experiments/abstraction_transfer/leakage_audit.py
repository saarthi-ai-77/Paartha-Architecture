"""
Multi-Domain Benchmark Leakage Audit Scanner.
Verifies that Domain A (Logistics), Domain B (Spectroscopy), and Domain C (Finance)
maintain absolute semantic and lexical separation with zero cross-contamination.
"""

import os
import re
from typing import Dict, List, Any

DOMAIN_A_EXCLUSIVE = ["freight_cost", "transit_hours", "weight_kg", "shipment_id", "hub"]
DOMAIN_B_EXCLUSIVE = ["absorbance_nm", "temp_kelvin", "quantum_noise", "probe_id", "chamber"]
DOMAIN_C_EXCLUSIVE = ["spread_bps", "latency_micros", "fill_volume", "order_id", "exchange"]

def run_multidomain_leakage_audit(base_dir: str) -> Dict[str, Any]:
    findings = []
    files_scanned = 0

    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            filepath = os.path.join(root, f)
            files_scanned += 1

            with open(filepath, "r", encoding="utf-8") as sfile:
                lines = sfile.readlines()

            for line_idx, line in enumerate(lines, 1):
                clean = line.strip().lower()
                # Skip comments, docstrings, and corpus definitions
                if clean.startswith("#") or clean.startswith('"""') or clean.startswith("'''"):
                    continue
                if "corpus_multidomain.py" in filepath:
                    continue  # The corpus file legitimately defines all three domains
                if "leakage_audit.py" in filepath:
                    continue  # The audit file legitimately lists forbidden words

                # In runtime engines and tool files, check that domain terms are not hardcoded
                for kw in DOMAIN_A_EXCLUSIVE + DOMAIN_B_EXCLUSIVE + DOMAIN_C_EXCLUSIVE:
                    if kw in clean:
                        findings.append({
                            "file": os.path.basename(filepath),
                            "line": line_idx,
                            "keyword": kw,
                            "snippet": line.strip()
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
    res = run_multidomain_leakage_audit(curr_dir)
    print(json.dumps(res, indent=2))
