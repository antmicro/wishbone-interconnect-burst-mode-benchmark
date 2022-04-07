#!/bin/bash

BASE_DIR=$PWD

# Install LiteX with dependencies
mkdir litex
cd $BASE_DIR/litex
$BASE_DIR/hw/deps/litex/litex_setup.py --init --install --user

# Install modified dependencies
cd $BASE_DIR
find hw/deps/ -mindepth 1 -maxdepth 1 -type d -exec /usr/bin/pip3 install --user -e {} \;

# Install test suite dependencies
cd $BASE_DIR/test
pip3 install -r requirements.txt
