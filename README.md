# Career Vault Resume

Career Vault Resume is a local-first skill and file format for building a
portable career memory from resumes, notes, links, project material, and job
descriptions.

The goal is not to make users fill out another resume form. The goal is to let
an agent carefully extract detailed career events from messy material, save them
in a local vault, and reuse the verified facts for resumes, job applications,
interviews, portfolios, and agent identity.

## What It Does

- Stores raw sources such as resumes, notes, PDFs, links, GitHub summaries, and
  job descriptions.
- Extracts small, reusable career events from those sources.
- Stores resume-safe claims and evidence.
- Exports an agent-readable identity summary.
- Builds target-job resume context from the local vault.
- Keeps data in portable files that can be committed to Git or moved across
  machines.

## Repository Layout

```text
career-vault-resume/
  SKILL.md
  README.md
  scripts/
    career_vault.py
  references/
    vault-format.md
    extraction-guide.md
    resume-context.md
  schemas/
    career-event.schema.json
    source-material.schema.json
    claim.schema.json
    vault-profile.schema.json
  assets/
    templates/
      markdown/
        resume_context.md
  examples/
    sample_vault/
```

## Quick Start

Initialize a vault:

```bash
python scripts/career_vault.py init --vault ~/.career-vault
```

Add a source note:

```bash
python scripts/career_vault.py add-source \
  --vault ~/.career-vault \
  --type note \
  --title "Initial career note" \
  --text "I built a LaTeX resume generator and explored AI rewriting for job-specific resumes."
```

Add an event:

```bash
python scripts/career_vault.py add-event \
  --vault ~/.career-vault \
  --title "Built AI Resume Generator" \
  --type project \
  --start 2025-05 \
  --description "Built a template-driven resume generation workflow with AI-assisted rewriting."
```

Build an agent identity summary:

```bash
python scripts/career_vault.py build-identity --vault ~/.career-vault
```

Build resume context for a job description:

```bash
python scripts/career_vault.py build-resume-context --vault ~/.career-vault --jd jd.md
```

## Data Storage

The default vault is a directory:

```text
.career-vault/
  profile.yaml
  events/
  claims/
  sources/
  resumes/
  exports/
```

MVP storage uses human-readable files so users can inspect, migrate, and version
their career memory. A future app can index the same files into SQLite or a
vector store without changing the source of truth.

## Status

This is an early skill-first MVP. It provides the shared data structure and
deterministic file operations. AI extraction should be performed by the host
agent using the instructions in `SKILL.md` and `references/`.
