# Burst Mode Interconnect Benchmark

## Building

Assuming you already have installed YosysHQ OSS CAD Suite, LiteX and RISC-V GCC toolchain:
```
# apt install verilator gtkwave libevent-dev libjson-c-dev
$ cd hw
$ ./bitstream.py --target=SimSoC --build
```
and if you have Vivado installed:
```
$ ./bitstream.py --target=ArtySoC --build
```
