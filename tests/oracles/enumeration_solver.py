"""A pseudo-oracle for the cargo model: a second, independent way to find the best load.

EnumerationSolver has the same contract as Optimization.run, but no solver behind it: it tries every
candidate load and keeps the best. It is slow, so it only makes sense on small instances, but each
step can be checked by reading it. It lives with the tests because nothing in the program uses it.
"""

from __future__ import annotations

from oracles.cargo import Instance, Solution


class EnumerationSolver:
    """Finds the load with the most revenue by trying every candidate load."""

    def run(self, instance: Instance) -> Solution | None:
        """Returns the load with the most revenue, or None when no load respects both capacities.

        Same contract as Optimization.run. Product i can load at most
        m_i = floor(min(W / w_i, V / v_i)) pallets, and at least its committed pallets, so the
        candidate loads are every combination of counts between those two bounds.

        Part 1 of the exercise: implement this method. itertools.product lists every combination
        of counts; keep the feasible one with the most revenue.

        Raises:
            ValueError: if instance is None.
        """
        raise NotImplementedError("Exercise: implement me")
