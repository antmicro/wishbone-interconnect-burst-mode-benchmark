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
    adr_inc = int(os.environ.get("adr_inc", "0")) # address increments in bytes
    length = int(os.environ.get("length", "4"))
    sram_fill = int(os.environ.get("sram_fill", "0"))
    fifo_fill = int(os.environ.get("fifo_fill", "0"))

    # prepare data and addresses
    test_data = random.sample(range(0x80000000, 0xffffffff), length)
    ops_read = []
    for i in range(length):
        ops_read.append((adr_base+adr_offset+(i*adr_inc), None))

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    if fifo_fill:
        await harness.fifo_write(test_data)
    if sram_fill:
        await harness.sram_write(adr_offset, test_data)
    responses = await harness.wb_classic_cycle(ops_read, acktimeout=3)

    clk_gen.kill()

    # verify
    for i in range(len(responses)):
        print("{} @ {:08x} ? {}".format(hex(responses[i].datrd), responses[i].adr, bin(test_data[i])))
        assert responses[i].datrd == test_data[i]


@cocotb.test()
async def test_write(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "3489660928")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "0")) # offset from which you want to start (byte addressed)
    adr_inc = int(os.environ.get("adr_inc", "0")) # address increments (byte addressed)
    length = int(os.environ.get("length", "4"))
    sram_fill = int(os.environ.get("sram_fill", "0"))
    fifo_fill = int(os.environ.get("fifo_fill", "0"))

    # prepare data and addresses
    test_data = random.sample(range(0x80000000, 0xffffffff), length)
    ops_write = []
    for i in range(length):
        t = (adr_base+adr_offset+(i*adr_inc), test_data[i])
        print("op: {:08x} @ {:08x}".format(t[1], t[0]))
        ops_write.append(t)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    responses = await harness.wb_classic_cycle(ops_write, acktimeout=3)
    if fifo_fill:
        fifo_rec = await harness.fifo_read(length)
    if sram_fill:
        sram_after = await harness.sram_read(adr_offset, length)

    clk_gen.kill()

    # verify
    for i in range(len(responses)):
        if fifo_fill:
            assert fifo_rec[i] == ops_write[i][1]
        if sram_fill:
            print("{:08x} @ {:08x} ? {}".format(responses[i].datwr, responses[i].adr, sram_after[i]))
            assert sram_after[i] == responses[i].datwr


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
