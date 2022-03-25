#!/bin/bash

BASE_DIR=$PWD

# Install system dependencies
apt-get update -q
apt-get install -q -y build-essential python3-setuptools python3-dev python3-pip git wget ninja-build libevent-dev libjson-c-dev llvm-dev clang nodejs
pip3 install meson

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
