# TEICHION Assurance Model

## Purpose

This document defines how TEICHION describes security-relevant behavior and what evidence is required before a claim is strengthened.

It is an engineering policy for this repository. It is not a certification statement.

Normative terms:

- **MUST**: required;
- **SHOULD**: expected unless there is a documented reason to deviate;
- **MAY**: optional.

## Evidence states

TEICHION uses three states.

### TARGET

The behavior is part of the intended design but is not implemented.

A TARGET statement should identify the boundary it is meant to protect and any unresolved dependency that affects security.

### IMPLEMENTED

The mechanism exists in repository source.

An IMPLEMENTED statement should identify the implementation boundary, relevant inputs and outputs, reset or failure behavior, and externally controlled values.

Implementation alone does not imply that the claimed property has been verified.

### VERIFIED

The mechanism exists and the stated property is exercised by reproducible verification.

A VERIFIED statement must be tied to:

- a precise property;
- a reproducible test or analysis method;
- pass or fail criteria;
- the toolchain or environment used;
- the assumptions under which the result holds.

Verification is limited to the conditions actually exercised.

## Evidence used in this repository

Evidence may include:

1. design rationale;
2. source implementation;
3. lint or static analysis;
4. deterministic simulation or unit tests;
5. negative and adversarial tests;
6. an independent reference implementation or verifier;
7. formal analysis;
8. physical hardware evaluation;
9. independent security review.

These forms of evidence answer different questions. Passing one does not automatically satisfy the others.

For example, simulation can show exercised RTL behavior but cannot establish protected key storage or physical side-channel resistance.

## Merge requirements

A substantive change must have a clear engineering purpose and a reviewable scope.

Security-relevant changes must not hide unrelated refactoring.

Before merge:

- `git diff --check` must pass;
- generated or accidental artifacts must be excluded;
- secrets, credentials, private keys, and sensitive evidence must not be committed;
- verification relevant to the changed boundary must be reproducible;
- existing required gates must remain green;
- documentation must match the implemented behavior.

Current executable gates cover Generation-0 RTL behavior and Canonical Seal Record V1 reference behavior.

## Security-boundary changes

A change requires explicit security review when it affects any of the following:

- ownership of state;
- sequence or epoch semantics;
- previous-chain state;
- reset or rollback behavior;
- record acceptance;
- canonical serialization;
- cryptographic inputs or outputs;
- key material;
- persistent state;
- transport framing;
- independent verification;
- FPGA configuration or boot trust.

If the implemented trust boundary changes, `docs/security/THREAT_MODEL.md` must be reviewed in the same change.

## Negative evidence

TEICHION distinguishes between:

```text
not observed
```

and:

```text
proven not to have occurred
```

A missing receipt does not prove that an external event never occurred.

Likewise, a passing test only supports the behavior and failure modes that the test can actually detect.

## Reset and persistence

Claims involving ordering, continuity, rollback resistance, or monotonicity must state their persistence boundary.

Relevant scopes include:

- transaction-local;
- reset-epoch-local;
- persistent across reset;
- persistent across power loss.

Generation-0 sequence monotonicity is reset-epoch-local. It must not be described as persistent anti-rollback.

## Cryptographic claims

The presence of a standard algorithm name in source or documentation is not cryptographic assurance.

Before TEICHION describes hardware sealing as VERIFIED, the project should have at least:

- a canonical byte-level input contract;
- explicit domain separation;
- independently generated known-answer vectors;
- RTL-to-reference agreement where applicable;
- a defined key lifecycle;
- reset and epoch semantics;
- malformed-input behavior;
- verifier agreement.

Secure boot, authenticated bitstreams, side-channel resistance, fault resistance, and physical tamper resistance require separate evidence.

## Test quality

Important tests should demonstrate that they can fail when the protected invariant is broken.

A useful review question is:

> If this property were intentionally violated, would this test notice?

If the answer is no, the test is not evidence for that property.

## Current supported statements

Current automated evidence supports the following hardware statement:

> Within one reset epoch, the single-transaction Generation-0 controller exposes deterministic sequence and previous-tag context, advances chain state after tag acceptance, preserves receipt state under exercised downstream backpressure, and returns to request acceptance after receipt completion.

Current protocol evidence also supports deterministic Canonical Seal Record V1 serialization and strict rejection behavior against the executable reference corpus.

Neither statement establishes cryptographic authenticity, protected key storage, persistent anti-rollback, telemetry completeness, or physical FPGA trust.
