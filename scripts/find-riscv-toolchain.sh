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

RVTOOLCHAIN_REL_PATH=$(find . -type d -name "riscv64-*" -print -quit)
if [ -z "$RVTOOLCHAIN_REL_PATH" ]
then
      RVTOOLCHAIN_REL_PATH=$(find ./.. -type d -name "riscv64-*" -print -quit)
fi

RVTOOLCHAIN_DIR=$(readlink -f $RVTOOLCHAIN_REL_PATH)

echo "export PATH=\$PATH:$RVTOOLCHAIN_DIR/bin"
