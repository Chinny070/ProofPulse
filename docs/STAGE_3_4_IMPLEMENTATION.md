# ProofPulse Stages 3 and 4: Provenance, Time, and Sampled Compliance

**Status:** Implemented in the local source; Direct Mode verified, genuine GenLayer runtime not verified.  
**Product scope:** The existing standalone Intelligent Contract remains unchanged in purpose and its existing public method signatures are preserved. No frontend, dashboard, token, or cross-contract dependency was added.

## Rationale and constraints

Stage 2 already stored approved URL references, response-body SHA-256 values, assessments, and transaction observation time. It did not bind a result to the exact immutable policy, provide a canonical evidence-manifest commitment, assign observations to periods, prevent multiple accepted samples in one period, or compute a history summary. This change adds those functions while keeping the evidence outcome model conservative.

The timestamp is the deterministic GenLayer transaction-context timestamp from `datetime.now(timezone.utc)`. It records when the verification transaction was observed by contract execution; it does not prove when a real-world event happened or when a publisher released a page. A source-supplied date remains untrusted. The reviewed transaction context does not supply a block hash/number in the fields used by this contract.

SHA-256 commitments provide byte/field integrity for later comparison. They do not attest to publisher identity, source truth, publication time, validator independence, or durable availability. The JSON encoding below is explicitly defined for reproducibility; it is not a digital signature.

## Record schema version 1

Each accepted verification record now includes:

- `schema_version: 1` and `policy_version: 1`.
- `policy_sha256`: SHA-256 of compact, sorted-key UTF-8 JSON containing policy version, normalized requirements, and exact approved-source URLs.
- `observation_window`: zero-based time bucket, computed as `floor((observed_at - registered_at) / observation_period_seconds)`. It is `-1` when no period is configured or the observation is after the deadline.
- `deadline_evaluation`: `NO_DEADLINE`, `ON_OR_BEFORE_DEADLINE`, or `AFTER_DEADLINE`. It evaluates the transaction timestamp only, not performance time.
- The existing outcome, verification ID, sequence, requirement-level assessments, concise explanation, and transaction timestamp.
- Each evidence reference includes its source index and exact policy URL, retrieval status, HTTP status, SHA-256 of successful response bytes, and `body_bytes` count returned by the web operation. For `OVERSIZED`, this count is informative only; the check happened after retrieval and does not cap download size.
- `evidence_manifest_sha256`: SHA-256 of compact, sorted-key UTF-8 JSON containing schema version, obligation/verification IDs, sequence, policy hash, observation window, outcome, evidence references, requirement assessments, timestamp, and deadline relation. Explanation prose is omitted from the decision commitment.

Records are append-only in contract state. The additional sequence-to-verification-ID index lets the aggregate view enumerate the bounded history. The contract-wide cap remains 64 accepted records; the per-obligation cap remains 8. No existing deployed contract requires migration because no ProofPulse deployment has been made. Any future migration plan must account for records created before this schema and index exist.

## Observation-window and replay rules

An observation period defines cadence. Window 0 begins at obligation registration; each period boundary advances the index. At most one accepted verification transaction can occupy a window. An attempt to repeat a window is rejected, even if it uses a new verification ID. A later window cannot be followed by a new sample in an earlier window. Failed retrieval that reaches and commits an `INCONCLUSIVE` result occupies that window; retrying inside the same period is not allowed. This avoids inflating coverage by resubmitting the same period, at the cost of waiting for the next period after an inconclusive observation.

The unique verification-ID check and window check happen before external retrieval and AI calls. Both the verification history and its sequence index are written only after the nondeterministic call returns, candidate/schema/record bounds pass, and the record is fully constructed. Direct Mode tests verify this source ordering and that an injected record-size failure leaves those fields unchanged; this is not proof of network rollback on consensus failure.

## PoCC read view

`get_pocc_summary(obligation_id)` is a public read-only method. It requires an observation period and scans at most the obligation's eight indexed records. The first window is expected immediately at registration; further windows become due at each period. The due horizon stops at the earlier of the current transaction timestamp and the policy deadline, when configured.

The returned JSON includes policy version, period, as-of/through timestamps, due/observed/missing window counts, the first missing index, each observed window's verification ID/sequence/outcome/time/manifest commitment, and an explicit statement that the scope is sampled windows only.

Aggregation order:

1. Any observed `VIOLATED` window produces aggregate `VIOLATED`, while missing-window counts remain visible.
2. With no due window, aggregate `PENDING`.
3. Any missing window or `INCONCLUSIVE` sample produces `INCONCLUSIVE` (unless a violation was observed).
4. Complete coverage containing `PENDING` produces `PENDING`.
5. Only complete coverage where every due window is `FULFILLED` produces `FULFILLED`.

This summary never establishes uninterrupted real-world compliance between observations. A `FULFILLED` result means only that all windows due at its `as_of_timestamp` were sampled and fulfilled under the registered policy. If a deadline has passed, windows after that deadline are not added to the expected compliance horizon, and a verification executed after the deadline is tagged `observation_window: -1`; it cannot backfill a due period.

## Security and limitations

- Authorization remains owner-only and lifecycle/policy behavior is unchanged.
- A unique ID prevents same-key replay; one-window uniqueness prevents duplicate samples within the configured cadence.
- History and view work are bounded by existing contract caps. Runtime storage/compute costs have not been measured.
- External source freshness is not authenticated. Transaction time and window indexes express observation cadence, not the age or publication time of source content.
- URL validation cannot observe or constrain a redirected final URL with the installed response surface. Body size limits apply after `web.get` returns and cannot prevent excessive transfer/allocation.
- Validator exact-quote equivalence can reject semantically similar independent runs. It was retained to preserve evidence-source attribution; there is no genuine validator data to justify weakening it.
- Direct Mode tests use mocked web/LLM responses. Neither validator consensus nor state rollback was observed.

## Checks

The Stage 3/4 code and adversarial additions to the existing tests are exercised in the current full command `gltest tests/ -q`. See [Final Readiness Report](FINAL_READINESS_REPORT.md) for exact current run, linter/schema results, package versions, network profile, and remaining gates.
