---
name: project-harness-refactor-and-migration
description: Workflow command scaffold for project-harness-refactor-and-migration in object3d-prior.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /project-harness-refactor-and-migration

Use this workflow when working on **project-harness-refactor-and-migration** in `object3d-prior`.

## Goal

Refactor and migrate the project harness structure to a new, lightweight entrypoint, updating documentation, folder structure, and routing pointers.

## Common Files

- `docs/superpowers/specs/*.md`
- `docs/superpowers/plans/*.md`
- `.project2/PROJECT.md`
- `.project2/CLAUDE.md`
- `.project2/agents/README.md`
- `.project2/skills/README.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Draft and add a design/specification document in docs/superpowers/specs/
- Add an implementation plan in docs/superpowers/plans/
- Create or restructure entrypoint files and placeholder READMEs in the new harness directory (e.g., .project2/ or .claude/), including PROJECT.md or CLAUDE.md and subfolders like agents/, skills/, hooks/, rules/, commands/
- Update the root CLAUDE.md to point to the new entrypoint
- Remove or archive the legacy harness directory (e.g., move .claude/ to .claude-legacy/ and later delete it)

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.