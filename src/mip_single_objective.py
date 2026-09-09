# This import makes all type annotations in this file lazy strings that are
# never evaluated at runtime. This lets us use the modern `X | Y` union syntax
# (PEP 604, Python 3.10+) without raising a TypeError on Python 3.7–3.9.
from __future__ import annotations

import abc
import itertools
from dataclasses import dataclass

import highspy


@dataclass(frozen=True)
class Item:
    """Represents one purchasable item in the knapsack model.

    An Item is a plain data holder shared by every KnapsackSolver
    implementation in this module. It is frozen so a single instance can be
    reused safely across multiple solvers in the same test, including
    parametrized tests that call several solvers with the exact same items.

    No validation is performed here: constructing an Item with a negative
    cost or a negative max_quantity is not rejected. This module's focus is
    testing solver *behavior*, not input validation, which is covered by a
    different exercise.
    """

    name: str
    cost: float
    volume: float
    calories: float
    max_quantity: int


@dataclass(frozen=True)
class KnapsackSolution:
    """Represents the outcome a KnapsackSolver promises to its caller.

    This is the contract every KnapsackSolver implementation in this module
    returns, regardless of how it computes the answer internally. A caller
    — or a test — can rely on these fields without knowing or caring
    whether the solver behind them is a brute-force search or a
    professional MIP solver.

    When feasible is False, no selection of items — including selecting
    nothing — respects both budgets, and quantities, total_calories,
    total_cost, and total_volume carry no meaning. When feasible is True,
    quantities maps every item's name to how many units of it were chosen,
    including 0 for items that were not chosen, and no other selection
    respecting both budgets reaches a higher total_calories.
    """

    feasible: bool
    quantities: dict[str, int]
    total_calories: float
    total_cost: float
    total_volume: float


class KnapsackSolver(abc.ABC):
    """Represents the ability to solve one knapsack instance.

    This is the public contract every concrete solver in this module
    fulfills: given a catalogue of items and two budgets, find the
    calorie-maximizing selection if one exists, or report that the
    instance is infeasible. Tests written against this contract assume
    nothing about how a concrete solver reaches its answer — that choice
    is an implementation detail deliberately kept out of the tests, so
    that any class fulfilling this contract can be tested the same way,
    including ones not yet written.
    """

    @abc.abstractmethod
    def solve(
        self, items: list[Item], cost_budget: float, volume_budget: float
    ) -> KnapsackSolution:
        """Return the calorie-maximizing selection, or report infeasibility.

        A selection is feasible when every item's chosen quantity is
        between 0 and its max_quantity, and the selection's total cost and
        total volume each stay within their respective budget.
        """
        raise NotImplementedError


class EnumerationSolver(KnapsackSolver):
    """A KnapsackSolver that searches every possible selection exhaustively.

    This exists to be an obviously correct oracle: for a small
    teaching-scale instance, checking every combination by hand is
    tractable to reason about, which is exactly what's needed from a
    reference implementation that another KnapsackSolver is tested
    against. It is not meant to represent how a production knapsack
    solver would be built.
    """

    def solve(
        self, items: list[Item], cost_budget: float, volume_budget: float
    ) -> KnapsackSolution:
        # Brute force chosen deliberately: correctness here needs to be obvious
        # by inspection, not merely tested, since this solver is itself the
        # ground truth that HighsSolver is tested against.
        quantity_ranges = [range(item.max_quantity + 1) for item in items]

        # found_feasible tracks whether *any* combination — including selecting
        # nothing — has satisfied both budgets. Selecting nothing costs 0 and
        # uses 0 volume, which only satisfies a budget that is itself
        # non-negative, so a negative budget can make even that trivial
        # selection infeasible. This is why feasibility cannot simply be
        # assumed and must be tracked explicitly across the search.
        found_feasible = False
        best_quantities: dict[str, int] = {}
        best_calories = 0.0
        best_cost = 0.0
        best_volume = 0.0

        # itertools.product(*[]) yields exactly one result, an empty tuple, when
        # items is empty — so the search below handles the no-items case the
        # same way as every other case, without needing a special branch for it.
        for combination in itertools.product(*quantity_ranges):
            cost = sum(q * item.cost for q, item in zip(combination, items))
            volume = sum(q * item.volume for q, item in zip(combination, items))
            if cost > cost_budget or volume > volume_budget:
                continue

            calories = sum(q * item.calories for q, item in zip(combination, items))
            # Strict '>' is a deliberate tie-break rule: the first feasible
            # combination found with a given calorie total is kept, so ties are
            # resolved by iteration order rather than by re-examining every
            # equally-good combination.
            if not found_feasible or calories > best_calories:
                found_feasible = True
                best_calories = calories
                best_cost = cost
                best_volume = volume
                best_quantities = dict(zip((item.name for item in items), combination))

        if not found_feasible:
            return KnapsackSolution(
                feasible=False, quantities={}, total_calories=0.0, total_cost=0.0, total_volume=0.0
            )

        return KnapsackSolution(
            feasible=True,
            quantities=best_quantities,
            total_calories=best_calories,
            total_cost=best_cost,
            total_volume=best_volume,
        )


