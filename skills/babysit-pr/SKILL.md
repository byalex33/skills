---
name: babysit-pr
description: Get a PR ready to merge. Use when asked to babysit, watch, or follow a PR.
---

# Babysit PR

Get the selected PR ready to merge by fixing conflicts, CI failures, and worthwhile AI review findings. Commit and push the necessary fixes, then follow the next round of checks through to completion. Do not merge the PR unless the user asks.

## Select the PR

- If the user specifies a PR, use that one, even if the current branch has another PR.
- Otherwise, use the open remote PR associated with the current branch.
- If no PR can be identified uniquely, ask for its URL or number.

Confirm the repository, PR head branch and commit, and target branch. Work on the selected PR's branch; preserve unrelated local changes and use an isolated checkout when necessary.

## Watch, fix, and repeat

1. Read the PR diff and repository instructions. Fetch the latest head and target branches and check for merge conflicts. Resolve conflicts locally in line with repository conventions, preserving both sides' intended behavior.
2. Inspect CI checks and every configured AI code review bot. Fetch full failing-job logs, check annotations, review bodies, inline review threads, and bot comments, including all pages. A green CI summary alone does not establish that bot reviews have finished.
3. Assess each finding against the actual code and its callers. Fix real defects and useful, in-scope improvements. Skip false positives, duplicates, obsolete findings, and changes whose cost exceeds their value. Keep a brief reason for each skipped finding; do not implement suggestions merely to satisfy a bot.
4. Make the necessary fixes locally, run appropriate focused validation, commit only the intended changes, and push to the PR's head branch. A babysitting request authorizes these ordinary fixes, commits, and pushes. Preserve others' commits; prefer a normal push and avoid rewriting published history unless separately authorized.
5. After each push, track the new remote head commit and wait for CI and bot reviews to run again. Re-fetch findings and repeat the fix cycle as needed. Treat old approvals and checks as historical evidence, not proof that the new commit passed. If another contributor updates the PR, incorporate their changes and reassess.
6. Poll with bounded waits and back off when nothing changes. For background follow-up, use the available native thread heartbeat or automation facility, saving the PR identity and outstanding work. Stay quiet on unchanged scheduled runs and notify on meaningful changes, completion, failure, or required user action. Do not claim monitoring will continue unless a follow-up was actually scheduled.

Retry a failed check when evidence suggests a transient failure; do not repeatedly rerun an unchanged deterministic failure. If progress requires unavailable credentials, infrastructure repair, human approval, or an unresolvable product decision, report the concrete blocker and the next action. Stop if the PR is closed or merged. Never bypass checks or weaken branch protections to manufacture success.

## Completion

Before declaring success, freshly verify that:

- The latest PR head has no merge conflicts with the current target branch.
- CI checks are green and no required check is missing, pending, or failing.
- All configured AI review bots have finished successfully, with every finding either implemented or deliberately skipped with a reason.

If a skipped finding leaves a bot check red or its review blocking, report that remaining blocker rather than calling the PR green. Missing, inaccessible, or stale results are not passing results.

Give the user the PR link, a concise summary of fixes made, any skipped findings and reasons, and a concise list of what the complete PR actually does based on its final diff. Include the verified check and conflict status, or any remaining blocker.

## Extra review

If the user asks for an extra review from you, use a subagent to review the PR. Give it the PR diff and relevant repository context. Treat its findings like another AI review bot's findings: assess, fix or skip, validate, commit, push, and repeat the checks above. If subagents are unavailable, disclose that limitation.
