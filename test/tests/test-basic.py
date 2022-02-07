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
from cocotbext.wishbone.driver import WishboneMaster
from cocotbext.wishbone.driver import WBOp


def make_clock(dut, clock_mhz):
    clk_period_ns = round(1 / clock_mhz * 1000, 2)
    dut._log.info("input clock = %d MHz, period = %.2f ns" % (clock_mhz, clk_period_ns))
    clock = Clock(dut.clk, clk_period_ns, units="ns")
    clock_sig = cocotb.fork(clock.start())
    return clock_sig


class WbSRAM(object):
    def __init__(self, dut, **kwargs):
        self.dut = dut
        self.wbs = WishboneMaster(self.dut, "io_wbs", self.dut.clk,
                              width=32,   # size of data bus
                              timeout=10) # in clock cycle number

        # Set the signal "test_name" to match this test
        test_name = kwargs.get('test_name', inspect.stack()[1][3])
        tn = cocotb.binary.BinaryValue(value=test_name.encode(), n_bits=4096)
        self.dut.test_name.value = tn

    @cocotb.coroutine
    async def reset(self):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 5)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 5)
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 5)

    @cocotb.coroutine
    async def wb_read(self, adr):
        result = await self.wbs.send_cycle([WBOp(adr >> 2, acktimeout=3)])
        for rec in result:
            self.log.debug("wb read: {}".format(rec))
        raise ReturnValue(result[-1].datrd)

    @cocotb.coroutine
    async def wb_write(self, adr, data):
        result = await self.wbs.send_cycle([WBOp(adr >> 2, data, acktimeout=3)])
        for rec in result:
            self.log.debug("wb write: {}".format(rec))
        raise ReturnValue(0)


@cocotb.test()
async def test_read(dut):
    address = 0x10000000
    harness = WbSRAM(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    value = await harness.wb_read(address)

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    address = 0x10000000
    value = 4
    harness = WbSRAM(dut)
    clk_gen = make_clock(harness.dut, 100)

    await harness.reset()
    await harness.wb_write(address, value)
    assert await harness.wb_read(address) == value

    clk_gen.kill()
