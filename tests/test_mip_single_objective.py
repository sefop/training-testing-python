from __future__ import annotations

import pytest

from mip_single_objective import EnumerationSolver, HighsSolver, Item

# Every situation below runs against both solvers. Agreement across two
# independently implemented KnapsackSolver classes is itself the evidence
# that these tests assert on the solver's contract rather than on either
# implementation's internals.
#
# The situations appear in the same order as the table in the guide, from the
# simplest instance to the most involved, so a row there and a test here can be
# read side by side.
SOLVERS = [EnumerationSolver(), HighsSolver()]
SOLVER_IDS = ["enumeration", "highs"]


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_no_items__returns_the_empty_selection(solver) -> None:
    # ARRANGE
    # There is nothing to choose from, regardless of how generous the budgets
    # are, so the only possible selection is the empty one.

    # ACT
    result = solver.solve([], cost_budget=10, volume_budget=10)

    # ASSERT
    assert result.feasible is True
    assert result.quantities == {}
    assert result.total_calories == pytest.approx(0, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_negative_cost_budget__reports_infeasible(solver) -> None:
    # ARRANGE
    # A negative cost budget means even selecting nothing, which costs 0,
    # already violates the budget — no selection can ever be feasible.
    item_r = Item(name="R", cost=1, volume=1, calories=10, max_quantity=5)

    # ACT
    result = solver.solve([item_r], cost_budget=-1, volume_budget=5)

    # ASSERT
    assert result.feasible is False


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_negative_volume_budget__reports_infeasible(solver) -> None:
    # ARRANGE
    # Mirrors the negative cost budget case: a negative volume budget makes
    # every selection, including the empty one, infeasible.
    item_s = Item(name="S", cost=1, volume=1, calories=10, max_quantity=5)

    # ACT
    result = solver.solve([item_s], cost_budget=5, volume_budget=-1)

    # ASSERT
    assert result.feasible is False


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_budgets_of_exactly_zero__returns_the_empty_selection(
    solver,
) -> None:
    # ARRANGE
    # Zero is the exact boundary between the infeasible negative budgets above
    # and the workable positive ones below: selecting nothing costs nothing, so
    # it still fits, but no item with a positive cost can be added to it. This
    # is tested separately precisely because it is the value where the answer
    # changes character.
    item_t = Item(name="T", cost=1, volume=1, calories=10, max_quantity=2)

    # ACT
    result = solver.solve([item_t], cost_budget=0, volume_budget=0)

    # ASSERT
    assert result.feasible is True
    assert result.quantities == {"T": 0}
    assert result.total_calories == pytest.approx(0, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_an_item_that_may_not_be_taken__ignores_it(solver) -> None:
    # ARRANGE
    # item_u would dominate every alternative on calories alone, and both
    # budgets could afford it, but its maximum quantity is zero. A solver that
    # treated max_quantity as advisory rather than binding would take it.
    item_u = Item(name="U", cost=1, volume=1, calories=100, max_quantity=0)
    item_v = Item(name="V", cost=1, volume=1, calories=5, max_quantity=1)

    # ACT
    result = solver.solve([item_u, item_v], cost_budget=2, volume_budget=2)

    # ASSERT
    assert result.quantities == {"U": 0, "V": 1}
    assert result.total_calories == pytest.approx(5, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_no_item_individually_affordable__returns_the_empty_selection(
    solver,
) -> None:
    # ARRANGE
    # item_c exceeds the cost budget on its own; item_d exceeds the volume
    # budget on its own. Neither can ever appear in a feasible selection.
    item_c = Item(name="C", cost=5, volume=1, calories=100, max_quantity=3)
    item_d = Item(name="D", cost=1, volume=5, calories=50, max_quantity=2)

    # ACT
    result = solver.solve([item_c, item_d], cost_budget=1, volume_budget=1)

    # ASSERT
    assert result.feasible is True
    assert result.quantities == {"C": 0, "D": 0}
    assert result.total_calories == pytest.approx(0, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_unique_optimum__returns_the_dominant_item(solver) -> None:
    # ARRANGE
    # Both items fit individually, but together they exceed the cost budget,
    # and item_a has strictly more calories per unit of budget than item_b.
    item_a = Item(name="A", cost=2, volume=1, calories=10, max_quantity=1)
    item_b = Item(name="B", cost=1, volume=2, calories=6, max_quantity=1)

    # ACT
    result = solver.solve([item_a, item_b], cost_budget=2, volume_budget=2)

    # ASSERT
    assert result.quantities == {"A": 1, "B": 0}
    assert result.total_calories == pytest.approx(10, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_only_cost_constrains_the_optimum__leaves_volume_slack(
    solver,
) -> None:
    # ARRANGE
    # item_n and item_o together exceed the cost budget, so the optimal
    # selection is item_n alone: it exactly exhausts the cost budget while
    # using only a fraction of the volume budget.
    item_n = Item(name="N", cost=2, volume=1, calories=10, max_quantity=1)
    item_o = Item(name="O", cost=1, volume=1, calories=3, max_quantity=1)

    # ACT
    result = solver.solve([item_n, item_o], cost_budget=2, volume_budget=5)

    # ASSERT
    assert result.total_cost == pytest.approx(2, rel=1e-8)
    assert result.total_volume < 5


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_only_volume_constrains_the_optimum__leaves_cost_slack(
    solver,
) -> None:
    # ARRANGE
    # item_p and item_q together exceed the volume budget, so the optimal
    # selection is item_p alone: it exactly exhausts the volume budget while
    # using only a fraction of the cost budget.
    item_p = Item(name="P", cost=1, volume=2, calories=10, max_quantity=1)
    item_q = Item(name="Q", cost=1, volume=1, calories=3, max_quantity=1)

    # ACT
    result = solver.solve([item_p, item_q], cost_budget=5, volume_budget=2)

    # ASSERT
    assert result.total_volume == pytest.approx(2, rel=1e-8)
    assert result.total_cost < 5


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_both_constraints_binding__exhausts_both_budgets(solver) -> None:
    # ARRANGE
    # item_l and item_m together consume the cost budget and the volume
    # budget exactly, and no other selection reaches as many calories.
    item_l = Item(name="L", cost=2, volume=1, calories=8, max_quantity=1)
    item_m = Item(name="M", cost=1, volume=2, calories=7, max_quantity=1)

    # ACT
    result = solver.solve([item_l, item_m], cost_budget=3, volume_budget=3)

    # ASSERT
    assert result.total_cost == pytest.approx(3, rel=1e-8)
    assert result.total_volume == pytest.approx(3, rel=1e-8)
    assert result.total_calories == pytest.approx(15, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_multiple_optimal_solutions__returns_shared_optimal_calories(
    solver,
) -> None:
    # ARRANGE
    # item_e and item_f are interchangeable (same cost, volume, calories), and
    # the budget admits exactly one of them. Either alone is optimal, so this
    # test deliberately never asserts which one was picked.
    item_e = Item(name="E", cost=1, volume=1, calories=5, max_quantity=1)
    item_f = Item(name="F", cost=1, volume=1, calories=5, max_quantity=1)

    # ACT
    result = solver.solve([item_e, item_f], cost_budget=1, volume_budget=1)

    # ASSERT
    assert result.total_calories == pytest.approx(5, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_room_for_multiple_units__takes_more_than_one_of_an_item(
    solver,
) -> None:
    # ARRANGE
    # Three units of item_j (max_quantity=3) yield more calories than one unit
    # of item_k, so an optimal solver must select the same item more than
    # once rather than treating items as binary take-it-or-leave-it choices.
    item_j = Item(name="J", cost=1, volume=1, calories=5, max_quantity=3)
    item_k = Item(name="K", cost=3, volume=1, calories=10, max_quantity=1)

    # ACT
    result = solver.solve([item_j, item_k], cost_budget=3, volume_budget=3)

    # ASSERT
    assert result.quantities == {"J": 3, "K": 0}
    assert result.total_calories == pytest.approx(15, rel=1e-8)


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_one_item_individually_infeasible__excludes_only_that_item(
    solver,
) -> None:
    # ARRANGE
    # item_h exceeds the cost budget on its own, even though item_g and item_i
    # together fit comfortably and yield more calories than item_h ever could
    # within this budget.
    item_g = Item(name="G", cost=1, volume=1, calories=4, max_quantity=1)
    item_h = Item(name="H", cost=10, volume=1, calories=100, max_quantity=1)
    item_i = Item(name="I", cost=1, volume=1, calories=3, max_quantity=1)

    # ACT
    result = solver.solve([item_g, item_h, item_i], cost_budget=2, volume_budget=2)

    # ASSERT
    assert result.quantities["H"] == 0
    assert result.total_calories == pytest.approx(7, rel=1e-8)
