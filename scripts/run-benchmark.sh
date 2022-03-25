#!/bin/sh

cd ./hw
python3 ./bitstream.py --burst --target=SimSoC
python3 ./bitstream.py --burst --target=SimSoC --build
