# TEICHION

## Hardware-Sealed Security Evidence Boundary

**TEICHION is an FPGA-backed security architecture for establishing independently verifiable evidence-chain state outside the ordinary trust domain of a potentially compromised host.**

The project investigates one narrow systems-security question:

> **After security evidence crosses a hardware trust boundary, can its ordering and chain state remain independently defensible even if the host that produced it later becomes untrustworthy?**

TEICHION is not designed around the assumption that host telemetry is complete.

It is designed around a stricter claim:

> **A record that has crossed the TEICHION hardware boundary may receive guarantees about its accepted order and chain relationship. A record that never crossed that boundary cannot be inferred not to have existed.**

That distinction defines the project.


---

## Current State

| Property                       | Status                                    |
| ------------------------------ | ----------------------------------------- |
| Project stage                  | Generation 0                              |
| Primary domain                 | FPGA-backed security evidence integrity   |
| RTL language                   | SystemVerilog                             |
| Verification                   | Verilator lint + executable simulation    |
| Implemented hardware primitive | Deterministic seal-chain state controller |
| Sequence ownership             | Hardware controller                       |
| Previous-tag ownership         | Hardware controller                       |
| Transactions in flight         | One                                       |
| Cryptographic engine           | Not implemented                           |
| Canonical evidence framing     | Not implemented                           |
| Device-key protection          | Not implemented                           |
| Host transport                 | Not implemented                           |
| Physical FPGA deployment       | Not yet claimed                           |
| Production root of trust       | Not yet claimed                           |

Generation 0 establishes deterministic chain-state semantics before cryptographic sealing, transport, key management, or physical deployment are introduced.

---

# The Security Problem

Security evidence is often collected by software operating inside the same trust domain as the system being monitored.

A simplified path is:

```text
Security Event
      ↓
Kernel / Runtime
      ↓
Collector
      ↓
Host Memory
      ↓
Host Storage
      ↓
Remote Analysis
```

If privileged host software becomes compromised, the attacker may gain influence over the same mechanisms responsible for preserving evidence of the compromise.

Possible failure modes include:

```text
deletion
modification
reordering
replay
substitution
selective suppression
timestamp manipulation
collector manipulation
chain-state rollback
```

Moving a log from one host process to another does not necessarily move it into a different trust domain.

TEICHION explores a different boundary.

---

# Trust Boundary

The intended architecture is:

```text
Potentially Compromised Host
             │
             │ canonical evidence frame
             ▼
┌───────────────────────────────────────────────────────────┐
│                 FPGA TRUST BOUNDARY                       │
│                                                           │
│  Frame Acceptance                                         │
│        ↓                                                  │
│  Hardware-Owned Sequence State                            │
│        ↓                                                  │
│  Previous Seal State                                      │
│        ↓                                                  │
│  Cryptographic Sealing                                    │
│        ↓                                                  │
│  Hardware-Sealed Receipt                                  │
│                                                           │
└───────────────────────────────────────────────────────────┘
             │
             ▼
      Independent Verification
```

The host may eventually construct and transmit evidence records.

The hardware boundary is intended to own the state that determines how accepted records are ordered and chained.

This produces an important semantic separation:

```text
Event occurred
        ≠
Event was observed by host software
        ≠
Event was transmitted
        ≠
Event crossed the FPGA boundary
        ≠
Event received a hardware-sealed receipt
```

These statements must never be treated as interchangeable.

---

# Evidence Completeness

TEICHION does **not** attempt to prove that host observation is complete.

If an event never reaches the FPGA boundary, TEICHION cannot determine whether:

```text
the event never occurred

the host failed to observe it

the collector failed

the host intentionally suppressed it

transport failed

the event was dropped before hardware acceptance
```

Therefore:

```text
absence of a TEICHION record
            ≠
proof of event non-occurrence
```

This is a security-model constraint, not an implementation inconvenience.

---

# Generation 0

Generation 0 implements the first TEICHION hardware primitive:

```text
teichion_seal_chain
```

Its responsibility is intentionally narrow.

It owns:

```text
current sequence state

previous accepted tag state

pending transaction context

receipt state

request/context/receipt handshakes
```

It does **not** compute SHA-256 or HMAC.

The current `tag_i` input represents a seal result supplied to the controller.

Generation 0 proves the state semantics surrounding that result before a hardware cryptographic engine is introduced.

---

# Generation-0 Transaction

A Generation-0 transaction follows:

```text
Request
   │
   ▼
Allocate current sequence
   │
   ▼
Capture previous tag
   │
   ▼
Expose sealing context
   │
   ▼
Wait for tag result
   │
   ▼
Commit new chain state
   │
   ▼
Expose receipt
   │
   ▼
Wait for receipt acceptance
   │
   ▼
Return to IDLE
```

Only one transaction may be active at a time.

This is deliberate.

The current priority is semantic correctness, not throughput.

---

# State Machine

