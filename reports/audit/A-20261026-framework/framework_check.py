#!/usr/bin/env python3
"""One-off framework completeness check for task T-20261026-01.

Evidence only (the reusable version is `verify-records`, roadmap M7). Checks that the
framework files exist, rules and configs parse and agree with each other, every path
referenced from Markdown exists, hooks are enabled and ignore rules behave as intended.

Usage (from project root):
    .venv/bin/python reports/audit/A-20261026-framework/framework_check.py
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


REQUIRED = [
    "AGENTS.md", "CLAUDE.md", "SOUL.md", "README.md", "CHANGELOG.md", "pyproject.toml",
    "requirements.lock", ".gitignore", ".gitattributes", ".editorconfig", ".env.example",
    ".gitmessage", ".githooks/commit-msg", ".githooks/pre-commit",
    ".cursor/rules/00-project.mdc", ".cursor/rules/10-forecasting.mdc",
    ".cursor/rules/20-records.mdc", ".cursor/rules/30-server.mdc",
    ".cursor/rules/40-code-structure.mdc", ".cursor/rules/README.md",
    "configs/README.md", "configs/datasets.yaml", "configs/validation-plan.json",
    "configs/runtime.yaml", "configs/experiments/_template.yaml",
    "data/README.md", "data/checksums.sha256",
    "docs/README.md", "docs/project-context.md", "docs/agent-contract.md",
    "docs/architecture.md", "docs/roadmap.md", "docs/current-status.md",
    "docs/sources-and-open-questions.md", "docs/ai-use-log.md",
    "docs/standards/coding.md", "docs/standards/git-workflow.md", "docs/standards/records.md",
    "docs/runbooks/environment.md", "docs/runbooks/sync-backup-release.md",
    "docs/runbooks/grokbot.md", "docs/tasks/README.md", "docs/decisions/README.md",
    "docs/templates/task-card.md", "docs/templates/adr.md", "docs/templates/run-record.json",
    "docs/worklog/2026-10.md", "reports/README.md", "reports/experiments.csv",
    "runs/README.md", "submissions/README.md", "scripts/README.md", "notebooks/README.md",
    "tests/README.md", "tests/test_layout.py", "src/aie1903/__init__.py",
]
for rel in REQUIRED:
    check(f"exists:{rel}", (ROOT / rel).is_file())

AREAS = ["config", "data", "splits", "features", "models", "evaluation", "tracking", "pipelines", "viz"]
for area in AREAS:
    check(f"area:{area}", (ROOT / "src/aie1903" / area / "__init__.py").is_file())


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    return yaml.safe_load(match.group(1)) if match else {}


for rule in sorted((ROOT / ".cursor/rules").glob("*.mdc")):
    fm = frontmatter(rule)
    check(f"rule_frontmatter:{rule.name}", bool(fm) and "alwaysApply" in fm and "description" in fm)
    lines = len(rule.read_text(encoding="utf-8").splitlines())
    check(f"rule_length<=60:{rule.name}", lines <= 60, f"{lines} lines")
    if fm.get("alwaysApply") is False:
        check(f"rule_globs_equal_paths:{rule.name}", fm.get("globs") == fm.get("paths"))
        for pattern in str(fm.get("globs", "")).split(","):
            hits = glob.glob(str(ROOT / pattern.strip()), recursive=True)
            check(f"rule_glob_matches:{rule.name}:{pattern.strip()}", bool(hits), f"{len(hits)} paths")
        link = ROOT / ".claude/rules" / (rule.stem + ".md")
        check(f"claude_symlink:{rule.stem}", link.is_symlink() and link.resolve() == rule.resolve())

claude_text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
imports = re.findall(r"^@(\S+)\s*$", claude_text, flags=re.MULTILINE)
check("claude_imports_present", imports[:2] == ["AGENTS.md", "SOUL.md"], str(imports))
for imp in imports:
    check(f"claude_import_resolves:{imp}", (ROOT / imp).is_file())

# Living documents must only reference existing paths. Historical records (changelog, task
# cards, ADRs, worklog, AI-use log, legacy and audit notes) legitimately name removed files,
# and "rev:path" references (git show archive/...:path) point into Git history.
PATH_RE = re.compile(
    r"(?<![\w./:-])((?:docs|configs|data|reports|src|tests|scripts|notebooks|runs|submissions|"
    r"artifacts|\.cursor|\.claude|\.githooks)/[A-Za-z0-9_./*<>{}-]*[A-Za-z0-9_/*>}-])"
)
SKIP_TOKENS = ("<", ">", "*", "{", "YYYY", "NNNN", "XXXX", "NN-")
HISTORICAL = ("CHANGELOG.md", "docs/tasks/", "docs/decisions/", "docs/worklog/",
              "docs/ai-use-log.md", "reports/legacy/", "reports/audit/")
md_files = [p for p in ROOT.rglob("*.md") if not any(
    part in {".git", ".venv", "references", "runs", "data"} for part in p.relative_to(ROOT).parts[:-1]
) or p.parent == ROOT / "data"]
md_files += list((ROOT / ".cursor/rules").glob("*.mdc"))
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
check("config_parse:runtime", runtime.get("device") == "cpu" and runtime.get("threads") == 8)
check("protocol_id_consistent", template.get("protocol") == plan["protocol_id"] == "expanding_289_v1")
folds = plan["development_folds"] + [plan["heldout_fold"]]
check("folds_289_each", all(f["validation_end_exclusive"] - f["validation_start"] == 289 for f in folds))
check("folds_non_overlapping_expanding", all(
    a["validation_end_exclusive"] <= b["validation_start"] and a["train_end_exclusive"] < b["train_end_exclusive"]
    for a, b in zip(folds, folds[1:])
))
check("folds_origin_equals_fit_end", all(f["train_end_exclusive"] == f["validation_start"] for f in folds))
check("heldout_ends_at_1728", plan["heldout_fold"]["validation_end_exclusive"] == plan["available_training_rows"] == 1728)
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
        check(f"registry_file:{ds_id}:{role}", path.is_file() and path.stat().st_size == meta["bytes"] and rel in sums)
check("checksums_cover_registry_exactly", registered == set(sums), f"{len(sums)} checksum entries")

hooks_path = git("config", "--get", "core.hooksPath").stdout.strip()
check("hooks_enabled", hooks_path == ".githooks", hooks_path)
for hook in ("commit-msg", "pre-commit"):
    check(f"hook_executable:{hook}", os.access(ROOT / ".githooks" / hook, os.X_OK))
check("commit_template_set", git("config", "--get", "commit.template").stdout.strip() == ".gitmessage")

SHOULD_IGNORE = [
    "data/raw/cell_217/cell_217_train.csv", "data/raw/cell_217/data_description_for_cell_217.pdf",
    "runs/R-x/run.json", "submissions/cell_217/R-x.csv", ".venv/bin/python", ".agent-lock",
    ".env", "logs/a.log", "backups/x.tar.gz", "artifacts/models/m.pt", "docs/.!!!junk.pdf",
    ".cursor/plans/x.md",
]
SHOULD_TRACK = [
    "AGENTS.md", "SOUL.md", ".cursor/rules/00-project.mdc", ".claude/rules/10-forecasting.md",
    "data/checksums.sha256", "data/raw/.gitkeep", "runs/README.md", "submissions/README.md",
    "submissions/cell_217/R-x.json", "reports/runs/.gitkeep", "reports/experiments.csv", ".env.example",
]
for rel in SHOULD_IGNORE:
    check(f"ignored:{rel}", git("check-ignore", "-q", "--no-index", rel).returncode == 0)
for rel in SHOULD_TRACK:
    check(f"not_ignored:{rel}", git("check-ignore", "-q", "--no-index", rel).returncode == 1)

tracked_raw = [p for p in git("ls-files", "data/raw").stdout.split() if p != "data/raw/.gitkeep"]
check("no_raw_data_tracked", not tracked_raw, " ".join(tracked_raw))

failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    if not ok:
        print(f"FAIL {name} {detail}")
print(f"checks={len(results)} passed={len(results) - len(failed)} failed={len(failed)}")
(Path(__file__).parent / "framework-check.json").write_text(
    json.dumps({"checks": [{"check": n, "ok": ok, "detail": d} for n, ok, d in results],
                "passed": len(results) - len(failed), "failed": len(failed)}, indent=1) + "\n",
    encoding="utf-8",
)
raise SystemExit(1 if failed else 0)
