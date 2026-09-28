# Security Policy

TEICHION is a hardware-security research project. The repository is not a production root of trust and should not be used as one.

## Reporting a vulnerability

Do not publish sensitive vulnerability details in a public issue, discussion, pull request, or commit.

Use GitHub private vulnerability reporting when it is available. A useful report includes:

- affected component and revision;
- violated property or invariant;
- conditions required to reproduce the problem;
- minimal reproducer when safe to provide;
- expected and observed behavior;
- realistic impact;
- whether the finding affects implemented behavior or only future architecture.

Do not include live credentials, private keys, customer data, operational evidence, or unnecessary exploit material.

## Current boundary

The implemented hardware boundary is the Generation-0 controller:

```text
rtl/core/teichion_seal_chain.sv
```

Current verification covers deterministic transaction sequencing, previous-tag propagation, and receipt stability under exercised backpressure conditions.

The current `tag_i` input is externally supplied. It is not evidence of cryptographic authenticity.

Canonical Seal Record V1 is specified and exercised by an independent software reference and machine-readable vectors. The repository does not yet implement the hardware cryptographic datapath, protected key lifecycle, persistent epoch, host transport, or physical FPGA trust mechanisms.

The detailed boundary is maintained in:

```text
docs/security/THREAT_MODEL.md
```

## Security-relevant reports

Reports are especially useful when they affect:

- sequence, epoch, or previous-chain state;
- reset and rollback behavior;
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

## Current non-properties

The repository does not currently establish:

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

Findings against an explicitly documented non-property may still be useful as engineering feedback, but they should not be presented as a broken guarantee.

## Disclosure

Provide enough information to reproduce and fix the defect while avoiding unnecessary operational detail.
