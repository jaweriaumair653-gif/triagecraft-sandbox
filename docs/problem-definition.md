# TriageCraft — Problem Definition

## 1. Problem Statement

Open source maintainers receive hundreds of repetitive issues and pull requests.

Many issues are duplicates.

Many questions have already been answered.

Maintainers spend significant time labeling issues, explaining duplicate reports, summarizing discussions, and asking for missing information.

This repetitive work slows development and contributes to maintainer burnout.

## 2. Who is affected?

Open source maintainers

Project owners

Organizations

Developers contributing to projects

Communities managing large repositories

## 3. Current Manual Workflow

When a new issue arrives, the maintainer typically:

New Issue

↓

Read

↓

Search

↓

Compare

↓

Label

↓

Reply

↓

Close or Keep Open

The real manual process often looks like this:

Open issue

↓

Read title

↓

Read description

↓

Search previous issues

↓

Compare manually

↓

Assign labels

↓

Ask for logs

↓

Ask for reproduction steps

↓

Close duplicate

↓

Notify user

## 4. Pain Points

Finding duplicates takes 2–10 minutes.

Reading long discussions takes 5–20 minutes.

Applying labels is repetitive.

Explaining duplicate reports is repetitive.

Requesting missing information is repetitive.

## 5. What Should Not Be Automated

The bot should never:

Merge PRs automatically

Close issues without confidence

Ban users

Delete comments

Modify code

It should assist maintainers, not replace them.

## 6. MVP Scope

Feature 1: Duplicate detection

Feature 2: Label suggestion

Feature 3: Issue summary

Feature 4: Missing information detection

Nothing else.

## 7. Success Metrics

Duplicate detection accuracy: 85%

Label suggestion accuracy: 90%

Summary length: under 100 words

Average maintainer time saved: 70%

## 8. Future Features

Reviewer recommendation

Project analytics

Contributor ranking

Semantic repository search

Release note generation

Issue clustering