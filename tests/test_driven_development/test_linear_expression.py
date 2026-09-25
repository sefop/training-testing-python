"""Unit tests for LinearExpression, written test-first.

The three tests below are the three cycles of the book's worked example, in the
order they were written. Each one was red before the code that makes it pass
existed. Continue from here: add one test for the next requirement in the
docstring of LinearExpression, watch it fail, then make it pass.

Test names follow test__method__given_condition__expected_outcome, so a failing
test reports in plain words which promise was broken.
"""

import pytest

from test_driven_development.linear_expression import LinearExpression

# Relative tolerance used when comparing floats.
RELATIVE_TOLERANCE: float = 1e-8


# =============================================================================
# The scalar part: the book's worked example, one test per cycle.
# =============================================================================


def test__linear_expression__given_no_arguments__has_scalar_zero() -> None:
    # Cycle 1. Red: LinearExpression did not exist yet.

    # Arrange
    # Nothing to prepare: the constructor itself is the unit under test.

    # Act
    expression: LinearExpression = LinearExpression()

    # Assert
    assert expression.scalar() == pytest.approx(0.0, rel=RELATIVE_TOLERANCE)


def test__linear_expression__given_a_scalar__has_that_scalar() -> None:
    # Cycle 2. Red: scalar() returned the constant 0.0.

    # Arrange
    scalar: float = 3.0

    # Act
    expression: LinearExpression = LinearExpression(scalar=scalar)

    # Assert
    assert expression.scalar() == pytest.approx(scalar, rel=RELATIVE_TOLERANCE)


def test__add_scalar__given_a_value__increases_the_scalar_by_it() -> None:
    # Cycle 3. Red: add_scalar did not exist yet.

    # Arrange
    expression: LinearExpression = LinearExpression(scalar=1.0)

    # Act
    expression.add_scalar(3.0)

    # Assert
    assert expression.scalar() == pytest.approx(4.0, rel=RELATIVE_TOLERANCE)


# =============================================================================
# The variables: your cycles start here.
# =============================================================================
