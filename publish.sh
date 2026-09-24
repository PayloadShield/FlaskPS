#!/usr/bin/env bash

# Build and publish flask-payloadshield to PyPI.
set -euo pipefail

if [[ ! -f "pyproject.toml" ]]; then
    echo "Run this script from the FlaskPS project root."
    exit 1
fi

python -m pip install --upgrade build twine
rm -rf build dist flask_payloadshield.egg-info
python -m build
python -m twine check dist/*

if [[ -n "${PYPI_TOKEN:-}" ]]; then
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$PYPI_TOKEN"
fi

python -m twine upload dist/* --skip-existing

echo "Published package: https://pypi.org/project/flask-payloadshield/"
