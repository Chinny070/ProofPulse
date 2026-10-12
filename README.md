# ProofPulse

ProofPulse is a standalone GenLayer Intelligent Contract for evaluating real-world obligations using AI-assisted evidence verification, web-based information, and validator consensus.

## Purpose

ProofPulse aims to make obligation status decisions more transparent and repeatable. Owners register an obligation, its requirements, and an immutable list of approved sources. They can request an AI-assisted verification of those sources; actual multi-validator behavior has not yet been exercised in this repository.

## Implemented capabilities

- Register obligations, their requirements, owners, and relevant lifecycle state.
- Retrieve only exact HTTPS URLs from an obligation's immutable approved-source list.
- Assess evidence against requirements with bounded AI output and independently rerun assessment in a custom validator callback.
- Record `FULFILLED`, `VIOLATED`, `INCONCLUSIVE`, or evidence-level `PENDING`, with bounded source references, body hashes, excerpts, and transaction timestamps.
- Keep verification history append-only and bounded.

## Planned capabilities

- Evidence freshness and fuller provenance rules.
- Proof of Continuing Compliance (PoCC) across defined observation periods.

Stage 1 implements the deterministic registry and lifecycle. Stage 2 implements owner-triggered evidence assessment and records. Stage 2 has a **conditional pass** based on Direct Mode mocks and local GenVM linting; real validator consensus and stable Studionet execution remain unverified. See [Stage 1 Implementation](docs/STAGE_1_IMPLEMENTATION.md) and [Stage 2 Implementation](docs/STAGE_2_IMPLEMENTATION.md). PoCC remains planned and is not implemented.

## Proof of Continuing Compliance

Proof of Continuing Compliance (PoCC) is ProofPulse's defining concept: compliance is assessed over multiple observation periods rather than inferred from a single snapshot. Each observation contributes to a history of whether an obligation continued to satisfy its requirements. The contract is intended to distinguish sustained compliance from a one-time result and to represent missing, conflicting, or insufficient evidence explicitly.

## Technology

The project is designed for GenLayer Intelligent Contracts and GenLayer's validator consensus, with AI-assisted evaluation and access to web-based information as part of evidence assessment. Development and deployment will use the GenLayer toolchain and a GenLayer network environment. Specific interfaces and execution details will be established during technical feasibility work; no mock blockchain is in scope.

## Development status

Stages 0 and 0B documentation are complete; Stages 1 and 2 are implemented with conditional local readiness. Real consensus and stable Studionet compatibility remain unverified. **ProofPulse has not been deployed.**

See [Project Vision](docs/PROJECT_VISION.md), [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md), and the [Stage 0 Report](docs/STAGE_0_REPORT.md) for product scope, feasibility findings, and readiness gates.
