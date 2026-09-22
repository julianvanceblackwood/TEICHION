# TEICHION Canonical Seal Record V1

## Status

**Document state: IMPLEMENTED specification**

**Cryptographic enforcement state: TARGET**

This document defines the byte-exact record that a future TEICHION cryptographic datapath is intended to authenticate.

It does not claim that HMAC-SHA-256, protected device keys, persistent epochs, or an independent verifier are implemented today.

No cryptographic-authenticity claim may be promoted to IMPLEMENTED or VERIFIED merely because this specification exists.

---

## 1. Purpose

Generation 0 established deterministic chain-state semantics.

Generation 1 removes the next source of ambiguity:

> **Which exact bytes does TEICHION authenticate?**

A cryptographic primitive can be implemented correctly while the surrounding protocol remains insecure or non-interoperable if two components disagree about:

- field order;
- integer width;
- byte order;
- length;
- version;
- domain;
- reset context;
- previous-chain state;
- acceptance semantics.

TEICHION therefore defines one canonical byte representation before the cryptographic datapath becomes authoritative.

---

## 2. Design constraints

Canonical Seal Record V1 is designed around the following constraints.

### 2.1 One logical accepted record, one byte sequence

For any accepted logical record and hardware context, there MUST be exactly one canonical authentication input.

Alternative encodings of the same logical record are not permitted.

### 2.2 Minimal parser ambiguity

The canonical authentication input uses:

- fixed field order;
- fixed-width integers;
- unsigned integers only;
- big-endian integer encoding;
- fixed-width domain and chain fields;
- one explicit payload-length field;
- raw payload bytes with no text normalization.

No map, schema negotiation, variable-width integer, implicit padding, or optional-field encoding exists in V1.

### 2.3 Hardware-owned ordering truth

The host MUST NOT authoritatively choose:

- epoch;
- sequence;
- previous seal.

Those values belong to the hardware-side chain context.

### 2.4 Rejection must not silently mutate committed chain state

Malformed, incomplete, oversized, or unsupported input MUST NOT advance committed sequence state or previous-seal state.

### 2.5 Reset limitations remain explicit

V1 includes an epoch field so reset-era context is authenticated.

The existence of the field does **not** establish trusted epoch persistence.

Until a protected epoch source exists, persistent anti-rollback remains unimplemented.

---

## 3. Terminology

### Presented record

Input offered to TEICHION by an upstream transport or host-facing interface.

Presentation alone does not mean the record crossed the trusted acceptance boundary.

### Accepted record

A complete input that passed the V1 acceptance rules and was assigned hardware-owned chain context.

### Canonical seal record

The exact byte sequence authenticated by the future cryptographic engine.

### Receipt

A structured result that communicates the accepted chain context and resulting seal to a downstream verifier or collector.

### Committed chain state

The sequence and previous-seal state that will govern the next accepted transaction.

---

## 4. Primitive encodings

All multi-byte integers use **network byte order / big-endian**.

No signed integers exist in V1.

| Type | Width | Encoding |
| --- | ---: | --- |
| `u8` | 1 byte | unsigned integer |
| `u32be` | 4 bytes | unsigned, most-significant byte first |
| `u64be` | 8 bytes | unsigned, most-significant byte first |
| `bytes[N]` | N bytes | uninterpreted octets |

There is no variable-width integer representation.

There is no alignment padding between fields.

---

## 5. Canonical authentication input

The future V1 sealing operation is defined conceptually as:

```text
Seal =
    HMAC-SHA-256(
        K_device,
        CanonicalSealRecordV1
    )
```

where `CanonicalSealRecordV1` is the byte sequence defined below.

**HMAC-SHA-256 is the TARGET algorithm for this specification. It is not yet implemented in TEICHION hardware.**

The device key is not serialized into the record.

---

## 6. Canonical Seal Record V1 layout

The fixed prefix is exactly **72 bytes**.

The payload begins at byte offset 72.

