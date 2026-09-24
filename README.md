# Sofware Engineering Training in Python

[![CI](https://github.com/sefop/training-testing-python/actions/workflows/ci.yml/badge.svg)](https://github.com/sefop/training-testing-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/github/license/sefop/training-testing-python)](LICENSE)

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

### 4. Run all tests to verify the repo runs ok
```bash
pytest
```

## Exercises

1. Unit tests and code coverage: [`src/unit_tests_and_coverage`](src/unit_tests_and_coverage/README.md)

Check out the [exercises](exercises) folder for the instructions of the other exercises.
