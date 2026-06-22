# Analyzing code coverage

Code coverage shows what percentage of the lines of your production code (code under the `src` folder) where touched by at least 1 unit test. `pytest-cov` is a 
library that offers tools to analyze this. Check out their docs here: `https://pytest-cov.readthedocs.io/en/latest/`.

This command will show you the code coverage on each file:

```bash
pytest --cov=src
```

This command prints a table in the terminal showing which line numbers were not executed during the test.

```bash
pytest --cov=src --cov-report=term-missing
```

This command generates a htmlcov/ folder; open htmlcov/index.html in a browser for a color-highlighted view.

```bash
pytest --cov=src --cov-report=html
```
