# TEICHION

## Hardware-Sealed Security Evidence Boundary

TEICHION is an FPGA-backed hardware security research system for preserving the integrity and ordering of security evidence after that evidence crosses a hardware trust boundary.

The project addresses a narrow but difficult problem:

> **If a host becomes compromised, can previously accepted security evidence remain independently resistant to silent rewriting, replay, and reordering?**

TEICHION separates two claims that must never be confused.

```text
Record crossed the FPGA trust boundary
    → TEICHION may provide cryptographic integrity and ordering guarantees.

Record never reached the FPGA trust boundary
    → TEICHION cannot honestly claim that the underlying event did not occur.
```

The system is therefore designed around hardware-sealed evidence, not assumed telemetry completeness.

## Target architecture

```text
Host Security Sources
        ↓
Canonical Event Framing
        ↓
Cross-Platform Transport
        ↓
┌──────────────────────── FPGA TRUST BOUNDARY ────────────────────────┐
│                                                                    │
│  Frame Parser                                                      │
│       ↓                                                            │
│  Monotonic Sequence State                                          │
│       ↓                                                            │
│  Previous Seal State                                               │
│       ↓                                                            │
│  HMAC-SHA-256 Engine                                               │
│       ↓                                                            │
│  Hardware-Sealed Receipt                                           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
        ↓
Independent Verification / Collection
```

## Generation 0

Generation 0 establishes the deterministic hardware state machine required by the future cryptographic sealing pipeline.

Current proof obligations are:

* monotonic sequence allocation;
* deterministic previous-seal propagation;
* explicit reset semantics;
* backpressure-safe context delivery;
* backpressure-safe receipt delivery;
* stable receipt state while the consumer is stalled.

Cryptographic tamper resistance is **not yet claimed** by the Generation-0 controller alone.

That claim becomes valid only after the cryptographic engine, canonical framing rules, key-provisioning model, and verification path are implemented and tested.

## Engineering principle

> **Hardware does not make an unsupported security claim true.**

Every TEICHION guarantee must identify its trust boundary, inputs, state transitions, cryptographic assumptions, and failure conditions.
