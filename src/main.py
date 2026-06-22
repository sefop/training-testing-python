"""Simple example demonstrating how to use the Calculator class.
If you want to use this module just type in your terminal:
python src/main.py
"""

from calculator import Calculator


def main() -> None:
    """Create a Calculator instance and perform basic arithmetic operations.

    This function shows users how to instantiate the Calculator and call
    its methods with numeric inputs.
    """
    # Initialize a stateless Calculator instance.
    calculator = Calculator()

    # Demonstrate addition.
    print(f"10 + 5 = {calculator.add(10, 5)}")

    # Demonstrate division.
    print(f"10 / 6 = {calculator.divide(10, 6)}")


if __name__ == "__main__":
    main()
