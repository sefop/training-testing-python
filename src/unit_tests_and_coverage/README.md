# Exercise 1: unit tests and coverage (Python)

The theory, and the reasoning behind this exercise, are in the training hub:
[Exercise 1: a calculator](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#exercise-1-a-calculator).
This page only covers what's specific to Python.

## The task

- [`calculator.py`](calculator.py) is the code under test.
- [`test_calculator.py`](../../tests/unit_tests_and_coverage/test_calculator.py) holds all the tests for
  `Calculator`, in two parts:
  - the `add` tests are a finished worked example. Read them first.
  - the `divide` tests are yours: eight empty tests, each marked `@pytest.mark.skip`.

For each `divide` test in `test_calculator.py`:

1. Write the body using the Arrange / Act / Assert layout from the `add` tests.
2. Delete the `@pytest.mark.skip(reason="Exercise: implement me")` line so pytest runs the test.
3. Run the tests and make sure the new test passes.
4. Check the coverage report to see which lines of `divide` are now covered.

When you're done, every test should pass, `skipped` should be 0, and `divide` should be fully covered.

The Java version of this exercise has six `divide` tests. The two extra ones here (invalid types and `int`
operands) exist because Python doesn't check argument types for you: `calculator.py` has to reject a string
or a `bool` itself, and has to turn an `int` result into a `float` itself.

## pytest in five minutes

[pytest](https://docs.pytest.org/) is the standard test framework for Python, the counterpart of JUnit 5.

| You want to… | pytest | JUnit 5 equivalent |
|---|---|---|
| Mark a function as a test | name it `test_...` | `@Test` |
| Run one test with several inputs | `@pytest.mark.parametrize` | `@ParameterizedTest` + `@ValueSource` / `@CsvSource` |
| Skip a test for now | `@pytest.mark.skip(reason="...")` | `@Disabled("reason")` |
| Compare floats | `result == pytest.approx(expected, rel=1e-8)` | `assertEquals(expected, actual, delta)` |
| Expect an exception | `with pytest.raises(SomeError):` | `assertThrows(SomeException.class, () -> ...)` |

Two things catch people out:

- **`pytest.approx` has a default tolerance.** `pytest.approx(3.0)` accepts anything within a relative
  1e-6 of 3.0. The contract of `Calculator` promises 1e-8, so the tests pass `rel=RELATIVE_TOLERANCE`
  explicitly. Never compare floats with a bare `==`: `0.1 + 0.2 == 0.3` is `False`.
- **The call must be inside the `with` block.** Write

  ```python
  with pytest.raises(ZeroDivisionError):
      calc.divide(1.0, 0.0)
  ```

  If the call is on a line before the `with`, it runs before pytest gets a chance to catch the exception,
  and the test crashes instead of passing.

## Running the tests

From the root of the repository, with the virtual environment activated:

```bash
pytest tests/unit_tests_and_coverage
```

To run only the `divide` tests (`-k` selects tests whose name contains the given text):

```bash
pytest tests/unit_tests_and_coverage -k divide
```

Add `-v` to see one line per test. In PyCharm or VS Code, click the green arrow next to a test function.

The output ends with a summary like this:

```
======================== 18 passed, 8 skipped in 0.03s ========================
```

`skipped` counts the tests that still have `@pytest.mark.skip`. Each input of a parameterized test counts
as a separate test, so the total goes up as you add cases.

## Code coverage with pytest-cov

[pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) is the Python counterpart of JaCoCo. It records
which lines and branches of `src` ran while the tests ran. It's already installed by `requirements.txt`, but
unlike JaCoCo it only runs when you ask for it.

This prints a table in the terminal with the coverage of each file and the line numbers no test reached:

```bash
pytest tests/unit_tests_and_coverage --cov=src/unit_tests_and_coverage --cov-branch --cov-report=term-missing
```

Before you start, it looks like this. The `Missing` column lists the lines of `divide`:

```
Name                                        Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------------------
src\unit_tests_and_coverage\__init__.py         0      0      0      0   100%
src\unit_tests_and_coverage\calculator.py      39     18     30      0    51%   108-136
---------------------------------------------------------------------------------------
TOTAL                                          39     18     30      0    51%
```

`--cov-branch` adds the `Branch` and `BrPart` columns. `BrPart` (partial branches) is the most useful number
here: a line can run while one side of its `if` has never been tested.

For a colored view, write an HTML report and open `htmlcov/index.html` in a browser:

```bash
pytest tests/unit_tests_and_coverage --cov=src/unit_tests_and_coverage --cov-branch --cov-report=html
```

Click `calculator.py` to see the source code colored:

- **Green:** the line ran during the tests.
- **Red:** the line never ran. No test covers it.
- **Yellow:** the line ran, but only some of its branches did. For example, an `if` whose condition was
  only ever `False`. The note at the end of the line says which branch was missed.

Before you start, `add` is fully green and `divide` is red. Watch `divide` turn green as you enable your
tests.

**IDE alternative:** in PyCharm, right-click the test file → *More Run/Debug* → *Run with Coverage*. PyCharm
colors the editor margin directly. The CI server uses pytest-cov, so that's the number that counts.
