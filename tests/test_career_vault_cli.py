import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "career_vault.py"


def run_cli(vault: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--vault", str(vault), *args],
        check=True,
        text=True,
        capture_output=True,
    )


def test_init_add_event_and_export(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")
    run_cli(
        vault,
        "add-event",
        "--title",
        "AI Resume Generator",
        "--type",
        "project",
        "--start",
        "2025-05",
        "--end",
        "2025-08",
        "--precision",
        "month",
        "--status",
        "confirmed",
        "--description",
        "Built a template-driven resume generation workflow.",
        "--claim",
        "Designed a template-driven resume generation workflow.",
    )

    listed = run_cli(vault, "list-events", "--json")
    events = json.loads(listed.stdout)
    assert len(events) == 1
    assert events[0]["title"] == "AI Resume Generator"
    assert events[0]["status"] == "confirmed"

    run_cli(vault, "build-identity")
    identity = vault / "exports" / "agent_identity.md"
    assert identity.exists()
    assert "AI Resume Generator" in identity.read_text()
