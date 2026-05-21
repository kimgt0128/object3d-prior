# 추천 Workflow 참고 자료

이 파일은 multi-agent orchestration, worktree, Issue, PR, code review, stacked change 전략을 다시 확인할 때 사용하는 저장용 참고 목록이다.

## Context Engineering

- NeoLabHQ Context Engineering Kit: https://github.com/NeoLabHQ/context-engineering-kit
  - 참고할 점: token-efficient skill, granular loading, subagent-driven development, review agent, reflection 기반 memory.
- Agent Skills for Context Engineering: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
  - 참고할 점: context를 attention budget으로 보는 관점, progressive disclosure, observation masking, filesystem-based context, structured compression, multi-agent context isolation.
- Project overview page: https://muratcankoylan.com/projects/agent-skills-context-engineering/
  - context engineering과 reusable skill의 프로젝트 가치 설명에 참고하기 좋다.
- Context fundamentals skill: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-fundamentals/SKILL.md
- Context optimization skill: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-optimization/SKILL.md
- Filesystem context skill: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/filesystem-context/SKILL.md
- Multi-agent patterns skill: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/multi-agent-patterns/SKILL.md
- Memory systems skill: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/memory-systems/SKILL.md

## Multi-Agent Orchestration

- Bryce Watson multi-agent systems guide: https://brycewatson.com/blog/15-multi-agent-guidelines/
  - 참고할 점: root orchestrator, subagent isolation, skill과 agent 구분, filesystem state, multi-agent pattern 남용 방지.
- Anthropic managed multi-agent sessions docs: https://platform.claude.com/docs/en/managed-agents/multi-agent
  - 참고할 점: coordinator thread, isolated agent session, shared filesystem, persistent thread.
- Sub-agent routing guide: https://www.buildthisnow.com/blog/guide/agents/sub-agent-best-practices
  - 참고할 점: parallel, sequential, background dispatch를 나누는 기준.
- Orchestrator pattern discussion: https://www.channel.tel/blog/claude-code-subagents-orchestrator-pattern
  - 참고할 점: main session을 coordinator로 두는 구조, subagent boundary, conflict-aware coordination.

## Worktree

- Git worktree docs: https://git-scm.com/docs/git-worktree
  - agent branch별 독립 local workspace를 만들 때 참고한다.

## GitHub Issue와 PR

- About pull requests: https://docs.github.com/articles/using-pull-requests
- Creating a pull request: https://docs.github.com/articles/creating-a-pull-request
- Linking pull requests to issues: https://docs.github.com/articles/closing-issues-via-commit-message
- Reviewing proposed changes: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request
- Pull request reviews REST API: https://docs.github.com/rest/pulls/reviews

## GitHub CLI

- `gh pr review`: https://cli.github.com/manual/gh_pr_review
  - 자동화 흐름에서 PR review comment를 남길 때 참고한다.

## Stacked PR

- Graphite stacked diffs guide: https://graphite.dev/guides/stacked-diffs
- Graphite stack structure guide: https://graphite.com/docs/how-to-structure-your-stacks
- GitHub `gh-stack` stacked PR guide: https://github.github.com/gh-stack/guides/stacked-prs/

## Code Review Practice

- Google Engineering Practices, code review standard: https://google.github.io/eng-practices/review/reviewer/standard.html
- What to look for in a code review: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Writing review comments: https://google.github.io/eng-practices/review/reviewer/comments.html
