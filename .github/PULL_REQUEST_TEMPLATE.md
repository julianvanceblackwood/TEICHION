## Linked issue / proof obligation

Closes #

## Objective

What problem or proof obligation does this PR address?

## Scope

### Changed

Describe the smallest meaningful change.

### Not changed

List important non-goals.

## Security boundary impact

Check every affected area:

- [ ] trust ownership
- [ ] sequence / epoch state
- [ ] previous-chain state
- [ ] reset / rollback semantics
- [ ] acceptance semantics
- [ ] canonical serialization
- [ ] cryptographic primitive
- [ ] key handling
- [ ] transport framing
- [ ] persistent state
- [ ] independent verification
- [ ] FPGA configuration / boot trust
- [ ] none

Explain checked items:

## Claim-state changes

- **TARGET**:
- **IMPLEMENTED**:
- **VERIFIED**:

Do not promote a claim without evidence.

## Proof obligations

- [ ]
- [ ]

## Verification

Provide exact commands and relevant results:

```text
<commands and PASS output>
```

Required checks:

- [ ] `git diff --check`
- [ ] relevant local lint
- [ ] relevant local build
- [ ] relevant simulation / tests
- [ ] GitHub CI
- [ ] no unexplained warning remains

## Edge conditions

Describe relevant cases such as reset, backpressure, malformed input, replay, reordering, overflow, rollback, untrusted host input, or partial transaction state.

## Performance and portability

State measured impact, no impact, or unknown.

List only platforms and toolchains actually exercised.

## Documentation

Which public claim, protocol rule, threat-model statement, or developer instruction changed?

## Known limitations

What remains unresolved after this PR?

## Review focus

Where is the highest-risk reasoning?

## Merge checklist

- [ ] diff matches the stated scope
- [ ] no accidental or generated files
- [ ] no secrets, credentials, keys, or sensitive evidence
- [ ] claims match implementation and evidence
- [ ] reset and persistence assumptions are explicit where relevant
- [ ] protected invariants have meaningful failure coverage
- [ ] documentation and implementation agree
- [ ] all MUST findings are resolved
