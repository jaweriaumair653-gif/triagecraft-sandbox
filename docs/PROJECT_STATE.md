# TriageCraft — Project State

## Project

TriageCraft is a GitHub issue triage automation service.

Repository:

https://github.com/jaweriaumair653-gif/triagecraft-sandbox

Primary branch:

`main`

---

## Current Git State

Latest pushed commit:

`ee0906d chore: ignore local triagecraft config`

Previous important fix:

`c68f28b fix: use GitHub issue number for API actions`

Working tree status at the latest checkpoint:

- `main` is up to date with `origin/main`
- working tree is clean
- `.triagecraft.yml` is ignored by `.gitignore`

---

## Current Architecture

GitHub Issue
→ GitHub Webhook
→ Cloudflare Quick Tunnel
→ TriageCraft FastAPI server
→ Webhook parser
→ Issue normalization
→ Duplicate detection
→ Label suggestion
→ Decision engine
→ Action engine
→ GitHub API
→ Labels/comments/event recording

---

## Verified Working Components

### Webhook

GitHub issue webhooks successfully reach the application.

Verified response:

`HTTP 200 OK`

### Docker

TriageCraft runs successfully inside Docker.

Typical local mapping:

`localhost:8002 → container:8000`

### Cloudflare

Cloudflare Quick Tunnel successfully forwards public webhook traffic to:

`http://localhost:8002`

Important:

Quick Tunnel URLs are temporary and change when the tunnel is restarted.

### GitHub Authentication

A fine-grained GitHub Personal Access Token was created for the repository:

`jaweriaumair653-gif/triagecraft-sandbox`

Permissions used:

- Issues: Read and write
- Metadata: Read-only
- Repository access: Only `triagecraft-sandbox`

The token was verified inside the Docker container and successfully accessed the repository with:

`HTTP 200`

The actual token must never be committed to Git or shared in chat.

---

## Configuration

Local configuration file:

`.triagecraft.yml`

Important verified values:

```yaml
repository: jaweriaumair653-gif/triagecraft-sandbox
duplicate_threshold: 0.85
label_threshold: 0.10
summary_threshold: 0.70
dry_run: false
allowed_labels:
  - bug
  - feature
  - docs
  - question
  - needs-info
  ```


  ## CURRENT TEST STATUS

The full automated test suite is now green.

Latest verified result:

`61 passed in 5.42s`

The `Issue.number` migration is fully covered by updated regression tests.

Previously failing tests were updated to reflect the new GitHub issue model and webhook payload contract.

Current test status:

- All tests passing
- No known test failures
- Issue ID vs issue number regression covered

---

## LATEST DEVELOPMENT CHECKPOINT

Latest pushed commit:

`7b84881 test: update issue number expectations`

Previous commits:

`b0e0fc0 docs: add project state handoff`

`ee0906d chore: ignore local triagecraft config`

`c68f28b fix: use GitHub issue number for API actions`

Repository status at this checkpoint:

- `main` is synchronized with `origin/main`
- Working tree is clean
- Full test suite passes: `61 passed`

The GitHub issue-number migration is complete.

---

## CURRENT DEVELOPMENT PHASE

The MVP is functionally working and regression-tested.

Phase 1 — MVP functionality:

**COMPLETE**

Phase 2 — Regression protection:

**COMPLETE**

Current phase:

**Feature and reliability development**

Do not change the existing working GitHub webhook/action flow without preserving the current 61-test green baseline.

---

## NEXT PLANNED WORK

Before adding major features:

1. Review the existing architecture and test coverage.
2. Identify the highest-value reliability or functionality improvement.
3. Add/update tests before changing production behavior where practical.
4. Keep the full suite green.
5. Commit focused changes.
6. Push to `origin/main`.
7. Update this project-state document after major milestones.

---

## CURRENT KNOWN-GOOD BASELINE

The following behavior has been verified live:

GitHub Issue Created
→ Webhook received
→ Issue parsed
→ Issue normalized
→ Duplicate detection
→ Label suggestions
→ Decision engine
→ GitHub labels applied
→ GitHub comment posted
→ Event recorded
→ HTTP 200

Observed successful result:

`comment_posted=True`

`labels_applied=True`

The system should continue to preserve this behavior.