# Validation and hardware checklist

Coverage describes plugin `fe078f29110a68f7ae326087ad2f8581d56130c3` against the firmware reference in
[REVISIONS.md](../REVISIONS.md). The dated 19-test results below are an earlier
checkpoint; current 24-test results are in [publication validation](PUBLICATION.md).

Environment: Ubuntu 26.04.1 LTS x86-64, GCC 15.2.0, Pidgin/libpurple 2.14.14,
GLib 2.88.0, Valgrind 3.26.0. The real system development headers and libraries
are used; there are no fake libpurple headers. Run from the maintained plugin checkout root:

```sh
make test
make memcheck
# Optional: exercise libpurple and the shared plugin under Valgrind too.
valgrind --error-exitcode=1 --leak-check=no ./tests/test-purple
```

The C fake companion is in `tests/test-core.c` and `tests/test-purple.c`. It uses
`openpty`, writes real framed serial responses and verifies outgoing commands.
Final-data/hangup tests substitute a nonblocking socketpair for the serial fd
while retaining the real GLib read callback: Linux PTYs can discard unread data
on master closure, whereas socketpairs retain buffered bytes with HUP.
No attached radio is opened by tests. No test issues RF transmissions.

## Automated coverage

| Test | Checks |
| --- | --- |
| core/queued-datagram | Fragmented binary channel datagram and empty datagram skipped; following ordinary text delivered and queue drained |
| core/malformed-datagram | Mismatched declared binary length rejected safely |
| core/final-ack-hangup | Final buffered ACK processed before disconnect; no false ACK cancellation |
| core/final-message-hangup | Final queued text delivered before disconnect, including next-sync scheduling during drain |
| serial/final-frames-hangup | 1,100 complete frames plus incomplete tail followed immediately by closure; bounded multi-dispatch drain and one error |
| core/messaging | Query/app/contact/channel initialization; duplicate aliases; exact byte offsets; direct/group send; ACK and duplicate ACK; unknown async event; queue notification and draining; repeated incoming text preserved; 160/161-byte boundary; multibyte Unicode rejection; channel prefix overhead; ACK timeout; close/reopen and fresh channel identities |
| core/ambiguous | Two full keys sharing six bytes stay separate; outgoing send rejected; incoming prefix never guessed |
| core/malformed | Oversized serial length closes safely |
| core/unplug | Master PTY closes; transport loss reported as retryable |
| core/timeout-late | Two sends queued; first reply withheld; timeout closes session; second canceled; late acceptance cannot complete it |
| core/busy | A second account/core cannot open the locked device |
| core/unsupported | Unknown firmware protocol rejected |
| core/queue-bound | One active plus 64 queued commands; excess rejected; shutdown cancels all |
| core/malformed-record | Truncated self response fails initialization safely |
| core/contact-change | Live contact import introduces a prefix collision while a send is pending; the queued ambiguous send is canceled without reconnect or retransmission |
| core/received-traffic-presence | Full-key path events, all identity-bearing response events, all text subtypes update activity; truncated/unknown identities and raw packet hash guesses do not |
| core/ambiguous-traffic-presence | Ambiguous six-byte prefixes cannot update a buddy; a full-key event can still identify it |
| core/ack-tracking-unavailable | Short exceptional notice retained when no ACK can be tracked; an untracked ACK cannot become a false confirmation |
| core/stale-initial-reply | Prior OK/SENT responses cannot establish a fresh session |
| serial/partial-coalesced | Forced 2-byte writes and EAGAIN via linker wrapper; bounded 4 KiB output; exact complete output; leading noise and multiple frames in one read; source cleanup |
| repeat/crypto-vectors | Independent OpenSSL/Python vectors across AES block boundaries; exact packet fingerprint; scoped floods and 1/2/3-byte paths; size rejection |
| repeat/feedback | Silent acceptance; malformed/unrelated/zero-hop/direct packets ignored; one matching repeat notice; duplicate suppression; identical texts with distinct timestamps; early repeat deferred until acceptance |
| repeat/silent-expiry | No notice when no repeat arrives; expired repeat ignored; disconnect remains silent |
| repeat/channel-key-change | Fresh read-only channel verification rejects a changed key before transmission |
| headless libpurple | Load actual shared plugin; account login; buddies with duplicate names; zero/old/future last-heard timestamps; relative last-heard labels (just now, minutes, days/hours/minutes, unknown); recent contact initially online; automatic 24-hour expiry using near-deadline fixtures; new path traffic resets the window and keeps a refreshed buddy online past its former deadline; immediate known/new advert presence; malformed advert ignored; actual room-list join dispatch; normal IM/group callbacks; silent channel acceptance after read-only channel verification; formatting removal; escaped incoming conversation history; unplug/replug using stable symlink and replacement PTY; alias rename; changed channel slot; stale room rejection; retry cancellation on account disable; plugin unload; automatic channel buddy-list entries and refreshed identities; preservation of user-created chats and per-buddy offline visibility preferences; channel sender parsing/escaping, Unicode names, automatic observed participants without duplicates, malformed labels, remote claims of our own nickname remain incoming, and matching buddy names do not fabricate public-key presence; duplicate channel labels with distinct keys/slots get separate conversation identities, readable titles, histories and reply targets; reconnect retains separate old windows and rejects stale chat IDs |

