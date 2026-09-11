---
name: testing
description: While testing an implemented feature or fix, investigate incidental suspected bugs and file new, unrelated findings in the project's designated GitHub repository. Use during implementation testing, not as a request for a broader bug audit.
---

# Testing

The user has authorized automatic GitHub issue creation for incidental bugs discovered while testing a feature or fix. Do not ask for confirmation for each issue within this scope.

1. When suspicious behavior appears, investigate enough to describe it and establish reproduction steps. Record what was observed and any uncertainty; do not present speculation as a confirmed defect.
2. Determine whether the current changes introduced it. Fix regressions from the current work within the original task. Report unrelated bugs separately rather than expanding the implementation scope.
3. Read the project's `AGENTS.md`, contributing guide, and any project guide they require. Resolve the issue repository from those instructions, not merely the push remote. For `FactoryGameFan/factorio-blueprint-editor`, use that repository, not the original upstream or the user's fork. If the destination is ambiguous, retain a draft and ask which repository to use.
4. Search both open and closed issues for the same behavior. If already reported, give the user the existing link instead of creating a duplicate. Explain any evidence that a closed issue still reproduces without automatically reopening or commenting on it.
5. For a new finding, create an issue using the repository's issue template. Include a concrete title, reproduction steps, expected and actual behavior, relevant version or commit and environment, and available evidence. Distinguish observed facts from suspected causes, and say when reproduction is intermittent or incomplete. Exclude secrets and private data from public evidence.
6. Continue testing and completing the original task. Include links to new and existing issues in the final report; do not fix unrelated bugs unless requested or necessary for the original task.

If filing fails, preserve the issue draft locally and report the blocker. If a creation response is uncertain, check whether the issue was created before retrying to avoid duplicates. This skill authorizes issue creation only, not unrelated comments, issue closure, or other external actions.
