"""A nightly planning job that pages the planner on call when no plan can be delivered.

Every night a planning job solves tomorrow's plan. NightlyPlanner receives the
result of that solve and decides whether a person must act before morning. When
one must, it pages them through a Pager.

NightlyPlanner never calls the solver itself: the solve result arrives as an
argument. Its only dependency is the pager, and it receives it from outside
(dependency injection), so a test can pass in a mock instead of a real pager.
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


class Pager(ABC):
    """Sends a short message to the planner on call.

    The real implementation sends an SMS or a chat message to a person. Tests
    never use it: they pass in a mock that records the calls instead.
    """

    @abstractmethod
    def page(self, message: str) -> None:
        """Sends message to the planner on call."""


class NightlyPlanner:
    """Reviews the result of the nightly solve and pages the planner on call when needed."""

    def __init__(self, pager: Pager) -> None:
        """Creates a planner that pages through the given pager."""
        self._pager = pager

    def review(self, result: SolveResult) -> None:
        """Pages the planner on call when tomorrow has no plan.

        Contract:
        - INFEASIBLE: sends exactly one page,
          "Instance <instance_id>: no feasible plan exists."
        - TIME_LIMIT_NO_SOLUTION: sends exactly one page,
          "Instance <instance_id>: no plan found within the time limit."
        - OPTIMAL or FEASIBLE: sends no page. A plan exists, so nobody needs to
          be woken up.

        Args:
            result: the outcome of the nightly solve.
        """
        if result.status is SolveStatus.INFEASIBLE:
            self._pager.page(f"Instance {result.instance_id}: no feasible plan exists.")
        elif result.status is SolveStatus.TIME_LIMIT_NO_SOLUTION:
            self._pager.page(f"Instance {result.instance_id}: no plan found within the time limit.")
