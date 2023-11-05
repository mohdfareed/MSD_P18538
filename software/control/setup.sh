# shell script to setup the python environment for the control software
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
