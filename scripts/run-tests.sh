#!/bin/sh

cd ./test
make
NO_WAVES=1 make test
