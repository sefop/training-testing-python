"""Domain implementation of a floating-point Calculator.

WHY THIS EXISTS:
    This module is the production code under test. In test-driven development (TDD)
    you always have two files: the implementation (this file) and the tests
    (tests/test_calculator.py). The tests describe the contract; this file fulfills it.

ROLE:
    Simple arithmetic domain object. No dependencies on external libraries beyond
    Python's standard library.
"""
import math


class Calculator:
    """Performs arithmetic operations on floating-point numbers.

    This class is stateless — it holds no data between calls. Each method
    receives all the values it needs as arguments and returns a result.
    Stateless design makes objects trivially safe to share and reuse, and
    makes tests simple: there is no setup state to prepare or tear down.

    The add method satisfies the following mathematical properties
    (verified by the test suite within a relative tolerance of 1e-8):
        - Identity:      add(x, 0.0) ≈ x  for all finite x
        - Commutativity: add(a, b)  ≈ add(b, a)  for all finite a, b
    """

    def add(self, a: float, b: float) -> float:
        """Return the sum of two floating-point numbers.

        Satisfies identity (add(x, 0.0) ≈ x) and commutativity
        (add(a, b) ≈ add(b, a)) within a relative tolerance of 1e-8.

        Args:
            a: First operand. Must be a finite float.
            b: Second operand. Must be a finite float.

        Returns:
            The arithmetic sum a + b as a finite float.

        Raises:
            OverflowError: If the result exceeds the range of IEEE 754
                double-precision floats. Python does not raise on float
                overflow by default — it silently returns inf. This method
                detects inf explicitly and raises so that callers receive
                a clear error instead of silently propagating a sentinel value
                through further calculations.
        """
        result = a + b
        # Python's float arithmetic follows IEEE 754: adding two sufficiently
        # large values produces float('inf') rather than raising an exception.
        # We detect this explicitly because silently returning inf would violate
        # the contract that add always returns a *finite* number, and inf
        # propagates invisibly through downstream arithmetic.
        if math.isinf(result):
            raise OverflowError(f"Result of {a} + {b} exceeds float range")
        return result
