# ProofPulse

ProofPulse is a standalone GenLayer Intelligent Contract for evaluating real-world obligations using AI-assisted evidence verification, web-based information, and validator consensus.

## Purpose

ProofPulse is intended to make obligation status decisions more transparent and repeatable. A user defines an obligation and its requirements, submits or identifies evidence, and requests an evaluation. The contract is planned to consider relevant evidence and return a reasoned verification outcome through GenLayer's consensus process.

## Planned capabilities

- Register obligations, their requirements, owners, and relevant lifecycle state.
- Evaluate submitted evidence against an obligation's defined requirements with AI-assisted, web-informed analysis.
- Preserve evidence provenance and observation timestamps for later review.
- Record successive observations and evaluate compliance across multiple periods.
- Return explicit outcomes and supporting reasoning that validators can assess.

Stage 1 implements the deterministic obligation registry and lifecycle described in [Stage 1 Implementation](docs/STAGE_1_IMPLEMENTATION.md). Its local readiness is **conditional pass**: 12 Direct Mode tests and GenVM lint/semantic validation pass, while stable Studionet compatibility remains unverified. Evidence evaluation, provenance records, observation history, four-valued verification outcomes, and PoCC remain planned capabilities, not implemented behavior.

## Proof of Continuing Compliance

Proof of Continuing Compliance (PoCC) is ProofPulse's defining concept: compliance is assessed over multiple observation periods rather than inferred from a single snapshot. Each observation contributes to a history of whether an obligation continued to satisfy its requirements. The contract is intended to distinguish sustained compliance from a one-time result and to represent missing, conflicting, or insufficient evidence explicitly.

## Technology

The project is designed for GenLayer Intelligent Contracts and GenLayer's validator consensus, with AI-assisted evaluation and access to web-based information as part of evidence assessment. Development and deployment will use the GenLayer toolchain and a GenLayer network environment. Specific interfaces and execution details will be established during technical feasibility work; no mock blockchain is in scope.

## Development status

Stage 0 and Stage 0B documentation are complete with a **conditional go** recommendation for environment readiness. Stage 1 deterministic registry implementation and Direct Mode tests are complete. Stable Studionet compatibility remains unverified. **ProofPulse has not been deployed.**

See [Project Vision](docs/PROJECT_VISION.md), [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md), and the [Stage 0 Report](docs/STAGE_0_REPORT.md) for product scope, feasibility findings, and readiness gates.
