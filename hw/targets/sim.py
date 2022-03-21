# -*- coding: utf-8 -*-

from soc import TestSoC

from litex.build.io import CRG
from litex.tools import litex_sim
from litex.build.sim.config import SimConfig
from litex.soc.cores.cpu import CPUS
from liteeth.phy.model import LiteEthPHYModel


class SimSoC(TestSoC):
    toolchain = "verilator"
    local_ip = ""
    remote_ip = ""
    
    def __init__(self, local_ip, remote_ip, **kwargs):
        platform = litex_sim.Platform()
        sys_clk_freq = int(1e6)
        crg = CRG(platform.request("sys_clk"))
        self.local_ip = local_ip
        self.remote_ip = remote_ip

        TestSoC.__init__(self, platform, sys_clk_freq, crg, uart_name="sim", **kwargs)

        # Ethernet / Etherbone
        self.submodules.ethphy = LiteEthPHYModel(self.platform.request("eth", 0))
        self.add_etherbone(phy=self.ethphy, ip_address=self.local_ip)
    
    def get_sim_config(self):
        sim_config = SimConfig()
        sim_config.add_clocker("sys_clk", freq_hz=self.sys_clk_freq)
        cpu = CPUS.get(self.cpu_type)

        # UART
        sim_config.add_module("serial2console", "serial")

        return sim_config
