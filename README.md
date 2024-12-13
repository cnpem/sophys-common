# sophys-common

A collection of [Bluesky](https://blueskyproject.io) and [Ophyd](https://blueskyproject.io/ophyd) utility code (plans, devices, and other useful stuff) for usage at LNLS/SIRIUS beamlines.

Sophys stands for **S**irius **Oph**yd and Bluesk**y** utilitie**s**. As an old wise monk once said, nothing beats a cool-looking name.

## Installation

This package can be installed via `pip`, via the normal procedure.

## Development

This package uses [`pre-commit`](https://pre-commit.com/) to ensure linting and formatting standards. For local development, it is recommended to install the package with `pip install -e ".[dev]"`, which already installs `pre-commit`, as well as `pytest`. Next, you should run `pre-commit install` so that it checks for formatting and linting mistakes before making a new commit, so you don't forget!

#### Documentation

There's also an HTML documentation, located at the `docs/` subdirectory. It uses sphinx, and some plugins, to do the job.

The online version is located at https://cnpem.github.io/sophys-common/. It is updated manually by a maintainer, usually right after a release or a major change.

To build it locally, go inside the `docs/` folder, where there's a `docs-requirements.txt` file containing the building dependencies. Install those requirements (e.g. via `pip install -r docs-requirements.txt`), and run `make html` to generate the built page. You can access the final result by opening `build/html/index.html`.