```text
                          request accepted
                                 │
                                 ▼
                           ┌──────────┐
                           │   IDLE   │
                           └────┬─────┘
                                │
                                ▼
                       ┌────────────────┐
                       │ SEND_CONTEXT   │
                       └───────┬────────┘
                               │
                    context handshake
                               │
                               ▼
                       ┌────────────────┐
                       │    WAIT_TAG    │
                       └───────┬────────┘
                               │
                         tag_valid_i
                               │
                               ▼
                       ┌────────────────┐
                       │ HOLD_RECEIPT   │
                       └───────┬────────┘
                               │
                    receipt handshake
                               │
                               └──────────────► IDLE
```

The controller must preserve externally visible context and receipt state while downstream components apply backpressure.

---

# Generation-0 Invariants

The current implementation is intended to maintain the following invariants.

### Request ownership

An accepted request receives exactly one pending sequence context.

```text
request_valid_i && request_ready_o
```

defines request acceptance.

### Previous-tag capture

Each accepted request observes the previous accepted chain tag as it existed when the request entered the controller.

### Controlled chain advancement

The chain state does not advance merely because a request exists.

Generation 0 advances sequence and previous-tag state only when a tag result is observed in `WAIT_TAG`.

### Receipt stability

Once generated, receipt sequence and tag values remain stable until the downstream receipt handshake completes.

### Single transaction

No second Generation-0 request may begin while the current transaction is still moving through context, tag, or receipt state.

---

# Sequence Semantics

Generation 0 contains a 64-bit sequence counter.

Within one uninterrupted reset epoch:

```text
0
1
2
3
...
```

accepted transactions receive monotonically increasing values.

However, this distinction is critical:

> **Generation-0 monotonicity is currently intra-epoch, not persistent across hardware reset.**

Reset currently returns sequence state to zero.

Therefore the current implementation does **not** yet provide production anti-rollback guarantees across:

```text
power loss
hardware reset
device restart
state restoration
malicious reset
```

A future design must introduce an explicit continuity mechanism such as an authenticated epoch, protected monotonic state, or another hardware-backed persistence model.

---

# Sequence Exhaustion

The current sequence register is 64 bits.

Generation 0 does not yet define a hardened production policy for sequence exhaustion.

A production design must explicitly choose behavior such as:

```text
fail-stop

authenticated epoch transition

persistent rollover protocol
```

Silent security-semantic wraparound must not become an accidental production behavior.

---

# Reset Semantics

The Generation-0 controller uses an explicit reset state:

```text
sequence       = 0
previous tag   = 0
pending state  = 0
receipt state  = 0
controller     = IDLE
```

This gives deterministic simulation and an explicit genesis condition.

It does not yet establish authenticated chain continuity across resets.

---

# Verification

Generation 0 is continuously checked with Verilator.

The verification pipeline performs:

```text
SystemVerilog lint
        ↓
Executable simulation build
        ↓
Deterministic testbench execution
        ↓
PASS / FAIL
```

The repository currently treats RTL warnings as engineering failures rather than silently accepting them.

The testbench verifies:

```text
reset initialization

controller readiness after reset

genesis sequence allocation

zero previous-tag genesis state

context handshake

tag acceptance

receipt generation

receipt stability under backpressure

receipt handshake

previous-tag propagation

second sequence allocation

return to IDLE
```

Current successful simulation terminates with:

```text
PASS: deterministic sequencing, chain carry, and receipt backpressure verified
```

---

# Reproduce Generation-0 Verification

TEICHION currently uses Verilator.

From the repository root:

```bash
verilator \
  --lint-only \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb
```

Build the executable simulation:

```bash
verilator \
  --binary \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb
```

Run:

```bash
./obj_dir/Vteichion_seal_chain_tb
```

Expected terminal result:

```text
PASS: deterministic sequencing, chain carry, and receipt backpressure verified
```

Generated Verilator output is not part of the source tree and must not be committed.

---

# Repository Map

```text
TEICHION/
│
├── .github/
│   └── workflows/
│       └── rtl.yml
│
├── rtl/
│   └── core/
│       └── teichion_seal_chain.sv
│
├── tb/
│   └── core/
│       └── teichion_seal_chain_tb.sv
│
├── .gitignore
└── README.md
```

### `rtl/core/teichion_seal_chain.sv`

Generation-0 hardware state controller.

Owns deterministic sequence, previous-tag, transaction-context, and receipt state.

### `tb/core/teichion_seal_chain_tb.sv`

Executable behavioral verification for the Generation-0 controller.

### `.github/workflows/rtl.yml`

Continuous verification gate.

A pull request is not considered technically clean merely because the source compiles.

Lint, build, and simulation must all succeed.

---

# Target Cryptographic Construction

The long-term architecture is expected to evolve toward a construction conceptually similar to:

```text
Seal[n] =
    HMAC-SHA-256(
        K_device,
        Domain ||
        Epoch ||
        Sequence[n] ||
        CanonicalRecord[n] ||
        Seal[n-1]
    )
```

where:

