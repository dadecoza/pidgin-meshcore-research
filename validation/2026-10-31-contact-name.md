# Missing single-character contact investigation

Plugin baseline: `fe078f29110a68f7ae326087ad2f8581d56130c3`, with a local
test-only change in `tests/test-purple.c` exercising a one-character alias.
Reviewed MeshCore source: `81dbae592ffad40b4212bc0b37e82b38da08f4bc`.
The flashed companion revision was not inspected.

Read-only inspection of the connected host Pidgin session via its libpurple
D-Bus interface found 69 buddies and no alias matching the reported name
(also checked with case folding and surrounding whitespace removed). Its saved
buddy list likewise had no exact matching alias. The user reports seeing the
contact in the official app. This does not establish whether both applications
refer to the same companion or contact snapshot.

`store_contact()` accepts one-character names, but only calls the buddy import
hook for `ADV_TYPE_CHAT` (1). Upstream defines repeater (2), room (3), and
sensor (4) separately. Contact type filtering is a possible explanation, not a
confirmed diagnosis for this contact. The device type/public-key prefix and
same-companion confirmation are still needed.

The headless libpurple PTY fixture now includes an offline chat contact with
the reported one-character alias and asserts its imported alias and
`show_offline` preference. `make test` passed all 24 core regressions and the
headless libpurple integration. `git diff --check` passed. Production code
was not changed or installed. No serial device was opened, no live RF tests
were performed, and simulator success does not prove over-the-air delivery.

## Authorized node contact inspection

The user subsequently authorized closing Pidgin and using `meshcore-cli` to
inspect stored node contacts. Pidgin exited through `PurpleCoreQuit`; its
process was confirmed absent before accessing the configured USB serial port.
Installed `meshcore-cli` version: 1.3.9. JSON mode was used; no CLI configuration
directory/device init scripts existed. Only `contact_info n` and `contacts`
were requested. No radio configuration or RF test commands were issued.

`contact_info n` returned `contact unknown`. A separate full contact read
returned 167 records: 69 chat clients, 83 repeaters, 3 room servers, and 12
sensors. Neither exact nor case-folded/whitespace-trimmed names matched the
reported one-character name. The 69 stored chat clients agree with the 69
Pidgin buddies. Thus this node's current stored contact list does not contain
the reported contact; contact type filtering does not explain this particular
absence. The official app may refer to another node, cached data, or a contact
not stored on this companion; these alternatives remain unverified. Exact
flashed firmware revision remains unknown. Pidgin was left closed as requested.

## Authorized live advert follow-up

The user identified the separate host attached to the missing node and
explicitly authorized stopping its MeshCore bot and sending an advert. The
bot's systemd service was stopped and verified inactive with MainPID 0. The
remote installed `meshcore` Python package was version 2.3.17 (no CLI installed).
The bot's open serial descriptor identified the companion port; reading self
info confirmed the reported one-character name before transmitting.

Exactly one `send_advert(flood=False)` command returned `EventType.OK`.
A subsequent local `meshcore-cli contact_info` read found the missing contact
as type 1 (chat client), with the same full public key as the remote self info.
Private host/device identifiers and the public key are omitted here. This is
real-device evidence of advert reception and storage at the local companion;
it does not test direct messaging, recipient ACKs, or Pidgin UI import after
reconnection. The prior absence was in the companion's stored contacts, not
one-character name handling or contact-type filtering. Why its earlier advert
was absent is not established. The remote bot remains stopped as requested,
and local Pidgin remains closed. No plugin production changes were made.
Exact flashed firmware revisions of both radios remain unrecorded.
