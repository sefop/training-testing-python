"""Collect and compare decisions from two releases using one fixed instance sample.

This exercise tool uses only Python's standard library. It assesses the public
web interface rather than importing either application's internal modules.
Reports are evidence for a reader's release review, not permission to deploy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
EPSILON = 1e-6


def digest(value: Any) -> str:
    """Identify the exact JSON values used in an experiment, ignoring formatting."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_sample(path: Path) -> dict[str, Any]:
    """Read a fixed sample with distinct instance identifiers and known expectations."""
    sample = json.loads(path.read_text(encoding="utf-8"))
    instances = sample["instances"]
    if not instances or len({item["id"] for item in instances}) != len(instances):
        raise ValueError("The sample must contain distinct, nonempty instances.")
    return sample


def request_json(url: str, timeout: float, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Request one public web result, exposing network failures to the caller."""
    data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def collect(args: argparse.Namespace) -> dict[str, Any]:
    """Record a release's responses to the fixed sample and its declared context."""
    sample = load_sample(args.sample)
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        raise ValueError("Record a full, lowercase 40-character Git commit identifier.")
    if urlsplit(args.url).scheme not in {"http", "https"}:
        raise ValueError("The service URL must use HTTP or HTTPS.")
    if not math.isfinite(args.deadline) or args.deadline <= 0:
        raise ValueError("The response deadline must be a finite positive number.")
    base_url = args.url.rstrip("/")
    # Waking an idle example host is separate from measuring warmed requests.
    # This socket timeout bounds waiting; it does not cancel a server-side solve.
    health = request_json(base_url + "/health", 120)
    if health.get("status") != "ok":
        raise ValueError("The service did not report healthy startup.")
    results: list[dict[str, Any]] = []
    for item in sample["instances"]:
        started = time.perf_counter()
        try:
            response = request_json(base_url + "/solve", args.deadline, item["request"])
            error = None
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            # Retain a failed instance so aggregates cannot silently exclude it.
            # Exception class is enough for the report; URLs may contain secrets.
            response = None
            error = type(exc).__name__
        results.append(
            {
                "id": item["id"],
                "request_sha256": digest(item["request"]),
                "seconds": time.perf_counter() - started,
                "response": response,
                "error": error,
            }
        )
    return {
        "schema_version": 1,
        "revision": args.revision,
        "solver": args.solver,
        "environment": args.environment,
        "deadline_seconds": args.deadline,
        "sample_sha256": digest(sample),
        "results": results,
    }


def number(value: Any) -> float:
    """Accept finite numeric measurements, excluding booleans and missing values."""
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError("Expected a finite numeric measurement.")
    return float(value)


def measures(instance: dict[str, Any], result: dict[str, Any], deadline: float) -> dict[str, float]:
    """Validate a reported selection against its inputs and return recomputed measures."""
    seconds = number(result["seconds"])
    if result.get("error") or seconds < 0 or seconds > deadline:
        raise ValueError("A response failed or missed the declared deadline.")
    response = result["response"]
    if not isinstance(response, dict) or response.get("status") != "SUCCESS":
        raise ValueError("The application did not return a successful decision.")
    recommendation = response["recommendation"]
    products = {product["name"]: product for product in instance["request"]["products"]}
    seen: set[str] = set()
    calories = cost = weight = 0.0
    items = recommendation["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("The known instances require a nonempty selection.")
    for selected in items:
        name = selected["name"]
        quantity = selected["quantity"]
        if name not in products or name in seen:
            raise ValueError("A product is unknown or duplicated in the selection.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Selected quantities must be positive whole numbers.")
        seen.add(name)
        product = products[name]
        # Recompute from the original input, never from response-supplied prices.
        for field in ("priceUsd", "weightKg", "calories"):
            if abs(number(selected[field]) - number(product[field])) > EPSILON:
                raise ValueError("A selected product's attributes differ from its input.")
        calories += quantity * number(product["calories"])
        cost += quantity * number(product["priceUsd"])
        weight += quantity * number(product["weightKg"])
    if cost > instance["request"]["maxBudgetUsd"] + EPSILON:
        raise ValueError("The selection exceeds the budget.")
    if weight > instance["request"]["maxWeightKg"] + EPSILON:
        raise ValueError("The selection exceeds the weight limit.")
    for field, actual in (("totalCalories", calories), ("totalCostUsd", cost), ("totalWeightKg", weight)):
        if abs(number(recommendation[field]) - actual) > EPSILON:
            raise ValueError("Reported totals disagree with the selected products.")
    if abs(calories - number(instance["expected_calories"])) > EPSILON:
        raise ValueError("Calories differ from this instance's known optimum.")
    return {"calories": calories, "cost": cost, "weight": weight, "seconds": seconds}


def checked_results(report: dict[str, Any], sample: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Require exactly the fixed sample under a recorded, supported report format."""
    if report.get("schema_version") != 1 or report["sample_sha256"] != digest(sample):
        raise ValueError("Reports must use the identical sample and supported format.")
    results = report["results"]
    indexed = {item["id"]: item for item in results}
    expected = {item["id"] for item in sample["instances"]}
    if len(indexed) != len(results) or set(indexed) != expected:
        raise ValueError("A report is missing instances or contains extra or duplicate instances.")
    for item in sample["instances"]:
        if indexed[item["id"]]["request_sha256"] != digest(item["request"]):
            raise ValueError("An instance's input differs between the report and fixed sample.")
    return indexed


def compare_reports(
    baseline: dict[str, Any], candidate: dict[str, Any], sample: dict[str, Any]
) -> tuple[list[str], bool]:
    """Assess paired measures, preserving instance-level failures for human review."""
    for report in (baseline, candidate):
        if not re.fullmatch(r"[0-9a-f]{40}", report["revision"]):
            raise ValueError("A report lacks a full commit identifier.")
    if baseline["solver"] != "google_scip" or candidate["solver"] != "highs":
        raise ValueError("This exercise compares the SCIP baseline with the HiGHS candidate.")
    if not baseline["environment"] or baseline["environment"] != candidate["environment"]:
        raise ValueError("Use comparable environments with the same recorded environment label.")
    deadline = number(baseline["deadline_seconds"])
    if deadline <= 0 or deadline != number(candidate["deadline_seconds"]):
        raise ValueError("Both reports must declare the same positive response deadline.")
    before = checked_results(baseline, sample)
    after = checked_results(candidate, sample)
    lines = [
        "| Instance | Calories before / after | Cost before / after | Weight before / after | Seconds before / after | Assessment |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    accepted = True
    differences: list[float] = []
    for instance in sample["instances"]:
        identifier = instance["id"]
        try:
            left = measures(instance, before[identifier], deadline)
            right = measures(instance, after[identifier], deadline)
            differences.append(right["calories"] - left["calories"])
            lines.append(
                f"| {identifier} | {left['calories']:g} / {right['calories']:g} | "
                f"{left['cost']:g} / {right['cost']:g} | {left['weight']:g} / {right['weight']:g} | "
                f"{left['seconds']:.3f} / {right['seconds']:.3f} | Meets declared decision criteria |"
            )
        except (KeyError, TypeError, ValueError) as exc:
            accepted = False
            lines.append(
                f"| {identifier} | unavailable | unavailable | unavailable | unavailable | INVESTIGATE: {exc} |"
            )
    if differences:
        lines.extend(
            ["", f"Mean paired calorie difference among valid pairs: {sum(differences) / len(differences):g}."]
        )
    lines.extend(
        [
            "",
            f"Valid pairs: {len(differences)} / {len(sample['instances'])}.",
            (
                "Decision criteria met; complete the human review before merge."
                if accepted
                else "Unexpected result: investigate before release."
            ),
            "Timing is warmed request duration, not isolated solver time. Review variation without claiming a speedup.",
            "Revision, solver, and environment labels are declared by the reader; confirm them against deployment records and logs.",
        ]
    )
    return lines, accepted


def main() -> int:
    """Provide repeatable collection and comparison commands for the exercise."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    collection = commands.add_parser("collect")
    collection.add_argument("--url", required=True)
    collection.add_argument("--revision", required=True)
    collection.add_argument("--solver", choices=("google_scip", "highs"), required=True)
    collection.add_argument("--environment", required=True)
    collection.add_argument("--deadline", type=float, default=30)
    collection.add_argument("--sample", type=Path, default=HERE / "instances.json")
    collection.add_argument("--output", type=Path, required=True)
    comparison = commands.add_parser("compare")
    comparison.add_argument("baseline", type=Path)
    comparison.add_argument("candidate", type=Path)
    comparison.add_argument("--sample", type=Path, default=HERE / "instances.json")
    args = parser.parse_args()
    try:
        if args.command == "collect":
            report = collect(args)
            args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            print(f"Recorded {len(report['results'])} instances in {args.output}.")
            return 1 if any(result["error"] for result in report["results"]) else 0
        lines, accepted = compare_reports(
            json.loads(args.baseline.read_text(encoding="utf-8")),
            json.loads(args.candidate.read_text(encoding="utf-8")),
            load_sample(args.sample),
        )
        print("\n".join(lines))
        return 0 if accepted else 1
    except (HTTPError, URLError, TimeoutError, OSError, KeyError, TypeError, ValueError):
        # Avoid dumping a supplied URL or response body into shared reports.
        print(
            "Collection or comparison failed. Check connectivity, report fields, sample identity, and declared settings.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
