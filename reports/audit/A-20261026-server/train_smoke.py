#!/usr/bin/env python3
"""Bounded training smoke test for task T-20261026-02 (audit A-20261026-server).

Evidence only, not project code: proves the training stack works on this server.
A tiny LSTM forecaster (288 input steps -> 289 outputs) is trained for a few steps
on RANDOM tensors (no project data is read) on CPU (8 threads), GPU strict FP32,
GPU TF32 (image default) and GPU bf16 autocast. Also checks seed determinism,
torch.compile on sm_120, peak GPU memory and peak RSS. Budget: < 3 min, < 2 GiB VRAM.

Usage (from project root):
    .venv/bin/python reports/audit/A-20261026-server/train_smoke.py
"""

from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "8"
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import json  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import torch  # noqa: E402
from torch import nn  # noqa: E402

OUT = Path(__file__).resolve().parent
LOOKBACK, HORIZON, HIDDEN, N, BATCH = 288, 289, 64, 512, 128


class TinyLSTM(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lstm = nn.LSTM(1, HIDDEN, num_layers=2, batch_first=True)
        self.head = nn.Linear(HIDDEN, HORIZON)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return self.head(out[:, -1])


def set_precision(mode: str) -> None:
    if mode == "fp32_strict":
        torch.set_float32_matmul_precision("highest")
        torch.backends.cudnn.allow_tf32 = False
    else:
        torch.set_float32_matmul_precision("high")
        torch.backends.cudnn.allow_tf32 = True


def train(device: str, mode: str, steps: int, seed: int = 0, deterministic: bool = False) -> dict:
    set_precision("fp32_strict" if mode == "bf16_autocast" else mode)
    torch.use_deterministic_algorithms(deterministic)
    torch.manual_seed(seed)
    gen = torch.Generator().manual_seed(seed)
    x = torch.randn(N, LOOKBACK, 1, generator=gen).to(device)
    y = torch.randn(N, HORIZON, generator=gen).to(device)
    model = TinyLSTM().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    losses, times = [], []
    for step in range(steps):
        idx = slice((step * BATCH) % N, (step * BATCH) % N + BATCH)
        if device == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device, dtype=torch.bfloat16, enabled=mode == "bf16_autocast"):
            loss = nn.functional.mse_loss(model(x[idx]).float(), y[idx])
        loss.backward()
        opt.step()
        if device == "cuda":
            torch.cuda.synchronize()
        times.append(time.perf_counter() - t0)
        losses.append(loss.item())
    warm = times[3:] or times
    result = {
        "device": device,
        "precision": mode,
        "steps": steps,
        "step_ms_median": round(sorted(warm)[len(warm) // 2] * 1000, 2),
        "first_step_ms": round(times[0] * 1000, 1),
        "loss_first": round(losses[0], 6),
        "loss_last": round(losses[-1], 6),
        "final_param_checksum": float(sum(p.detach().double().sum().item() for p in model.parameters())),
    }
    if device == "cuda":
        result["peak_gpu_mib"] = round(torch.cuda.max_memory_allocated() / 2**20, 1)
    torch.use_deterministic_algorithms(False)
    return result


COMPILE_CHECK = """
import time, torch
torch.manual_seed(0)
m = torch.nn.Sequential(torch.nn.Linear(289, 256), torch.nn.GELU(), torch.nn.Linear(256, 289)).cuda()
cm = torch.compile(m)
x = torch.randn(256, 289, device="cuda")
t0 = time.perf_counter(); y = cm(x); y.sum().backward(); torch.cuda.synchronize()
first = time.perf_counter() - t0
t0 = time.perf_counter()
for _ in range(20):
    y = cm(x); y.sum().backward()
torch.cuda.synchronize()
print(round(first, 2), round((time.perf_counter() - t0) / 20 * 1000, 3))
"""


def compile_check() -> dict:
    t0 = time.perf_counter()
    try:
        res = subprocess.run([sys.executable, "-c", COMPILE_CHECK], capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout after 240 s"}
    if res.returncode != 0:
        return {"ok": False, "error": res.stderr.strip()[-500:]}
    first, steady = res.stdout.split()
    return {"ok": True, "first_call_incl_compile_s": float(first), "steady_step_ms": float(steady),
            "wall_s": round(time.perf_counter() - t0, 1)}


def main() -> int:
    t_start = time.perf_counter()
    torch.set_num_threads(8)
    report: dict = {
        "audit_id": "A-20261026-server",
        "task_id": "T-20261026-02",
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "data": "random tensors only (no project data)",
        "model": f"LSTM(1->{HIDDEN}, 2 layers) + Linear({HIDDEN}->{HORIZON}); batch {BATCH}, lookback {LOOKBACK}",
        "torch": torch.__version__,
        "cpu_threads": torch.get_num_threads(),
        "runs": [],
    }
    report["runs"].append(train("cpu", "fp32_strict", steps=8))
    if torch.cuda.is_available():
        for mode in ("fp32_strict", "tf32_default", "bf16_autocast"):
            report["runs"].append(train("cuda", mode, steps=40))
        try:
            a = train("cuda", "fp32_strict", steps=10, seed=123, deterministic=True)
            b = train("cuda", "fp32_strict", steps=10, seed=123, deterministic=True)
            report["determinism_gpu_fp32"] = {
                "ok": a["final_param_checksum"] == b["final_param_checksum"] and a["loss_last"] == b["loss_last"],
                "checksum_a": a["final_param_checksum"],
                "checksum_b": b["final_param_checksum"],
            }
        except RuntimeError as exc:
            report["determinism_gpu_fp32"] = {"ok": False, "error": str(exc)[:500]}
        report["torch_compile_sm120"] = compile_check()
        free, total = torch.cuda.mem_get_info()
        report["gpu_mem_after_gib"] = {"free": round(free / 2**30, 2), "total": round(total / 2**30, 2)}
    report["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    report["wall_s"] = round(time.perf_counter() - t_start, 1)
    (OUT / "train-smoke.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
