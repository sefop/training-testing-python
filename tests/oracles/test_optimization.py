"""Tests for Optimization.run, the cargo model, sorted by the test oracle each one uses.

A test oracle is whatever tells the test the expected behavior. Three kinds appear here:
- Known oracle: the expected answer, worked out by hand before the test runs.
- Pseudo-oracle: EnumerationSolver, a second implementation that tries every candidate load.
- Metamorphic relation: two related runs whose results must compare in a way you can prove,
  even when neither result is known.

The file has three parts:
- Worked examples: the book's three tests, one per oracle, finished. The differential sweep is
  skipped until you implement EnumerationSolver in Part 1.
- Part 1: one test for every promise of the contract (see Optimization's docstring), plus
  EnumerationSolver, which the differential sweep needs.
- Part 2: every remaining example test of the book's contract.

Test names follow test__method__given_condition__expected_outcome, so a failing test reports in
plain words which promise was broken. Revenues and totals are compared with pytest.approx, because
the model computes with floating-point numbers.
"""

import random

import pytest
from enumeration_solver import EnumerationSolver

from oracles.cargo import Instance, Optimization, Product, Solution


def assert_valid_solution(instance: Instance, solution: Solution) -> None:
    """Asserts behavior 1, a valid solution: the load is feasible and reported correctly."""
    raise NotImplementedError("Exercise: implement me")


def three_products(
    weight_capacity: float = 5, volume_capacity: float = 4, committed_c: int = 0
) -> Instance:
    """The book's instance for the relation tests: its best load is two pallets of A and one of B."""
    return Instance(
        products=[
            Product(name="A", weight=2, volume=1, revenue=10),
            Product(name="B", weight=1, volume=2, revenue=6),
            Product(name="C", weight=3, volume=1, revenue=14, committed_quantity=committed_c),
        ],
        weight_capacity=weight_capacity,
        volume_capacity=volume_capacity,
    )


# =============================================================================
# Worked examples: the book's three tests, one per oracle.
# =============================================================================


def test__run__given_the_two_pallet_instance__loads_the_higher_revenue_pallet() -> None:
    """Known oracle: the four candidate loads, listed by hand, show the best one earns 10."""
    # Arrange
    a = Product(name="A", weight=2, volume=1, revenue=10)
    b = Product(name="B", weight=1, volume=2, revenue=6)
    instance = Instance(products=[a, b], weight_capacity=2, volume_capacity=2)

    # Act
    solution = Optimization().run(instance)

    # Assert
    assert solution is not None
    assert solution.objective_value == pytest.approx(10)


@pytest.mark.skip(reason="Part 1: implement EnumerationSolver, then delete this line")
def test__run__given_random_small_instances__agrees_with_enumeration() -> None:
    """Pseudo-oracle: on 200 small random instances, run and EnumerationSolver agree."""
    rng = random.Random(20260908)

    for _ in range(200):
        # Arrange
        products = [
            Product(
                name=f"P{i}",
                weight=rng.randint(1, 5),
                volume=rng.randint(1, 5),
                revenue=rng.randint(0, 20),
                committed_quantity=rng.randint(0, 2),
            )
            for i in range(rng.randint(1, 4))
        ]
        instance = Instance(products, weight_capacity=rng.randint(0, 8), volume_capacity=rng.randint(0, 8))

        # Act
        reference = EnumerationSolver().run(instance)
        candidate = Optimization().run(instance)

        # Assert
        assert (candidate is None) == (reference is None), f"feasibility differs on {instance}"
        if reference is not None:
            assert candidate.objective_value == pytest.approx(reference.objective_value), f"on {instance}"


def test__run__given_a_higher_payload_capacity__does_not_lower_the_revenue() -> None:
    """Metamorphic relation: more payload can only keep or raise the best revenue."""
    # Arrange
    before_instance = three_products(weight_capacity=5)
    after_instance = three_products(weight_capacity=8)

    # Act
    before = Optimization().run(before_instance)
    after = Optimization().run(after_instance)

    # Assert
    assert after.objective_value >= before.objective_value


