"""Unit tests for NightlyPlanner.

The behavior of NightlyPlanner is a call to another system: it notifies a person.
It returns nothing, so these tests replace the notifier with a mock, a stand-in
that records every call it receives, and assert on those calls.

The file has two parts:
- Two finished tests, from the book's worked example. The first uses a mock
  written by hand, so you can see that a mock is nothing more than an object
  that records its calls. The second uses unittest.mock, the standard library
  tool that builds such an object for you.
- Three tests for you to write, each marked @pytest.mark.skip.

Test names follow test__method__given_condition__expected_outcome, so a failing
test reports in plain words which promise was broken.
"""

from unittest.mock import Mock

import pytest

from mocks.nightly_planner import NightlyPlanner, Notifier, SolveResult, SolveStatus


class RecordingNotifier(Notifier):
    """A mock written by hand: it sends nothing and records every message."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str) -> None:
        self.messages.append(message)


# =============================================================================
# Worked example: the two tests from the book.
# =============================================================================


def test__review__given_an_infeasible_plan__notifies_once_with_the_instance() -> None:
    # Arrange
    notifier = RecordingNotifier()
    planner = NightlyPlanner(notifier)
    result = SolveResult(instance_id="2026-09-26", status=SolveStatus.INFEASIBLE)

    # Act
    planner.review(result)

    # Assert
    assert notifier.messages == ["Instance 2026-09-26: no feasible plan exists."]


def test__review__given_a_feasible_plan__sends_no_notification() -> None:
    # Arrange
    # spec=Notifier makes the mock accept only the calls a Notifier has: a typo such
    # as notifier.notfiy(...) fails instead of being silently recorded.
    notifier = Mock(spec=Notifier)
    planner = NightlyPlanner(notifier)
    result = SolveResult(instance_id="2026-09-26", status=SolveStatus.FEASIBLE)

    # Act
    planner.review(result)

    # Assert
    notifier.notify.assert_not_called()


# =============================================================================
# Your tests: use Mock(spec=Notifier), then delete the skip line.
# =============================================================================


@pytest.mark.skip(reason="Exercise: implement me")
def test__review__given_the_time_limit_ran_out__notifies_once_with_the_time_limit_message() -> None:
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__review__given_an_optimal_plan__sends_no_notification() -> None:
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__review__given_another_instance__names_that_instance_in_the_notification() -> None:
    pass
