# Exercise 1: unit tests and coverage (Python)

The theory, and the reasoning behind this exercise, are in the training hub:
[Exercise 1: a calculator](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#exercise-1-a-calculator).
This page only covers what's specific to Python.

The exercise has two parts:

- **[Part A](#part-a-test-divide):** write the tests for `divide` until `Calculator` is 100% covered.
- **[Part B](#part-b-refactor-without-touching-the-tests):** change how `Calculator` works inside, without
  changing what it promises, and see that the tests don't need to change.

## Part A: test `divide`

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

## Part B: refactor without touching the tests

### Why

`Calculator` has two sides. The docstring of each method is its **contract**, or interface: what it
accepts, what it returns, and which exceptions it raises. The method bodies are **implementation details**:
one way, among many, of keeping that promise. Good tests check the contract only. So if you change the
implementation and keep the contract, the tests must stay green **without being edited**. That's what makes
it safe to clean up code: the tests tell you straight away whether you broke a promise.

### Before you start

Finish Part A first: no `@pytest.mark.skip` left and `divide` fully covered. A test that is still skipped
protects nothing, so a refactor could break `divide` without any warning.

### Steps

1. **Run the tests with coverage** and write down the summary line (`… passed`) and the coverage of
   `calculator.py`.

2. **Refactor.** `add` and `divide` both start with the same block that rejects non-numbers, booleans, and
   NaN or infinite operands. Move that duplicated validation into **one private helper method** that both
   `add` and `divide` call. Don't open `test_calculator.py` while you do it.

   <details>
   <summary>Hint</summary>

   A signature that works well:

   ```python
   @staticmethod
   def _validate_operand(value: object, name: str) -> None:
   ```

   It raises the same exceptions as before, using `name` in the messages. `add` and `divide` then call it
   once per operand: `self._validate_operand(a, "a")` and `self._validate_operand(b, "b")`. The leading `_`
   is Python's convention for "private: not part of the interface". `@staticmethod` says the helper uses no
   data of the object, which fits a stateless class.

   **Keep the order of the checks:** the `bool` check, then the `int | float` check, then the finiteness
   check. If you check finiteness first, `math.isfinite("1")` raises its own `TypeError`. The tests would
   still pass, but by accident, with a confusing message.

   </details>

3. **Run the tests again.** You should see the same summary as in step 1, with every test passing and
   `calculator.py` still 100% covered. Run `git status`: `calculator.py` is modified and `test_calculator.py`
   isn't. The implementation changed, the contract didn't, and the tests didn't notice. That's the point.

   Don't add a test for `_validate_operand`. It's an implementation detail, not part of the contract. It
   already runs through the tests of `add` and `divide`, and the coverage report proves it: still 100%
   without any new test. A test that called the helper directly would break the day someone renames it or
   inlines it back, even though no promise changed. Python won't stop you from calling it, but the leading
   `_` is a clear "don't".

4. **Break the contract on purpose.** In the helper, raise an `ArithmeticError` instead of a `ValueError`
   for a non-finite operand, then run the tests. The non-finite tests of `add` fail, and so does yours for
   `divide`. This time the tests are right to complain: the exception type is written in the docstring, so
   it's part of the contract. Also notice that one change in one shared place broke two methods.
   **Undo the change** and check that everything passes again.

5. **Optional challenge.** In `divide`, call the helper for `a` only and remove the call for `b`. Run the
   tests. Did anything fail? If not, your Part A tests never tried an invalid *divisor*. The promise is
   broken and nobody noticed. Add that case to your test, watch it fail, then put the call back.
   Asking "would my tests catch this bug?" is exactly what exercise 3 (mutation testing) automates.

### What you learned

- Tests pin down the contract, not the code. The implementation is free to change underneath them.
- That's what makes refactoring safe: the same tests, still passing, are your evidence that no promise broke.
- A test that fails after a contract change is doing its job. The fix is in the code, or, if the new
  behavior is intended, in the contract and its tests together.
