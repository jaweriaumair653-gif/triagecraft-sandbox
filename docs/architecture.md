# TriageCraft - System Design (v0.1)

## 1. Goal

TriageCraft is an AI-powered GitHub maintainer assistant designed to reduce repetitive maintenance work in open-source repositories. The system helps maintainers by automatically detecting duplicate issues, suggesting labels, generating concise issue summaries, and identifying missing information required for issue triage. The objective is to save maintainer time, improve issue management efficiency, and reduce burnout while keeping humans fully in control of repository decisions.

---

## 2. Non-Goals

TriageCraft must not perform any actions that can negatively impact a repository without explicit maintainer review.

The system will not:

* Merge pull requests automatically
* Close issues automatically without sufficient confidence
* Delete comments or user-generated content
* Modify repository code
* Ban users
* Change repository settings
* Perform destructive actions

The bot is designed to assist maintainers, not replace them.

---

## 3. Main Components

### GitHub App

The GitHub App serves as the integration layer between GitHub and TriageCraft.

Responsibilities:

* Receive repository installation events
* Subscribe to issue-related events
* Authenticate with GitHub APIs
* Post comments and suggestions
* Read repository metadata

---

### Webhook Receiver

The Webhook Receiver acts as the entry point for all GitHub events.

Responsibilities:

* Receive GitHub webhook payloads
* Validate webhook signatures
* Verify event authenticity
* Prevent duplicate event processing
* Forward valid events to the Triage Engine

---

### Triage Engine

The Triage Engine is the core intelligence layer of the system.

Responsibilities:

* Normalize issue content
* Detect duplicate issues
* Suggest issue labels
* Generate issue summaries
* Detect missing information
* Produce maintainer recommendations

---

### Storage Layer

The Storage Layer stores operational and configuration data required by the platform.

Responsibilities:

* Repository configuration storage
* Event tracking
* Duplicate issue fingerprints
* Generated summaries
* Label recommendation history
* Processing logs

---

## 4. Data Flow

The issue processing pipeline follows this sequence:

New Issue

↓

GitHub Webhook Event

↓

Webhook Receiver

↓

Signature Validation

↓

Normalize Text

↓

Duplicate Detection

↓

Label Suggestion

↓

Summary Generation

↓

Missing Information Detection

↓

Recommendation Assembly

↓

GitHub Comment

↓

Maintainer Review

---

## 5. Storage

The system will store the following data:

### Repository Configuration

Stores repository-specific settings.

Examples:

* Enabled features
* Confidence thresholds
* Label mappings
* Dry-run configuration

### Issue Fingerprints

Stores issue embeddings and similarity fingerprints used for duplicate detection.

### Processed Event IDs

Stores previously processed GitHub event IDs to prevent duplicate execution.

### Summaries

Stores generated issue summaries for future reference and auditing.

### Label Decisions

Stores suggested labels and final maintainer decisions for future model improvement.

---

## 6. Safety Rules

The system must follow these safety requirements at all times.

### Rule 1

Never spam repository comments.

### Rule 2

Never perform the same action twice on the same issue.

### Rule 3

Never act below the configured confidence threshold.

### Rule 4

Always support dry-run mode.

### Rule 5

Always allow maintainers to override recommendations.

### Rule 6

Maintain complete auditability of generated actions.

---

## 7. MVP Architecture (v0.1)

Version 0.1 will only support the following capabilities:

### Feature 1

Duplicate Detection

Identify previously reported issues using semantic similarity techniques.

### Feature 2

Label Suggestions

Recommend labels based on issue content and repository conventions.

### Feature 3

Summary Comment

Generate concise issue summaries for maintainers.

### Feature 4

Configuration File

Support repository-level configuration through a project configuration file.

### Feature 5

Safe Webhook Handling

Receive, validate, and process GitHub events securely and reliably.

---

## Out of Scope for v0.1

The following features are intentionally excluded from the first release:

* Reviewer recommendation
* Pull request analysis
* Automatic issue closure
* Repository analytics
* Contributor ranking
* Release note generation
* Issue clustering
* Semantic repository search

These features may be considered in future versions after the MVP has been validated.
