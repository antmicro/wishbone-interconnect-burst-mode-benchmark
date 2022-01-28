from os import environ

import os
import sys
import cocotb
import logging
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

class WbSRAM(object):
    """
    """
    LOGLEVEL = logging.INFO

    # clock frequency is 50Mhz
    PERIOD = (100, "ps")

    STATUSADDR = 0
    DIRADDR    = 1
    READADDR   = 2
    WRITEADDR  = 3

    def __init(self, dut):
        self._dut = dut
        self.wbs = WishboneMaster(dut, "io_wbs", dut.clock,
                              width=32,   # size of data bus
                              timeout=10) # in clock cycle number

    @cocotb.coroutine
    def reset(self):
        self._dut.reset <= 1
        short_per = Timer(100, units="ns")
        yield short_per
        self._dut.reset <= 1
        yield short_per
        self._dut.reset <= 0
        yield short_per
