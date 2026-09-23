# Windows recovery commands

Use the existing Moonlight pairing when SSH cannot execute. Computer Use must show the intended terminal and readable output. Type one command, inspect it, then press Enter. Fast batched Run-dialog input lost characters during previous incidents. Use a fresh console if a prior WSL invocation has not returned; do not queue commands into a stuck process. Avoid changing Moonlight input preferences unless needed and authorized. Previous working settings used desktop mouse mode and Windows shortcut capture.

With the Codex computer-use API, a visible Moonlight window may reject coordinate clicks with `noWindowsAvailable`. Refresh its accessibility tree and activate the Desktop tile's exposed button instead. This resumed the stream on September 10. If the bundle identifier is ambiguous because a mounted Moonlight disk image shares it, select `/Applications/Moonlight.app` explicitly. Re-select the app if the tool says Computer Use is no longer active.

## Check Windows and startup first

Open PowerShell through Win+R. Dismiss optional Windows setup with **Remind me later**. If credentials are required, let the user complete sign-in.

```powershell
Get-Date
Get-CimInstance Win32_OperatingSystem | Select LastBootUpTime,FreePhysicalMemory,TotalVisibleMemorySize
Get-WinEvent -FilterHashtable @{LogName='System';Id=1074,6008,41,6005,6006;StartTime=(Get-Date).AddDays(-2)} -MaxEvents 12 | Select TimeCreated,Id,Message | Format-List
Get-Process VmmemWSL -ErrorAction SilentlyContinue | Select Id,WorkingSet64,CPU
Get-CimInstance Win32_StartupCommand | Where-Object Name -eq 'CoreDevWSLKeepAlive' | Select Name,Command,Location
```

The verified startup entry is the Windows user's Run registry value `CoreDevWSLKeepAlive`, executing `C:\Users\user\core-dev-bootstrap\keep-wsl-running.ps1`. That script launches Ubuntu, starts Docker and SSH, and holds WSL open with `sleep infinity`. It depends on user startup, whereas Tailscale and Sunshine are automatic system services. This explains how Moonlight can be available hours before SSH after an update reboot. Inspect the current file before invoking it; do not run the broader Desktop bootstrap/install shortcuts as a recovery shortcut.

After an authorized Ubuntu termination, restore its keepalive as well as checking services. On September 10 evening, Ubuntu returned `WSL_OK` and showed SSH active on 2222, yet Windows localhost refused connections. No `wsl.exe` client remained. A hidden PowerShell launch of the existing script without the startup entry's process execution-policy option exited. Do not treat a returned launcher PID as success; inspect whether the process remains and collect launch errors if needed.

This minimal recovery session restored sustained access without editing scripts, execution policy, or startup configuration:

```powershell
Start-Process wsl.exe -ArgumentList '-d Ubuntu-24.04 -u leo --exec sleep infinity' -WindowStyle Hidden -PassThru
```

It intentionally remains running. Confirm its command line using `Get-CimInstance Win32_Process`, then prove two remote SSH commands and service/container health. This is a temporary live session, not a fix for the user-login dependency. Check for an existing equivalent session before launching another; Windows may expose parent/child wsl.exe processes for one launch.

## Bound commands entering WSL

For commands that might hang, use this helper in the Windows console. It kills only its own timed-out `wsl.exe` client, not the distribution. A timed-out client does not prove the operation was cancelled inside WSL; inspect state before another mutation.

```powershell
function Invoke-WslBounded {
    param([string[]]$WslArgs, [int]$Seconds = 15)
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo.FileName = "$env:WINDIR\System32\wsl.exe"
    $p.StartInfo.Arguments = $WslArgs -join ' '
    $p.StartInfo.UseShellExecute = $false
    [void]$p.Start()
    if (-not $p.WaitForExit($Seconds * 1000)) {
        Stop-Process -Id $p.Id -ErrorAction SilentlyContinue
        throw "WSL client exceeded $Seconds seconds; inspect state before retrying."
    }
    if ($p.ExitCode -ne 0) { throw "WSL exited $($p.ExitCode)" }
}
Invoke-WslBounded -WslArgs @('--list','--verbose')
Invoke-WslBounded -WslArgs @('-d','Ubuntu-24.04','-u','root','--exec','/bin/echo','WSL_OK')
```

The example arguments contain no spaces within individual values. For arbitrary shell snippets, avoid joining arguments without quoting; use a script file or properly quoted command instead.

## Responsive Ubuntu, failed SSH

```powershell
Invoke-WslBounded -WslArgs @('-d','Ubuntu-24.04','-u','root','--exec','/usr/sbin/sshd','-t')
Invoke-WslBounded -WslArgs @('-d','Ubuntu-24.04','-u','root','--exec','systemctl','is-active','ssh')
Invoke-WslBounded -WslArgs @('-d','Ubuntu-24.04','-u','root','--exec','systemctl','start','ssh')
& 'C:\Program Files\Tailscale\tailscale.exe' serve status
```

An inactive `is-active` exits nonzero; inspect that result before continuing. If SSH is already active, collect unit logs/listeners instead of treating a repeated start as a repair. Verify expected `localhost:2222` and tailnet port 22. `netsh interface portproxy show all` can reveal an additional proxy, but the known installation uses Tailscale Serve. Do not replace one with the other.

## Unresponsive Ubuntu

Only after capturing evidence and resolving interruption authorization:

```powershell
Invoke-WslBounded -WslArgs @('--terminate','Ubuntu-24.04') -Seconds 30
Invoke-WslBounded -WslArgs @('-d','Ubuntu-24.04','-u','root','--exec','/bin/echo','WSL_OK') -Seconds 30
Invoke-WslBounded -WslArgs @('-d','Ubuntu-24.04','-u','root','--exec','systemctl','start','ssh')
```

Terminating Ubuntu stops its agents, shells, containers, and development servers. It preserves files but can interrupt in-flight writes. If this sequence times out, stop and assess; do not loop through terminate, shutdown, service restart, and reboot blindly. September 3 required a separately authorized Windows reboot after narrower attempts failed; September 9 needed only Ubuntu termination; September 10 morning needed neither, while the evening recurrence needed Ubuntu termination and a restored keepalive session.

A client timeout is not proof that termination had no effect. In the September 10 evening recurrence, the terminate client timed out after 30 seconds and VmmemWSL memory subsequently fell. Inspect Windows process state and the existing Serve route before deciding whether a single bounded Ubuntu responsiveness check is warranted. Do not issue another termination merely because the first client timed out.

After recovery, use SSH and inspect prior-boot logs with `sudo -n journalctl`. Windows PowerShell is available from WSL at `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`; bare `powershell.exe` was absent from SSH PATH on September 10. Do not modify PATH to work around this.

Sources: [Microsoft WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands), [WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking). Host facts were checked against the installed setup on September 10, 2026. The bounded PowerShell helper passed live WSL list and echo checks. Its termination path was not exercised against a deliberately hung VM.
