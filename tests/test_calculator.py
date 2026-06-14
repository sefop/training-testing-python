"""Contract tests for Calculator.add defined in src/calculator.py.

WHY THIS EXISTS:
    In TDD, tests are written before (or alongside) the implementation. This file
    describes the *contract* of Calculator.add — what it must do — independently
    of how it does it. If the implementation is rewritten from scratch, these tests
    should still pass unchanged, because the observable behavior has not changed.

HOW TO RUN:
    From the project root with the virtual environment active:
        pytest tests/test_calculator.py -v
"""
import math
import pytest
from calculator import Calculator


def test__add__given_two_positive_floats__returns_their_sum() -> None:
    # Tracer bullet — confirms the basic mechanism works before testing edge cases.
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(1.0, 2.0)

    # ASSERT
    assert result == 3.0


@pytest.mark.parametrize("x", [0.0, 1.5, -3.7, 1e15])
def test__add__given_zero_as_second_operand__returns_first_operand(x: float) -> None:
    # We use math.isclose with rel_tol=1e-8 because floating-point arithmetic is not
    # exact — rel_tol scales with the magnitude of the numbers, which is correct when
    # operands can span many orders of magnitude (e.g., 1.5 vs. 1e15).
    # ARRANGE
    calc = Calculator()

    # ACT
    result = calc.add(x, 0.0)

    # ASSERT
    assert math.isclose(result, x, rel_tol=1e-8)


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
    assert math.isclose(forward, backward, rel_tol=1e-8)


def test__add__given_near_max_float_inputs__raises_overflow_error() -> None:
    # We assert OverflowError rather than accepting silent inf, because inf would
    # propagate invisibly through further calculations and produce hard-to-diagnose
    # errors downstream. 1.8e308 is near the IEEE 754 double maximum (~1.8 × 10^308).
    # ARRANGE
    calc = Calculator()

    # ACT / ASSERT
    with pytest.raises(OverflowError):
        calc.add(1.8e308, 1.8e308)
