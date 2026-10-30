# Real-device validation — 2026-10-30

Historical observations, not a certification of the current plugin. Exact
pre-Git plugin commits and the flashed firmware commit were not recorded.
See [revision limits](../REVISIONS.md). Later statements supersede earlier ones,
including presence policy, notices and the separately fixed host shutdown hang.

Historical testing used an explicitly authorized USB companion. Device identity
has been removed from the public record:

`/dev/serial/by-id/<companion>`

Live messages were authorized only in `#test`. Exactly one test message was
submitted there through the normal Pidgin group-chat send path:

> [Explicit RF test text omitted; no private conversation retained.]

## Observed results

- The real USB companion reports protocol 14 and 40 channel slots.
- The actual Pidgin GUI created a MeshCore account with local label
  `usb-radio` (example label), connected to that device and imported 69 chat contacts.
- Pidgin's normal room list displayed `#test`; joining opened its normal chat.
- The single test send produced the normal conversation notice:
  “Companion accepted channel transmission; recipient delivery is unknown.”
- The configured node name was read before account creation, compared with the
  connected display name, then read again directly from the companion after
  closing Pidgin. It matched throughout. The account label remained
  `usb-radio` (example label); no set-name or other radio configuration commands were used.
- Pidgin was restarted normally against the installed fixed libpurple packages,
  reconnected successfully and was left running with the account enabled.

The local account label is never sent as a node name. The plugin now reads the
existing node name for the connection display name and outgoing conversation
labels. Automated PTY tests verify that a different local label does not cause
a set-name command and that the outgoing chat display uses the companion name.

The application crash encountered during account setup was traced to an
existing libpurple GStreamer device-lifetime bug; see [the local fix](../host-compat/README.md).

## Still pending

The send acceptance verifies the USB companion command path; no receiving radio
was observed, so **recipient/over-the-air delivery remains unverified**. No
direct RF test was sent. Real-device recipient ACKs/timeouts, queued receive,
Unicode boundaries, unplug/replug, reboot, permission failures and shutdown
stress remain hardware checklist items in [TESTING.md](../validation/TESTING.md). These paths
have simulator coverage where documented there.

## Automatic buddy-list import follow-up

On connection and a second real-device reconnect, the updated plugin imported
69 contacts and 13 configured channels (from the device's 40 available slots).
At that historical checkpoint, contacts were shown without online presence; configured channels are
added to the normal **MeshCore channels** buddy-list group. Reconnect replaced
the imported channel identities without duplicating the 13 entries. No RF
messages were sent during this follow-up check.

## Recent-heard presence follow-up

The user requested a 24-hour recent-heard online policy. After installing the
update and connecting normally, 4 of the 69 real-device buddies met that window;
65 remained offline. No RF messages were sent for this change. Immediate
existing/new advert updates and expiry were validated with the PTY companion,
including a near-expiry timestamp rather than waiting a full day. No live
advert receipt is claimed as part of this hardware check.

## Broader activity follow-up

The broader identity-bearing activity handler was installed and Pidgin
reconnected to the real device with 69 buddies. No RF messages were sent. The
new event-family handlers and deadline renewal were verified using PTYs, not
claimed as observed live RF events. Encrypted packets addressed to other nodes
only expose source hashes, so they cannot safely identify a buddy; see
[the protocol limitation](../current/PROTOCOL.md#broader-received-traffic-policy).

## Channel sender display follow-up

A historical screenshot showed a channel reply with a claimed sender name in
the body, displayed under a generic unverified sender and with an empty room
participant list. The screenshot and original sender label are not published. The plugin now displays the parsed nickname and tracks
observed speakers. The user selected public-key evidence for buddy availability,
so matching channel names do not mark a contact online. This behavior, Unicode
names, escaping, participant deduplication, and own-nickname impersonation
handling passed the PTY/libpurple integration test and Valgrind error checks.
The plugin was installed and the real account reconnected with 69 contacts;
no additional RF test messages were sent.

During restart, the previous Pidgin process hung in `gst_deinit` /
`gst_task_cleanup_all` / `g_thread_pool_free` after entering `purple_core_quit`.
It did not respond to SIGTERM and was terminated with SIGKILL. The new instance
connected normally. This separate GStreamer shutdown issue remains a host
application limitation; clean PTY/plugin shutdown does not certify Pidgin's
audio/video subsystem shutdown.

## Shutdown hang investigation and resolution

A later investigation reproduced the GStreamer shutdown hang in a temporary
profile with a local IRC account and an active notification sound, without
MeshCore. A local Pidgin sound-shutdown compatibility patch removed the blocking
optional global teardown call. Three candidate playback/quit checks and one
installed-binary check exited normally. The user's real profile then connected
with 69 contacts and quit in 0.235 seconds without forced termination. Pidgin
was relaunched normally afterward. No RF messages were sent. See
[the investigation, patch, test and rollback instructions](../host-compat/README.md#pidgin-shutdown-hang-fix).

## Channel repeat feedback follow-up

The update removes routine channel acceptance notices and reports only a matching
overheard repeat. The user previously authorized RF tests in `#test`; exactly
one short message was submitted through the normal Pidgin chat-send path:

> [Explicit RF test text omitted; no private conversation retained.]

The actual conversation displayed **Heard a repeat of your channel message.**
after about 3.98 seconds. The previous acceptance notice did not appear.
Only one repeat notice appeared for the test send. This verifies a matching
forwarded packet was heard over RF; it does not establish recipient delivery
or authenticate a particular repeater. Simulator tests cover absent repeats,
silent expiry, malformed/unrelated raw packets, early repeats, duplicates,
identical text at different timestamps and channel-key changes. No repeat-related
radio configuration or automatic retransmission was used. Pidgin was left running
and connected.

## Review fix installation (2026-10-30)

Updated plugin installed locally; Pidgin exited cleanly, restarted and connected
to the authorized USB companion, importing 69 buddies. No RF messages were sent.
The three reported regressions were exercised in automated companion/transport
fixtures; hardware reproduction of these edge cases remains pending.

## Structured historical repeat observation

Moved from the mixed development test log to keep RF evidence separate.
This is the same single repeat test described above, not an additional send.
Plugin source was unversioned; flashed firmware reported protocol 14, exact
build unknown. No message body, sender or channel secret is retained.

```json
{"repeat_observed": true, "seconds": 3.98, "acceptance_notice_absent": true, "messages_sent": 1}
```
