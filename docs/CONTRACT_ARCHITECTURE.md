# ProofPulse Contract Architecture (Stage 0)

This document records the target architecture. Stages 1 and 2 implement the bounded deterministic registry/lifecycle and a conditional local evidence-verification path; see [Stage 1 Implementation](STAGE_1_IMPLEMENTATION.md) and [Stage 2 Implementation](STAGE_2_IMPLEMENTATION.md). Live consensus and Studionet integration remain unverified.

## Current Stage 3/4 implementation

The implementation now uses record schema version 1 with a canonical SHA-256 commitment to policy version 1 and a commitment to each verification manifest. Records identify each configured source by index and exact URL, record returned body-byte counts, observation-window index, transaction-pinned observation timestamp, and whether that observation was before/after a configured deadline. No source publication timestamp is trusted. The public `get_pocc_summary(obligation_id)` view computes only a bounded aggregate over at most eight per-obligation records.

The initial observation window begins at registration (window index 0); each later interval increments the index by `observation_period_seconds`. Due windows are counted through the earlier of the view's transaction timestamp and the configured deadline, if any. At most one accepted verification may occupy each window, and later windows cannot be followed by a new verification for an earlier window. A failed retrieval can therefore occupy that period with an accepted `INCONCLUSIVE` record. This prevents repeated submissions from inflating one sample window, but it also means a retry waits until a later period.

PoCC returns `FULFILLED` only when every due sampled window has an accepted `FULFILLED` result; it reports missing windows explicitly. A recorded `VIOLATED` observation remains a violation even if other windows are missing. Uncertainty, conflict, or gaps prevent an overall fulfillment claim. The result explicitly limits its scope to sampled windows and makes no claim about conditions between them. This is not proof of uninterrupted compliance.

The code computes commitments and aggregates deterministically. External retrieval and model interpretation remain nondeterministic and are subject to the existing custom validator. These additions are covered by Direct Mode tests only; no target-runtime storage cost, transaction consensus, or rollback guarantee has been measured.

## Design decisions

| Decision | Rationale | Assumptions | Limitations |
|---|---|---|---|
| One standalone Intelligent Contract | Matches the product boundary and avoids unnecessary trust/dependency chains. | GenLayer state and method limits can support a bounded registry. | A single contract still has finite storage and execution capacity; capacity must be measured. |
| Separate deterministic rules from nondeterministic evidence analysis | Only consensus-agreed results should change state; stable rules are easier to audit. | Documented `gl.eq_principle.*` or custom validator APIs are available in the pinned runner. | Exact runtime/API compatibility remains untested locally. |
| Immutable policy per obligation version | Reproducible historical evaluations require the rules used at observation time. | Policy can be represented in bounded, canonical fields. | Any policy change creates a new version; migration semantics need later design. |
| Evidence references and digests, not full archives | Limits state growth and provides a content commitment. | Users/reviewers can retain evidence elsewhere. | A digest alone cannot retrieve evidence or prove who published it. Availability depends on external retention. |
| Four-valued result plus explicit error/pending lifecycle | Prevents missing information or failed retrieval from becoming a violation or fulfillment. | Applications can handle non-final states. | Consensus transaction lifecycle and domain outcome must be kept distinct. |
| Bounded append-only observation records | Supports auditability and replay protection while limiting each call. | Per-obligation caps and pagination are acceptable. | A cap can stop new submissions; archive/indexing policy remains a product decision. |

## Proposed components and data

