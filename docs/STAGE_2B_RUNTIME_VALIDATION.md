# ProofPulse Stage 2B Runtime Validation

**Decision: CONDITIONAL PASS**  
**Scope:** Validation and security review of the existing Stage 1/2 implementation. No product features were added, no network was changed, and no contract was deployed.

## Summary

The current contract remains locally validated with the installed `genlayer-test` Direct Mode harness and cached GenVM lint runner. All 28 existing tests pass, lint and semantic validation pass, and the public schema extracts 12 methods. These checks do not establish real web access, LLM inference, validator execution, accepted/rejected transactions, persistent network state, or rollback.

The installed stack is still a mixed release line: CLI `0.40.0-rc.3` is identified in the Stage 0B investigation as the Consensus v0.6 RC family, while `genlayer-py 0.16.3` and `genlayer-test 0.29.2` are the earlier line. A coherent stable Studionet toolchain is not established. Docker inspection was blocked by the sandbox, so the presence of a local Studio service could not be verified. No live Studio or Studionet execution evidence was obtained.

## Environment and compatibility

| Component | Observed version/status | Finding |
|---|---|---|
| Windows | Windows PowerShell environment | Workspace accessible; profile and Docker pipe permissions are restricted by sandbox. |
| Python | 3.12.10 | Available. |
| `genlayer-py` | 0.16.3 | Installed; package metadata says `genlayer-test` accepts `>=0.13,<0.17`. |
| `genlayer-test` | 0.29.2 | Imports successfully; Direct Mode pytest fixtures run. |
| GenLayer CLI | 0.40.0-rc.3, from Stage 0B isolated-profile run | RC release line. The real-profile CLI startup requires writes to `.genlayer`; this sandbox cannot perform them. |
| Node.js | v24.14.0 | Available. Stage 0B isolated-profile check did not identify Node as the `.genlayer` EPERM cause. |
| Contract runner | `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` | Contract pins this runner. Local lint reports a newer runner but uses cached tooling; no runner update was made. |
| Intended network | Stable Studionet | Stage 0B found alias `studionet`, RPC `https://studio.genlayer.com/api`, chain ID `61999` in packaged presets. This Stage 2B pass made no RPC request. |

Stage 0B documents that CLI `0.40.0-rc.3` belongs to the Consensus v0.6 RC family associated with Studio-dev (chain `61997`), while the installed Python SDK/test packages satisfy their own declared dependency range. No authoritative stable compatibility matrix supporting this combined stack for Studionet writes was found in the earlier review. Network access to official documentation was denied in this sandbox during this Stage 2B pass, so this compatibility conclusion relies on the repository's Stage 0B observations and installed package metadata, not a fresh upstream check. Do not switch to Studio-dev to work around this mismatch.

## Genuine execution evidence

No genuine nondeterministic execution evidence was obtained:

- The Direct Mode test harness substitutes web and LLM operations with configured mocks.
- Inspection of the installed `gltest.direct.loader` shows its Direct Mode replacement for `run_nondet_unsafe` calls only the leader function and stores the validator callback in an in-memory list. It returns the leader result without requiring validator acceptance.
- `direct_vm.run_validator()` later invokes the captured callback manually against current mocks or a supplied leader result. The disagreement test therefore demonstrates that the callback returns `False` for a changed decisive result; it does not demonstrate an on-chain reject or rollback.
- There is no Direct Mode evidence of leader/validator node separation, transaction acceptance, transaction rejection, or committed persistent state after consensus.
- Docker daemon inspection returned access denied for the Docker config/engine pipe. No local Studio availability was established. The sandbox also blocked network sockets, so no live external web/LLM request or official documentation fetch could be performed.
- No Studio Mode integration test, live web retrieval, live LLM inference, Studionet RPC request, transaction, or deployment was attempted successfully.

Consequently, consensus callback invocation in the current Direct Mode tests must not be reported as genuine validator consensus.

## Custom equivalence audit

The existing validator callback independently invokes the same evaluation routine. That routine repeats retrieval from the exact registered URLs, invokes an LLM, validates the response against retrieved body text, and derives the outcome locally. It compares the aggregate outcome and every requirement's status, evidence type, source index, exact quote, and contradiction source/quote. It does not compare explanation prose or raw response digest equality. Exact quote comparison can cause disagreement when separate retrievals or model runs choose different valid excerpts, but removing quote/source identity from equivalence would weaken attribution; no change is recommended without genuine validator data and a deliberate equivalence policy.

The code does not prove that validator hosts or web/LLM providers are operationally independent. It preserves approved URL identity in each evidence item and requires contradiction quotes to come from distinct source indexes. Any retrieval failure produces an `INCONCLUSIVE` leader payload; if validators cannot agree on a valid result, the expected runtime behavior is a failed nondeterministic transaction, but this was not exercised here. Malformed model output is reduced to an `INCONCLUSIVE` assessment.

## Evidence retrieval and security findings

