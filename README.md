# Skills

A public collection of reusable agent skills. Each skill lives in its own directory under `skills/` and can be installed with the Skills CLI.

## Installation

```sh
npx skills add leo-paz/skills --skill herdr-delegate --agent codex claude-code --global --yes
```

## Available Skills

| Skill | Description |
| --- | --- |
| `herdr-delegate` | Start and coordinate another interactive coding agent through Herdr, locally or on a saved SSH machine. Requires Herdr 0.9 or newer and the `herdr-delegate` helper on `PATH`. |

## License

Available under the [MIT License](LICENSE).
