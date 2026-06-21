# Testing training

[![CI](https://github.com/sefop/training-testing-python/actions/workflows/ci.yml/badge.svg)](https://github.com/sefop/training-testing-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/github/license/sefop/training-testing-python)](LICENSE)

Learn how to:
- Do unit testing
- Interpret code coverage
- Do test-driven development (also known as 'TDD')

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/sefop/training-testing-python.git
cd training-testing-python
```

### 2. Create a virtual environment with python 3.12
```bash
py -3.12 -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run all tests
```bash
pytest
```

## Analyzing code coverage

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

## Exercises

Check out the exercises in the folder [exercises](exercises) for detailed instructions.
