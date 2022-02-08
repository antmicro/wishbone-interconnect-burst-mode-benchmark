# Default to verilog
TOPLEVEL_LANG ?= verilog

PWD=$(shell pwd)

PYTHONPATH := $(PWD)/..:$(PYTHONPATH)

TEST_SCRIPT = test-basic
TARGET = sram

VERILOG_SOURCES = $(PWD)/dut.v $(PWD)/tb.v
TOPLEVEL = tb
WRAPPER_SCRIPT = wrappers/generate_$(TARGET).py
MODULE = tests.$(TEST_SCRIPT)

CUSTOM_COMPILE_DEPS = $(PWD)/dut.v

include $(shell cocotb-config --makefiles)/Makefile.sim

$(PWD)/tb.v: $(PWD)/wrappers/tb_$(TARGET).v
	cp $(PWD)/wrappers/tb_$(TARGET).v ./tb.v

$(PWD)/dut.v: $(WRAPPER_SCRIPT) $(PWD)/tb.v $(TARGET_DEPS)
	cd ..
	python3 $(WRAPPER_SCRIPT) $(TARGET_OPTIONS)
	mv build/gateware/dut.v .

clean-all: clean
	rm -r build dut.v tb.v results.xml dump.vcd csr.csv
