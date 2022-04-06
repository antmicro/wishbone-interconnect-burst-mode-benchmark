#!/bin/sh

cd ./hw
python3 ./bitstream.py --bus-bursting --target=SimSoC
python3 ./bitstream.py --bus-bursting --target=SimSoC --build
