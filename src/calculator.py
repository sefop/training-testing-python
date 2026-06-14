import math


class Calculator:
    """Performs arithmetic operations on floating-point numbers.

    This class is stateless — it holds no data between calls. Each method
    receives all the values it needs as arguments and returns a result.
    Stateless design makes objects trivially safe to share and reuse, and
    makes tests simple: there is no setup state to prepare or tear down.
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
            TypeError: If either operand is not a float.
            ValueError: If either operand is non-finite (inf or nan).
            OverflowError: If the result exceeds the range of IEEE 754
                double-precision floats. Python does not raise on float
                overflow by default — it silently returns inf. This method
                detects inf explicitly and raises so that callers receive
                a clear error instead of silently propagating a sentinel value
                through further calculations.
        """
        if not isinstance(a, float):
            raise TypeError(f"a must be a float, got {type(a).__name__}")
        if not isinstance(b, float):
            raise TypeError(f"b must be a float, got {type(b).__name__}")
        # inf and nan are valid IEEE 754 floats in Python, so isinstance alone
        # does not catch them — we must check finiteness explicitly.
        if not math.isfinite(a):
            raise ValueError(f"a must be finite, got {a}")
        if not math.isfinite(b):
            raise ValueError(f"b must be finite, got {b}")
        result = a + b
        # Python's float arithmetic follows IEEE 754: adding two sufficiently
        # large values produces float('inf') rather than raising an exception.
        # We detect this explicitly because silently returning inf would violate
        # the contract that add always returns a *finite* number, and inf
        # propagates invisibly through downstream arithmetic.
        if math.isinf(result):
            raise OverflowError(f"Result of {a} + {b} exceeds float range")
        return result

    def divide(self, a: float, b: float) -> float:
        """Return the quotient of two floating-point numbers.

        Args:
            a: Dividend. Must be a finite float.
            b: Divisor. Must be a finite, non-zero float.

        Returns:
            The arithmetic quotient a / b as a finite float.

        Raises:
            TypeError: If either operand is not a float.
            ValueError: If either operand is non-finite (inf or nan).
            ZeroDivisionError: If b is zero.
            OverflowError: If the result exceeds the range of IEEE 754
        """
        pass
