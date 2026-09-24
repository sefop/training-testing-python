"""Unit tests for Calculator.

Python convention is one test file per production module: calculator.py is
tested by test_calculator.py, and every method of Calculator gets its tests
here. You don't create a new file for each method you test.

The file has two parts:
- The tests for add are a finished worked example. They show the patterns the
  exercise expects: one behavior per test, the Arrange / Act / Assert layout,
  parameterized tests for properties that must hold for many inputs, and
  assertions on the exceptions that form part of the contract.
- The tests for divide are the exercise. Each stub names one promise from the
  docstring of divide. Write its body following the add examples, then delete
  its @pytest.mark.skip line so pytest runs it.

Test names follow test__method__given_condition__expected_outcome, so a failing
test reports in plain words which promise was broken.
"""

# Makes every annotation a lazy string, so the `int | float` syntax used in the
# signatures below also works on Python versions older than 3.10.
from __future__ import annotations

import sys

import pytest

from unit_tests_and_coverage.calculator import Calculator

# Relative tolerance used when comparing floats, matching the contract in the
# docstrings of Calculator.
RELATIVE_TOLERANCE: float = 1e-8


# =============================================================================
# add: worked example. Read these tests before writing the divide tests below.
# =============================================================================


def test__add__given_two_numbers__returns_their_sum() -> None:
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(1.0, 2.0)

    # ASSERT
    # Floats are compared with a tolerance, never with exact equality, because
    # most decimal numbers have no exact binary representation (0.1 + 0.2 is
    # not exactly 0.3). rel= makes the tolerance scale with the expected value.
    assert result == pytest.approx(3.0, rel=RELATIVE_TOLERANCE)


@pytest.mark.parametrize("x", [0.0, 1.5, -3.7, 1e15])
def test__add__given_zero_as_second_operand__returns_first_operand(x: float) -> None:
    # A relative tolerance matters here because the inputs span many orders of
    # magnitude: an absolute tolerance of 1e-8 would be far too strict for 1e15
    # and meaningless near 1e-10.

    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(x, 0.0)

    # ASSERT
    assert result == pytest.approx(x, rel=RELATIVE_TOLERANCE)


@pytest.mark.parametrize("a,b", [(1.0, 2.0), (-1.5, 3.5), (1e10, -1e10), (0.0, 0.0)])
def test__add__given_reversed_operands__returns_same_result(a: float, b: float) -> None:
    # Tested explicitly to document the commutativity contract. If add were ever
    # reimplemented with a non-commutative algorithm, this test would catch the
    # regression.

    # ARRANGE
    calc = Calculator()

    # ACT
    forward = calc.add(a, b)
    backward = calc.add(b, a)

    # ASSERT
    assert forward == pytest.approx(backward, rel=RELATIVE_TOLERANCE)


@pytest.mark.parametrize("a,b", [
    ("1", 2.0),    # string as first operand
    (True, 2.0),   # bool as first operand
    (1.0, "2"),    # string as second operand
    (1.0, False),  # bool as second operand
])
def test__add__given_invalid_operand_type__raises_type_error(a: object, b: object) -> None:
    # Python-only test: Java rejects these calls at compile time. bool is
    # included on purpose, because True is an int in Python and would otherwise
    # slip through as 1.

    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    # The call must be inside the `with` block: pytest.raises only catches
    # exceptions raised while the block runs.
    with pytest.raises(TypeError):
        calc.add(a, b)  # type: ignore[arg-type]


@pytest.mark.parametrize("a,b,expected", [
    (1, 2.0, 3.0),  # int first operand promoted to float
    (1.0, 2, 3.0),  # int second operand promoted to float
])
def test__add__given_int_operand__returns_float(
    a: int | float, b: int | float, expected: float
) -> None:
    # Python-only test: Java widens int to double automatically. The type check
    # is needed on top of approx, because approx(3.0) also accepts the int 3.

    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(a, b)

    # ASSERT
    assert result == pytest.approx(expected, rel=RELATIVE_TOLERANCE)
    assert isinstance(result, float)


@pytest.mark.parametrize("a,b", [
    (float("inf"), 1.0),  # inf as first operand
    (1.0, float("nan")),  # nan as second operand
])
def test__add__given_non_finite_operand__raises_value_error(a: float, b: float) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(ValueError):
        calc.add(a, b)


def test__add__given_near_max_float_inputs__raises_overflow_error() -> None:
    # We expect an exception rather than accepting a silent inf, because inf
    # would propagate invisibly through further calculations and cause
    # hard-to-diagnose errors downstream. sys.float_info.max is the largest
    # finite float (~1.8 x 10^308); adding it to itself overflows.

    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(OverflowError):
        calc.add(sys.float_info.max, sys.float_info.max)


# =============================================================================
# divide: your exercise. Fill in each test, then delete its @pytest.mark.skip
# line.
#
# The stubs are skipped rather than left empty on purpose: an empty test
# passes, and a passing test that checks nothing gives false confidence.
# Skipped tests show up as "skipped" in the report, which is an honest account
# of the work still to do.
# =============================================================================


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_two_valid_numbers__returns_their_quotient() -> None:
    # ARRANGE

    # ACT

    # ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_dividend_and_one__returns_dividend() -> None:
    # ARRANGE

    # ACT

    # ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_same_numbers__returns_one() -> None:
    # ARRANGE

    # ACT

    # ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_int_operands__returns_float() -> None:
    # ARRANGE

    # ACT

    # ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_invalid_types__raises_type_error() -> None:
    # ARRANGE

    # ACT / ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_non_finite_operand__raises_value_error() -> None:
    # ARRANGE

    # ACT / ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_zero_divisor__raises_zero_division_error() -> None:
    # ARRANGE

    # ACT / ASSERT
    pass


@pytest.mark.skip(reason="Exercise: implement me")
def test__divide__given_inputs_that_overflow__raises_overflow_error() -> None:
    # ARRANGE

    # ACT / ASSERT
    pass