1. **Obligation registry.** A bounded `TreeMap[ObligationId, Obligation]` keyed by a deterministic ID. Store creator/authorized actors, subject identity/reference, lifecycle state, active policy version, and counters.
2. **Immutable policy versions.** The Stage 1 contract stores initial requirement descriptions and opaque approved-source references as immutable version 1. Future policies may define bounded source rules, evaluation windows, evidence limits, freshness constraints, and output schemas. Policy revision is deferred until version migration and authorization semantics are specified; do not infer that the Stage 1 registry implements revisions or policy digests.
3. **Approved source set.** Policy records allowed schemes/hosts/path patterns and expected content types/fields where practicable. Do not accept arbitrary URLs as authority. DNS/IP rebinding and redirects remain a retrieval-layer risk requiring tool/runtime review.
4. **Evidence manifest.** Bounded evidence records contain requested URL/source ID, normalized final URL if available, retrieval outcome, transaction observation time, source-claimed publication time (separate and explicitly untrusted), content digest, evidence type, and concise extracted facts. Keep raw content outside contract storage unless a later feasibility measurement justifies bounded on-chain storage.
5. **Nondeterministic evaluator.** Stage 2 fetches only exact HTTPS URLs stored in immutable source references through `gl.nondet.web.get`, then calls `gl.nondet.exec_prompt(..., response_format="json")`. It returns a bounded candidate with requirement assessments and exact source quotes. Storage writes occur after the nondeterministic callback returns.
6. **Consensus validator.** Stage 2 uses the documented `gl.vm.run_nondet_unsafe` custom callback to independently re-fetch/re-evaluate and require agreement on outcome, per-requirement status, evidence kind, source indexes, and exact quotes. Direct Mode callback simulations pass; actual validators have not been exercised.
7. **Deterministic commit path.** After the nondeterministic result returns, ordinary code checks owner/lifecycle/idempotency, derives the outcome, checks record and count bounds, then appends the record and updates indexes/counters. A true network consensus rejection/rollback remains unverified locally.
8. **Read views.** Bounded `@gl.public.view` methods expose obligation summaries, policy version/digest, individual observation records, and paginated history. Avoid an unbounded “return all records” view.

## Result model

- **FULFILLED:** agreed evidence supports every applicable criterion for this observation window.
- **VIOLATED:** agreed evidence affirmatively supports failure of at least one criterion under the policy.
- **INCONCLUSIVE:** evidence is missing, unavailable, stale, contradictory, or too weak to support either affirmative result.
- **PENDING:** an explicitly submitted evaluation has not reached an accepted/finalized domain result, or its lifecycle is incomplete. It is not a permanent conclusion.

Domain result is separate from GenLayer transaction status. A transaction rejected by consensus must not append a result. A retrieval/LLM failure should lead to `INCONCLUSIVE` if the contract can reach a consensus-approved bounded failure result, otherwise execution remains pending/failed under network lifecycle and no observation is committed. Missing evidence is never converted into `VIOLATED`.

## Deterministic vs nondeterministic boundary

**Deterministic:** authorization, ID construction, policy version immutability, schema and size bounds, accepted observation ordering, replay protection, time-window comparison using transaction context, digest computation over exact canonical bytes, history append, outcome storage, and pagination.

**Nondeterministic:** retrieving web content, rendering dynamic pages, AI interpretation/extraction, and any validator LLM judgement. Nondeterministic code returns candidates only. It must not read/write contract storage, mutate shared Python state, emit messages, or directly decide persistent state.

## Equivalence criteria

Do not compare free-form reasoning or whole webpage bodies. Define a canonical result with exact enum outcome, policy version/digest, requirement-level booleans/unknowns, source/evidence identifiers, and stable factual claims. Use exact equality for purely deterministic extracted values. For qualitative judgement, use a custom validator (or documented comparative/non-comparative wrapper) whose explicit rule is: independently check that each decisive claim is supported by approved evidence; all decisive requirement statuses must match; disagreement, unsupported claims, incomplete retrieval, or contradictory facts yields `INCONCLUSIVE` or validator disagreement. Store no LLM rationale as authority; a short explanation is descriptive and bounded.

Before implementation, create adversarial vectors that vary wording while holding facts constant, alter one decisive fact, inject instructions in page content, return malformed/oversized JSON, produce contradictory sources, and simulate unavailable sources. Compare validator decisions and test rotations/errors on the genuine runtime. This is a plan; no such tests have run.

## PoCC model

PoCC is an aggregate over policy-defined observation windows. Each window can be `FULFILLED`, `VIOLATED`, `INCONCLUSIVE`, or `PENDING`; the aggregate must report counts, covered interval, gaps, and policy versions. It may claim “fulfilled at each recorded observation” only when all required windows are present and fulfilled. It must not claim uninterrupted real-world compliance from periodic samples. Any gap, inconclusive period, policy discontinuity, or missed deadline prevents an “all recorded windows fulfilled” summary until resolved under explicit policy rules.

## Rationale and open design choices

This design favors conservative evidence status, bounded state, and transparent history over storing large raw evidence. Stages 1 and 2 now define the initial policy JSON encoding, IDs and caps, owner-only verification/closure, exact HTTPS source-reference convention, SHA-256 body commitment, custom validator criteria, and evidence-level `PENDING` semantics. Remaining decisions include verified host redirect and transport limits, measured target-network storage/compute costs, source freshness/authenticity policy, and Stage 4 observation-window/deduplication rules.
