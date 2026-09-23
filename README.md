# TEICHION

## Hardware-Sealed Security Evidence Boundary

TEICHION explores a narrow systems-security problem:

> After a security record crosses a hardware trust boundary, can its accepted order and chain relationship remain defensible even if the host later becomes untrustworthy?

The project does not assume host telemetry is complete. It separates two questions that are often conflated:

1. Did an event occur?
2. Did a record cross the TEICHION acceptance boundary and become part of the hardware-owned chain?

TEICHION addresses the second question.

A missing TEICHION record is not proof that an external event did not occur.

## Current state

| Area | State |
| --- | --- |
| Project stage | Generation 1 complete, Generation 2 scoped |
| RTL | SystemVerilog |
| Hardware primitive | Deterministic seal-chain state controller |
| Canonical record | V1 specified and reference-verified |
| Protocol verification | Python reference encoder, vectors, negative tests |
| RTL verification | Verilator lint, build, simulation |
| Cryptographic engine | Not implemented |
| Protected device key | Not implemented |
| Persistent epoch | Not implemented |
| Host transport | Not implemented |
| Physical FPGA trust | Not claimed |

Generation 0 established deterministic chain-state semantics.

Generation 1 fixed the byte-exact Canonical Seal Record V1 contract and added an independent reference encoder, machine-readable vectors, strict rejection tests, and a dedicated protocol verification gate.

Generation 2 is scoped around the SHA-256 compression primitive. HMAC, key handling, transport, persistence, and physical deployment remain separate proof boundaries.

## Security model

A simplified host-only evidence path looks like this:

```text
Security event
    |
    v
Kernel / runtime
    |
    v
Collector
    |
    v
Host memory / storage
    |
    v
Analysis
```

If the host is compromised, the mechanisms preserving evidence may share the same trust domain as the attacker.

TEICHION introduces a separate hardware-owned state boundary:

```text
Potentially compromised host
            |
            | presented record
            v
+---------------------------------------------+
|             FPGA trust boundary             |
|                                             |
|  acceptance                                 |
|      |                                      |
|      v                                      |
|  hardware-owned sequence                    |
|      |                                      |
|      v                                      |
|  previous chain state                       |
|      |                                      |
|      v                                      |
|  future cryptographic sealing               |
|      |                                      |
|      v                                      |
|  receipt                                    |
+---------------------------------------------+
            |
            v
Independent verification
```

The important distinction is:

```text
event occurred
    !=
host observed event
    !=
record was presented
    !=
record was accepted
    !=
record received a cryptographic seal
```

Only properties supported by the implemented boundary and reproducible evidence are claimed.

## Generation 0: seal-chain controller

The current RTL primitive is:

```text
rtl/core/teichion_seal_chain.sv
```

It owns:

- the next 64-bit sequence value;
- the pending sequence value;
- the previous accepted tag;
- pending previous-tag context;
- receipt sequence and tag state;
- request, context, tag, and receipt transaction state.

It does not compute SHA-256 or HMAC.

The current `tag_i` input is externally supplied. Generation 0 verifies the state semantics around that result, not its cryptographic origin.

### Transaction flow

```text
request accepted
       |
       v
capture sequence and previous tag
       |
       v
publish context
       |
       v
wait for tag
       |
       v
commit next sequence and previous tag
       |
       v
hold receipt until accepted
       |
       v
return to IDLE
```

Only one transaction is active at a time.

The present priority is unambiguous state ownership and reproducible behavior, not throughput.

### State machine

```text
IDLE
  |
  | request accepted
  v
SEND_CONTEXT
  |
  | context accepted
  v
WAIT_TAG
  |
  | tag_valid_i
  v
HOLD_RECEIPT
  |
  | receipt accepted
  v
IDLE
```

### Verified Generation-0 properties

Under the current deterministic testbench:

- reset establishes sequence zero and zero previous-tag genesis state;
- accepted transactions receive sequential values within one reset epoch;
- the next transaction observes the previous accepted tag;
- receipt state remains stable while downstream acceptance is stalled;
- a second transaction is not accepted while one is active;
- the controller returns to request acceptance after receipt completion.

The strongest current hardware statement is intentionally narrow:

> Within one reset epoch, the Generation-0 controller provides deterministic chain-state sequencing around an externally supplied tag and preserves receipt state under the exercised backpressure conditions.

## Reset and sequence limits

Generation-0 sequence monotonicity is local to one reset epoch.

Reset returns the controller to genesis:

```text
sequence       = 0
previous tag   = 0
pending state  = 0
receipt state  = 0
controller     = IDLE
```

This is not persistent anti-rollback.

The 64-bit sequence space also has no production exhaustion policy yet. A hardened design must define explicit fail-stop or authenticated epoch-transition behavior instead of relying on silent wraparound.

## Canonical Seal Record V1

Generation 1 defines the exact byte sequence intended for future authentication.

The fixed prefix is 72 bytes:

