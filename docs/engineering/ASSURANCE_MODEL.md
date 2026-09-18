# TEICHION Assurance Model

## Purpose

This document defines the minimum evidence required before TEICHION may describe a security-relevant property as TARGET, IMPLEMENTED, or VERIFIED.

It is a repository engineering policy, not a certification claim.

The words **MUST**, **SHOULD**, and **COULD** indicate review priority:

- **MUST** — required for merge or claim promotion;
- **SHOULD** — expected unless a documented reason justifies deviation;
- **COULD** — optional improvement.

## Core rule

> A security claim may advance only as far as its evidence.

A design document can establish intent.

Source code can establish implementation.

A test can establish exercised behavior under defined conditions.

None of these, by itself, proves properties outside its stated assumptions.

## Claim states

### TARGET

A TARGET claim describes intended architecture or future work.

A TARGET claim MUST:

- identify that it is not yet implemented;
- avoid present-tense production language;
- state the boundary it intends to protect;
- identify unresolved dependencies when security relevant.

### IMPLEMENTED

An IMPLEMENTED claim means the mechanism exists in repository source.

An IMPLEMENTED claim MUST:

- point to the implementation boundary;
- define relevant inputs and outputs;
- state reset and failure semantics;
- identify host-controlled or externally controlled values;
- avoid implying verification that has not occurred.

### VERIFIED

A VERIFIED claim means the property is implemented and exercised by reproducible verification.

A VERIFIED claim MUST include:

- a precise property statement;
- a reproducible test or analysis method;
- deterministic pass/fail criteria where practical;
- the tested toolchain or environment;
- explicit assumptions;
- explicit non-properties.

A VERIFIED claim is scoped only to the conditions actually exercised.

## Evidence hierarchy

TEICHION treats the following as progressively stronger forms of evidence, without assuming that one automatically subsumes another:

1. **Design rationale** — explains intended semantics.
2. **Source implementation** — demonstrates that the mechanism exists.
3. **Static analysis / lint** — detects classes of structural or semantic defects.
4. **Deterministic simulation / unit test** — exercises defined behavior.
5. **Adversarial or negative testing** — demonstrates failure behavior and invariant protection.
6. **Independent implementation / verifier** — reduces common-mode interpretation errors.
7. **Formal specification / proof** — demonstrates a property under formal assumptions.
8. **Physical hardware evaluation** — exercises implementation effects absent from simulation.
9. **Independent security review** — challenges assumptions from outside the implementation path.

A later evidence type does not erase the need to document its assumptions.

## Merge gates

Every substantive pull request MUST satisfy the gates relevant to its scope.

### Scope gate

The change MUST correspond to a stated issue, proof obligation, or narrowly defined defect.

Unrelated refactoring MUST NOT be mixed into security-relevant changes.

### Hygiene gate

The change MUST:

- pass `git diff --check`;
- exclude generated artifacts unless explicitly versioned by policy;
- exclude credentials, secrets, private keys, sensitive evidence, and unrelated binary artifacts;
- keep file placement consistent with repository architecture.

### Verification gate

Changes to implemented behavior MUST have a reproducible verification path.

For current Generation 0 RTL, required gates are:

- warning-clean Verilator lint;
- successful executable simulation build;
- deterministic simulation PASS;
- successful GitHub Actions verification.

### Security-boundary gate

A change MUST explicitly state whether it affects:

- trust ownership;
- sequence or epoch state;
- reset behavior;
- acceptance semantics;
- previous-seal state;
- cryptographic inputs or outputs;
- key material;
- persistent state;
- transport framing;
- independent verification.

If affected, the corresponding threat-model documentation MUST be reviewed.

### Claim gate

Documentation MUST NOT get ahead of implementation.

Implementation MUST NOT get ahead of verification claims.

Verification claims MUST NOT extend beyond the tested assumptions.

## Negative evidence

TEICHION MUST distinguish between:

```text
not observed
```

and:

```text
proven not to have occurred
```

The absence of a hardware receipt does not prove that an external event never occurred.

A test that did not detect a failure does not prove absence of all failures.

## Reset and persistence

Any property involving ordering, monotonicity, rollback resistance, or continuity MUST state whether it is:

- combinational;
- transaction-local;
- reset-epoch-local;
- persistent across reset;
- persistent across power loss.

Generation-0 sequence monotonicity is currently reset-epoch-local.

No document may describe it as persistent anti-rollback.

## Cryptographic claims

A cryptographic claim MUST NOT become VERIFIED solely because a standard algorithm name appears in RTL.

Before a cryptographic sealing claim can be promoted, TEICHION SHOULD require at minimum:

- canonical byte-level input specification;
- domain separation;
- deterministic known-answer vectors;
- independently generated reference vectors;
- key-lifecycle definition;
- reset / epoch semantics;
- malformed-input behavior;
- verifier agreement.

Physical side-channel or fault-resistance claims require separate evidence.

## Test quality

A verification artifact SHOULD demonstrate that it can fail.

For important invariants, reviewers SHOULD ask:

> If this invariant were intentionally broken, would the test detect it?

A passing test that cannot detect the protected failure mode is weak evidence.

## Review expectations

Reviewers SHOULD inspect:

- correctness;
- security assumptions;
- state ownership;
- reset behavior;
- error handling;
- malformed input;
- concurrency / backpressure;
- overflow;
- rollback;
- portability;
- performance claims;
- test strength;
- documentation accuracy;
- unnecessary complexity.

## Current Generation-0 assured boundary

Current automated evidence supports the following narrow statement:

> Within one reset epoch, the single-transaction Generation-0 controller deterministically exposes sequence and previous-tag context, advances its chain state after tag acceptance, preserves receipt state under downstream backpressure, and returns to request acceptance after receipt completion.

This statement does not establish:

- cryptographic authenticity;
- trustworthiness of externally supplied `tag_i`;
- persistent anti-rollback;
- telemetry completeness;
- protected key storage;
- physical tamper resistance;
- production FPGA trust.

## Principle

> Assurance is the distance between what the system claims and what its evidence can reproduce. TEICHION should keep that distance as close to zero as possible.
