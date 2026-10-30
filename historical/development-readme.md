# pidgin-meshcore

Archived pre-publication README, not maintained setup guidance. Some claims
reflect intermediate behavior. Use the [maintained plugin README](https://github.com/dadecoza/pidgin-meshcore)
and [revision ledger](../REVISIONS.md) for current scope and provenance.

A small Linux Pidgin 2/libpurple protocol plugin for ordinary text messaging
through a USB serial MeshCore companion. Native C and GLib; no sidecar or service.
This is a separate project from pidgin-meshtastic.

## Build and user-local installation

Tested on Ubuntu 26.04.1, Pidgin/libpurple **2.14.14**, GLib **2.88.0**, GCC 15.
Requires libpurple 2 headers, GLib >= 2.52 and OpenSSL libcrypto development headers; Pidgin 3 is unsupported. Other
Pidgin 2 releases have not been tested. No Python runtime dependency.

```sh
sudo apt install build-essential pkg-config libpurple-dev libglib2.0-dev libssl-dev pidgin
make
make test
make install                 # ~/.purple/plugins/pidgin-meshcore.so
# Restart Pidgin after installing/upgrading/removing the plugin.
make uninstall
```

For a custom Pidgin profile: `make install PLUGIN_DIR=/path/to/profile/plugins`.
`DESTDIR` is supported for staging. License: GPL-2.0-or-later.

## Companion and account setup

Use **MeshCore companion USB firmware v1.18.0 (protocol 14)** exposing the serial
companion protocol at **115200 baud, 8N1**. BLE-only companion firmware, repeaters,
room servers and console-only serial firmware are unsuitable. Unknown protocol
versions are rejected. See [the source review](../current/PROTOCOL.md) for exact revisions.
Configure contacts, channels and the radio with the official app first; close
other serial applications before enabling this account.

1. Ensure you can access the serial device: on Ubuntu, add your user with
   `sudo usermod -aG dialout "$USER"`, then log out and back in. Do not run Pidgin
   as root or make the device world writable.
2. Add a **MeshCore** account in Pidgin. The username is a local account label
   (for example `usb-radio`); it never changes the configured node name.
   There is no password or radio login. The connection/chat display uses the
   companion's existing name.
3. In Advanced options, enter the explicit serial path. Prefer a stable path
   under `/dev/serial/by-id/` rather than `/dev/ttyUSB0`.
4. Enable the account. Every connection downloads the companion's chat contacts
   and configured channels. Contacts appear in **MeshCore** and channels in
   **MeshCore channels** in the buddy list. Imported contacts initially have
   **Show When Offline** enabled so older contacts also remain visible. You can
   change this per buddy; your choice is preserved. Online means **heard within
   the last 24 hours**, as described below.
5. Double-click a contact for an ordinary IM, or a channel for a normal group
   chat. The usual **Buddies → Join a Chat → Room List** also lists the downloaded
   channels. Joining/leaving only opens/closes a local conversation. Incoming
   channel messages also open the normal chat window.

Automatically imported channel entries refresh on every reconnect, including
changed channel slots. Their session identities prevent sending to an old slot.
User-created saved/autojoin room entries remain separate; refresh or replace
those after reconnecting. Each account has its own connection and room state;
two accounts cannot open the same device. Use a different local label per account.

## Message behavior and limits

- Direct text: **160 UTF-8 bytes** maximum. Channel text: **160 minus the device
  name's UTF-8 byte length minus 2** (`name: `) bytes. These include firmware
  overhead; an oversized/empty/invalid UTF-8 message is rejected, never split or
  truncated. Pidgin formatting becomes plain text before checking the limit.
- Queued messages drain after initialization and on new-message notifications.
  Incoming text is escaped and uses Pidgin's normal logging and notification
  settings. No additional message database or radio debug log is created.
- Channel sends have **no acceptance notice**. If a matching forwarded packet
  is received, the conversation shows **Repeat heard.**
  once for that send. If none is heard, there is no feedback or automatic retry.
  A repeat is not recipient delivery. Actual send failures are still reported.
  Direct recipient ACKs show **Acknowledged.**; ACK timeouts and failures remain
  visible. If tracking cannot start, the notice is **ACK tracking unavailable.**
  Routine acceptance and room joins are quiet. An ACK is not a read receipt.
- Channel messages display `name: message` as a normal sender nickname and body.
  Senders are added to the room's participant list when they speak (up to 128
  distinct names per conversation); repeated messages do not duplicate entries.
  This is a list of observed names, not verified identities or live membership.
  Channel labels do not establish authenticated public-key identities.
  Channel packets have a channel hash and shared-key MAC, but **no sender public
  key or sender hash**. Anyone holding the channel key can claim another name,
  even a name matching a saved buddy. Such name matches do not update public-key
  buddy availability. Use direct messaging when contact identity matters.
  There is no typing indicator. Buddy presence follows the recent-heard rule below.
- Unknown or ambiguous incoming six-byte key prefixes are dropped with a normal
  warning. Ambiguous outgoing prefixes are rejected too, including collisions
  with non-chat contacts. New-contact adverts import the full identity immediately;
  pending direct sends are checked again before transmission in case a prefix
  collision appeared. Deleted-contact events force a safe reconnect. Reconnect
  manually to reload other name changes.
