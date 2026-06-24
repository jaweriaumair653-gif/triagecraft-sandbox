# TriageCraft — System Design

## 1. Core Objects

### Issue
- id
- repository
- title
- body
- author
- labels
- created_at

### NormalizedIssue
- clean_title
- clean_body
- tokens
- embedding (optional)

### DuplicateResult
- confidence
- matched_issue_id
- reason

### LabelSuggestion
- label
- confidence

### Summary
- text
- length

### BotDecision
- should_comment
- should_label
- should_request_info
- should_skip

---

## 2. Processing Flow

GitHub

↓

Webhook

↓

Validation

↓

Normalization

↓

Duplicate Detector

↓

Label Suggester

↓

Summarizer

↓

Decision Engine

↓

GitHub API Response

---

## 3. Design Rules

- Every class will be designed before implementation.
- Every function will have a single responsibility.
- Every module will have one purpose.
- Every commit will be meaningful.
- Every test will exist before production features are considered complete.