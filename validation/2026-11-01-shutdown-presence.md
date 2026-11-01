# Presence sounds at shutdown — 2026-11-01

Plugin base `fe078f29110a68f7ae326087ad2f8581d56130c3` with the earlier persistent-history and room-label working-tree changes. This investigation changes only the close-time presence guard and adds signal-level libpurple regressions. Exact resulting files:

| File | SHA-256 |
| --- | --- |
| `src/plugin.c` | `4381bc3ffbca07f48f082fe4f588455d38b8237692d52ed3939ff1f41364d860` |
| `tests/test-purple.c` | `240b3228ff368010dd3595086e8ddc161a3e1de132c6e7aedb16642bc120dd92` |

Upstream source: Ubuntu Pidgin/libpurple `1:2.14.14-1ubuntu3`; installed libpurple `1:2.14.14-1ubuntu3+meshcorefix1`, GUI `1:2.14.14-1ubuntu3+meshcorefix2`. Protocol 14 PTY/socketpair tests follow MeshCore firmware source `81dbae592ffad40b4212bc0b37e82b38da08f4bc`. No RF or hardware testing. No private contact names, keys, logs or host preferences copied.

## Cause

libpurple core.c purple_core_quit calls purple_connections_disconnect_all. In connection.c _purple_connection_destroy invokes the protocol close callback while its connection is still connected. The plugin close_account sets closing=TRUE and calls clear_presence; that function previously announced offline status for each recently heard buddy through purple_prpl_got_user_status. This emits buddy-signed-off in blist.c purple_blist_update_buddy_status. Pidgin gtksound.c buddy_state_cb subscribes to that signal and requests PURPLE_SOUND_BUDDY_LEAVE. Quitting was therefore presented as a series of individual remote buddy departures.

libpurple then transitions the connection to disconnected and calls purple_blist_remove_account, which resets buddy presence and roster accounting without emitting those individual sign-off signals. The plugin's earlier announcements are redundant on intentional close.

## Change and evidence

clear_presence still cancels its timer and clears its per-account cache on every disconnect. It skips publishing individual offline statuses when Account.closing is true, leaving the normal libpurple disconnect cleanup to reset presence. Unexpected serial loss still marks the buddies offline immediately; ordinary 24-hour presence expiry is unchanged. No global sound preference changes or sound suppression hooks.

Added a real libpurple signal regression with recent-heard buddies. Before the fix, intentional account disable emitted FOUR buddy-signed-off events and failed the zero-events assertion (exit 134). After the fix, both intentional account disable and purple_connections_disconnect_all (the path used by core quit) emit zero such events while leaving buddies offline. Unexpected PTY closure still emits sign-off events and clears presence.

make test passes: all 24 core tests and expanded libpurple integration, including existing presence expiry and room/logging regressions. This verifies the exact signal that Pidgin maps to its leave sound; no claim of an acoustic recording or live-radio check. Installed the updated user-local plugin and compared it with the built binary; restarting Pidgin is needed to load the change.
