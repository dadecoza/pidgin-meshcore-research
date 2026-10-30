#!/usr/bin/env python3
"""Actual Pidgin sound/quit regression using an isolated profile and loopback IRC.
Run under: dbus-run-session -- xvfb-run -a python3 test-sound-shutdown.py ...
No serial devices, external servers, real accounts, or RF are used.
"""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import wave

import dbus

NAME = 'im.pidgin.purple.PurpleService'
PATH = '/im/pidgin/purple/PurpleObject'
IFACE = 'im.pidgin.purple.PurpleInterface'


def run(binary, delay, expect_hang):
    with tempfile.TemporaryDirectory(prefix='pidgin-sound-quit-') as directory:
        root = Path(directory)
        sound = root / 'silent.wav'
        with wave.open(str(sound), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(b'\0\0' * 44100 * 30)
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(10)
        connected = threading.Event()
        deliver = threading.Event()
        errors = []

        def server():
            try:
                conn, _ = listener.accept()
                with conn:
                    conn.settimeout(10)
                    incoming = conn.makefile('rb')
                    nick = 'test'
                    user = False
                    while not user:
                        line = incoming.readline().decode('utf-8', errors='replace')
                        if not line:
                            raise RuntimeError('IRC client disconnected before login')
                        if line.startswith('NICK '):
                            nick = line.split()[1]
                        if line.startswith('USER '):
                            user = True
                    conn.sendall((f':localhost 001 {nick} :Welcome\r\n'
                                  f':localhost 376 {nick} :End of MOTD\r\n').encode())
                    connected.set()
                    if not deliver.wait(10):
                        raise RuntimeError('Test did not request a notification')
                    conn.sendall(f':sender!user@localhost PRIVMSG {nick} :sound shutdown test\r\n'.encode())
                    while conn.recv(4096):
                        pass
            except (OSError, RuntimeError) as error:
                errors.append(str(error))

        thread = threading.Thread(target=server, daemon=True)
        thread.start()
        log = open(root / 'pidgin.log', 'w')
        proc = subprocess.Popen([binary, '-m', '-n', '-c', str(root / 'profile')],
                                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            bus = dbus.SessionBus()
            deadline = time.monotonic() + 12
            while time.monotonic() < deadline and not bus.name_has_owner(NAME):
                if proc.poll() is not None:
                    raise RuntimeError('Pidgin exited during initialization')
                time.sleep(.05)
            if not bus.name_has_owner(NAME):
                raise RuntimeError('Pidgin D-Bus did not initialize')
            api = dbus.Interface(bus.get_object(NAME, PATH), IFACE)
            assert not api.PurpleAccountsGetAll(), 'Requires an isolated profile/session bus'
            api.PurplePrefsSetString('/pidgin/sound/method', 'automatic')
            api.PurplePrefsSetBool('/pidgin/sound/mute', False)
            api.PurplePrefsSetInt('/pidgin/sound/volume', 0)
            for kind in ('im_recv', 'first_im_recv'):
                api.PurplePrefsSetBool('/pidgin/sound/enabled/' + kind, True)
                api.PurplePrefsSetPath('/pidgin/sound/file/' + kind, str(sound))
            account = api.PurpleAccountNew('test@127.0.0.1', 'prpl-irc')
            api.PurpleAccountsAdd(account)
            api.PurpleAccountSetInt(account, 'port', listener.getsockname()[1])
            api.PurpleAccountSetEnabled(account, 'gtk-gaim', True)
            status = api.PurpleSavedstatusNew('', 2)
            api.PurpleSavedstatusActivate(status)
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline and not api.PurpleAccountIsConnected(account):
                time.sleep(.05)
            assert connected.is_set() and api.PurpleAccountIsConnected(account), errors
            deliver.set()
            deadline = time.monotonic() + 5
            playback_seen = False
            while time.monotonic() < deadline:
                for task in Path(f'/proc/{proc.pid}/task').glob('*/comm'):
                    try:
                        if 'wavparse' in task.read_text():
                            playback_seen = True
                    except FileNotFoundError:
                        pass
                if playback_seen:
                    break
                time.sleep(.005)
            assert playback_seen, 'Notification WAV playback never started'
            time.sleep(delay)
            start = time.monotonic()
            try:
                api.PurpleCoreQuit(timeout=1)
            except dbus.DBusException:
                pass  # A normal exit can close the bus before replying.
            try:
                result = proc.wait(timeout=3)
                elapsed = time.monotonic() - start
                assert not expect_hang, 'Baseline did not reproduce the hang'
                assert result == 0, f'Pidgin exited with {result}'
                print(f'PASS: active WAV notification; normal quit in {elapsed:.3f}s; delay={delay}', flush=True)
            except subprocess.TimeoutExpired:
                if not expect_hang:
                    raise RuntimeError('Pidgin hung while quitting with an active sound')
                print(f'REPRODUCED: WAV notification active; quit still blocked after {time.monotonic()-start:.1f}s', flush=True)
        except Exception:
            log.flush()
            print((root / 'pidgin.log').read_text()[-6000:], flush=True)
            raise
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=3)
            deliver.set()
            listener.close()
            thread.join(timeout=1)
            log.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pidgin', default='/usr/bin/pidgin')
    parser.add_argument('--expect-hang', action='store_true')
    parser.add_argument('--delay', type=float, default=0)
    args = parser.parse_args()
    run(args.pidgin, args.delay, args.expect_hang)
