# Self-Service Email Account Migration for KEEPER

**Status:** Design Phase  
**Owner:** Keeper Team  
**Related:** MaxIT Email Migration  
**Target Repo for PR:** https://github.com/MPDL/KEEPER  
**Workspace:** `keeper-email-migration` (this repo)

---

## 1. Executive Summary

This design introduces a **self-service** flow that allows KEEPER users to initiate the migration of their account data from an old email identity to a new email identity (driven by the MaxIT institutional email migration).

The flow follows the proven safety model of the existing `migrate_account.py` pipeline while removing the need for manual coordination by the Keeper Team / IT Operations for every individual migration.

**Core principle:** The user experience should feel as simple and safe as "moving an app from one phone to another."

**Key constraints (decided):**
- Migration table lives in the **keeper-db** (via the existing `DbRouter`).
- The secret codes (called "code" or "move code" to users) are valid for **7 days** and **regenerate is supported**.
- Users **cannot cancel** pending moves.
- Notifications: **Email + in-app** (where feasible).
- The heavy migration **pipeline stays exactly as-is** on the automation host. All operational scripts live in `/opt/seafile/scripts/migration/`. A periodic worker (`process_keeper_email_migrations.py`) polls the database and executes the existing `migrate_account.py` via subprocess.
- UI and all user-facing text: **English only**.

---

## 2. Goals & Non-Goals

### Goals
- Dramatically reduce operational load on the Keeper Team during the email migration waves.
- Give users control and visibility ("I can start this when I'm ready").
- Maintain or improve safety compared to the current operator-driven process.
- Preserve every existing guarantee (library ownership, folder-level shares, group admin roles, password continuity, Keeper-specific DB migration, session invalidation, source deactivation).
- Produce a clean, reviewable contribution to the upstream MPDL/KEEPER repository.

### Non-Goals (for v1)
- Moving the core migration pipeline logic into the web application.
- German localization.
- Allowing users to cancel pending migrations.
- Full self-service for bulk/department migrations (CLI bulk runner remains for ops).

---

## 3. User Experience (The "Phone Move" Flow)

### Landing Page
**Recommended URL:** `/account/migrate/` (or `/migration/`)

The page is deliberately **context-aware** based on the currently authenticated user.

#### 3.1 When logged in with the **source** (old) account
- Prominent banner (red/orange treatment):  
  **"You are currently logged in as: `old@olddomain` — This is the SOURCE account"**
- Clear explanation of what will be transferred.
- Strong warning box: "After successful migration this account will be **deactivated** and become permanently unusable for logging in or accessing data."
- Primary action: **"Get the code for the move"** (big button).
- After generation: The code is shown + emailed with full link. "Your move code: ... This code will stop working after ... Go to the migration page (link) ... Check the big box at the top. It must say ... (TARGET ACCOUNT). If wrong, log out, log in with the new email..."
- Regenerate supported.

#### 3.2 When logged in with the **target** (new) account
- Prominent banner (green/blue treatment):  
  **"You are currently logged in as: `new@newdomain` — This is the TARGET account"**
- Paste code field (label: "Paste the code from the email").
- On successful validation: Confirmation screen (with banner check reminder) with:
  - Exact before/after.
  - Irreversible warning list.
  - Checkboxes in plain language: "I understand that my old email will stop working..."
  - "I understand I must set up all my apps..."
  - "I have my encrypted library passwords ready..."
- Button: **"I have read and understood — Yes, move my stuff now"**.

#### 3.3 Post-Confirmation / Status View
- Both can return (via link in email or directly) and see current state on screen (with big banner reminder to check account):
  - Waiting to start → "We have your move ready. It will begin soon. Look here later for news..."
  - Moving your files now
  - Done → "Done! Your files are now with the new email..."
  - Had a problem → "Something went wrong..." + contact
- No ability for users to cancel.

**Visual & Branding Requirements**
- 100% visual consistency with existing KEEPER theme (logo, colors, typography, footer).
- Uses the same custom CSS and template overrides already present in `seahub-data/custom/`.
- Extremely clear "which account am I using right now?" messaging (big box with SOURCE/TARGET) on every screen + explicit "check the box, logout/login if wrong" instructions in emails and on screens to prevent mistakes.

---

## 4. Technical Architecture

### 4.1 Database

**Table:** `keeper_email_migration` (in the **keeper** database)

