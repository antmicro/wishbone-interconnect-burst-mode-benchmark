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
            cpu_variant              = "full",
            ident                    = "Interconnect Benchmark SoC",
            ident_version            = True,
            integrated_main_ram_size = 0x2000,
            integrated_rom_size      = 0x6000,
            **kwargs)

        # CRG
        self.submodules.crg = crg

        # Additional RAM
        self.add_ram("test_ram", 0x20000000, 0x10000)

        # LiteScope
        # TODO: What signals could be also monitored?
        analyzer_signals = [
            self.cpu.dbus,
        ]
        self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
            depth        = 960,
            clock_domain = "sys",
            csr_csv      = "analyzer.csv")
        self.add_csr("analyzer")

    def get_sim_config(self):
        return None
