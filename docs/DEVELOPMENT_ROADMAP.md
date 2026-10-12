# ProofPulse Development Roadmap

This roadmap tracks implemented and planned work. Stages 0–5 have documentation, implementation and local checks. The mixed CLI/SDK release lines and lack of a Studio Mode run remain blockers to genuine validator/network verification and deployment readiness.

## Stage 0: Technical feasibility and architecture

Confirm the supported GenLayer Intelligent Contract programming model, execution limits, validator consensus behavior, web and AI interfaces, and the available Studionet workflow. Define obligation/evidence models, outcomes, threat boundaries, and the standalone architecture. **Status:** documentation and Direct Mode feasibility checks complete. Current official docs and an isolated CLI profile confirm the stable Studionet alias/RPC/chain ID; the installed CLI 0.40 RC is not proven compatible with the installed earlier SDK/test line. Genuine remote execution remains unverified. See [Stage 0 Report](STAGE_0_REPORT.md), [Stage 0B Environment Report](STAGE_0B_ENVIRONMENT_REPORT.md), and [Final Readiness Report](FINAL_READINESS_REPORT.md).

## Stage 1: Obligation registry and lifecycle

Implement deterministic obligation registration, immutable initial requirement/source-reference policy, owner authorization, bounded reads, and owner-only closure. **Status:** complete locally; all 12 Stage 1 Direct Mode tests are preserved in the current 45-test suite. Policy revisions, reopening, deletion, and transfer remain deferred.

## Stage 2: AI-powered evidence verification

Integrate bounded evidence evaluation with explicit uncertainty handling. **Status:** implemented locally; mocked Direct Mode covers retrieval, model outputs, deterministic result derivation, validator callback behavior, malformed/forged leader results, and pickling checks. No live web/AI or genuine validator consensus has run. See [Stage 2 Implementation](STAGE_2_IMPLEMENTATION.md) and [Stage 2B Runtime Validation](STAGE_2B_RUNTIME_VALIDATION.md).

## Stage 3: Evidence provenance and timestamps

Add immutable policy commitments, evidence-manifest commitments, explicit source indexes/byte counts, transaction-pinned observation time, deadline relation, and observation-window identifiers. **Status:** implemented locally in record schema version 1. Hashes commit to stored policy/evidence fields; they do not authenticate publisher, truth, or publication time. No trusted source freshness metadata is available, so it is not inferred. See [Stage 3/4 Implementation](STAGE_3_4_IMPLEMENTATION.md) and [Evidence Model](EVIDENCE_MODEL.md).

## Stage 4: Proof of Continuing Compliance

Compute PoCC from accepted, unique time-window observations, reporting due windows, observed windows, missing windows, first gap, and conservative aggregate outcome. **Status:** implemented as a bounded read view; one accepted verification per time window, based on registration transaction time plus the configured period. A fulfillment summary means all due sampled windows were fulfilled and says nothing about intervening time. See [Stage 3/4 Implementation](STAGE_3_4_IMPLEMENTATION.md).

## Stage 5: Security and adversarial testing

Review authorization, policy/history integrity, untrusted external data, prompt injection, bounded resources, replay, conflicts, and forged consensus input. **Status:** local static/adversarial work complete for current source; 45 Direct Mode tests and cached GenVM lint pass. Transfer size, redirects, validator disagreement rollback, and actual host resource ceilings remain unverified; this is not an independent audit. See [Threat Model](THREAT_MODEL.md) and [Final Readiness Report](FINAL_READINESS_REPORT.md).

## Stage 6: Studionet deployment and verification

Validate with a coherent stable Studionet-compatible toolchain, run genuine Studio Mode tests for accepted/rejected transactions and rollback, then deploy only after those gates pass and deployment authorization is established. **Status:** blocked; no genuine Studio Mode test or deployment was performed. Do not claim deployment until independently verified.

## Stage 7: Final audit and submission readiness

Review code, docs, security results, integration receipts, clean-clone reproducibility, and deployment evidence. **Status:** local review package is prepared, but final submission readiness is blocked on genuine compatible runtime validation, deployment evidence, and Git metadata permissions in this Codex environment.
