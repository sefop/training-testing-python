"""Integration tests for the nightly planner and its results files.

Every test here touches the real file system, so every test here is an
integration test. pytest's tmp_path fixture gives each test a new, empty
temporary folder, and deletes it afterwards: the real file system, without
leaving files behind.

The file has two parts:
- One finished test, from the book's worked example: the real ResultsWriter
  writes tonight's file, the real ResultsReader reads it inside NightlyPlanner,
  and only the notifier is a mock.
- Three tests for you to write, each marked @pytest.mark.skip.

Test names follow test__method__given_condition__expected_outcome, so a failing
test reports in plain words which promise was broken.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from integration_testing.nightly_planner import NightlyPlanner, Notifier, SolveResult, SolveStatus
from integration_testing.results_reader import MissingResultError, ResultsReader
from integration_testing.results_writer import ResultsWriter


# =============================================================================
# Worked example: the test from the book. It joins the writer and the reader.
# =============================================================================


def test__review_tonight__given_an_infeasible_result_on_disk__notifies_once(tmp_path: Path) -> None:
    # Arrange
    ResultsWriter(tmp_path).write(SolveResult(instance_id="2026-09-26", status=SolveStatus.INFEASIBLE))
    notifier = Mock(spec=Notifier)
    planner = NightlyPlanner(ResultsReader(tmp_path), notifier)

    # Act
    planner.review_tonight("2026-09-26")

    # Assert
    notifier.notify.assert_called_once_with("Instance 2026-09-26: no feasible plan exists.")


# =============================================================================
# Your tests: use tmp_path for the folder, then delete the skip line.
# =============================================================================


@pytest.mark.skip(reason="Exercise: implement me")
def test__read__given_no_file_for_the_instance__raises_missing_result_error(tmp_path: Path) -> None:
    # An edge case only the real file system can produce: tonight's file does not exist.
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__write__given_an_infeasible_result__writes_the_expected_text(tmp_path: Path) -> None:
    # The writer's own test: compare the file's text with the exact text you expect.
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__read__given_a_hand_written_file__returns_its_result(tmp_path: Path) -> None:
    # The reader's own test: write the file's text yourself, without ResultsWriter.
    pass
