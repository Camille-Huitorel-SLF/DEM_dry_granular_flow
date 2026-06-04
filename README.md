
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11.9](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

Scripts and notebooks for extracting and post-processing Discrete Element Method (DEM) simulations data from **Rocky 2023 R2** to investigate the influence of porous erodible bed parameters on the mobility and entrainment of granular flow. Developed as part of Camille Huitorel’s PhD research at SLF Davos and ETH Zurich.

This repository contains the scripts used in:

<!-- > C. Huitorel et al., "Granular flow over highly porous erodible beds: 3D DEM modelling of
bed mobilisation and entrainment," *Journal Name*, vol. X, pp. X–X, 2026. DOI: [10.XXXX/XXXXX](https://doi.org/10.XXXX/XXXXX) -->


![Reference simulation snapshots](media/default_4snapshots_houdini.png.svg)

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

