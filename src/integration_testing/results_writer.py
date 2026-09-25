"""Saves each night's solve result to a file. Owned by the solve job's team.

The writer and the reader (results_reader.py) share no code on purpose: each
team encodes its own idea of the file's format. Only a test that runs both of
them against a real file can show that the two ideas agree.
"""

from __future__ import annotations

from pathlib import Path

from integration_testing.nightly_planner import SolveResult


class ResultsWriter:
    """Writes solve results as CSV files, one file per instance, in a folder."""

    def __init__(self, folder: Path) -> None:
        """Creates a writer that saves results in folder."""
        self._folder = folder

    def write(self, result: SolveResult) -> None:
        """Saves result to <folder>/<instance_id>.csv.

        Contract: the file holds a header line and one data line, with the
        status in lowercase, e.g.

            instance_id,status
            2026-09-26,infeasible

        An existing file for the same instance is replaced.
        """
        path = self._folder / f"{result.instance_id}.csv"
        status = result.status.value
        path.write_text(f"instance_id,status\n{result.instance_id},{status}\n", encoding="utf-8")
