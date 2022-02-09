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


class WbMaster(object):
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
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 3)
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 3)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 3)

    @cocotb.coroutine
    async def wb_classic_cycle(self, requests, idle=0, acktimeout=1):
        ops = []
        result = []
        adr_shift = self.wbs._width//8

        for req in requests:
            ops.append(WBOp(req[0] // adr_shift, req[1], idle=idle, acktimeout=acktimeout))

        responses = await self.wbs.send_cycle(ops)

        for res in responses:
            result.append((res.adr * adr_shift, res.datrd))
        return result