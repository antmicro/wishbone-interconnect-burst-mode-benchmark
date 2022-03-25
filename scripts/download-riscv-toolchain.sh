#!/bin/sh

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

TOOLCHAIN_RELEASE=2020.08.2
GCC_VERSION=10.1.0
TRIPLET=riscv64-unknown-elf
BASE_URL="https://static.dev.sifive.com/dev-tools/freedom-tools"
HOST_ARCH=x86_64
HOST_OS=linux-ubuntu14

TOOLCHAIN_ARCHIVE=$TRIPLET-gcc-$GCC_VERSION-$TOOLCHAIN_RELEASE-$HOST_ARCH-$HOST_OS.tar.gz
TOOLCHAIN_URL=$BASE_URL/v${TOOLCHAIN_RELEASE%.*}/$TOOLCHAIN_ARCHIVE

wget -nv $TOOLCHAIN_URL
tar -xf $TOOLCHAIN_ARCHIVE