```text
domain[16]
||
format_version[1]
||
record_kind[1]
||
algorithm_id[1]
||
flags[1]
||
epoch_u64be[8]
||
sequence_u64be[8]
||
payload_length_u32be[4]
||
previous_seal[32]
||
payload[payload_length]
```

Key properties:

- fixed field order;
- fixed-width unsigned integers;
- big-endian integer encoding;
- explicit payload length;
- no implicit padding;
- no text normalization;
- no optional-field ambiguity;
- host software does not authoritatively choose epoch, sequence, or previous seal;
- rejected input does not consume committed sequence state.

The normative byte-level contract is in:

```text
docs/protocol/CANONICAL_SEAL_RECORD_V1.md
```

The independent reference implementation is:

```text
tools/reference/canonical_record_v1.py
```

Machine-readable fixtures are in:

```text
test_vectors/canonical_seal_record_v1.json
```

## Target cryptographic construction

The current target construction is:

```text
Seal[n] =
    HMAC-SHA-256(
        K_device,
        CanonicalSealRecordV1[n]
    )
```

This is architecture, not an implemented cryptographic claim.

Before cryptographic authenticity can be claimed, TEICHION still needs:

- a verified SHA-256 datapath;
- HMAC construction and known-answer coverage;
- an explicit key lifecycle;
- reset and epoch semantics;
- canonical-record integration;
- an independent verifier.

Physical FPGA trust requires additional evidence beyond simulation.

## Verification

### RTL gate

Lint:

```bash
verilator \
  --lint-only \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb
```

Build:

```bash
verilator \
  --binary \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb
```

Run:

```bash
./obj_dir/Vteichion_seal_chain_tb
```

Expected result:

```text
PASS: deterministic sequencing, chain carry, and receipt backpressure verified
```

### Canonical protocol gate

```bash
python3 -m compileall -q tools/reference tests/reference

python3 tools/reference/canonical_record_v1.py \
  --vectors test_vectors/canonical_seal_record_v1.json

python3 -m unittest discover \
  -s tests/reference \
  -p 'test_*.py' \
  -v
```

The protocol gate verifies positive serialization fixtures, malformed-input rejection, mutation coverage, profile limits, and exact round-trip behavior.

These tests establish canonical protocol behavior. They do not establish cryptographic authenticity.

## Repository map

```text
TEICHION/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── protocol.yml
│       └── rtl.yml
├── docs/
│   ├── engineering/
│   │   └── ASSURANCE_MODEL.md
│   ├── protocol/
│   │   └── CANONICAL_SEAL_RECORD_V1.md
│   └── security/
│       └── THREAT_MODEL.md
├── rtl/
│   └── core/
│       └── teichion_seal_chain.sv
├── tb/
│   └── core/
│       └── teichion_seal_chain_tb.sv
├── test_vectors/
│   └── canonical_seal_record_v1.json
├── tests/
│   └── reference/
│       └── test_canonical_record_v1.py
├── tools/
│   └── reference/
│       └── canonical_record_v1.py
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## Source of truth

Each document has one primary responsibility:

- `README.md`: project state and architecture overview;
- `docs/engineering/ASSURANCE_MODEL.md`: claim and evidence policy;
- `docs/security/THREAT_MODEL.md`: implemented trust boundary and attacker model;
- `docs/protocol/CANONICAL_SEAL_RECORD_V1.md`: byte-level V1 protocol contract;
- `SECURITY.md`: vulnerability reporting.

When summary text and a normative document differ, the normative document governs.

## Explicit non-properties

TEICHION does not currently establish:

- host telemetry completeness;
- cryptographic authenticity;
- protected key storage;
- persistent anti-rollback;
- secure boot;
- authenticated FPGA configuration;
- side-channel resistance;
- fault-injection resistance;
- physical tamper resistance;
- production FPGA root-of-trust status.

It is also not currently a SIEM, endpoint detection product, TPM replacement, HSM, or complete forensic acquisition platform.

## Assurance discipline

TEICHION uses three claim states:

- **TARGET**: intended architecture, not implemented;
- **IMPLEMENTED**: mechanism exists in source;
- **VERIFIED**: the stated property is exercised by reproducible verification.

The normative rules for moving between these states live in `docs/engineering/ASSURANCE_MODEL.md`.

Core engineering rule:

> A security claim may advance only as far as its evidence.

## Development flow

```text
problem or proof obligation
        |
        v
focused branch
        |
        v
implementation or specification
        |
        v
local verification
        |
        v
pull request
        |
        v
CI and review
        |
        v
merge
```

Changes should remain narrow, auditable, and reproducible. Generated artifacts, unrelated refactors, and unsupported claims do not belong in security-relevant diffs.

## Next proof boundary

The next technical boundary is the SHA-256 compression primitive.

The scope is deliberately limited to one 512-bit message block and one 256-bit input chaining state. Message padding, arbitrary-length hashing, HMAC, key management, canonical-record integration, and protected persistence remain later boundaries.

The objective is not to claim "SHA-256 support" early. The objective is to isolate the compression function, verify it against an independent reference and deterministic vectors, and only then build higher layers.

## Engineering principle

> Move the trust boundary only when the evidence moves with it.
