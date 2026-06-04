<h1>DEM_dry_granular_flow</h1>

Scripts and notebooks for extracting and post-processing Discrete Element Method (DEM) simulations data from **Rocky 2023 R2** to investigate the influence of porous erodible bed parameters on the mobility and entrainment of granular flow. Developed as part of Camille Huitorel’s PhD research at SLF Davos and ETH Zurich.

![Snapshots](media/default_4snapshots_houdini.png.svg)

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
pip install git+https://github.com/Camille-Huitorel-SLF/DEM_dry_granular_flow.git.git
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

