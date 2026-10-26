#!/usr/bin/env python3
"""Bounded performance probe for task T-20261026-02 (audit A-20261026-server).

Evidence only, not project code. Measures (1) CPU matmul throughput versus thread
count under the 24-core cgroup quota, including cgroup throttling, and (2) storage
throughput and small-file latency on the NFS project volume, the container overlay
(/tmp) and /dev/shm. Temporary files are removed. Runtime is about 1-2 minutes.

Usage (from project root):
    .venv/bin/python reports/audit/A-20261026-server/perf_probe.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")

NUMPY_BENCH = """
import time, numpy as np
n = 3000
a = np.random.default_rng(0).standard_normal((n, n)); b = a.T.copy()
a @ b
t0 = time.perf_counter(); reps = 3
for _ in range(reps): a @ b
dt = (time.perf_counter() - t0) / reps
print(2 * n**3 / dt / 1e9)
"""

TORCH_BENCH = """
import sys, time, torch
torch.set_num_threads(int(sys.argv[1])) if sys.argv[1] != "default" else None
n = 3000
a = torch.randn(n, n, dtype=torch.float64); b = a.T.contiguous()
a @ b
t0 = time.perf_counter(); reps = 3
for _ in range(reps): a @ b
dt = (time.perf_counter() - t0) / reps
print(2 * n**3 / dt / 1e9, torch.get_num_threads())
"""


def throttle() -> tuple[int, int]:
    stat = dict(line.split() for line in Path("/sys/fs/cgroup/cpu.stat").read_text().splitlines())
    return int(stat["nr_throttled"]), int(stat["throttled_usec"])


def run_bench(code: str, threads: str, args: list[str] | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in THREAD_VARS}
    if threads != "default":
        env.update({k: threads for k in THREAD_VARS})
    n0, u0 = throttle()
    t0 = time.perf_counter()
    res = subprocess.run([sys.executable, "-c", code, *(args or [])], env=env, capture_output=True, text=True, timeout=300)
    wall = time.perf_counter() - t0
    n1, u1 = throttle()
    parts = res.stdout.split()
    return {
        "threads_env": threads,
        "gflops": round(float(parts[0]), 1) if parts else None,
        "effective_threads": int(parts[1]) if len(parts) > 1 else None,
        "wall_s": round(wall, 2),
        "throttled_periods": n1 - n0,
        "throttled_s": round((u1 - u0) / 1e6, 2),
        "error": res.stderr.strip()[-300:] if res.returncode else None,
    }


def io_bench(base: Path, label: str, size_mib: int = 256) -> dict:
    base.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="iotest-", dir=base))
    try:
        blob = work / "blob.bin"
        chunk = os.urandom(1 << 20)
        t0 = time.perf_counter()
        with open(blob, "wb") as fh:
            for _ in range(size_mib):
                fh.write(chunk)
            fh.flush()
            os.fsync(fh.fileno())
        write_s = time.perf_counter() - t0
        dd = subprocess.run(["dd", f"if={blob}", "of=/dev/null", "bs=1M", "iflag=direct"],
                            capture_output=True, text=True, timeout=300)
        read_note = dd.stderr.strip().splitlines()[-1] if dd.stderr else None
        small = work / "small"
        small.mkdir()
        payload = os.urandom(4096)
        t0 = time.perf_counter()
        for i in range(300):
            (small / f"f{i:04d}.bin").write_bytes(payload)
        create_ms = (time.perf_counter() - t0) * 1000 / 300
        t0 = time.perf_counter()
        for p in small.iterdir():
            p.stat()
        stat_ms = (time.perf_counter() - t0) * 1000 / 300
        return {
            "location": label,
            "write_mib_s_with_fsync": round(size_mib / write_s, 1),
            "read_direct_dd": read_note,
            "small_file_create_ms": round(create_ms, 3),
            "small_file_stat_ms": round(stat_ms, 3),
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    result = {
        "audit_id": "A-20261026-server",
        "task_id": "T-20261026-02",
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "cpu_quota_cores": 24,
        "numpy_matmul_float64_n3000": [run_bench(NUMPY_BENCH, t) for t in ("1", "8", "16", "24", "default")],
        "torch_cpu_matmul_float64_n3000": [
            run_bench(TORCH_BENCH, t, [t if t != "default" else "default"]) for t in ("8", "24", "default")
        ],
        "storage": [
            io_bench(ROOT / "logs", "nfs:/ai/workspace (project logs/)"),
            io_bench(Path("/tmp"), "overlay:/tmp (ephemeral)"),
            io_bench(Path("/dev/shm"), "tmpfs:/dev/shm (RAM, counts toward memory limit)"),
        ],
    }
    (OUT / "perf.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
