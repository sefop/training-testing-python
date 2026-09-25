"""Reads each night's solve result back from its file. Owned by the planner's team.

The reader and the writer (results_writer.py) share no code on purpose: each
team encodes its own idea of the file's format. Only a test that runs both of
them against a real file can show that the two ideas agree.
"""

from __future__ import annotations

from pathlib import Path

from integration_testing.nightly_planner import ResultReader, SolveResult, SolveStatus


class MissingResultError(Exception):
    """Raised when no result was saved for the requested instance."""


class ResultsReader(ResultReader):
    """Reads solve results from CSV files, one file per instance, in a folder."""

    def __init__(self, folder: Path) -> None:
        """Creates a reader that looks for results in folder."""
        self._folder = folder

    def read(self, instance_id: str) -> SolveResult:
        """Returns the result saved in <folder>/<instance_id>.csv.

        Contract: the file holds a header line "instance_id,status" and one data
        line whose status is one of the lowercase SolveStatus values, e.g.
        "2026-09-26,infeasible".

        Raises:
            MissingResultError: if no file exists for instance_id. Only a missing
                file becomes this error; any other I/O failure propagates as is.
            ValueError: if the status in the file is not a known status.
        """
        path = self._folder / f"{instance_id}.csv"
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError as error:
            raise MissingResultError(f"No result for instance {instance_id} in {self._folder}") from error
        saved_id, status = lines[1].split(",")
        return SolveResult(instance_id=saved_id, status=SolveStatus(status))
