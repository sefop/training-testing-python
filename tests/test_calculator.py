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


class TestCalculatorAdd:
    """Contract tests for the Calculator.add public interface.

    Each test method verifies one behavioral property. Tests are written
    against the public API (Calculator().add(...)) only — no access to
    internal state — so the implementation can be freely refactored without
    touching this file.

    Mathematical properties tested (within rel_tol=1e-8):
        - Basic correctness: known inputs produce the expected output.
        - Identity:          adding zero leaves the value unchanged.
        - Commutativity:     argument order does not affect the result.
        - Overflow guard:    inputs that would produce inf raise OverflowError.
    """

    def test__calculator__add_two_positive_floats__returns_sum(self) -> None:
        # Tracer bullet: verifies the simplest possible happy path end-to-end
        # before testing edge cases. If this test fails, none of the others
        # are meaningful — the basic mechanism is broken.
        calc = Calculator()
        result = calc.add(1.0, 2.0)
        assert result == 3.0

    @pytest.mark.parametrize("x", [0.0, 1.5, -3.7, 1e15])
    def test__calculator__add_identity__returns_x(self, x: float) -> None:
        # The identity element of addition is 0: x + 0 = x for all x.
        # We use math.isclose with rel_tol=1e-8 because floating-point
        # arithmetic is not exact — two results that are mathematically
        # equal may differ in the last few binary digits. rel_tol scales
        # the tolerance with the magnitude of the numbers being compared,
        # which is the right choice when operands can span many orders of
        # magnitude (e.g., 1.5 vs. 1e15).
        calc = Calculator()
        assert math.isclose(calc.add(x, 0.0), x, rel_tol=1e-8)

    @pytest.mark.parametrize("a,b", [(1.0, 2.0), (-1.5, 3.5), (1e10, -1e10), (0.0, 0.0)])
    def test__calculator__add_commutative__same_result_both_orders(self, a: float, b: float) -> None:
        # Commutativity: a + b = b + a. This holds exactly for Python's native
        # float addition, but we test it explicitly to document the contract.
        # If add were ever reimplemented with a non-commutative algorithm
        # (e.g., Kahan summation over a list), this test would catch a regression.
        calc = Calculator()
        assert math.isclose(calc.add(a, b), calc.add(b, a), rel_tol=1e-8)

    def test__calculator__add_overflow__raises_overflow_error(self) -> None:
        # 1.8e308 is near the maximum representable IEEE 754 double (~1.8 × 10^308).
        # Adding two such values produces infinity under the default Python behavior.
        # We assert that the implementation raises OverflowError rather than silently
        # returning inf, because inf would propagate invisibly through further
        # calculations and produce hard-to-diagnose errors downstream.
        calc = Calculator()
        with pytest.raises(OverflowError):
            calc.add(1.8e308, 1.8e308)
