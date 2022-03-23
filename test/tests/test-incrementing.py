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
from .wb_master import WbMaster, wrap_bitmask


@cocotb.test()
async def test_read(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "268435456")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "4")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))
    bte = int(os.environ.get("bte", "0"))
    sram_fill = int(os.environ.get("sram_fill", "0"))
    fifo_fill = int(os.environ.get("fifo_fill", "0"))

    # prepare data and addresses
    prefill = random.sample(range(0x1, 0xffffffff), length)

    # bus data writes
    bus_read = [None for i in range(length)]

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.sram_write(adr_offset, prefill, wrap_bitmask(bte))
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_read, acktimeout=3, bte=bte)

    harness.count_cycles(responses)

    # verify if bus reads match initial RAM contents
    for i in range(len(prefill)):
        assert responses[i].datrd == prefill[i]

    clk_gen.kill()


@cocotb.test()
async def test_write(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "268435456")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "4")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))
    bte = int(os.environ.get("bte", "0"))
    # target RAM contents, starting from offset with wrap lsb masked out
    bus_write = random.sample(range(0x1, 0xffffffff), length)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_write, acktimeout=3, bte=bte)
    sram_read = await harness.sram_read(adr_offset, len(bus_write), wrap_bitmask(bte))

    harness.count_cycles(responses)

    # verify if RAM contents match bus writes
    for i in range(len(bus_write)):
        assert responses[i].datwr == sram_read[i]

    clk_gen.kill()


@cocotb.test(skip=True)
async def test_read_with_write_tail(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "268435456")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "4")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))
    bte = int(os.environ.get("bte", "0"))
    # initial RAM contents, starting from offset with wrap lsb masked out
    prefill = random.sample(range(0x1, 0xffffffff), length)
    # separate single operation executed when ending burst cycle
    tail = (adr_base+adr_offset, 60)

    # bus data writes
    bus_read = [None for i in prefill]

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    await harness.sram_write(adr_offset, prefill, wrap_bitmask(bte))
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_read, acktimeout=3, bte=bte, end=tail)
    sram_post = await harness.sram_read(tail[0] - adr_base, 1)

    harness.count_cycles(responses)

    # get burst operations results sorted by address
    responses_sorted = sorted(responses[:-1], key=lambda a: (a.adr))

    # verify if bus reads match initial RAM contents
    for i in range(len(prefill)):
        assert responses_sorted[i].datrd == prefill[i]

    # verify end operation (changed RAM word match tail write)
    assert sram_post[0] == tail[1]

    clk_gen.kill()


@cocotb.test()
async def test_write_with_read_tail(dut):
    # parameters
    adr_base = int(os.environ.get("adr_base", "268435456")) # base peripheral address (byte addressed, look at csr.csv)
    adr_offset = int(os.environ.get("adr_offset", "4")) # offset from which you want to start (byte addressed)
    length = int(os.environ.get("length", "8"))
    bte = int(os.environ.get("bte", "0"))
    # target RAM contents, starting from offset with wrap lsb masked out
    bus_write = random.sample(range(0x1, 0xffffffff), length)
    # separate single operation executed when ending burst cycle
    tail = (adr_base+adr_offset, None)

    # setup
    harness = WbMaster(dut)
    clk_gen = make_clock(harness.dut, 100)

    # action!
    await harness.reset()
    responses = await harness.wb_inc_adr_burst_cycle(adr_base + adr_offset, bus_write, acktimeout=3, bte=bte, end=tail)
    sram_read = await harness.sram_read(adr_offset, len(bus_write), wrap_bitmask(bte))

    harness.count_cycles(responses)

    # verify if RAM contents match bus writes
    for i in range(len(bus_write)):
        assert bus_write[i] == sram_read[i]

    # verify end operation (read RAM word match previous write)
    assert responses[-1].datrd in bus_write

    clk_gen.kill()
