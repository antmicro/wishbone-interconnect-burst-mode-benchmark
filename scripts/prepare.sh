#!/bin/bash

BASE_DIR=$PWD

# Install LiteX with dependencies
mkdir litex
cd $BASE_DIR/litex
python3 $BASE_DIR/hw/deps/litex/litex_setup.py --init --install

# Install modified dependencies
cd $BASE_DIR
find hw/deps/ -mindepth 1 -maxdepth 1 -type d -exec $(which pip3) install -e {} \;

# Install test suite dependencies
cd $BASE_DIR/test
pip3 install -r requirements.txt
