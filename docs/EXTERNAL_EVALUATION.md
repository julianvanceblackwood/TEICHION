# External Engineering Evaluation

**Status:** Generation 1 canonical record and chain-state research; Generation 2 SHA-256 compression research is in progress on a separate development branch.

## Engineering problem

If a compromised host controls both evidence storage and its ordering metadata, a later verifier may have limited grounds for trusting the record sequence. TEICHION investigates the narrower property of hardware-owned ordering and a canonical accepted-record representation.

The current design distinguishes an external event occurring from a record being observed, presented, and accepted. Only the acceptance boundary is within the stated claim.

## Reproducible material

- [Implementation status](../README.md#current-state)
- [RTL chain controller and testbench](../README.md#generation-0-chain-state-controller)
- [Canonical Seal Record V1](protocol/CANONICAL_SEAL_RECORD_V1.md)
- [Assurance model](engineering/ASSURANCE_MODEL.md)
- [Threat model](security/THREAT_MODEL.md)

Run the RTL lint and simulation instructions and the Python reference-vector tests in [Verification](../README.md#verification). Record the simulator and Python versions, source revision and output. A passing simulation confirms the checked properties of the testbench, not hardware authenticity.

## Review questions

1. Does the controller preserve sequence and previous-tag state across accepted records?
2. Is the receipt stable under backpressure and are rejected transactions prevented from advancing committed state?
3. Is the canonical byte representation unambiguous across independent implementations?
4. Which resets, power events and replays are *not* covered by persistent-epoch protection?
5. What tests would be needed before claiming hardware-managed cryptographic sealing, protected device keys or physical FPGA assurance?

## Limitations and next gate

Cryptographic datapath, HMAC, protected key storage, persistent anti-rollback, authenticated FPGA configuration and physical security are not implemented or proven on the default branch. The planned next technical boundary is SHA-256 message scheduling and compression validation, not a production root of trust.

## External review

Useful contributions include vector mismatches, reset/backpressure counterexamples, RTL portability findings, hardware trust-boundary critique and independent verification procedures. Provide tool versions, failing stimulus, expected output and observed output. Use repository issues for non-sensitive findings and [SECURITY.md](../SECURITY.md) for security reports.

For private technical discussions, see the [research profile](https://github.com/julianvanceblackwood). No external validation, silicon deployment, investment or partnership is claimed. Public access is not itself a license to reuse or commercialize the design.
