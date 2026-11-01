# Revision ledger

## 2026-11-01 follow-up publication

Current plugin revision: [`8c12c3bf90caf7a1c72079d5688410108b9076f9`](https://github.com/dadecoza/pidgin-meshcore/tree/8c12c3bf90caf7a1c72079d5688410108b9076f9). This contains persistent companion/channel log identities, readable saved-chat aliases and title refresh, silent intentional-close presence cleanup, and expanded libpurple regressions including single-character contact aliases.

`make test` passed all 24 core regressions plus expanded headless integration against real libpurple. Actual Pidgin GUI checks used a private profile and PTY simulator: readable tabs/title/header across reconnect, slot/name changes and incoming messages; reopening; and View Log retrieval of a prior session. No RF testing was performed for these fixes. The user subsequently confirmed room presentation and shutdown behavior in their live installation; that report is not an independently recorded hardware delivery test.

Dated validation records preserve exact intermediate working-tree hashes. The final committed source/test bytes match the latest shutdown record plus the unchanged meshcore.c/meshcore.h hashes in the persistent-history record. The maintained README was updated for publication. The earlier single-character contact investigation separately records explicitly authorized advert reception, with unknown flashed firmware revisions; it does not validate room message delivery.

The original publication and upstream revision ledger below remain historical evidence. Upstream source references are unchanged.

## Published implementation and source references

Original publication claims and tests apply to maintained plugin
commit [`fe078f29110a68f7ae326087ad2f8581d56130c3`](https://github.com/dadecoza/pidgin-meshcore/tree/fe078f29110a68f7ae326087ad2f8581d56130c3).
The plugin was first placed under Git during this publication. It has no earlier
Git history. Production C/header bytes were compared with the private pre-tidy
copy and are unchanged. One observed nickname in a synthetic test was replaced
with an invented Unicode label; protocol behavior and assertions are preserved.

| Upstream | Exact reference used | Purpose |
| --- | --- | --- |
| MeshCore firmware | [`81dbae592ffad40b4212bc0b37e82b38da08f4bc`](https://github.com/meshcore-dev/MeshCore/tree/81dbae592ffad40b4212bc0b37e82b38da08f4bc), tag companion-v1.18.0, protocol 14 | Authoritative serial, message, datagram, crypto and queue layouts |
| meshcore_py | [`ee987216b3364b64043766bda8b0037a90001c77`](https://github.com/meshcore-dev/meshcore_py/tree/ee987216b3364b64043766bda8b0037a90001c77) | Independent transport/reader comparison |
| pidgin-meshtastic | [`f311404cad11b3cabe5c354db175d1c411480fac`](https://github.com/dadecoza/pidgin-meshtastic/tree/f311404cad11b3cabe5c354db175d1c411480fac) | Pidgin integration patterns; repository left untouched |
| MeshCore Open | [`ac28dac575d591976d848a34f66a1d7a44b676dc`](https://github.com/zjs81/meshcore-open/tree/ac28dac575d591976d848a34f66a1d7a44b676dc) | Channel-repeat behavior comparison |
| meshcore.js | [`26193c059fcd1d0524f1ad5b19fd88287ecc5c61`](https://github.com/meshcore-dev/meshcore.js/tree/26193c059fcd1d0524f1ad5b19fd88287ecc5c61) | Companion packet/repeat comparison |
| Pidgin source | Ubuntu source package `1:2.14.14-1ubuntu3` | Frontend icon lookup and host media/sound investigations |

All source comparisons used read-only upstream checkouts. The closed official
native app was not source-audited. The generic `chat` icon is retained; the
rejected embedded-image experiment is not present in the maintained source.

## Investigation applicability and provenance limits

| Investigation/evidence | Plugin revision | Firmware revision or hardware scope |
| --- | --- | --- |
| `current/PROTOCOL.md`, `current/DECISIONS.md` | `fe078f29110a68f7ae326087ad2f8581d56130c3` | Firmware source `81dbae592ffad40b4212bc0b37e82b38da08f4bc` |
| `reviews/2026-10-30-review.md` | Fixes verified in `fe078f29110a68f7ae326087ad2f8581d56130c3`; exact vulnerable pre-Git revision unavailable | Same firmware source; simulator regressions, no new RF |
| `validation/TESTING.md` coverage and `validation/PUBLICATION.md` | `fe078f29110a68f7ae326087ad2f8581d56130c3` | Same firmware source emulated by PTYs/socketpairs; no hardware access |
| `historical/test-results.txt` | Dated unversioned development checkpoints; intermediate plugin commits were never recorded | Same reviewed firmware source; simulator output only |
| `historical/HARDWARE.md` | Multiple dated unversioned checkpoints; not validation of `fe078f29110a68f7ae326087ad2f8581d56130c3` | Device reported protocol 14; exact flashed firmware build/commit was not captured. Do not equate this with the reviewed source SHA. |
| `historical/development-readme.md` | Unversioned pre-publication documentation, retained for context | Firmware reference as above; hardware claims limited by the hardware record |
| `host-compat/*` | Independent of MeshCore; original hang/crash also reproduced without a MeshCore account | No firmware applicability or RF; target host source/package versions below |

Historical logs mix earlier test counts and command lines. They are useful
observations but cannot reproduce an unrecorded intermediate source state.
Current 24-test results have an exact plugin commit and are recorded separately.
The original report of three defects also predates Git; do not invent a
vulnerable commit from the later fixed snapshot.

## Host-only patch identities

Both patches target Ubuntu Pidgin source `1:2.14.14-1ubuntu3`:

- `host-compat/pidgin-2.14.14-gst-device-lifetime.patch` backports the recorded
  upstream Mercurial changeset `b0cd433f154a` (the historical record contains
  this abbreviated node ID, not its full hash). It produced local libpurple
  `1:2.14.14-1ubuntu3+meshcorefix1`.
- `host-compat/pidgin-2.14.14-gstreamer-shutdown.patch` is a local, distinct
  workaround, with no claimed upstream commit. The tested Pidgin executable
  package was `1:2.14.14-1ubuntu3+meshcorefix2`; libpurple remained at fix1.
- Exact patch content hashes are listed in [publication validation](validation/PUBLICATION.md).
  No binary packages or private settings backups are included.

These host investigations have not been rerun during publication and are not
requirements applied by the plugin installer. The upstream Mercurial URL returned
HTTP 418 to the publication link checker; retain the citation as historical
provenance, with its full node hash unverified. Debian's issue, the Pidgin issue
and the GStreamer documentation URLs responded successfully.
