`default_nettype none

module teichion_seal_chain #(
    parameter int unsigned TAG_BITS = 256
) (
    input  logic                  clk_i,
    input  logic                  rst_ni,

    input  logic                  request_valid_i,
    output logic                  request_ready_o,

    output logic                  context_valid_o,
    input  logic                  context_ready_i,
    output logic [63:0]           context_sequence_o,
    output logic [TAG_BITS-1:0]   context_previous_tag_o,

    input  logic                  tag_valid_i,
    input  logic [TAG_BITS-1:0]   tag_i,

    output logic                  receipt_valid_o,
    input  logic                  receipt_ready_i,
    output logic [63:0]           receipt_sequence_o,
    output logic [TAG_BITS-1:0]   receipt_tag_o
);

    typedef enum logic [1:0] {
        IDLE,
        SEND_CONTEXT,
        WAIT_TAG,
        HOLD_RECEIPT
    } state_t;

    state_t state_q;

    logic [63:0]         next_sequence_q;
    logic [63:0]         pending_sequence_q;
    logic [63:0]         receipt_sequence_q;

    logic [TAG_BITS-1:0] previous_tag_q;
    logic [TAG_BITS-1:0] pending_previous_tag_q;
    logic [TAG_BITS-1:0] receipt_tag_q;

    always_comb begin
        request_ready_o        = 1'b0;
        context_valid_o        = 1'b0;
        receipt_valid_o        = 1'b0;

        context_sequence_o     = pending_sequence_q;
        context_previous_tag_o = pending_previous_tag_q;

        receipt_sequence_o     = receipt_sequence_q;
        receipt_tag_o          = receipt_tag_q;

        unique case (state_q)
            IDLE: begin
                request_ready_o = 1'b1;
            end

            SEND_CONTEXT: begin
                context_valid_o = 1'b1;
            end

            WAIT_TAG: begin
            end

            HOLD_RECEIPT: begin
                receipt_valid_o = 1'b1;
            end

            default: begin
            end
        endcase
    end

    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            state_q                <= IDLE;

            next_sequence_q        <= 64'd0;
            pending_sequence_q     <= 64'd0;
            receipt_sequence_q     <= 64'd0;

            previous_tag_q         <= '0;
            pending_previous_tag_q <= '0;
            receipt_tag_q          <= '0;
        end else begin
            unique case (state_q)
                IDLE: begin
                    if (request_valid_i && request_ready_o) begin
                        pending_sequence_q     <= next_sequence_q;
                        pending_previous_tag_q <= previous_tag_q;

                        state_q <= SEND_CONTEXT;
                    end
                end

                SEND_CONTEXT: begin
                    if (context_valid_o && context_ready_i) begin
                        state_q <= WAIT_TAG;
                    end
                end

                WAIT_TAG: begin
                    if (tag_valid_i) begin
                        receipt_sequence_q <= pending_sequence_q;
                        receipt_tag_q      <= tag_i;

                        previous_tag_q  <= tag_i;
                        next_sequence_q <= next_sequence_q + 64'd1;

                        state_q <= HOLD_RECEIPT;
                    end
                end

                HOLD_RECEIPT: begin
                    if (receipt_valid_o && receipt_ready_i) begin
                        state_q <= IDLE;
                    end
                end

                default: begin
                    state_q <= IDLE;
                end
            endcase
        end
    end

endmodule

`default_nettype wire
