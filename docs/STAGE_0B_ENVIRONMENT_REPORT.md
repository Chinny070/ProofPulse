# ProofPulse Stage 0B Environment Report

**Date:** 2026-10-12  
**Decision:** **CONDITIONAL GO** — deterministic local development is verified; full stable Studionet compatibility and the user's normal-shell CLI run remain unverified.  
**Scope:** Non-destructive diagnosis, package/config inspection, isolated read-only CLI queries, and one disposable direct-mode test. No ProofPulse contract was implemented, no network was changed, and no blockchain transaction or deployment was made.

## 1. CLI error root cause

The EPERM is caused by the Codex sandbox identity and the CLI's startup behavior together. The Windows directory is owned by `ACHINNYS\\USERpc` and its ACL grants that user Full Control. The current tool process instead runs as `ACHINNYS\\CodexSandboxOffline`; the `ACHINNYS\\CodexSandboxUsers` ACE grants only Read and Execute. The directory is therefore read-only to the sandbox process even though it is writable by the normal user account.

The installed CLI's `ConfigFileManager` unconditionally calls `fs.chmodSync(folderPath, 0700)` for `%USERPROFILE%\\.genlayer` during initialization, and then does the same for the `keystores` directory. In the sandbox it fails on the first call, before CLI command execution. Source inspection confirms this behavior. Node.js v24.14.0 is not the cause: with the same Node and CLI, all requested CLI commands ran successfully when `USERPROFILE` was redirected to a disposable, writable profile containing only `{"network":"studionet"}`.

Diagnostics found an existing `.genlayer` directory and `genlayer-config.json` selecting `studionet`; no running GenLayer/Node process was found that would indicate a lock. The normal Windows user ACL is Full Control, so this does not look like a general Windows permission problem. The config content did not cause the error. The error is a sandbox write restriction exposed by the CLI's unconditional permission update.

No `.genlayer` contents or permissions were changed by this review. The CLI also runs config and keystore migration routines on startup; a normal-profile invocation may rewrite legacy config/keystore files if they need migration. See the safe procedure below.

## 2. Installed versions and compatibility

| Component | Installed | Evidence / compatibility conclusion |
|---|---:|---|
| Python | 3.12.10 | Meets the documented `genlayer-py` and `genlayer-test` Python >=3.12 requirement. |
| `genlayer-py` | 0.16.3 | Installed SDK imports successfully. The installed test package requires `genlayer-py >=0.13,<0.17`, so 0.16.3 satisfies the package's declared dependency range. SDK release versions track protocol generations; the docs advise using a matching SDK for the target deployment. |
| `genlayer-test` | 0.29.2 | Imports successfully; exposes `get_contract_factory`; pytest plugin and direct fixtures are installed. Metadata requires Python >=3.12 and `genlayer-py >=0.13,<0.17`. |
| GenLayer CLI | 0.40.0-rc.3 | Package metadata confirms this is a prerelease. CLI works under Node v24.14.0 with an isolated profile. It belongs to the documented Consensus v0.6 RC family, not an established stable-release pairing. |
| Node.js | v24.14.0 | No failure with the isolated profile; confirms the original startup EPERM is not a general Node 24 failure. |
| Python runner | `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` | Exact runner hash was present in the existing Direct Mode cache and the fixture loaded it. It is also the hash shown in current official contract examples. This confirms that this direct-mode fixture ran against that cached runner; it does not establish the runtime used by a live Studionet transaction. |

## 3. Stable Studionet versus Consensus v0.6 RC

Official network documentation identifies stable Studionet as alias `studionet`, RPC `https://studio.genlayer.com/api`, chain ID `61999`. Both the Python SDK's installed `studionet` preset and the isolated CLI's built-in `studionet` profile report that same endpoint and chain ID. Their explorer metadata reports `https://genlayer-explorer.vercel.app`, while the current official Networks page lists `explorer-studio.genlayer.com`; use the official page as the current reference and treat the local explorer preset as potentially stale. This is a static preset comparison; no RPC request or transaction was made.

Official Consensus v0.6 migration guidance describes a distinct coherent RC family: Consensus/node v0.6 RC, Studio v0.123 RC, `genlayer-js` v2.0 RC, `genlayer-py` v0.19 RC, CLI v0.40 RC, and matching v0.6-compatible prerelease `gltest`/fee tooling. That family targets `studio-dev`, RPC `https://studio-dev.genlayer.com/api`, chain ID `61997`. The docs explicitly distinguish this from stable Studionet and warn against mixing the chain preset and the RC endpoint.

Therefore the installed Python SDK/test pair is internally package-compatible and the stable Studionet preset is correct, but the installed CLI is the RC CLI. The exact stable CLI/SDK/test version combination for stable Studionet is not given in the reviewed official compatibility matrix. No authoritative evidence supports declaring this entire installed set compatible for stable Studionet writes or integration tests. Do not switch to Studio-dev or install the RC Python SDK as a workaround for the stable target. No automatic upgrades were made and no exact replacement stable versions are recommended without a published stable compatibility matrix.

## 4. CLI execution results

The CLI was first invoked with the real sandbox profile; startup failed with `EPERM` on `.genlayer` as described above. It was then run with `USERPROFILE` and `HOME` temporarily set to a disposable directory, preconfigured to the already-selected `studionet` alias. Results:

- `genlayer --version` — succeeded; `0.40.0-rc.3`.
- `genlayer --help` — succeeded; command list displayed.
- `genlayer network list` — succeeded; listed `studionet` and separate `studio-dev` aliases.
- `genlayer network info` — succeeded; `studionet`, `https://studio.genlayer.com/api`, chain ID `61999`.

