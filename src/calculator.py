# This import makes all type annotations in this file lazy strings that are
# never evaluated at runtime. This lets us use the modern `X | Y` union syntax
# (PEP 604, Python 3.10+) without raising a TypeError on Python 3.7–3.9.
from __future__ import annotations

import math


class Calculator:
    """Performs arithmetic operations on floating-point numbers.

    This class is stateless — it holds no data between calls. Each method
    receives all the values it needs as arguments and returns a result.
    Stateless design makes objects trivially safe to share and reuse, and
    makes tests simple: there is no setup state to prepare or tear down.
    """

    def add(self, a: int | float, b: int | float) -> float:
        """Return the sum of two numbers as a float.

        Satisfies identity (add(x, 0) ≈ x) and commutativity
        (add(a, b) ≈ add(b, a)) within a relative tolerance of 1e-8.

        Args:
            a: First operand. Must be a finite int or float. bool is not accepted.
            b: Second operand. Must be a finite int or float. bool is not accepted.

        Returns:
            The arithmetic sum a + b as a finite float. int inputs are promoted
            to float so the return type is always float regardless of input types.

        Raises:
            TypeError: If either operand is not an int or float (including bool).
            ValueError: If either operand is non-finite (inf or nan).
            OverflowError: If the result exceeds the range of IEEE 754
                double-precision floats. Python does not raise on float
                overflow by default — it silently returns inf. This method
                detects inf explicitly and raises so that callers receive
                a clear error instead of silently propagating a sentinel value
                through further calculations.
        """
        # bool is a subclass of int in Python, so isinstance(True, int) is True.
        # We reject it explicitly before the int | float check because passing a
        # boolean to an arithmetic method is almost certainly a bug.
        if isinstance(a, bool):
            raise TypeError(f"a must be int or float, got {type(a).__name__}")
        if not isinstance(a, (int, float)):
            raise TypeError(f"a must be int or float, got {type(a).__name__}")
        if isinstance(b, bool):
            raise TypeError(f"b must be int or float, got {type(b).__name__}")
        if not isinstance(b, (int, float)):
            raise TypeError(f"b must be int or float, got {type(b).__name__}")
        # inf and nan are valid IEEE 754 floats in Python, so isinstance alone
        # does not catch them — we must check finiteness explicitly.
        # math.isfinite works on both int and float; all ints are finite.
        if not math.isfinite(a):
            raise ValueError(f"a must be finite, got {a}")
        if not math.isfinite(b):
            raise ValueError(f"b must be finite, got {b}")
        # Explicit float() promotion ensures the return type is always float even
        # when both operands are int (1 + 2 = 3 in Python, not 3.0).
        result = float(a) + float(b)
        # Python's float arithmetic follows IEEE 754: adding two sufficiently
        # large values produces float('inf') rather than raising an exception.
        # We detect this explicitly because silently returning inf would violate
        # the contract that add always returns a *finite* number, and inf
        # propagates invisibly through downstream arithmetic.
        if math.isinf(result):
            raise OverflowError(f"Result of {a} + {b} exceeds float range")
        return result

    def divide(self, a: int | float, b: int | float) -> float:
        """Return the quotient of two numbers as a float.

        Args:
            a: Dividend. Must be a finite int or float. bool is not accepted.
            b: Divisor. Must be a finite, non-zero int or float. bool is not accepted.

        Returns:
            The arithmetic quotient a / b as a finite float.

        Raises:
            TypeError: If either operand is not an int or float (including bool).
            ValueError: If either operand is non-finite (inf or nan).
            ZeroDivisionError: If b is zero.
            OverflowError: If the result exceeds the range of IEEE 754
                double-precision floats.
        """

        # bool is a subclass of int in Python, so isinstance(True, int) is True.
        # We reject it explicitly before the int | float check because passing a
        # boolean to an arithmetic method is almost certainly a bug.
        if isinstance(a, bool):
            raise TypeError(f"a must be int or float, got {type(a).__name__}")
        if not isinstance(a, (int, float)):
            raise TypeError(f"a must be int or float, got {type(a).__name__}")
        if isinstance(b, bool):
            raise TypeError(f"b must be int or float, got {type(b).__name__}")
        if not isinstance(b, (int, float)):
            raise TypeError(f"b must be int or float, got {type(b).__name__}")
        # inf and nan are valid IEEE 754 floats in Python, so isinstance alone
        # does not catch them — we must check finiteness explicitly.
        # math.isfinite works on both int and float; all ints are finite.
        if not math.isfinite(a):
            raise ValueError(f"a must be finite, got {a}")
        if not math.isfinite(b):
            raise ValueError(f"b must be finite, got {b}")
        # Checked after type and finiteness guards so the error message is unambiguous:
        # a zero b that reaches this point is a genuine zero divisor, not a type mistake.
        if b == 0:
            raise ZeroDivisionError("b must be non-zero")
        # Explicit float() promotion ensures the return type is always float even
        # when both operands are int (4 / 2 = 2 in Python, not 2.0).
        result = float(a) / float(b)
        # Python's float arithmetic follows IEEE 754: dividing a very large value
        # by a very small one can produce float('inf') rather than raising.
        # We detect this explicitly because silently returning inf would violate
        # the contract that divide always returns a *finite* number.
        if math.isinf(result):
            raise OverflowError(f"Result of {a} / {b} exceeds float range")
        return result
