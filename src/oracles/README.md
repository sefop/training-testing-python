# Oracles (Python)

The theory, and the three worked tests this exercise starts from, are in the training hub:
[Test oracles](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#ch-oracles).
The promises you test are listed, with example tests for each, in
[The optimization contract](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#model-contract).
This page only covers what's specific to Python.

## The starting point

- [`cargo.py`](cargo.py) is the code under test: the cargo loading model of the book, solved with
  OR-Tools. It's complete: you only write tests (and one pseudo-oracle). `Optimization().run(instance)`
  returns a `Result`: a `status` (`Status.OPTIMAL`, `FEASIBLE`, `INFEASIBLE` or `NOT_FOUND`) and, when the
  status is `OPTIMAL` or `FEASIBLE`, a `solution` holding the load. This implementation solves the model
  to proven optimality, so you will meet `OPTIMAL` when a load respects both capacities and `INFEASIBLE`
  when none does. Its docstring is the contract, with the seven promises numbered as in the book. The
  contract itself is defined in the design section, in
  [Contracts](https://github.com/sefop/sefop-training-hub/blob/main/book/04-design/README.md#ch-contracts).
- [`enumeration_solver.py`](../../tests/oracles/enumeration_solver.py) is a pseudo-oracle waiting to be
  written: a second implementation of the same contract that tries every candidate load, so it returns
  `OPTIMAL` or `INFEASIBLE` and nothing else.
- [`test_optimization.py`](../../tests/oracles/test_optimization.py) holds:
  - the book's three tests, finished, one per oracle: the two-pallet test (known oracle), the differential
    sweep (pseudo-oracle) and the capacity relation test (metamorphic relation). The sweep is skipped until
    `EnumerationSolver` exists.
  - **Part 1:** one empty test for every promise, plus the helper `assert_valid_solution`.
  - **Part 2:** one empty test for every remaining example test of the contract.

  Each empty test's docstring names the promise it checks and the oracle that fits it.

## Part 1: one test per promise

1. Write `assert_valid_solution(instance, solution)`, which takes the `solution` of a `Result`: every quantity is a whole number, every committed
   pallet is loaded, both capacities hold, and the reported revenue and totals match the load.
2. For each empty test in Part 1, write the body with the Arrange / Act / Assert layout of the finished
   tests, then delete its `@pytest.mark.skip(reason="Exercise: implement me")` line.
3. Implement `EnumerationSolver.run`. Enable the test that checks it against the known two-pallet answer,
   then delete the skip line of the differential sweep. A pseudo-oracle is only useful if you trust it, so
   check it on a known answer first.
4. Run the tests and make sure every Part 1 test passes.

## Part 2: every remaining example test

Do the same for each empty test in Part 2. The helper `three_products(...)` builds the book's three-product
instance with the capacities and commitment you choose, which most relation tests need.

## Break the code on purpose

Each step below is a bug that one kind of oracle catches. Make the change in `cargo.py`, run the tests, then
**undo the change.**

1. **Known oracle.** In `_build_model`, change `<= instance.weight_capacity` to
   `<= instance.weight_capacity - 1`, a strict `<` for whole-number weights. Your test of committed pallets
   that fill the payload exactly fails: a boundary case is where an off-by-one shows.
2. **Pseudo-oracle.** In `_build_model`, change `math.inf` to `1`, so the model treats every product as a
   0/1 choice, as a knapsack would. The worked two-pallet test still passes, because its best load holds
   one pallet. The differential sweep fails, and so do your tests whose load needs two pallets of one
   product: a hand-picked instance catches a mistake only if someone thought of it, and 200 generated ones
   need no one to.
3. **Metamorphic relation.** In `_build_model`, change `for product in instance.products:` to
   `for product in instance.products[1:]:`, so the model forgets the first product. Your reverse-order test
   fails, although it never knew the optimal revenue.

You're done when every test passes, `skipped` is 0, and the three breakages above were caught. Stuck? The
[`solutions`](https://github.com/sefop/training-testing-python/tree/solutions) branch holds every test of
this exercise finished, and `EnumerationSolver` too.

## OR-Tools in five minutes

[OR-Tools](https://developers.google.com/optimization) is Google's open-source optimization library.
`pip install -r requirements.txt` installs it with its solvers; this exercise uses SCIP, a mixed-integer
solver. You only need to read `cargo.py`, not change it, but these are the pieces it uses:

| The model | OR-Tools |
|---|---|
| a solver | `solver = pywraplp.Solver.CreateSolver("SCIP")` |
| $x_i \in \mathbb{Z}$, $x_i \ge l_i$ | `solver.IntVar(lower_bound, math.inf, name)` |
| $\sum_i w_i x_i \le W$ | `solver.Add(solver.Sum(terms) <= capacity)` |
| $\max \sum_i r_i x_i$ | `solver.Maximize(solver.Sum(terms))` |
| solve, and read what was established | `solver.Solve()` returns `OPTIMAL`, `FEASIBLE`, `INFEASIBLE` or `NOT_SOLVED` |
| the value of $x_i$ | `variable.solution_value()` |

Two things catch people out:

- **Values come back as floats.** A solver may report `1.9999999` for two pallets, so `cargo.py` rounds each
  count, and the tests compare revenues with `pytest.approx`.
- **Use `solver.Sum`, not `sum`.** On an empty list, Python's `sum` returns the number `0`, which
  `solver.Add` cannot turn into a constraint. `solver.Sum` builds an expression even then.

## Running the tests

From the root of the repository, with the virtual environment activated:

```bash
pytest tests/oracles
```

Before you start, the summary reads:

```
======================== 2 passed, 26 skipped in 0.06s =========================
```
