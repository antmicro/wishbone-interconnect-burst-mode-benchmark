#!/usr/bin/env python3
import os
import csv
import random
import pytest
from cocotb_test.simulator import run

def read_csr(filename):
    file = open(filename)
    data = list(csv.reader(filter(lambda row: row[0] != "#",
                                  file)))
    file.close()
    return data

def get_csr_memory_regions(data):
    output = {}
    for i in data:
        if i[0] == "memory_region":
            output[i[1]] = {"base_address": int(i[2].replace("0x", ""), 16),
                            "size": int(i[3])}
    return output

def get_csr_constants(data):
    output = {}
    for i in data:
        if i[0] == "constant":
            output[i[1]] = i[2]
    return output

csr = read_csr("csr.csv")
mem_regs = get_csr_memory_regions(csr)
consts = get_csr_constants(csr)


@pytest.mark.compile
def test_compile():
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-classic",
        compile_only=True,
    )

@pytest.mark.parametrize("offset", range(0, 16, 4))
@pytest.mark.parametrize("length", [2, 4, 8, 16])
def test_sram_classic(offset, length):
    reg = mem_regs["sram"]
    extra_env = {
        "adr_base": str(reg["base_address"]),
        "adr_offset": str(offset),
        "adr_inc": str(4),
        "length": str(length),
        "sram_fill": str(1),
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-classic",
        extra_env=extra_env,
        waves=True,
    )

@pytest.mark.parametrize("offset", range(0, 16, 4))
@pytest.mark.parametrize("length", [2, 4, 8, 16])
@pytest.mark.parametrize("bte", range(4))
def test_sram_incrementing(offset, length, bte):
    reg = mem_regs["sram"]
    extra_env = {
        "adr_base": str(reg["base_address"]),
        "adr_offset": str(offset),
        "adr_inc": str(4),
        "length": str(length),
        "bte": str(bte),
        "sram_fill": str(1),
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-incrementing",
        extra_env=extra_env,
        waves=True,
    )

@pytest.mark.parametrize("length", range(2,9))
def test_fifo_classic(length):
    reg = mem_regs["fifo"]
    extra_env = {
        "adr_base": str(reg["base_address"]),
        "length": str(length),
        "fifo_fill": str(1),
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-classic",
        extra_env=extra_env,
        waves=True,
    )

@pytest.mark.parametrize("length", range(2,9))
def test_fifo_constant(length):
    reg = mem_regs["fifo"]
    extra_env = {
        "adr_base": str(reg["base_address"]),
        "length": str(length),
        "fifo_fill": str(1),
    }
    run(
        verilog_sources=["dut.v", "tb.v"],
        toplevel="tb",
        module="tests.test-constant",
        extra_env=extra_env,
        waves=True,
    )
