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
    adr = 0xd0000000
    fifo_fill = [10, 20, 30, 40]
    bus_read = [None, None, None, None]

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_const_adr_burst_cycle(adr, bus_read, acktimeout=3)

    for i in range(len(responses)):
        assert responses[i][1] == fifo_fill[i]

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    adr = 0xd0000000
    bus_write = [10, 20, 30, 40]

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_const_adr_burst_cycle(adr, bus_write, acktimeout=3)
    fifo_rec = await harness.fifo_read(len(bus_write))

    for i in range(len(responses)):
        print("[{}] written from wb: {}, received from fifo: {}".format(i, bin(bus_write[i]), fifo_rec[i]))
        assert fifo_rec[i] == bus_write[i]

    clk_gen.kill()


@cocotb.test()
async def test_read_with_write_tail(dut):
    adr = 0xd0000000
    fifo_fill = [10, 20, 30, 40]
    bus_read = [None, None, None, None]
    tail = (adr, 1)

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_const_adr_burst_cycle(adr, bus_read, acktimeout=3, end=tail)
    fifo_rec = await harness.fifo_read(1)

    for i in range(len(fifo_fill)):
        assert responses[i][1] == fifo_fill[i]
    assert fifo_rec[0] == tail[1]

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    adr = 0xd0000000
    bus_write = [1, 2, 3, 4]
    fifo_fill = [6]
    tail = (adr, None)

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_const_adr_burst_cycle(adr, bus_write, acktimeout=3, end=tail)
    fifo_rec = await harness.fifo_read(len(bus_write))

    for i in range(len(bus_write)):
        assert fifo_rec[i] == bus_write[i]
    assert responses[-1][1] == fifo_fill[0]

    clk_gen.kill()
