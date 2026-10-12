# ProofPulse Threat Model (Stages 0–5 local review)

This document is not a security audit. It distinguishes implemented Stage 1/2 controls and mocked test coverage from remaining network/runtime risks.

## Assets and trust boundaries

**Assets:** obligation and policy state, evidence manifests/digests, observation chronology, authorization state, and the integrity of reported outcomes.

**Trust boundaries:** user-supplied policies/evidence references; external websites/APIs; LLM providers; leader and validator executions; GenLayer transaction context; and any off-contract evidence archive. Web and model outputs are untrusted. Consensus can establish agreement under a rule, but agreement does not make a source truthful.

## Threats and controls

| Threat | Risk | Controls / implementation status | Residual limitation |
|---|---|---|---|
| Prompt injection in web pages/documents | Content attempts to override task instructions or fabricate fields. | Stage 2 prompt explicitly treats page text as untrusted data; contract validates exact cited substrings and the custom validator independently re-fetches and reassesses decisive claims. Mocked injection text is covered in Direct Mode. | Prompt defenses are not complete; a model can still misinterpret evidence. No live-model adversarial or network-consensus test has run. |
| Malicious or unavailable sources | False content, redirects, downtime, malformed/oversized responses. | The contract fetches exact HTTPS URL values from immutable policy; source indexes and URLs are retained; returned-byte counts, prompts, records, and history are bounded; retrieval failures become `INCONCLUSIVE`. | Body checks run after `web.get` returns and do not cap transfer/allocation. Redirect/final URL, DNS rebinding, and host egress controls remain unverified. Allowlisting does not establish truth or availability. |
| False publication timestamp | Source invents or backdates dates. | Stage 2 records only the transaction-pinned observation time; source publication timestamps are not used as trusted time. | Transaction time cannot authenticate when a real-world event occurred or when an external page was published. |
| Conflicting evidence | Sources disagree and model chooses arbitrarily. | Stage 2 requires two exact, distinct-source quotes for a `CONFLICTED` assessment; deterministic aggregation maps any conflict to `INCONCLUSIVE`; the validator reruns the assessment. | Validator/source independence is not verified on a live network; source independence and evidentiary hierarchy remain policy decisions. |
| Unauthorized state changes | Attacker alters obligations, policies, evidence, or lifecycle. | Stage 1 creator-only closure remains; Stage 2 checks owner and `ACTIVE` status before any external/AI call. Direct Mode tests cover unauthorized and closed verification requests. | Ownership transfer, delegated roles, and live transaction authorization have not been implemented or network-tested. |
| Replay attacks | Same accepted evidence/evaluation submitted again. | The contract rejects repeated `(obligation_id, verification_id)` and repeated observation windows before retrieval; accepted records are sequence-indexed for the bounded aggregate. | An accepted inconclusive sample occupies its window; retry waits for a later period. |
| Duplicate or reordered observations | Inflated history, duplicate windows, misleading continuity. | Period windows derive from transaction-pinned registration/observation time; one accepted record per window; earlier windows cannot follow later ones. | Transaction timestamp ordering and consensus rollback remain to be verified on a supported runtime. |
| Unbounded storage/resource exhaustion | Large policy, content, histories or prompts exceed execution/storage budget. | Contract bounds source/requirement counts, policy/input bytes, returned body bytes, output text, manifest record size, per-obligation history (8) and total history (64); PoCC reads at most 8 records; raw pages are not persisted. | Body limits apply after `web.get` returns. Runtime transfer, timeout, compute and storage cost are not measured on Studionet. |
| False continuous-compliance claims | Sparse samples presented as proof of uninterrupted compliance. | PoCC reports due/observed/missing windows and the first gap; only complete fulfilled due-window coverage yields `FULFILLED`; response text states it makes no claim about conditions between observations. | Real-world state between observations remains unobserved absent continuous trusted instrumentation. |
| Validator disagreement / model/provider failure | Decision stalls, rotates, fails, or differs across validators. | Stage 2 uses `run_nondet_unsafe` and compares outcome, per-requirement status/type, source indexes, and exact quotes; fetch/model failures can yield `INCONCLUSIVE`. Direct Mode can invoke the captured callback under changed mocks. | Direct Mode does not enforce consensus or rollback. Consensus latency, real provider behavior, validator rotations, and network transaction rollback remain unverified. |
| Hash misuse or misleading provenance | Digest is mistaken for proof of authenticity or time. | Schema/policy version, canonical sorted-key JSON policy and evidence-manifest commitments, exact source identities, and documented semantics. | Digest proves only byte/field consistency, not origin, truth, publisher, availability, or time. No signed publisher timestamp is verified. |

## Security invariants

1. Only authorized actors can change obligation lifecycle or policy state.
2. Historical policy/evidence/outcome references and accepted observation windows are immutable after acceptance.
3. No untrusted model or web result changes persistent state before consensus acceptance and deterministic validation.
4. `INCONCLUSIVE` covers missing, unavailable, stale, malformed, or contradictory evidence; it is not coerced to another result.
5. A replayed ID or repeated window cannot create another sample or change an earlier result.
6. Public outputs never imply continuous observation or authenticated source time unless the specific evidence mechanism supports that claim.
7. Every write has explicit resource bounds.

## Remaining security gates

Stages 1–4 define owner authorization, identifier/policy bounds, requested-URL constraints, conservative failure handling, ID/window replay protection, provenance commitments, and sampled-window aggregation. Before deployment, verify redirect and transport-size controls, runtime storage/compute budgets, and transaction rollback on validator disagreement. Source freshness/authenticity and malicious redirect/DNS defenses also need host/runtime review. Direct Mode does not establish these properties.
