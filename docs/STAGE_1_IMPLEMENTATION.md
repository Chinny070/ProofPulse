# ProofPulse Stage 1 Implementation

**Scope:** Deterministic obligation registration and lifecycle only. No evidence is fetched or evaluated; no outcome, history, or PoCC computation is implemented. No deployment is claimed.

## Implemented contract

The primary Intelligent Contract is [`contracts/proofpulse.py`](../contracts/proofpulse.py). It uses the documented GenVM runner identifier in its first-line `Depends` comment, imports `genlayer`, inherits `gl.Contract`, and exposes public methods through `@gl.public.write` and `@gl.public.view`.

### Public methods

| Method | Access | Behavior |
|---|---|---|
| `register_obligation(...)` | Write | Validates bounded inputs, records the caller as creator, stores the initial immutable policy and transaction timestamp, and initializes lifecycle to `ACTIVE`. |
| `close_obligation(obligation_id)` | Write | Allows only the stored creator to move an `ACTIVE` obligation to `CLOSED`. |
| `get_obligation_metadata(obligation_id)` | View | Returns one bounded JSON string containing creator, description, lifecycle, registration timestamp, deadline, and period. |
| `get_lifecycle_state(obligation_id)` | View | Returns `ACTIVE` or `CLOSED`. |
| `get_policy(obligation_id)` | View | Returns version 1 and the immutable requirement/source-reference arrays as a JSON string. |
| `get_owner(obligation_id)` | View | Returns the stored creator address in GenLayer's `Address.as_hex` representation. |
| `get_obligation_counters(obligation_id)` | View | Returns total registry count and this obligation's requirement/source counts as JSON. |
| `get_registry_count()` | View | Returns the bounded total obligation count. |

Returning JSON as `str` keeps the public output ABI to a documented primitive while preserving structured data. Registration accepts requirement and source lists as JSON strings for the same reason; they are parsed, validated, and re-encoded compactly before storage.

## Storage schema

Persistent state uses explicitly typed GenLayer storage fields:

| Field | Type | Purpose |
|---|---|---|
| `owners` | `TreeMap[str, Address]` | Creator/only lifecycle operator, sourced from `gl.message.sender_address`. |
| `descriptions` | `TreeMap[str, str]` | Bounded human-readable obligation description. |
| `statuses` | `TreeMap[str, str]` | `ACTIVE` or `CLOSED`; domain lifecycle only. |
| `registered_at` | `TreeMap[str, u64]` | Unix seconds derived from GenVM's transaction-pinned `datetime`. |
| `deadlines` | `TreeMap[str, u64]` | Deadline timestamp; zero means none. |
| `observation_periods` | `TreeMap[str, u64]` | Observation interval in seconds; zero means none. |
| `requirements_json` | `TreeMap[str, str]` | Compact normalized JSON array, written once at registration. |
| `sources_json` | `TreeMap[str, str]` | Compact normalized JSON array of opaque approved source references. |
| `obligation_count` | `u32` | Total number registered, capped at 128. |

Separate maps make each persisted field a supported simple storage type and avoid storing arbitrary Python dictionaries. The public identifier is the key; it is not derived from a hash, so collision risk is handled by strict syntax, global uniqueness, and rejecting duplicates. A bounded global count limits registry growth. No enumeration method exists.

## Deterministic constraints

- Identifier: 1–64 UTF-8 bytes; lowercase ASCII `[a-z0-9][a-z0-9._:-]*`.
- Description: non-empty, trimmed, at most 512 UTF-8 bytes.
- Requirement list: JSON array of 1–8 unique, non-empty, trimmed strings; each is at most 256 UTF-8 bytes; encoded input at most 2,048 bytes.
- Approved source references: same list bounds as requirements. They are opaque policy labels, not URLs and are not fetched or authenticated in Stage 1.
- Registry: at most 128 obligations. This is a conservative code-level bound, not a measured GenVM storage quota or cost optimum.
- Deadline: zero means absent; a nonzero deadline must be later than registration's transaction timestamp and no greater than `253402300799` (9999-12-31T23:59:59Z).
- Observation period: zero means absent; otherwise 60 through 31,536,000 seconds inclusive.
- At least one of deadline or period must be nonzero. These are registration policy fields only; Stage 1 does not automatically expire or schedule obligations.
- Validate the complete call before the first storage write. GenLayer transaction rollback remains the runtime safety boundary; Direct Mode tests also assert observable state after rejected calls.

