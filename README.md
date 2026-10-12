# ProofPulse

ProofPulse is a standalone GenLayer Intelligent Contract for registering real-world obligations, checking approved external evidence with AI-assisted validator consensus, and summarizing compliance across sampled observation windows.

## Purpose

ProofPulse makes each verification traceable to an immutable obligation policy, approved sources, structured evidence assessments, and a transaction-time observation. Missing, unavailable, stale, ungrounded, or contradictory evidence must not be represented as a supported violation or fulfillment.

## Current capabilities

- Register bounded obligations with owner authorization, immutable version 1 requirements/source policy, and an `ACTIVE` → `CLOSED` lifecycle.
- Retrieve only policy-approved HTTPS URLs and request structured AI assessments within GenLayer's nondeterministic execution boundary.
- Reassess independently in a custom validator callback and compare decision-critical outcome, requirement statuses, evidence kinds, source identities, and grounded excerpts.
- Record `FULFILLED`, `VIOLATED`, `INCONCLUSIVE`, or evidence-level `PENDING` outcomes, policy and evidence-manifest SHA-256 commitments, source references, body byte counts, observation windows, and transaction timestamps.
- Enforce unique verification IDs, one accepted sample per time window, bounded histories, and deterministic PoCC summaries with explicit missing-window counts.

## Proof of Continuing Compliance

PoCC summarizes only the observation windows due under an obligation's configured period. A `FULFILLED` summary means each due sampled window has an accepted `FULFILLED` record; it does not establish what happened between observations. A missing window, uncertain record, or contradictory evidence prevents an overall fulfillment claim. Source publication dates are not trusted; timestamps refer to the GenLayer transaction context.

## Technology and boundaries

The implementation uses GenLayer's Python Intelligent Contract model, typed persistent storage, public view/write methods, `gl.nondet.web.get`, `gl.nondet.exec_prompt`, and `gl.vm.run_nondet_unsafe`. It is one standalone contract: there is no frontend, dashboard, mock blockchain, or required cross-contract dependency. Direct Mode tests mock web/LLM calls; they do not establish genuine validator consensus.

## Development status

Stages 0–5 now have feasibility, implementation, and local security/regression documentation. Current local checks pass, but the installed CLI (`0.40.0-rc.3`) belongs to the Consensus v0.6 release-candidate line and is not a verified compatible toolchain for stable Studionet with the installed `genlayer-py 0.16.3` / `genlayer-test 0.29.2`. The Studionet network definition was confirmed in an isolated CLI profile as alias `studionet`, RPC `https://studio.genlayer.com/api`, chain ID `61999`. No live contract execution, genuine network validator consensus, or rollback has been verified. **ProofPulse has not been deployed.**

See [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md), [Contract Architecture](docs/CONTRACT_ARCHITECTURE.md), [Stage 3/4 Implementation](docs/STAGE_3_4_IMPLEMENTATION.md), and [Final Readiness Report](docs/FINAL_READINESS_REPORT.md).
