from migen import *
from migen.fhdl.specials import Tristate
from migen.genlib.fifo import SyncFIFO

from litex.soc.interconnect import wishbone


class TestFIFOTransceiver(Module):
    # Example module supporting constant address burst cycles,
    # could be later adapted into Wishbone2CSR
    def __init__(self, pads, fifo_depth=8, wait=True):
        # Wishbone bus
        self.bus = bus = wishbone.Interface()
        rd_ack = Signal()
        wr_ack = Signal()
        bus_sel = Signal()
        # Select ACK source
        self.comb += [
            bus_sel.eq(bus.cyc & bus.stb),
            If(bus_sel,
                If(bus.we, 
                    bus.ack.eq(wr_ack & bus.stb),
                ).Else(
                    bus.ack.eq(rd_ack & bus.stb),
                ),
            ).Else(
                bus.ack.eq(0)
            )
        ]

        # Receiver FIFO (outside -> SoC)
        self.submodules.fifo_rx = fifo_rx = SyncFIFO(bus.data_width, fifo_depth)
        self.comb += [
            # Connect RX FIFO input with pads
            fifo_rx.din.eq(pads.dat_rx),
            pads.wait_rx.eq(fifo_rx.writable),
            fifo_rx.we.eq(pads.stb_rx),
        ]

        # Transmitter FIFO (SoC -> outside)
        self.submodules.fifo_tx = fifo_tx = SyncFIFO(bus.data_width, fifo_depth)
        bus_write = Signal()
        self.comb += [
            # Connect TX FIFO output with pads
            pads.dat_tx.eq(fifo_tx.dout),
            pads.wait_tx.eq(fifo_tx.readable),
            fifo_tx.re.eq(pads.stb_tx),
        ]

        # Wishbone FSM
        self.submodules.fsm = fsm = FSM(reset_state="IDLE")
        fsm.act("IDLE",
            If(bus_sel,
                If(bus.we,
                    NextState("WRITE")
                ).Else(
                    NextState("READ")
                )
            )
        )
        fsm.act("READ",
            If(bus_sel & fifo_rx.readable,
                bus.dat_r.eq(fifo_rx.dout),
                fifo_rx.re.eq(1),
                rd_ack.eq(1),
            ).Else(
                bus.dat_r.eq(0xdeadbeef),
                fifo_rx.re.eq(0),
                rd_ack.eq(0),
            ),
            # If constant addr. burst, then repeat, else return to idle
            If(bus_sel & (bus.cti == 0b001),
                NextState("READ")
            ).Else(
                NextState("IDLE")
            )
        )
        fsm.act("WRITE",
            fifo_tx.din.eq(bus.dat_w),
            If(fifo_tx.writable,
                # ACK on WB and TX FIFO input
                fifo_tx.we.eq(1),
                wr_ack.eq(1),
            ).Else(
                fifo_tx.we.eq(0),
                wr_ack.eq(0),
            ),
            # If constant addr. burst, then repeat, else return to idle
            If(bus_sel & (bus.cti == 0b001),
                NextState("WRITE")
            ).Else(
                NextState("IDLE")
            )
        )