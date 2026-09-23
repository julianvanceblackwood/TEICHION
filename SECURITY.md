# Security Policy

TEICHION is a hardware-security research project. Security reports are welcome, but the repository is not a production root of trust and should not be treated as one.

## Reporting a vulnerability

Do not publish sensitive vulnerability details in a public issue, discussion, pull request, or commit.

Use GitHub's private security reporting path when available. A useful report should include:

- the affected component and revision;
- the violated security property or invariant;
- the conditions required to reproduce the problem;
- a minimal reproducer when safe to provide;
- expected behavior;
- observed behavior;
- realistic impact;
- whether the issue crosses an implemented trust boundary or affects only a future target.

Avoid including live credentials, private keys, customer data, operational evidence, or unnecessary exploit material.

## Current security boundary

The implemented hardware boundary is the Generation-0 seal-chain controller in:

```text
rtl/core/teichion_seal_chain.sv
```

Within the conditions exercised by the current verification suite, the controller provides deterministic transaction sequencing, previous-tag propagation, and receipt stability under downstream backpressure.

The current `tag_i` input is externally supplied. It is not evidence of cryptographic authenticity.

Canonical Seal Record V1 is specified and reference-verified at the byte level, but the hardware cryptographic datapath, protected key lifecycle, persistent epoch, host transport, and physical FPGA trust model are not implemented.

The authoritative security-boundary description is:

```text
docs/security/THREAT_MODEL.md
```

## Security-relevant scope

Reports are especially relevant when they affect:

- sequence or previous-chain state;
- reset or rollback semantics;
- transaction acceptance;
- canonical serialization;
- malformed-input handling;
- receipt stability;
- cryptographic implementation;
- key ownership or lifecycle;
- persistent state;
- host transport;
- independent verification;
- FPGA configuration or boot trust.

## Explicit non-properties

The current repository does not establish:

- complete host telemetry;
- cryptographic authenticity;
- protected key storage;
- persistent anti-rollback;
- secure boot;
- authenticated bitstreams;
- side-channel resistance;
- fault-injection resistance;
- physical tamper resistance;
- production certification.

A missing TEICHION record is not proof that an external event did not occur.

## Claim quality

Security reports and fixes should distinguish:

- **TARGET**: intended architecture;
- **IMPLEMENTED**: mechanism exists in source;
- **VERIFIED**: the stated property is exercised by reproducible evidence.

The normative evidence rules live in `docs/engineering/ASSURANCE_MODEL.md`.

Do not promote a security claim because a primitive name, algorithm name, or future architecture appears in documentation.

## Out-of-scope reports

The following are generally not security vulnerabilities by themselves:

- behavior explicitly documented as a current non-property;
- unsupported production assumptions;
- missing features that are already classified as future work;
- findings that require changing the stated trust model before they become meaningful.

A report may still be valuable as an engineering issue if it identifies ambiguity or an unsafe future dependency.

## Disclosure principle

The goal is simple:

> Preserve enough information to reproduce and fix the defect without exposing unnecessary operational detail.
