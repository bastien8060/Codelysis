#!/bin/bash
chmod 777 * -R
#pip3 --disable-pip-version-check -q install cython --upgrade;
pip --disable-pip-version-check -q --upgrade-strategy to-satisfy-only install -r requirements.txt;
python3 main.py;