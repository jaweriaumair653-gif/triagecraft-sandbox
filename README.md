# TriageCraft

TriageCraft is a GitHub App that reduces repetitive maintainer work by detecting duplicate issues, suggesting labels, summarizing long discussions, and highlighting missing information.

## Why this exists

Open-source maintainers spend a large amount of time on repetitive triage work:
- checking for duplicate issues
- assigning labels
- reading long comment threads
- asking for missing logs or reproduction steps
- replying to common questions

TriageCraft helps reduce that workload while keeping maintainers in control.

## What it does

- Detects possible duplicate issues
- Suggests labels such as bug, feature, docs, and question
- Summarizes long issue threads
- Detects missing information in new issues
- Works in dry-run mode for safe testing

## What it does not do

- It does not merge pull requests
- It does not close issues automatically without confidence
- It does not delete user content
- It does not modify code
- It does not replace maintainers

## Project status

TriageCraft is in early development.

Current focus:
- problem definition
- architecture design
- workflow design
- MVP planning

## Planned MVP

- GitHub App authentication
- Webhook event handling
- Duplicate detection
- Label suggestions
- Short issue summaries
- Repository config file
- Safe comment posting
- Dry-run mode

## Repository structure

- `docs/problem-definition.md` — problem statement and scope
- `docs/architecture.md` — system architecture
- `docs/workflow.md` — event and decision flow
- `docs/roadmap.md` — phased development plan

## Quick start

1. Copy `.env.example` to `.env`
2. Copy `.triagecraft.example.yml` to `.triagecraft.yml`
3. Edit `.env` and `.triagecraft.yml`
4. Install dependencies
5. Run the app

## Run locally

```powershell
python -m triagecraft

Required environment variables
TRIAGECRAFT_GITHUB_TOKEN
TRIAGECRAFT_CONFIG_PATH
TRIAGECRAFT_DB_PATH
TRIAGECRAFT_HOST
TRIAGECRAFT_PORT
TRIAGECRAFT_LOG_LEVEL

## Deployment notes

- `dry_run: true` is recommended while testing
- webhook signatures should use `webhook_secret`
- `TRIAGECRAFT_GITHUB_TOKEN` should be kept private
- the SQLite database file is created automatically if needed

## Contributing

Contributions will be welcomed after the MVP structure is finalized.

## License

See `LICENSE`.