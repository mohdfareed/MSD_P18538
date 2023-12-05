#!/usr/bin/env bash

# shell script to setup the python environment for the backend
python -m venv .venv --prompt "backend"  # create the virtual environment
source .venv/bin/activate # activate the virtual environment
pip install -r requirements.txt # install the project requirements
