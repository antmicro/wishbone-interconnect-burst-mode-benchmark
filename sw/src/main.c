#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <generated/csr.h>

uint64_t system_ticks = 0;

void isr(void);
int main(void);

void isr(void)
{
    unsigned int irqs;

    irqs = irq_pending() & irq_getmask();

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

    printf("Hello, world!\n");

    while (1) {
    }

    return 0;
}
