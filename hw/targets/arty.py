# -*- coding: utf-8 -*-

from soc import TestSoC

from litex_boards.platforms import digilent_arty as platform_arty
from litex_boards.targets import digilent_arty as target_arty
from liteeth.phy.mii import LiteEthPHYMII


class ArtySoC(TestSoC):
    toolchain = "vivado"

    def __init__(self, local_ip, **kwargs):
        platform = platform_arty.Platform(variant="a7-35", toolchain=self.toolchain)
        sys_clk_freq = int(100e6)
        crg = target_arty._CRG(platform, sys_clk_freq)

        TestSoC.__init__(self, platform=platform, sys_clk_freq=sys_clk_freq, crg=crg, **kwargs)

        # Ethernet / Etherbone
        self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
        self.add_etherbone(phy=self.ethphy, ip_address=local_ip)
