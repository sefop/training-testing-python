from __future__ import annotations

import sys

import pytest

from calculator import Calculator


def test__divide__given_two_valid_numbers__returns_their_quotient() -> None:
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.divide(10.0, 2.0)

    # ASSERT
    assert result == pytest.approx(5.0, rel=1e-8)


@pytest.mark.parametrize("x", [1.5, -3.7, 1e15])
def test__divide__given_dividend_and_one__returns_dividend(x: float) -> None:
    # pytest.approx with rel=1e-8 scales tolerance with the magnitude of the numbers.
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.divide(x, 1.0)

    # ASSERT
    assert result == pytest.approx(x, rel=1e-8)


@pytest.mark.parametrize("a,b", [(1.0, 1.0), (-2.5, -2.5), (1e10, 1e10)])
def test__divide__given_same_numbers__returns_one(a: float, b: float) -> None:
    # Tested explicitly to document the multiplicative inverse property. If divide
    # were ever reimplemented incorrectly, this test would catch the regression.

    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.divide(a, b)

    # ASSERT
    assert result == pytest.approx(1.0, rel=1e-8)


@pytest.mark.parametrize("a,b,expected", [
    (4, 2.0, 2.0),   # int first operand promoted to float
    (4.0, 2, 2.0),   # int second operand promoted to float
])
def test__divide__given_int_operands__returns_float(
    a: int | float, b: int | float, expected: float
) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.divide(a, b)

    # ASSERT
    assert result == pytest.approx(expected, rel=1e-8)
    assert isinstance(result, float)


@pytest.mark.parametrize("a,b", [
    ("1", 2.0),   # string as first operand
    (True, 2.0),  # bool as first operand
    (1.0, "2"),   # string as second operand
    (1.0, False), # bool as second operand
])
def test__divide__given_invalid_types__raises_type_error(
    a: object, b: object
) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(TypeError):
        calc.divide(a, b)  # type: ignore[arg-type]


@pytest.mark.parametrize("a,b", [
    (float("inf"), 1.0),  # inf as first operand
    (1.0, float("nan")),  # nan as second operand
])
def test__divide__given_non_finite_operand__raises_value_error(
    a: float, b: float
) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(ValueError):
        calc.divide(a, b)


def test__divide__given_zero_divisor__raises_zero_division_error() -> None:
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(ZeroDivisionError):
        calc.divide(10.0, 0.0)


def test__divide__given_inputs_that_overflow__raises_overflow_error() -> None:
    # Dividing a very large number by a very small one can produce inf at the output.
    # We assert OverflowError rather than accepting silent inf, because inf would
    # propagate invisibly through further calculations and produce hard-to-diagnose
    # errors downstream. sys.float_info.max is the largest *finite* IEEE 754 double
    # (~1.8 × 10^308); dividing it by a tiny value produces inf, which divide
    # detects and re-raises as OverflowError.
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(OverflowError):
        calc.divide(sys.float_info.max, 1e-300)
