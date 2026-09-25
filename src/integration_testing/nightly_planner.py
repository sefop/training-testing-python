"""A nightly planning job that notifies the planner on call when tonight has no plan.

Every night, a solve job saves the result of tomorrow's plan to a file (see
results_writer.py). NightlyPlanner reads that file back through a ResultsReader
and, when a person must act before morning, notifies them through a Notifier.

Both dependencies are received from outside (dependency injection). In an
integration test the reader stays real, because the results files are used only
by this program (a managed dependency); the notifier is replaced by a mock,
because people observe it (an unmanaged dependency).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class SolveStatus(Enum):
    """How a solve ended."""

    OPTIMAL = "optimal"
    """A plan was found and proven optimal."""

    FEASIBLE = "feasible"
    """A plan was found, but not proven optimal."""

    INFEASIBLE = "infeasible"
    """The model proved that no plan satisfies every constraint."""

    TIME_LIMIT_NO_SOLUTION = "time_limit_no_solution"
    """The time limit ran out before any plan was found."""


@dataclass(frozen=True)
class SolveResult:
    """The outcome of one night's solve.

    Attributes:
        instance_id: the name of the instance that was solved, e.g. "2026-09-26".
        status: how the solve ended.
    """

    instance_id: str
    status: SolveStatus


class Notifier(ABC):
    """Sends a short message to the planner on call.

    The real implementation sends an SMS or a chat message to a person. Tests
    never use it: they pass in a mock that records the calls instead.
    """

    @abstractmethod
    def notify(self, message: str) -> None:
        """Sends message to the planner on call."""


class ResultReader(ABC):
    """Anything that can read tonight's result: the real ResultsReader, or a stand-in in unit tests."""

    @abstractmethod
    def read(self, instance_id: str) -> SolveResult:
        """Returns the saved result of the given instance."""


class NightlyPlanner:
    """Reads tonight's result and notifies the planner on call when needed."""

    def __init__(self, reader: ResultReader, notifier: Notifier) -> None:
        """Creates a planner that reads results with reader and notifies through notifier."""
        self._reader = reader
        self._notifier = notifier

    def review_tonight(self, instance_id: str) -> None:
        """Reads the result of instance_id and notifies the planner on call when tomorrow has no plan.

        Contract:
        - INFEASIBLE: sends exactly one notification,
          "Instance <instance_id>: no feasible plan exists."
        - TIME_LIMIT_NO_SOLUTION: sends exactly one notification,
          "Instance <instance_id>: no plan found within the time limit."
        - OPTIMAL or FEASIBLE: sends no notification.
        - No result saved for instance_id: the reader's MissingResultError
          propagates, and no notification is sent.

        Args:
            instance_id: the instance solved tonight, e.g. "2026-09-26".
        """
        result = self._reader.read(instance_id)
        if result.status is SolveStatus.INFEASIBLE:
            self._notifier.notify(f"Instance {instance_id}: no feasible plan exists.")
        elif result.status is SolveStatus.TIME_LIMIT_NO_SOLUTION:
            self._notifier.notify(f"Instance {instance_id}: no plan found within the time limit.")
