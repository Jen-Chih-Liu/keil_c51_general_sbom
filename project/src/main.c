/*--------------------------------------------------------------------------
 * Winbond / Nuvoton W78 Series (W78E052D) Standard 8051 Bare-Metal Firmware
 * 
 * Target MCU : W78E052D (Standard 8052 compatible core, 8KB Flash, 256B RAM)
 * Toolchain  : Keil C51
 * BSP        : None (Zero-BSP, standard Keil 8051 header only)
 *--------------------------------------------------------------------------*/

#include <REG52.H>
#include <INTRINS.H>

/* Global initialized variables (triggers ?C_INIT in C51S.LIB) */
volatile unsigned int g_tick_counter = 1000;
volatile unsigned int g_divider = 7;
volatile unsigned char g_tx_buffer = 0xAA;

/* Timer0 Interrupt Service Routine (Standard 8051 Interrupt 1, Vector 0x000B) */
void timer0_isr(void) interrupt 1
{
    /* Reload Timer 0 for 50ms at 11.0592MHz (Mode 1: 16-bit) */
    TH0 = 0x4C;
    TL0 = 0x00;
    
    g_tick_counter++;
    P1 ^= 0x01; /* Toggle LED pin P1.0 */
}

/* UART Initialization: 9600 bps @ 11.0592MHz, Timer 1 Mode 2 */
void uart_init(void)
{
    SCON = 0x50;  /* Mode 1: 8-bit UART, enable receiver */
    TMOD |= 0x20; /* Timer 1 Mode 2: 8-bit auto-reload */
    TH1  = 0xFD;  /* 9600 bps @ 11.0592MHz (SMOD=0) */
    TL1  = 0xFD;
    TR1  = 1;     /* Start Timer 1 */
    TI   = 1;     /* Ready to transmit */
}

/* Timer0 Initialization: 50ms periodic interrupt */
void timer0_init(void)
{
    TMOD = (TMOD & 0xF0) | 0x01; /* Timer 0 Mode 1: 16-bit */
    TH0  = 0x4C;
    TL0  = 0x00;
    ET0  = 1;     /* Enable Timer 0 Interrupt */
    TR0  = 1;     /* Start Timer 0 */
}

/* Simple UART transmit character */
void uart_send_char(unsigned char c)
{
    while (!TI);
    TI = 0;
    SBUF = c;
}

void main(void)
{
    unsigned int computed_val;

    /* Initialize hardware peripherals */
    uart_init();
    timer0_init();
    EA = 1; /* Enable Global Interrupts */

    /* 16-bit integer division / modulo operations
     * This explicitly triggers Keil C51 runtime library helper: ?C?UIDIV in C51S.LIB
     */
    computed_val = g_tick_counter / g_divider;
    
    /* Write results to SFRs so compiler does not optimize them away */
    P2 = (unsigned char)(computed_val & 0xFF);
    P3 = (unsigned char)((computed_val >> 8) & 0xFF);
    uart_send_char((unsigned char)computed_val);

    while (1)
    {
        _nop_();
        if (g_tick_counter > 50000)
        {
            g_tick_counter = 1000;
        }
    }
}
