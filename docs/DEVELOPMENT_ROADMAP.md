# ProofPulse Development Roadmap

This roadmap tracks implemented and planned work. Stage 0B documented a conditional-go environment result; Stages 1 and 2 have local implementations and tests but do not establish live validator consensus, stable Studionet compatibility, or deployment readiness.

## Stage 0: Technical feasibility and architecture

Confirm the supported GenLayer Intelligent Contract programming model, execution limits, validator consensus behavior, web and AI interfaces, and the available Studionet workflow. Define the obligation and evidence data model, outcome semantics, threat model, and a minimal architecture that respects the standalone contract boundary. Record feasibility findings and unresolved constraints before implementation. **Status:** architecture documentation and deterministic Direct Mode fixture complete; conditional go. The real-profile CLI still needs a normal-shell check, and stable Studionet toolchain compatibility is not yet established. See [Stage 0 Report](STAGE_0_REPORT.md) and [Stage 0B Environment Report](STAGE_0B_ENVIRONMENT_REPORT.md).

## Stage 1: Obligation registry and lifecycle

Implement deterministic obligation registration, immutable initial requirement/source-reference policy, owner authorization, bounded reads, and owner-only closure. **Status:** complete with conditional pass: 12 Direct Mode tests and GenVM lint/semantic validation pass. See [Stage 1 Implementation](STAGE_1_IMPLEMENTATION.md). Policy revisions, reopening, deletion, and transfer remain deferred. Stable Studionet compatibility is unverified.

## Stage 2: AI-powered evidence verification

Integrate evidence evaluation using the supported GenLayer capabilities. Define bounded, structured inputs and outputs, explicit uncertainty handling, and safeguards for untrusted evidence and web content. Verify that decisions are tied to stated requirements and do not silently treat missing evidence as success. **Status:** implemented with conditional pass. Direct Mode mocks cover retrieval, AI outputs, deterministic outcome derivation, and the custom validator callback; no live web/AI or real validator consensus has run. See [Stage 2 Implementation](STAGE_2_IMPLEMENTATION.md).

## Stage 3: Evidence provenance and timestamps

Extend Stage 2 records with the full evidence-provenance model, freshness rules, and robust source/observation linking. Stage 2 already records exact approved URL references, response SHA-256 commitments, transaction observation timestamps, and requirement assessments, but does not authenticate sources or publication dates.

## Stage 4: Proof of Continuing Compliance

Add observations across multiple periods and rules for evaluating continuity. Define how observation intervals, missed checks, status changes, and insufficient evidence affect the continuing-compliance result. Ensure each period can be interpreted in context without overwriting prior observations.

## Stage 5: Security and adversarial testing

Review authorization, lifecycle and history integrity, external-data handling, prompt-injection resistance, denial-of-service considerations, and consensus-sensitive behavior. Exercise adversarial evidence, conflicting sources, missing data, boundary cases, and invalid transitions. Document findings and resolve high-priority issues before deployment work.

## Stage 6: Studionet deployment and verification

Prepare a deployment candidate using the genuine GenLayer toolchain, deploy to Studionet, and verify the deployed contract and its intended interactions. Capture reproducible deployment details and distinguish on-chain observations from local assumptions. Do not claim deployment until it has actually succeeded and been verified.

## Stage 7: Final audit and submission readiness

Review the implementation, documented scope, security findings, and deployment evidence. Resolve release-blocking issues, confirm that known limitations and verification semantics are clear, and prepare the repository for final review or submission. Report remaining risks honestly.
