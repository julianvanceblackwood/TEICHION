# TEICHION

## Hardware-Sealed Security Evidence Boundary

TEICHION is a hardware-security research project built around one problem: after a record is accepted by the hardware boundary, its ordering and chain relationship should remain independently checkable even if the host later becomes untrusted.

TEICHION does not claim that every external event was observed. Its claims are limited to records that cross the acceptance boundary.

## Current state

| Area | Status |
| --- | --- |
| Project stage | Generation 1 complete, Generation 2 scoped |
| RTL | SystemVerilog |
| Hardware state controller | Implemented |
| Canonical Seal Record V1 | Implemented and reference-verified |
| Protocol reference | Python, standard library only |
| RTL verification | Verilator lint, build, simulation |
| Cryptographic datapath | Not implemented |
| Protected device key | Not implemented |
| Persistent epoch | Not implemented |
| Host transport | Not implemented |
| Physical FPGA trust | Not claimed |

Generation 0 established the chain-state controller.

Generation 1 defines the byte representation intended for future cryptographic authentication.

Generation 2 is limited to the SHA-256 compression primitive. Full message hashing, HMAC, key handling, persistence, transport, and deployment remain separate work.

## Why the boundary exists

A host-only evidence path commonly looks like this:

```text
security event
    |
    v
kernel / runtime
    |
    v
collector
    |
    v
host memory / storage
    |
    v
analysis
```

If the host is compromised, both the evidence and the mechanisms preserving it may share the attacker's trust domain.

TEICHION introduces hardware-owned ordering state:

```text
potentially compromised host
            |
            | presented record
            v
+---------------------------------------------+
|              FPGA boundary                  |
|                                             |
|  accept record                              |
|       |                                     |
|       v                                     |
|  allocate sequence                          |
|       |                                     |
|       v                                     |
|  bind previous chain state                  |
|       |                                     |
|       v                                     |
|  cryptographic sealing (future)             |
|       |                                     |
|       v                                     |
|  receipt                                    |
+---------------------------------------------+
            |
            v
independent verification
```

These states are not equivalent:

```text
event occurred
    !=
host observed event
    !=
record was presented
    !=
record was accepted
```

A missing TEICHION record is not proof that an external event did not occur.

## Generation 0: chain-state controller

The current RTL primitive is:

```text
rtl/core/teichion_seal_chain.sv
```

It owns the sequence state, previous accepted tag, pending transaction context, and receipt state for one transaction at a time.

Transaction flow:

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
commit chain state
       |
       v
hold receipt until accepted
       |
       v
IDLE
```

The current `tag_i` input is external. Generation 0 verifies state behavior around that input. It does not claim that the tag is cryptographically authentic.

The current deterministic testbench exercises:

- reset to a zero-state genesis;
- sequential allocation within one reset epoch;
- previous-tag propagation;
- receipt stability under downstream backpressure;
- single-transaction behavior;
- return to request acceptance after receipt completion.

Reset returns the controller to genesis. Sequence continuity is therefore reset-epoch-local, not persistent anti-rollback.

## Generation 1: Canonical Seal Record V1

The canonical record defines one byte representation for an accepted record.

The fixed prefix is 72 bytes:

```text
domain[16] ||
format_version[1] ||
record_kind[1] ||
algorithm_id[1] ||
flags[1] ||
epoch_u64be[8] ||
sequence_u64be[8] ||
payload_length_u32be[4] ||
previous_seal[32] ||
payload[payload_length]
```

Record properties:

- fixed field order and widths;
- unsigned big-endian integers;
- explicit payload length;
- no implicit padding;
- raw payload bytes with no text normalization;
- hardware-owned epoch, sequence, and previous-seal context;
- rejected input does not advance committed chain state.

Normative specification:

```text
docs/protocol/CANONICAL_SEAL_RECORD_V1.md
```

Independent reference:

```text
tools/reference/canonical_record_v1.py
```

Machine-readable vectors:

```text
test_vectors/canonical_seal_record_v1.json
```

## Target cryptographic construction

The planned seal construction is:

```text
Seal[n] =
    HMAC-SHA-256(
        K_device,
        CanonicalSealRecordV1[n]
    )
```

This construction is still a target and is not implemented in RTL.

Cryptographic authenticity requires, at minimum, a verified SHA-256 datapath, HMAC construction, key lifecycle, canonical-record integration, reset and epoch handling, and an independent verifier.

## Verification

### RTL

```bash
verilator \
  --lint-only \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb

verilator \
  --binary \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb

./obj_dir/Vteichion_seal_chain_tb
```

Expected simulation result:

```text
PASS: deterministic sequencing, chain carry, and receipt backpressure verified
```

### Canonical protocol

```bash
python3 -m compileall -q tools/reference tests/reference

python3 tools/reference/canonical_record_v1.py \
  --vectors test_vectors/canonical_seal_record_v1.json

python3 -m unittest discover \
  -s tests/reference \
  -p 'test_*.py' \
  -v
```

These checks cover canonical serialization, rejection behavior, mutations, profile limits, and exact round trips. They do not establish cryptographic authenticity.

## Security limits

Current evidence does not establish:

- complete host telemetry;
- cryptographic authenticity;
- protected key storage;
- persistent anti-rollback;
- secure boot;
- authenticated FPGA configuration;
- side-channel resistance;
- fault-injection resistance;
- physical tamper resistance;
- production root-of-trust status.

The current security boundary is documented in `docs/security/THREAT_MODEL.md`.

## Repository map

```text
TEICHION/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
├── docs/
│   ├── engineering/ASSURANCE_MODEL.md
│   ├── protocol/CANONICAL_SEAL_RECORD_V1.md
│   └── security/THREAT_MODEL.md
├── rtl/core/
├── tb/core/
├── test_vectors/
├── tests/reference/
├── tools/reference/
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## Documentation ownership

Document roles are intentionally separate:

- `README.md`: project overview and current implementation state;
- `docs/engineering/ASSURANCE_MODEL.md`: evidence and claim policy;
- `docs/security/THREAT_MODEL.md`: trust zones, attacker capabilities, and current limits;
- `docs/protocol/CANONICAL_SEAL_RECORD_V1.md`: normative byte-level protocol;
- `SECURITY.md`: vulnerability reporting.

If a summary conflicts with a normative document, the normative document takes precedence.

## Next technical boundary

The next implementation target is a vendor-neutral SHA-256 compression primitive for one 512-bit message block and one 256-bit input chaining state.

The scope is narrower than "SHA-256 support." Padding, arbitrary-length message handling, HMAC, key handling, and canonical-record integration remain separate verification boundaries.
