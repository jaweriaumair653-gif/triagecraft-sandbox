# TriageCraft - Workflow

## 1. Event Triggers

TriageCraft listens to the following GitHub events:

- issues.opened
- issues.edited
- pull_request.opened
- issue_comment.created only if needed later

## 2. Processing Pipeline

Event received → validate webhook → check repo config → normalize text → search similar issues → score duplicate likelihood → suggest labels → generate summary → decide whether to comment

## 3. Decision Rules

- If duplicate confidence is below threshold, do not mention duplicates.
- If label confidence is low, only suggest labels, never apply them.
- If issue is too short, ask for more information.
- If the bot already commented, do not comment again.

## 4. Confidence Thresholds

- Duplicate detection threshold: placeholder
- Label suggestion threshold: placeholder
- Summary generation threshold: placeholder

These thresholds will be tuned later.

## 5. Comment Policy

- One bot comment per event
- No spam
- No repeated messages
- Keep comments short and useful
- Use dry-run mode during development

## 6. Failure Handling

- Webhook invalid → reject
- Repository config missing → use safe defaults
- AI service fails → skip AI step and log error
- Database write fails → do not post public comment

## 7. Non-automation Rules

- Do not merge
- Do not close automatically
- Do not delete content
- Do not edit user code