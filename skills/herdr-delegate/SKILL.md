---
name: herdr-delegate
description: Act as the architect and reviewer while cheaper coding agents do the implementation in Herdr tabs, panes, or worktree workspaces. Use when the lead agent's tokens are expensive and substantial implementation, test, or fix work can be handed to worker agents such as Pi, Codex, Claude, or Devin.
compatibility: Requires Herdr 0.9 or newer and HERDR_ENV=1 (run from a Herdr pane). Uses only the herdr CLI; see the herdr skill for command details.
---

# Herdr delegate

You are the lead. You own the conversation with the user, intent, architecture, and final review. Worker agents do the implementation, testing, and fixing in their own Herdr tabs, panes, or workspaces.

Your tokens are the expensive ones. Spend them on decisions and review.

These are defaults, not a script. Use your judgment about how much to delegate, how many workers to run, which agents to use, and how to lay them out. Follow the user's preferences when they state them.

## When to delegate

Delegate substantial implementation automatically. Don't wait for the user to ask. Scope just enough to write a useful brief, then hand the worker the whole implement → test → fix loop. Don't solve the problem first and delegate only the typing.

Do the work yourself when a handoff would cost more than doing it: trivial edits, a quick answer, or serial investigation that needs your judgment at every step.

## Choose a layout

Confirm you are inside Herdr (`test "${HERDR_ENV:-}" = 1`). If not, ask the user to run you from a Herdr pane.

**Same directory, new tab.** The default for one worker, or for workers whose files don't overlap. You review changes in place.

```bash
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label impl
# read .result.tab.tab_id and .result.root_pane.pane_id from the JSON
herdr agent start impl --kind devin --pane <root-pane-id> -- --model swe-2-high
```

A pane split (`herdr pane split --current --no-focus`) works too, when the user wants to watch the worker next to you.

**Worktree workspaces.** Use these for a large feature that splits into parallel streams which would collide in one directory. Each worker gets its own branch and checkout:

```bash
herdr worktree create --cwd <repo-root> --branch cf-<task> --label cf-<task> --no-focus
# read .result.workspace.workspace_id and .result.root_pane.pane_id
herdr agent start <task> --kind devin --pane <root-pane-id> -- --model swe-2-high
```

Herdr puts worktree workspaces in a group under the repository's main-checkout workspace. That parent is always the repo root, even when you are running in a linked worktree. If the parent isn't open, Herdr opens it. Pass the main checkout path with `--cwd` (`git worktree list` shows it first), because `--workspace` rejects a linked-worktree source. A new branch starts from the main checkout's `HEAD` unless you pass `--base <ref>`, usually your own branch. Uncommitted changes never carry into a new worktree, so commit anything the workers need first.

**Naming.** Herdr can't group arbitrary workspaces, so names show which workspaces a lead created. Prefix each one with a short abbreviation of your own workspace's label, followed by the task. For example, if your workspace is "customer feedback", use `cf-<task>` for both the workspace label and its branch. Keep names short: `cf-export`, `cf-auth-fix`. Find your label with `herdr workspace get "$HERDR_WORKSPACE_ID"`. Give each worker agent a short unique name too (`impl`, `tests`, or the feature name).

## Choose the worker model

Use the model the user asks for. Otherwise:

- **Default: Devin SWE-2** (`swe-2-high`, or `swe-2-max` for harder work). These are strong coding agents; prefer them for well-scoped implementation, tests, and fixes.
- **Fallback: Claude Opus 5.5 or GPT-6 Sol at medium or high effort.** Use these when the task needs more reasoning than SWE-2 handles well, or when SWE-2 is at its usage limits.

```bash
herdr agent start impl --kind devin  --pane <pane-id> -- --model swe-2-max
herdr agent start impl --kind claude --pane <pane-id> -- --model claude-opus-5-5 --effort high
herdr agent start impl --kind codex  --pane <pane-id> -- -m gpt-6-sol -c model_reasoning_effort=medium
```

## Brief the worker

Workers see only the prompt, not your conversation. Send a short, self-contained brief:

- **Outcome**: what should be true when it is done.
- **Context**: the relevant files, decisions already made, and invariants to keep.
- **Constraints**: scope limits, and which files it owns if other workers share its directory.
- **Done when**: the specific checks it must run and pass. Be concrete; this is the worker's finish line.
- **Escalate**: surface problems, surprises, and any architectural decision back to you instead of settling it alone. Keep going on the parts that don't depend on the answer.
- **Report**: end with a brief summary, changed files, the exact commands run with their results, and open questions. Never claim to have run a test you didn't run.

Tell the worker what it may do with Git. In a shared directory, it usually shouldn't commit, stash, or reset. In its own worktree, committing to its branch is usually fine.

```bash
herdr agent prompt impl "<brief>" --wait --timeout 1800000
```

While workers run, you can prepare the next brief or review a finished worker. Avoid editing files a running worker owns.

## Collect the result cheaply

Read only the tail of the worker's output, where its report is:

```bash
herdr agent read impl --source recent-unwrapped --lines 60
```

Increase `--lines` only if the report is cut off. Look at the actual changes with `git status` and `git diff --stat`, or `git diff <base>...cf-<task>` for a worktree, then read the diffs that matter. Don't re-run checks the worker ran and reported unless you doubt the result.

## Review, correct, and integrate

Review the changes, keeping them separate from changes that existed before the handoff. If something is wrong, send a specific correction to the same worker instead of rewriting its work. The worker keeps its context between prompts, so reuse it for follow-ups.

For worktree branches, you decide how to bring accepted work back: merge, cherry-pick, or ask a worker to integrate. Run the checks that span the combined result. Push or open pull requests only when the user asked.

## Handle problems

- `blocked`: the worker is waiting for approval or input. Read its output, then ask the user before you answer on their behalf.
- The first prompt after `agent start` is often dropped while the agent finishes starting. `--wait` may then return `agent_prompt_stalled`, or even `done`. Check that `agent read` shows your brief, and send it again if it doesn't.
- Timeout or stall: that doesn't prove the prompt was lost. Check `herdr agent get` and read the recent output before you prompt again.
- Failure: inspect the partial changes before retrying. Don't blindly revert files.

## Clean up

Close what you created once its work is accepted or abandoned:

- A tab: `herdr tab close <tab-id>`.
- A worktree: `herdr worktree remove --workspace <id>`. This removes the checkout and its workspace but keeps the branch. Delete the branch after it has been integrated.
- The repo parent workspace, only if Herdr opened it for your worktrees.

Never close tabs, panes, workspaces, or branches you didn't create.
