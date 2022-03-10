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

uint64_t system_ticks = 0;

void isr(void);
int main(void);


void isr(void)
{
    unsigned int irqs;

    irqs = irq_pending() & irq_getmask();

    if (irqs & (1 << UART_INTERRUPT)) {
        uart_isr();
    }

    if (irqs & (1 << TIMER0_INTERRUPT)) {
        system_ticks++;
        timer0_ev_pending_write(1);
    }
}

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif
    uart_init();

    printf("%s\n\n", MEM_REGIONS);
    printf(":%x@%p\n", TEST_SIZE, (void *)TEST_ADDR);

    puts(":A");
    memtest((unsigned int *)TEST_ADDR, TEST_SIZE);
    puts(":B");
    memspeed((unsigned int *)TEST_ADDR, TEST_SIZE, 0, 0);
    puts(":C");
    memspeed((unsigned int *)TEST_ADDR, TEST_SIZE, 0, 1);
    puts(":D");

    return 0;
}
