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
    adr = 0x10000004
    bus_read = [None, None, None, None, None, None, None, None]
    adr_verify = []
    bte = 0b01
    sram = [] # replace with second port access to the prefilled SRAM

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_read, acktimeout=3, bte=bte)

    for res in responses:
        adr_verify.append(res.adr)

    adr_verify_start = min(adr_verify)
    # for i in range(bus_read):
    #     assert responses[i] == sram[adr_verify[i]-adr_verify_start]

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    adr = 0x10000004
    bus_write = [10, 20, 30, 40, 50, 60, 70, 80]
    adr_verify = []
    bte = 0b01
    sram = [] # replace with second port access to the prefilled SRAM

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_write, acktimeout=3, bte=bte)

    for res in responses:
        adr_verify.append(res.adr)

    adr_verify_start = min(adr_verify)
    # for i in range(bus_write):
    #     assert bus_write[adr_verify[i]-adr_verify_start] == sram[adr_verify[i]-adr_verify_start]

    clk_gen.kill()


@cocotb.test()
async def test_read_with_write_tail(dut):
    adr = 0x10000004
    bus_read = [None, None, None, None, None, None, None, None]
    adr_verify = []
    bte = 0b00
    tail = (adr, 1)
    sram = [] # replace with second port access to the prefilled SRAM

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_read, acktimeout=3, bte=bte, end=tail)

    for res in responses[:-1]:
        adr_verify.append(res.adr)

    adr_verify_start = min(adr_verify)
    # for i in range(bus_read):
    #     assert responses[i] == sram[adr_verify[i]-adr_verify_start]

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    adr = 0x10000004
    bus_write = [10, 20, 30, 40, 50, 60, 70, 80]
    adr_verify = []
    bte = 0b00
    tail = (adr, None)
    sram = [] # replace with second port access to the prefilled SRAM

    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr, bus_write, acktimeout=3, bte=bte, end=tail)

    for res in responses[:-1]:
        adr_verify.append(res.adr)

    adr_verify_start = min(adr_verify)
    # for i in range(bus_write):
    #     assert bus_write[adr_verify[i]-adr_verify_start] == sram[adr_verify[i]-adr_verify_start]

    clk_gen.kill()
