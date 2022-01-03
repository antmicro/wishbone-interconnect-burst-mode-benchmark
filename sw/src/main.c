#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <generated/csr.h>

#define ARR_SIZE 64

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
    uint32_t i = 0;
    uint32_t test_arr[ARR_SIZE];
    uint32_t temp = 0xaa;
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif
    uart_init();

    printf("test_arr: 0x%p\n", test_arr);

    for (i=0;i<UINT32_MAX;i++) {}

    printf("uint32_t write\n");
    for (i = 0; i < ARR_SIZE; i++) {
        test_arr[i] = temp;
    }

    printf("uint32_t read\n");
    for (i = 0; i < ARR_SIZE; i++) {
        temp = test_arr[i];
    }

    puts("done");

    while (1) {
    }

    return 0;
}
