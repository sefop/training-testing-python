"""A nightly planning job that notifies the planner on call when no plan can be delivered.

Every night a planning job solves tomorrow's plan. NightlyPlanner receives the
result of that solve and decides whether a person must act before morning. When
one must, it notifies them through a Notifier.

NightlyPlanner never calls the solver itself: the solve result arrives as an
argument. Its only dependency is the notifier, and it receives it from outside
(dependency injection), so a test can pass in a mock instead of a real notifier.
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


class NightlyPlanner:
    """Reviews the result of the nightly solve and notifies the planner on call when needed."""

    def __init__(self, notifier: Notifier) -> None:
        """Creates a planner that notifies through the given notifier."""
        self._notifier = notifier

    def review(self, result: SolveResult) -> None:
        """Notifies the planner on call when tomorrow has no plan.

        Contract:
        - INFEASIBLE: sends exactly one notification,
          "Instance <instance_id>: no feasible plan exists."
        - TIME_LIMIT_NO_SOLUTION: sends exactly one notification,
          "Instance <instance_id>: no plan found within the time limit."
        - OPTIMAL or FEASIBLE: sends no notification. A plan exists, so nobody needs to
          be woken up.

        Args:
            result: the outcome of the nightly solve.
        """
        if result.status is SolveStatus.INFEASIBLE:
            self._notifier.notify(f"Instance {result.instance_id}: no feasible plan exists.")
        elif result.status is SolveStatus.TIME_LIMIT_NO_SOLUTION:
            self._notifier.notify(f"Instance {result.instance_id}: no plan found within the time limit.")
