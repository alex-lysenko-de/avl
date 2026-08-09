# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository currently contains only `readme.md` (a Russian-language specification/architecture document) and no source code, no commits, and no build tooling yet. There are no build, lint, or test commands to run because implementation has not started. When code is added, this file should be updated with the actual commands and any architectural learnings that aren't obvious from the code itself.

Treat `readme.md` as the authoritative project spec until real code and its own conventions exist — read it before proposing implementation choices, since it fixes several decisions (stack, deployment model, data boundaries) that should not be re-litigated without cause.

## What this project is

A local Windows application (or set of related Python applications) for working with Microsoft Word documents, PDFs, and client data. Core functions: filling Word templates, generating documents from data, PDF handling, a client/vehicle/inspection database, business-rule checks, and producing final documents. It starts as a single-user, single-machine, fully local app; a future move to a centralized DB/multi-user setup is anticipated but must not complicate the first version.

## Fixed technical baseline (from readme.md section 21)

| Purpose | Tool |
|---|---|
| Language | Python |
| GUI | PySide6 |
| Database | SQLite (file kept outside the app/source tree, e.g. `ClientApp/data/database.sqlite`) |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Word documents | python-docx |
| Testing | pytest |
| Env management | venv / uv |
| VCS / hosting | Git / GitHub |
| CI/CD | GitHub Actions |
| Packaging | PyInstaller or equivalent, producing one or more standalone `.exe` files |
| Initial install | separate Windows installer |
| Auto-update | a dedicated **Updater** executable (must be separate from the main app — a running exe cannot replace itself) |
| Ticket tracking | Trello |
| Backup / sync | Google Drive (prefer the synced desktop folder over implementing the Drive API directly) |

Specific libraries may be swapped later if technically justified, but deviating from this stack should be a deliberate, explained decision, not an incidental one.

## Non-negotiable constraints

- **Customer machine stays clean.** The customer must never need to install Python, Git, an IDE, a venv, Docker, a SQLite server, or build tools — only the packaged app and Microsoft Word. Any design that leaks a dev-tool dependency onto the customer machine is wrong.
- **`git push` is the delivery trigger.** The intended pipeline is push → GitHub Actions → install deps → run tests → build Windows app → package → publish artifact → available to customer. A failing test or build must never let a new version reach the customer.
- **The Updater is a separate executable** from the main application, by design (see readme.md section 8).
- **SQLite database file lives outside the Git repo and outside the packaged app directory**, kept under a `data/` (or similar) folder alongside the app, never committed. Personal/sensitive data (names, addresses, VINs, inspection results) must never enter the public GitHub repository.
- **Schema changes go through Alembic migrations only** — never hand-edit the SQLite schema. App updates must migrate the customer's existing database in place; they must never replace it with an empty one.
- **Backups are separate from version control.** GitHub is not used to store working SQLite backups; Google Drive (a synced folder) is the intended backup destination, not Git history.
- **Relational design, not a single flat table.** Anticipated entities: Client, Vehicle, Inspection, InspectionItem, InspectionResult, Document, with proper relationships, inspection history, repeat inspections, and integrity constraints.
- **Templates are separate from business logic.** Word templates are filled via placeholders or another controlled mechanism, not hardcoded alongside app code.
- **Don't build for the hypothetical future.** Section 24 of readme.md is explicit: keep the architecture as simple as the current single-user/single-machine stage requires, and don't add infrastructure "because it might be useful someday." At the same time, avoid choices that would force a full rewrite of business logic if/when the project moves to a centralized API + PostgreSQL model later.

## Roles in the intended AI-agent workflow (future, per readme.md section 19)

The developer plans to use Claude Code as the primary AI agent, eventually wired into Trello and GitHub, with three distinct roles:
- **Architect**: `ticket.txt` + clarifying info → `implementation_plan.md`
- **Coder**: `implementation_plan.md` → code + `implementation_report.md` + git commit
- **Reviewer**: `ticket.txt` + clarifying info + `implementation_plan.md` + `git diff` + `implementation_report.md` → code review

This isn't wired up yet, but favor technical choices that expose a usable API/CLI surface (over anything that would require a human-only GUI workflow), since ticket/PR automation is a stated goal.
