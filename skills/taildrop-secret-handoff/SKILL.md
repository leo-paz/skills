---
name: taildrop-secret-handoff
description: Get a password, API key, sign-in code or other secret from the user onto the machine an agent runs on without it ever entering chat, logs or model context, using Tailscale Taildrop; and sign into web apps as the user in a non-automated "login desk" browser. Use whenever a task needs a credential, a file only the user has, or a human sign-in (for example Slack or Google SSO).
compatibility: Requires Tailscale on both the user's device and the agent's machine, on the same tailnet and user (Taildrop). The login desk part requires a Linux machine with Chromium, a virtual display (Xvfb or Xvnc), a VNC web client and xdotool.
---

# Taildrop secret handoff

Taildrop is Tailscale's built-in file transfer: `tailscale file cp <file> <node>:` sends a file directly between devices on the same tailnet over the encrypted tailnet, with no cloud copy, and `tailscale file get` receives it. Use it to hand secrets from the user's device to the agent's machine.

## Rules

- Never ask the user to paste a secret into chat. Chat is stored in transcripts and sent to the model.
- Never read, `cat`, print, grep, log or copy the secret into any context or output. Pass only the file path to whatever consumes it.
- Keep it in a `700` directory as a `600` file, and `shred -u` it right after use. Confirm with `ls` that it is gone.
- Never extract, export or decrypt browser cookie stores (macOS Keychain, Chrome cookies). That is infostealer behavior and trips model safeguards. If a safeguard flags a session, change the approach; do not switch models to get around it.
- Never solve CAPTCHAs or "I'm not a robot" checks with automated input. Ask the user to click them, or use another sign-in path.
- Never type into, or accept, account recovery flows.

## 1. Find the node names

Run `tailscale status` on the agent's machine. Note this machine's node name and the user's device. Do not hardcode them in shared files.

## 2. Give the user one command (macOS zsh; fill in `<agent-node>` and the file name)

```bash
read -rs "P?Password: "; echo; printf %s "$P" > ~/handoff-secret && chmod 600 ~/handoff-secret && "$(command -v tailscale || echo /Applications/Tailscale.app/Contents/MacOS/Tailscale)" file cp ~/handoff-secret <agent-node>: ; rm -f ~/handoff-secret; unset P
```

On Linux, use `read -rs P` and a plain `tailscale`. For an existing file, the user runs `tailscale file cp <file> <agent-node>:`.

## 3. Receive and use it without reading it

```bash
install -d -m 700 ~/.config/agent-secrets/inbox
tailscale file get --wait --conflict=overwrite ~/.config/agent-secrets/inbox   # blocks until it arrives
chmod 600 ~/.config/agent-secrets/inbox/*
```

Then use one of these:
- Typing into a browser field on the login desk display: focus the field, then `DISPLAY=<desk> xdotool type --clearmodifiers --delay 40 --file <path>`, then `xdotool key Return`.
- A CLI that reads secrets from stdin: `<cli> --password-stdin < <path>`.

Finish with `shred -u <path> && ls ~/.config/agent-secrets/inbox`.

## Login desk: sign in as the user once, then reuse the session

Web sign-ins through Google SSO are refused in automation-controlled browsers (CDP, Playwright, `navigator.webdriver`). To avoid that:

1. Run a normal Chromium with no remote debugging and no automation flags, on a dedicated profile directory (`700`), on a virtual display.
2. Expose that display with a VNC web client on the tailnet only (`tailscale serve`, never Funnel), with a one-time password. The user can watch or click if needed.
3. Type from the agent's machine with `xdotool` on that display (XTest input, not CDP). Type the email yourself, since it is not secret. Get the password through Taildrop (above). The user approves 2-step prompts on their phone.
4. Stop the desk cleanly: close Chromium normally so it writes its cookies. Check that the profile has no saved passwords.
5. Reuse the profile headlessly with your browser automation tool (for example `agent-browser --profile <dir>`). When a reused session is signed out, send the user one notification asking them to repeat the sign-in. Never ask for a sign-in any other way.

Tips:
- In noVNC, macOS Cmd maps to Alt, so paste inside the desk with Ctrl+V.
- If the viewer drops keys, type from the agent side with `xdotool` instead of asking the user to type.
