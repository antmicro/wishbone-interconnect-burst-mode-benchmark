#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021 Antmicro
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

LX_DEPENDENCIES = ["riscv", "icestorm", "yosys", "nextpnr-ice40"]

# Import lxbuildenv to integrate the deps/ directory
import lxbuildenv

import os, os.path, sys
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build import *
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.soc.integration.builder import *
from litex.soc.integration.soc import SoCRegion

from targets.sim import SimSoC
from targets.arty import ArtySoC

kB = 1024


def main():
    targets = dict(filter(lambda item: item[0].endswith("SoC"), globals().items()))

    ## Read and parse arguments
    parser = argparse.ArgumentParser(
        description="Interconnect Benchmark - gateware/BIOS/firmware builder"
    )
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument(
        "--target", default="SimSoC",
        help="Target platform: {} (default=\"SimSoC\")".format(", ".join(targets.keys()))
    )

    # Simulation parameters
    parser.add_argument("--threads",              default=1,               help="Set number of threads (default=1)")
    parser.add_argument("--opt-level",            default="O3",            help="Compilation optimization level")
    parser.add_argument("--sim-debug",            action="store_true",     help="Add simulation debugging modules")
    # IP
    parser.add_argument("--local-ip",             default="169.254.10.10",  help="Local IP address of SoC (default=169.254.10.10)")
    parser.add_argument("--remote-ip",            default="169.254.10.1", help="Remote IP address of TFTP server (default=169.254.10.1)")

    builder_args(parser)
    vivado_build_args(parser)

    parser.set_defaults(csr_csv="csr.csv")
    args = parser.parse_args()

    if (args.target) not in targets.keys():
        print("Unknown target {}".format(args.target))
        exit(1)
    else:
        target = targets[args.target]

    ## Create SoC

    soc = target(local_ip=args.local_ip, remote_ip=args.remote_ip, **soc_kwargs)

    for i in range(4):
        soc.add_constant("LOCALIP{}".format(i+1), int(args.local_ip.split(".")[i]))
    for i in range(4):
        soc.add_constant("REMOTEIP{}".format(i+1), int(args.remote_ip.split(".")[i]))

    # BIOS/software constants
    #soc.add_constant("FLASH_BOOT_ADDRESS", 0x0)

    sim_config = soc.sim_config()

    # Build final SoC
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = {}
    if soc.toolchain == "vivado":
        builder_kwargs = vivado_build_argdict(args)

    #if not args.no_compile_software:
    #    builder.add_software_package("firmware", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sw")))

    builder.build(**builder_kwargs,
                  run        = args.build,
                  sim_config = sim_config,
                  threads    = args.threads,
                  opt_level  = args.opt_level,
                  interactive = True)

if __name__ == "__main__":
    main()
