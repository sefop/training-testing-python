# Integration testing (Python)

The theory, and the worked example this exercise starts from, are in the training hub:
[Integration testing](https://github.com/sefop/sefop-training-hub/blob/main/book/05-testing/README.md#ch-integration).
This page only covers what's specific to Python.

## The starting point

Every night, a solve job saves tomorrow's result to a file, and the nightly planner reads it back to decide whether
to wake the planner on call. The code is complete: you only write tests.

- [`results_writer.py`](results_writer.py): `ResultsWriter(folder).write(result)` saves `<instance_id>.csv`, owned
  by the solve job's team.
- [`results_reader.py`](results_reader.py): `ResultsReader(folder).read(instance_id)` reads it back, owned by the
  planner's team. It raises `MissingResultError` when tonight's file doesn't exist.
- [`nightly_planner.py`](nightly_planner.py): `NightlyPlanner(reader, notifier).review_tonight(instance_id)` reads
  the result and notifies when there is no plan.

The writer and the reader share no code on purpose: each encodes its own idea of the file's format, and the docstrings
state it. [`test_nightly_planner_integration.py`](../../tests/integration_testing/test_nightly_planner_integration.py)
holds:

- the book's test, finished. It writes a real file with the real writer, runs the planner with the real reader, and
  keeps only the notifier a mock.
- three empty tests for you, each marked `@pytest.mark.skip`. All of them touch the real file system, so all of them
  are integration tests.

## The steps

For each empty test:

1. Write the body with the Arrange / Act / Assert layout of the finished test, using `tmp_path` for the folder.
   - **Missing file:** read an instance that was never written, and check that `MissingResultError` is raised
     (`with pytest.raises(MissingResultError):`).
   - **The writer's own test:** write an infeasible result, then compare the file's text with the exact text you
     expect: `"instance_id,status\n2026-09-26,infeasible\n"`.
   - **The reader's own test:** write that text into the file yourself, without `ResultsWriter`, then check that
     `read` returns the right `SolveResult`.
2. Delete the `@pytest.mark.skip(reason="Exercise: implement me")` line.
3. Run the tests and make sure the new one passes.

Then play the solve job's team changing its format, to see what only the joined test catches:

4. In `results_writer.py`, write the status capitalized: `status = result.status.value.capitalize()`. Update the
   writer's own test to expect `Infeasible`, as that team would. Run the tests: the writer's test passes, the
   reader's test passes, and only the finished test, which joins the two, fails. **Undo both changes.**

You're done when every test passes, `skipped` is 0, and step 4 behaved as described.

## tmp_path in one minute

`tmp_path` is a [pytest fixture](https://docs.pytest.org/en/stable/how-to/tmp_path.html): name it as a parameter of a
test function, and pytest passes in a new, empty temporary folder as a `pathlib.Path`. Each test gets its own folder,
so tests never see each other's files. Use it for the writer and the reader alike:

```python
def test__example(tmp_path: Path) -> None:
    ResultsWriter(tmp_path).write(...)
    text = (tmp_path / "2026-09-26.csv").read_text(encoding="utf-8")
```

## Running the tests

From the root of the repository, with the virtual environment activated:

```bash
pytest tests/integration_testing
```

Before you start, the summary reads:

```
========================= 1 passed, 3 skipped in 0.19s =========================
```
