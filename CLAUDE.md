# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

The application/project name is **avl_docs** (matches the GitHub repo `alex-lysenko-de/avl`, confirmed with the user). **`avl_docs` is not one monolithic app — it's a suite of roughly a dozen separate document-handling utility programs.** Each utility is its own subpackage under `avl_docs/<utility_name>/` (a single file, a few files, or a whole folder, depending on complexity), with its own `main.py` entry point, and — per readme.md section 6 — potentially its own packaged `.exe`. Shared code (config, version) lives in `avl_docs/core/`. Existing subpackages: `app/` (primary application, stub), `updater/` (update-mechanism support, stub), `demo/` (a Tkinter test utility used only to exercise the ticket workflow, unrelated to real business functionality). When adding a new utility, follow this same subpackage pattern rather than growing `app/` into a catch-all. No venv/CI/packaging exists yet; see `tickets/dashboard.yaml` for what's done vs pending.

Treat `readme.md` as the authoritative project spec, and `wiki/update_workflow.md` as the authoritative, more detailed and more current description of the build/release/update mechanism specifically — where the two disagree on build/release/update details, `update_workflow.md` wins (it was written later, deliberately superseding parts of `readme.md`'s sections 6–10 for the current development stage: no installer, no separate Updater.exe yet — see below). Read both before proposing implementation choices in that area.

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
| Packaging | PyInstaller (already installed on the dev machine, 6.12.0) |
| Initial install | manual, one-time, during active development (see `wiki/update_workflow.md`); a separate Windows installer (Inno Setup) is deferred until the app stabilizes — ticket 107 was cancelled for now on this basis |
| Auto-update | during active development: `deployment/update.bat` → `update.ps1`, pulling signed releases from **GitHub Releases** (public repo) — no separate Updater.exe yet. A dedicated Updater executable remains the intended long-term design once installer work resumes |
| Ticket tracking | Trello |
| Backup / sync | Google Drive (prefer the synced desktop folder over implementing the Drive API directly) |

Specific libraries may be swapped later if technically justified, but deviating from this stack should be a deliberate, explained decision, not an incidental one.

## Non-negotiable constraints

- **Customer machine stays clean.** The customer must never need to install Python, Git, an IDE, a venv, Docker, a SQLite server, or build tools — only the packaged app and Microsoft Word. Any design that leaks a dev-tool dependency onto the customer machine is wrong.
- **`git push` is the delivery trigger.** The intended pipeline is push → GitHub Actions → install deps → run tests → build Windows app → package → publish artifact → available to customer. A failing test or build must never let a new version reach the customer.
- **Update delivery, current stage:** `update.bat`/`update.ps1` download the latest **public** GitHub Release (app ZIP + `manifest.json` with a SHA-256), verify the checksum before touching anything, back up the SQLite database, stage-extract before replacing files, run the app in a `--migrate` mode to apply Alembic migrations, then relaunch — see `wiki/update_workflow.md` for the full sequence and rationale. A failed checksum/backup/migration must abort with `update = failed`, never a false "success". Long-term the plan reverts to a separate Updater executable (readme.md section 8); don't build toward that until told to.
- **Version has exactly one source of truth: `pyproject.toml`.** `version.txt`, `manifest.json`, the release ZIP name, and the GitHub Release tag are all derived from it at build time — never hand-edited independently.
- **The GitHub repo (`alex-lysenko-de/avl`) is intentionally public** so the customer machine can download releases with no GitHub account/token/CLI. This means secrets, customer data, and the working SQLite DB must never reach it — enforce via `.gitignore`, not vigilance alone.
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

## The `tickets/` folder

`tickets/` is a file-based ticket queue specifically for the AI agent (as opposed to Trello, which is for developer↔customer communication). Each ticket is a numbered folder, e.g. `tickets/101/`, containing `101.md` (the task text — kept current; rewrite it in place if a ticket's scope is substantively revised), `status.txt` (one of `NEW`, `IN_PROGRESS`, `DONE`, `CANCELLED`, and possibly a customer-waiting status analogous to Trello's `WAITING FOR CUSTOMER`), and optionally `readme.md` for supplementary notes (revision history, cancellation rationale) — create it only when there's real content, not as boilerplate. `tickets/dashboard.yaml` is a compact `id`/`title`/`status` list across all tickets, kept intentionally free of extra fields; update it whenever a ticket's `status.txt` changes — `status.txt` stays the source of truth per ticket, the dashboard is a synced aggregate view. Full structure notes: [[Папка tickets]] in the wiki.

Rules for working a ticket (from `tickets/readme.md`, authoritative — mirrored here because that file requires it):

1. **Don't start drafting requirements if the ticket is ambiguous.** First assess whether there's enough information to implement it.
2. **If information is insufficient**, ask only clarifying questions that actually affect the implementation — never ask for the sake of asking. If multiple implementation approaches exist, list them and ask the user to pick one.
3. **Never make significant assumptions unilaterally.** Anything that could affect the implementation must be confirmed with the user first.
4. **Always split findings into four categories**: confirmed requirements, assumptions, open questions, recommendations (if any).
5. **Clarifying questions must be answerable by voice or a short keyboard reply.** Give each question an id (`[Q1]`, `[Q2]`…) and each answer option an id (`[v1]`, `[v2]`, `[y/n]`), so the user can reply with something like "Question 1, option 2" (voice) or `Q1v2 Q3y Q4:free text` (keyboard) instead of repeating the full question. Mark the recommended option explicitly.

When a ticket is fully completed, update its `status.txt` to `DONE` (or the appropriate closed state) as part of finishing the work — don't leave completed tickets `IN_PROGRESS`.