class HighsSolver(KnapsackSolver):
    """A KnapsackSolver backed by the open-source HiGHS MIP solver.

    Same contract as EnumerationSolver: given the items and the two
    budgets, it returns the calorie-maximizing selection, or reports
    infeasibility, using the exact same rules for what counts as feasible.
    Having two solvers that satisfy the exact same contract is what lets a
    single test suite prove they agree, rather than trusting either one
    blindly.
    """

    def solve(
        self, items: list[Item], cost_budget: float, volume_budget: float
    ) -> KnapsackSolution:
        if not items:
            # With no items, the only candidate selection is the empty one,
            # which contributes zero cost and zero volume. Feasibility reduces
            # to whether that trivial selection respects both budgets, which is
            # answered directly rather than asking HiGHS to solve a model with
            # no variables and a bare-number constraint expression — untested,
            # undocumented behavior this module doesn't rely on.
            feasible = cost_budget >= 0 and volume_budget >= 0
            return KnapsackSolution(
                feasible=feasible, quantities={}, total_calories=0.0, total_cost=0.0, total_volume=0.0
            )

        model = highspy.Highs()
        # Without this, HiGHS prints solver iteration/status banners to stdout on
        # every solve, which would pollute pytest -v output across every situation
        # and every solver this module is tested with.
        model.setOptionValue("output_flag", False)

        variables = {}
        # Built as three separate accumulators, each consumed exactly once by a
        # single addConstr/maximize call below, rather than reused afterward or
        # summed with Python's sum(). This sidesteps a known mutation quirk in
        # highspy's linear-expression type when the same expression object is
        # combined into more than one larger expression.
        cost_expr = 0
        volume_expr = 0
        calorie_expr = 0
        for item in items:
            variable = model.addVariable(lb=0, ub=item.max_quantity, type=highspy.HighsVarType.kInteger)
            # Keyed by item name rather than position, so reading the solution back
            # below never depends on HiGHS preserving the order variables were added in.
            variables[item.name] = variable
            cost_expr = cost_expr + item.cost * variable
            volume_expr = volume_expr + item.volume * variable
            calorie_expr = calorie_expr + item.calories * variable

        model.addConstr(cost_expr <= cost_budget)
        model.addConstr(volume_expr <= volume_budget)
        model.maximize(calorie_expr)

        # A negative budget makes even the all-zero selection violate a
        # constraint, which HiGHS reports through its model status rather than
        # through the objective value — an infeasible model has no solution
        # values to read at all.
        if model.getModelStatus() != highspy.HighsModelStatus.kOptimal:
            return KnapsackSolution(
                feasible=False, quantities={}, total_calories=0.0, total_cost=0.0, total_volume=0.0
            )

        # round() is necessary because an integer MIP solution can come back as
        # e.g. 1.9999999996 due to solver tolerance, and this module's contract
        # promises quantities are exact ints.
        quantities = {name: round(model.val(variable)) for name, variable in variables.items()}
        total_cost = sum(q * item.cost for q, item in zip(quantities.values(), items))
        total_volume = sum(q * item.volume for q, item in zip(quantities.values(), items))
        total_calories = sum(q * item.calories for q, item in zip(quantities.values(), items))

        return KnapsackSolution(
            feasible=True,
            quantities=quantities,
            total_calories=total_calories,
            total_cost=total_cost,
            total_volume=total_volume,
        )
