# Persistent room history — 2026-11-01

Implementation: plugin base `fe078f29110a68f7ae326087ad2f8581d56130c3`, plus the working-tree files identified below (not a claimed committed revision). The pre-existing contact-alias regression edits in test-purple.c were preserved.

| File | SHA-256 of validated working-tree content |
| --- | --- |
| `src/meshcore.c` | `642c342b3cf1c6c6192f82b2e3aefb86b46a0a7e836b86ac455e01ffb5ce8ff0` |
| `src/meshcore.h` | `a3e1ff9dcd4dccc803d30177fc50d4e314c819b1c833c1189746187d7da48497` |
| `src/plugin.c` | `ade0222b86dda5ae39555d5327d3364cd145707de99636e8429336a8c5b80b55` |
| `tests/test-purple.c` | `a84d05322138755c0839768bb626a95331202bceb0b1aecb239832634e454daa` |

Upstream scope: MeshCore companion source `81dbae592ffad40b4212bc0b37e82b38da08f4bc` (protocol 14); libpurple 2.14.14 from Ubuntu source `1:2.14.14-1ubuntu3`, installed host library `1:2.14.14-1ubuntu3+meshcorefix1` as previously documented. Self-info contains the full 32-byte public key at offset 4; channel info contains the 16-byte secret at offset 34. No RF testing or hardware delivery claim.

## Identity and send validation

Conversation name = lowercase SHA-256 of the ASCII domain `pidgin-meshcore-room-v1` INCLUDING its terminating NUL, then the full 32-byte companion public key, then the 16-byte channel key. Fixed-length inputs exclude channel slot and label. Only the digest is persisted in room components and log paths; channel secret bytes are not retained or persisted. Normal libpurple account scoping still applies.

The random per-session UUID remains the join token, independent from the persistent `conversation` component. Imported buddy-list chats and room-list entries carry both; get_chat_name returns the persistent component for View Log, with the old UUID fallback only for legacy entries. Joined sessions still receive monotonically allocated chat IDs. Old IDs and old join tokens cannot authorize sends after reconnect. Existing core pre-send channel name/key/slot checks remain in force. An existing left window can be explicitly rejoined by libpurple under a fresh ID.

## Logging and validation

`make` and `make test`: pass, all 24 core regressions and headless libpurple integration. Tests use PTYs/socketpairs only. Integration exercises BOTH real HTML and text libpurple loggers, closes conversations to flush logs, and retrieves them with purple_log_get_logs/purple_log_read. The same key pair retains old messages across reconnect and slot/name changes. Changes to the last byte of either full key isolate messages. Duplicate labels with distinct keys remain separate, existing windows can rejoin, stale IDs remain rejected, and buddy-list get_chat_name agrees with the log identity. No mock logger or identity-string-only evidence.

Read-only host check: saved /purple/logging/log_chats is enabled (1), format html. libpurple defaults log_chats to TRUE and new chat conversations inherit it. No preferences changed and the plugin preserves logging controls. The integration asserts logging is active before writing messages. Persistent identity cannot recover messages from sessions in which logging was disabled, or files that were deleted.

## Legacy UUID investigation

Read-only metadata inventory: 16 UUID room directories under logs/chat (generic chat icon determines this protocol directory), 14 saved MeshCore chat entries, none with a persistent conversation component; 2 directory UUIDs match currently saved join tokens. Message bodies, account labels, channel labels and secrets were not copied into this evidence.

The old plugin generated UUIDs randomly and retained no UUID-to-companion-public-key/channel-key mapping. Standard HTML/text log headers use log->name (the UUID), time, account and protocol; setting a conversation title does not record a cryptographic channel binding. Matching a saved UUID can identify its current display label, but that label is neither unique nor durable and supplies no full companion/key identity. Slot, name, sender labels, timestamps and account device paths cannot establish the missing binding. Even the two saved-token matches do not justify assigning those histories to a cryptographic identity.

No logs were renamed, merged or deleted. A future explicit migration would need independent contemporaneous evidence binding an individual UUID to BOTH the full companion public key and exact channel-key identity; ambiguous entries must remain untouched. Existing UUID files remain available as legacy logs and are not silently attached to new conversations.
