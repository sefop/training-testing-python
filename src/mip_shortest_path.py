# This import makes all type annotations in this file lazy strings that are
# never evaluated at runtime. This lets us use the modern `X | Y` union syntax
# (PEP 604, Python 3.10+) without raising a TypeError on Python 3.7–3.9.
from __future__ import annotations

import abc
import heapq
from collections import deque
from dataclasses import dataclass

import highspy


@dataclass(frozen=True)
class Edge:
    """Represents one directed connection between two nodes.

    A graph is expressed as a plain list of these, rather than as an
    adjacency structure, so that a caller can describe an instance without
    committing to how any particular solver wants to traverse it.

    Two edges may share the same source and target with different costs;
    nothing here rejects that, and a correct solver must simply prefer the
    cheaper one.
    """

    source: str
    target: str
    cost: float


@dataclass(frozen=True)
class ShortestPathSolution:
    """Represents the outcome a ShortestPathSolver promises to its caller.

    When feasible is True, path lists the visited nodes in order, starting
    at the requested source and ending at the requested target, and
    total_cost is the summed cost of the cheapest such route. When
    feasible is False, no route from source to target exists, and neither
    path nor total_cost carries any meaning.
    """

    feasible: bool
    path: list[str]
    total_cost: float


class ShortestPathSolver(abc.ABC):
    """Represents the ability to find a cheapest route through a graph.

    This is the public contract every concrete solver here fulfils: given
    a set of directed edges, a source and a target, find the cheapest
    route from source to target if one exists, or report that none does.
    How that route is found is not part of the promise.

    Callers must supply non-negative edge costs. This restriction is not
    imposed by the underlying optimization model, which handles negative
    costs perfectly well; it comes from Dijkstra's algorithm, which is one
    of the implementations below. Stating the assumption here rather than
    burying it in whichever implementation happens to need it is what
    keeps the two interchangeable.
    """

    @abc.abstractmethod
    def solve(
        self, edges: list[Edge], source: str, target: str
    ) -> ShortestPathSolution:
        """Return the cheapest route from source to target, or report infeasibility.

        A route is a sequence of edges where each edge begins at the node
        the previous edge ended at, the first begins at source, and the
        last ends at target. Requesting a route from a node to itself is
        answered by the empty route, at zero cost.
        """
        raise NotImplementedError


class DijkstraSolver(ShortestPathSolver):
    """A ShortestPathSolver using Dijkstra's algorithm.

    This exists as the specialised counterpart to the general-purpose
    solver below: it exploits the structure of the shortest-path problem
    directly and never builds an optimization model at all. Two solvers
    that share a contract while sharing nothing else is what makes the
    contract worth testing on its own terms.
    """

    def solve(
        self, edges: list[Edge], source: str, target: str
    ) -> ShortestPathSolution:
        if source == target:
            return ShortestPathSolution(feasible=True, path=[source], total_cost=0.0)

        # Built once up front because the search below revisits a node's
        # outgoing edges every time that node is popped, and rescanning the
        # full edge list each time would turn a linear step into a quadratic one.
        outgoing: dict[str, list[Edge]] = {}
        for edge in edges:
            outgoing.setdefault(edge.source, []).append(edge)

        best_cost: dict[str, float] = {source: 0.0}
        previous: dict[str, str] = {}
        settled: set[str] = set()
        # Entries are (cost, node). A node can be pushed several times as
        # cheaper routes to it are discovered; rather than update entries in
        # place, which heapq does not support, stale entries are left in the
        # queue and skipped via `settled` when they surface.
        queue: list[tuple[float, str]] = [(0.0, source)]

        while queue:
            cost, node = heapq.heappop(queue)
            if node in settled:
                continue
            settled.add(node)
            if node == target:
                break

            for edge in outgoing.get(node, []):
                candidate = cost + edge.cost
                # Non-negative edge costs are what make this greedy step sound:
                # once a node is settled no cheaper route to it can appear later.
                # That assumption is stated in the base class contract.
                if candidate < best_cost.get(edge.target, float("inf")):
                    best_cost[edge.target] = candidate
                    previous[edge.target] = node
                    heapq.heappush(queue, (candidate, edge.target))

        if target not in best_cost:
            return ShortestPathSolution(feasible=False, path=[], total_cost=0.0)

        path = [target]
        while path[-1] != source:
            path.append(previous[path[-1]])
        path.reverse()

        return ShortestPathSolution(
            feasible=True, path=path, total_cost=best_cost[target]
        )