- Duplicate ACKs are suppressed by consuming a bounded pending record. RF packet
  deduplication belongs to the firmware. The serial queued-message format has no
  unique message ID, so text/timestamp deduplication would discard legitimate
  repeated messages; the plugin deliberately preserves those messages.

### Channel repeat feedback

Repeat detection uses the companion's raw receive notifications and matches the
exact encrypted packet fingerprint, including timestamp, node name, message and
channel. It requires a non-empty flood relay path and ignores duplicate echoes,
zero-hop packets, unrelated text and unsupported/malformed packet layouts. The
notice does not identify a particular repeater or update a buddy's presence.

Before sending, the plugin re-reads that channel to verify its name/key against
the connection snapshot and generate the expected ciphertext fingerprint. The
key is used transiently; it is not cached, persisted or logged. A changed channel
is rejected before transmission and requires reconnecting to refresh it.

Tracking is bounded to the most recent 32 accepted channel sends for five minutes.
Expiry is silent. Firmware omits raw receive records that exceed its 176-byte
serial-frame limit, so a long message or long relay path may be repeated over RF
without this client receiving enough information to report it. Silence therefore
provides no delivery conclusion. No channel/radio settings are changed.

### Recent-heard presence

A buddy is online when the companion has heard it within the last **24 hours**.
At connection, this uses the contact's receiver-side `lastmod` timestamp. A valid
live advert for a known full public key makes that buddy online immediately;
a new-contact advert imports it and marks it online immediately as well. Live
direct messages of all supported subtypes after the initial queue drain,
matched recipient ACKs, received path updates and received responses with an
unambiguous contact identity also restart the full 24-hour window. Bodies outside
the text-messaging scope are not displayed and no additional radio requests
are sent. A channel sender label never identifies a buddy.

This counts **all received traffic the companion safely attributes to a contact**,
not just adverts or messages displayed in Pidgin. However, encrypted traffic
between other nodes exposes only a **one-byte source hash** in the raw packet
log, not a full source public key. Those packets cannot reliably be attributed
to a contact, even if only one saved contact currently matches that byte; unknown
nodes can share it. Such traffic and unauthenticated channel names do not refresh
presence. Full coverage of that traffic would require additional trustworthy
source-identity information from the firmware/protocol.

Presence expires automatically 24 hours after the last observation. The status
text shows the elapsed time, for example **5 minutes ago** or **2 days, 5 hours,
32 minutes ago**, and refreshes every minute and on new activity. Very recent
activity says **Just now**; missing/invalid timestamps say **Last heard unknown**.
This is a recent-activity indicator,
not a guarantee that the recipient is currently reachable. Disconnecting makes
the account's buddies offline. Startup queued messages do not refresh presence
merely because an old message is downloaded. Zero or future contact timestamps
do not imply online; accurate host/companion clocks matter for the initial sync.
The plugin does not set either clock or change the node's configured name.

## Recovery and troubleshooting

USB loss and open errors retry after 1, 2, 4, 8, 16, then at most 30 seconds.
Disabling the account cancels retries immediately. There is no automatic resend:
queued unsent messages fail; an interrupted send reports an uncertain outcome.
A silent radio is checked with an idle device query about every 30 seconds.

A **command timeout (10 seconds without a reply)** or inconsistent protocol reply
stops the session and requires disabling/re-enabling the account. Untagged
responses cannot safely be assigned to another command after a timeout. ACK
waiting is separate and does not stop the session (firmware estimate, bounded to
1–300 seconds). A reboot that drops USB reconnects; a silent reboot/hang may
require this manual recovery. Initialization may need retrying if opening the
port resets the board before it can answer.

For “permission denied”, check group membership and device permissions. For a
busy port, disable other accounts/apps using it. For initialization failure,
check the USB firmware and baud rate, then reconnect. If channels or names change
in the official app, reconnect and refresh the room list. Do not use two apps on
the same port. Pidgin can still show the account as connected during a USB retry;
sends are rejected until initialization completes.

Memory and queues are bounded: 176-byte frames, <= 690 buffered input bytes,
4 KiB serial output, 64 queued commands plus one active command, 4096 contacts,
64 channel slots, 32 pending ACKs and 32 channel-repeat fingerprints per account. No channel secrets are retained,
persisted or logged; channel query responses necessarily contain secret bytes
transiently in transport memory. No configuration commands are sent.

Bluetooth/TCP, maps/GPS/telemetry, administration, room-server login/history,
configuration/key editing, flashing, file transfer and dashboards are out of scope.

## Validation

`make test` runs a real pseudo-terminal fake companion and a headless libpurple
integration test loading the built shared plugin. `make memcheck` runs the core
suite under Valgrind. See [test results and the hardware checklist](../validation/TESTING.md).
**Basic real-device USB operation is now verified**: account creation, connection,
69 imported contacts, room listing/joining and one authorized `#test` send accepted
by the companion. The node name was verified unchanged. Recipient/over-the-air
delivery remains unverified. See [hardware results](HARDWARE.md).

On Ubuntu 26.04, a pre-existing libpurple media-device bug can crash Pidgin during
account setup or while idle. The installed library on this machine has the
[upstream lifetime fix](../host-compat/README.md) backported. Pidgin also has a
[local shutdown fix](../host-compat/README.md#pidgin-shutdown-hang-fix) for a
reproduced GStreamer notification-sound hang during quit.
