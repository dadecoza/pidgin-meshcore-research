# Design decisions and rejected approaches

Current conclusions apply to plugin `fe078f29110a68f7ae326087ad2f8581d56130c3`, with MeshCore firmware
`81dbae592ffad40b4212bc0b37e82b38da08f4bc` (companion-v1.18.0/protocol 14).
See [REVISIONS.md](../REVISIONS.md) for other exact source references.

| Decision | Reason and rejected alternative |
| --- | --- |
| Native C/GLib, separate serial/protocol/Pidgin layers | Avoid a Python sidecar, service supervision and a second event loop. Existing libraries informed the protocol review; BLE behavior was not copied into USB framing. |
| USB-only, explicit device path | No Bluetooth/TCP transports or discovery dashboards in this release. |
| One active command plus bounded queue | Most responses lack request IDs. Concurrent requests or reusing a session after command timeout could misattribute late replies. |
| No automatic resend after uncertain transmission | An interrupted write/reply may already have transmitted. Automatic retransmission can duplicate messages. |
| Full-key buddies, unique-prefix lookup only | Aliases and truncated hashes are unsafe identities. Duplicate names never merge contacts. |
| Stable companion/channel log identities; session UUIDs and fresh chat IDs for sends | Full companion public key and channel-key digest preserve history across reconnects and name/slot changes. Distinct keys isolate duplicate names. Session tokens and fresh IDs reject stale sends. Saved-chat aliases keep Pidgin title refresh readable. Legacy UUID logs are not guessed or merged. |
| Public-key evidence for 24-hour availability | Unique alias matches, channel names and one-byte raw source hashes cannot identify a contact safely. Presence is recent-heard activity, not guaranteed online reachability. |
| Observed channel speaker names | Channel text has no sender public key. Names are display labels; membership/authenticated sender lists would be invented. |
| Exact packet-fingerprint repeat matching | Reject sender-name/text-only guesses. Channel keys are used transiently during read-only verification rather than retained for a dashboard or persistent decrypting cache. |
| Short normal conversation notices | Direct ACKs and channel repeats are distinct; radio acceptance and silent repeat expiry do not add routine notices. No recipient-delivery claims for channels. |
| Reject oversized UTF-8 messages | Firmware silently truncates some group text. Splitting or truncating would hide data loss or imply extra sends. |
| Firmware-level RF duplicate suppression | Serial queue records have no stable packet ID. Text/timestamp suppression would drop legitimate repeats; plugin ACK/repeat state is bounded instead. |
| Generic `chat` icon | Pidgin 2.14.14's selector builds fixed installation-directory PNG paths. It offers no user-directory or in-memory protocol-image hook. An embedded PNG experiment was removed; no asset code/tooling remains. Extraction to an unread directory, installation-directory writes, path traversal and GTK interception were rejected. |
| Host fixes kept outside plugin | Media lifetime and GStreamer shutdown defects also reproduced without MeshCore. Patching host libraries during plugin installation would conflate scope and distro compatibility. |

Historical decision dates preceded Git initialization. No intermediate plugin
commit exists for the removed image experiment or earlier presence/notices;
the retained evidence is explicitly labeled rather than presented as current code.
