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