| Offset | Size | Field | Ownership | V1 rule |
| ---: | ---: | --- | --- | --- |
| 0 | 16 | `domain` | protocol constant | exact bytes for `TEICHION-SEAL-V1` |
| 16 | 1 | `format_version` | protocol constant | `0x01` |
| 17 | 1 | `record_kind` | protocol constant | `0x01` = evidence record |
| 18 | 1 | `algorithm_id` | protocol constant | `0x01` = target HMAC-SHA-256 |
| 19 | 1 | `flags` | protocol constant | MUST be `0x00` |
| 20 | 8 | `epoch` | hardware context | `u64be` |
| 28 | 8 | `sequence` | hardware context | `u64be` |
| 36 | 4 | `payload_length` | derived at acceptance | `u32be` |
| 40 | 32 | `previous_seal` | hardware context | 256-bit previous accepted seal |
| 72 | N | `payload` | upstream supplied | exactly `payload_length` raw bytes |

Total encoded length:

```text
72 + payload_length
```

There are no trailing bytes.

---

## 7. Domain separation

The first 16 bytes MUST be exactly:

```text
ASCII: TEICHION-SEAL-V1
HEX:   54 45 49 43 48 49 4f 4e 2d 53 45 41 4c 2d 56 31
```

This constant separates the V1 TEICHION seal-record domain from unrelated authenticated objects.

A future incompatible seal-record format MUST use a different domain value.

A parser MUST reject a presented internal record representation whose domain does not exactly match the expected V1 domain.

---

## 8. Version

`format_version` MUST equal:

```text
0x01
```

The domain string and version byte intentionally both bind V1.

A mismatch is an error, not a negotiation request.

V1 has no version-negotiation mechanism.

---

## 9. Record kind

V1 currently defines one record kind:

```text
0x01 = evidence record
```

All other values are reserved.

An unsupported value MUST be rejected before committed chain state advances.

---

## 10. Algorithm identifier

V1 reserves:

```text
0x01 = HMAC-SHA-256
```

This identifier defines intended cryptographic interpretation.

It does not claim that the algorithm is implemented merely because the identifier is present.

Unknown algorithm identifiers MUST be rejected.

A future algorithm change that alters verification semantics SHOULD receive a new identifier and MUST be reviewed for domain-separation consequences.

---

## 11. Flags

`flags` MUST equal:

```text
0x00
```

All bits are reserved in V1.

A receiver MUST reject a non-zero V1 flags field.

This rule prevents undefined flag bits from creating multiple accepted interpretations of the same logical record.

---

## 12. Epoch

`epoch` is an unsigned 64-bit big-endian value.

The field is intended to bind a record to a reset / continuity context.

### Ownership

The authoritative epoch MUST come from the hardware trust boundary or a future protected continuity mechanism.

The host MUST NOT be able to override the authoritative value.

### Current maturity

Generation 0 does not implement a trusted persistent epoch.

Reference vectors may use epoch zero.

That does not make epoch zero a production anti-rollback mechanism.

### Required future property

Before TEICHION claims persistent anti-rollback, the project must define how epochs survive or securely transition across:

- reset;
- power loss;
- restart;
- state restoration;
- rollback attempts.

---

## 13. Sequence

`sequence` is an unsigned 64-bit big-endian value.

### Ownership

The authoritative sequence is hardware-owned.

The host MUST NOT provide the accepted sequence value.

### V1 ordering rule

Within one trusted epoch, accepted records are assigned monotonically increasing sequence values.

### Exhaustion

V1 does not permit silent security-semantic wraparound.

Before sequence `0xffffffffffffffff` can be followed by another accepted record, the implementation MUST enter a defined fail-stop or authenticated epoch-transition behavior.

Generation 1 does not yet choose the production persistence mechanism.

---

## 14. Payload length

`payload_length` is an unsigned 32-bit big-endian integer.

It represents the exact number of payload bytes authenticated after the fixed 72-byte prefix.

### Derivation

The canonical value MUST be derived from the accepted payload.

A host-declared transport length is not authoritative unless the hardware parser verifies it against the received frame.

### Generation-1 profile limit

The initial Generation-1 reference profile defines:

```text
GEN1_MAX_PAYLOAD = 4096 bytes
```

This is an implementation-profile limit, not an intrinsic limit of the 32-bit field.

A future profile may increase the accepted maximum without changing the V1 byte layout, provided interoperability and resource-exhaustion consequences are reviewed.

### Zero length

A zero-length payload is structurally valid in V1.

Higher-level application semantics may later impose stricter rules.

---

## 15. Previous seal

`previous_seal` is exactly 32 bytes.

