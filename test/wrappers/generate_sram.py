#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2022 Antmicro
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from migen import Module, Signal, ClockDomain
from migen.fhdl.structure import ClockSignal, ResetSignal

from litex.build.sim.platform import SimPlatform
from litex.build.generic_platform import Pins, Subsignal
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder
from litex.soc.interconnect import wishbone
from fifo_transceiver import TestFIFOTransceiver

import argparse

_io = [
    # Wishbone
    ("wishbone", 0,
        Subsignal("adr",   Pins(30)),
        Subsignal("dat_r", Pins(32)),
        Subsignal("dat_w", Pins(32)),
        Subsignal("sel",   Pins(4)),
        Subsignal("cyc",   Pins(1)),
        Subsignal("stb",   Pins(1)),
        Subsignal("ack",   Pins(1)),
        Subsignal("we",    Pins(1)),
        Subsignal("cti",   Pins(3)),
        Subsignal("bte",   Pins(2)),
        Subsignal("err",   Pins(1))),
    ("fifo", 0,
        Subsignal("dat_rx", Pins(32)),
        Subsignal("dat_tx", Pins(32)),
        Subsignal("stb_rx", Pins(1)),
        Subsignal("stb_tx", Pins(1)),
        Subsignal("wait_rx", Pins(1)),
        Subsignal("wait_tx", Pins(1))),
    ("sram", 0,
        Subsignal("adr",   Pins(6)),
        Subsignal("dat_r", Pins(32)),
        Subsignal("dat_w", Pins(32)),
        Subsignal("we",    Pins(1))),
    ("clk", 0, Pins(1)),
    ("reset", 0, Pins(1)),
]

_connectors = []


class _CRG(Module):
    def __init__(self, platform):
        clk = platform.request("clk")
        rst = ~platform.request("reset")

        self.clock_domains.cd_sys = ClockDomain()

        self.comb += [
            ClockSignal("sys").eq(clk),
            ResetSignal("sys").eq(rst),
        ]


class Platform(SimPlatform):
    def __init__(self, toolchain="verilator"):
        SimPlatform.__init__(self, "sim",
                             _io, _connectors,
                             toolchain=toolchain)

    def create_programmer(self):
        raise ValueError("Programming is not supported")


def copy_layout_directions(source, target):
    # update target.layout direction values from source.layout
    # as _io does not provide them
    for i, (name, width) in enumerate(target.layout):
        found = list(filter(lambda entry: entry[0] == name, source.layout))
        assert len(found) == 1, 'Layout element not found in source: ' + name
        direction = found[0][2]
        target.layout[i] = (name, width, direction)


class BaseSoC(SoCCore):
    SoCCore.csr_map = {
        "ctrl": 0,  # provided by default (optional)
        "crg": 1,  # user
        "uart_phy": 2,  # provided by default (optional)
        "uart": 3,  # provided by default (optional)
        "identifier_mem": 4,  # provided by default (optional)
        "timer0": 5,  # provided by default (optional)
    }

    SoCCore.mem_map = {
        "rom": 0x00000000,  # (default shadow @0x80000000)
        "sram": 0x10000000,  # (default shadow @0xa0000000)
        "spiflash": 0x20000000,  # (default shadow @0xa0000000)
        "main_ram": 0x40000000,  # (default shadow @0xc0000000)
        "fifo": 0xd0000000,
        "csr": 0xe0000000,
    }

    def __init__(self, platform, output_dir="build", **kwargs):
        self.output_dir = output_dir

        clk_freq = int(12e6)
        self.submodules.crg = _CRG(platform)

        SoCCore.__init__(self, platform, clk_freq,
                         cpu_type=None, integrated_rom_size=0x0,
                         integrated_sram_size=0x100,
                         integrated_main_ram_size=0x0,
                         csr_address_width=14, csr_data_width=32,
                         with_uart=False, with_timer=False
                         )

        class _WishboneBridge(Module):
            def __init__(self, interface):
                self.wishbone = interface

        # expose wishbone master for simulation purpose
        sim_wishbone = wishbone.Interface()

        # connect wishbone to io pins
        wb = self.platform.request('wishbone')
        copy_layout_directions(source=sim_wishbone, target=wb)
        self.comb += wb.connect(sim_wishbone)
        self.add_wb_master(sim_wishbone)

        # SRAM port
        sram_pins = self.platform.request('sram')
        sram_port = self.sram.mem.get_port(write_capable=True)
        self.specials += sram_port
        self.comb += [
            sram_port.adr.eq(sram_pins.adr),
            sram_port.dat_w.eq(sram_pins.dat_w),
            sram_pins.dat_r.eq(sram_port.dat_r),
            sram_port.we.eq(sram_pins.we),
        ]

        # FIFO
        fifo_pins = self.platform.request('fifo')
        self.submodules.fifo = TestFIFOTransceiver(fifo_pins, 8)
        self.add_memory_region("fifo", self.mem_map["fifo"], self.bus.data_width//8, type=[])
        self.add_wb_slave(self.mem_map["fifo"], self.fifo.bus)


def generate(output_dir, csr_csv):
    platform = Platform()
    soc = BaseSoC(platform, cpu_type=None, cpu_variant=None,
                  output_dir=output_dir
                  )
    builder = Builder(soc, output_dir=output_dir,
                      csr_csv=csr_csv, compile_software=False
                      )
    vns = builder.build(run=False, build_name="dut")
    soc.do_exit(vns)


def main():
    parser = argparse.ArgumentParser(
        description="Build test file for SRAM")
    parser.add_argument('--dir',
                        metavar='DIRECTORY',
                        default='build',
                        help='Output directory (defauilt: %(default)s)')
    parser.add_argument('--csr',
                        metavar='CSR',
                        default='csr.csv',
                        help='csr file (default: %(default)s)')
    args = parser.parse_args()
    output_dir = args.dir
    generate(output_dir, args.csr)

    print("""Simulation build complete.  Output files:
    {}/gateware/dut.v               Source Verilog file. Run this under Cocotb.
""".format(output_dir))


if __name__ == "__main__":
    main()
