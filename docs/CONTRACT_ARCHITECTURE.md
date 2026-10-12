# ProofPulse Contract Architecture (Stage 0)

This document proposes architecture only. It does not define an implemented ABI or claim that any contract execution has been tested.

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
2. **Immutable policy versions.** Each policy defines requirement identifiers and bounded descriptions, approved source rules, evaluation window/deadline rules, maximum evidence count/bytes, freshness constraints, and the consensus output schema. Store a canonical policy encoding and digest. Any update appends a new version; historical observations point to the exact version used.
3. **Approved source set.** Policy records allowed schemes/hosts/path patterns and expected content types/fields where practicable. Do not accept arbitrary URLs as authority. DNS/IP rebinding and redirects remain a retrieval-layer risk requiring tool/runtime review.
4. **Evidence manifest.** Bounded evidence records contain requested URL/source ID, normalized final URL if available, retrieval outcome, transaction observation time, source-claimed publication time (separate and explicitly untrusted), content digest, evidence type, and concise extracted facts. Keep raw content outside contract storage unless a later feasibility measurement justifies bounded on-chain storage.
5. **Nondeterministic evaluator.** A local callback inside a write method fetches only policy-approved inputs through `gl.nondet.web.get` or `.render`, then calls `gl.nondet.exec_prompt` for a constrained classification/extraction task. It returns a small, schema-checked candidate. No storage writes occur inside this block.
6. **Consensus validator.** Validators independently re-fetch/re-evaluate where practical or independently assess the leader candidate against the same approved evidence and explicit criteria. They validate substantive facts and policy outcomes, not merely JSON shape. Deterministic fields (IDs, policy digest, window, source allowlist, timestamp bounds, evidence digest format) are checked in ordinary code.
7. **Deterministic commit path.** Once the non-deterministic result passes the equivalence rule, deterministic code validates input bounds, caller rights, current lifecycle, non-duplicate observation ID/window, and timestamp/deadline rules, then appends exactly one immutable observation and updates indexes/counters.
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

This design favors conservative evidence status, bounded state, and transparent history over storing large raw evidence. Stage 1 must decide canonical policy encoding and IDs, caps, source allowlist syntax, actor roles, deadline/grace semantics, content digest format, exact consensus validator strategy, and how non-final transaction lifecycle maps to `PENDING`. These depend on runtime measurements and product requirements.
