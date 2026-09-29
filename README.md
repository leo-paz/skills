# Skills

A public collection of reusable agent skills. Each skill lives in its own directory under `skills/` and can be installed with the Skills CLI.

## Installation

```sh
npx skills add leo-paz/skills --skill herdr-delegate --agent codex claude-code --global --yes
npx skills add leo-paz/skills --skill taildrop-secret-handoff --agent '*' --global --yes
```

## Available Skills

| Skill | Description |
| --- | --- |
| `herdr-delegate` | Start and coordinate another interactive coding agent through Herdr, locally or on a saved SSH machine. Requires Herdr 0.9 or newer and the `herdr-delegate` helper on `PATH`. |
| `taildrop-secret-handoff` | Hand passwords, API keys or files from the user's device to the agent's machine over Tailscale Taildrop without the secret entering chat or model context, and sign into web apps (for example Google SSO) once in a non-automated login desk browser whose session agents then reuse. |

## License

Available under the [MIT License](LICENSE).
