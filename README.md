# pidgin-meshcore research archive

Development evidence for the maintained
[pidgin-meshcore plugin](https://github.com/dadecoza/pidgin-meshcore).
Build and install the plugin from that repository. Nothing here is applied by
its installer, and this archive is not a release or an alternative plugin build.

## Current conclusions and reproducible validation

- [Revision ledger](REVISIONS.md): exact plugin/firmware/library references and
  explicit limits on pre-Git history and hardware firmware identification.
- [Protocol and architecture](current/PROTOCOL.md): USB framing, command layouts,
  identities, limits, presence, repeat matching and timeout policy.
- [Design decisions and rejected approaches](current/DECISIONS.md).
- [Reviewed issues and regression mapping](reviews/2026-10-30-review.md).
- [Validation coverage and hardware checklist](validation/TESTING.md).
- [Publication validation](validation/PUBLICATION.md): current build, regressions,
  staged install/uninstall, memory checks, link checks and publication audit.

## Historical experiments and observations

These records are dated development checkpoints; later entries can supersede
earlier behavior. Unknown source revisions are marked as unknown, never assigned
a fabricated Git commit.

- [Hardware observations](historical/HARDWARE.md): real USB/Pidgin integration,
  explicitly authorized channel tests and a heard repeat. Acceptance and repeats
  do not demonstrate recipient delivery. No direct over-the-air exchange was
  validated. Simulator coverage is listed separately.
- [Historical test output](historical/test-results.txt): selected sanitized
  compiler/test/Valgrind evidence across intermediate implementations.
- [Archived development README](historical/development-readme.md): expanded
  background, retained for context; use the maintained README for installation.
- [Host Pidgin compatibility investigations](host-compat/README.md): upstream
  GstDevice lifetime backport and a locally tested GStreamer shutdown workaround,
  patches, loopback-only harness and [historical results](host-compat/shutdown-results.txt).

## Evidence and privacy

Only sanitized source, documentation, patches and selected text logs are stored.
Device serial identifiers, real account labels and observed sender labels were
removed or replaced with examples. RF test message bodies were omitted. No
credentials, private keys, real channel secrets, conversations, personal Pidgin
profiles, packages, binaries, dumps or packet captures are included. Synthetic
fixture bytes and public upstream commit hashes are not device secrets.

New hardware/RF work requires explicit authorization. Current publication
validation uses PTYs/socketpairs and performs no RF testing. Historical host
patches are optional manual investigations for their recorded distro revision,
not advice to apply them indiscriminately to newer Pidgin versions.

The source/patch/harness material is GPL-2.0-or-later; see [LICENSE](LICENSE).
External projects retain their own licenses. Original repositories were read-only.
