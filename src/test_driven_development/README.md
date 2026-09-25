# Test-driven development (Python)

The theory, and the worked example this exercise continues, are in the training hub:
[Test-driven development](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#ch-tdd).
This page only covers what's specific to Python.

## The starting point

- [`linear_expression.py`](linear_expression.py) holds `LinearExpression`, a linear expression
  a0 + a1\*x1 + ... + an\*xn. Its docstring is the full specification.
- The scalar part is already built, test-first, exactly as in the book: `LinearExpression()`,
  `LinearExpression(scalar=3.0)`, `scalar()` and `add_scalar(value)`.
- [`test_linear_expression.py`](../../tests/test_driven_development/test_linear_expression.py) holds the book's
  three tests, one per cycle.

Everything about variables is yours: construction with a term, adding a term (and accumulating it when the
variable is already there), merging two expressions, the set of variables, and the coefficient of a variable
(0.0 when it is absent). Names and parameters of the new methods are up to you.

## The steps

Repeat this cycle, one requirement of the docstring at a time:

1. **Red.** Add one test for the next requirement to `test_linear_expression.py`, under "your cycles start
   here". Run the tests and watch the new one fail. If it passes straight away, it tests nothing new: change
   the test, not the code.
2. **Green.** Write the minimum code in `linear_expression.py` that makes it pass. Hard-coding an answer is
   allowed: the next test will force the general code.
3. **Refactor.** Improve the code (names, duplication, structure) and run the tests again. They must all
   still pass.
4. **Commit.** `git commit` after each green or refactor, so the history shows one cycle per commit.

Suggested order, from simplest to hardest: an empty expression has no variables (the first test that needs a
method for the set of variables), then a single term, a scalar and a term, adding a term for a new variable,
adding a term for a variable already present, the coefficient of an absent variable, and finally merging two
expressions.

You're done when every example in the docstring has a test and every test passes.

## Running the tests

From the root of the repository, with the virtual environment activated:

```bash
pytest tests/test_driven_development
```

Add `-v` to see one line per test. Before you start, the summary reads:

```
============================== 3 passed in 0.01s ===============================
```

A red step shows up as `1 failed`. Read the failure message: it should say which requirement is missing,
which is the test's name at work.

Two Python details that come up in this exercise:

- **Compare floats with `pytest.approx`**, never with a bare `==`: `0.1 + 0.2 == 0.3` is `False`.
- **"Read-only" needs care.** If a method returns the dictionary or set the expression keeps inside,
  the caller can change it and so change the expression. The docstring forbids that: write a test that tries
  it, watch it fail, then return a copy.
