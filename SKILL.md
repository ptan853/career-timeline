---
name: career-vault-resume
description: Build and maintain a local career memory vault from resumes, notes, links, files, GitHub/project material, and job descriptions. Use when Codex needs to extract career events, store verified professional facts, create resume context for a target JD, or provide agent-readable user identity from a local vault.
---

# Career Vault Resume

Use this skill to maintain a local, portable career memory that agents can share.
The vault stores source material, career events, resume-safe claims, evidence,
and generated resume context. Prefer updating the vault before drafting resumes
or professional identity summaries.

## Core Rules

- Treat the vault as the user's professional source of truth.
- Never invent employers, dates, metrics, awards, degrees, or responsibilities.
- Preserve raw source material before extracting events.
- Write AI output as draft events, draft claims, or patch previews unless the
  user explicitly confirms the information.
- Prefer confirmed claims when generating resumes or agent identity summaries.
- Mark uncertain fields as `needs_review` instead of forcing a value.
- Keep facts language-neutral; localize only generated resume text.

## Vault Location

Default to the nearest `.career-vault/` directory. If none exists, use:

```text
~/.career-vault/
```

When working inside a project repo, ask before creating `.career-vault/` in that
repo unless the user explicitly wants the career memory versioned there.

## Workflow

1. Initialize or locate the vault.
2. Save user-provided material as a source.
3. Extract detailed career events from the source.
4. Add events with `status: draft` or `status: confirmed` depending on user
   confirmation.
5. Extract or update claims for each event.
6. Build `exports/agent_identity.md` when an agent needs user background.
7. Build `exports/resume_context.md` when a user provides a target JD.

## Data Model

Use these primary objects:

- `SourceMaterial`: raw text, file references, URLs, GitHub/project material,
  resume PDFs, job descriptions, and notes.
- `CareerEvent`: timeline unit such as work, internship, project, education,
  award, publication, certification, scholarship, startup, milestone, or custom.
- `Claim`: resume-safe fact derived from one event.
- `Evidence`: source reference that supports a claim.
- `ResumeContext`: selected events and claims for a target job description.

Events should be flexible. Do not force work -> project -> achievement nesting.
Use event relations such as `part_of`, `occurred_during`, `related_to`,
`led_to`, and `resulted_in` when hierarchy or linkage matters.

## Event Extraction Standard

When extracting from resumes, files, notes, or links, look for small, reusable
events. One internship may contain several project events, one project may
contain claims, and one award or paper should be its own event when useful for
resume generation.

Each event should include at least:

```yaml
title: Built AI Resume Generator
type: project
time:
  start: 2025-05
  end: 2025-08
  precision: month
```

Use optional fields when supported by the source:

```yaml
description: Built a LaTeX-template resume generation workflow with AI-assisted content rewriting.
role: Creator
organization: null
location: Remote
tags: [AI, resume, LaTeX]
details:
  tech_stack: Python, LaTeX, FastAPI
  achievement: Designed a reusable resume generation pipeline.
claims:
  - Designed a template-driven resume generation workflow.
sources:
  - sources/resume_20260404.pdf
visibility: private
status: draft
```

## Scripts

Use `scripts/career_vault.py` for deterministic file operations:

```bash
python scripts/career_vault.py init --vault ~/.career-vault
python scripts/career_vault.py add-source --vault ~/.career-vault --type note --title "Career note" --text "..."
python scripts/career_vault.py add-event --vault ~/.career-vault --title "Built AI Resume Generator" --type project --start 2025-05 --description "..."
python scripts/career_vault.py list-events --vault ~/.career-vault
python scripts/career_vault.py build-identity --vault ~/.career-vault
python scripts/career_vault.py build-resume-context --vault ~/.career-vault --jd path/to/jd.md
```

The script does not replace agent judgment. Use the script to create, validate,
list, and export vault files after extracting structured content.

## References

- Read `references/vault-format.md` before creating or modifying vault files.
- Read `references/extraction-guide.md` before extracting events from messy
  resumes, notes, links, or project material.
- Read `references/resume-context.md` before producing a targeted resume context
  from a JD.

## Output Expectations

When updating the vault, summarize:

- sources added
- events created or changed
- claims created or changed
- fields marked `needs_review`
- generated export paths

When generating resume context, explain which events/claims were selected and
which facts still need user confirmation.