Fragmented headers/payloads are exercised byte by byte during initialization and
incoming direct messaging. Coalescing is tested separately in the serial layer.
Unsent and uncertain sends are distinguished; no automatic retransmissions occur.

## Results (2026-10-30)

- Historical checkpoint: build, 19 automated core/serial PTY tests and the headless libpurple integration
  test pass. [Captured output](../historical/test-results.txt) records the final run.
- Core Valgrind: zero memory errors, zero definitely/indirectly/possibly lost
  bytes. GLib has process-global reachable allocations at exit.
- Headless libpurple Valgrind: zero reported memory errors with leak checking
  disabled. System-loaded media plugins produce Mesa/camera probing and fd
  warnings; this run does not certify libpurple/system-plugin leak freedom.
- GCC static analysis compilation: no diagnostics in project sources.
- User-local install/uninstall rules tested with `DESTDIR` staging, without
  changing the active user's Pidgin plugin installation.

These tests validate host behavior against the reviewed wire format. They do
**not** prove serial electrical compatibility, board reset timing, actual radio
acceptance, ACK timing or over-the-air delivery.

## Hardware results and remaining checklist

The initial simulator-only run left both serial devices untouched. In a later
user-authorized run, the CP2102 device was confirmed as a protocol-14 companion.
Actual Pidgin account creation, 69 imported contacts, room listing/joining and
one accepted `#test` send passed. The configured node name remained unchanged.
See [the hardware record](../historical/HARDWARE.md) for exact scope and remaining gaps.

Historical authorization applied only to the original session. Obtain explicit
permission and an agreed test channel before any new live RF test.

1. Identify board and USB companion firmware (v1.18.0/protocol 14). Confirm
   permissions, 115200 serial behavior and whether opening the port resets it.
2. Connect without sending: compare full keys, duplicate aliases, own name byte
   length and channel names with the official app. Confirm no configuration
   changes and no channel secrets in Pidgin profile/logs.
3. With RF permission, send one direct message each way. Observe acceptance,
   recipient ACK and missing-ACK timeout; confirm there are no read receipts.
   Test a 160-byte message, multibyte Unicode and an oversized rejection.
4. Join/leave an existing configured channel and confirm settings/keys stay
   unchanged. With permission, exchange one channel message, verify plain text,
   unverified sender labeling, group byte limit and no recipient-delivery claim.
5. Receive queued direct/channel messages after reconnect and while a chat is
   closed. Confirm Pidgin's normal logs and notification preferences apply.
6. Unplug during idle and during a send; replug through by-id. Confirm bounded
   recovery and no automatic resend. Reboot the radio; test both a disappearing
   USB device and a silent serial reset/hang with manual timeout recovery.
7. Use the official app while disconnected to change contact aliases/channel
   slots. Reconnect; verify full-key identity, new aliases and rejection of old
   room entries. Verify two plugin accounts cannot open the same device.
8. Disable the account during retries and exit Pidgin during an ACK wait. Repeat
   under Valgrind where practical; check for fd/timer leaks and shutdown errors.
