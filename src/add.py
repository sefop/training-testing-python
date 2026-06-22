import sys


def add(x: int, y: int) -> int:
    """
    Add two integers with validation and overflow detection.
    - Complies with commutativity: add(x,y) = add(y,x)
    - Complies with identity: add(x,0) = add(0,x)

    :param x: First integer to add
    :param y: Second integer to add
    :return: x + y
    :raises TypeError: If either x or y is not an integer
    :raises OverflowError: If the sum exceeds the maximum
    representable integer
    """
    # Input validation
    if not isinstance(x, int) or isinstance(x, bool):
        raise TypeError("x is not an integer")
    if not isinstance(y, int) or isinstance(y, bool):
        raise TypeError("y is not an integer")

    # Compute the sum
    result = x + y

    # Check for overflow
    if result > sys.maxsize or result < -sys.maxsize - 1:
        raise OverflowError("Integer overflow")

    return result





if __name__ == "__main__":
    # Demonstrate normal usage
    print("=== Normal Usage ===")
    print(f"add(5, 3) = {add(5, 3)}")
    print(f"add(-10, 4) = {add(-10, 4)}")
    print(f"add(0, 42) = {add(0, 42)}")

    # Demonstrate TypeError
    print("\n=== Type Error Handling ===")
    try:
        add("5", 3)
    except TypeError as e:
        print(f"TypeError caught: {e}")

    # Demonstrate OverflowError
    print("\n=== Overflow Error Handling ===")
    try:
        print(add(sys.maxsize, 1))
    except OverflowError as e:
        print(f"OverflowError caught: {e}")