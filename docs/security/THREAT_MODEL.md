# TEICHION Threat Model

## Scope

This document describes the trust boundary implemented by the current repository.

Generation 0 implements deterministic chain-state control around an externally supplied tag result.

Generation 1 defines and reference-verifies Canonical Seal Record V1.

The repository does not yet implement a hardware cryptographic engine, protected key lifecycle, persistent epoch, host transport, or physical FPGA root of trust.

## Security-relevant assets

Current security-relevant state includes:

- next sequence value;
- pending sequence value;
- previous accepted tag;
- pending previous-tag context;
- receipt sequence;
- receipt tag;
- controller transaction state;
- Canonical Seal Record V1 field interpretation and rejection behavior.

The primary concern is unauthorized or ambiguous change to accepted ordering, chain context, or protocol interpretation.

## Trust zones

### Host and upstream environment

The host is not trusted to define authoritative chain ordering.

A compromised or faulty host may:

- forge or alter payloads;
- replay records;
- reorder submissions;
- submit malformed input;
- stall or disconnect;
- lie about timestamps or process identity;
- suppress events before they reach TEICHION.

Suppression before the hardware boundary is outside the current protection model.

### Generation-0 controller

The implemented RTL controller owns:

- sequence allocation;
- previous-tag context capture;
- transaction progression;
- receipt holding behavior.

Within one reset epoch, this is the current hardware-owned ordering boundary.

### External tag producer

The current `tag_i` and `tag_valid_i` interface is outside the cryptographic trust boundary.

Generation 0 accepts the supplied value only to exercise chain-state behavior. It does not establish that the tag is secret-derived, collision resistant, authentic, or produced by trusted hardware.

### Downstream receipt consumer

The downstream consumer may stall receipt acceptance with `receipt_ready_i`.

The controller is expected to preserve visible receipt state while stalled.

The consumer is not yet modeled as a persistent or independent verifier.

### Canonical protocol reference

The Python reference implementation and machine-readable vectors provide independent executable evidence for Canonical Seal Record V1 serialization and rejection behavior.

They are not a cryptographic trust anchor.

## Attacker capabilities in scope

The current model allows a hostile or faulty surrounding environment to:

- assert requests at adversarial times;
- delay context acceptance;
- delay receipt acceptance;
- provide arbitrary tag values;
- control `tag_valid_i` timing;
- reset or power-cycle the design through the external reset boundary;
- replay higher-level host events;
- suppress events before hardware acceptance;
- present malformed or non-canonical protocol input to future framing logic.

Not every capability is mitigated today.

## Properties currently exercised

### Reset state

Reset establishes:

```text
sequence       = 0
previous tag   = 0
pending state  = 0
receipt state  = 0
controller     = IDLE
```

### Reset-epoch ordering

Within one uninterrupted reset epoch, accepted transactions receive sequential 64-bit values beginning at zero.

This is not persistent monotonic state.

### Previous-tag propagation

After a tag result is accepted, the next transaction context observes that value as its previous tag.

### Receipt stability

While `receipt_valid_o` is asserted and `receipt_ready_i` is deasserted, the exercised test keeps receipt sequence and tag stable.

### Single transaction

Generation 0 accepts one transaction at a time.

### Return to acceptance

After the receipt handshake completes, the controller returns to the request-accepting state.

### Canonical V1 behavior

The reference suite exercises:

- fixed field order and widths;
- big-endian integer encoding;
- exact domain and version fields;
- payload profile bounds;
- strict length matching;
- reserved-value rejection;
- malformed and trailing-byte rejection;
- mutation-sensitive canonical bytes.

This is protocol evidence. It does not establish cryptographic authenticity.

## Current non-properties

### Event completeness

If an event never reaches the acceptance boundary, TEICHION cannot determine whether the event never occurred, the host failed to observe it, an upstream component dropped it, or the host suppressed it.

```text
absence of a TEICHION record
            !=
proof of event non-occurrence
```

### Cryptographic authenticity

The current hardware does not compute HMAC-SHA-256 or any other authenticated seal.

### Persistent anti-rollback

Reset returns sequence and previous-tag state to genesis.

The current design does not resist rollback caused by reset, power loss, state restoration, or malicious restart.

### Sequence exhaustion

The sequence register is 64 bits. Production behavior at exhaustion is not implemented.

### Protected key storage

No device secret or protected key lifecycle exists.

### Physical FPGA security

No current claim covers:

- secure boot;
- authenticated bitstreams;
- debug-port hardening;
- eFuse or BBRAM protection;
- probing;
- fault injection;
- side channels;
- physical tamper;
- supply-chain compromise.

### Public verification

The current receipt model is not a public attestation mechanism. Under the target HMAC construction, verification authority depends on the future key model.

## Reset and persistence boundary

Reset is a major unresolved trust transition.

A persistent design must distinguish among first boot, expected reboot, unexpected reset, power interruption, rollback attempts, restored state, and forked chain state.

Persistent ordering must not be claimed until continuity is bound to a protected epoch or another trusted persistence mechanism.

## Backpressure boundary

Backpressure creates state-holding conditions where handshake defects can appear.

Current tests exercise receipt stability. Future verification should extend this to longer context stalls, adversarial handshake timing, reset during each transaction state, unexpected tag-valid behavior, and sequence-boundary conditions.

## Review triggers

Review this threat model whenever implementation changes any of the following:

- trust ownership;
- reset semantics;
- sequence or epoch behavior;
- previous-chain state;
- acceptance semantics;
- canonical serialization;
- tag generation;
- cryptographic primitives;
- key material;
- persistent storage;
- host transport;
- independent verification;
- physical FPGA trust.

## Current boundary summary

TEICHION currently has two independently exercised boundaries:

1. deterministic reset-epoch chain-state behavior around an externally supplied tag;
2. deterministic Canonical Seal Record V1 serialization and rejection behavior.

Cryptographic authenticity, persistent anti-rollback, protected key storage, telemetry completeness, and physical FPGA trust remain outside the implemented boundary.
