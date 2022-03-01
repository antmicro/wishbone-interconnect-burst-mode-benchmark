TARGET = sram

WRAPPER_SCRIPT = wrappers/generate_$(TARGET).py

all: tb.v dut.v prepare

prepare: tb.v dut.v
	pytest -m compile test.py
	cp mem.init sim_build/

test: tb.v dut.v
	pytest -n `nproc` -m 'not compile' --html=pytest_report.html --self-contained-html test.py

tb.v: wrappers/tb_$(TARGET).v
	cp wrappers/tb_$(TARGET).v ./tb.v

dut.v: $(WRAPPER_SCRIPT) tb.v
	python3 $(WRAPPER_SCRIPT) $(TARGET_OPTIONS)
	mv build/gateware/dut.v .

clean:
	rm -r build sim_build __pycache__ dut.v tb.v results.xml dump.vcd csr.csv pytest_report.html
