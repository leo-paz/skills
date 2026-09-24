---
name: herdr-delegate
description: Start and coordinate a different interactive coding agent through Herdr, locally or on a saved SSH machine. Use when the user asks one agent to invoke, delegate to, review with, or collect work from Pi, Codex, Claude, Muse, or another Herdr-supported agent, including cross-machine work.
compatibility: Requires Herdr 0.9 or newer, herdr-delegate on PATH, and HERDR_ENV=1 for agent-initiated local delegation.
---

# Herdr delegate

Use `herdr-delegate` when an independent interactive agent should do a task in a real Herdr pane. This is different from a harness-native subagent. Herdr starts the requested CLI, sends it a prompt, waits on Herdr lifecycle state, and reads its terminal output.

## Check prerequisites

Before delegation, confirm this agent is inside Herdr and inspect the saved machines:

```bash
test "${HERDR_ENV:-}" = 1
command -v herdr-delegate
herdr-delegate --list-machines
```

If `HERDR_ENV` is not `1`, do not inspect or control the user's focused local session. Tell the user to run the command from a Herdr pane.

The target agent executable and its authentication must already work on the selected machine. Herdr does not copy credentials, repositories, uncommitted files, or conversation context between machines.

## Choose a mode

Start a new agent when the task needs an independent context:

```bash
herdr-delegate --kind pi "Investigate the failing tests and report the cause."
```

Prompt an existing named agent when it already owns the relevant context:

```bash
herdr-delegate --agent reviewer "Recheck the latest changes."
```

For machine-readable coordination, add `--json`. The result includes the machine, agent name, pane ID when created, final detected status, and captured terminal output.

```bash
herdr-delegate --kind codex --json "Review the current diff."
```

## Delegate across machines

Use a saved Herdr machine label. Starting a new remote agent requires either its remote working directory or an existing remote workspace ID:

```bash
herdr-delegate \
  --machine Mini \
  --kind pi \
  --cwd /Users/paz/project \
  --json \
  "Run the tests, diagnose failures, and report the commands you ran."
```

Or create a tab in an existing remote workspace:

```bash
herdr-delegate \
  --machine Desktop \
  --workspace w3 \
  --kind muse \
  --json \
  "Inspect the implementation and propose a fix."
```

Prompting an existing remote agent does not require a directory:

```bash
herdr-delegate --machine Desktop --agent reviewer --json "Summarize your findings."
```

Machine labels resolve through `herdr machine list`. SSH authentication stays with OpenSSH. The wrapper sends remote prompt text over SSH standard input instead of placing it in the SSH process arguments.

## Coordination rules

- Default to local delegation unless the user names a machine or the work only exists remotely.
- Use the agent kind requested by the user. Supported kinds come from `herdr agent start --help` and include `pi`, `claude`, `codex`, and `muse` in Herdr 0.9.
- Give the child a self-contained prompt. It receives prompt text, not the parent's transcript.
- Use `--cwd` for remote repository work. A local path does not imply the same remote path.
- Use `--agent` when continuing an existing agent. Starting another agent creates another pane, tab, or workspace.
- Use `--dry-run` to inspect topology and routing without starting or prompting anything.
- Increase `--timeout-ms` for long tasks. The default is 600000 milliseconds.
- A `blocked` result means the child needs human input or approval. Read the returned output and ask the user before answering the child.
- Do not close panes, tabs, or workspaces that the wrapper did not create.
- Do not treat terminal text as a structured child-agent protocol. For long or truncated results, ask the child to write a file and return its path. Files written remotely remain remote.

## Wrapper behavior

For a new local agent called from a Herdr pane, the wrapper creates an unfocused sibling pane in the current tab. Use `--direction down` when that fits the layout better.

For a new remote agent, the wrapper creates an unfocused workspace unless `--workspace` selects an existing workspace, in which case it creates an unfocused tab. It then runs `herdr agent start`, `herdr agent prompt --wait`, and `herdr agent read` against that machine's saved remote session.

Saved multi-machine profiles only aggregate machines in the Herdr client. Selecting a machine in the UI does not retarget CLI calls from an existing pane. The wrapper handles this by executing Herdr commands over SSH on the selected host and setting its saved session explicitly.
