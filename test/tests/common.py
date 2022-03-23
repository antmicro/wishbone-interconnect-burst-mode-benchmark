# -*- coding: utf-8 -*-

# Copyright (C) 2022 Antmicro
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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

def make_clock(dut, clock_mhz):
    clk_period_ns = round(1 / clock_mhz * 1000, 2)
    dut._log.info("input clock = %d MHz, period = %.2f ns" % (clock_mhz, clk_period_ns))
    clock = Clock(dut.clk, clk_period_ns, units="ns")
    clock_sig = cocotb.fork(clock.start())
    return clock_sig
