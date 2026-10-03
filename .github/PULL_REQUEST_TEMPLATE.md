## Linked issue

Closes #

## Problem

What problem does this pull request solve?

## Change

Describe the change in concrete terms.

## Non-goals

What remains unchanged?

## Security boundary impact

Check every area affected by this change:

- [ ] state ownership
- [ ] sequence / epoch state
- [ ] previous-chain state
- [ ] reset / rollback behavior
- [ ] acceptance semantics
- [ ] canonical serialization
- [ ] cryptographic primitive
- [ ] key handling
- [ ] transport framing
- [ ] persistent state
- [ ] independent verification
- [ ] FPGA configuration / boot trust
- [ ] none

Explain the checked items:

## Evidence state

Only fill in rows that changed.

- **TARGET**:
- **IMPLEMENTED**:
- **VERIFIED**:

## Verification

Provide the exact commands used and the relevant result.

```text
<commands and result>
```

- [ ] `git diff --check`
- [ ] relevant lint
- [ ] relevant build
- [ ] relevant simulation or tests
- [ ] GitHub CI
- [ ] no unexplained warning remains

## Failure and edge cases

Describe the cases that matter for this change, such as reset, malformed input, backpressure, replay, reordering, overflow, rollback, untrusted input, or partial transaction state.

## Documentation

List any public behavior, protocol rule, threat-model statement, or developer instruction changed by this PR.

## Known limitations

What remains unresolved after this change?

## Review focus

Point reviewers to the code or reasoning that deserves the most scrutiny.

## Merge checklist

- [ ] diff matches the stated scope
- [ ] no accidental or generated files
- [ ] no secrets, credentials, keys, or sensitive evidence
- [ ] documented behavior matches implementation
- [ ] relevant reset and persistence assumptions are explicit
- [ ] important invariants have meaningful failure coverage
- [ ] review findings are resolved
