from os import environ

import os
import sys
import random
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
    # parameters
    adr_base = int(os.environ.get("adr_base", "3489660928")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "0")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))

    # initial rx fifo contents and memory reads
    fifo_fill = random.sample(range(0x1, 0xffffffff), length)
    bus_read = [None for i in fifo_fill]

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_const_adr_burst_cycle(adr_base+adr_offset, bus_read, acktimeout=3)

    harness.count_cycles(responses)

    # verify bus responses from rx fifo
    for i in range(len(responses)):
        assert responses[i].datrd == fifo_fill[i]

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "3489660928")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "0")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))

    # tx fifo writes
    bus_write = random.sample(range(0x1, 0xffffffff), length)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    responses = await harness.wb_const_adr_burst_cycle(adr_base+adr_offset, bus_write, acktimeout=3)
    fifo_rec = await harness.fifo_read(len(bus_write))

    harness.count_cycles(responses)

    # verify tx fifo output
    for i in range(len(responses)):
        harness.dut._log.info("[{}] written from wb: {}, received from fifo: {}".format(i, bin(bus_write[i]), fifo_rec[i]))
        assert fifo_rec[i] == bus_write[i]

    clk_gen.kill()


@cocotb.test(skip=True)
async def test_read_with_write_tail(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "3489660928")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "0")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))

    # initial rx fifo contents and memory reads
    fifo_fill = random.sample(range(0x1, 0xffffffff), length)
    bus_read = [None for i in fifo_fill]
    # tail operation (tx fifo write)
    tail = (adr_base+adr_offset, 1)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_const_adr_burst_cycle(adr_base+adr_offset, bus_read, acktimeout=3, end=tail)
    fifo_rec = await harness.fifo_read(1)

    harness.count_cycles(responses)

    # verify bus responses from rx fifo
    for i in range(len(fifo_fill)):
        assert responses[i].datrd == fifo_fill[i]
    # verify tx fifo output
    assert fifo_rec[0] == tail[1]

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "3489660928")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "0")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))

    # tx fifo writes
    bus_write = random.sample(range(0x1, 0xffffffff), length)

    # rx fifo prefill
    fifo_fill = [6]
    # tail operation (rx fifo write)
    tail = (adr_base+adr_offset, None)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.fifo_write(fifo_fill)
    responses = await harness.wb_const_adr_burst_cycle(adr_base+adr_offset, bus_write, acktimeout=3, end=tail)
    fifo_rec = await harness.fifo_read(len(bus_write))

    harness.count_cycles(responses)

    # verify tx fifo output
    for i in range(len(bus_write)):
        assert fifo_rec[i] == bus_write[i]
    # verify last bus response from rx fifo
    assert responses[-1].datrd == fifo_fill[0]

    clk_gen.kill()
