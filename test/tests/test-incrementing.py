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
    adr_base = 0x10000000
    adr_offset = 0x4
    bte = 0b01
    sram_prefill = [10, 20, 30, 40, 50, 60, 70, 80]

    adr = adr_base + adr_offset
    wrap_modulo = (2<<bte) if bte > 0 else 1
    bitmask = wrap_modulo-1
    bus_read = [None for i in sram_prefill]
    adr_verify = []

    harness = WbMaster(dut)
    adr_shift = harness.wbs._width//8
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.sram_write((adr_offset // adr_shift) & (~bitmask), sram_prefill)
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_read, acktimeout=3, bte=bte)

    for res in responses:
        adr_verify.append(res.adr)
    adr_verify_start = min(adr_verify)

    for i in range(len(adr_verify)):
        assert responses[i].datrd == sram_prefill[adr_verify[i]-adr_verify_start]

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    adr_base = 0x10000000
    adr_offset = 0x4
    bte = 0b01
    bus_write = [10, 20, 30, 40, 50, 60, 70, 80]

    adr = adr_base + adr_offset
    wrap_modulo = (2<<bte) if bte > 0 else 1
    bitmask = wrap_modulo-1
    adr_verify = []

    harness = WbMaster(dut)
    adr_shift = harness.wbs._width//8
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_write, acktimeout=3, bte=bte)
    sram_read = await harness.sram_read((adr_offset // adr_shift) & (~bitmask), len(bus_write))
    print(sram_read)

    for res in responses:
        adr_verify.append(res.adr)
    adr_verify_start = min(adr_verify)

    for i in range(len(adr_verify)):
        assert bus_write[i] == sram_read[i]

    clk_gen.kill()


@cocotb.test()
async def test_read_with_write_tail(dut):
    adr_base = 0x10000000
    adr_offset = 0x4
    bte = 0b01
    tail = (adr_base+adr_offset, 60)
    sram_prefill = [10, 20, 30, 40, 50, 60, 70, 80]

    adr = adr_base + adr_offset
    wrap_modulo = (2<<bte) if bte > 0 else 1
    bitmask = wrap_modulo-1
    bus_read = [None for i in sram_prefill]
    adr_verify = []

    harness = WbMaster(dut)
    adr_shift = harness.wbs._width//8
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.sram_write((adr_offset // adr_shift) & (~bitmask), sram_prefill)
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_read, acktimeout=3, bte=bte, end=tail)

    for res in responses[:-1]:
        adr_verify.append(res.adr)

    adr_verify_start = min(adr_verify)
    for i in range(len(adr_verify)):
        assert responses[i].datrd == sram_prefill[adr_verify[i]-adr_verify_start]

    # TODO: verify end operation

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    adr_base = 0x10000000
    adr_offset = 0x4
    bte = 0b01
    bus_write = [10, 20, 30, 40, 50, 60, 70, 80]
    tail = (adr_base+adr_offset, None)

    adr = adr_base + adr_offset
    wrap_modulo = (2<<bte) if bte > 0 else 1
    bitmask = wrap_modulo-1
    adr_verify = []

    harness = WbMaster(dut)
    adr_shift = harness.wbs._width//8
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_write, acktimeout=3, bte=bte, end=tail)
    sram_read = await harness.sram_read((adr_offset // adr_shift) & (~bitmask), len(bus_write))
    print(sram_read)

    for res in responses[:-1]:
        adr_verify.append(res.adr)

    adr_verify_start = min(adr_verify)
    for i in range(len(adr_verify)):
        assert bus_write[i] == sram_read[i]

    # TODO: verify end operation

    clk_gen.kill()
