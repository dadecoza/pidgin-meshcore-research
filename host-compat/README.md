# Ubuntu 26.04 libpurple crash fix

Host-only investigations for Ubuntu Pidgin source `1:2.14.14-1ubuntu3`. These
patches are never applied by the plugin build/install. They have not been rerun
as part of publication. Plugin revision applicability and firmware independence
are recorded in [REVISIONS.md](../REVISIONS.md). No private profiles, packages or
crash dumps are published.

The user's Pidgin crash report on 2026-10-30 stopped in
`gst_device_get_display_name`, called from libpurple's media-device removal
callback. The unpatched GUI also crashed while idle before a MeshCore account
was connected. This is the device-lifetime use-after-free described in
[PIDGIN-18155](https://issues.imfreedom.org/issue/PIDGIN-18155/Pidgin-is-crashing-with-GStreamer-gstdevicegetdeviceclass-assertion-GSTISDEVICE-device-failed)
and [Debian #1135675](https://bugs.debian.org/1135675).

The attached patch backports the lifetime change from upstream commit
[`b0cd433f154a`](https://keep.imfreedom.org/pidgin/pidgin/rev/b0cd433f154a/): hold a
reference to the registered `GstDevice` and release it when its media element
is destroyed. It does not disable audio/video or change MeshCore's scope.
This fix belongs in libpurple, not in a radio protocol plugin.

On this machine, Ubuntu's `pidgin` source `1:2.14.14-1ubuntu3` was rebuilt with
this patch and local version `1:2.14.14-1ubuntu3+meshcorefix1`. The patched
`libpurple0t64` and matching `libpurple-dev` packages are installed. The GUI
successfully created the MeshCore account, connected to the real companion,
listed/joined #test, sent a test message and restarted normally afterward.
No special launcher, environment variable or disabled media provider is needed.
Other Pidgin warnings about missing canberra/Mesa devices are still emitted.

Local patched and original packages are retained in:
`~/.local/share/pidgin-meshcore/compat/`. A later distro package revision can
supersede the local fix normally; no package hold was set.

To reproduce the package build **outside this project directory**:

```sh
sudo apt-get build-dep pidgin
apt-get source pidgin
cd pidgin-2.14.14
patch -p1 < /path/to/pidgin-meshcore-research/host-compat/pidgin-2.14.14-gst-device-lifetime.patch
dch --local '+meshcorefix' 'Backport upstream GstDevice lifetime fix.'
dpkg-buildpackage -b -uc -us -j4
# Install the resulting libpurple0t64 and matching libpurple-dev .deb files.
```

To restore the original distro packages, quit Pidgin, install both original
packages below and restart it. This also restores the original crash defect:

```sh
sudo dpkg -i \
  ~/.local/share/pidgin-meshcore/compat/libpurple0t64_2.14.14-1ubuntu3_amd64.deb \
  ~/.local/share/pidgin-meshcore/compat/libpurple-dev_2.14.14-1ubuntu3_amd64.deb
```

## Pidgin shutdown hang fix

On 2026-10-30, the running Pidgin process was found already inside
`purple_core_quit`, blocked in this main-thread stack:

```
purple_sound_uninit
pidgin_sound_uninit -> gst_deinit
gst_task_cleanup_all -> g_thread_pool_free -> g_cond_wait
```

Another thread was still processing a notification WAV, through `wavparse`,
GStreamer pads and `gst_task_new`. The MeshCore account/serial connection had
already been closed. The main loop could not finish shutdown because global
GStreamer teardown waited on active streaming tasks.

This was reproduced **without MeshCore**, using an empty temporary Pidgin
profile, a private D-Bus session, Xvfb, a loopback IRC server and an actual silent
30-second notification WAV. The original executable remained blocked after the
four-second test timeout. The already-stuck user process required termination;
settings were backed up privately first.

[The shutdown patch](pidgin-2.14.14-gstreamer-shutdown.patch) removes the optional
process-global `gst_deinit()` call from the sound subsystem's uninitialization.
GStreamer is also shared by libpurple's media subsystem; sound teardown should
not globally deinitialize it while tasks are still active. GStreamer's own
[documentation](https://gstreamer.freedesktop.org/documentation/gstreamer/gst.html#gst_deinit)
states this call normally is not needed for an application terminating normally.
The process exit releases the remaining GStreamer resources. This is a locally
tested compatibility fix, distinct from the earlier upstream GstDevice patch.
Notification sounds remain enabled and no user sound preferences were changed.

Installed package: `pidgin 1:2.14.14-1ubuntu3+meshcorefix2`.
`libpurple0t64` and `libpurple-dev` remain at `+meshcorefix1`; they did not need
another change. The MeshCore plugin source was unchanged by this investigation.
The rebuilt and original Pidgin packages are in
`~/.local/share/pidgin-meshcore/compat/`; no package hold was set.

### Regression test

```sh
# Original executable: verify the known failure before applying the patch.
dbus-run-session -- xvfb-run -a python3 host-compat/test-sound-shutdown.py --expect-hang
# Fixed executable: require a normal exit while sound playback is active.
dbus-run-session -- xvfb-run -a python3 host-compat/test-sound-shutdown.py
```

The harness requires `python3-dbus`, `dbus-run-session`, Xvfb and installed
Pidgin IRC support. It creates only temporary test accounts/settings and a local
IRC connection; there is no radio access or external network traffic. The sound
volume is zero **in the test profile only**; WAV playback is still exercised.
It checks for a WAV streaming thread before quitting. A failed test terminates
only its own temporary Pidgin process.

Results: candidate exits in 0.398, 0.058 and 0.039 seconds at three playback
timings; installed executable exits in 0.034 seconds. The user's real profile
connected with 69 MeshCore contacts and quit normally in 0.235 seconds, without
forced termination. The application was then relaunched normally.

To reproduce the package, apply the shutdown patch to the same Ubuntu source
used above, use local package version `1:2.14.14-1ubuntu3+meshcorefix2`, rebuild
with `dpkg-buildpackage -b -uc -us -j4`, and install the resulting `pidgin` package.
The earlier libpurple fix can stay installed. [Recorded results](shutdown-results.txt).

To roll back only the shutdown fix, quit Pidgin and run:

```sh
sudo dpkg -i ~/.local/share/pidgin-meshcore/compat/pidgin_2.14.14-1ubuntu3_amd64.deb
```

That restores the original Pidgin executable, including its shutdown hang risk.
It leaves the earlier libpurple crash fix and the MeshCore plugin installed.
Private settings backups were excluded from this archive.
