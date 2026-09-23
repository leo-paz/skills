# Skills

A public collection of reusable agent skills. Each skill lives in its own directory under `skills/` and can be installed with the Skills CLI.

## Installation

Install every skill in this repository:

```sh
npx skills add leo-paz/skills --agent codex --yes
```

Install a specific skill:

```sh
npx skills add leo-paz/skills --skill write-goal-prompts --agent codex --yes
```

## Available Skills

| Skill | Description |
| --- | --- |
| `write-goal-prompts` | Create, rewrite, and review durable Codex `/goal` prompts for long-running work. |
| `recover-desktop` | Diagnose and recover Windows Desktop and Ubuntu WSL access from the MacBook. |

## License

Available under the [MIT License](LICENSE).