The disposable CLI profile was removed afterward. The existing `%USERPROFILE%\\.genlayer` network selection was not changed. `network info` read the packaged network definition; it did not establish RPC availability or protocol compatibility.

### Safe commands for normal PowerShell

The sandbox-only failure should not require administrator access or broad ACL changes. In a normal PowerShell opened as the same Windows user, first inspect the current profile/ACL, then run the read-oriented CLI commands:

```powershell
$env:USERPROFILE
Get-Acl "$env:USERPROFILE\.genlayer" | Format-List Owner,AccessToString
genlayer --version
genlayer --help
genlayer network list
genlayer network info
```

These commands do not select another network, submit transactions, or deploy. CLI startup may migrate legacy config/keystore formats; back up `.genlayer` first if preserving a byte-for-byte copy matters. Do not use `genlayer network set` for this verification. Admin privileges are not indicated by the observed ACL.

## 5. Python import and direct-mode test results

- `import gltest` succeeded; `get_contract_factory` was exposed.
- `import genlayer` in ordinary host Python failed with `ModuleNotFoundError`. This is expected for the direct harness architecture: it supplies the contract SDK path when loading a contract with its `Depends` runner declaration.
- `genlayer-test` direct pytest plugin imported. A disposable contract outside the product tree declared one `u256` field, a view, and a write method. The test deployed it using `direct_deploy`, read the initial value, wrote a new value, and read it back.
- Result: **1 passed in 0.15s**, using Python 3.12.10, pytest 8.4.2, `genlayer-test` 0.29.2, and the cached runner hash shown above. The temporary contract and test file were removed.
- Direct Mode is local/in-memory and has no GenLayer Studio, network, or multi-validator consensus. This passing test does not prove Studionet compatibility.
- One initial attempt via the `gltest` wrapper with a temporary test path did not complete cleanly; it selected its default localnet profile and pytest reported a collection error before the run was interrupted. The explicit installed Direct Mode pytest plugin then ran the same deterministic round-trip successfully. Stage 1 should use the documented test invocation from the project root and confirm its exact behavior there.

## 6. Remaining blockers

1. The real-home CLI cannot run inside this Codex sandbox because the sandbox principal lacks write permission to `.genlayer`; a normal-user PowerShell invocation has not been performed by this agent.
2. The CLI installed here is `0.40.0-rc.3`. Official docs place CLI 0.40 RC in the Consensus v0.6 / Studio-dev family. A coherent stable Studionet toolchain pairing is not established from the reviewed official version matrix.
3. No RPC reachability, read-only remote call, Studio Mode integration, consensus execution, or live AI/web path was verified.
4. No authoritative exact stable replacement versions are documented in the sources reviewed; versions should not be guessed or upgraded automatically.

## 7. Recommended corrective actions

1. Have the repository owner run the read-oriented commands in the provided normal-user PowerShell block. If those also fail, capture the exact error and Windows ACL output; do not broadly relax permissions or elevate privileges without a specific finding.
2. Keep the active target at stable `studionet` (61999). Ask GenLayer's official release notes/support for the exact stable CLI + Python SDK + test package set; pin that coherent set only after confirmation.
3. Do not combine CLI 0.40 RC, `genlayer-py` 0.16.3, and `genlayer-test` 0.29.2 for claims of v0.6 RC compatibility. If later validating v0.6, use the complete matching RC family and its dedicated Studio-dev endpoint only as a separately authorized target.
4. For Stage 1 deterministic logic, use the verified Direct Mode path for fast feedback, then establish a supported stable Studio integration path before relying on external calls, validator consensus, or Studionet behavior.

## 8. Readiness decision

**CONDITIONAL GO.** The installed Python test framework can execute a deterministic contract fixture in Direct Mode, and the SDK/CLI built-in stable Studionet presets agree on alias, RPC, and chain ID. The CLI's EPERM is specifically caused by Codex sandbox ACLs and CLI startup chmod behavior; it works with the same Node/CLI in an isolated writable profile. Full stable Studionet compatibility is still unverified because the CLI is a v0.6 RC and no authoritative stable compatibility matrix was found. Do not declare GO until the owner confirms normal-shell CLI operation and the stable toolchain versions are established; no deployment or Stage 1 work was performed here.

## Official references

- [GenLayer Networks](https://docs.genlayer.com/developers/networks) — stable Studionet alias, endpoint, and chain ID.
- [GenLayer network configuration](https://docs.genlayer.com/developers/intelligent-contracts/deploying/network-configuration) — CLI aliases and separation between Studionet and Studio-dev.
- [Consensus v0.6 migration](https://docs.genlayer.com/developers/consensus-v06-migration) — compatible RC release family and Studio-dev target.
- [GenLayerPY SDK](https://docs.genlayer.com/api-references/genlayer-py) — SDK guidance and explicit v0.19 RC requirement for v0.6 preview.
- [GenLayer Testing Suite](https://docs.genlayer.com/developers/intelligent-contracts/testing) and [`genlayer-test` 0.29.2 on PyPI](https://pypi.org/project/genlayer-test/0.29.2/) — Direct/Studio modes, Python requirement, and test fixtures.
- [`genlayer-py` 0.16.3 on PyPI](https://pypi.org/project/genlayer-py/0.16.3/) — installed stable SDK release metadata.

Documentation and package metadata were reviewed on 2026-10-12. Local executable/package results are from this workspace; official docs were not treated as proof that a local or remote transaction succeeded.
