# Protocol/source review

Current implementation conclusions apply to plugin `fe078f29110a68f7ae326087ad2f8581d56130c3` and the
firmware source revision recorded in [REVISIONS.md](../REVISIONS.md). Historical
notes are retained where explicitly dated; hardware firmware build identity is
not inferred from its protocol number.

Reviewed 2026-10-30. All upstream checkouts were read-only under `/tmp`; no old
repository files were modified or copied into this implementation.

| Source | Exact revision | Use |
| --- | --- | --- |
| [MeshCore](https://github.com/meshcore-dev/MeshCore/tree/81dbae592ffad40b4212bc0b37e82b38da08f4bc) | `81dbae592ffad40b4212bc0b37e82b38da08f4bc`, tag `companion-v1.18.0`, protocol 14 | Firmware source is authoritative |
| [meshcore_py](https://github.com/meshcore-dev/meshcore_py/tree/ee987216b3364b64043766bda8b0037a90001c77) | `ee987216b3364b64043766bda8b0037a90001c77`, `v2.3.17-1-gee98721` | Independent serial framing/reader comparison |
| [pidgin-meshtastic](https://github.com/dadecoza/pidgin-meshtastic/tree/f311404cad11b3cabe5c354db175d1c411480fac) | `f311404cad11b3cabe5c354db175d1c411480fac` | libpurple integration patterns |

Firmware files inspected: `src/helpers/ArduinoSerialInterface.{h,cpp}`,
`BaseSerialInterface.h`, `BaseChatMesh.{h,cpp}`, `src/MeshCore.h`, `src/Mesh.cpp`,
`src/helpers/SimpleMeshTables.h`, and `examples/companion_radio/MyMesh.{h,cpp}`.
Also reviewed `docs/companion_protocol.md`; its BLE-focused introduction and
warning about inaccuracies make it insufficient as a USB specification.
Python files reviewed: `src/meshcore/serial_cx.py`, `reader.py`, `packets.py`.

## Verified wire facts

USB frames are `< length-low length-high payload` to the device and
`> length-low length-high payload` from it. Frame payload maximum is 176 bytes;
there is no BLE MTU/chunk/characteristic behavior in the serial implementation.
115200 baud and nonblocking raw 8N1 are used; hardware flow control is off.
Control line reset behavior varies by board and still needs hardware testing.

The plugin advertises app target 3 with `DEVICE_QUERY` (22), selecting V3 queued
message layouts, while explicitly requiring firmware protocol 14's inspected
self/contact layouts. Initialization then uses `APP_START` (1, seven reserved
bytes and app label), `GET_CONTACTS` (4), `GET_CHANNEL` (31) for every reported
slot, and `SYNC_NEXT_MESSAGE` (10) until `NO_MORE_MESSAGES` (10). No clock-setting,
advertising, configuration or channel-writing commands are issued.

Contacts (response 3) have the full key at offset 1, type at 33, 64 path bytes
at 36, and 32 name bytes at 100 (148 bytes total). All contact types are indexed
for collision detection; only chat contacts are imported. Channels (18) contain
slot at 1, 32 name bytes at 2, and 16 secret bytes at 34. Only name, a one-way key fingerprint and a random
session identity are retained. Slot IDs alone are never saved as room identities.
Account-owned random identities also expire when the same device reconnects.

Direct send (2) is type, attempt, uint32 LE timestamp, six key-prefix bytes,
then text (13 bytes of command overhead). Channel send (3) is type, slot,
timestamp, then text (7 bytes overhead). `BaseChatMesh.h` defines 160 text bytes;
`sendGroupMessage` prepends `sender_name + ": "` and silently truncates if too
long. The plugin rejects that case before sending. It uses attempt zero and
monotonically increasing per-account timestamps to distinguish repeated sends.

Direct `SENT` (6) is exactly 10 bytes: code, flood flag, four-byte expected ACK,
and uint32 LE estimated ACK timeout in milliseconds. This reports acceptance,
not delivery. `SEND_CONFIRMED` (0x82) is nine bytes: code, ACK hash, trip time.
Group sends return generic OK (0), without recipient ACKs. Generic errors (1)
are associated only with the single active command. Async push events never
complete commands. Duplicate ACKs consume no further state or notifications;
ambiguous ACK hashes are never attributed to a guessed recipient.

V3 direct queued text (16) has six key-prefix bytes at 4, path at 10, type at
11, timestamp at 12 and text at 16. Group text (17) has slot at 4, path at 5,
type at 6, timestamp at 7 and text at 11. Only plain text (type 0) is displayed;
CLI and room-server signed/history formats are excluded. New-message push 0x83
requests a queue drain, including notifications received during another command.
Unknown async codes are ignored; invalid lengths and unexpected command replies
stop the session. Existing-contact adverts (0x80) carry a full 32-byte key and
refresh that contact immediately. New-contact adverts (0x8A) carry the complete
contact record and are imported immediately. Every queued direct send is
rechecked for prefix ambiguity when dispatched, covering collisions introduced
by a new advert. Deleted-contact pushes force reconnect. Other name changes
reload on reconnect; no identity is guessed from an advertisement prefix.

Firmware `Mesh.cpp` and `SimpleMeshTables.h` already implement bounded packet
hash duplicate suppression. Serial queue records lack those packet hashes. An
additional text/timestamp cache here would conflate legitimate repeated messages;
therefore only ACK duplicates are suppressed at the plugin layer.

## Architecture and tradeoffs

- `src/serial.c`: nonblocking descriptor, advisory exclusive lock by device inode,
  raw termios, bounded framing and partial output, GLib fd sources.
- `src/meshcore.c`: one active command, bounded FIFO, initialization, contact and
  channel snapshots, queued-message parsing, ACK tracking and timers.
- `src/plugin.c`: per-account lifecycle/backoff, buddies, room list, normal
  libpurple conversations and local room joins. GLib sources use Pidgin's GLib
  main loop, with no worker or blocking serial calls.

Native C avoids sidecar process supervision, IPC, deployment dependencies and a
second asynchronous lifecycle. The old project's per-account connection state,
libpurple I/O integration, `serv_got_im`/chat dispatch and plugin registration
were useful patterns. Its Meshtastic protobuf/configuration/routing code is not
applicable to MeshCore. Responses without IDs here require a strict single
command state machine instead of multiple loosely assigned callback slots.

Timeout recovery deliberately fails closed: all queued operations are canceled,
the fd and sources close, and no new command can consume the late response in
that session. Re-enable to make a fresh connection. Ordinary transport loss uses
bounded automatic reconnect, clears every channel identity and never resends
uncertain transmissions. Full contacts are loaded on reconnect, including alias
changes. Removed buddies remain in Pidgin but cannot be sent to unless present
in the current device snapshot. Unknown incoming prefixes generate a warning.

The initial release supports the reviewed protocol revision only. This is a
source-verified implementation; basic USB operation has subsequently been
checked on the user's companion as recorded in [hardware observations](../historical/HARDWARE.md).

## Recent-heard presence (user-requested policy)

The contact record's uint32 LE `lastmod` at offset 144 is the companion-local
last-heard/modified time; `last_advert_timestamp` at 132 is the sender-provided
advert timestamp. `BaseChatMesh.cpp` updates `lastmod` on received adverts,
received text and contact path reception. It can also reflect a contact edit,
so the on-connect indication depends on the companion's stored timestamps and
clock. The plugin uses `lastmod` for the initial 24-hour presence classification;
zero/future timestamps are excluded.

Live adverts and unambiguous matched ACKs use the host receipt time. Plain direct
messages received after the initial queue drain also count as live activity;
startup queued records do not create fresh presence. A per-account, bounded
full-key timestamp table and one timer expire statuses at the earliest deadline.
The timer is canceled and statuses cleared on disconnect/unload. Group sender
labels and radio send acceptance never identify a recently heard buddy.

### Broader received-traffic policy

Receive-path updates (0x81) contain a full public key and reset activity immediately.
Login success/failure (0x85/0x86), status responses (0x87), telemetry responses
(0x8B), and discovery responses (0x8D) expose six-byte contact prefixes after
firmware processing. These prefixes are resolved uniquely across all contact
types before updating activity; discovery path lengths are checked. Only identity
metadata is used, without administration requests or payload UIs. All supported
queued direct-text subtypes (plain, CLI data, signed plain, CLI command) update
live presence after the initial drain, while only plain text is displayed.

`src/Packet.h` defines payload version 1 as one-byte source/destination hashes.
`src/Mesh.cpp` reads those two bytes for REQ, RESPONSE, TXT_MSG and PATH, and
attempts contact decryption only when the destination hash matches the companion.
Consequently overheard encrypted traffic for another destination does not
supply an authenticated source public key. The raw-log event (0x88) exposes those
same packet bytes, not a resolved identity; using a matching first key byte
would misattribute traffic from unknown/colliding nodes. Raw/custom packets,
untagged binary responses and channel sender names are intentionally not guessed.
This is a firmware information limit, not a receive-address filter in the plugin.

## Channel sender presentation

`BaseChatMesh::sendGroupMessage` constructs timestamp, text type and
`sender_name + ": " + text`; group encryption uses the channel secret. `Mesh.cpp`
parses a channel hash and MAC/encrypted data for group text, not a sender public
key/hash. The serial V3 response similarly contains slot/path/type/time/text.
Holding the channel key permits claiming another sender name. A buddy alias
match cannot authenticate that channel sender or justify public-key presence.

The plugin parses the first `: ` delimiter within the firmware's 32-byte name
limit, displays the claimed name via libpurple's chat alias API and escapes the
body. Missing/malformed labels preserve the complete message under Unknown sender.
Room participant entries represent observed names, bounded to 128 and cleared
by ordinary conversation rejoin; they are not live membership assertions.
Incoming channel names use a separate internal namespace longer than any valid
node name, so a remote claim of our own nickname cannot become an outgoing echo
or collide with a full-key buddy. Local senders enter the list when they send.
Unverified identity semantics are documented here rather than announced on each
join. Sender aliases replace the generic "channel (unverified sender)" nickname.

## Last-heard display

The buddy status text formats the cached observation time as elapsed days, hours
and minutes, including older offline contacts. Zero/future values are unknown;
activity less than one minute old shows Just now. The existing per-account timer
also refreshes the buddy-list labels every minute, while retaining exact nearest
presence-expiry scheduling. New activity redraws the label immediately. There
is no extra radio query, configuration command or per-buddy timer.

## Outgoing channel repeat tracking

The read-only comparison includes MeshCore Open revision
[`ac28dac575d591976d848a34f66a1d7a44b676dc`](https://github.com/zjs81/meshcore-open/tree/ac28dac575d591976d848a34f66a1d7a44b676dc),
especially `_handleLogRxData` and channel repeat matching in
`lib/connector/meshcore_connector.dart`. It processes raw RX group packets,
decrypts them using cached channel keys, and correlates repeats with channel
history. The official companion JavaScript library was also reviewed at
[`26193c059fcd1d0524f1ad5b19fd88287ecc5c61`](https://github.com/meshcore-dev/meshcore.js/tree/26193c059fcd1d0524f1ad5b19fd88287ecc5c61).
The closed native official app was not source-audited; its documented repeat
feedback is the behavior being reproduced. No code was copied.

This implementation avoids retaining channel secrets or relying on sender-name
heuristics. Each channel send is a serialized two-step transaction: GET_CHANNEL
(31), validate the slot/name and one-way key fingerprint, then send the original
channel text command. The transient GET_CHANNEL key is used by `src/repeat.c`
to generate the expected ciphertext and packet fingerprint; no key survives in
pending state. Cached metadata consists of one-way key fingerprints and exact
packet fingerprints only. AES-128-ECB comes from OpenSSL EVP; zero-padding,
HMAC-SHA256 truncated to two bytes, 16-byte-key channel SHA256 prefix and plain
message construction match the reviewed `Utils.cpp`, `BaseChatMesh.cpp` and
`Mesh.cpp`. SHA256 hashes type byte 5 plus the full channel/MAC/ciphertext payload,
following `Packet::calculatePacketHash`, with all 32 digest bytes retained for
local correlation. Mutable routing/path bytes are excluded.

`Dispatcher::checkRecv` calls `logRxRaw` before deduplication. Companion event
0x88 is code/SNR/RSSI followed by raw packet bytes. The parser supports payload
version 1, normal and transport-scoped flood routing, path hash widths 1–3 and
path data up to 64 bytes. Only a non-empty relay path and an exact immutable
payload match count. No relay public-key identity is inferred from path hashes.

Generic OK for a channel send is silent. A matching repeat after OK produces
one normal conversation notice; a match arriving before OK is deferred until
acceptance. Error/rejection discards that early observation. Duplicate copies
produce no extra notice. Up to 32 accepted-send fingerprints survive for five
minutes, expire silently, and clear on disconnect. There is no retransmission or
no-repeat timeout message. The test build shortens only this tracking lifetime
to one second for the expiry test; production remains five minutes.

`MyMesh::logRxRaw` drops packets when raw length + 3 exceeds 176, even if RF
reception succeeded. Hence some long messages or long paths cannot produce a
serial repeat observation. A repeat notice proves an overheard forwarded copy,
not recipient acknowledgment/delivery, repeater identity or buddy presence.

## Concise conversation notices

Routine radio acceptance and local room joins are silent. A matched recipient
ACK shows `Acknowledged.`; a matched channel repeat shows `Repeat heard.`.
These remain distinct outcomes. Direct messages that cannot start ACK tracking
show `ACK tracking unavailable.`; timeouts and disconnects retain concise failure
notices that preserve whether a send was unsent or its outcome/delivery unknown.
No extra radio traffic or retry behavior is introduced by this wording change.

## Review regressions (2026-10-30)

Queued channel datagrams (0x1B) use a nine-byte header followed by exactly the
one-byte declared data length: SNR, two reserved bytes, slot, encoded path,
little-endian data type and length. Validate slot/path/length, discard unsupported
binary content, and continue SYNC_NEXT_MESSAGE. No binary sender label updates
presence. Layout verified against the pinned firmware's MyMesh::onChannelDataRecv.

Pidgin's internal chat name is the session-scoped channel identity; the channel
name is only the readable title. Each opened conversation receives a fresh chat
ID, independent of its radio slot. Incoming messages, notices and observed users
resolve the current identity; stale windows cannot send or leave a replacement
conversation. Reconnecting intentionally creates a separate conversation/history.

Serial HUP/error handling drains successfully read bytes before reporting loss.
Reads are bounded to eight 512-byte chunks per GLib dispatch and continue on the
next dispatch if more final data remains. Write errors also drain input first;
new output watches are suppressed during that drain. Truncated final frames are
not delivered, while preceding complete messages and ACKs are processed normally.
