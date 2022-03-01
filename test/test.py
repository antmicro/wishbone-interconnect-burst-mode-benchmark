#!/usr/bin/env python3
import os
import csv
import random
import pytest
from cocotb_test.simulator import run

def get_memory_regions():
    data = list(csv.reader(filter(lambda row: row[0] != "#",
                                  open("csr.csv"))))
    output = {}
    for i in data:
        if i[0] == "memory_region":
            output[i[1]] = {"base_address": int(i[2].replace("0x", ""), 16),
                            "size": int(i[3])}
    return output

mem_regs = get_memory_regions()

@pytest.mark.compile
def test_compile():
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-classic",
        compile_only=True,
    )

@pytest.mark.parametrize("offset", range(16))
@pytest.mark.parametrize("length", [1, 2, 4, 8, 16])
def test_sram_classic(offset, length):
    reg = mem_regs["sram"]
    parameters = {
        "adr_base": reg["base_address"],
        "adr_offset": offset,
        "length": length,
        "sram_fill": 1,
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-classic",
        parameters=parameters,
        waves=True,
    )

@pytest.mark.parametrize("offset", range(16))
@pytest.mark.parametrize("length", [1, 2, 4, 8, 16])
@pytest.mark.parametrize("bte", range(4))
def test_sram_incrementing(offset, length, bte):
    reg = mem_regs["sram"]
    parameters = {
        "adr_base": reg["base_address"],
        "adr_offset": offset,
        "length": length,
        "bte": bte,
        "sram_fill": 1,
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-incrementing",
        parameters=parameters,
        waves=True,
    )

@pytest.mark.parametrize("length", [1, 2, 4, 8, 16])
@pytest.mark.parametrize("module", ["tests.test-classic", "tests.test-constant"])
def test_fifo(module, length):
    reg = mem_regs["fifo"]
    parameters = {
        "adr_base": reg["base_address"],
        "length": length,
        "fifo_fill": 1,
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module=module,
        parameters=parameters,
        waves=True,
    )
