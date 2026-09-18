## Linked issue / proof obligation

Closes #

## Objective

What engineering problem does this pull request solve?

## What changed

Describe the smallest meaningful set of changes introduced by this PR.

## What did not change

State important non-goals so reviewers can detect accidental scope expansion.

## Security boundary impact

Does this change affect any of the following?

- [ ] trust boundary
- [ ] sequence / epoch state
- [ ] previous-seal state
- [ ] reset / rollback semantics
- [ ] acceptance semantics
- [ ] canonical serialization
- [ ] cryptographic primitive
- [ ] key handling
- [ ] transport framing
- [ ] persistent state
- [ ] independent verification
- [ ] FPGA configuration / boot trust
- [ ] none of the above

Explain every checked item:

## Claim-state changes

For each affected capability, classify the resulting state:

- **TARGET** — intended, not implemented
- **IMPLEMENTED** — present in source
- **VERIFIED** — present and exercised by reproducible verification

Do not promote a claim without evidence.

## Proof obligations

List the properties this PR must demonstrate before merge.

- [ ]
- [ ]

## Verification evidence

Provide exact reproducible commands and results.

```text
<commands and relevant PASS output>
```

### Required checks

- [ ] `git diff --check` passes
- [ ] local lint passes
- [ ] local build passes
- [ ] local simulation / tests pass
- [ ] GitHub CI passes
- [ ] no unexplained warnings remain

## Adversarial / edge conditions considered

Describe relevant cases such as:

- reset;
- backpressure;
- malformed input;
- replay;
- reordering;
- overflow;
- power loss;
- rollback;
- untrusted host-controlled values;
- partial transaction state.

## Performance impact

State measured impact, no impact, or unknown.

Do not make performance claims without measurements.

## Portability impact

State which platforms or toolchains were actually exercised.

Do not convert intended portability into verified portability.

## Documentation impact

Which public claims, architecture diagrams, threat-model statements, or developer instructions changed?

## Known limitations

List limitations that remain after this PR.

## Review focus

Tell the reviewer where the highest-risk reasoning is located.

## Merge checklist

- [ ] Diff is limited to the issue scope
- [ ] No generated artifacts or accidental files are included
- [ ] No secrets, credentials, keys, or sensitive evidence are present
- [ ] Security claims match implementation reality
- [ ] Reset and persistence assumptions are explicit
- [ ] Tests fail when the protected invariant is intentionally broken
- [ ] Documentation and code agree
- [ ] All MUST review findings are resolved
