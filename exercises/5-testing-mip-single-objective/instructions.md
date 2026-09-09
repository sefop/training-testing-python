# Testing a single-objective MIP

## Introduction

Testing a calculator — the canonical example on [Wikipedia's unit testing page](https://en.wikipedia.org/wiki/Unit_testing)
— is straightforward: for any input, you can compute the expected output by hand, run the code, and compare the
two. `add(2, 3)` should return `5`, and you know that independently of the code under test.

Testing a MIP solver does not offer that shortcut. The difficulty has a name in the software testing literature:
the [oracle problem](https://en.wikipedia.org/wiki/Test_oracle), surveyed in depth in
[Barr et al., "The Oracle Problem in Software Testing: A Survey," IEEE TSE 2015](https://ieeexplore.ieee.org/document/6963470).
A test oracle is whatever mechanism decides if a given output is correct. For a calculator, the oracle is
arithmetic you already know. For a MIP, computing the true optimal solution independently of the solver usually
means solving the same NP-hard problem the solver exists to solve in the first place — so there is often no cheap,
independent oracle to compare against.

So, should a MIP be tested at all? Yes: it is software, and testing remains a crucial part of building
maintainable, efficient software, whether or not the oracle problem makes it harder to do. This guide proposes one
way to do it despite that difficulty.

Solvers end up as the least-tested part of an optimization pipeline as a result. And when they are tested, the
tests often end up coupled to one specific algorithm anyway, so replacing that algorithm breaks tests that never
should have broken. This guide shows one way around both problems, using a knapsack problem as the worked example.

## The Knapsack Problem

The example is a knapsack. A catalogue of items, each with a cost, a volume, and a calorie count. Each item can be
taken more than once, up to a maximum quantity. The task: choose how many units of each item to take so that total
calories is maximized, subject to a cost budget and a volume budget.

The formulation is as follows: let $I$ be the set of items. For each item $i \in I$, let $c_i$ be its cost, $v_i$
its volume, and $k_i$ its calorie count, all fixed parameters of the problem instance. Let $u_i$ be its maximum
quantity, $C$ the cost budget, and $V$ the volume budget.

The decision variable $x_i$ is the quantity of item $i$ selected: one non-negative integer per item, bounded above
by $u_i$.

$$
\begin{aligned}
\max_{x} \quad & \sum_{i \in I} k_i x_i \\
\text{s.t.} \quad & \sum_{i \in I} c_i x_i \le C \\
& \sum_{i \in I} v_i x_i \le V \\
& 0 \le x_i \le u_i, \quad x_i \in \mathbb{Z}, \quad \forall i \in I
\end{aligned}
$$

Three components define this as a MIP: a linear objective, linear constraints, and integer decision variables.
"Mixed" refers to the general class allowing both integer and continuous variables — this particular instance has
no continuous variables, so it is fully integer, a special case of a MIP rather than a counterexample to the name.

The feasible region defined by these constraints can be empty. If $C < 0$, for instance, no $x$ satisfies
$\sum_i c_i x_i \le C$, not even $x = 0$, since costs are non-negative — the instance has no solution at all,
optimal or otherwise. A correct solver must recognize this and report it, rather than returning any $x$.

### An example instance

Two items make the formulation concrete. The parameters:

| Item $i$ | Cost $c_i$ | Volume $v_i$ | Calories $k_i$ | Max quantity $u_i$ |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 2 | 1 | 10 | 1 |
| 2 | 1 | 2 | 6 | 1 |

with a cost budget $C = 2$ and a volume budget $V = 2$. Substituting these values into the general formulation above
gives:

$$
\begin{aligned}
\max_{x} \quad & 10 x_1 + 6 x_2 \\
\text{s.t.} \quad & 2 x_1 + x_2 \le 2 \\
& x_1 + 2 x_2 \le 2 \\
& 0 \le x_1 \le 1, \quad 0 \le x_2 \le 1, \quad x_1, x_2 \in \mathbb{Z}
\end{aligned}
$$

Taking both items ($x_1 = x_2 = 1$) costs $2(1) + 1(1) = 3$, which exceeds $C$, so that selection is infeasible.
Item 1 alone ($x_1 = 1$, $x_2 = 0$) respects both budgets and reaches 10 calories; item 2 alone reaches only 6. The
optimal solution is therefore $x_1 = 1$, $x_2 = 0$ — exactly the instance situation 1 in the taxonomy below tests.

## Circumventing the oracle problem

The Introduction named the problem: computing the true optimal solution independently of the solver usually means
solving the same NP-hard problem the solver exists to solve, so there is rarely a cheap oracle to check against.
This guide sidesteps that problem rather than solving it, through two simplifications.

First, every situation in the taxonomy below is a small, hand-solvable instance — like the example above, with a
handful of items and small budgets. At that size, a human can enumerate every possible selection and identify the
best one directly, exactly as the example instance was solved by hand two paragraphs up. The oracle here is not
automated: it is a person working out the answer once, in advance, for a deliberately small case. This does not
scale to a catalogue with thousands of items, and it is not meant to — its job is only to pin down expected
behavior for a representative slice of the input space, not to verify every instance a solver might ever face.

Second, every situation assumes optimality is achievable and checks for it exactly. `KnapsackSolver`'s contract, as
written, promises the best calorie total achievable, and the tests hold every implementation strictly to that. This
is a simplification worth naming rather than leaving implicit: it works only because the reference instances here
are small enough that finding the true optimum, and confirming a solver found it too, are both tractable by hand.

That simplification does not survive contact with a solver that trades optimality for speed on purpose — the
heuristic mentioned earlier in this guide, built for a catalogue too large to search exhaustively. A heuristic
gives up the guarantee that its answer is the best one, deliberately, in exchange for finishing in reasonable time.
Testing it against "did you find the exact optimum" would fail it for doing exactly what it was designed to do.
Before moving on, it's worth thinking through on your own: if a `KnapsackSolver` implementation could not be
trusted to find the exact optimum, what would the taxonomy's assertions need to become instead?

## Why test a solver as a black box

You often do not control, and sometimes do not even know, what algorithm sits behind a function that "solves" a
problem like this one. It could be a brute-force search, a heuristic that trades optimality for speed, or a
commercial or open-source solver. That algorithm can also change over time: today a simple search is fast enough;
tomorrow the catalogue grows and someone swaps in a faster solver.

If tests assert on implementation details, a valid algorithm change makes them fail even though the behavior they
were meant to protect never regressed. The fix is to test the contract instead: does the selection respect both
budgets, is the calorie total the best achievable, does the solver return a sensible answer at the edges of the
input space. Two solvers that both honor that contract should pass the exact same tests, and neither should be
favored by how the tests are written.

This is a trade-off, not a free win. Contract-only tests catch fewer bugs at the algorithm level — they will not
tell you why a solver is wrong, only that it is. What they buy in return is a test suite that survives a solver
swap, which in a production pipeline happens more often than most test suites assume.

## Design aspects of testing

The previous section argued informally that tests should not assume anything about the algorithm behind a solver.
This section names that idea and gives it a concrete shape: the tests in this guide are written against
`KnapsackSolver`, an abstraction defined in `src/mip_single_objective.py` as an abstract base class with a single
method, `solve`.

`KnapsackSolver` makes one promise: given a catalogue of items and two budgets, find the calorie-maximizing
selection if one exists, or report that the instance is infeasible. Nothing about *how* that answer is found is
part of the promise — not the algorithm, not its running time, not any internal data structure. `EnumerationSolver`
and `HighsSolver` are two classes that keep this promise in entirely different ways, and the test suite cannot tell
them apart, because it only ever calls `solve` and checks the returned `KnapsackSolution` against the contract
above.

This separation is deliberate, not a byproduct of how the code happened to be organized. Writing the tests against
the contract first — before deciding how many concrete solvers would exist, or how each would work — forces the
contract itself to be explicit and complete: every situation in the taxonomy below is really a question about the
contract ("what does `solve` promise when nothing is affordable?", "what does it promise when a budget is
negative?"), answered once and checked against every implementation, rather than a question about one particular
algorithm's behavior.

The same discipline that produces solver-agnostic tests also produces a more modular design, for the same reason: a
class that can be tested without reference to its internals is, by construction, a class whose internals are not
leaking into its interface. Coupling tests to implementation details and coupling a design to implementation
details are two symptoms of the same underlying problem — the abstraction's boundary was drawn in the wrong place,
or not drawn deliberately at all.

## The situation taxonomy

Organize the test suite as a list of named situations — one test per class of input expected to produce distinct,
meaningful behavior. Eleven situations cover this knapsack model:

1. Unique feasible optimum. One item dominates the other; sanity-checks the basic case.
2. Nothing individually affordable. Every item exceeds a budget on its own; the correct answer is to take nothing,
   which is still a feasible selection, just one worth zero calories.
3. Multiple optimal solutions. Two interchangeable items tie for best. The test asserts the shared optimal calorie
   total and never asserts which item was picked, since either answer is correct.
4. One item individually infeasible among otherwise-feasible items. An expensive item must be excluded without the
   solver failing on the rest of the problem.
5. Optimal solution takes more than one unit of an item. Confirms quantities are genuine integer decision variables,
   not 0/1 choices in disguise.
6. Both constraints bind at once. The optimal selection exhausts the cost budget and the volume budget
   simultaneously.
7. Only the cost constraint binds. The optimal selection exhausts the cost budget and leaves volume budget unused.
8. Only the volume constraint binds. The mirror case: volume budget exhausted, cost budget with room to spare.
9. No items at all. The trivial edge case; the only possible selection is the empty one.
10. Negative cost budget. Even the empty selection costs more than a negative budget allows, so the instance itself
    is infeasible — `solve` must report that, not return an empty-but-feasible answer.
11. Negative volume budget. The mirror case of situation 10, for volume instead of cost.

Situations 2 and 10 are easy to conflate but test different things: situation 2 is feasible, with an optimal answer
of zero calories; situations 10 and 11 are infeasible outright, with no answer to report at all. `KnapsackSolver`'s
contract distinguishes them explicitly through the `feasible` field, and the taxonomy tests both sides of that
distinction on purpose.

## Proving the tests are solver-agnostic

A claim like this is easy to make and hard to verify, so the guide backs it with two independently implemented
`KnapsackSolver` subclasses, both in `src/mip_single_objective.py`:

- `EnumerationSolver` — a brute-force reference solver, plain Python, no dependency beyond the standard library.
  Its only job is to be an obviously correct oracle.
- `HighsSolver` — backed by [HiGHS](https://highs.dev/), an open-source mixed-integer solver, through its official
  Python bindings.

The trade-off between them is direct: enumeration is exponential in the number of items and exists purely as
ground truth, while HiGHS scales to real catalogues but is a dependency you have to trust.

Every situation in `tests/test_mip_single_objective.py` runs against both solvers, via `pytest.mark.parametrize`
over `[EnumerationSolver(), HighsSolver()]`. Each situation test therefore does two jobs at once: it checks the
expected behavior, and it checks that both solvers agree on it. That agreement is what you would want to confirm
before trusting either solver, or before swapping one out for a third — or, since both are ordinary
`KnapsackSolver` subclasses, before adding a third solver to this same parametrized list.

## Scope

This guide covers testing a solver's output contract for a single objective under linear integer constraints. It
does not cover multi-objective trade-offs (see the next exercise) or performance testing under large instances. An
infeasible instance here always comes from the budgets themselves (a negative `cost_budget` or `volume_budget`),
never from a malformed `Item` — this guide still does not validate item inputs, which is out of scope, same as
before.

## Try it yourself

Open `src/mip_single_objective.py` first, for the `KnapsackSolver` abstraction, its two implementations
(`EnumerationSolver`, `HighsSolver`), and the shared data model (`Item`, `KnapsackSolution`) that makes swapping
between solvers possible. Then open `tests/test_mip_single_objective.py`, where the eleven situations above become
twenty-two runnable tests.

Run:

```bash
pytest tests/test_mip_single_objective.py -v
```
