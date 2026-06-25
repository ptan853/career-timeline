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

For a simple basic resume, the CLI can also produce:

- `exports/basic_resume.json`
- `exports/basic_resume.md`
- `exports/basic_resume.html`

The basic resume is a conservative black-and-white fallback. It is not the
design-forward resume path.
By default, it uses confirmed events only. Draft or `needs_review` events should
be confirmed by the user before being used in a formal resume.

## Basic Resume Controls

Support user preferences for:

- language: `zh` or `en`
- page count: usually `1` or `2`
- optional photo/headshot inclusion

Photo is optional. If used, recommend JPG/PNG, square or 4:5, at least 600x600
px. The current CLI places the image in a fixed frame but does not crop or align
faces yet.

## Section Selection

Do not force every resume to use the same sections. Prefer these candidates,
then select, merge, rename, or omit sections based on the user's background, JD,
language, and page limit:

- Education
- Work Experience
- Internship Experience
- Projects
- Personal Projects & Open Source
- Skills
- Research
- Publications
- Awards
- Certifications
- Languages
- Summary

For Chinese resumes, localize section labels at output time, such as `教育背景`,
`工作经历`, `项目经历`, and `专业技能`.

## Rewrite Rules

When rewriting for a JD:

- Keep facts unchanged.
- Change emphasis, order, and language.
- Make bullets concise and evidence-aware.
- Localize to the requested language only at output time.
- Keep private events out of public resumes unless user allows them.