class HighsPathSolver(ShortestPathSolver):
    """A ShortestPathSolver that models the problem as a MIP and calls HiGHS.

    Same contract as DijkstraSolver, reached by an entirely different
    route: the graph is expressed as a minimum-cost flow of one unit from
    source to target, and a general-purpose solver is asked to optimize
    it. This is the formulation an operations researcher would write for a
    problem that has no specialised algorithm; shortest path is used here
    only because its answers can also be checked another way.
    """

    def solve(
        self, edges: list[Edge], source: str, target: str
    ) -> ShortestPathSolution:
        if source == target:
            return ShortestPathSolution(feasible=True, path=[source], total_cost=0.0)

        nodes = {edge.source for edge in edges} | {edge.target for edge in edges}
        # A source or target absent from every edge cannot be routed between,
        # and a model with no variables at all is a shape HiGHS is not asked
        # to reason about here.
        if not edges or source not in nodes or target not in nodes:
            return ShortestPathSolution(feasible=False, path=[], total_cost=0.0)

        model = highspy.Highs()
        # Without this, HiGHS prints solver banners to stdout on every solve,
        # which would pollute the output of any test suite built on this class.
        model.setOptionValue("output_flag", False)

        # One binary variable per edge: 1 when the route uses that edge. Held in
        # a list parallel to `edges` so a solved variable can be traced back to
        # the edge it stands for without depending on HiGHS's column ordering.
        variables = [
            model.addVariable(lb=0, ub=1, type=highspy.HighsVarType.kInteger)
            for _ in edges
        ]

        # One flow-conservation equality per node, each accumulated separately
        # and consumed by exactly one addConstr call. Reusing a highspy linear
        # expression after it has been folded into another one triggers a known
        # mutation quirk in that type, so no expression here is touched twice.
        net_flow: dict[str, object] = {node: 0 for node in nodes}
        for edge, variable in zip(edges, variables):
            net_flow[edge.source] = net_flow[edge.source] + variable
            net_flow[edge.target] = net_flow[edge.target] - variable

        for node, flow in net_flow.items():
            required = 1 if node == source else -1 if node == target else 0
            model.addConstr(flow == required)

        cost_expr = 0
        for edge, variable in zip(edges, variables):
            cost_expr = cost_expr + edge.cost * variable
        model.minimize(cost_expr)

        if model.getModelStatus() != highspy.HighsModelStatus.kOptimal:
            return ShortestPathSolution(feasible=False, path=[], total_cost=0.0)

        # round() is necessary because a binary variable can come back as
        # 0.9999999998 within solver tolerance, and an edge is either used or
        # it is not.
        chosen: dict[str, list[str]] = {}
        for edge, variable in zip(edges, variables):
            if round(model.val(variable)) == 1:
                chosen.setdefault(edge.source, []).append(edge.target)

        return ShortestPathSolution(
            feasible=True,
            path=self._trace(chosen, source, target),
            total_cost=model.getObjectiveValue(),
        )

    @staticmethod
    def _trace(chosen: dict[str, list[str]], source: str, target: str) -> list[str]:
        """Recover the ordered list of nodes from the set of chosen edges.

        Flow conservation constrains which edges may be chosen together,
        but it does not by itself put them in an order, and it permits a
        zero-cost cycle to sit alongside the route without changing the
        objective. This walks the chosen edges to produce the route the
        caller asked for.
        """
        # A breadth-first walk rather than following edges one at a time: the
        # visited set means a zero-cost cycle among the chosen edges is stepped
        # around instead of being followed forever.
        previous: dict[str, str] = {}
        visited = {source}
        frontier = deque([source])
        while frontier:
            node = frontier.popleft()
            if node == target:
                break
            for successor in chosen.get(node, []):
                if successor not in visited:
                    visited.add(successor)
                    previous[successor] = node
                    frontier.append(successor)

        path = [target]
        while path[-1] != source:
            path.append(previous[path[-1]])
        path.reverse()
        return path
