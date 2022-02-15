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


@cocotb.test()
async def test_read(dut):
    adr = 0x10000000
    bus_read = [None, None, None, None]

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_read, acktimeout=3)

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    adr = 0x10000000
    bus_write = [10, 20, 30, 40]

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_write, acktimeout=3)

    clk_gen.kill()


@cocotb.test()
async def test_read_with_write_tail(dut):
    adr = 0x10000000
    bus_read = [None, None, None, None]
    tail = (adr, 1)

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_read, acktimeout=3, end=tail)

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    adr = 0x10000000
    bus_write = [1, 2, 3, 4]
    tail = (adr, None)

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_write, acktimeout=3, end=tail)

    clk_gen.kill()