```sql
CREATE TABLE keeper_email_migration (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_email VARCHAR(255) NOT NULL,
    target_email VARCHAR(255) NOT NULL,
    migration_token CHAR(64) NOT NULL,           -- the secret "code" shown to user (plain language in UI/emails)
    token_expires_at DATETIME NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'failed') DEFAULT 'pending',
    requested_at DATETIME NOT NULL,
    confirmed_at DATETIME NULL,
    completed_at DATETIME NULL,
    error_message TEXT NULL,
    metadata JSON NULL,                          -- shares captured, logs, etc.
    UNIQUE KEY uniq_active_pair (source_email, target_email, status)  -- prevent duplicates while active
);
```

- Use the existing `keeper` database + `DbRouter` (see `keeper/dbrouter.py` and `keeper-db.sql` pattern).
- The table definition is committed directly to `seafile_keeper_ext/seafile-server-latest/seahub/keeper/keeper-db.sql`.
- A standalone copy `create_keeper_email_migration_table.sql` is provided in `opt/seafile/scripts/migration/` for ops teams deploying the worker on existing systems.

### 4.2 Backend Code Location

New package following the established pattern:

```
seafile_keeper_ext/seafile-server-latest/seahub/keeper/migration/
```

- `models.py`
- `views.py`
- `forms.py`
- `utils.py` (token generation, validation, status helpers)
- `admin.py` (for operator visibility)

### 4.3 Execution Model (Critical Decision)

**The migration pipeline stays on the automation host.** All scripts are consolidated under `/opt/seafile/scripts/migration/`.

- A new periodic script (or management command run via cron/systemd timer on `automation-keeper.mpdl.mpg.de`) polls for rows with `status = 'pending'`.
- It calls the (refactored) logic currently in `migrate_account.py` / `seafile_common.py`.
- On start → set `in_progress`.
- On success → `completed`, send notifications.
- On failure → `failed`, store error, send notifications.
- The web application only creates and observes requests. It never executes the heavy migration.

This decision preserves all current operational safety, SSH access patterns, and privileged DB operations.

### 4.4 Notifications

- **Email** (primary): Use existing Seafile/KEEPER email infrastructure. All user emails use very plain language ("move your Keeper files", "check the big box at the top for (SOURCE or TARGET ACCOUNT)", "log out and log in with the correct email if the box is wrong", full links, direct status link).
  - On code generation (to source, with instructions for target).
  - On confirmation (to both).
  - On completion or problem (from worker, with link).
- **In-app** (secondary): Where easy (e.g., system notification or a simple banner on login for the target user).

### 4.5 Code Rules (plain language "code" or "move code" to users)

- 7-day lifetime from generation time.
- Support "Regenerate" (invalidates previous, issues a new one with fresh 7-day window).
- The code must be single-use for claiming.
- Strongly bound to the specific `(source_email, target_email)` pair at generation time.

---

## 5. Security & Safety Controls

1. All pages require authentication.
2. Token generation is only allowed while authenticated as the **source**.
3. Token claiming/confirmation is only allowed while authenticated as the **target**.
4. Extremely prominent, always-visible "Current Session Identity + Role (Source/Target)" indicator.
5. Multi-step confirmation with explicit irreversible-action acknowledgment on the target side.
6. Cryptographically secure random tokens (minimum 32 bytes).
7. Full audit trail in the database + Django admin logging.
8. Rate limiting on token generation and claim attempts.
9. No self-migration (source == target blocked).
10. Source account must be active at the time of claim.

---

## 6. Files Expected in the PR to MPDL/KEEPER

### New Files
- `seafile_keeper_ext/seafile-server-latest/seahub/keeper/migration/__init__.py`
- `.../models.py`
- `.../views.py`
- `.../forms.py`
- `.../utils.py`
- `.../admin.py`
- `seahub-data/custom/templates/keeper/migration/base.html`
- `.../landing.html`
- `.../confirm.html`
- `.../status.html`
- Worker script skeleton at `/opt/seafile/scripts/migration/process_keeper_email_migrations.py` (ops side, not in the web PR)
- `docs/email-migration-self-service.md` (or update existing docs)

### Modified Files
- `seafile_keeper_ext/seafile-server-latest/seahub/keeper/keeper-db.sql` (table added directly)
- Management command `list_migration_requests` for admins (in keeper/management/commands/)
- Worker CLI `--list-pending` for manual ops (in process_keeper_email_migrations.py). Includes run_migration_worker.sh wrapper.
- Custom CSS keeper-migration.css for the migration UI pages.
- `seafile_keeper_ext/seafile-server-latest/seahub/keeper/urls.py` (route registration)
- `seafile_keeper_ext/conf/seahub_settings.py` (no new settings required; all values have built-in defaults in the migration code. We might expose KEEPER_MIGRATION_* keys here for configuration later, as noted in the code comments and integration notes.)
- Possibly small additions to `keeper/utils.py` or `common.py`

