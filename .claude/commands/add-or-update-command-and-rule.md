---
name: add-or-update-command-and-rule
description: Workflow command scaffold for add-or-update-command-and-rule in object3d-prior.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-command-and-rule

Use this workflow when working on **add-or-update-command-and-rule** in `object3d-prior`.

## Goal

Add or update a command (e.g., git workflow) and its corresponding rule documentation, updating entrypoint references and cleaning up placeholder files.

## Common Files

- `.claude/rules/*.md`
- `.claude/commands/*/*.md`
- `.claude/CLAUDE.md`
- `.claude/commands/.gitkeep`
- `.claude/rules/.gitkeep`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add or update a rule documentation file in .claude/rules/ (e.g., git.md)
- Add or update a command implementation or spec in .claude/commands/ (e.g., git/commit.md)
- Update .claude/CLAUDE.md to reference the new command/rule
- Remove .gitkeep from commands/ or rules/ if they now contain real files

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.