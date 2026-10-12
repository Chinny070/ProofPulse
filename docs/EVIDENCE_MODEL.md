# ProofPulse Evidence Model (Stages 0–4)

Evidence is untrusted input. Stage 2 implements a bounded subset: exact approved HTTPS URL references, retrieved response bytes, SHA-256 commitments, transaction observation time, and requirement-level cited assessments. This model describes the implementation plus remaining design needs; the contract does not authenticate source statements or publication times.

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

The current record schema version 1 links the exact approved URL and source index, successful response digest and returned body byte count, requirement-level assessment, outcome, verification ID/sequence, policy version/commitment, observation window, deadline relation, and transaction observation timestamp. It includes a canonical SHA-256 commitment over the policy and an evidence-manifest SHA-256 commitment over schema version, obligation/verification IDs, sequence, policy hash, window, result, source references, requirement assessments, timestamp, and deadline relation. The commitment excludes explanation prose. The digest is a commitment to a precisely encoded field set, not proof of source authenticity. The available contract transaction context does not expose a block number/hash in the reviewed interface, and the record does not claim to store one.

## Implemented record fields

- `schema_version` and `policy_version` (currently both version 1).
- `policy_sha256`: SHA-256 over compact UTF-8 JSON with sorted keys for policy version, normalized requirements, and exact approved-source strings.
- `observation_window`: `floor((observed_at - registered_at) / observation_period_seconds)` for period-based obligations; `-1` where PoCC windows do not apply or the verification is after the configured deadline.
- `deadline_evaluation`: `NO_DEADLINE`, `ON_OR_BEFORE_DEADLINE`, or `AFTER_DEADLINE`. This describes the verification transaction time only; it does not prove when performance occurred.
- Evidence references with source index, exact policy URL, retrieval status, HTTP status, body byte count returned, and SHA-256 for successfully retrieved bytes.
- `evidence_manifest_sha256` for the canonical decision-critical manifest described above.

For a configured period, window 0 begins at registration, and one subsequent window begins at each period boundary. The contract accepts at most one successful verification transaction per window and rejects attempts to fill an earlier window after a later one. Accepted `INCONCLUSIVE` results occupy a window too. This is a deliberate replay/resource rule; an unavailable source cannot be retried within the same window.

The `get_pocc_summary` view reports due, observed, and missing windows, the first missing index, per-window results, aggregate outcome, and a fixed sampled-scope statement. It iterates at most the eight records permitted for an obligation. Expected windows are counted through the current transaction time, capped at the configured deadline. No state is written by this view.

## Digest and commitment semantics

Stage 2 computes SHA-256 over the exact successful UTF-8 response body bytes returned by the Web API. The v1 record adds canonical policy and manifest commitments using compact UTF-8 JSON, sorted object keys, and SHA-256. The body hash is still a byte commitment and not an origin proof. These encodings are exercised under Direct Mode; live-runner behavior remains unverified.

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

The implementation bounds source and requirement counts, URL/policy bytes, returned per-source and aggregate body bytes, quotes, explanation, record size, records per obligation, and total records. Raw page bodies are not persisted; a sequence-to-verification-ID index enables the bounded PoCC view to enumerate each obligation's records. The caps (8 per obligation, 64 overall, 8 sources, 4,096 bytes per body, 16,384 aggregate returned body bytes, 8,192 record bytes) are code-level limits, not measured runtime quotas. The body checks occur after `web.get` returns and do not prevent an oversized transfer/allocation. The implementation has no independently trusted source-age/freshness field; webpage publication dates remain untrusted. Transaction-time windows measure observation cadence only, not source-content freshness.
