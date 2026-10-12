# ProofPulse Threat Model (Stage 0 design and Stage 1/2 controls)

This document is not a security audit. It distinguishes implemented Stage 1/2 controls and mocked test coverage from remaining network/runtime risks.

## Assets and trust boundaries

**Assets:** obligation and policy state, evidence manifests/digests, observation chronology, authorization state, and the integrity of reported outcomes.

**Trust boundaries:** user-supplied policies/evidence references; external websites/APIs; LLM providers; leader and validator executions; GenLayer transaction context; and any off-contract evidence archive. Web and model outputs are untrusted. Consensus can establish agreement under a rule, but agreement does not make a source truthful.

## Threats and controls

| Threat | Risk | Controls / implementation status | Residual limitation |
|---|---|---|---|
| Prompt injection in web pages/documents | Content attempts to override task instructions or fabricate fields. | Stage 2 prompt explicitly treats page text as untrusted data; contract validates exact cited substrings and the custom validator independently re-fetches and reassesses decisive claims. Mocked injection text is covered in Direct Mode. | Prompt defenses are not complete; a model can still misinterpret evidence. No live-model adversarial or network-consensus test has run. |
| Malicious or unavailable sources | False content, redirects, downtime, malformed/oversized responses. | Stage 2 fetches exact HTTPS URL values from the immutable policy, bounds source count and post-response body bytes, commits successful body bytes, and maps retrieval failures to `INCONCLUSIVE`. | The URL belongs to the obligation creator's policy; redirects/final URLs, DNS rebinding, host-side SSRF controls, and pre-download response limits remain unverified. Allowlisting does not establish truth or availability. |
| False publication timestamp | Source invents or backdates dates. | Stage 2 records only the transaction-pinned observation time; source publication timestamps are not used as trusted time. | Transaction time cannot authenticate when a real-world event occurred or when an external page was published. |
| Conflicting evidence | Sources disagree and model chooses arbitrarily. | Stage 2 requires two exact, distinct-source quotes for a `CONFLICTED` assessment; deterministic aggregation maps any conflict to `INCONCLUSIVE`; the validator reruns the assessment. | Validator/source independence is not verified on a live network; source independence and evidentiary hierarchy remain policy decisions. |
| Unauthorized state changes | Attacker alters obligations, policies, evidence, or lifecycle. | Stage 1 creator-only closure remains; Stage 2 checks owner and `ACTIVE` status before any external/AI call. Direct Mode tests cover unauthorized and closed verification requests. | Ownership transfer, delegated roles, and live transaction authorization have not been implemented or network-tested. |
| Replay attacks | Same accepted evidence/evaluation submitted again. | Stage 2 rejects a repeated `(obligation_id, verification_id)` before retrieval and appends bounded sequential records. | A caller can deliberately use a new ID to create a later observation, including with unchanged page bytes; Stage 4 must define observation-window replay semantics. |
| Duplicate or reordered observations | Inflated history, duplicate windows, misleading continuity. | Unique window key; monotonic sequence/deadline checks; reject conflict; preserve accepted order. | Exceptional corrections require explicit supersession policy, never silent edits. |
| Unbounded storage/resource exhaustion | Large policy, content, histories or prompts exceed execution/storage budget. | Stage 1/2 bound per-source and aggregate returned body bytes, output text, source/requirement counts, record size, records per obligation, and contract-wide record count; raw pages are not persisted. | Retrieval body limits apply after `web.get` returns. Numerical caps/costs and runtime transport limits are not measured on Studionet. |
| False continuous-compliance claims | Sparse samples presented as proof of uninterrupted compliance. | Label output as sampled-window coverage; report gaps and `INCONCLUSIVE`; only aggregate required windows; prohibit uninterrupted claim from periodic snapshots. | Real-world state between observations remains unobserved absent continuous trusted instrumentation. |
| Validator disagreement / model/provider failure | Decision stalls, rotates, fails, or differs across validators. | Stage 2 uses `run_nondet_unsafe` and compares outcome, per-requirement status/type, source indexes, and exact quotes; fetch/model failures can yield `INCONCLUSIVE`. Direct Mode can invoke the captured callback under changed mocks. | Direct Mode does not enforce consensus or rollback. Consensus latency, real provider behavior, validator rotations, and network transaction rollback remain unverified. |
| Hash misuse or misleading provenance | Digest is mistaken for proof of authenticity or time. | Versioned canonical encoding; domain separation; store algorithm/version; state exact meaning of commitment; retain evidence externally. | Digest alone proves only byte consistency, not origin, truth, availability, or time. |

## Security invariants

1. Only authorized actors can change obligation lifecycle or policy state.
2. Historical policy/evidence/outcome references are immutable after acceptance.
3. No untrusted model or web result changes persistent state before consensus acceptance and deterministic validation.
4. `INCONCLUSIVE` covers missing, unavailable, stale, malformed, or contradictory evidence; it is not coerced to another result.
5. A replayed observation cannot create another period or change an earlier result.
6. Public outputs never imply continuous observation or authenticated source time unless the specific evidence mechanism supports that claim.
7. Every write has explicit resource bounds.

## Remaining security gates

Stages 1/2 define the owner actor, identifier and policy bounds, HTTPS source-reference rules, failure mapping, and verification-ID replay behavior. Before deployment, verify web redirect and transport-size controls, runtime storage/compute budgets, and transaction rollback on validator disagreement. Additional adversarial work should test malicious redirects and DNS behavior, source freshness, repeated/out-of-order observation windows, and borderline validator disagreement with genuine Studio/network execution. Existing Direct Mode tests do not establish these properties.
