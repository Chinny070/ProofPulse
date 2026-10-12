# ProofPulse Threat Model (Stage 0)

This is a design threat model, not an audit or evidence of implemented mitigation.

## Assets and trust boundaries

**Assets:** obligation and policy state, evidence manifests/digests, observation chronology, authorization state, and the integrity of reported outcomes.

**Trust boundaries:** user-supplied policies/evidence references; external websites/APIs; LLM providers; leader and validator executions; GenLayer transaction context; and any off-contract evidence archive. Web and model outputs are untrusted. Consensus can establish agreement under a rule, but agreement does not make a source truthful.

## Threats and planned controls

| Threat | Risk | Planned controls | Residual limitation |
|---|---|---|---|
| Prompt injection in web pages/documents | Content attempts to override task instructions or fabricate fields. | Delimit evidence as quoted data; instruct model to ignore embedded instructions; extract only policy-required fields; validate against source structure and deterministic constraints; validators independently inspect evidence. | Prompt defenses are not complete; arbitrary semantic evidence can remain ambiguous. Adversarial consensus tests required. |
| Malicious or unavailable sources | False content, redirects, downtime, malformed/oversized responses. | Allowlisted source IDs, HTTPS and redirect policy, strict size/type/time bounds, graceful `INCONCLUSIVE`, bounded source count. | Source allowlisting does not guarantee source security or uptime; GenLayer host/network enforcement details need verification. |
| False publication timestamp | Source invents or backdates dates. | Separate claimed publication time from transaction-observation time; require signatures or independent timestamp/archive evidence for stronger claims. | Transaction timestamp cannot authenticate an external publication date. |
| Conflicting evidence | Sources disagree and model chooses arbitrarily. | Preserve per-source claims; define requirement-specific conflict rules; classify material contradiction as `INCONCLUSIVE`; no ungrounded majority vote. | Source independence and evidentiary hierarchy are policy choices, not automatic properties. |
| Unauthorized state changes | Attacker alters obligations, policies, evidence, or lifecycle. | Deterministic role checks on every write; creator/admin and subject roles explicit; immutable policy versions; test caller and internal-call semantics (`sender_address` vs `origin_address`). | No roles are implemented; exact authority model awaits product decisions. |
| Replay attacks | Same accepted evidence/evaluation submitted again. | Deterministic idempotency key over obligation epoch, policy version, window and evidence digest; reject conflicting reuse; append once. | Transaction nonce/replay protections are not a substitute for application-level deduplication. |
| Duplicate or reordered observations | Inflated history, duplicate windows, misleading continuity. | Unique window key; monotonic sequence/deadline checks; reject conflict; preserve accepted order. | Exceptional corrections require explicit supersession policy, never silent edits. |
| Unbounded storage/resource exhaustion | Large policy, content, histories or prompts exceed execution/storage budget. | Hard caps, bounded pages, compact hashes/extracts, no raw-page archive on-chain, bounded calls. | Numerical caps/costs are unknown until measured in target runtime. |
| False continuous-compliance claims | Sparse samples presented as proof of uninterrupted compliance. | Label output as sampled-window coverage; report gaps and `INCONCLUSIVE`; only aggregate required windows; prohibit uninterrupted claim from periodic snapshots. | Real-world state between observations remains unobserved absent continuous trusted instrumentation. |
| Validator disagreement / model/provider failure | Decision stalls, rotates, fails, or differs across validators. | Keep output schema small; compare decisive fields; validators independently assess evidence; treat disagreement/errors as no committed observation or `INCONCLUSIVE` under verified error handling; monitor transaction status off-contract. | Consensus latency, provider behavior, and error lifecycle are platform/runtime dependent and not measured here. |
| Hash misuse or misleading provenance | Digest is mistaken for proof of authenticity or time. | Versioned canonical encoding; domain separation; store algorithm/version; state exact meaning of commitment; retain evidence externally. | Digest alone proves only byte consistency, not origin, truth, availability, or time. |

## Security invariants

1. Only authorized actors can change obligation lifecycle or policy state.
2. Historical policy/evidence/outcome references are immutable after acceptance.
3. No untrusted model or web result changes persistent state before consensus acceptance and deterministic validation.
4. `INCONCLUSIVE` covers missing, unavailable, stale, malformed, or contradictory evidence; it is not coerced to another result.
5. A replayed observation cannot create another period or change an earlier result.
6. Public outputs never imply continuous observation or authenticated source time unless the specific evidence mechanism supports that claim.
7. Every write has explicit resource bounds.

## Stage 1 security gate

Before merging implementation, define actor roles, canonical identifiers/encoding, per-call caps, deadline rules, redirect/source policy, failure mapping, and correction/supersession behavior. Later security testing must include injection strings embedded in source content, malicious redirects, HTTP errors, oversized responses, stale and false timestamps, contradictions, repeated/out-of-order windows, unauthorized callers, malformed LLM output, and validator disagreements on borderline evidence. No such implementation or testing has occurred in Stage 0.