- **HTTPS / URL scope:** URL validation allows only a constrained HTTPS DNS-host form, rejects credentials, explicit ports, query strings, fragments, IP-like hosts and local names, and fetches only the exact immutable policy URL. This does not control DNS resolution, rebinding, redirect targets, or host-side egress policy.
- **Redirects:** the response surface used by the contract does not expose a verified final URL or redirect chain. The contract cannot prove that a redirect stayed within the approved destination. Follow redirects only if the host runtime can enforce destination restrictions or expose a validated final URL; otherwise treat redirect safety as an unresolved host-side gate.
- **Response size:** `MAX_EVIDENCE_BODY_BYTES` and aggregate limits are checked after `gl.nondet.web.get` returns. They bound text passed to the model and retained in transient contract values, but they do not prevent an oversized transfer or allocation before return. No request-time cap is available in the reviewed installed interface. Do not describe this as a download cap.
- **Unavailability / malformed data:** exceptions, non-byte bodies, non-2xx responses, oversized returned bodies, invalid UTF-8, malformed JSON/model shapes and ungrounded quotes map to `INCONCLUSIVE` or validator rejection. Missing evidence is not converted to `VIOLATED`.
- **Prompt injection:** page text is framed as untrusted data and exact quoted excerpts must be found in fetched text. This reduces some injection risk but does not prove model resistance. No live adversarial prompt test ran.
- **Publication claims:** source-provided publication timestamps are not used as trusted time. Records store the contract transaction timestamp only; that timestamp cannot authenticate when an external event occurred.
- **Conflicts:** a `CONFLICTED` assessment requires grounded quotes from distinct source indexes and derives `INCONCLUSIVE`. This ensures source identity is retained, but does not establish that sources are independent or equally authoritative.
- **Resource limits:** source count and returned prompt body, output quote, explanation, record, per-obligation history and total history limits exist. Runtime CPU, nondeterministic-call cost, HTTP timeout, transfer size, and Studionet storage/compute budgets were not measured.

## State integrity audit

Code inspection and Direct Mode regressions confirm that verification checks registered/ACTIVE status, owner authorization, identifier syntax and duplicate key before retrieval. History is capped at eight records per obligation and 64 globally. The policy has no mutation method; closing is owner-only and terminal. All verification writes happen after `run_nondet_unsafe` returns and after record size validation. Existing tests cover duplicate IDs, owner rejection, closed-obligation rejection, history preservation, and accepted Direct Mode writes.

This supports the intended transaction shape, but the installed Direct Mode harness is not evidence of rollback. Its `expect_revert` catches raised exceptions; the suite does not establish that a real validator rejection restores all persistent maps and counters. No Stage 2 test directly simulates a callback failure as part of the contract invocation and then asserts atomic rollback; `run_validator()` is a separate post-call operation. This remains a material runtime gate.

Repeated observations with different IDs remain intentionally allowed; the Stage 2 contract has no observation-window deduplication. A digest is a commitment to returned bytes, not an origin or timestamp attestation. Continuous compliance is not claimed by Stage 2.

## Regression and repository checks

Executed from the repository root:

| Command | Result |
|---|---|
| `gltest tests/ -q` | **PASS** — 28 passed in 3.63s; Direct Mode, mock-based. Harness selected default `localnet` configuration, but these fixtures ran in-memory and made no RPC calls. |
| `genvm-lint check contracts/proofpulse.py` | Initial output failed on PowerShell CP1252 when printing a Unicode checkmark after lint completed. Rerun with `$env:PYTHONIOENCODING='utf-8'`: **PASS**, 3 lint checks and semantic validation; 12 methods (9 view, 3 write). Latest-runner network lookup was blocked; cached runner used. |
| `genvm-lint schema contracts/proofpulse.py` | **PASS** — extracted constructor and all 12 public methods. Cached runner used after blocked latest-runner lookup. |
| `git diff --check` | **PASS** before this report was created; rerun after documentation changes before commit. |
| `python -c "import gltest"` | **PASS** — Direct Mode package imports. |
| `docker ps --format ...` | **BLOCKED** — access denied reading Docker config/engine pipe; local Studio presence unknown. |
| HTTPS documentation request from PowerShell | **BLOCKED** — sandbox denied socket access. |

No test was added or modified for this review. No direct or integration result is represented as a genuine network result.

## Code changes

No contract or test code changes were warranted by evidence available in this environment. The important retrieval limitations (redirect visibility and the post-return size check) depend on host runtime behavior unavailable to this contract code; adding speculative API calls would risk compatibility and would not establish the property. This report records these as blockers for genuine runtime validation.

## Remaining blockers and recommended action

1. Establish a supported, coherent stable Studionet-compatible CLI, Python SDK, test framework, and runner set from current official GenLayer release guidance. Do not mix the v0.6 RC CLI with the earlier SDK/test line based on assumption; do not install or upgrade automatically.
2. Make a compatible local Studio service available in an environment where the Studio runtime is supported, and run Studio Mode against that local runtime without changing network configuration.
3. Capture genuine transaction evidence for leader and validator web/LLM execution, custom callback invocation by validators, an accepted write, a rejected disagreement/failure, persistent state after acceptance, and complete rollback after rejection.
4. Confirm host-enforced redirect restrictions, request/response transfer limits, timeouts, and resource ceilings. If the web API cannot expose/enforce them, document the residual risk before deployment.
5. Revisit exact-quote equivalence only after observing genuine validator behavior; do not weaken source attribution solely to improve agreement rate.

## Final decision

**CONDITIONAL PASS.** Existing Direct Mode behavior, cached GenVM lint/semantic checks, and public schema extraction pass. Runtime compatibility remains mixed and unconfirmed; local Studio could not be inspected; no genuine web/LLM, leader/validator, transaction acceptance/rejection, persistence, or rollback evidence exists. This is not a deployment readiness decision.

Stage 2B stops here. Do not begin Stage 3 or implement Proof of Continuing Compliance without the user's next instruction.
