# Exercise: Unit Testing

## What is a unit test?

A unit test is a small, isolated experiment that checks whether a single function
behaves correctly under a specific condition. Think of it as a controlled experiment:
you fix the inputs (the "treatment"), run the function (the "observation"), and verify
the output matches your prediction (the "hypothesis"). Just as a good experiment
tests one thing at a time, a good unit test targets one scenario per function call.

---

## The AAA pattern

Every test in this repo follows the same three-phase structure:

| Phase | Purpose |
|-------|---------|
| **Arrange** | Set up everything the function needs: create objects, define input values. |
| **Act** | Call the function under test — exactly once, with the arranged inputs. |
| **Assert** | Verify the result or side effect matches what you expected. |

Keeping these phases visually separate makes tests easy to read and diagnose.

---

## Test naming convention

Test function names follow this pattern:

```
test__<unit>__given_<context>__<expected outcome>
```

Examples:
- `test__divide__given_two_valid_numbers__returns_their_quotient`
- `test__divide__given_zero_divisor__raises_zero_division_error`

The double underscores act as separators between the three parts, making the name
readable as a plain-English sentence: *"test divide: given a zero divisor, raises
ZeroDivisionError."* When a test fails, pytest prints its name — a descriptive name
tells you exactly what broke without reading the code.

---

## What is code coverage?

Code coverage measures what percentage of your source code is actually executed
when the tests run. A line that is never reached by any test is invisible to your
test suite — bugs hiding there will not be caught.

**100% coverage on `Calculator.divide()` means every line and every branch inside
that function was exercised at least once.** It does not guarantee correctness, but
it does guarantee that no code path was left untested.

To check coverage after writing your tests:

```bash
pytest -v tests/test_calculator.py --cov=src --cov-report=term-missing
```

The `Missing` column in the output lists line numbers that were never reached.
Your goal is an empty `Missing` column for `calculator.py`.

---

## The exercise

Open `tests/test_calculator.py`. The first section contains the complete tests for
`Calculator.add()` — read them carefully, they are your worked example. The second
section contains six empty stubs for `Calculator.divide()`.

Your task is to fill in each stub so that:

1. All six divide tests **pass** (`pytest` reports no failures).
2. The coverage report shows **100%** for `calculator.py`.

Read the docstring of `Calculator.divide()` in `src/calculator.py` — it describes
the full contract: what inputs are valid, what the function returns, and what
exceptions it raises. Your tests must exercise all of those cases.

---

## Worked example

The complete `Calculator.add()` tests in `tests/test_calculator.py` are your
reference. Here is the simplest one to orient you:

```python
def test__add__given_two_positive_floats__returns_their_sum() -> None:
    # Tracer bullet — confirms the basic mechanism works before testing edge cases.
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(1.0, 2.0)

    # ASSERT
    assert result == pytest.approx(3.0, rel=1e-8)
```

> **Note on floating-point comparison:** `pytest.approx` compares with a small
> relative tolerance instead of exact equality. This is necessary because
> floating-point arithmetic can introduce tiny rounding errors — e.g., `0.1 + 0.2`
> is `0.30000000000000004` in Python, not exactly `0.3`.

---

## Test stubs

The stubs below are already in `tests/test_calculator.py`. Fill in the body of
each one:

```python
def test__divide__given_two_valid_numbers__returns_their_quotient() -> None:
    # Arrange

    # Act

    # Assert
    pass


def test__divide__given_int_operands__returns_float() -> None:
    # Arrange

    # Act

    # Assert
    pass


def test__divide__given_invalid_type__raises_type_error() -> None:
    # Arrange

    # Act

    # Assert
    pass


def test__divide__given_non_finite_operand__raises_value_error() -> None:
    # Arrange

    # Act

    # Assert
    pass


def test__divide__given_zero_divisor__raises_zero_division_error() -> None:
    # Arrange

    # Act

    # Assert
    pass


def test__divide__given_inputs_that_overflow__raises_overflow_error() -> None:
    # Arrange

    # Act

    # Assert
    pass
```

**Hints:**

- For tests that expect an exception, use `pytest.raises`:
  ```python
  with pytest.raises(SomeError):
      calc.divide(bad_input, 1.0)
  ```
- For the overflow test, `sys.float_info.max` divided by a very small positive number
  (e.g., `sys.float_info.min`) produces `inf`.
- For non-finite inputs, `float("inf")` and `float("nan")` are valid Python expressions.

---

## How to run tests and check coverage

From the repo root:

```bash
# Run only the exercise tests (fast feedback while you work)
pytest -v tests/test_calculator.py

# Run with coverage to see which lines are still missing
pytest -v tests/test_calculator.py --cov=src --cov-report=term-missing
```

A successful run looks like this:

```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src\calculator.py      XX      0   100%
```

---

## Deliverable

A completed `tests/test_calculator.py` where:

- All six divide test functions have a real body (no bare `pass`).
- `pytest` reports all tests **passed**.
- The coverage table shows **100%** for `calculator.py` with no missing lines.
