#!/bin/bash

cd ./hw
python3 ./bitstream.py --bus-bursting --target=ArtySoC
python3 ./bitstream.py --bus-bursting --target=ArtySoC --build
