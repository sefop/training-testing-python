"""A pseudo-oracle for the cargo model: a second, independent way to find the best load.

EnumerationSolver has the same contract as Optimization.run, but no solver behind it: it tries every
candidate load and keeps the best. It is slow, so it only makes sense on small instances, but each
step can be checked by reading it. It lives with the tests because nothing in the program uses it.
"""

from __future__ import annotations

import itertools
import math

from oracles.cargo import Instance, InvalidInstance, Result, Solution, Status


class EnumerationSolver:
    """Finds the load with the most revenue by trying every candidate load."""

    def run(self, instance: Instance) -> Result:
        """Returns the load with the most revenue and the status OPTIMAL, or the status INFEASIBLE.

        Same contract as Optimization.run. Trying every candidate load is a proof, so the status is
        OPTIMAL when a load respects both capacities and INFEASIBLE when none does, and never
        FEASIBLE or NOT_FOUND. Product i can load at most
        m_i = floor(min(W / w_i, V / v_i)) pallets, and at least its committed pallets, so the
        candidate loads are every combination of counts between those two bounds.

        Raises:
            InvalidInstance: if instance is None.
        """
        if instance is None:
            raise InvalidInstance("instance must not be None")
        products = instance.products
        counts_per_product = []
        for product in products:
            most = math.floor(
                min(instance.weight_capacity / product.weight, instance.volume_capacity / product.volume)
            )
            counts_per_product.append(range(product.committed_quantity, most + 1))

        best = None
        for counts in itertools.product(*counts_per_product):
            total_weight = sum(product.weight * count for product, count in zip(products, counts))
            total_volume = sum(product.volume * count for product, count in zip(products, counts))
            if total_weight > instance.weight_capacity or total_volume > instance.volume_capacity:
                continue
            revenue = sum(product.revenue * count for product, count in zip(products, counts))
            if best is None or revenue > best.objective_value:
                best = Solution(
                    picked={product.name: count for product, count in zip(products, counts)},
                    objective_value=revenue,
                    total_weight=total_weight,
                    total_volume=total_volume,
                )
        if best is None:
            return Result(Status.INFEASIBLE)
        return Result(Status.OPTIMAL, best)
