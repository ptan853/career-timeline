# Resume Context Generation

Use this guide when the user provides a job description and asks for a targeted
resume, resume bullets, cover letter context, or interview preparation.

## Inputs

- Target job description
- Confirmed or draft career events
- Confirmed or review-needed claims
- User preferences and target locale
- Template constraints if provided

## Selection Rules

- Prefer confirmed claims.
- Include draft or `needs_review` claims only if clearly marked.
- Select events by relevance to responsibilities, required skills, domain, and
  seniority.
- Do not fabricate missing metrics or technologies.
- Preserve user truth over JD keyword matching.

## Output Sections

Produce `exports/resume_context.md` with:

- target job summary
- selected events
- selected claims
- missing information questions
- suggested resume angle
- risk notes for unsupported facts

## Rewrite Rules

When rewriting for a JD:

- Keep facts unchanged.
- Change emphasis, order, and language.
- Make bullets concise and evidence-aware.
- Localize to the requested language only at output time.
- Keep private events out of public resumes unless user allows them.
