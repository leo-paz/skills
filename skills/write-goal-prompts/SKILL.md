---
name: write-goal-prompts
description: Use when creating, rewriting, or reviewing Codex /goal prompts for long-running work, migrations, refactors, prototypes, experiments, deployment retries, or prompt-optimization loops that need clear scope, validation, checkpoints, progress reports, and stopping conditions.
---

# Write Goal Prompts

## Overview

Turn long-running Codex work into one durable `/goal` prompt with a clear contract. A good goal is bigger than one normal prompt, smaller than an open-ended backlog, and anchored to a verifiable stopping condition. Treat the goal prompt as exit criteria, not a full design document: keep the success condition short enough that Codex can check it after each turn, and put deep background in referenced plans or files.

Source baseline: OpenAI Developers, "Follow a goal" (`https://developers.openai.com/codex/use-cases/follow-goals`). If the user asks about current CLI setup, feature availability, or exact control commands, verify the official docs because `/goal` behavior can change.

## Fit Check

Use `/goal` when the task has:

- One durable objective Codex can pursue across turns.
- A concrete end state that can be checked with commands, artifacts, screenshots, eval scores, or tests.
- Enough independent work for Codex to make progress without constant steering.
- A validation loop Codex can repeat after each checkpoint.

Do not use `/goal` for:

- A loose list of unrelated tasks.
- Work that needs frequent product, policy, security, or business judgment.
- A one-shot answer or small edit that should finish in a normal turn.
- A task with no practical way to verify progress.

## Prompt Contract

Before drafting, identify these fields. If a field is missing, either add a bracketed placeholder or ask one concise question only when guessing would make the goal unsafe or unverifiable.

| Field | What to capture |
| --- | --- |
| Objective | The single outcome Codex should complete. |
| Stop condition | The exact state that means Codex should stop; prefer a number, threshold, parity target, named artifact, or binary pass/fail condition when natural. |
| Initial context | Files, docs, issues, logs, plans, designs, or commands to inspect first. |
| Scope | What Codex may change and what must stay untouched. |
| Measurement | How progress is measured: commands, evals, visual diff tools, timing scripts, coverage reports, or artifact checks. |
| Environment and tools | Realistic runtime assumptions: local/staging/preview/prod-like data, flags, browser/device access, deploy logs, or acceptable generated fixtures. |
| Validation loop | Commands, tests, evals, screenshots, builds, deploy checks, or artifacts proving progress. |
| Checkpoints | Milestones Codex should complete and verify incrementally. |
| Progress reports | Short status format: checkpoint, verified evidence, remaining work, blocked or not. |
| Anti-gaming constraints | What must not count as success, such as lowering test coverage, disabling checks, cropping a reference image, or changing the metric instead of the system. |
| Pause rules | Conditions that should stop the run for human guidance. |
| Final cleanup | Review/reflection steps before stopping: remove failed attempts, run a local review, update docs/artifacts, commit or draft PR if requested. |

## Template

Use this structure and remove fields that do not apply:

```text
/goal Complete [objective] without stopping until [short measurable stop condition].

Read [files/docs/issues/logs/PLAN.md] first. Keep changes limited to [scope], and do not [non-goals].
Use [realistic environment/tools/data source], with [acceptable fallback or fixture] if unavailable. Measure progress with [command/eval/tool/artifact], and do not satisfy the goal by [anti-gaming shortcut].

Work in checkpoints:
1. [checkpoint with proof]
2. [checkpoint with proof]
3. [checkpoint with proof]

After each checkpoint, run [validation command or artifact check], inspect failures, and keep changes minimal and targeted. Keep a short progress log/status that names the current checkpoint, what was verified, what remains, and whether anything is blocked. For long-running work, [commit at meaningful milestones / update a progress artifact / push to a draft PR / post updates] if appropriate.

Pause and ask for guidance if [risk, missing decision, destructive change, credential need, policy/product ambiguity, unrealistic environment, or repeated validation failure]. Before stopping, clean up failed attempts, run [final review or verification], and report the final evidence.
```

## Review Checklist

A strong `/goal` prompt:

- Starts with a single objective, not a backlog.
- Names a short stopping condition that can be proven, preferably with a number/threshold/parity target when natural.
- Points Codex to the first sources of truth to read.
- Defines allowed scope and explicit non-goals.
- Names the realistic environment or fixture Codex should use.
- Explains how progress is measured, not only how the final result is tested.
- Gives repeatable validation commands or artifact checks.
- Blocks shortcut success, such as disabling tests, weakening coverage, editing generated metrics, or faking visual parity.
- Requests checkpointed progress instead of vague effort.
- For multi-hour goals, asks for useful breadcrumbs: milestone commits, a draft PR, a progress artifact, or status updates.
- Requires final cleanup/review so abandoned attempts do not remain in the diff.
- States when to pause instead of pushing through ambiguity.
- Avoids subjective terms like "polished" or "good" unless paired with concrete acceptance criteria.

## Special Cases

Optimization goals:

- Capture a baseline and target in the prompt, such as "reduce build time by 30%" or "LCP below 2.5s."
- Require comparable environments: same flags, database shape, deploy path, dataset size, and runtime tier where practical.
- Say what cannot be changed to win the metric, such as skipping build steps or reducing test coverage.

Visual/UI goals:

- Use screenshots or videos as context, not as the only stop condition.
- Prefer a design-system checklist, user-flow acceptance criteria, and visual diff/browser tooling over "pixel perfect."
- Warn against shortcuts like cropping the reference image, inlining screenshots, or spending unlimited effort on decorative assets.

Long-running goals:

- Ask Codex to leave progress breadcrumbs when useful: meaningful commits, a draft PR, a markdown/HTML status artifact, or updates to a requested channel.
- Include a final reflection/review step that removes failed experiments and verifies the remaining diff is intentional.

## Examples

Migration:

```text
/goal Migrate this project from [legacy stack] to [target stack] without stopping until the new path passes [contract tests] and the legacy path still has [rollback/parity condition].

Read [migration plan/docs] first. Keep public behavior and visual output unchanged. Work screen-by-screen or module-by-module, running [test command] and [visual verification command] after each checkpoint. Pause if parity cannot be preserved without a product decision.
```

Prototype:

```text
/goal Implement [PLAN.md] without stopping until the app builds, launches, and satisfies every acceptance criterion in the plan.

Read [PLAN.md and references] first. Work milestone-by-milestone, adding focused tests or browser checks for each milestone. After each checkpoint, run [build/test/playwright command] and record what passed, what remains, and blockers.
```

Prompt optimization:

```text
/goal Optimize the prompts in [prompt files] until [eval command] reaches [target score or pass rate].

After each prompt change, run [eval command], inspect failures, and keep edits minimal and targeted. Stop when the target is met or when further improvement requires product, policy, or dataset guidance.
```

Deployment or retry loop:

```text
/goal Diagnose and fix [deployment/check failure] without stopping until [service/check URL/CI job] passes twice in a row.

Read [logs, runbook, config files] first. Make the smallest plausible change, run [verification command], and capture the result after each attempt. Pause if the next step would require secrets, destructive infrastructure changes, or unexplained production risk.
```
