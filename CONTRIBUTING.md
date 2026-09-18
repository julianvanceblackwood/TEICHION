# Contributing to TEICHION

TEICHION is a hardware-security research project. Contributions are evaluated not only for whether they compile, but for whether their claims, trust assumptions, state transitions, and verification evidence remain reviewable.

The project prefers small, issue-backed, security-auditable changes over broad refactors.

## Before implementing

For non-trivial work:

1. Search existing issues.
2. Open or select an issue that defines the engineering problem.
3. State the required proof obligations, non-goals, and security-boundary impact.
4. Create a focused branch from the current `main`.

Do not invest significant implementation effort in a cross-cutting change before its scope is written down.

Documentation-only typo fixes may proceed without a dedicated issue when they do not alter technical meaning.

## Branch discipline

Start from a clean and current `main`:

```bash
git switch main
git pull --ff-only origin main
git switch -c <type>/<meaningful-name>
```

Recommended prefixes:

```text
feat/
fix/
docs/
test/
ci/
refactor/
```

A branch should represent one reviewable engineering purpose.

## Local preflight

Before modifying the repository:

```bash
git fetch origin --prune
git status
git branch --show-current
git diff --check
```

Unexpected local modifications, generated files, or branch divergence should be resolved before new work begins.

## Generation-0 verification gate

Changes touching current SystemVerilog RTL, its testbench, or the verification workflow must pass the local gate before push.

Lint:

```bash
verilator \
  --lint-only \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb
```

Build:

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

Expected result:

```text
PASS: deterministic sequencing, chain carry, and receipt backpressure verified
```

A warning-clean result is required. Do not silence a new warning merely to recover a green build unless the warning is proven irrelevant and the suppression is itself reviewed.

## Change hygiene

Contributions MUST:

- keep generated artifacts out of Git;
- pass `git diff --check`;
- avoid unrelated formatting or refactoring;
- keep test changes traceable to the behavior being tested;
- preserve explicit reset and handshake semantics;
- update documentation when a security boundary changes;
- avoid capability claims unsupported by implementation and verification.

Contributions SHOULD:

- be the smallest reasonable patch that solves the stated problem;
- separate independent changes into separate commits or pull requests;
- use imperative, descriptive commit messages;
- explain why a state transition or interface exists, not only what code changed.

## Commit discipline

Before each commit:

```bash
git diff --check
git status --short
git diff
```

Stage only the intended file or coherent change:

```bash
git add <path>
git diff --cached --check
git diff --cached
```

Then commit.

TEICHION prefers semantically coherent commits over large catch-all commits.

Cryptographically signed commits are encouraged now and are expected to become mandatory before the first tagged security-sensitive release.

## Claim discipline

TEICHION uses three documentation states:

### TARGET

Part of the intended architecture, but not implemented.

### IMPLEMENTED

The mechanism exists in the repository.

### VERIFIED

The mechanism exists and the stated property is exercised by reproducible verification.

A contribution MUST NOT:

- describe TARGET behavior as implemented;
- describe IMPLEMENTED behavior as verified without evidence;
- infer event non-occurrence from missing telemetry;
- convert a reset-local guarantee into a persistent guarantee;
- describe externally supplied Generation-0 `tag_i` as cryptographically trusted.

## Security-sensitive changes

Changes affecting any of the following require explicit security analysis in the pull request:

- trust boundaries;
- sequence or epoch state;
- previous-seal state;
- reset behavior;
- acceptance semantics;
- canonical serialization;
- cryptographic primitives;
- key handling;
- transport framing;
- persistent state;
- independent verification;
- FPGA configuration or boot trust.

Potential vulnerabilities must follow `SECURITY.md`. Do not place sensitive exploit details in a public issue.

## Pull requests

A pull request should answer:

- What problem is being solved?
- Which issue or proof obligation authorizes the change?
- What changed?
- What deliberately did not change?
- Which security assumptions changed?
- Which properties are now TARGET, IMPLEMENTED, or VERIFIED?
- What exact commands reproduce verification?
- What known limitations remain?

Large pull requests that combine unrelated work are difficult to audit and may be split before review.

## Review standard

Review is technical cross-examination, not ceremonial approval.

Review should consider:

- functional correctness;
- state-machine correctness;
- security-boundary correctness;
- reset and rollback semantics;
- evidence integrity;
- malformed-input behavior;
- error and backpressure behavior;
- portability claims;
- performance claims;
- test coverage;
- documentation accuracy;
- unnecessary complexity or scope creep.

The following language may be used during review:

- **MUST** — required before merge;
- **SHOULD** — strongly recommended unless a documented reason justifies otherwise;
- **COULD** — optional improvement.

## Merge gate

A change is ready to merge only when:

- the diff matches the issue scope;
- local required checks pass;
- GitHub CI passes;
- no known warning or failing verification remains;
- security-impact statements are complete;
- documentation matches actual behavior;
- unresolved review findings are closed.

A green CI result is necessary, but not sufficient, for merge.
