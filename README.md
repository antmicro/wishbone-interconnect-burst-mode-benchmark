# Burst Mode Interconnect Benchmark

## Building test SoC

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

## Usage

Connect Arty with flashed bitstream to your host's Ethernet interface or start simulation (which will create tap0 interface) and set it's IP address to 169.254.10.1/24.
Then connect with lxserver, boot the benchmark application with lxterm and use litescope_cli to trigger the scope and download results.

```
$ lxserver --udp --udp-ip 169.254.10.10
$ lxterm --serial-boot --kernel build/sim/software/application/application.bin socket://localhost:1111
$ litescope_cli -v simsoc_dbus_dbus_adr 0x10001ef0
```
