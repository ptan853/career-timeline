#!/usr/bin/env python3
"""Small file-based CLI for Career Vault Resume.

The script intentionally uses only the Python standard library so it can run in
most agent environments without installing dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_TYPES = {
    "work",
    "internship",
    "project",
    "education",
    "research",
    "publication",
    "award",
    "scholarship",
    "certification",
    "course",
    "competition",
    "open_source",
    "volunteer",
    "startup",
    "milestone",
    "custom",
}

EVENT_STATUSES = {"draft", "confirmed", "needs_review", "archived"}
VISIBILITIES = {"private", "resume", "public"}
SOURCE_TYPES = {"note", "resume", "file", "url", "github", "jd", "agent_session"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:48] or fallback


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def vault_path(args: argparse.Namespace) -> Path:
    if args.vault:
        return Path(args.vault).expanduser().resolve()
    return Path.home() / ".career-vault"


def ensure_vault(vault: Path) -> None:
    for dirname in ("events", "claims", "sources", "resumes", "exports"):
        (vault / dirname).mkdir(parents=True, exist_ok=True)
    profile = vault / "profile.yaml"
    if not profile.exists():
        profile.write_text(
            "\n".join(
                [
                    "schema_version: 1",
                    "user:",
                    '  display_name: ""',
                    '  headline: ""',
                    "  default_locale: en",
                    "  target_roles: []",
                    "privacy:",
                    "  default_visibility: private",
                    "  public_summary_allowed: false",
                    "",
                ]
            ),
            encoding="utf-8",
        )


def parse_kv(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Expected KEY=VALUE, got: {value}")
        key, raw = value.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Empty key in detail: {value}")
        parsed[key] = raw.strip()
    return parsed


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text:
        return '""'
    if re.fullmatch(r"[A-Za-z0-9_./:@+-]+", text) and text not in {"null", "true", "false"}:
        return text
    return json.dumps(text, ensure_ascii=False)


def yaml_block(data: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(yaml_block(value, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
        return lines
    if isinstance(data, list):
        lines = []
        if not data:
            return [f"{prefix}[]"]
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(yaml_block(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return lines
    return [f"{prefix}{yaml_scalar(data)}"]


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text("\n".join(yaml_block(data)) + "\n", encoding="utf-8")


def read_event(path: Path) -> dict[str, Any]:
    # Event files are written as YAML-like JSON-compatible scalars. For robust
    # export without a YAML dependency, keep a hidden JSON copy next to each file.
    json_path = path.with_suffix(".json")
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return {"id": path.stem, "title": path.stem, "status": "needs_review"}


def write_event(vault: Path, event: dict[str, Any]) -> Path:
    event_id = event["id"]
    yaml_path = vault / "events" / f"{event_id}.yaml"
    json_path = vault / "events" / f"{event_id}.json"
    write_yaml(yaml_path, event)
    json_path.write_text(json.dumps(event, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return yaml_path


def command_init(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    print(f"Initialized career vault: {vault}")


def command_add_source(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    source_id = f"src_{compact_timestamp()}_{slugify(args.title, 'source')}"
    source_path = vault / "sources" / f"{source_id}.md"
    if args.file:
        original = Path(args.file).expanduser().resolve()
        if not original.exists():
            raise SystemExit(f"Source file does not exist: {original}")
        stored = vault / "sources" / f"{source_id}{original.suffix}"
        shutil.copy2(original, stored)
        body = f"# {args.title}\n\nSource type: {args.type}\nOriginal file: {original}\nStored file: {stored.name}\n"
    elif args.url:
        body = f"# {args.title}\n\nSource type: {args.type}\nURL: {args.url}\n\n"
    else:
        body = f"# {args.title}\n\nSource type: {args.type}\n\n{args.text or ''}\n"
    source_path.write_text(body, encoding="utf-8")
    print(source_path)


def command_add_event(args: argparse.Namespace) -> None:
    if args.type not in EVENT_TYPES:
        raise SystemExit(f"Unsupported event type: {args.type}")
    if args.status not in EVENT_STATUSES:
        raise SystemExit(f"Unsupported status: {args.status}")
    if args.visibility not in VISIBILITIES:
        raise SystemExit(f"Unsupported visibility: {args.visibility}")
    vault = vault_path(args)
    ensure_vault(vault)
    event_id = args.id or f"evt_{compact_timestamp()}_{slugify(args.title, 'event')}"
    event = {
        "schema_version": 1,
        "id": event_id,
        "title": args.title,
        "type": args.type,
        "custom_type": args.custom_type,
        "time": {
            "start": args.start,
            "end": args.end,
            "precision": args.precision,
        },
        "status": args.status,
        "description": args.description or "",
        "role": args.role,
        "organization": args.organization,
        "location": args.location,
        "tags": args.tag,
        "details": parse_kv(args.detail),
        "claims": args.claim,
        "sources": args.source,
        "relations": [],
        "visibility": args.visibility,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    path = write_event(vault, event)
    print(path)


def command_list_events(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    events = [read_event(path) for path in sorted((vault / "events").glob("evt_*.yaml"))]
    if args.json:
        print(json.dumps(events, indent=2, ensure_ascii=False))
        return
    for event in events:
        time = event.get("time", {})
        start = time.get("start") or "unknown"
        end = time.get("end") or ""
        span = f"{start}..{end}" if end else start
        print(f"{event.get('id')} | {span} | {event.get('type')} | {event.get('status')} | {event.get('title')}")


def load_events(vault: Path) -> list[dict[str, Any]]:
    return [read_event(path) for path in sorted((vault / "events").glob("evt_*.yaml"))]


def command_build_identity(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    events = load_events(vault)
    confirmed = [event for event in events if event.get("status") == "confirmed"]
    draft = [event for event in events if event.get("status") != "confirmed"]
    lines = [
        "# Agent Identity",
        "",
        "This file is generated from the local career vault. Treat it as context, not as permission to invent facts.",
        "",
        "## Confirmed Career Events",
        "",
    ]
    for event in confirmed:
        lines.extend(format_event_markdown(event))
    if not confirmed:
        lines.append("No confirmed events yet.")
    lines.extend(["", "## Draft Or Review-Needed Events", ""])
    for event in draft:
        lines.extend(format_event_markdown(event))
    if not draft:
        lines.append("No draft events.")
    output = vault / "exports" / "agent_identity.md"
    output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(output)


def format_event_markdown(event: dict[str, Any]) -> list[str]:
    time = event.get("time", {})
    span = time.get("start") or "unknown"
    if time.get("end"):
        span = f"{span} to {time['end']}"
    lines = [
        f"### {event.get('title', event.get('id'))}",
        "",
        f"- Type: {event.get('type')}",
        f"- Time: {span}",
        f"- Status: {event.get('status')}",
    ]
    if event.get("role"):
        lines.append(f"- Role: {event['role']}")
    if event.get("organization"):
        lines.append(f"- Organization: {event['organization']}")
    if event.get("description"):
        lines.extend(["", event["description"]])
    claims = event.get("claims") or []
    if claims:
        lines.extend(["", "Claims:"])
        lines.extend([f"- {claim}" for claim in claims])
    lines.append("")
    return lines


def command_build_resume_context(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    jd_path = Path(args.jd).expanduser().resolve()
    if not jd_path.exists():
        raise SystemExit(f"JD file does not exist: {jd_path}")
    jd_text = jd_path.read_text(encoding="utf-8", errors="replace")
    events = load_events(vault)
    keywords = set(re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", jd_text.lower()))

    def score(event: dict[str, Any]) -> int:
        haystack = " ".join(
            str(value)
            for value in [
                event.get("title", ""),
                event.get("type", ""),
                event.get("description", ""),
                " ".join(event.get("tags") or []),
                " ".join(event.get("claims") or []),
            ]
        ).lower()
        return sum(1 for word in keywords if word in haystack)

    ranked = sorted(events, key=score, reverse=True)
    selected = [event for event in ranked if score(event) > 0][: args.limit]
    if not selected:
        selected = ranked[: args.limit]

    lines = [
        "# Resume Context",
        "",
        "## Target Job Description",
        "",
        jd_text.strip(),
        "",
        "## Selected Career Events",
        "",
    ]
    for event in selected:
        lines.extend(format_event_markdown(event))
    lines.extend(
        [
            "",
            "## Missing Information",
            "",
            "- Confirm dates, metrics, ownership, and public visibility before final resume generation.",
            "",
            "## Risk Notes",
            "",
            "- This context was selected by local keyword matching. Ask the agent to refine selection semantically before producing final resume bullets.",
        ]
    )
    output = vault / "exports" / "resume_context.md"
    output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Career Vault Resume file CLI")
    parser.add_argument("--vault", help="Path to .career-vault directory")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize a career vault")
    init.set_defaults(func=command_init)

    source = sub.add_parser("add-source", help="Add raw source material")
    source.add_argument("--type", required=True, choices=sorted(SOURCE_TYPES))
    source.add_argument("--title", required=True)
    source.add_argument("--text", default="")
    source.add_argument("--file")
    source.add_argument("--url")
    source.set_defaults(func=command_add_source)

    event = sub.add_parser("add-event", help="Add a structured career event")
    event.add_argument("--id")
    event.add_argument("--title", required=True)
    event.add_argument("--type", required=True, choices=sorted(EVENT_TYPES))
    event.add_argument("--custom-type")
    event.add_argument("--start")
    event.add_argument("--end")
    event.add_argument("--precision", default="unknown", choices=["day", "month", "year", "range", "unknown"])
    event.add_argument("--status", default="draft", choices=sorted(EVENT_STATUSES))
    event.add_argument("--description")
    event.add_argument("--role")
    event.add_argument("--organization")
    event.add_argument("--location")
    event.add_argument("--tag", action="append", default=[])
    event.add_argument("--detail", action="append", default=[], help="Custom detail as KEY=VALUE")
    event.add_argument("--claim", action="append", default=[])
    event.add_argument("--source", action="append", default=[])
    event.add_argument("--visibility", default="private", choices=sorted(VISIBILITIES))
    event.set_defaults(func=command_add_event)

    list_events = sub.add_parser("list-events", help="List career events")
    list_events.add_argument("--json", action="store_true")
    list_events.set_defaults(func=command_list_events)

    identity = sub.add_parser("build-identity", help="Export agent identity summary")
    identity.set_defaults(func=command_build_identity)

    context = sub.add_parser("build-resume-context", help="Export resume context for a JD")
    context.add_argument("--jd", required=True)
    context.add_argument("--limit", type=int, default=8)
    context.set_defaults(func=command_build_resume_context)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