The byte/item caps are implementation choices to bound individual calls and state. Their aggregate execution/storage cost has not been measured on Studionet and they must be revisited after target-runtime measurements.

## Authorization and lifecycle

The registration caller becomes owner using the immediate caller `gl.message.sender_address`; no caller-supplied owner is accepted. Only that address can close the obligation. Views are public. Writes reject a nonexistent obligation, a non-owner caller, or any state other than `ACTIVE` before changing status.

Implemented lifecycle:

```text
UNREGISTERED --register--> ACTIVE --owner closes--> CLOSED
```

Policies are immutable version 1. Policy revision, reopen, deletion, ownership transfer, role delegation, and verification-outcome transitions are deferred. This avoids inventing unsafe policy migration or correction semantics in Stage 1. Lifecycle state remains separate from future `FULFILLED`, `VIOLATED`, `INCONCLUSIVE`, and `PENDING` verification outcomes.

## Direct Mode evidence

`genlayer-test` 0.29.2 was already installed. The command `gltest tests/ -q` executed actual `direct_deploy` / `direct_vm` pytest fixtures in Direct Mode: **12 passed in 1.83 seconds**. During iteration, tests found that unannotated class-level numeric bounds were observed as zero in the Direct Mode contract object; moving them to module-level constants fixed the issue. Two subsequent failures were test-only assumptions about `Address.as_hex` casing and were corrected by making address comparisons case-insensitive.

`genvm-lint check contracts/proofpulse.py` passed lint and SDK semantic validation (3 lint checks; 8 public methods). `genvm-lint schema contracts/proofpulse.py` extracted the ABI with six view methods and two write methods. The linter could not access its remote latest-runner lookup due sandbox network restrictions, used its local cached artifact, and reported that a newer runner is available. No runner upgrade was made. `git diff --check` completed without whitespace errors.

Direct Mode runs contract code in memory. It does not test validator agreement, live web/LLM calls, RPC behavior, stable Studionet compatibility, contract deployment, or production costs. No such tests or deployment were attempted.

## Stage 1 readiness

**CONDITIONAL PASS.** The deterministic registry and lifecycle pass all 12 Direct Mode tests, and GenVM lint, semantic validation, and ABI schema extraction succeeded against the locally cached runner. This supports local deterministic development. Stable Studionet compatibility, validator consensus, remote RPC behavior, and deployment remain unverified; these limits prevent a production-readiness claim.

## Remaining risks and deferred functionality

- Stage 1 does not validate semantic quality or identity of approved sources; references are labels only.
- A deadline is checked against the transaction-pinned registration timestamp; no evidence timing is judged yet.
- A period does not cause automatic observations and cannot establish uninterrupted compliance.
- Global limit and per-field limits have not been measured against Studionet storage/compute budgets.
- No update, revision, reopen, deletion, transfer, or recovery path is implemented.
- No evidence provenance digest, observation history, replay key, contradiction model, AI output, Equivalence Principle callback, or PoCC result is implemented.
- Stable Studionet compatibility remains unverified because Stage 0B found a CLI prerelease/toolchain pairing uncertainty. Direct Mode success is not a substitute.

## References

- [GenLayer first contract](https://docs.genlayer.com/developers/intelligent-contracts/first-contract) — runner comment, contract class, decorators, and persistent fields.
- [GenLayer storage reference](https://docs.genlayer.com/developers/intelligent-contracts/features/storage) — `TreeMap`, sized integers, storage defaults.
- [GenLayer transaction context](https://docs.genlayer.com/developers/intelligent-contracts/features/transaction-context) — `sender_address` and transaction-pinned time.
- [GenLayer testing](https://docs.genlayer.com/developers/intelligent-contracts/testing) — Direct Mode fixtures and limits.
