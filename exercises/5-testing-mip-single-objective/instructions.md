# Testing a single-objective MIP

## Introduction

Testing a calculator — the canonical example on [Wikipedia's unit testing page](https://en.wikipedia.org/wiki/Unit_testing)
— is straightforward: for any input, you can compute the expected output by hand, run the code, and compare the
two. `add(2, 3)` should return `5`, and you know that independently of the code under test.

Testing a MIP solver does not offer that shortcut. The difficulty has a name in the software testing literature:
the [oracle problem](https://en.wikipedia.org/wiki/Test_oracle), surveyed in
[Barr et al., "The Oracle Problem in Software Testing: A Survey," IEEE TSE 2015](https://ieeexplore.ieee.org/document/6963470).
A test oracle is whatever mechanism decides whether a given output is correct. For a calculator, the oracle is
arithmetic you already know. For a MIP, computing the true optimal solution independently of the solver generally
means solving the same problem the solver exists to solve.

That claim deserves a caveat, because the example in this guide does not fully honour it. Knapsack is only *weakly*
NP-hard: a pseudo-polynomial dynamic program solves it exactly, so a cheap independent oracle does exist for this
particular problem. The oracle problem bites hardest on general MIPs, where no such shortcut is available. Knapsack
is used here because it is small enough to reason about by hand, not because it is the hardest case available.

So, should a MIP be tested at all? Yes: it is software, and testing remains a crucial part of building maintainable,
efficient software. The oracle problem is a reason to choose the technique deliberately, not a reason to skip the
exercise.

There is a second problem, discussed less often than the first. When solvers do get tested, the tests are frequently
written against one particular algorithm, so replacing that algorithm breaks tests that were never about the
algorithm in the first place. This guide addresses both problems with a knapsack problem as the worked example, and
then hands you a second problem — shortest path — left deliberately untested, to work through on your own.

## The Knapsack Problem

The example is a knapsack. A catalogue of items, each with a cost, a volume, and a calorie count. Each item can be
taken more than once, up to a maximum quantity. The task: choose how many units of each item to take so that total
calories is maximized, subject to a cost budget and a volume budget.

The formulation is as follows: let $I$ be the set of items. For each item $i \in I$, let $c_i$ be its cost, $v_i$
its volume, and $k_i$ its calorie count, all fixed, **non-negative** parameters of the problem instance. Let $u_i$
be its maximum quantity, $C$ the cost budget, and $V$ the volume budget.

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

The feasible region defined by these constraints can be empty. If $C < 0$, no $x$ satisfies $\sum_i c_i x_i \le C$,
not even $x = 0$ — this is where the non-negativity of $c_i$ matters, since it puts every attainable total cost at
zero or above. The instance then has no solution at all, optimal or otherwise, and a correct solver must recognize
this and report it rather than returning some $x$ anyway.

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
optimal solution is therefore $x_1 = 1$, $x_2 = 0$ — exactly the instance situation 7 in the taxonomy below tests.

Work through that paragraph once more before moving on, because it is the whole method in miniature: a person,
enumerating a handful of candidate selections by hand, arriving at an answer nobody needed a solver to produce.

## The abstraction under test

You often do not control, and sometimes do not even know, which algorithm sits behind a function that "solves" a
problem like this one. It could be a brute-force search, a heuristic that trades optimality for speed, or a
commercial or open-source solver. That choice also changes over time: today a simple search is fast enough;
tomorrow the catalogue grows and someone swaps in something faster.

If tests assert on implementation details, a legitimate change of algorithm makes them fail even though the
behavior they were meant to protect never regressed. The alternative is to test the contract: does the selection
respect both budgets, is the calorie total the best achievable, does the solver return a sensible answer at the
edges of the input space. Two solvers that both honour that contract should pass the same tests, and neither should
be favoured by the way the tests are written.

In this guide that contract has a name and a location. `KnapsackSolver`, in `src/mip_single_objective.py`, is an
abstract base class with a single method, `solve`. It makes one promise: given a catalogue of items and two
budgets, find the calorie-maximizing selection if one exists, or report that the instance is infeasible. Nothing
about *how* the answer is found forms part of that promise — not the algorithm, not its running time, not any
internal data structure. `EnumerationSolver` and `HighsSolver` keep the promise in entirely different ways, and the
test suite cannot tell them apart, because it only ever calls `solve` and inspects the returned `KnapsackSolution`.

The separation is deliberate rather than a byproduct of how the code happened to be organized. Writing tests
against the contract first — before deciding how many solvers would exist, or how each would work — forces the
contract itself to be explicit: each situation in the taxonomy below is really a question about the contract
("what does `solve` promise when nothing is affordable?"), answered once and checked against every implementation.

The same discipline produces a more modular design, for the same underlying reason. A class that can be tested
without reference to its internals is, by construction, a class whose internals are not leaking into its interface.
Coupling tests to implementation details and coupling a design to implementation details are two symptoms of one
problem: the abstraction's boundary was drawn in the wrong place, or was never drawn deliberately at all.

This is a trade-off rather than a free win. Contract-only tests catch fewer bugs at the algorithm level — they tell
you that a solver is wrong, not why. What they buy in exchange is a suite that survives a solver swap, which in a
production pipeline happens more often than most test suites assume.

## Part 1 — Oracles you can write by hand

Barr et al. group the responses to the oracle problem into four families. This guide uses three of them, and gets
the fourth for free:

- A **specified oracle** states the expected answer in advance. That is Part 1, below.
- A **derived oracle** checks a relation between runs rather than an absolute answer. Part 2.
- A **pseudo-oracle** is a second, independent implementation to compare against. Part 2.
- An **implicit oracle** catches what is wrong in any program at all — a crash, a hang, a corrupted result. Every
  test here carries one for free, because a solver that raises an exception fails regardless of what was asserted.

Part 1's oracle is a person. Every situation below is a small instance — a handful of items, small budgets — where
a human can enumerate the possible selections and identify the best one directly, exactly as the example instance
was solved a few paragraphs ago. This does not scale to a catalogue of thousands of items, and it is not meant to.
Its job is to pin down expected behavior across a representative slice of the input space.

Two simplifications are worth naming rather than leaving implicit. The instances are small enough to solve by hand,
and every situation assumes optimality is achievable and checks for it exactly. Both hold here; neither holds for a
solver that deliberately trades optimality for speed, which is discussed at the end of this guide.

Choosing which instances to write is not guesswork. Each row below is an equivalence class of inputs expected to
produce distinct behavior, and several rows sit deliberately on a boundary between two such classes — the standard
techniques are called *equivalence partitioning* and *boundary value analysis*. The rows are ordered from simplest
to most involved, roughly by how many items are in play and how much reasoning the expected answer takes.

| # | Characteristic | Expected behavior |
|:---:|---|---|
| 1 | No items at all | The trivial edge case: nothing to pick, so no item is chosen and the answer is a zero-calorie solution. |
| 2 | Negative cost budget | Even the empty selection violates a negative budget, so the instance is infeasible and must be reported as such. |
| 3 | Negative volume budget | The mirror case of situation 2, for volume instead of cost. |
| 4 | Budgets of exactly zero | The boundary between situations 2 and 5: the empty selection still fits, but nothing can be added to it. |
| 5 | An item that may not be taken | An item with a maximum quantity of zero is ignored, however attractive its calories would otherwise make it. |
| 6 | Nothing individually affordable | Every item exceeds a budget on its own; taking nothing is still feasible, worth zero calories. |
| 7 | Unique feasible optimum | One item dominates the other; sanity-checks the basic case. |
| 8 | Only the cost constraint binds | The optimal selection exhausts the cost budget and leaves volume budget unused. |
| 9 | Only the volume constraint binds | The mirror case: volume budget exhausted, cost budget with room to spare. |
| 10 | Both constraints bind at once | The optimal selection exhausts the cost budget and the volume budget simultaneously. |
| 11 | Multiple optimal solutions | Two interchangeable items tie for best; only the shared optimal calorie total is asserted, never which item was picked. |
| 12 | More than one unit of an item | Confirms quantities are genuine integer decision variables, not 0/1 choices in disguise. |
| 13 | One item individually infeasible | An expensive item is excluded without the solver failing on the rest of the problem. |

These live in `tests/test_mip_single_objective.py`, in this order, each running against both solvers: 26 tests from
13 situations. Situations 2 and 3 are the ones to read carefully against 4 and 6, since all four produce a
zero-calorie answer of some kind and only two of them are infeasible.

Note what Part 1 cannot do. Thirteen situations pin down thirteen points in an input space that is effectively
unbounded, and every one of them required a person to work out the answer first. That is the ceiling of a specified
oracle, and it is why there is a Part 2.

## Part 2 — Testing without an oracle

The techniques here share one property: none of them needs anybody to know the right answer.

**Metamorphic relations** (a derived oracle) assert a relationship between two runs rather than the outcome of
either. Four of them hold for this model, whatever the instance:

- Adding an item to the catalogue never decreases the optimal calorie total — every previously available selection
  is still available, with the new item at quantity zero.
- Raising either budget never decreases the optimal calorie total, since relaxing a constraint only enlarges the
  feasible region.
- Scaling every calorie count by a positive factor scales the optimum by exactly that factor.
- Capping an item's maximum quantity at zero gives the same optimal value as removing the item entirely.

None of these requires solving anything by hand, and none of them stops working when the catalogue grows to ten
thousand items. That is what makes them the more transferable half of Part 2.

**Differential testing** (a pseudo-oracle) runs two independent implementations on the same input and compares. It
is worth being precise about what this catches, because the obvious framing is the wrong one. HiGHS is not going to
compute a wrong optimum. What can be wrong is the *model built for it* — a coefficient attached to the wrong sum, a
budget applied to the wrong constraint, an index set that quietly drops an item. Enumeration is obviously correct by
inspection, so any disagreement points at the formulation rather than at the solver. This is the disciplined version
of the sanity check most people already run informally when they write a new model.

`tests/test_mip_single_objective_properties.py` holds both: the four relations, plus one differential test that
generates 200 random instances from a fixed seed and checks that both solvers agree. Two details in that file are
deliberate. The seed is fixed, because a randomized failure that vanishes on the retry cannot be investigated. And
the comparison is on feasibility and total calories only, never on the selected quantities — when several selections
tie for best, the contract explicitly permits the two solvers to return different ones, so demanding agreement there
would assert something never promised.

The honest limitation: differential testing works only while the reference implementation stays tractable, which is
the same small-instance regime Part 1 already occupies. It broadens coverage within that regime considerably. It
does not reach the large instances where you would most want an answer.

Try it: swap `item.cost` for `item.volume` in `HighsSolver`'s model and run both suites. Four of the thirteen
situations go red, which is reassuring, and the differential test goes red as well. The difference between them is
reliability rather than detection. Those four situations catch this particular swap because they happen to be
sensitive to it, not because anyone picked them with it in mind — a different modeling error can slip past all
thirteen hand-chosen instances while a sweep across generated ones still finds it. Deliberately breaking code to
find out whether the tests notice is the subject of its own exercise in this repository.

## Run it yourself

```bash
pytest tests/test_mip_single_objective.py -v            # 26 tests: 13 situations x 2 solvers
pytest tests/test_mip_single_objective_properties.py -v # 19 tests: 4 relations + 1 differential sweep
```

Open `src/mip_single_objective.py` alongside them, for the `KnapsackSolver` abstraction, its two implementations,
and the shared data model that makes swapping between them possible.

## Your turn — shortest path

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

One contract clause is worth reading before you start, because it is the kind of assumption this guide has been
arguing should never stay implicit: **edge costs must be non-negative**. The MIP formulation does not require that;
Dijkstra's algorithm does. It is stated in the abstraction rather than buried in the implementation that needs it,
which is precisely what makes the two interchangeable.

Write `tests/test_mip_shortest_path.py` yourself. All three techniques transfer:

1. Build a situation table first, before writing any test, exactly as in Part 1. What is the shortest-path analogue
   of "no items at all"? Of a tie? Of an item that may not be taken? Some rows carry over almost unchanged, some
   have no counterpart at all, and this problem raises at least one situation the knapsack could never produce.
2. Find the metamorphic relations. Two are worth the effort of proving to yourself first: adding an edge never
   increases the shortest distance, and raising the cost of any edge never decreases it.
3. Compare the two implementations on randomly generated graphs. If your arc-based formulation and Dijkstra
   disagree on any graph, one of them is wrong, and you will not need anyone to tell you the right answer to know it.

You have a scoreboard while you work. `src/mip_shortest_path.py` currently reports 0% coverage and drags the
repository total down to 42%, which is deliberate rather than an oversight — it is the one module here with no tests
behind it. Run `pytest --cov=src --cov-report=term-missing` and watch the number move as you go.

## What this guide does not cover

The scope is testing a solver's output contract for a single objective under linear integer constraints. Multi-
objective trade-offs belong to the next exercise. Performance and scale are not addressed anywhere here. Item inputs
are never validated: an infeasible instance in this guide always comes from the budgets, never from a malformed
item, and no solver here rejects a nonsensical catalogue.

The largest omission is deliberate and worth stating plainly. Every assertion in Part 1 assumes the solver returns a
genuinely optimal answer. That assumption fails for a heuristic — a solver that gives up the guarantee of optimality
on purpose, in exchange for finishing in reasonable time on a catalogue too large to search exhaustively. Testing
such a solver against "did you find the exact optimum" would fail it for doing exactly what it was designed to do.

So, a question to sit with rather than an answer: if a `KnapsackSolver` implementation could not be trusted to
return the optimum, which of the thirteen situations would still hold unchanged, which would need weakening, and
which would have to be thrown out? Notice that most of Part 2 survives the change untouched — that is not a
coincidence, and it is a large part of why those techniques are worth knowing.

## Further reading

This guide's strategy is neither new nor specific to MIP solvers. Robert C. Martin applies the same idea — tests
written against an algorithm's contract, ordered from degenerate cases up through progressively more complex ones —
to Dijkstra's shortest-path algorithm, in
["Search for a Path"](https://blog.cleancoder.com/uncle-bob/2016/10/26/DijkstrasAlg.html). Having just been asked to
test a shortest-path solver yourself, it makes a useful comparison: same algorithm, same underlying technique,
arrived at from a different direction.

The randomized sweep in Part 2 is hand-rolled, which keeps it readable and adds no dependency, but the industrial
version of the idea is a property-based testing library such as [Hypothesis](https://hypothesis.readthedocs.io/).
Given a failing case, it automatically shrinks it to the smallest input that still fails — which, on a randomized
test over generated instances, is most of the work.
