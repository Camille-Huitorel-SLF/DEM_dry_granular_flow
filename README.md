<h1>MyProject</h1>

project_description

<h1>Table of Contents</h1>

- [Installation](#installation)
- [Constribute](#constribute)

# Installation

Make sure you have Python installed then:

**1. (Optional) Create and activate a virtual environment:**

```bash
python -m venv venv
venv/Scripts/activate
```

**2. Install the package using pip in your terminal:**

```bash
pip install git+project_url.git
```

# Constribute

**1. Install the package in editable with dev requirements:**

```bash
pip install -e .[dev]
```

**2. Install pre-commit checks:**

```bash
pre-commit install -t pre-commit -t pre-push
```

