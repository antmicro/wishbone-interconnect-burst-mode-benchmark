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
from .wb_master import WbMaster, wrap_bitmask


@cocotb.test()
async def test_read(dut):
    # parameters
    adr_base = 0x10000000 # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = 0x4 # offset from which you want to start (byte addressed)
    bte = 0b01
    # initial RAM contents, starting from offset with wrap lsb masked out
    sram_prefill = [10, 20, 30, 40, 50, 60, 70, 80]

    # bus data writes
    bus_read = [None for i in sram_prefill]

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.sram_write(adr_offset, sram_prefill, wrap_bitmask(bte))
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_read, acktimeout=3, bte=bte)

    # get operations addresses in execution order
    adr_verify = []
    for res in responses:
        adr_verify.append(res.adr)

    # verify if bus reads match initial RAM contents
    adr_verify_start = min(adr_verify)
    for i in range(len(adr_verify)):
        assert responses[i].datrd == sram_prefill[adr_verify[i]-adr_verify_start]

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    # parameters
    adr_base = 0x10000000 # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = 0x4 # offset from which you want to start (byte addressed)
    bte = 0b01
    # target RAM contents, starting from offset with wrap lsb masked out
    bus_write = [10, 20, 30, 40, 50, 60, 70, 80]

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_write, acktimeout=3, bte=bte)
    sram_read = await harness.sram_read(adr_offset, len(bus_write), wrap_bitmask(bte))

    # get operations addresses in execution order
    adr_verify = []
    for res in responses:
        adr_verify.append(res.adr)

    # verify if RAM contents match bus writes
    for i in range(len(adr_verify)):
        assert bus_write[i] == sram_read[i]

    clk_gen.kill()


@cocotb.test()
async def test_read_with_write_tail(dut):
    # parameters
    adr_base = 0x10000000 # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = 0x4 # offset from which you want to start (byte addressed)
    bte = 0b01
    # initial RAM contents, starting from offset with wrap lsb masked out
    sram_prefill = [10, 20, 30, 40, 50, 60, 70, 80]
    # separate single operation executed when ending burst cycle
    tail = (adr_base+adr_offset, 60)

    # bus data writes
    bus_read = [None for i in sram_prefill]

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.sram_write(adr_offset, sram_prefill, wrap_bitmask(bte))
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_read, acktimeout=3, bte=bte, end=tail)

    # get operations addresses in execution order
    adr_verify = []
    for res in responses[:-1]:
        adr_verify.append(res.adr)

    # verify if bus reads match initial RAM contents
    adr_verify_start = min(adr_verify)
    for i in range(len(adr_verify)):
        assert responses[i].datrd == sram_prefill[adr_verify[i]-adr_verify_start]

    # TODO: verify end operation

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    # parameters
    adr_base = 0x10000000 # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = 0x4 # offset from which you want to start (byte addressed)
    bte = 0b01
    # target RAM contents, starting from offset with wrap lsb masked out
    bus_write = [10, 20, 30, 40, 50, 60, 70, 80]
    # separate single operation executed when ending burst cycle
    tail = (adr_base+adr_offset, None)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_write, acktimeout=3, bte=bte, end=tail)
    sram_read = await harness.sram_read(adr_offset, len(bus_write), wrap_bitmask(bte))

    # get operations addresses in execution order
    adr_verify = []
    for res in responses[:-1]:
        adr_verify.append(res.adr)

    # verify if RAM contents match bus writes
    for i in range(len(adr_verify)):
        assert bus_write[i] == sram_read[i]

    # TODO: verify end operation

    clk_gen.kill()
