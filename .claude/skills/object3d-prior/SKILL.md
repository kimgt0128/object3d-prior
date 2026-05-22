```markdown
# object3d-prior Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches the core development patterns and workflows used in the `object3d-prior` TypeScript codebase. It covers coding conventions, file organization, commit styles, and project-specific workflows for harness migration and command/rule management. By following these guidelines, contributors can maintain consistency and efficiency across the project.

## Coding Conventions

- **Language:** TypeScript
- **Framework:** None detected

### File Naming

- Use **kebab-case** for all file and folder names.

  **Example:**
  ```
  object-utils.ts
  mesh-loader.test.ts
  ```

### Imports

- Use **relative imports** for all internal modules.

  **Example:**
  ```typescript
  import { calculateNormals } from './geometry-utils';
  ```

### Exports

- Use **named exports**.

  **Example:**
  ```typescript
  // geometry-utils.ts
  export function calculateNormals(...) { ... }
  export const DEFAULT_COLOR = '#fff';
  ```

### Commit Messages

- Use **Conventional Commits** style.
- Common prefixes: `docs`, `chore`, `fix`.
- Keep commit messages concise (average ~35 characters).

  **Example:**
  ```
  fix: correct mesh normal calculation
  docs: update README with usage example
  chore: remove deprecated loader
  ```

## Workflows

### Project Harness Refactor and Migration

**Trigger:** When the project harness structure needs to be refactored or migrated to a new location or format.  
**Command:** `/harness-migrate`

1. Draft and add a design/specification document in `docs/superpowers/specs/`.
2. Add an implementation plan in `docs/superpowers/plans/`.
3. Create or restructure entrypoint files and placeholder READMEs in the new harness directory (e.g., `.project2/` or `.claude/`), including `PROJECT.md` or `CLAUDE.md` and subfolders like `agents/`, `skills/`, `hooks/`, `rules/`, `commands/`.
4. Update the root `CLAUDE.md` to point to the new entrypoint.
5. Remove or archive the legacy harness directory (e.g., move `.claude/` to `.claude-legacy/` and later delete it).
6. Clean up git tracking for removed or moved files.

**Example Directory Structure After Migration:**
```
.project2/
  PROJECT.md
  CLAUDE.md
  agents/
    README.md
  skills/
    README.md
    workflow.md
  commands/
    .gitkeep
  hooks/
    .gitkeep
  rules/
    .gitkeep
```

### Add or Update Command and Rule

**Trigger:** When introducing a new command (such as a git operation) and its usage rules to the harness.  
**Command:** `/add-command`

1. Add or update a rule documentation file in `.claude/rules/` (e.g., `git.md`).
2. Add or update a command implementation or spec in `.claude/commands/` (e.g., `git/commit.md`).
3. Update `.claude/CLAUDE.md` to reference the new command/rule.
4. Remove `.gitkeep` from `commands/` or `rules/` if they now contain real files.

**Example:**
```
.claude/
  rules/
    git.md
  commands/
    git/
      commit.md
  CLAUDE.md
```

## Testing Patterns

- **Test files** use the pattern `*.test.*` (e.g., `geometry-utils.test.ts`).
- **Testing framework** is not specified; follow the project's test file naming and structure conventions.
- Place test files alongside the modules they test or in a dedicated test directory as appropriate.

**Example:**
```
geometry-utils.ts
geometry-utils.test.ts
```

## Commands

| Command           | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| /harness-migrate  | Refactor and migrate the project harness structure                      |
| /add-command      | Add or update a command and its corresponding rule documentation        |
```
