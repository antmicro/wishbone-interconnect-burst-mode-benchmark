#!/usr/bin/env python3
from migen import Module, Signal, ClockDomain
from migen.fhdl.structure import ClockSignal, ResetSignal

from litex.build.sim.platform import SimPlatform
from litex.build.generic_platform import Pins, Subsignal
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder
from litex.soc.interconnect import wishbone

import argparse

_io = [
    # Wishbone
    ("wishbone", 0,
        Subsignal("adr",   Pins(30)),
        Subsignal("dat_r", Pins(32)),
        Subsignal("dat_w", Pins(32)),
        Subsignal("sel",   Pins(1)),
        Subsignal("cyc",   Pins(1)),
        Subsignal("stb",   Pins(1)),
        Subsignal("ack",   Pins(1)),
        Subsignal("we",    Pins(1)),
        Subsignal("cti",   Pins(3)),
        Subsignal("bte",   Pins(2)),
        Subsignal("err",   Pins(1))),
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


def add_fsm_state_names():
    """Hack the FSM module to add state names to the output"""
    from migen.fhdl.visit import NodeTransformer
    from migen.genlib.fsm import NextState, NextValue, _target_eq
    from migen.fhdl.bitcontainer import value_bits_sign

    class My_LowerNext(NodeTransformer):
        def __init__(self, next_state_signal, next_state_name_signal, encoding,
                     aliases):
            self.next_state_signal = next_state_signal
            self.next_state_name_signal = next_state_name_signal
            self.encoding = encoding
            self.aliases = aliases
            # (target, next_value_ce, next_value)
            self.registers = []

        def _get_register_control(self, target):
            for x in self.registers:
                if _target_eq(target, x[0]):
                    return x[1], x[2]
            raise KeyError

        def visit_unknown(self, node):
            if isinstance(node, NextState):
                try:
                    actual_state = self.aliases[node.state]
                except KeyError:
                    actual_state = node.state
                return [
                    self.next_state_signal.eq(self.encoding[actual_state]),
                    self.next_state_name_signal.eq(
                        int.from_bytes(actual_state.encode(), byteorder="big"))
                ]
            elif isinstance(node, NextValue):
                try:
                    next_value_ce, next_value = self._get_register_control(
                        node.target)
                except KeyError:
                    related = node.target if isinstance(node.target,
                                                        Signal) else None
                    next_value = Signal(bits_sign=value_bits_sign(node.target),
                                        related=related)
                    next_value_ce = Signal(related=related)
                    self.registers.append(
                        (node.target, next_value_ce, next_value))
                return next_value.eq(node.value), next_value_ce.eq(1)
            else:
                return node

    import migen.genlib.fsm as fsm

    def my_lower_controls(self):
        self.state_name = Signal(len(max(self.encoding, key=len)) * 8,
                                 reset=int.from_bytes(
                                     self.reset_state.encode(),
                                     byteorder="big"))
        self.next_state_name = Signal(len(max(self.encoding, key=len)) * 8,
                                      reset=int.from_bytes(
                                          self.reset_state.encode(),
                                          byteorder="big"))
        self.comb += self.next_state_name.eq(self.state_name)
        self.sync += self.state_name.eq(self.next_state_name)
        return My_LowerNext(self.next_state, self.next_state_name,
                            self.encoding, self.state_aliases)

    fsm.FSM._lower_controls = my_lower_controls


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
    add_fsm_state_names()
    output_dir = args.dir
    generate(output_dir, args.csr)

    print("""Simulation build complete.  Output files:
    {}/gateware/dut.v               Source Verilog file. Run this under Cocotb.
""".format(output_dir))


if __name__ == "__main__":
    main()
