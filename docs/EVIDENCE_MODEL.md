# ProofPulse Evidence Model (Stage 0)

Evidence is untrusted input. The model below separates an external source's statements from facts the contract can establish deterministically.

## Evidence record proposal

Each bounded manifest item should include:

- `evidence_id`: deterministic ID scoped to obligation and observation.
- `source_id`: policy-approved source rule identifier.
- `requested_url` and, if exposed by the retrieval API, normalized final URL/redirect chain summary.
- `retrieval_time`: transaction-pinned time at which the request was initiated/observation submitted.
- `claimed_published_at`: source/page-provided time, explicitly untrusted unless separately authenticated.
- `media_type`, retrieval status, and bounded byte count.
- `content_digest`: SHA-256 commitment to explicitly defined canonical bytes or extracted representation.
- `extract`: bounded, schema-constrained facts relevant to named policy requirements.
- `provenance_note`: bounded explanation of the source and extraction path.

The public observation links the manifest digest to the obligation ID, immutable policy digest/version, observation window, evaluator result, and consensus transaction reference where available to the client/indexer. Exact GenLayer transaction/block linkage exposed to contract code is limited: transaction context documents no block number or hash.

## Digest and commitment semantics

Use a domain-separated canonical encoding before hashing, for example a fixed version tag plus length-prefixed UTF-8 fields, then SHA-256. The official GenLayer docs include `hashlib.sha256()` in a contract example, so the algorithm is documented in the environment; exact canonical encoding and execution under ProofPulse's selected pinned runner remain unverified.

A digest proves only that later-presented bytes match the committed bytes, assuming the hash and canonicalization are implemented correctly. It does **not** prove source identity, publication time, authorship, truth, or that the content was publicly accessible at the claimed time. A URL is a locator, not a durable archive. If long-term audit requires retrieval, use a separately governed archive or content-addressed store off-contract and record its locator plus digest; that archive is outside the standalone contract's trust guarantee.

## Source policy

Policy should name approved sources and expected fields/domains rather than allow user-selected arbitrary URLs to drive verification. Prefer authenticated APIs, signed documents, or stable authoritative publications. Restrict schemes to HTTPS, normalize hostnames, define redirect behavior, constrain content types, and reject oversized or malformed payloads. Confirm what the GenLayer web host enforces (redirects, DNS/private address protections, response size and timeout) before relying on contract-level URL checks.

## Time fields

- **Observed/submitted time:** derive from deterministic transaction context (`datetime.now(timezone.utc)` / `gl.message_raw['datetime']`); this timestamps transaction execution, not the moment the validator runs.
- **Publication time:** retain as a source claim. A displayed page date is forgeable/editable unless backed by a trusted signature, transparency log, trusted timestamping authority, or independently corroborated archival capture.
- **Deadline time:** compare the contract transaction timestamp to the policy deadline deterministically. This only proves the submitted transaction timestamp falls before/after the configured value; it does not prove when an external event happened.

## Contradiction and missing data

Track source claims by requirement and source. Contradiction is present when approved evidence sources assert incompatible values for the same requirement/window under the policy's normalization rules. Do not resolve by majority count alone unless a policy justifies source independence and weighting. Incompatible decisive evidence yields `INCONCLUSIVE`; unavailable/stale evidence is also `INCONCLUSIVE`. Missing evidence must never be interpreted as proof of non-compliance.

## Resource bounds and retention

Before implementation set maximum evidence items and URL length, response/extract bytes, prompt length, records per obligation, policy versions, and page size. Store digests and concise extracts instead of full web pages; keep histories append-only with paginated reads. Define whether a cap halts new observations or requires a new obligation epoch. The current review found no measured ProofPulse storage or web limits, so values cannot responsibly be selected yet.
