# ProofPulse Stage 2 Implementation

**Scope:** External source retrieval, AI-assisted evidence interpretation, conservative outcomes, custom validator reassessment, and bounded verification records. Proof of Continuing Compliance is not implemented. No Studionet deployment or live-network transaction was attempted.

## Implemented methods

Stage 1 registry methods remain available. Stage 2 adds:

| Method | Access | Behavior |
|---|---|---|
| `verify_obligation(obligation_id, verification_id)` | Write | Owner-only verification for an active obligation, using only exact URLs from its immutable source policy. Stores one record after the nondeterministic call returns and the validator equivalence callback accepts. |
| `get_verification_record(obligation_id, verification_id)` | View | Returns one historical record by its caller idempotency key. |
| `get_verification_count(obligation_id)` | View | Returns the number of accepted local contract records for the obligation. |
| `get_latest_verification(obligation_id)` | View | Returns the most recently appended record. |

Verification IDs are unique per obligation and restricted to the registry's lowercase identifier alphabet, up to 64 UTF-8 bytes. Limits are 8 records per obligation and 64 records for the entire contract. These are code-level bounds, not measured Studionet quotas or cost estimates.

## Runtime API verification

Local environment versions already installed: Python 3.12.10, `genlayer-py` 0.16.3, `genlayer-test` 0.29.2, GenLayer CLI `0.40.0-rc.3`, and contract runner identifier `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. No package was installed or changed. Stage 0B found that this CLI is a Consensus v0.6 release candidate and stable Studionet compatibility is unverified.

Confirmed from official GenLayer documentation and the local test/linter surfaces:

- `gl.nondet.web.get(url)` retrieves external content inside a nondeterministic function. Official examples inspect response status and decode `body` bytes.
- `gl.nondet.exec_prompt(prompt, response_format="json")` requests structured AI output.
- `gl.vm.run_nondet_unsafe(leader_fn, validator_fn)` runs the leader path and a custom validator path; deterministic storage writes must occur after this call returns.
- A validator receives a `gl.vm.Return` with the leader's `calldata`; validators can independently re-fetch and reassess.
- `genlayer-test` Direct Mode mocks web/LLM requests and captures `run_nondet_unsafe` callbacks. Its `direct_vm.run_validator()` executes a captured callback with the current mocks.

There is a response-shape discrepancy across references/runtime versions: the current official web-access example refers to `response.status_code`, while the installed Direct Mode GenVM `Response` object exposes `status`, `body`, and `headers`. The contract reads `status_code` when present and otherwise `status`. The installed mock test confirms this fallback. Live network behavior for either field shape was not exercised.

References: [Web Access](https://docs.genlayer.com/developers/intelligent-contracts/features/web-access), [Calling LLMs](https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms), [Non-determinism](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism), [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), and [Testing](https://docs.genlayer.com/developers/intelligent-contracts/testing).

## Approved source rules and retrieval

The immutable `approved_sources_json` registry input remains unchanged. For Stage 2 retrieval, **every** source entry must itself be an exact HTTPS URL; otherwise verification records `INCONCLUSIVE` with `UNSUPPORTED_REFERENCE` and makes no web request. This keeps older opaque Stage 1 labels valid as registry entries without treating them as fetchable web addresses. No verification caller can submit or substitute a URL.

The Stage 2 fetchable URL subset accepts lowercase DNS hostnames with at least two labels and an optional simple path. It rejects non-HTTPS schemes, IP-literal/localhost-like hosts, credentials, ports, query strings, fragments, whitespace, and unsupported characters. Exact policy URLs are passed to `gl.nondet.web.get`; redirects and final URLs cannot be validated by this contract implementation because the installed response surface does not expose a final URL. Domain rebinding and host-side network controls remain outside this check.

Per response the contract caps decoded UTF-8 content at 4,096 bytes and total prompt content at 16,384 bytes, and caps source count at 8 (inherited from Stage 1). These are checked after `web.get` returns. The reviewed API does not expose a request-time response-byte cap, so this does not bound transport or pre-return memory usage; confirm GenLayer host limits before production use. Non-2xx responses, exceptions, malformed bodies, and over-limit bodies are recorded as non-success retrieval references and lead to `INCONCLUSIVE`, never `VIOLATED`.

## AI assessment and outcome rules

The AI prompt presents each page as untrusted evidence data and explicitly directs the model to ignore instructions embedded in page text. It requests one assessment per registered requirement with a status, evidence kind, source index, and exact quote. The model does not set the final outcome.

Deterministic validation requires the right number/order of assessments; recognized enums; exact source indexes; quote lengths no greater than 128 UTF-8 bytes; and exact quote substrings in retrieved source bodies. `MET`, `NOT_MET`, and `PENDING` require a grounded quote classified as `DIRECT_OBSERVATION` or `SOURCE_CLAIM`. `CONFLICTED` requires two distinct approved source indexes and two grounded quotes. Unsupported claims use `UNKNOWN` / `UNSUPPORTED` with no quote. Malformed, ungrounded, unavailable, or oversized results fall back to `INCONCLUSIVE`.

Outcome aggregation is deterministic:

| Outcome | Exact condition |
|---|---|
| `FULFILLED` | Every requirement is `MET`; every configured approved source was successfully retrieved. |
| `VIOLATED` | At least one requirement is affirmatively `NOT_MET`, all other requirements are `MET` or `NOT_MET`, and there is no missing, pending, or contradictory requirement. |
| `PENDING` | At least one requirement is explicitly `PENDING`; remaining requirements are `MET` or `PENDING`; there is no unknown, contradiction, or retrieval failure. This describes source evidence of an unfinished process, not an unfinished GenLayer transaction. |
| `INCONCLUSIVE` | Any source is unavailable/non-2xx/over-limit; AI output is malformed or ungrounded; any requirement is `UNKNOWN` or `CONFLICTED`; or no supported URL policy is present. |

The reduction is intentionally conservative: missing evidence never implies a violation; uncertainty or contradiction prevents a fulfillment/violation claim. The implementation does not determine freshness because Stage 1 policy has no freshness rule. Source publication dates are not treated as trusted timestamps.

## Validator equivalence

The contract uses the documented custom `gl.vm.run_nondet_unsafe` pattern, not `strict_eq` over model prose. The validator independently repeats source retrieval and AI assessment. It validates its own candidate, recomputes SHA-256 for retrieved bodies, checks grounded quotes, derives the outcome deterministically, and compares the outcome plus each requirement's status, evidence kind, source indexes, and exact cited quotes. Explanation prose and body digest equality are not equivalence criteria; exact page bytes can change between requests, while the validators must agree on the decisive structured evidence.

Direct Mode tests confirm the installed callback can be replayed with mocks and that a changed decisive result returns disagreement. This is **not** a genuine validator-consensus test: Direct Mode runs the callback in-process and does not gate state writes or apply consensus rollback. Real validator execution, rotations, external retrieval across validator nodes, and agreement behavior require GenLayer Studio/Studio Mode or a supported live network and remain unverified. No consensus-validation claim is made.

## Persistent record schema

Each append-only record is stored as a compact JSON string and contains:

```json
{
  "obligation_id": "...",
  "verification_id": "...",
  "sequence": 1,
  "outcome": "INCONCLUSIVE",
  "evidence": [
    {"url": "https://example.org/status", "retrieval": "OK", "http_status": 200, "sha256": "..."}
  ],
  "assessments": [
    {"requirement_index": 0, "status": "UNKNOWN", "evidence_type": "UNSUPPORTED", "source_index": -1, "quote": "", "conflicting_source_index": -1, "conflicting_quote": ""}
  ],
  "explanation": "...",
  "observed_at": 0
}
```

The SHA-256 value commits to the exact UTF-8 response body delivered to the contract. It does not prove origin, truth, authorship, publication time, or that the URL will remain available. The transaction-pinned timestamp records the verification transaction time only. Raw page bodies are not stored. Historical records are retrievable by unique verification ID; the latest record is separately indexed for bounded reads.

## Security controls and limits

- Owner authorization and active-lifecycle checks run before any external or AI call.
- Verification callers cannot pass a source URL or replace the immutable policy.
- Source URLs, call count, response/prompt body bytes, quotes, explanation, per-obligation record count, total record count, and record bytes are bounded.
- Candidate claims must cite exact excerpts from retrieved approved content; validator independently re-fetches and reassesses.
- Source failures and disagreement cannot be converted into `VIOLATED`; uncertainty is `INCONCLUSIVE` or a transaction-level consensus failure.
- Duplicate verification IDs are rejected before retrieval. A different ID can intentionally create a later observation, even if a page has unchanged bytes; Stage 4 must define observation windows and deduplication semantics.
- Prompt-injection instructions are explicitly treated as data, but prompt defenses are not a proof against model manipulation. Grounding and independent validator review reduce risk without eliminating it.
- The exact response-length cap, redirect/final-URL behavior, source authenticity, network/DNS isolation, web timeout, and runtime failure categorization are not verified on the live GenLayer host.
- Direct Mode cannot demonstrate transaction rollback on validator disagreement. Production safety relies on GenLayer's nondeterministic execution/consensus boundary; verify this in a compatible Studio integration environment before deployment.

## Test results

Command: `gltest tests/ -q` using the installed `genlayer-test` 0.29.2 Direct Mode pytest fixtures.

- **28 passed** in the latest run: 12 existing Stage 1 tests plus 16 Stage 2 tests.
- Stage 2 mocks exercised grounded success, callback re-assessment, simulated disagreement, rejection of a mismatched evidence digest, opaque/unapproved policy references, caller/closed-state authorization, duplicate IDs, HTTP 503, oversized content, contradictory sources, malformed AI JSON, ungrounded quotes, prompt-injection text handling, PENDING aggregation, and historical record retrieval.
- `genvm-lint check contracts/proofpulse.py` passed lint and semantic validation; `genvm-lint schema contracts/proofpulse.py` extracted the updated public ABI. The linter's remote latest-runner lookup was blocked by sandbox networking and it used cached tooling; no runner change was made.
- No live web request, real LLM call, Studio Mode run, independent network validator, Studionet call, transaction, or deployment was executed. `gltest` printed its default `localnet` configuration, but the selected Direct Mode fixtures ran in memory and made no RPC calls.

## Decision

**CONDITIONAL PASS.** The contract API, mocks, and custom validator callback are exercised locally against installed Direct Mode/linter versions. Real nondeterministic execution, validator consensus, response-size enforcement before download, redirect behavior, and stable Studionet compatibility remain unverified. Production use is not established.