For non-genesis records it contains the previous committed V1 seal in the same epoch.

For the first record of an epoch, the V1 genesis value is:

```text
32 bytes of 0x00
```

The previous seal is hardware-owned chain context.

The host MUST NOT be able to substitute a different accepted previous-seal value.

---

## 16. Payload

The payload is an uninterpreted byte string.

V1 performs no:

- Unicode normalization;
- character-set conversion;
- whitespace normalization;
- JSON canonicalization;
- decompression;
- implicit padding;
- line-ending conversion.

The authenticated payload is exactly the accepted octet sequence.

If a higher layer needs structured evidence, that layer must define its own deterministic representation before producing payload bytes.

---

## 17. Acceptance boundary

The security-relevant transition is:

```text
PRESENTED
    ↓
COMPLETE FRAME RECEIVED
    ↓
STRUCTURAL VALIDATION
    ↓
PROFILE LIMIT VALIDATION
    ↓
HARDWARE CONTEXT SNAPSHOT
    ↓
ACCEPTED
    ↓
CANONICAL SEAL RECORD
```

Presentation is not acceptance.

A transport writing bytes toward TEICHION does not by itself prove that the bytes entered the accepted evidence chain.

---

## 18. Acceptance requirements

A V1 record may become accepted only when all of the following hold:

1. the complete presented payload is available;
2. the payload length is known exactly;
3. the payload length does not exceed `GEN1_MAX_PAYLOAD`;
4. the protocol version is supported;
5. the record kind is supported;
6. the algorithm identifier is supported;
7. all reserved flags are zero;
8. no trailing or truncated bytes remain in the enclosing frame;
9. hardware chain context can be snapshotted without violating current transaction state.

Transport-specific framing is intentionally outside this document.

The transport specification must eventually prove how conditions 1 through 9 are established.

---

## 19. Rejection semantics

Rejected input MUST NOT change committed:

- next sequence;
- previous seal;
- epoch continuity state;
- receipt state.

A rejected presentation MUST NOT produce a successful receipt.

An implementation may use temporary internal state while validating a frame, but that state must not become externally observable committed chain advancement.

Examples requiring rejection include:

- unsupported version;
- unsupported record kind;
- unsupported algorithm identifier;
- non-zero reserved flags;
- payload beyond the active profile maximum;
- declared-length mismatch;
- truncated frame;
- trailing bytes where the enclosing framing contract forbids them.

---

## 20. Sequence consumption rule

A malformed or rejected input consumes **no committed sequence number**.

The sequence becomes part of an accepted transaction only after structural acceptance.

The existing Generation-0 implementation already delays permanent sequence advancement until tag acceptance; future integration must preserve an equivalent no-silent-consumption invariant for rejected records.

---

## 21. Chain commit rule

For a future integrated cryptographic pipeline, committed chain state may advance only after the cryptographic result associated with the accepted context is successfully produced and accepted by the chain controller.

Conceptually:

```text
Accepted record
      ↓
Canonical bytes
      ↓
Seal result
      ↓
Receipt state established
      ↓
Commit next sequence + previous seal
```

The precise cycle-level integration belongs to a later RTL issue.

---

## 22. Receipt V1

A receipt is not the authenticated record itself.

It is a verifier-facing representation of the accepted context and resulting seal.

The proposed V1 receipt encoding is exactly **104 bytes**:

| Offset | Size | Field | Rule |
| ---: | ---: | --- | --- |
| 0 | 16 | `receipt_domain` | exact bytes for `TEICHION-RCPT-V1` |
| 16 | 1 | `format_version` | `0x01` |
| 17 | 1 | `record_kind` | `0x01` |
| 18 | 1 | `algorithm_id` | `0x01` |
| 19 | 1 | `flags` | `0x00` |
| 20 | 8 | `epoch` | same value authenticated in record |
| 28 | 8 | `sequence` | same value authenticated in record |
| 36 | 4 | `payload_length` | same value authenticated in record |
| 40 | 32 | `previous_seal` | same value authenticated in record |
| 72 | 32 | `seal` | resulting 256-bit seal |

Receipt domain:

```text
ASCII: TEICHION-RCPT-V1
HEX:   54 45 49 43 48 49 4f 4e 2d 52 43 50 54 2d 56 31
```

A receipt does not contain the payload.

