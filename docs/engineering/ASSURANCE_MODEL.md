# TEICHION Assurance Model

## Purpose

This document defines when TEICHION may describe a security-relevant property as TARGET, IMPLEMENTED, or VERIFIED.

It is repository policy, not a certification claim.

Normative terms:

- **MUST**: required for merge or claim promotion;
- **SHOULD**: expected unless a documented reason justifies deviation;
- **COULD**: optional improvement.

## Core rule

> A security claim may advance only as far as its evidence.

Design establishes intent. Source establishes implementation. Verification establishes exercised behavior under stated assumptions.

None of those automatically proves properties outside its boundary.

## Claim states

### TARGET

A TARGET claim describes intended architecture or future work.

It MUST:

- be identified as not implemented;
- avoid present-tense production language;
- identify the boundary it is intended to protect;
- identify unresolved security dependencies.

### IMPLEMENTED

An IMPLEMENTED claim means the mechanism exists in repository source.

It MUST:

- identify the implementation boundary;
- define relevant inputs and outputs;
- state reset and failure semantics;
- identify externally controlled values;
- avoid implying verification that has not occurred.

### VERIFIED

A VERIFIED claim means the mechanism exists and the stated property is exercised by reproducible verification.

It MUST include:

- a precise property statement;
- a reproducible method;
- deterministic pass/fail criteria where practical;
- tested toolchain or environment;
- explicit assumptions;
- explicit non-properties.

VERIFIED is always scoped to the conditions actually exercised.

## Evidence classes

TEICHION uses the following evidence classes. They are not interchangeable and a later class does not erase assumptions from earlier work.

1. **Design rationale**: intended semantics.
2. **Source implementation**: mechanism exists.
3. **Static analysis or lint**: structural and semantic checks.
4. **Deterministic simulation or unit tests**: defined behavior is exercised.
5. **Negative or adversarial tests**: failure behavior and invariant protection.
6. **Independent implementation or verifier**: reduces common-mode interpretation error.
7. **Formal analysis**: proves a property under formal assumptions.
8. **Physical hardware evaluation**: exercises effects absent from simulation.
9. **Independent security review**: challenges assumptions outside the implementation path.

## Merge gates

### Scope

A substantive change MUST correspond to a clear engineering problem or proof obligation.

Security-relevant work MUST NOT include unrelated refactors.

### Hygiene

A change MUST:

- pass `git diff --check`;
- exclude accidental generated artifacts;
- exclude secrets, credentials, private keys, and sensitive evidence;
- keep files consistent with repository architecture.

### Verification

Implemented behavior MUST have a reproducible verification path.

Current repository gates include:

- warning-clean Verilator lint;
- executable RTL simulation;
- deterministic Generation-0 PASS result;
- canonical protocol vector reproduction;
- canonical protocol negative tests;
- GitHub Actions execution.

Only gates relevant to the changed boundary are required, but existing gates must remain green.

### Security boundary

A change MUST state whether it affects:

- state ownership;
- sequence or epoch semantics;
- previous-chain state;
- reset or rollback;
- acceptance semantics;
- canonical serialization;
- cryptographic inputs or outputs;
- key material;
- persistent state;
- transport framing;
- independent verification;
- FPGA configuration or boot trust.

If the implemented trust boundary changes, `docs/security/THREAT_MODEL.md` MUST be reviewed.

### Claims

Documentation MUST NOT get ahead of implementation.

Implementation MUST NOT get ahead of verification claims.

Verification claims MUST NOT exceed tested assumptions.

## Negative evidence

TEICHION distinguishes:

```text
not observed
```

from:

```text
proven not to have occurred
```

A missing hardware receipt does not prove that an external event never occurred.

A test that does not expose a failure does not prove that the failure class is impossible.

## Reset and persistence

Any property involving ordering, continuity, rollback resistance, or monotonicity MUST state whether it is:

- transaction-local;
- reset-epoch-local;
- persistent across reset;
- persistent across power loss.

Generation-0 sequence monotonicity is reset-epoch-local.

It MUST NOT be described as persistent anti-rollback.

## Cryptographic claims

A standard algorithm name in source is not cryptographic assurance.

Before a sealing claim can become VERIFIED, TEICHION SHOULD require at minimum:

- a canonical byte-level input contract;
- explicit domain separation;
- independently generated known-answer vectors;
- RTL-to-reference agreement where applicable;
- key-lifecycle definition;
- reset and epoch semantics;
- malformed-input behavior;
- verifier agreement.

Side-channel, fault-resistance, secure-boot, bitstream-authenticity, and physical-tamper claims require separate evidence.

## Test quality

A verification artifact SHOULD demonstrate that it can fail.

For an important invariant, review should ask:

> If this invariant were intentionally broken, would the test detect it?

A passing test that cannot detect the protected failure mode is weak evidence.

## Current assured boundary

Current automated evidence supports this narrow hardware statement:

> Within one reset epoch, the single-transaction Generation-0 controller deterministically exposes sequence and previous-tag context, advances chain state after tag acceptance, preserves receipt state under downstream backpressure, and returns to request acceptance after receipt completion.

Current protocol evidence additionally establishes deterministic Canonical Seal Record V1 serialization and strict rejection behavior against the executable reference corpus.

Neither statement establishes cryptographic authenticity, protected key storage, persistent anti-rollback, telemetry completeness, or physical FPGA trust.

## Principle

> Keep the distance between a security claim and reproducible evidence as close to zero as possible.
