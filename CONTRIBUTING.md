# Contributing to TEICHION

TEICHION accepts small, reviewable changes that keep security claims, state ownership, and verification evidence explicit.

## Before implementing

For non-trivial work:

1. identify the engineering problem or proof obligation;
2. confirm the current trust boundary and non-goals;
3. branch from the current `main`;
4. keep the change narrow enough to audit.

Documentation-only corrections that do not change technical meaning may proceed without a dedicated issue.

## Branch discipline

Start from a clean, current `main`:

```bash
git fetch origin --prune
git switch main
git pull --ff-only origin main
git status
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

One branch should represent one engineering purpose.

## Local preflight

Before editing:

```bash
git status
git branch --show-current
git diff --check
```

Resolve unexpected local changes or branch divergence before starting new work.

## Verification gates

### Generation-0 RTL

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

### Canonical protocol

```bash
python3 -m compileall -q tools/reference tests/reference

python3 tools/reference/canonical_record_v1.py \
  --vectors test_vectors/canonical_seal_record_v1.json

python3 -m unittest discover \
  -s tests/reference \
  -p 'test_*.py' \
  -v
```

A relevant change must pass its local gate before push and its GitHub Actions gate before merge.

## Change hygiene

Every contribution must:

- pass `git diff --check`;
- exclude generated artifacts unless repository policy explicitly versions them;
- avoid unrelated formatting and refactors;
- keep tests traceable to the behavior they protect;
- preserve explicit reset and handshake semantics;
- update the relevant normative document when a trust boundary changes;
- avoid claims unsupported by implementation and evidence.

Prefer the smallest patch that solves the stated problem.

## Commit discipline

Before a commit:

```bash
git diff --check
git status --short
git diff
```

Stage only the intended change:

```bash
git add <path>
git diff --cached --check
git diff --cached
```

Commit messages should describe technical intent, not activity.

Cryptographically signed commits are encouraged for security-sensitive work.

## Claim discipline

TEICHION uses three claim states:

- **TARGET**: intended, not implemented;
- **IMPLEMENTED**: present in source;
- **VERIFIED**: present and exercised by reproducible verification.

The normative promotion rules live in `docs/engineering/ASSURANCE_MODEL.md`.

A contribution must not:

- describe target behavior as implemented;
- describe implemented behavior as verified without evidence;
- convert reset-local ordering into persistent anti-rollback;
- infer event non-occurrence from missing telemetry;
- describe externally supplied Generation-0 `tag_i` as cryptographically trusted.

## Security-sensitive changes

Explicit security analysis is required when a change affects:

- trust ownership;
- sequence or epoch state;
- previous-chain state;
- reset or rollback semantics;
- acceptance semantics;
- canonical serialization;
- cryptographic primitives;
- key handling;
- persistent state;
- host transport;
- independent verification;
- FPGA configuration or boot trust.

Potential vulnerabilities must follow `SECURITY.md`.

## Pull requests

A pull request should make the following clear:

- problem or proof obligation;
- exact scope;
- deliberate non-goals;
- security-boundary impact;
- claim-state changes;
- reproducible verification;
- known limitations;
- highest-risk reasoning.

The repository template exists to make those questions explicit, not to create checkbox theater.

## Review standard

Review should challenge:

- functional correctness;
- state-machine correctness;
- trust ownership;
- reset and rollback behavior;
- malformed-input handling;
- backpressure and error behavior;
- overflow and boundary conditions;
- test strength;
- documentation accuracy;
- unnecessary complexity;
- unsupported portability or performance claims.

Review language:

- **MUST**: required before merge;
- **SHOULD**: expected unless a documented reason justifies deviation;
- **COULD**: optional improvement.

## Merge gate

A change is ready only when:

- the diff matches its stated scope;
- required local checks pass;
- GitHub CI passes;
- no known warning or failing verification remains;
- security-impact statements are complete;
- normative documentation matches implementation;
- unresolved review findings are closed.

A green build is necessary, not sufficient.
