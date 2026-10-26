#!/usr/bin/env python3
"""Framework completeness check (maintained successor of the A-20261026-framework probe).

Checks that the framework files exist, rules in rules/ (the single source) parse and are
self-consistent, tool adapters are in sync, every path referenced from living Markdown
exists, configs agree with each other and with the measured server limits, hooks are
enabled and ignore rules behave as intended. Replaced by `verify-records` at roadmap M7.

Usage (from project root):
    .venv/bin/python scripts/check-framework.py [--json OUTPUT.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


RULES = [
    "00-project",
    "10-forecasting",
    "20-records",
    "30-server",
    "35-training",
    "40-code-structure",
]
REQUIRED = [
    "AGENTS.md",
    "CLAUDE.md",
    "SOUL.md",
    "README.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "requirements.lock",
    ".gitignore",
    ".cursorignore",
    ".gitattributes",
    ".editorconfig",
    ".env.example",
    ".gitmessage",
    ".githooks/commit-msg",
    ".githooks/pre-commit",
    "rules/README.md",
    *[f"rules/{r}.md" for r in RULES],
    *[f".cursor/rules/{r}.mdc" for r in RULES],
    ".cursor/rules/05-soul.mdc",
    ".cursor/rules/README.md",
    "scripts/sync-rules.sh",
    "configs/README.md",
    "configs/datasets.yaml",
    "configs/validation-plan.json",
    "configs/runtime.yaml",
    "configs/experiments/_template.yaml",
    "data/README.md",
    "data/checksums.sha256",
    "docs/README.md",
    "docs/project-context.md",
    "docs/agent-contract.md",
    "docs/architecture.md",
    "docs/roadmap.md",
    "docs/current-status.md",
    "docs/sources-and-open-questions.md",
    "docs/ai-use-log.md",
    "docs/standards/coding.md",
    "docs/standards/git-workflow.md",
    "docs/standards/records.md",
    "docs/runbooks/environment.md",
    "docs/runbooks/training.md",
    "docs/runbooks/sync-backup-release.md",
    "docs/runbooks/grokbot.md",
    "docs/tasks/README.md",
    "docs/decisions/README.md",
    "docs/templates/task-card.md",
    "docs/templates/adr.md",
    "docs/templates/run-record.json",
    "reports/README.md",
    "reports/experiments.csv",
    "reports/audit/A-20261026-server/server-facts.json",
    "reports/audit/A-20261026-server/perf.json",
    "reports/audit/A-20261026-server/train-smoke.json",
    "runs/README.md",
    "submissions/README.md",
    "scripts/README.md",
    "notebooks/README.md",
    "tests/README.md",
    "tests/test_layout.py",
    "src/aie1903/__init__.py",
]
for rel in REQUIRED:
    check(f"exists:{rel}", (ROOT / rel).is_file())

AREAS = [
    "config",
    "data",
    "splits",
    "features",
    "models",
    "evaluation",
    "tracking",
    "pipelines",
    "viz",
]
for area in AREAS:
    check(f"area:{area}", (ROOT / "src/aie1903" / area / "__init__.py").is_file())


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    return yaml.safe_load(match.group(1)) if match else {}


canonical = sorted(p for p in (ROOT / "rules").glob("*.md") if p.name != "README.md")
check(
    "rules_set_matches_index",
    [p.stem for p in canonical] == RULES,
    str([p.stem for p in canonical]),
)
agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
for rule in canonical:
    fm = frontmatter(rule)
    check(
        f"rule_frontmatter:{rule.name}",
        bool(fm) and "alwaysApply" in fm and bool(fm.get("description")),
    )
    lines = len(rule.read_text(encoding="utf-8").splitlines())
    check(f"rule_length<=60:{rule.name}", lines <= 60, f"{lines} lines")
    check(f"rule_listed_in_AGENTS:{rule.name}", f"rules/{rule.name}" in agents_text)
    if fm.get("alwaysApply") is True:
        check(f"always_rule_has_no_scope:{rule.name}", "globs" not in fm and "paths" not in fm)
    else:
        check(
            f"rule_globs_equal_paths:{rule.name}",
            bool(fm.get("globs")) and fm.get("globs") == fm.get("paths"),
        )
        for pattern in str(fm.get("globs", "")).split(","):
            hits = glob.glob(str(ROOT / pattern.strip()), recursive=True)
            check(
                f"rule_glob_matches:{rule.name}:{pattern.strip()}", bool(hits), f"{len(hits)} paths"
            )

sync = subprocess.run(
    [str(ROOT / "scripts/sync-rules.sh"), "--check"], capture_output=True, text=True, cwd=ROOT
)
check("rule_adapters_in_sync", sync.returncode == 0, (sync.stdout + sync.stderr).strip())

claude_text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
imports = re.findall(r"^@(\S+)\s*$", claude_text, flags=re.MULTILINE)
check("claude_imports_present", imports[:2] == ["AGENTS.md", "SOUL.md"], str(imports))
for imp in imports:
    check(f"claude_import_resolves:{imp}", (ROOT / imp).is_file())

# Living documents must only reference existing paths. Historical records (changelog, task
# cards, ADRs, worklog, AI-use log, legacy and audit notes) legitimately name removed files,
# and "rev:path" references (git show archive/...:path) point into Git history.
PATH_RE = re.compile(
    r"(?<![\w./:-])((?:docs|configs|data|reports|src|tests|scripts|notebooks|runs|submissions|rules|"
    r"artifacts|\.cursor|\.claude|\.githooks)/[A-Za-z0-9_./*<>{}-]*[A-Za-z0-9_/*>}-])"
)
SKIP_TOKENS = ("<", ">", "*", "{", "YYYY", "NNNN", "XXXX", "NN-", "$")
HISTORICAL = (
    "CHANGELOG.md",
    "docs/tasks/",
    "docs/decisions/",
    "docs/worklog/",
    "docs/ai-use-log.md",
    "reports/legacy/",
    "reports/audit/",
)
md_files = [
    p
    for p in ROOT.rglob("*.md")
    if not any(
        part in {".git", ".venv", "references", "runs", "data", ".cursor", ".claude"}
        for part in p.relative_to(ROOT).parts[:-1]
    )
    or p.parent == ROOT / "data"
]
md_files = [p for p in md_files if not str(p.relative_to(ROOT)).startswith(HISTORICAL)]
missing_refs: list[str] = []
for md in md_files:
    for ref in PATH_RE.findall(md.read_text(encoding="utf-8")):
        ref = ref.rstrip("./")
        if any(token in ref for token in SKIP_TOKENS):
            continue
        if not (ROOT / ref).exists():
            missing_refs.append(f"{md.relative_to(ROOT)} -> {ref}")
check("markdown_path_references_exist", not missing_refs, "; ".join(sorted(set(missing_refs))))

datasets = yaml.safe_load((ROOT / "configs/datasets.yaml").read_text(encoding="utf-8"))
runtime = yaml.safe_load((ROOT / "configs/runtime.yaml").read_text(encoding="utf-8"))
template = yaml.safe_load((ROOT / "configs/experiments/_template.yaml").read_text(encoding="utf-8"))
plan = json.loads((ROOT / "configs/validation-plan.json").read_text(encoding="utf-8"))
check(
    "runtime_threads_within_quota",
    1 <= runtime["threads"] <= runtime["max_threads"] <= 24,
    f"threads={runtime['threads']} max_threads={runtime['max_threads']}",
)
check(
    "runtime_precision_explicit",
    runtime.get("precision") in {"fp32_strict", "tf32", "bf16_autocast"},
)
check("runtime_deterministic_default", runtime.get("deterministic") is True)
check(
    "runtime_env_defaults",
    runtime.get("env", {}).get("WANDB_MODE") == "disabled"
    and runtime.get("env", {}).get("CUBLAS_WORKSPACE_CONFIG") == ":4096:8",
)
check("runtime_device_default_cpu", runtime.get("device") == "cpu")
check(
    "protocol_id_consistent", template.get("protocol") == plan["protocol_id"] == "expanding_289_v1"
)
folds = plan["development_folds"] + [plan["heldout_fold"]]
check(
    "folds_289_each",
    all(f["validation_end_exclusive"] - f["validation_start"] == 289 for f in folds),
)
check(
    "folds_non_overlapping_expanding",
    all(
        a["validation_end_exclusive"] <= b["validation_start"]
        and a["train_end_exclusive"] < b["train_end_exclusive"]
        for a, b in zip(folds, folds[1:], strict=False)
    ),
)
check(
    "folds_origin_equals_fit_end",
    all(f["train_end_exclusive"] == f["validation_start"] for f in folds),
)
check(
    "heldout_ends_at_1728",
    plan["heldout_fold"]["validation_end_exclusive"] == plan["available_training_rows"] == 1728,
)
check("heldout_untouched", plan.get("heldout_status") == "untouched")

sums = {}
for line in (ROOT / "data/checksums.sha256").read_text(encoding="utf-8").splitlines():
    digest, rel = line.split(maxsplit=1)
    sums[rel.strip()] = digest
registered = set()
for ds_id, ds in datasets["datasets"].items():
    for role, meta in ds["files"].items():
        rel = f"raw/{ds['dir']}/{meta['name']}"
        registered.add(rel)
        path = ROOT / "data" / rel
        check(
            f"registry_file:{ds_id}:{role}",
            path.is_file() and path.stat().st_size == meta["bytes"] and rel in sums,
        )
check("checksums_cover_registry_exactly", registered == set(sums), f"{len(sums)} checksum entries")

hooks_path = git("config", "--get", "core.hooksPath").stdout.strip()
check("hooks_enabled", hooks_path == ".githooks", hooks_path)
for hook in ("commit-msg", "pre-commit"):
    check(f"hook_executable:{hook}", os.access(ROOT / ".githooks" / hook, os.X_OK))
check("sync_rules_executable", os.access(ROOT / "scripts/sync-rules.sh", os.X_OK))
check(
    "commit_template_set", git("config", "--get", "commit.template").stdout.strip() == ".gitmessage"
)

SHOULD_IGNORE = [
    "data/raw/cell_217/cell_217_train.csv",
    "data/raw/cell_217/data_description_for_cell_217.pdf",
    "runs/R-x/run.json",
    "submissions/cell_217/R-x.csv",
    ".venv/bin/python",
    ".agent-lock",
    ".env",
    "logs/a.log",
    "backups/x.tar.gz",
    "artifacts/models/m.pt",
    "docs/.!!!junk.pdf",
    ".cursor/plans/x.md",
]
SHOULD_TRACK = [
    "AGENTS.md",
    "SOUL.md",
    "rules/30-server.md",
    "rules/README.md",
    ".cursor/rules/05-soul.mdc",
    ".claude/rules/35-training.md",
    "data/checksums.sha256",
    "data/raw/.gitkeep",
    "runs/README.md",
    "submissions/README.md",
    "submissions/cell_217/R-x.json",
    "reports/runs/.gitkeep",
    "reports/experiments.csv",
    ".env.example",
    "scripts/sync-rules.sh",
]
for rel in SHOULD_IGNORE:
    check(f"ignored:{rel}", git("check-ignore", "-q", "--no-index", rel).returncode == 0)
for rel in SHOULD_TRACK:
    check(f"not_ignored:{rel}", git("check-ignore", "-q", "--no-index", rel).returncode == 1)

tracked_raw = [p for p in git("ls-files", "data/raw").stdout.split() if p != "data/raw/.gitkeep"]
check("no_raw_data_tracked", not tracked_raw, " ".join(tracked_raw))

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--json", type=Path, default=None, help="also write the results as JSON")
args = parser.parse_args()
failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    if not ok:
        print(f"FAIL {name} {detail}")
print(f"checks={len(results)} passed={len(results) - len(failed)} failed={len(failed)}")
if args.json:
    args.json.write_text(
        json.dumps(
            {
                "checks": [{"check": n, "ok": ok, "detail": d} for n, ok, d in results],
                "passed": len(results) - len(failed),
                "failed": len(failed),
            },
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
raise SystemExit(1 if failed else 0)