### Supporting (in this workspace or automation repo)
- Refactored reusable migration functions (extracted from current `migrate_account.py`).
- The periodic worker script (`scripts/process_email_migrations.py`).

---

## 7. Implementation Phases

**Phase 0 – Preparation (MINIMAL – low risk)**
- **Do NOT refactor** `migrate_account.py` or `seafile_common.py`. These scripts continue to run exactly as they do today on the background/automation server.
- Create the **minimal cron worker** at `/opt/seafile/scripts/migration/process_keeper_email_migrations.py` that:
  - Polls the new `keeper_email_migration` table for `pending` rows.
  - Invokes the **existing** `migrate_account.py --from X --to Y` via subprocess (exactly like `bulk_migrate.py` does today).
  - Records success/failure + log location back into the DB row.
- Create this design document and get agreement on all decisions.

**Phase 1 – Data Model + Admin** (done)
- Table committed directly to `keeper-db.sql`.
- Django model + full admin registration (search, filters, mark failed action).

**Phase 2 – Source-Side Flow** (core done)
- Landing page for source users (generate + regenerate token).
- Strong "current logged in as SOURCE" banner.
- Basic rate limiting and validation.

**Phase 3 – Target-Side Flow + Confirmation** (core done)
- Paste + validation (as target).
- Strong multi-step confirmation with multiple required checkboxes + irreversible warnings.
- Status page.

**Phase 4 – Worker Integration + Notifications** (worker ready, notifications stub)
- The worker is production-oriented (lock, stuck recovery, manual-friendly).
- Notification hook present (can be wired to real emails later; user runs table create manually).
- End-to-end path from UI request → worker processing the existing migrate_account logic.

**Phase 5 – Hardening & Documentation** (complete)
- Basic rate limiting in UI (per-user, 60s cooldown on generate/claim using session).
- Updated SOP for self-service (including merged user instructions in the legacy SOP).
- Integration notes + PR description + dedicated STEP1 integration checklist.
- Templates include clear integration comments for real KEEPER base + CSS.
- Full visual match and URL wiring documented as post-PR deployment steps (see local KEEPER_Integration_Notes.md / STEP1 in pilot materials; removed from proposed-pr/ per request).

---

## 8. Open Questions / Follow-ups (post-PR / during pilot)

- Preferred support contact email shown on failure (can be adjusted in the code).
- Whether to show a global banner or help center link promoting the new self-service page during active migration waves (example banner text is provided).
- Monitoring/alerting thresholds for stuck `in_progress` items (basic recovery exists in the worker).
- Exact visual/CSS polish once applied to real KEEPER base (templates are ready with comments).

---

## 9. Success Criteria

- A user can successfully complete the full source → generate token → target → paste → confirm flow without assistance.
- The worker processes requests using the existing migrate_account.py logic (no refactoring).
- Ops can list pending via --list-pending or the Django command.
- The UI is styled to match KEEPER (via custom CSS and base).
- Table creation is straightforward (manual SQL or via keeper-db.sql in redeploy).
- Everything deploys via standard KEEPER mechanisms (scripts/ and seahub-data for UI).
- The background worker correctly picks up the request and executes the existing proven migration logic.
- No regressions in data integrity, sharing permissions, or deactivation behavior.
- The feature is delivered as a clean, documented PR to the MPDL/KEEPER repository.

---

**Document Version:** 1.2  
**Last Updated:** 2026-06 (post-implementation, wording finalized)

**Decisions captured from stakeholder (confirmed):**

- Migration table: **keeper-db** (via existing `DbRouter`)
- Code lifetime: **7 days**, **regenerate supported** (user-facing term: "migration code")
- User cancellation: **Not allowed**
- Notifications: **Email + in-app** (where practical; plain language)
- Execution model: Heavy pipeline **stays on automation host**; background worker polls DB periodically
- Localization: **English only**

This document should be included (or lightly adapted) as part of the PR to https://github.com/MPDL/KEEPER.

---

## Appendix: Workspace

This design was developed in the `keeper-email-migration` workspace together with starter files under `proposed-pr/`. The `proposed-pr/` tree (plus the updated real SOP and STEP checklists in the companion ops dir) is the complete deliverable for the PR to https://github.com/MPDL/KEEPER. See the workspace root README.md for the current status and remaining pilot/deployment steps.