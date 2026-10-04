"""The cargo loading model: how many pallets of each product to load on a cargo flight.

This is the running example of the book: any number of pallets of each product may be loaded, so
only the two capacities limit the load. Every pallet has a positive weight and volume, and a revenue
of zero or more. Some pallets are committed: they must fly.

The model sits behind one class, Optimization, with a single public method, run. It takes an
Instance and returns a Result: a status, and a Solution when there is a load to return. Everything
run does to find the load (building the model, calling the solver, reading the answer back) is an
implementation detail: the tests check only what run promises.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from ortools.linear_solver import pywraplp


@dataclass(frozen=True)
class Product:
    """One product on the booking list.

    Attributes:
        name: identifies the product; unique within an instance.
        weight: the weight of one pallet, positive.
        volume: the volume of one pallet, positive.
        revenue: the revenue one pallet earns, zero or more.
        committed_quantity: how many pallets must fly, 0 by default.
    """

    name: str
    weight: float
    volume: float
    revenue: float
    committed_quantity: int = 0


@dataclass(frozen=True)
class Instance:
    """One flight to load.

    Attributes:
        products: the booking list.
        weight_capacity: the most weight the aircraft may carry (the payload capacity).
        volume_capacity: the most volume the hold takes (the hold capacity).
    """

    products: list[Product]
    weight_capacity: float
    volume_capacity: float


@dataclass(frozen=True)
class Solution:
    """A load.

    Attributes:
        picked: product name -> whole number of pallets, 0 when the product is left behind.
        objective_value: the revenue of the load.
        total_weight: the weight of the load.
        total_volume: the volume of the load.
    """

    picked: dict[str, int]
    objective_value: float
    total_weight: float
    total_volume: float


class Status(Enum):
    """What run established about an instance.

    OPTIMAL and INFEASIBLE are facts about the instance: they hold whichever algorithm runs and
    however long it takes. FEASIBLE and NOT_FOUND are facts about the search: more time or another
    algorithm could turn the first into OPTIMAL and the second into any other status.
    """

    OPTIMAL = "optimal"  # the solution is a feasible load, and no feasible load earns more
    FEASIBLE = "feasible"  # the solution is a feasible load; a better one may exist
    INFEASIBLE = "infeasible"  # no feasible load exists for this instance
    NOT_FOUND = "not_found"  # the search stopped with no load and no proof that none exists


@dataclass(frozen=True)
class Result:
    """What run returns.

    Attributes:
        status: what run established about the instance.
        solution: the load, when status is OPTIMAL or FEASIBLE; None otherwise.
    """

    status: Status
    solution: Solution | None = None


class InvalidInstance(ValueError):
    """Raised by run when the instance breaks what the contract requires of it."""


class Optimization:
    """Finds the load of a flight that earns the most revenue.

    Contract of run, as in the book's chapters "Contracts" (design section) and "Testing an
    optimization model" (testing section):

    Software promises:
    - run raises InvalidInstance when the instance is malformed: it is None, a weight or a volume is
      not positive, a revenue, a committed quantity or a capacity is negative, a committed quantity
      is not a whole number, or two products share a name.
    - otherwise run returns a Result, which carries a Solution exactly when its status is OPTIMAL or
      FEASIBLE.

    Mathematical promises of every status, with z the objective value of a returned Solution:
    1. Valid solution: whenever a Solution is returned, every quantity is a whole number of pallets,
       every committed pallet is loaded, both capacities are respected, and the reported revenue and
       totals match the load.
    2. No solution from an empty feasible set: if no load respects both capacities, no Solution is
       returned, and the status INFEASIBLE is returned only then.

    Mathematical promises of the status OPTIMAL. This implementation solves the model to proven
    optimality, so it returns OPTIMAL on every instance that has a feasible load, and INFEASIBLE on
    every other one:
    3. Existence & optimality: if a feasible load exists, run returns one with the optimal revenue.
    4. Permutation invariance: listing the products in another order leaves z unchanged.
    5. Objective changed, feasible set unchanged: multiplying every revenue by k > 0 multiplies z by
       k; raising revenues never lowers z.
    6. Feasible set expanded: z never falls when the set of feasible loads grows.
    7. Feasible set reduced: z never rises when the set of feasible loads shrinks, and stays the
       same when the first load is still feasible.
    """

    def run(self, instance: Instance) -> Result:
        """Returns the load with the most revenue, with a status saying what was established.

        Args:
            instance: the flight to load.

        Raises:
            InvalidInstance: if the instance is malformed.
            RuntimeError: if the solver fails; a failure is an error, never a status.
        """
        self._check_instance(instance)
        solver = pywraplp.Solver.CreateSolver("SCIP")
        pallets = self._build_model(solver, instance)
        solver_status = solver.Solve()
        if solver_status == pywraplp.Solver.OPTIMAL:
            return Result(Status.OPTIMAL, self._assemble_solution(instance, pallets))
        if solver_status == pywraplp.Solver.FEASIBLE:
            return Result(Status.FEASIBLE, self._assemble_solution(instance, pallets))
        if solver_status == pywraplp.Solver.INFEASIBLE:
            return Result(Status.INFEASIBLE)
        if solver_status == pywraplp.Solver.NOT_SOLVED:
            return Result(Status.NOT_FOUND)
        raise RuntimeError(f"the solver failed with status {solver_status}")

    def _check_instance(self, instance: Instance) -> None:
        """Raises InvalidInstance unless the instance respects what the contract requires."""
        if instance is None:
            raise InvalidInstance("instance must not be None")
        if instance.weight_capacity < 0 or instance.volume_capacity < 0:
            raise InvalidInstance("capacities must not be negative")
        names = [product.name for product in instance.products]
        if len(names) != len(set(names)):
            raise InvalidInstance("product names must be unique")
        for product in instance.products:
            if product.weight <= 0 or product.volume <= 0:
                raise InvalidInstance(f"{product.name}: weight and volume must be positive")
            if product.revenue < 0:
                raise InvalidInstance(f"{product.name}: revenue must not be negative")
            committed = product.committed_quantity
            if committed < 0 or committed != int(committed):
                raise InvalidInstance(f"{product.name}: committed quantity must be a whole number, zero or more")

    def _build_model(self, solver: pywraplp.Solver, instance: Instance) -> dict[str, pywraplp.Variable]:
        """Adds one integer variable per product, the two capacity constraints and the objective."""
        pallets = {}
        weight, volume, revenue = [], [], []
        for product in instance.products:
            # The committed pallets are the variable's lower bound: they must fly.
            count = solver.IntVar(product.committed_quantity, math.inf, product.name)
            pallets[product.name] = count
            weight.append(product.weight * count)
            volume.append(product.volume * count)
            revenue.append(product.revenue * count)

        # solver.Sum, unlike Python's sum, still builds an expression when there are no products.
        solver.Add(solver.Sum(weight) <= instance.weight_capacity)
        solver.Add(solver.Sum(volume) <= instance.volume_capacity)
        solver.Maximize(solver.Sum(revenue))
        return pallets

    def _assemble_solution(self, instance: Instance, pallets: dict[str, pywraplp.Variable]) -> Solution:
        """Reads the pallets back from the solver and computes the load's revenue and totals."""
        # The solver returns floating-point values such as 1.9999999: round them to whole pallets.
        picked = {name: round(variable.solution_value()) for name, variable in pallets.items()}
        by_name = {product.name: product for product in instance.products}
        return Solution(
            picked=picked,
            objective_value=sum(by_name[name].revenue * count for name, count in picked.items()),
            total_weight=sum(by_name[name].weight * count for name, count in picked.items()),
            total_volume=sum(by_name[name].volume * count for name, count in picked.items()),
        )