```text
K_device
    device-bound secret material

Domain
    domain-separation identifier

Epoch
    authenticated continuity / reset context

Sequence[n]
    hardware-owned ordering value

CanonicalRecord[n]
    deterministic byte representation of accepted evidence

Seal[n-1]
    previous authenticated chain state
```

This construction is a **target architecture**, not a Generation-0 implementation claim.

No cryptographic tamper-resistance claim should be made until the cryptographic datapath, canonical encoding, key model, reset model, and verifier exist and pass reproducible test vectors.

---

# Threat Model Direction

The future TEICHION architecture is intended to remain meaningful when substantial portions of the host are no longer trusted.

Potentially untrusted components may eventually include:

```text
user-space applications

security agents

privileged host services

host storage

host timestamps

host-generated sequence numbers

local evidence databases

operating-system state
```

TEICHION does not currently claim resistance to every hardware adversary.

The following areas remain outside Generation 0:

```text
physical probing

fault injection

side-channel leakage

bitstream extraction

malicious FPGA configuration

device-key extraction

supply-chain compromise

persistent reset rollback

secure boot

FPGA configuration authenticity
```

These properties must be addressed explicitly before production hardware-root-of-trust claims become defensible.

---

# Cross-Platform Direction

The hardware trust boundary is intended to remain independent of the operating system used by the host.

Future host integration is expected to consider:

```text
Linux
Kali Linux
macOS
Windows
```

No cross-platform collector is currently implemented.

Cross-platform support is therefore a **target**, not a current feature.

---

# Security Claim Classes

TEICHION documentation uses three claim classes.

## IMPLEMENTED

The mechanism exists in the repository.

## VERIFIED

The mechanism exists and its stated property is exercised by reproducible verification.

## TARGET

The mechanism is part of the intended architecture but has not yet been implemented.

A TARGET property must never be presented as IMPLEMENTED.

An IMPLEMENTED property must never be presented as VERIFIED without corresponding evidence.

This distinction is part of the engineering model.

---

# What TEICHION Is Not

TEICHION is not currently:

```text
a SIEM

an endpoint detection product

an FPGA antivirus

a packet inspection appliance

a TPM replacement

a production HSM

a complete forensic acquisition platform

a proof that host telemetry is complete
```

The scope is narrower:

> **Build a defensible hardware boundary for accepted security evidence and prove exactly what that boundary does and does not guarantee.**

---

# Engineering Rules

TEICHION development follows several non-negotiable rules.

```text
No security property exists because documentation claims it.

No hardware component becomes a root of trust by naming alone.

No cryptographic primitive is accepted without reproducible test vectors.

No host-controlled value becomes hardware truth without an explicit trust decision.

No missing observation becomes proof of non-occurrence.

No state transition affecting a security property remains implicit.

No optimization may silently weaken an established invariant.

No future architecture is documented as though it already exists.
```

---

# Development Discipline

Engineering work should follow:

```text
Security or systems problem
        ↓
Meaningful GitHub issue
        ↓
Focused feature branch
        ↓
Semantically coherent commits
        ↓
Local verification
        ↓
Pull request
        ↓
CI verification
        ↓
Review
        ↓
Merge into main
```

GitHub issues represent meaningful engineering problems.

They are not created merely to inflate activity.

Commits should communicate technical intent.

Pull requests should represent reviewable proof boundaries.

---

# Next Proof Boundary

The immediate next engineering problem is **not** hardware acceleration.

It is specification.

Before implementing SHA-256 or HMAC, TEICHION must define an unambiguous canonical sealing contract.

That contract must answer:

```text
Which exact bytes are authenticated?

Which values are hardware-owned?

Which values are host-supplied?

How are integer fields encoded?

What is the byte order?

How is domain separation represented?

How is record length represented?

How is an epoch represented?

How is the previous seal incorporated?

What constitutes malformed input?

What constitutes hardware acceptance?

What exact receipt is returned?
```

Only after these semantics are fixed should the cryptographic datapath become authoritative.

---

# Planned Proof Boundaries

```text
Generation 0
Deterministic chain-state controller
        ↓
Canonical seal-record specification
        ↓
Reference test vectors
        ↓
SHA-256 datapath
        ↓
HMAC-SHA-256 integration
        ↓
Device-key model
        ↓
Reset / epoch / rollback continuity
        ↓
Independent verifier
        ↓
Host transport abstraction
        ↓
Cross-platform host integration
        ↓
Physical FPGA reference platform
        ↓
Adversarial hardware evaluation
```

The order may change as engineering evidence develops.

The security claims must not.

---

# Current Verified Boundary

As of Generation 0, TEICHION verifies a narrow property:

> **Within one reset epoch, a single-transaction FPGA controller deterministically allocates sequence context, carries forward the previous accepted tag, advances chain state after tag acceptance, and preserves receipt state under downstream backpressure.**

It does **not** yet verify:

```text
cryptographic authenticity

persistent anti-rollback

host telemetry completeness

device-key secrecy

physical tamper resistance

production FPGA trust
```

That boundary is intentionally explicit.

---

## Engineering Principle

> **A security system becomes more credible when it can state precisely where its guarantees end.**
