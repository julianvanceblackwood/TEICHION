`timescale 1ns/1ps
`default_nettype none

module teichion_seal_chain_tb;

    localparam int unsigned TAG_BITS = 256;

    localparam logic [TAG_BITS-1:0] TAG_A =
        256'h1111111111111111111111111111111111111111111111111111111111111111;

    localparam logic [TAG_BITS-1:0] TAG_B =
        256'h2222222222222222222222222222222222222222222222222222222222222222;

    logic                clk_i;
    logic                rst_ni;

    logic                request_valid_i;
    logic                request_ready_o;

    logic                context_valid_o;
    logic                context_ready_i;
    logic [63:0]         context_sequence_o;
    logic [TAG_BITS-1:0] context_previous_tag_o;

    logic                tag_valid_i;
    logic [TAG_BITS-1:0] tag_i;

    logic                receipt_valid_o;
    logic                receipt_ready_i;
    logic [63:0]         receipt_sequence_o;
    logic [TAG_BITS-1:0] receipt_tag_o;

    teichion_seal_chain #(
        .TAG_BITS(TAG_BITS)
    ) dut (
        .clk_i                  (clk_i),
        .rst_ni                 (rst_ni),

        .request_valid_i        (request_valid_i),
        .request_ready_o        (request_ready_o),

        .context_valid_o        (context_valid_o),
        .context_ready_i        (context_ready_i),
        .context_sequence_o     (context_sequence_o),
        .context_previous_tag_o (context_previous_tag_o),

        .tag_valid_i            (tag_valid_i),
        .tag_i                  (tag_i),

        .receipt_valid_o        (receipt_valid_o),
        .receipt_ready_i        (receipt_ready_i),
        .receipt_sequence_o     (receipt_sequence_o),
        .receipt_tag_o          (receipt_tag_o)
    );

    always #5 clk_i <= ~clk_i;

    task automatic expect_context(
        input logic [63:0]         expected_sequence,
        input logic [TAG_BITS-1:0] expected_previous_tag
    );
        begin
            if (!context_valid_o) begin
                $fatal(1, "context_valid_o was not asserted");
            end

            if (context_sequence_o !== expected_sequence) begin
                $fatal(
                    1,
                    "sequence mismatch: expected=%0d actual=%0d",
                    expected_sequence,
                    context_sequence_o
                );
            end

            if (context_previous_tag_o !== expected_previous_tag) begin
                $fatal(1, "previous tag mismatch");
            end
        end
    endtask

    task automatic expect_receipt(
        input logic [63:0]         expected_sequence,
        input logic [TAG_BITS-1:0] expected_tag
    );
        begin
            if (!receipt_valid_o) begin
                $fatal(1, "receipt_valid_o was not asserted");
            end

            if (receipt_sequence_o !== expected_sequence) begin
                $fatal(
                    1,
                    "receipt sequence mismatch: expected=%0d actual=%0d",
                    expected_sequence,
                    receipt_sequence_o
                );
            end

            if (receipt_tag_o !== expected_tag) begin
                $fatal(1, "receipt tag mismatch");
            end
        end
    endtask

    initial begin
        clk_i           = 1'b0;
        rst_ni          = 1'b0;

        request_valid_i = 1'b0;
        context_ready_i = 1'b0;

        tag_valid_i     = 1'b0;
        tag_i           = '0;

        receipt_ready_i = 1'b0;

        repeat (3) @(posedge clk_i);

        @(negedge clk_i);
        rst_ni = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        if (!request_ready_o) begin
            $fatal(1, "controller was not ready after reset");
        end

        /*
         * Transaction 0
         */

        request_valid_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        request_valid_i = 1'b0;

        expect_context(
            64'd0,
            '0
        );

        context_ready_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        context_ready_i = 1'b0;

        tag_i       = TAG_A;
        tag_valid_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        tag_valid_i = 1'b0;

        expect_receipt(
            64'd0,
            TAG_A
        );

        repeat (2) begin
            @(posedge clk_i);
            @(negedge clk_i);

            expect_receipt(
                64'd0,
                TAG_A
            );
        end

        receipt_ready_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        receipt_ready_i = 1'b0;

        if (receipt_valid_o) begin
            $fatal(1, "receipt remained valid after handshake");
        end

        /*
         * Transaction 1
         */

        request_valid_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        request_valid_i = 1'b0;

        expect_context(
            64'd1,
            TAG_A
        );

        context_ready_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        context_ready_i = 1'b0;

        tag_i       = TAG_B;
        tag_valid_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        tag_valid_i = 1'b0;

        expect_receipt(
            64'd1,
            TAG_B
        );

        receipt_ready_i = 1'b1;

        @(posedge clk_i);
        @(negedge clk_i);

        receipt_ready_i = 1'b0;

        if (!request_ready_o) begin
            $fatal(1, "controller did not return to IDLE");
        end

        $display(
            "PASS: deterministic sequencing, chain carry, and receipt backpressure verified"
        );

        $finish;
    end

endmodule

`default_nettype wire