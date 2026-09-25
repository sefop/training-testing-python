# Exercise 2: test-driven development. See README.md in this folder for the instructions.
#
# The scalar part of LinearExpression is already built, test-first, exactly as in the
# book's worked example: an empty expression, an expression with a scalar, and
# add_scalar. Everything about variables is yours to build, one red-green-refactor
# cycle at a time. For the new methods, names, parameters and internal design are up
# to you: only the observable behavior described in the docstring is required.


class LinearExpression:
    """
    Models a linear expression of the form: a0 + a1*x1 + a2*x2 + ... + an*xn

    Where a0 is a scalar, a1,a2,...,an are non-zero coefficients, and x1..xn are
    non-empty variable names.

    Types: the scalar and the coefficients are floats; each variable is identified
    by its name, a str.

    Examples:
    - 0            -> scalar 0.0, no variables.
    - 1 + 2x       -> scalar 1.0, coefficient 2.0 for "x".
    - -1 - x + 2y  -> scalar -1.0, coefficient -1.0 for "x", coefficient 2.0 for "y".

    Construction
    ------------
    The expression must be constructible in each of these forms:
    - Empty: no scalar and no terms given. The scalar defaults to 0.0 and
      there are no variables.
      Example: a freshly constructed empty expression has scalar 0.0 and
      an empty set of variables.
    - Scalar only: constructed with just a scalar value.
      Example: constructed with scalar 3.0, the scalar is 3.0 and the set
      of variables is empty.
    - Single term only: constructed with a coefficient and a variable name.
      Example: constructed with coefficient 2.0 for variable "x1", the
      scalar is 0.0 and the coefficient for "x1" is 2.0.
    - Scalar and a single term together: constructed with a scalar,
      coefficient, and variable name.
      Example: constructed with scalar 1.0 and coefficient 2.0 for
      variable "x1", the scalar is 1.0 and the coefficient for "x1" is 2.0.

    Modifying operations
    ---------------------
    - Add a scalar value to the expression. This changes the expression's
      own scalar by adding the given amount to it.
      Example: an expression with scalar 1.0, after adding scalar 3.0, has
      scalar 4.0.
    - Add a term (a coefficient for a variable) to the expression. If the
      variable is not yet present, it is added with the given coefficient.
      If the variable is already present, the given coefficient is added
      to (accumulated with) its existing coefficient rather than replacing
      it.
      Example: an expression with an existing coefficient of 3.0 for "x1",
      after adding term (2.0, "x1"), has coefficient 5.0 for "x1".
      Example: an expression with no term for "x2", after adding term
      (4.0, "x2"), has coefficient 4.0 for "x2".
    - Merge another LinearExpression into this one. The other expression's
      scalar is added to this expression's scalar. Each of the other
      expression's terms is added to this expression following the same
      accumulation rule as adding a single term (matching variables have
      their coefficients summed; new variables are added).
      Example: an expression with scalar 1.0 and coefficient 2.0 for "x1",
      after merging in an expression with scalar 3.0, coefficient 4.0 for
      "x1", and coefficient 5.0 for "x2", ends up with scalar 4.0,
      coefficient 6.0 for "x1", and coefficient 5.0 for "x2".

    Inspection operations
    ----------------------
    - Retrieve the scalar part (a0) of the expression.
    - Retrieve the set of variable names currently present in the
      expression.
    - Retrieve the coefficient of a given variable name. If that variable
      is not present in the expression, this returns 0.0 rather than
      raising an error.
    - All these operations are read-only, thus, can't modify the expression.
    """

    def __init__(self, scalar: float = 0.0) -> None:
        self._scalar = scalar

    def scalar(self) -> float:
        """Returns the scalar part (a0) of the expression."""
        return self._scalar

    def add_scalar(self, value: float) -> None:
        """Adds value to the scalar part of the expression."""
        self._scalar += value
