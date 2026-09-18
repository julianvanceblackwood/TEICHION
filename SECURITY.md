# Security Policy

TEICHION is an FPGA-backed hardware-security research project.

The repository currently contains a Generation-0 deterministic seal-chain controller and its verification environment. It does **not** yet implement a production root of trust, cryptographic sealing engine, protected key store, persistent anti-rollback mechanism, or production FPGA deployment.

Security reports should therefore distinguish between:

- a defect in an implemented or verified property;
- a documentation error that overstates a guarantee;
- an expected limitation that is already documented as out of scope or not yet implemented.

## Reporting a vulnerability

Do **not** publish sensitive vulnerability details, exploit steps, secrets, keys, or proof-of-concept material in a public issue.

Preferred reporting path:

1. Use GitHub's private vulnerability-reporting / security-advisory interface for this repository when it is available.
2. If no private reporting interface is exposed, open only a minimal public issue requesting a private contact channel. Do not include technical exploit details in that issue.

General, non-sensitive defects may be reported through normal GitHub issues.

## Security-relevant scope

Security-relevant reports may include defects involving:

- sequence ownership or allocation;
- previous-tag propagation;
- request/context/receipt handshake semantics;
- receipt stability under backpressure;
- reset or genesis semantics;
- chain-state advancement;
- acceptance-boundary ambiguity;
- verification gaps that permit an invalid security claim to pass;
- future canonical-record parsing or encoding;
- future cryptographic datapaths, key handling, transport, verifier, or persistence logic;
- documentation that incorrectly promotes a TARGET or IMPLEMENTED property to VERIFIED.

## Generation-0 security boundary

Generation 0 verifies a narrow state-machine property.

Within one reset epoch, the current controller is expected to:

- allocate deterministic sequence context;
- carry the previous accepted tag into the next context;
- advance chain state after a tag result is accepted;
- preserve receipt state while the downstream consumer applies backpressure;
- allow only one transaction in flight.

Generation 0 does **not** provide cryptographic authenticity.

The current `tag_i` input is externally supplied. Generation 0 does not prove that this tag was produced by a trustworthy cryptographic engine.

Generation-0 sequence monotonicity is also **intra-epoch**. Reset returns the controller to its explicit genesis state; persistent anti-rollback across reset or power loss is not yet implemented.

## Out-of-scope reports

The following are not vulnerabilities by themselves when they match the documented project state:

- absence of SHA-256 or HMAC hardware;
- absence of device-key provisioning;
- absence of persistent epoch or monotonic storage;
- absence of production secure boot or bitstream-authentication guarantees;
- absence of host transport or cross-platform collectors;
- absence of physical tamper, fault-injection, or side-channel resistance;
- behavior explicitly identified as TARGET rather than IMPLEMENTED or VERIFIED.

A report is still valuable if it demonstrates that an implemented mechanism behaves differently from the documented boundary.

## Report quality

Useful reports should include:

- affected commit or branch;
- exact preconditions;
- reproducible steps;
- observed result;
- expected result;
- security impact;
- whether reset, backpressure, malformed input, or sequence state is involved;
- the smallest reproducer that demonstrates the issue.

If AI tools materially assisted in discovering or preparing the report, disclose that fact and include independently reproduced evidence. AI-generated speculation without reproducible evidence is not sufficient for a security finding.

## Disclosure principle

TEICHION favors precise, evidence-backed disclosure over premature severity claims.

A security claim is accepted only when its trust boundary, assumptions, reproducer, and impact are clear.
