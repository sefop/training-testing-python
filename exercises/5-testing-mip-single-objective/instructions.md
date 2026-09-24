# Testing a single-objective MIP

The theory behind this exercise lives in the SEFOP book:
[Part 01 — Testing optimization models](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/README.md).
This file is the hands-on half. Its sections follow the chapters in order, and each one names the chapter to read
first.

Everything here uses two source files:

- `src/mip_single_objective.py` — the knapsack contract (`Item`, `KnapsackSolution`, `KnapsackSolver`) and two
  implementations that keep it by entirely different means: `EnumerationSolver` and `HighsSolver`.
- `src/mip_shortest_path.py` — a shortest-path solver with no tests at all, for the final exercise.

## Setup

> Read first: [01 — Why optimization models are hard to test](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/01-why-optimization-models-are-hard-to-test.md)

Install the repository as described in the [README](../../README.md), then run both suites:

```bash
pytest tests/test_mip_single_objective.py -v            # 26 tests: 13 situations x 2 solvers
pytest tests/test_mip_single_objective_properties.py -v # 19 tests: 4 relations + 1 differential sweep
```

Both should pass. The two-item instance that chapter 01 solves by hand is in `tests/test_mip_single_objective.py` as
`test__solve__given_unique_optimum__returns_the_dominant_item` — same items A and B, same budgets, same answer.

## Practice: the contract

> Read first: [02 — Test the contract, not the algorithm](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/02-test-the-contract-not-the-algorithm.md)

1. Open `src/mip_single_objective.py` and read the docstrings of `KnapsackSolver` and `KnapsackSolution`. That is the
   contract from chapter 02, written where the code lives: what `solve` promises, what the fields mean when the
   instance is infeasible, and nothing about how the answer is found.
2. Compare `EnumerationSolver.solve` with `HighsSolver.solve`. One loops over every combination; the other builds a
   model for HiGHS. Both keep the same promise.
3. Open `tests/test_mip_single_objective.py`. Every test is parametrized over
   `SOLVERS = [EnumerationSolver(), HighsSolver()]` and only ever calls `solve` and inspects the returned
   `KnapsackSolution`. Look for an assertion that would break if you added a third solver that keeps the contract.
   There should be none.

## Practice: situation tables

> Read first: [03 — Oracles you write by hand](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/03-oracles-you-write-by-hand.md)

`tests/test_mip_single_objective.py` implements the thirteen-situation table from chapter 03, in the same order, each
situation running against both solvers. Read the table and the file side by side.

Situations 2 and 3 are the ones to read carefully against 4 and 6: all four produce a zero-calorie answer of some kind,
and only two of them are infeasible.

## Practice: metamorphic relations

> Read first: [04 — Metamorphic relations](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/04-metamorphic-relations.md)

The first four tests in `tests/test_mip_single_objective_properties.py` are the four relations from chapter 04, all
applied to the same `BASE_ITEMS` catalogue. Its optimum happens to be 26 calories, and no test relies on knowing that.

Notice how each relation is parametrized: an extra item that is affordable and one that is not; the cost budget, the
volume budget, and both raised; calories doubled, multiplied by ten, and halved. Each variation targets a way a solver
could plausibly get one case right and another wrong.

## Practice: differential testing

> Read first: [05 — Differential testing](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/05-differential-testing.md)

The last test in `tests/test_mip_single_objective_properties.py` generates 200 random instances from the fixed seed
`20260908` and checks that `EnumerationSolver` and `HighsSolver` agree on feasibility and total calories, never on the
selected quantities. The failing instance is included in the assertion message, so a red run can be investigated.

Try it: swap `item.cost` for `item.volume` in `HighsSolver`'s model and run both suites. Four of the thirteen
situations go red, which is reassuring, and the differential test goes red as well. The difference between them is
reliability rather than detection. Those four situations catch this particular swap because they happen to be
sensitive to it, not because anyone picked them with it in mind — a different modeling error can slip past all
thirteen hand-chosen instances while a sweep across generated ones still finds it. Undo the swap when you are done.
Deliberately breaking code to find out whether the tests notice is the subject of
[exercise 3, mutation testing](../3-mutation-testing/instructions.md).

## Your turn: shortest path

> Read first: chapters [03](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/03-oracles-you-write-by-hand.md), [04](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/04-metamorphic-relations.md), and [05](https://github.com/sefop/sefop-training-hub/blob/main/book/01-testing-optimization-models/05-differential-testing.md)

`src/mip_shortest_path.py` ships with **no tests at all**. That is the exercise.

It contains the same shape you have just read: an `Edge` and a `ShortestPathSolution`, a `ShortestPathSolver`
abstraction promising the cheapest route from a source to a target — or a report that no route exists — and two
implementations that keep that promise by entirely different means. `DijkstraSolver` runs the classical
shortest-path algorithm. `HighsPathSolver` expresses the same problem as a MIP, with one binary variable per edge,
flow-conservation equalities at every node, and total cost minimized, then hands it to HiGHS.

The problem is a better exercise than the knapsack in two respects. Infeasibility is honest: no route from source to
target is a real, ordinary situation, where the knapsack needed a contrived negative budget to produce one. And the
constraints are equalities rather than budget inequalities, so the technique is visibly not tied to the one
constraint shape you have just seen.

One contract clause is worth reading before you start, because it is the kind of assumption chapter 02 argues should
never stay implicit: **edge costs must be non-negative**. The MIP formulation does not require that; Dijkstra's
algorithm does. It is stated in the abstraction rather than buried in the implementation that needs it, which is
precisely what makes the two interchangeable.

Write `tests/test_mip_shortest_path.py` yourself. All three techniques transfer:

1. **Build a situation table first** (chapter 03), before writing any test. What is the shortest-path analogue of "no
   items at all"? Of a tie? Of an item that may not be taken? Some rows carry over almost unchanged, some have no
   counterpart at all, and this problem raises at least one situation the knapsack could never produce.
2. **Find the metamorphic relations** (chapter 04). Two are worth the effort of proving to yourself first: adding an
   edge never increases the shortest distance, and raising the cost of any edge never decreases it.
3. **Compare the two implementations on randomly generated graphs** (chapter 05). If your arc-based formulation and
   Dijkstra disagree on any graph, one of them is wrong, and you will not need anyone to tell you the right answer to
   know it.

You have a scoreboard while you work. `src/mip_shortest_path.py` currently reports 0% coverage and drags the
repository total down to 42%, which is deliberate rather than an oversight — it is the one module here with no tests
behind it. Run `pytest --cov=src --cov-report=term-missing` and watch the number move as you go.

## Further reading

Robert C. Martin applies the same strategy — tests written against an algorithm's contract, ordered from degenerate
cases up through progressively more complex ones — to Dijkstra's shortest-path algorithm, in
["Search for a Path"](https://blog.cleancoder.com/uncle-bob/2016/10/26/DijkstrasAlg.html). Having just been asked to
test a shortest-path solver yourself, it makes a useful comparison.

The randomized sweep is hand-rolled, which keeps it readable and adds no dependency, but the industrial version of the
idea is a property-based testing library such as [Hypothesis](https://hypothesis.readthedocs.io/). Given a failing
case, it automatically shrinks it to the smallest input that still fails.
