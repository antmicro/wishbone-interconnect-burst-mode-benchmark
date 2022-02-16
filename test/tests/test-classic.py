from os import environ

import os
import sys
import cocotb
import logging
import inspect
from itertools import repeat
from cocotb.triggers import Timer
from cocotb.result import raise_error
from cocotb.result import TestError
from cocotb.result import ReturnValue
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import ClockCycles
from cocotb.binary import BinaryValue
from .common import make_clock
from .wb_master import WbMaster


# TODO: SRAM prefill
@cocotb.test(skip=True)
async def test_read(dut):
    ops_read = [(0x10000000, None), (0x10000004, None), (0x10000008, None), (0x1000000c, None)]
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_classic_cycle(ops_read, acktimeout=3)

    clk_gen.kill()


@cocotb.test()
async def test_read_constant(dut):
    fifo_fill = [10, 20, 30, 40]
    ops_read = [(0xd0000000, None), (0xd0000000, None), (0xd0000000, None), (0xd0000000, None)]
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_classic_cycle(ops_read, acktimeout=3)

    for i in range(len(responses)):
        assert responses[i][1] == fifo_fill[i]

    clk_gen.kill()


@cocotb.test(skip=True)
async def test_write(dut):
    ops_write = [(0x10000000, None), (0x10000004, None), (0x10000008, None), (0x1000000c, None)]
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_classic_cycle(ops_write, acktimeout=3)

    clk_gen.kill()

@cocotb.test()
async def test_write_constant(dut):
    ops_write = [(0xd0000000, 10), (0xd0000000, 20), (0xd0000000, 30), (0xd0000000, 40)]
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_classic_cycle(ops_write, acktimeout=3)
    fifo_rec = await harness.fifo_read(len(ops_write))

    for i in range(len(responses)):
        assert fifo_rec[i] == ops_write[i][1]

    clk_gen.kill()


# TODO: SRAM prefill
@cocotb.test(skip=True)
async def test_readwrite(dut):
    ops_read = [(0x10000000, None), (0x10000004, None), (0x10000008, None), (0x1000000c, None)]
    ops_write = [(0x10000000, 1), (0x10000004, 2), (0x10000008, 3), (0x1000000c, 4)]
    ops_read = [(0x10000000, None), (0x10000004, None), (0x10000008, None), (0x1000000c, None)]
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses_before = await harness.wb_classic_cycle(ops_read, acktimeout=3)
    await harness.wb_classic_cycle(ops_write, acktimeout=3)
    responses_after = await harness.wb_classic_cycle(ops_read, acktimeout=3)

    assert responses_after == ops_write
    assert responses_after != responses_before

    clk_gen.kill()

#@cocotb.test()
#async def test_readmodifywrite(dut):
#    # TODO: add an empty operation to cocotbext-wishbone (negate STB for n cycles)
