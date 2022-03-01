`timescale 100ps / 1ps

module tb(
  input clk,
  input reset,
  input [29:0] io_wbs_adr,
  input [31:0] io_wbs_datwr,
  output [31:0] io_wbs_datrd,
  input io_wbs_cyc,
  input io_wbs_stb,
  output io_wbs_ack,
  input io_wbs_we,
  input io_wbs_sel,
  input io_wbs_err,
  input [2:0] io_wbs_cti,
  input wire [1:0] io_wbs_bte,
  input [31:0] io_fifo_dat_rx,
  output [31:0] io_fifo_dat_tx,
  input wire io_fifo_stb_rx,
  output wire io_fifo_stb_tx,
  output wire io_fifo_wait_rx,
  output wire io_fifo_wait_tx,
  input  wire [5:0] io_sram_adr,
  output wire [31:0] io_sram_datrd,
  input  wire [31:0] io_sram_datwr,
  input  wire io_sram_we,
	input [4095:0] test_name
);

  dut dut(
    .clk(clk),
    .reset(reset),
    .wishbone_adr(io_wbs_adr),
    .wishbone_dat_r(io_wbs_datrd),
    .wishbone_dat_w(io_wbs_datwr),
    .wishbone_cyc(io_wbs_cyc),
    .wishbone_stb(io_wbs_stb),
    .wishbone_ack(io_wbs_ack),
    .wishbone_we(io_wbs_we),
    .wishbone_sel({io_wbs_sel, io_wbs_sel, io_wbs_sel, io_wbs_sel}),
    .wishbone_cti(io_wbs_cti),
    .wishbone_bte(io_wbs_bte),
    .wishbone_err(io_wbs_err),
    .fifo_dat_rx(io_fifo_dat_rx),
    .fifo_dat_tx(io_fifo_dat_tx),
    .fifo_stb_rx(io_fifo_stb_rx),
    .fifo_stb_tx(io_fifo_stb_tx),
    .fifo_wait_rx(io_fifo_wait_rx),
    .fifo_wait_tx(io_fifo_wait_tx),
    .sram_adr(io_sram_adr),
    .sram_dat_r(io_sram_datrd),
    .sram_dat_w(io_sram_datwr),
    .sram_we(io_sram_we)
  );

  // Dump waves
  //initial begin
    //$dumpfile("dump.vcd");
    //$dumpvars(0, tb);
  //end

endmodule
