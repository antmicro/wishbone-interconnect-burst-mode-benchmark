# Burst Mode Interconnect Benchmark

Copyright (c) 2022 Antmicro

A test suite and an example SoC used for testing and benchmarking Wishbone Registered Feedback Bus Cycles implementation in LiteX.

## Preparing environment

This project requires RISC-V GCC toolchain installed and available in $PATH for building benchmark application.

To install test suite and benchmark SoC generator dependencies, use these commands:
```
# apt install verilator gtkwave libevent-dev libjson-c-dev
$ hw/deps/litex/litex_setup.py --init --update
$ pip install --user -e hw/deps/*
$ pip install -r test/requirements.txt
```

## Test suite

This test suite is a set of testbenches and scripts used for verifying Wishbone interconnect implementation compatibility with specification.
Tests are written in Python, using Cocotb simulation library and cocotbext-wishbone extension for testbenches.
Test automation was done with cocotb-test and pytest libraries, with GNU Make used for automating DUT preparing steps.

### Usage

```
$ cd test
$ make
$ make test
```

Waveform dump for each test is being written to the same file, so after running tests you will only have last executed test iteration recorded.
To get a waveform dump for a chosen test, you need to execute it separately:
```
$ # -k parameter contains test name and parameters
$ pytest -k 'test_sram_classic[2-0]' --html=pytest_report.html --self-contained-html test.py
```

## Test SoC

Test SoC is a basic System on Chip design made with LiteX framework for executing benchmarks in more practical environment.

### Building

Assuming you already have installed LiteX and RISC-V GCC toolchain:
```
$ cd hw
$ ./bitstream.py --target=SimSoC
$ ./bitstream.py --target=SimSoC --build
```
and if you have Vivado installed:
```
$ cd hw
$ ./bitstream.py --target=ArtySoC
$ ./bitstream.py --target=ArtySoC --build
```

### Usage

Connect Arty with flashed bitstream to your host's Ethernet interface and set it's IP address to 169.254.10.1/24.
Then connect with litex_server, use litex_term to connect to the serial port and use litescope_cli to trigger the scope and download results.

```
$ litex_server --udp --udp-ip 169.254.10.10
$ litex_term socket://localhost:1111
$ litescope_cli -v simsoc_dbus_dbus_adr 0x10001ef0
```
