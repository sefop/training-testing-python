from __future__ import annotations

import random

import pytest

from mip_single_objective import EnumerationSolver, HighsSolver, Item

SOLVERS = [EnumerationSolver(), HighsSolver()]
SOLVER_IDS = ["enumeration", "highs"]

# A base catalogue whose optimum is not obvious by inspection: the best
# selection is two units of A plus one B, worth 26 calories, and it exhausts
# both budgets exactly. None of the tests below rely on knowing that — the
# whole point of this file is that they do not need to.
BASE_ITEMS = [
    Item(name="A", cost=2, volume=1, calories=10, max_quantity=2),
    Item(name="B", cost=1, volume=2, calories=6, max_quantity=1),
    Item(name="C", cost=3, volume=1, calories=14, max_quantity=1),
]
BASE_COST_BUDGET = 5
BASE_VOLUME_BUDGET = 4


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
@pytest.mark.parametrize(
    "extra_item",
    [
        Item(name="D", cost=1, volume=1, calories=9, max_quantity=1),
        Item(name="D", cost=99, volume=99, calories=99, max_quantity=1),
    ],
    ids=["affordable", "unaffordable"],
)
def test__solve__given_an_extra_item__optimum_never_decreases(solver, extra_item) -> None:
    # Offering one more item can only ever help: any selection that was
    # available before is still available now, simply with the new item at
    # quantity zero. This holds whether or not the new item is affordable,
    # which is why both cases are checked.
    # ARRANGE
    enlarged = BASE_ITEMS + [extra_item]

    # ACT
    before = solver.solve(BASE_ITEMS, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)
    after = solver.solve(enlarged, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)

    # ASSERT
    assert after.total_calories >= before.total_calories


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
@pytest.mark.parametrize(
    "extra_cost,extra_volume", [(3, 0), (0, 3), (3, 3)], ids=["cost", "volume", "both"]
)
def test__solve__given_a_larger_budget__optimum_never_decreases(
    solver, extra_cost, extra_volume
) -> None:
    # Relaxing a constraint enlarges the feasible region, so the best
    # achievable value cannot fall. Each budget is relaxed alone and then
    # together, since a solver could plausibly mishandle one and not the other.
    # ARRANGE
    cost_budget = BASE_COST_BUDGET + extra_cost
    volume_budget = BASE_VOLUME_BUDGET + extra_volume

    # ACT
    before = solver.solve(BASE_ITEMS, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)
    after = solver.solve(BASE_ITEMS, cost_budget, volume_budget)

    # ASSERT
    assert after.total_calories >= before.total_calories


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
@pytest.mark.parametrize("factor", [2, 10, 0.5], ids=["double", "tenfold", "halve"])
def test__solve__given_all_calories_scaled__optimum_scales_by_the_same_factor(
    solver, factor
) -> None:
    # Scaling every calorie count by the same positive number rescales the
    # objective without changing which selections are feasible, so the optimal
    # value must scale by exactly that factor. The chosen selection is not
    # asserted: rescaling can turn a near-tie into a tie, and the contract
    # never promised a particular winner among equals.
    # ARRANGE
    scaled_items = [
        Item(
            name=item.name,
            cost=item.cost,
            volume=item.volume,
            calories=item.calories * factor,
            max_quantity=item.max_quantity,
        )
        for item in BASE_ITEMS
    ]

    # ACT
    original = solver.solve(BASE_ITEMS, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)
    scaled = solver.solve(scaled_items, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)

    # ASSERT
    assert scaled.total_calories == pytest.approx(
        original.total_calories * factor, rel=1e-8
    )


@pytest.mark.parametrize("solver", SOLVERS, ids=SOLVER_IDS)
def test__solve__given_an_item_capped_at_zero__matches_removing_it(solver) -> None:
    # An item that may be taken zero times at most cannot participate in any
    # selection, so it should influence the answer exactly as much as an item
    # that was never offered: not at all.
    # ARRANGE
    capped = [
        Item(
            name=item.name,
            cost=item.cost,
            volume=item.volume,
            calories=item.calories,
            max_quantity=0 if item.name == "C" else item.max_quantity,
        )
        for item in BASE_ITEMS
    ]
    removed = [item for item in BASE_ITEMS if item.name != "C"]

    # ACT
    with_cap = solver.solve(capped, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)
    without_item = solver.solve(removed, BASE_COST_BUDGET, BASE_VOLUME_BUDGET)

    # ASSERT
    # Only the calorie totals are compared. The quantity maps legitimately
    # differ: one still carries a "C" key holding zero, the other has no such
    # key at all, and the contract says nothing that forbids either.
    assert with_cap.feasible == without_item.feasible
    assert with_cap.total_calories == pytest.approx(
        without_item.total_calories, rel=1e-8
    )


def test__solve__given_randomly_generated_instances__both_solvers_agree() -> None:
    # This is model validation rather than solver validation. HiGHS is not
    # going to compute a wrong optimum; the risk is that the model built for it
    # does not say what it was meant to say — a swapped coefficient, a budget
    # applied to the wrong sum. Brute-force enumeration is obviously correct by
    # inspection, so disagreement on any instance points at the formulation.
    #
    # The seed is fixed so a failure here is reproducible; without it a red run
    # could vanish on the retry.
    # ARRANGE
    rng = random.Random(20260908)

    for _ in range(200):
        items = [
            Item(
                name=f"item_{index}",
                cost=rng.randint(0, 5),
                volume=rng.randint(0, 5),
                calories=rng.randint(0, 20),
                max_quantity=rng.randint(1, 3),
            )
            for index in range(rng.randint(1, 4))
        ]
        # Negative budgets are drawn deliberately, so the agreement being
        # checked covers instances that are infeasible as well as solvable ones.
        cost_budget = rng.randint(-1, 8)
        volume_budget = rng.randint(-1, 8)

        # ACT
        reference = EnumerationSolver().solve(items, cost_budget, volume_budget)
        candidate = HighsSolver().solve(items, cost_budget, volume_budget)

        # ASSERT
        # The failing instance is included in the message because a generated
        # input that is not reported cannot be investigated.
        instance = f"items={items}, cost_budget={cost_budget}, volume_budget={volume_budget}"
        assert reference.feasible == candidate.feasible, instance
        if reference.feasible:
            # Quantities are deliberately not compared: when several selections
            # tie for best, the contract permits the two solvers to return
            # different ones, and a test that demanded agreement there would be
            # asserting something the contract never promised.
            assert candidate.total_calories == pytest.approx(
                reference.total_calories, rel=1e-8
            ), instance
