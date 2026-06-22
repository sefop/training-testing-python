from __future__ import annotations

import sys

import pytest

from calculator import Calculator


def test__add__given_two_integers__returns_their_sum() -> None:
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(1.0, 2.0)

    # ASSERT
    assert result == pytest.approx(3.0, rel=1e-8)


@pytest.mark.parametrize("x", [0.0, 1.5, -3.7, 1e15])
def test__add__given_zero_as_second_operand__returns_first_operand(x: float) -> None:
    # pytest.approx with rel=1e-8 scales tolerance with the magnitude of the numbers,
    # which is correct when operands can span many orders of magnitude (e.g., 1.5 vs. 1e15).
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(x, 0.0)

    # ASSERT
    assert result == pytest.approx(x, rel=1e-8)


@pytest.mark.parametrize("a,b", [(1.0, 2.0), (-1.5, 3.5), (1e10, -1e10), (0.0, 0.0)])
def test__add__given_reversed_operands__returns_same_result(a: float, b: float) -> None:
    # Tested explicitly to document the commutativity contract. If add were ever
    # reimplemented with a non-commutative algorithm this test would catch the regression.

    # ARRANGE
    calc = Calculator()

    # ACT
    forward = calc.add(a, b)
    backward = calc.add(b, a)

    # ASSERT
    assert forward == pytest.approx(backward, rel=1e-8)


@pytest.mark.parametrize("a,b", [
    ("1", 2.0),   # string as first operand
    (True, 2.0),  # bool as first operand
    (1.0, "2"),   # string as second operand
    (1.0, False), # bool as second operand
])
def test__add__given_invalid_operand_type__raises_type_error(
    a: object, b: object
) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(TypeError):
        calc.add(a, b)  # type: ignore[arg-type]


@pytest.mark.parametrize("a,b,expected", [
    (1,   2.0, 3.0),  # int first operand promoted to float
    (1.0, 2,   3.0),  # int second operand promoted to float
])
def test__add__given_int_operand__returns_float(
    a: int | float, b: int | float, expected: float
) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(a, b)

    # ASSERT
    assert result == pytest.approx(expected, rel=1e-8)
    assert isinstance(result, float)


@pytest.mark.parametrize("a,b", [
    (float("inf"), 1.0),  # inf as first operand
    (1.0, float("nan")),  # nan as second operand
])
def test__add__given_non_finite_operand__raises_value_error(
    a: float, b: float
) -> None:
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(ValueError):
        calc.add(a, b)


def test__add__given_near_max_float_inputs__raises_overflow_error() -> None:
    # We assert OverflowError rather than accepting silent inf, because inf would
    # propagate invisibly through further calculations and produce hard-to-diagnose
    # errors downstream. sys.float_info.max is the largest *finite* IEEE 754 double
    # (~1.8 × 10^308); adding it to itself produces inf at the output, which add
    # detects and re-raises as OverflowError.
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(OverflowError):
        calc.add(sys.float_info.max, sys.float_info.max)
