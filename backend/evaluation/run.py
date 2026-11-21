"""Repeatable smoke tests and optional live Vertex evaluation."""

import argparse
import json
import os
import statistics
import time
from pathlib import Path

import httpx

from utils.image_analysis import AnalysisError, ImageAnalyzer, MAX_IMAGE_BYTES, vertex_analyzer

ROOT = Path(__file__).parent


def run_case(case, live):
    case_id = case["id"]
    data = (ROOT / "images" / case["image"]).read_bytes() if "image" in case else b"invalid image"
    mime = "image/png"
    if case_id == "unsupported":
        mime = "text/plain"
    if case_id == "empty":
        data = b""
    if case_id == "oversized":
        data = b"x" * (MAX_IMAGE_BYTES + 1)

    calls = 0

    def simulate(*_):
        nonlocal calls
        calls += 1
        if case_id == "timeout":
            raise httpx.ReadTimeout("injected")
        if case_id == "malformed":
            return '{"fireDetected":'
        if case["group"] == "validation":
            raise AssertionError("Invalid input reached model")
        fire = case.get("fire", False)
        return json.dumps({
            "personCount": 3 if case_id == "three-people" else 0,
            "crowdDensity": "low",
            "smokeDetected": False,
            "fireDetected": fire,
            "stampedeDetected": False,
            "medicalEmergency": False,
            "potentialRisk": fire,
            "incidentRecommended": fire,
            "uncertain": case["expected"] == "uncertain",
            "incidentType": "fire" if fire else "none",
            "suggestedAction": "Review the visible scene manually.",
        })

    analyzer = live if live and case["group"] not in {"validation", "failure"} else ImageAnalyzer(simulate)
    start = time.perf_counter()
    try:
        result = analyzer.analyze(data, mime)
        actual, fire = result["status"], result["fireDetected"]
    except AnalysisError as error:
        actual, fire = error.code, None
    if case_id == "timeout":
        assert calls == 2
    if case_id == "malformed":
        assert calls == 1
    matched = actual == case["expected"] and ("fire" not in case or case["fire"] == fire)
    return {**case, "actual": actual, "fireFlag": fire, "matched": matched,
            "milliseconds": round((time.perf_counter() - start) * 1000, 2)}


def summarize(rows):
    labeled = [row for row in rows if "fire" in row]
    answered = [row for row in labeled if row["actual"] in {"detected", "no_detection"}]
    tp = sum(row["fire"] and row["fireFlag"] for row in answered)
    fp = sum(not row["fire"] and row["fireFlag"] for row in answered)
    positives = sum(row["fire"] for row in labeled)
    return {
        "fireLabeled": len(labeled),
        "fireDecisions": len(answered),
        "fireTruePositives": tp,
        "fireFalsePositives": fp,
        "firePrecision": tp / (tp + fp) if tp + fp else None,
        "fireRecall": tp / positives if positives else None,
        "medianImageAnalysisMilliseconds": statistics.median(
            row["milliseconds"] for row in rows if row["group"] in {"clear", "degraded", "ambiguous"}
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send the six synthetic images to Vertex AI")
    args = parser.parse_args()
    live = vertex_analyzer() if args.live else None
    rows = [run_case(case, live) for case in json.loads((ROOT / "cases.json").read_text())]
    report = {
        "mode": "vertex" if live else "scripted-model",
        "matched": sum(row["matched"] for row in rows),
        "total": len(rows),
        "cases": rows,
    }
    if live:
        report["model"] = os.getenv("DRISHTI_VISION_MODEL", "gemini-2.5-pro")
        report["results"] = summarize(rows)
    else:
        report["medianScriptedImageAnalysisMilliseconds"] = summarize(rows)["medianImageAnalysisMilliseconds"]
    print(json.dumps(report, indent=2))
    return int(report["matched"] != report["total"])


if __name__ == "__main__":
    raise SystemExit(main())
