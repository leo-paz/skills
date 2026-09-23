---
name: recover-desktop
description: Manually diagnose and recover Leo's Windows Desktop and Ubuntu WSL access from the MacBook. Use only when explicitly invoked for a Desktop outage or recovery drill.
---

# Recover Desktop

Restore access to `DESKTOP-78ONHIT` using current evidence and the least disruptive repair. Run from a working machine, normally Leo's MacBook. This skill is explicit-only, not a monitor or a scheduled restart.

## Known setup

Verify these if configuration has changed:

- SSH alias `desktop`, Linux user `leo`, Tailscale IP `100.102.149.62`.
- The alias has an intentionally non-resolving hostname and a netcat ProxyCommand. Do not replace it because DNS lookup fails.
- Tailscale Serve forwards tailnet port **22 to Windows localhost:2222**. Ubuntu sshd listens on **2222**. This is not ordinary Windows OpenSSH or a port-22 netsh rule.
- WSL distribution `Ubuntu-24.04`; Windows user `user`.
- Moonlight `/Applications/Moonlight.app` reaches Windows when SSH fails. Select host `DESKTOP-78ONHIT`, then Desktop.
- SSH host `remote-ssh-discovered:desktop` and remote-control host `remote-control:env_e_6a76d77e93f8833093d66f339744a04e` refer to the same PC. Specify the host when reading a task.

## Diagnose before choosing a repair

1. Run `python3 <skill-dir>/scripts/probe.py --output work/desktop-before.json`. It is read-only and bounds each network/SSH operation. A successful TCP connection is not a successful SSH login. If needed, make one comparison through `mini`; do not loop on a dead endpoint.
2. If SSH succeeds, collect the Windows snapshot with `--windows`. Check memory pressure and boot times. A healthy machine needs no restart. If only a Codex task is failing, investigate that runtime/task separately.
3. If SSH fails but Windows is reachable, use Moonlight and [Windows recovery](references/windows-recovery.md). First look for the lock screen or the optional **Let's finish setting up your PC** screen. On September 10, dismissing that screen allowed login startup to run and restored WSL without a restart.
4. Check whether a direct `wsl -d Ubuntu-24.04 -u root --exec /bin/echo WSL_OK` completes. This starts a stopped distribution; it does not restart a running one. Bound the attempt to 15 seconds. A distribution labelled Running can still be wedged.
5. Compare fresh evidence to [previous incidents](references/incidents.md). The same external SSH symptom has had different causes. Do not label this an OOM event from an old baseline, old logs, high disk activity, or large VmmemWSL alone.

## Recovery choices

| Current evidence | Action |
| --- | --- |
| Windows booted recently; user setup/login unfinished; Ubuntu has not started | Complete ordinary sign-in or dismiss optional setup. Allow existing startup to run, then probe SSH. If necessary start the named distribution and SSH. |
| WSL command completes; SSH inactive | Validate sshd configuration, then start the existing SSH unit. Restart only if it is active but demonstrably stuck. Verify port 2222 locally and the existing Serve route. |
| WSL healthy and local SSH healthy; remote port fails | Inspect current Tailscale Serve status. Preserve tailnet-only exposure. Do not add firewall rules, public listeners, or replace proxy configuration speculatively. |
| WSL command hangs and fresh metrics/logs show severe pressure | Capture available evidence. If a particular disposable job is conclusively responsible and interruption is authorized, stop only that job. Otherwise consider terminating just Ubuntu. |
| Ubuntu remains unresponsive after a bounded targeted recovery | Stop repeating the same commands. Report evidence and the next escalation. A Windows reboot is a separate disruptive action, not an automatic fallback. |
| Tailnet and Moonlight both unavailable | Distinguish local Tailscale health, expired host key, sleeping/offline host, and routing. Report the unavailable Windows-side evidence. Do not pretend a remote command was executed. |

Starting a stopped distro or SSH service is part of an ordinary recovery request. Before stopping running workloads, use the user's existing authorization. If interruption is not already authorized, describe the exact affected distro/processes and ask once. A request to diagnose or create a playbook alone does not authorize killing jobs. A Windows reboot, global WSL shutdown, persistent startup changes, credential changes, or workload limits require their own scope. Never unregister a distro, delete VHDs/worktrees, clear caches, reinstall WSL, or update every app as generic recovery.

When asked whether agents are running, distinguish active model turns from application processes. Windows `codex` or `codex-core-node-host` processes do not prove an active agent. If Ubuntu cannot execute commands and the explicit Desktop task lookup fails, report the agent state as unknown. A task on the MacBook or Mini is outside an Ubuntu termination's scope. A later user instruction to proceed after the interruption has been explained authorizes that proposed recovery; do not ask again for the same action.

## Prove recovery

- Run two successful bounded `ssh desktop` commands, including a fresh health snapshot. Report available memory, swap, current PSI, and SSH service state. Static swap occupancy alone is not an outage.
- Check expected containers/services without launching builds: MySQL and ClickHouse were the relevant containers in September 2026. Identify failures rather than restarting everything.
- After terminating Ubuntu, verify that a Windows-owned WSL keepalive session survived or was restored. A successful short WSL command or active systemd service does not establish continued Windows localhost forwarding. See the keepalive recovery in [Windows recovery](references/windows-recovery.md).
- Use `read_thread` on an existing Desktop task with the explicit host. `notLoaded` means lazy loading, not failure. Loading history proves history access; it does not prove a new model turn or every app tool works. Do not send prompts to other tasks without authorization.
- State the cause, repair actually performed, remaining uncertainty, and any interrupted processes. Separate recovery from prevention.
- For historical kernel evidence, first use `journalctl --list-boots`, then select the incident boot explicitly with `journalctl -k -b <boot-id>`. `journalctl -k` alone selects the current boot, even when given an earlier `--since` time. No Windows event 2004 does not rule out memory exhaustion inside WSL.
- Save incident evidence in the current task's `work/` and a concise report in `outputs/` when useful. Do not edit persistent memories unless asked.

## Prevention is a separate decision

September 10 exposed a user-login dependency in `CoreDevWSLKeepAlive`; earlier incidents exposed unbounded heavy workloads. Recommend addressing the applicable mechanism. Do not silently create a scheduled task, change Windows Update policy, add memory limits, or modify the existing daily read-only monitor while recovering access.
