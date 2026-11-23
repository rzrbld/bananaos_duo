# Development and commits

## Start a change

Read [AGENTS.md](../AGENTS.md) and [STATE.md](STATE.md). Confirm the actual Git
root, branch, working tree and affected repository before editing. The local
bring-up workspace may contain this repository inside `port/`, plus historical
checkouts and large ignored build caches. Do not reset or clean unrelated work.

Find the owning layer in [ARCHITECTURE.md](ARCHITECTURE.md). Keep port changes in
authored files and external app changes in that app's repository. A package
installer can choose a compatible upstream artifact or provide supported launch
options; it cannot fix an unconditional unsupported CPU instruction through an
environment variable. Record binary/runtime evidence before choosing a fix.

For source/overlay changes:

```sh
make clean-source
make prepare
make test
```

`clean-source` removes the generated tree, not authored files or the build cache.
Buildroot stamps can retain stale packages after source or patch changes: rebuild
or dirclean the affected package deliberately. Use the normal full image target
before deployment. See [BUILD.md](BUILD.md) for full build/release commands.

Do not rebuild the kernel or rerun broad suites without a relevant change.
Use the focused test and then the required image checks. Boot, storage and update
changes need meaningful failure tests plus hardware verification. Display changes
need unequal-panel and real-page tests, not just a launcher screenshot.

## Commits and review

- Use the existing project author identity. Stage only the intended files and
  inspect `git diff --cached` and `git diff --check` before committing.
- Every authored commit includes this trailer:

  ```text
  Co-authored-by: Codex <noreply@openai.com>
  ```

- Keep related changes reviewable. Describe the concrete behavior changed and
  the validation actually performed; distinguish pending hardware checks.
- For OS work that should wait for nightly CI, include `[skip ci]` in the commit
  subject. The user explicitly allows local complete builds and device updates.
- Do not rewrite published tags, force-push shared history, or replace release
  assets. A changed public binary needs a new version.
- Preserve upstream licenses and attribution, including for code adapted into a
  patch. Never commit build outputs, generated source trees, credentials, raw
  device logs, recordings, ROMs or BIOS files.

## CI and independent update streams

| Repository | Validation | Release behavior |
| --- | --- | --- |
| `bananaos_duo` | Quick Checks on ordinary main pushes/PRs; local `make test` and image checks | Full firmware nightly at 00:00 UTC or manually; a manual run on a matching version tag publishes through CI |
| `slopetanium` | Its own UI/core/installer tests | Small app releases through its own CI; independent writable self-update |
| `gba-ds` fork | Rotation/pointer tests, cross-build and archive checks on PR/manual runs | `v*` tags build and publish installable Linux ZIPs and checksums through Actions |

Do not infer firmware release publication from a tag push: its workflow is
deliberately nightly/manual. Nightly branch artifacts are not public OTA releases.
No public assets are manually uploaded from the local build machine.

For the firmware, keep `VERSION`, board `RELEASE` and any release tag consistent.
For GBA DS Duo, use four-number versions such as `1.6.1.1` and `1.6.1.2`, which
the inherited updater compares correctly. A suffix-only fork counter would not.
Adding the fork to Slopetanium uses `rzrbld/gba-ds` as an App source and the Linux
AArch64 ZIP; the upstream app can remain installed separately.

Update [STATE.md](STATE.md) at handoff. Record source/release/local/installed
states separately, validation evidence locations, known limitations and the next
action. Link to stable commits or release pages; keep private logs local.
