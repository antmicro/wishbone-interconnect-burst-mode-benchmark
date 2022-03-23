/*
Copyright (C) 2022 Antmicro

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <generated/csr.h>
#include <generated/mem.h>
#include <libbase/uart.h>
#include <libbase/memtest.h>

#define TEST_ADDR TEST_RAM_BASE
#define TEST_SIZE TEST_RAM_SIZE

int main(void);

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif
    uart_init();

    printf("%s\n\n", MEM_REGIONS);
    printf(":%x@%p\n", TEST_SIZE, (void *)TEST_ADDR);

#ifdef CSR_SIM_TRACE_BASE
    /* Start tracing */
    sim_trace_enable_write(1);
#endif

    puts(":A");
#ifdef CSR_SIM_MARKER_BASE
    sim_marker_marker_write(1);
#endif
    memtest((unsigned int *)TEST_ADDR, TEST_SIZE);
    puts(":B");
#ifdef CSR_SIM_MARKER_BASE
    sim_marker_marker_write(2);
#endif
    memspeed((unsigned int *)TEST_ADDR, TEST_SIZE, 0, 0);
    puts(":C");
#ifdef CSR_SIM_MARKER_BASE
    sim_marker_marker_write(3);
#endif
    memspeed((unsigned int *)TEST_ADDR, TEST_SIZE, 0, 1);
#ifdef CSR_SIM_MARKER_BASE
    sim_marker_marker_write(0);
#endif
    puts(":D");

    /* Finish simulation */
#ifdef CSR_SIM_TRACE_BASE
    sim_trace_enable_write(0);
#endif
#ifdef CSR_SIM_FINISH_BASE
    sim_finish_finish_write(1);
#endif

    return 0;
}
