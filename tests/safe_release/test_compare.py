"""Check the release report against plausible misleading comparison outcomes."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from safe_release.compare import compare_reports, digest, load_sample


def reports() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Provide known decisions for the exercise without depending on a hosted service."""
    sample = load_sample(Path(__file__).parents[2] / "src" / "safe_release" / "instances.json")
    quantities = [{"apple": 64}, {"apple": 64}, {"apple": 22, "pear": 20}]
    results: list[dict[str, Any]] = []
    for instance, selected in zip(sample["instances"], quantities):
        products = {p["name"]: p for p in instance["request"]["products"]}
        items = [dict(products[name], quantity=quantity) for name, quantity in selected.items()]
        results.append(
            {
                "id": instance["id"],
                "request_sha256": digest(instance["request"]),
                "seconds": 0.1,
                "error": None,
                "response": {
                    "status": "SUCCESS",
                    "recommendation": {
                        "items": items,
                        "totalCalories": sum(p["calories"] * p["quantity"] for p in items),
                        "totalCostUsd": sum(p["priceUsd"] * p["quantity"] for p in items),
                        "totalWeightKg": sum(p["weightKg"] * p["quantity"] for p in items),
                    },
                },
            }
        )
    baseline = {
        "schema_version": 1,
        "revision": "a" * 40,
        "solver": "google_scip",
        "environment": "same-host",
        "deadline_seconds": 30,
        "sample_sha256": digest(sample),
        "results": results,
    }
    candidate = deepcopy(baseline)
    candidate.update(revision="b" * 40, solver="highs")
    return baseline, candidate, sample


def test_equally_good_tied_selection_is_accepted() -> None:
    """A different optimal selection is acceptable under the declared business criteria."""
    baseline, candidate, sample = reports()
    item = candidate["results"][1]["response"]["recommendation"]["items"][0]
    item.update(name="pear")
    lines, accepted = compare_reports(baseline, candidate, sample)
    assert accepted
    assert "Valid pairs: 3 / 3." in lines


@pytest.mark.parametrize("difference", ["sample", "input", "missing", "duplicate", "environment", "deadline"])
def test_nonpaired_or_incomparable_reports_are_rejected(difference: str) -> None:
    """A report cannot substitute another sample or silently exclude difficult instances."""
    baseline, candidate, sample = reports()
    if difference == "sample":
        candidate["sample_sha256"] = "different"
    elif difference == "input":
        candidate["results"][0]["request_sha256"] = "different"
    elif difference == "missing":
        candidate["results"].pop()
    elif difference == "duplicate":
        candidate["results"].append(deepcopy(candidate["results"][0]))
    elif difference == "environment":
        candidate["environment"] = "another-host"
    else:
        candidate["deadline_seconds"] = 60
    with pytest.raises(ValueError):
        compare_reports(baseline, candidate, sample)


@pytest.mark.parametrize("problem", ["objective", "capacity", "fractional", "timeout", "nan", "attributes"])
def test_bad_decisions_and_failed_runs_require_investigation(problem: str) -> None:
    """Validity and instance-level regressions remain visible even when other pairs are good."""
    baseline, candidate, sample = reports()
    result = candidate["results"][0]
    recommendation = result["response"]["recommendation"]
    if problem == "objective":
        recommendation["items"][0]["quantity"] = 63
        recommendation.update(totalCalories=6300, totalCostUsd=63, totalWeightKg=63)
    elif problem == "capacity":
        recommendation["items"][0]["quantity"] = 65
        recommendation.update(totalCalories=6500, totalCostUsd=65, totalWeightKg=65)
    elif problem == "fractional":
        recommendation["items"][0]["quantity"] = 63.5
    elif problem == "timeout":
        result["seconds"] = 31
    elif problem == "nan":
        recommendation["totalCalories"] = float("nan")
    else:
        recommendation["items"][0]["priceUsd"] = 0.5
    lines, accepted = compare_reports(baseline, candidate, sample)
    assert not accepted
    assert any("INVESTIGATE" in line for line in lines)
    assert "Valid pairs: 2 / 3." in lines
