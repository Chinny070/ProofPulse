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

Stage 2 uses a unique `(obligation_id, verification_id)` key and monotonically increments a bounded per-obligation sequence. Stages 3/4 also assign a zero-based window from transaction time and the configured observation period:

- a repeated verification ID → reject before external calls and do not append;
- a repeated occupied observation window → reject before external calls, even with a different ID;
- a later window → append only after the nondeterministic result returns and deterministic schema/record bounds pass;
- an attempt to fill an earlier window after a later one → reject;
- conflicting sources or insufficient evidence → `INCONCLUSIVE`, not `VIOLATED`;
- affirmative evidence of a missed requirement with no unknown, pending, or contradiction → `VIOLATED`;
- a record-size failure before append → no verification record or count change in Direct Mode; actual consensus-rejection rollback remains unverified.

Window 0 begins at registration. Every `observation_period_seconds` after that advances the index. An accepted `INCONCLUSIVE` result occupies its window; retrying requires a later period.

## Deadlines and timestamps

Use transaction-pinned time for registration, observation, window arithmetic, deadline relation, and PoCC as-of time. The stored deadline relation says only whether the verification transaction was on, before, or after the configured deadline; it does not prove when performance occurred. A submitted publication date is not trusted. The reviewed context does not expose a block number/hash in the fields used here.

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

`get_pocc_summary` is a deterministic, bounded read over at most eight accepted records. It counts expected windows from registration through the earlier of the as-of timestamp and configured deadline, and reports due/observed/missing counts, first missing index, each sampled outcome, and the manifest commitment:

- all due windows present and `FULFILLED` → aggregate `FULFILLED`, scoped to those sampled windows;
- any recorded `VIOLATED` window → aggregate `VIOLATED`, with gaps still reported;
- missing windows or an `INCONCLUSIVE` sample → `INCONCLUSIVE`, unless a violation was observed;
- complete windows with a `PENDING` sample → `PENDING`;
- no due windows → `PENDING`.

This deliberately avoids the unsupported claim that periodic checks prove real-world state between observations. No trusted continuous sensor or authenticated source-freshness timestamp is available.
