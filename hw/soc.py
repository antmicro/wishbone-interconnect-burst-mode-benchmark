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

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litescope import LiteScopeAnalyzer


class TestSoC(SoCCore):
    def __init__(self, platform, sys_clk_freq, crg, **kwargs):

        # SoCCore
        SoCCore.__init__(self, platform, sys_clk_freq,
            cpu_type                 = "vexriscv",
            cpu_variant              = "full",
            ident                    = "Interconnect Benchmark SoC",
            ident_version            = True,
            integrated_rom_size      = 0x6000,
            **kwargs)

        # CRG
        self.submodules.crg = crg

        # Additional RAM
        self.add_ram("test_ram", 0x20000000, 0x10000, burst=kwargs["integrated_sram_burst"])

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
