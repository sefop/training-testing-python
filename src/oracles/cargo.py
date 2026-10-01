"""The cargo loading model: how many pallets of each product to load on a cargo flight.

This is the running example of the book, in its "unlimited tender" variant: the shipper tenders as
many pallets of each product as the aircraft takes, so only the two capacities limit the load.
Every pallet has a positive weight and volume, and a revenue of zero or more. Some pallets are
committed: they must fly.

The model sits behind one class, Optimization, with a single public method, run. Everything run
does to find the load (building the model, calling the solver, reading the answer back) is an
implementation detail: the tests check only what run promises.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

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
    """The load that run found.

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


class Optimization:
    """Finds the load of a flight that earns the most revenue.

    Contract of run, as in the book's chapter "Testing an optimization model":

    Software promises:
    - run raises a ValueError when instance is None.
    - otherwise run returns a Solution, or None when it could not provide a feasible solution.

    Mathematical promises, with z the objective value of a returned Solution:
    1. Valid solution: every quantity is a whole number of pallets, every committed pallet is
       loaded, both capacities are respected, and the reported revenue and totals match the load.
    2. No solution from an empty feasible set: if no load respects both capacities, run returns
       None.
    3. Existence & optimality: if a feasible load exists, run returns one with the optimal revenue.
    4. Permutation invariance: listing the products in another order leaves z unchanged.
    5. Objective changed, feasible set unchanged: multiplying every revenue by k > 0 multiplies z by
       k; raising revenues never lowers z.
    6. Feasible set expanded: z never falls when the set of feasible loads grows.
    7. Feasible set reduced: z never rises when the set of feasible loads shrinks, and stays the
       same when the first load is still feasible.
    """

    def run(self, instance: Instance) -> Solution | None:
        """Returns the load with the most revenue, or None when no load respects both capacities.

        Args:
            instance: the flight to load; must not be None.

        Raises:
            ValueError: if instance is None.
        """
        if instance is None:
            raise ValueError("instance must not be None")
        solver = pywraplp.Solver.CreateSolver("SCIP")
        pallets = self._build_model(solver, instance)
        status = solver.Solve()
        if status != pywraplp.Solver.OPTIMAL:
            return None
        return self._assemble_solution(instance, pallets)

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
