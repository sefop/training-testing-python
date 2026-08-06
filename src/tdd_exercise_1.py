# TDD EXERCISE
#
# This file has no implementation on purpose. Implement LinearExpression
# below using red-green-refactor:
#   1. Write ONE failing test for a single requirement from the docstring.
#   2. Write the minimum code to make it pass.
#   3. Refactor if needed, keeping all tests green.
#   4. Repeat for the next requirement.
# Method names, parameters, and internal design are entirely up to you —
# only the observable behavior described below is required.


class LinearExpression:
    """
    Models a linear expression of the form: a0 + a1*x1 + a2*x2 + ... + an*xn

    Where a0 is a scalar, a1,a2,...,an are non-zero coefficients, and x1..xn are
    non-empty variable names.

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

    pass
