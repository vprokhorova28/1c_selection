#!/bin/zsh

pip install virtualenv
virtualenv venv
source venv/bin/activate

pip install -r requirements.txt

python3 main.py