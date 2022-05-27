# Wishbone Interconnect Burst Mode Benchmark

Copyright (c) 2022 Antmicro

A test suite and an example SoC used for testing and benchmarking the Wishbone Registered Feedback Bus Cycles implementation in LiteX.

## Environment preparation

This project requires the RISC-V GCC toolchain to be installed and available in the $PATH for building benchmark applications.

To install the test suite and the benchmark SoC generator dependencies, use the following commands:
```
# apt install verilator gtkwave libevent-dev libjson-c-dev
$ hw/deps/litex/litex_setup.py --init --update
$ pip install --user -e hw/deps/*
$ pip install -r test/requirements.txt
```

## Test suite

This test suite is a set of testbenches and scripts used for verifying the compatibility of the Wishbone interconnect implementation with the specification.
The tests are written in Python, using the Cocotb simulation library and the cocotbext-wishbone extension for testbenches.
Test automation was done with cocotb-test and pytest libraries, with GNU Make used for automating the steps for preparing the Design Under Test (DUT).

### Usage

```
$ cd test
$ make
$ make test
```

A waveform dump for each test is written to the same file, so after running multiple tests you will only have the last executed test iteration recorded.
To get a waveform dump for a chosen test, you need to execute it separately:
```
$ # -k parameter contains test name and parameters
$ pytest -k 'test_sram_classic[2-0]' --html=pytest_report.html --self-contained-html test.py
```

## Test SoC

The test SoC is a basic System on Chip design made with the LiteX framework for executing benchmarks in a more practical environment.

### Building

Assuming you already have LiteX and the RISC-V GCC toolchain installed:
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

Connect Arty flashed with a bitstream to your host's Ethernet interface and set its IP address to 169.254.10.1/24.
Then connect with litex_server, use litex_term to connect to the serial port and litescope_cli to trigger the scope and download the results.

```
$ litex_server --udp --udp-ip 169.254.10.10
$ litex_term socket://localhost:1111
$ litescope_cli -v simsoc_dbus_dbus_adr 0x10001ef0
```

### Benchmark results

#### Simulated SoC (Verilator, 1 MHz simulated clock):

64 KiB sequential:

|       | w/o bursts  | w/ bursts | difference (% of speed w/o bursts) |
|-------|-------------|-----------|------------------------------------|
| write |   1.6 MiB/s | 1.6 MiB/s | 100.0 %                            |
|  read | 918.3 KiB/s | 1.1 MiB/s | 123.6 %                            |


64 KiB random:

|       | w/o bursts  | w/ bursts   | difference (% of speed w/o bursts) |
|-------|-------------|-------------|------------------------------------|
| write |   1.6 MiB/s |   1.6 MiB/s | 100.0 %                            |
|  read | 122.7 KiB/s | 154.8 KiB/s | 126.2 %                            |


#### SoC on FPGA (Arty A7-35T, 100 MHz clock):

64 KiB sequential:

|       | w/o bursts  | w/ bursts   | difference (% of speed w/o bursts) |
|-------|-------------|-------------|------------------------------------|
| write | 166.6 MiB/s | 166.6 MiB/s | 100.0 %                            |
|  read |  87.2 MiB/s | 110.4 MiB/s | 126.6 %                            |


64 KiB random:

|       | w/o bursts  | w/ bursts   | difference (% of speed w/o bursts) |
|-------|-------------|-------------|------------------------------------|
| write | 166.6 MiB/s | 166.7 MiB/s | 100.0 %                            |
|  read |  11.6 MiB/s |  14.7 MiB/s | 126.7 %                            |

The VexRiscv core used in this SoC uses write-through L1 instructions and data cache.
Write speed hasn't changed, because it is limited by the speed of slower memory, 
L1 cache in this case.
