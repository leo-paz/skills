#!/usr/bin/env python3
"""Read-only Desktop diagnostic snapshot. Never restarts or repairs the host."""
import argparse
import base64
import datetime
import json
import os
from pathlib import Path
import signal
import socket
import subprocess


def run(argv, seconds):
    try:
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
    except OSError as e:
        return {'ok': False, 'error': str(e)}
    try:
        out, err = p.communicate(timeout=seconds)
        return {'ok': p.returncode == 0, 'exit_code': p.returncode,
                'stdout': out, 'stderr': err}
    except subprocess.TimeoutExpired:
        # Only this helper's local client process group; no remote process killing.
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        return {'ok': False, 'timeout_seconds': seconds, 'stdout': out, 'stderr': err}


def tcp_probe(host, port, banner=False):
    try:
        with socket.create_connection((host, port), timeout=4) as sock:
            result = {'connected': True}
            if banner:
                sock.settimeout(4)
                try:
                    data = sock.recv(256)
                    result['banner'] = data.decode('ascii', errors='replace')
                    result['ssh_banner'] = data.startswith(b'SSH-')
                except OSError as e:
                    result['banner_error'] = str(e)
            return result
    except OSError as e:
        return {'connected': False, 'error': str(e)}


LINUX = r'''date -Is
hostname
uptime
free -h
cat /proc/pressure/memory /proc/pressure/io
systemctl is-active ssh
systemctl --failed --no-pager
ps -eo pid,ppid,comm,rss --sort=-rss | head -12
systemctl show user-1000.slice -p MemoryHigh -p MemoryMax -p MemorySwapMax
if command -v docker >/dev/null; then timeout 8 docker ps --format '{{.Names}} {{.Status}}'; fi
'''
WINDOWS = r'''$ProgressPreference='SilentlyContinue'
Get-Date
Get-CimInstance Win32_OperatingSystem | Select LastBootUpTime,FreePhysicalMemory,TotalVisibleMemorySize | Format-List
Get-WinEvent -FilterHashtable @{LogName='System';Id=1074,6008,41,6005,6006;StartTime=(Get-Date).AddDays(-2)} -MaxEvents 12 | Select TimeCreated,Id,ProviderName,Message | Format-List
Get-CimInstance Win32_StartupCommand | Where-Object Name -eq 'CoreDevWSLKeepAlive' | Select Name,Command,Location | Format-List
Get-Service | Where-Object {$_.Name -match 'wsl|ssh|tailscale|sunshine'} | Select Name,Status,StartType | Format-Table
& 'C:\Program Files\Tailscale\tailscale.exe' serve status
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='desktop', help='Existing SSH alias')
    parser.add_argument('--ip', default='100.102.149.62', help='Verified Tailscale IP')
    parser.add_argument('--windows', action='store_true', help='Include Windows boot/startup evidence if SSH works')
    parser.add_argument('--output', type=Path, help='Save JSON snapshot with owner-only permissions')
    args = parser.parse_args()
    if args.host.startswith('-'):
        parser.error('host must be an SSH alias, not an option')
    report = {'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'host': args.host, 'ip': args.ip}
    ts = run(['tailscale', 'status', '--json'], 8)
    if ts.get('ok'):
        try:
            state = json.loads(ts['stdout'])
            report['tailscale'] = {'backend': state.get('BackendState'), 'health': state.get('Health'),
                'matching_peers': [{k: peer.get(k) for k in ('HostName', 'Online', 'LastSeen', 'TailscaleIPs')}
                    for peer in state.get('Peer', {}).values() if args.ip in peer.get('TailscaleIPs', [])]}
        except (ValueError, TypeError) as e:
            report['tailscale'] = {'parse_error': str(e)}
    else:
        report['tailscale'] = ts
    report['ssh_tcp'] = tcp_probe(args.ip, 22, banner=True)
    report['moonlight_tcp'] = tcp_probe(args.ip, 47989)
    ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
           '-o', 'ConnectionAttempts=1', '-o', 'ServerAliveInterval=4',
           '-o', 'ServerAliveCountMax=1', args.host]
    # Shell startup and remote execution need a deadline beyond ConnectTimeout.
    report['ssh_command'] = run(ssh + ['hostname'], 15)
    if report['ssh_command'].get('ok'):
        report['linux'] = run(ssh + [LINUX], 20)
        if args.windows:
            encoded = base64.b64encode(WINDOWS.encode('utf-16le')).decode('ascii')
            report['windows'] = run(ssh + [
                '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe '
                '-NoProfile -NonInteractive -EncodedCommand ' + encoded], 30)
    data = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(data)
        print(f'Saved {args.output.resolve()}')
        print('SSH command: ' + ('passed' if report['ssh_command'].get('ok') else 'failed'))
    else:
        print(data, end='')
    return 0 if report['ssh_command'].get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
