# Publication validation — 2026-10-31

Plugin revision: [`fe078f29110a68f7ae326087ad2f8581d56130c3`](https://github.com/dadecoza/pidgin-meshcore/tree/fe078f29110a68f7ae326087ad2f8581d56130c3).
Firmware source emulated: MeshCore
`81dbae592ffad40b4212bc0b37e82b38da08f4bc` (companion-v1.18.0/protocol 14).
These are **simulator/host results**, not new hardware or over-the-air tests.

## Local results

Environment: Ubuntu 26.04.1 x86-64, Pidgin/libpurple 2.14.14, GLib 2.88.0,
OpenSSL 3.5.5, GCC 15.2.0, Valgrind 3.26.0. The host used the separately recorded
Pidgin compatibility packages; that is not a guarantee about stock host media
subsystems. CI uses distro dependencies independently.

| Check | Result |
| --- | --- |
| `make clean`, `make` | Passed; [compiler output](build.txt), no compiler warnings |
| `make test` | All 24 regressions and headless libpurple integration passed; [output](regressions.txt) |
| `make memcheck` | Zero errors and zero definitely/indirectly/possibly lost bytes; [output](memcheck.txt). GLib process-global reachable allocations remain. |
| Staged `make install` / `make uninstall` | Passed with temporary `DESTDIR` and `PLUGIN_DIR=/plugins`; installed bytes matched the built `.so`, removal verified. Live Pidgin installation untouched. |
| Production code preservation | All `src/` files byte-identical to the private pre-reorganization copy. Generic `chat` icon retained; no embedded asset/API/tooling. |
| Three reviewed fixes | Datagram draining, separate same-name channel conversations/stale-ID rejection, and final text/ACK/HUP tests retained and passed. |
| Documentation | Relative files/anchors checked across both worktrees. GitHub repository/revision links checked remotely; host citations checked as described below. |
| RF/hardware | No physical serial access or RF test messages during publication. Historical hardware evidence remains separate. |

## Independent GitHub CI

[Ubuntu 24.04 CI run 41137371607](https://github.com/dadecoza/pidgin-meshcore/actions/runs/41137371607)
completed successfully for the same plugin commit. Build, normal regressions,
core Valgrind and staged install/uninstall all passed using runner distro
packages. This independently exercises the plugin without the local host patches.
The run did not contact hardware or send RF.

## Documentation and external references

[Revision ledger](../REVISIONS.md) pins all source comparisons and identifies
unrecorded historical revisions. Local Markdown targets and anchors resolve.
The Pidgin issue, Debian issue and GStreamer documentation returned HTTP 200.
The upstream Mercurial changeset citation returned HTTP 418 (anti-bot response)
and could not be revalidated; its recorded abbreviated node is not silently
expanded to an invented full hash. Host patch/build instructions are historical,
manual and version-specific; they were not executed during this publication.

## Publication inspection

Both worktrees started without Git history; both GitHub repositories were absent.
They were created public on `main`, without replacing any repository or rewriting
existing history. A private original backup was retained outside either worktree.

Reviewed the intended tracked files and every reachable commit blob before
pushing: source/header/test code, manifests, docs, CI, patches and selected logs.
Inspected commit metadata/messages and file inventories. Pattern scans covered
private-key blocks, common GitHub/cloud/service credentials, authenticated URLs,
sensitive assignments, personal home paths and the known hardware serial ID.
No prohibited content was found after sanitization. Synthetic repeated-byte
fixture keys/contacts, fixed crypto vectors, public upstream hashes and GLib
random test seeds were reviewed as deliberate non-secret data.

Removed real device/account/observed-sender identifiers and test RF message
bodies from public evidence. Excluded profiles, private settings backups,
conversation logs, channel secrets, credentials, raw captures/dumps, package files,
compiled libraries/executables and the reproducible review ZIP. The public archive
retains selected sanitized text evidence and useful host patches/harness only.
This is a bounded content review, not a claim of exhaustive secret detection.

No host patches were applied, no Pidgin settings changed, and no release created.

## Exact host patch artifacts

SHA-256 of the archived patch bytes:

```text
ff6e8932c164964e4667566cee14fb46b30d29ff9e8f5ca0c21697082bcbc496  pidgin-2.14.14-gst-device-lifetime.patch
c8a0635b4828e5191868e77d6006d04c2fa458abc6fbdbbd49c39b60238df70f  pidgin-2.14.14-gstreamer-shutdown.patch
```

Target host versions and upstream provenance are in [REVISIONS.md](../REVISIONS.md).
