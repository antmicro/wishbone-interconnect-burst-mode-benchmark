# -*- coding: utf-8 -*-

from soc import TestSoC

from litex.build.io import CRG
from litex.tools import litex_sim
from liteeth.phy.model import LiteEthPHYModel


class SimSoC(TestSoC):
    toolchain = "verilator"
    def __init__(self, eth_ip, **kwargs):
        platform = litex_sim.Platform()
        sys_clk_freq = int(1e6)
        crg = CRG(platform.request("sys_clk"))

        TestSoC.__init__(self, platform=platform, sys_clk_freq=sys_clk_freq, crg=crg, uart_name="sim")

        # Ethernet / Etherbone
        self.submodules.ethphy = LiteEthPHYModel(self.platform.request("eth", 0))
        self.add_ethernet(phy=self.ethphy, dynamic_ip=True)
        self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

    def sim_config():
        return {}