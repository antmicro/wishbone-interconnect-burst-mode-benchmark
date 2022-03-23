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

from migen import *
from soc import TestSoC

from litex.build.generic_platform import *
from litex.build.io import CRG
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig
from litex.soc.cores.cpu import CPUS
from liteeth.phy.model import LiteEthPHYModel


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),

    # Serial.
    ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid",   Pins(1)),
        Subsignal("sink_ready",   Pins(1)),
        Subsignal("sink_data",    Pins(8)),
    ),

    # Ethernet (Stream Endpoint).
    ("eth_clocks", 0,
        Subsignal("tx", Pins(1)),
        Subsignal("rx", Pins(1)),
    ),
    ("eth", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid",   Pins(1)),
        Subsignal("sink_ready",   Pins(1)),
        Subsignal("sink_data",    Pins(8)),
    ),
]


class SimSoC(TestSoC):
    toolchain = "verilator"
    local_ip = ""
    remote_ip = ""

    def __init__(self, local_ip, remote_ip, **kwargs):
        platform = SimPlatform("SIM", _io)
        sys_clk_freq = int(1e6)
        crg = CRG(platform.request("sys_clk"))
        self.local_ip = local_ip
        self.remote_ip = remote_ip

        TestSoC.__init__(self, platform, sys_clk_freq, crg, uart_name="sim", **kwargs)

        # Ethernet / Etherbone
        self.submodules.ethphy = LiteEthPHYModel(self.platform.request("eth", 0))
        self.add_etherbone(phy=self.ethphy, ip_address=self.local_ip)

        # Simulation debug
        platform.add_debug(self, reset=0)

    def get_sim_config(self):
        sim_config = SimConfig()
        sim_config.add_clocker("sys_clk", freq_hz=self.sys_clk_freq)
        cpu = CPUS.get(self.cpu_type)

        # UART
        sim_config.add_module("serial2console", "serial")

        return sim_config
