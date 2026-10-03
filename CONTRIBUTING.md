# Contributing to TEICHION

TEICHION favors small changes that are easy to audit and easy to reproduce.

## Start clean

For non-trivial work:

1. identify the engineering problem;
2. confirm the affected trust boundary;
3. branch from the current `main`;
4. keep the patch focused.

Documentation corrections that do not change technical meaning do not require a dedicated issue.

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

Before editing, confirm that the working tree is clean:

```bash
git status
git branch --show-current
git diff --check
```

## Verification

Run the checks that cover the boundary you changed.

### Generation-0 RTL

```bash
verilator \
  --lint-only \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb

verilator \
  --binary \
  --timing \
  -Wall \
  rtl/core/teichion_seal_chain.sv \
  tb/core/teichion_seal_chain_tb.sv \
  --top-module teichion_seal_chain_tb

./obj_dir/Vteichion_seal_chain_tb
```

Expected simulation result:

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

A relevant local gate should pass before push. GitHub Actions should pass before merge.

## Patch discipline

Every contribution should:

- pass `git diff --check`;
- keep generated artifacts out of Git unless they are explicitly versioned;
- avoid unrelated formatting and refactors;
- keep tests tied to the behavior they protect;
- preserve explicit reset and handshake semantics;
- update the relevant normative document when a trust boundary changes;
- avoid claims that exceed implementation or test evidence.

Before committing:

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

Commit messages should describe technical intent.

## Evidence states

TEICHION uses three terms in security-relevant documentation:

- **TARGET**: intended architecture that is not implemented;
- **IMPLEMENTED**: mechanism exists in source;
- **VERIFIED**: a stated property is exercised by reproducible verification.

The rules for these terms live in `docs/engineering/ASSURANCE_MODEL.md`.

Do not describe reset-local ordering as persistent anti-rollback, infer event non-occurrence from missing telemetry, or treat the current external `tag_i` as a cryptographically trusted result.

## Pull requests

A useful pull request makes these points easy to find:

- problem being solved;
- exact scope and non-goals;
- security-boundary impact;
- verification commands and results;
- known limitations;
- areas where review should concentrate.

The pull request template is a review aid, not a substitute for technical reasoning.

## Merge standard

A change is ready when the diff matches its stated purpose, relevant local checks pass, CI is green, documentation matches behavior, and known review findings are resolved.

A green build is necessary. It is not evidence for properties the test suite does not exercise.
