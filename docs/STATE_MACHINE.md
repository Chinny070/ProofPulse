# ProofPulse State Machine (Stage 1 implementation plus future evaluation design)

Obligation transitions below are implemented in Stage 1. The synchronous evaluation transaction and append-only result record are implemented in Stage 2. State names describe domain state; they are not GenLayer transaction lifecycle statuses.

## Obligation lifecycle

```text
UNREGISTERED --register--> ACTIVE (immutable policy version 1)
ACTIVE --close by owner--> CLOSED
```

Stage 1 implements only these transitions. Policy revision and reopening are deferred: they require explicit version migration, authorization, and audit semantics before implementation. No policy or obligation deletion is allowed. Closed obligations reject lifecycle writes. Stage 2 verification outcomes are stored separately from this obligation lifecycle.

## Evaluation lifecycle

```text
ACTIVE --owner requests verification--> consensus-gated evaluation
consensus accepted + deterministic checks pass --> append FULFILLED | VIOLATED | INCONCLUSIVE | PENDING record
consensus rejected / execution fails --> no committed record on the actual network
CLOSED --verification request--> reject
```

Stage 2's `PENDING` outcome means approved evidence explicitly shows an unfinished process, while the GenLayer transaction itself has completed. Direct Mode tests exercise the validator callback but do not prove network rollback or consensus behavior. External retrieval/model failures become `INCONCLUSIVE` if the call can complete; uncaught transaction/consensus failure appends no record.

## Observation transitions

Stage 2 uses a unique `(obligation_id, verification_id)` key and monotonically increments a bounded per-obligation sequence:

- a repeated verification ID → reject before external calls and do not append;
- a new verification ID → append only after the nondeterministic validator callback accepts and deterministic record bounds pass;
- conflicting sources or insufficient evidence → `INCONCLUSIVE`, not `VIOLATED`;
- affirmative evidence of a missed requirement with no unknown, pending, or contradiction → `VIOLATED`;
- periodic-window ordering and continuity aggregation remain future Stage 4 behavior.

## Deadlines and timestamps

Use transaction-pinned time for contract submission/observation time and arithmetic. A submitted claim of source publication time is metadata from the source, not trusted chain time. A deadline result should distinguish “observation submitted after deadline” (deterministic comparison) from “evidence proves timely real-world performance” (requires authenticated evidence). The contract cannot infer current wall-clock at validator replay, and documentation reports no block number/hash in transaction context.

## Authorization gates

Every state-changing method must check the relevant stored role against `gl.message.sender_address` (or carefully justified `origin_address`). Public views may be unrestricted. Registration creator becomes initial administrator unless a different explicit role model is chosen. Policy changes, source changes, close/reopen, and evaluation submission must have explicit authorization rules. The validator cannot repair missing access control after a transaction is invoked.

## Invariants

1. Policy versions and terminal observation records are append-only.
2. A terminal observation references exactly one obligation, lifecycle epoch, policy version, window, evidence manifest, and accepted transaction time.
3. No observation is committed before the equivalence/consensus result is accepted.
4. Missing or inaccessible evidence never implies `VIOLATED` or `FULFILLED`.
5. An idempotency key maps to no more than one committed observation.
6. Each call has hard caps on input bytes, source count, response bytes processed, and records appended.
7. “Continuing compliance” summarizes only sampled windows and reports gaps; it never implies uninterrupted compliance from sparse observations.

## PoCC aggregate transitions

The aggregate is a deterministic view of recorded observations under one specified policy version/range, not an independently trusted AI label:

- all required windows present and `FULFILLED` → “all required recorded windows fulfilled”;
- any `VIOLATED` window → violation present in the covered sample;
- any `INCONCLUSIVE`/missing/`PENDING` window → coverage incomplete;
- policy version change or lifecycle epoch change → split coverage; do not combine without explicit migration semantics.

This deliberately avoids the stronger and unsupported claim that periodic checks prove continuous real-world state between observation times.