# =============================================================================
# Part 1: one test per promise, and the helper above. Write the body, then delete the skip line.
# =============================================================================


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_a_feasible_instance__returns_a_valid_solution() -> None:
    """Behavior 1, valid solution. Oracle: the constraint definition (assert_valid_solution)."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_committed_pallets_heavier_than_the_payload__returns_none() -> None:
    """Behavior 2, no solution from an empty feasible set. Oracle: known (one sum)."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_committed_pallets_that_fill_the_payload_exactly__loads_only_the_committed_pallets() -> None:
    """Behavior 3, existence & optimality, on a boundary. Oracle: known."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_the_products_in_reverse_order__earns_the_same_revenue() -> None:
    """Behavior 4, permutation invariance. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_every_revenue_multiplied_by_k__multiplies_the_revenue_by_k() -> None:
    """Behavior 5, objective changed. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_a_new_uncommitted_product__does_not_lower_the_revenue() -> None:
    """Behavior 6, feasible set expanded. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_the_first_runs_pallets_committed__earns_the_same_revenue() -> None:
    """Behavior 7, feasible set reduced, keeping the first load. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__enumeration_solver__given_the_two_pallet_instance__finds_the_known_optimum() -> None:
    """Checks the pseudo-oracle itself against a known answer before trusting it in the sweep."""
    pass


# =============================================================================
# Part 2: every remaining example test of the contract.
# =============================================================================


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_committed_pallets_bulkier_than_the_hold__returns_none() -> None:
    """Behavior 2. Oracle: known (one sum)."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_no_products__returns_an_empty_load_worth_zero() -> None:
    """Behavior 3. Oracle: known."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_no_product_fits_on_its_own__returns_an_empty_load_worth_zero() -> None:
    """Behavior 3. Oracle: known."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_one_product_that_fits_several_times__loads_as_many_pallets_as_fit() -> None:
    """Behavior 3. Oracle: known, m = floor(min(W / w, V / v)) = floor(min(7 / 2, 10 / 1)) = 3."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_an_optimum_that_fills_only_the_payload__returns_that_load() -> None:
    """Behavior 3. Oracle: known; the unique best load is two pallets of A, worth 20."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_an_optimum_that_fills_only_the_hold__returns_that_load() -> None:
    """Behavior 3. Oracle: known; the unique best load is two pallets of A, worth 20."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_an_optimum_that_fills_both_capacities__returns_that_load() -> None:
    """Behavior 3. Oracle: known; the unique best load is one A and two B, worth 22."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_two_tied_pallets_that_do_not_fit_together__earns_the_tied_revenue() -> None:
    """Behavior 3. Oracle: known. Either pallet is optimal, so assert the revenue, never picked."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_an_uncommitted_product_too_heavy_to_fly__leaves_it_behind() -> None:
    """Behavior 3. Oracle: known; the rest of the load is the two-pallet answer, one A."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_one_revenue_raised__does_not_lower_the_revenue() -> None:
    """Behavior 5. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_several_revenues_raised__does_not_lower_the_revenue() -> None:
    """Behavior 5. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_a_higher_hold_capacity__does_not_lower_the_revenue() -> None:
    """Behavior 6. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_a_committed_pallet_released__does_not_lower_the_revenue() -> None:
    """Behavior 6. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_a_lower_payload_capacity__does_not_raise_the_revenue() -> None:
    """Behavior 7. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_a_lower_hold_capacity__does_not_raise_the_revenue() -> None:
    """Behavior 7. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_an_uncommitted_product_removed__does_not_raise_the_revenue() -> None:
    """Behavior 7. Oracle: metamorphic relation."""
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__run__given_one_more_committed_pallet__does_not_raise_the_revenue() -> None:
    """Behavior 7. Oracle: metamorphic relation."""
    pass
