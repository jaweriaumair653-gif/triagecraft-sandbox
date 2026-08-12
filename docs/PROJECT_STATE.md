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