# -*- coding: utf-8 -*-

from migen import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy
from litescope import LiteScopeAnalyzer

from litex.tools.litex_sim import *

class TestSoC(SoCCore):
    def __init__(self, platform, sys_clk_freq, crg, **kwargs):

        # SoCCore
        SoCCore.__init__(self, platform, sys_clk_freq,
            cpu_type                 = "vexriscv",
            cpu_variant              = "full+debug", 
            ident                    = "Interconnect Benchmark SoC",
            ident_version            = True,
            integrated_main_ram_size = 0x10000,
            integrated_rom_size      = 0x8000,
            **kwargs)
        
        # CRG
        self.submodules.crg = crg

        # LiteScope
        # TODO: replace analyzed signals with AXI when used
        analyzer_signals = [
            self.cpu.ibus,
            self.cpu.dbus,
        ]
        self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
            depth        = 1024,
            clock_domain = "sys",
            csr_csv      = "analyzer.csv")
        self.add_csr("analyzer")
    
    def sim_config(self):
        return None