An independent verifier therefore requires the corresponding payload plus the verification authority required by the selected cryptographic design.

For HMAC, possession of a receipt alone does not provide public verification.

---

## 23. Genesis example

The following example is a **serialization vector only**.

It is not an HMAC test vector.

Inputs:

```text
domain          = TEICHION-SEAL-V1
format_version  = 0x01
record_kind     = 0x01
algorithm_id    = 0x01
flags           = 0x00
epoch           = 0
sequence        = 0
payload_length  = 0
previous_seal   = 32 bytes of 0x00
payload         = empty
```

Canonical record length:

```text
72 bytes
```

Hex dump:

```text
0000: 54 45 49 43 48 49 4f 4e 2d 53 45 41 4c 2d 56 31
0010: 01 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0040: 00 00 00 00 00 00 00 00
```

The independent reference encoder and machine-readable vector corpus reproduce these bytes exactly under the canonical protocol verification gate.

---

## 24. Mutation expectations

Reference-vector testing must demonstrate that each of the following changes the canonical authentication input:

- payload bit mutation;
- payload-length mutation;
- sequence mutation;
- epoch mutation;
- previous-seal mutation;
- domain mutation;
- format-version mutation;
- record-kind mutation;
- algorithm-id mutation;
- flags mutation.

Unsupported or reserved-value mutations must be rejected rather than normalized into an accepted equivalent.

---

## 25. Canonicality rule

V1 canonicality is defined by construction:

```text
CanonicalSealRecordV1 =
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

No alternative field order or representation is valid.

---

## 26. Security distinctions

The V1 contract preserves the following distinctions.

```text
event occurred
    !=
host observed event

host observed event
    !=
record presented to TEICHION

record presented
    !=
record accepted

record accepted
    !=
persistent anti-rollback

deterministic serialization
    !=
cryptographic authenticity

correct HMAC computation
    !=
protected key lifecycle

receipt exists
    !=
publicly verifiable proof
```

These distinctions are normative parts of the TEICHION security model.

---

## 27. Verification status and remaining obligations

The current repository already provides:

- an independent reference encoder and strict decoder;
- machine-readable positive serialization vectors;
- machine-readable negative and malformed-input vectors;
- mutation coverage for payload, sequence, previous-seal, domain, version, algorithm, flags, truncation, trailing bytes, and profile bounds;
- a canonical protocol CI gate that reproduces the vector corpus.

These artifacts verify deterministic serialization and rejection behavior. They do not establish cryptographic authenticity.

Before TEICHION can support a VERIFIED cryptographic claim, later work must still provide:

- SHA-256 known-answer tests;
- HMAC-SHA-256 known-answer tests;
- RTL-to-reference differential testing;
- key-lifecycle definition;
- reset / epoch implementation;
- verifier implementation;
- negative tests demonstrating that protected cryptographic mutations fail verification.

Physical implementation claims require additional evidence beyond simulation.

---

## 28. Non-goals of V1 specification

This document does not define:

- USB framing;
- PCIe framing;
- host API;
- key provisioning;
- key zeroization;
- secure boot;
- FPGA bitstream authentication;
- persistent epoch storage;
- physical tamper resistance;
- side-channel resistance;
- fault-injection resistance;
- public-key attestations;
- public verifiability.

These require separate issues and proof obligations.

---

## 29. Review questions

A reviewer should be able to answer **yes** to all of the following for this contract:

1. Is every authenticated byte defined?
2. Is there exactly one valid encoding for the same accepted logical record?
3. Can the host override any hardware-owned ordering value?
4. Can rejected input silently consume committed sequence state?
5. Can reserved bits create a second accepted interpretation?
6. Is reset-era continuity represented without pretending persistence already exists?
7. Can an independent encoder reproduce the exact byte sequence?
8. Does the receipt expose enough context for a future verifier?
9. Are cryptographic and key-management claims still clearly TARGET?
10. Would an incompatible future format be forced into a distinct version/domain?

---

## 30. Current claim

The strongest claim established by this document alone is:

> **TEICHION has a deterministic V1 byte contract, an independent reference encoder, and machine-readable serialization and rejection vectors. These artifacts verify canonical protocol behavior, not cryptographic authenticity. Cryptographic authenticity remains unimplemented until the datapath, key model, cryptographic vectors, and verifier exist.**
