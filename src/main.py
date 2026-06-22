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
    calc = Calculator()

    # Demonstrate addition.
    result_add = calc.add(10, 5)
    print(f"10 + 5 = {result_add}")

    # Demonstrate division.
    result_divide = calc.divide(10, 5)
    print(f"10 / 5 = {result_divide}")


if __name__ == "__main__":
    main()
