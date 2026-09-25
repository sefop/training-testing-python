# Exercise 3: mocks (Python)

The theory, and the worked example this exercise starts from, are in the training hub:
[Mocks](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#ch-mocks).
This page only covers what's specific to Python.

## The starting point

- [`nightly_planner.py`](nightly_planner.py) is the code under test. It's complete: you only write tests.
  `NightlyPlanner.review(result)` pages the planner on call when the nightly solve found no plan. Its
  docstring is the contract:
  - `INFEASIBLE`: one page, `"Instance <id>: no feasible plan exists."`
  - `TIME_LIMIT_NO_SOLUTION`: one page, `"Instance <id>: no plan found within the time limit."`
  - `OPTIMAL` or `FEASIBLE`: no page.
- [`test_nightly_planner.py`](../../tests/mocks/test_nightly_planner.py) holds:
  - the book's two tests, finished. The first uses `RecordingPager`, a mock written by hand: a class whose
    `page` appends the message to a list. The second uses `unittest.mock`, which builds such an object for
    you. Read both: they do the same job.
  - three empty tests for you, each marked `@pytest.mark.skip`.

## The steps

For each empty test:

1. Write the body with the Arrange / Act / Assert layout of the finished tests, using `Mock(spec=Pager)`.
2. Delete the `@pytest.mark.skip(reason="Exercise: implement me")` line.
3. Run the tests and make sure the new one passes.

Then break the code on purpose, to see what the mock protects:

4. In `review`, call `self._pager.page(...)` twice for `INFEASIBLE`. Run the tests: the "called once"
   assertions fail, because a planner woken up twice for one problem is a bug. **Undo the change.**
5. In `review`, remove the `TIME_LIMIT_NO_SOLUTION` branch. Run the tests: your time-limit test fails. Without
   a mock, nothing in the program would show that a page was missing. **Undo the change.**

You're done when every test passes, `skipped` is 0, and both breakages above were caught.

## unittest.mock in five minutes

[`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) is part of Python's standard library:
there is nothing to install. Its `Mock` creates an object that accepts calls and records each one.

| The book's pseudocode | unittest.mock |
|---|---|
| `pager = mock(Pager)` | `pager = Mock(spec=Pager)` |
| `expect pager.page called once with "…"` | `pager.page.assert_called_once_with("…")` |
| `expect pager.page never called` | `pager.page.assert_not_called()` |

Two things catch people out:

- **Always pass `spec=`.** A bare `Mock()` accepts *any* call, including typos: `pager.pgae("…")` is recorded
  without complaint, and a test can pass while checking nothing. `spec=Pager` makes the mock reject any call
  a `Pager` doesn't have.
- **Assertions start with `assert_`.** `pager.page.assert_called_once_with(...)` checks. On old Python
  versions, a misspelled `pager.page.called_once_with(...)` was just another recorded call and checked
  nothing. Python 3.12, which this repository uses, raises an `AttributeError` for that typo instead.

## Running the tests

From the root of the repository, with the virtual environment activated:

```bash
pytest tests/mocks
```

Before you start, the summary reads:

```
========================= 2 passed, 3 skipped in 0.29s =========================
```
