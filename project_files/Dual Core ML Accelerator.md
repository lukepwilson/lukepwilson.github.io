# Dual-Core ML Accelerator for Attention Mechanism

This is your ECE260B final project — a synthesizable RTL design of a dual-core machine learning accelerator that computes the core operation of transformer attention: **Q·Kᵀ matrix multiplication followed by L1 normalization**, targeting a 1 GHz clock with an eventual RTL-to-GDSII flow.

## What the Hardware Computes

The accelerator implements a simplified attention mechanism. Given 8 query vectors (Q0–Q7, each 8 elements of 8-bit signed integers) and 16 key vectors (K0–K15, same dimensions), it computes:

**Stage 1 — Q·K dot products:** Each Q vector is dotted against all 16 K vectors. Since a single core only has an 8-column MAC array, the 16 K vectors are split across two cores (K0–K7 on core0, K8–K15 on core1). Both cores share the same Q data. The result is an 8×8 partial-sum matrix per core stored in pmem.

**Stage 2 — L1 normalization:** For each row, the normalization denominator is the sum of absolute values across *all 16 columns* (both cores). This requires the two cores to exchange their local row sums via an asynchronous handshake, since they operate on separate clock domains. The normalized output is `abs(QiKj) * 256 / total_row_sum` (Q8 fixed-point with SCALE_BITS=8), written back to pmem.

**Stage 3 (future) — Norm·V multiplication:** The normalized attention weights are multiplied by value vectors (V) using the same MAC array hardware, just with different data loaded. This reuses the existing datapath.

## Architecture

### Top Level: `dual_core.v`

Instantiates two `core_2` instances and two `async_handshake` modules forming a bidirectional CDC bridge. Core0 runs on `clk_core0`, core1 on `clk_core1` (same frequency in the testbench but phase-shifted to exercise the async interface). The cores exchange partial row sums during normalization through 4-phase req/ack handshakes with 2-stage synchronizers.

### Single Core: `core_2.v`

Each core contains:

**Memory hierarchy** — three SRAM blocks (`sram_w16`, 16 entries each): `qmem` (64-bit, stores Q vectors), `kmem` (64-bit, stores K vectors), and `psum_mem` (160-bit, stores 8×20-bit partial sums per row). All SRAMs use active-low CEN/WEN with synchronous read/write.

**MAC array** (`mac_array.v`) — 8 columns of `mac_col` units. Each column holds one K vector and computes its dot product against incoming Q vectors using `mac_8in` (combinational 8-element dot product via a 3-level adder tree). The array operates in systolic Q-chaining mode: during execution, Q tokens enter column 0 and propagate rightward one column per cycle. A `row_store` buffer reassembles the staggered column outputs into complete rows.

**Output FIFO** (`ofifo.v`) — 16-deep FIFO collecting completed rows from the MAC array. Used primarily for testbench verification and pipeline decoupling.

**Normalization FSM** — a 9-state machine (`NORM_IDLE` through `NORM_DONE`) that processes rows one at a time: reads a pmem row, computes the local absolute-value sum, exchanges sums with the other core via the async interface, computes `total_sum = local + remote`, normalizes each element, and writes the result back to pmem.

**17-bit instruction word** — decoded as: `inst[16]` ofifo_rd, `inst[15:12]` qk memory address, `inst[11:8]` pmem address, `inst[7:6]` MAC instruction (00=idle, 01=load K, 10=execute, 11=trigger norm), `inst[5:0]` individual SRAM read/write enables.

### CDC: `async_handshake.v`

A 4-phase protocol: source captures data into `data_hold`, waits one cycle for stability, then asserts `req`. The destination detects `req` rising edge through a 2-stage synchronizer, captures data, asserts `ack`. Source sees `ack` (also through a 2-stage sync), drops `req`, waits for `ack` to fall, then returns to idle. This guarantees data stability across the domain crossing.

### Testbench: `dual_core_tb.v`

Drives both cores with deterministic pseudo-random data (seeded `$random`), computes expected Q·K products and normalized values in software, then verifies hardware outputs column-by-column. The flow is: reset → write Q to both cores' qmem → write K0–K7 to core0's kmem and K8–K15 to core1's kmem → load K into MAC columns → execute Q·K for all 8 rows → flush pipeline → verify OFIFO results → trigger normalization → wait for completion → read back pmem and verify normalized values.

## Key Design Decisions

The systolic Q-chaining mode avoids broadcasting Q to all columns simultaneously, which would create a massive fan-out problem at high frequencies. The `col_id + 1` offset in `mac_col` accounts for one cycle of SRAM read latency during K loading. The normalization uses Verilog `function` blocks (`row_abs_sum`, `normalize_row`) with division — synthesizable but representing the critical path for timing closure. The SRAMs will eventually be hardened as separate macros in the hierarchical PnR flow.

## Project Deliverables by Step

**Step 1:** Single-core Q·K multiplication, synthesis + PnR at 1 GHz (OK to have negative WNS). **Step 2:** Add normalization, behavioral sim verification. **Step 3:** Hierarchical synthesis with hardened SRAMs (M4 top metal, 4μm pin pitch). **Step 4:** Dual-core with async CDC, verified against `kdata_core0/1.txt` and `qdata.txt`. **Step 5:** Optimization and final PnR with power/timing analysis.
