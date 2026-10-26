#!/usr/bin/env python3
"""Read-only server survey for task T-20261026-02 (audit A-20261026-server).

Evidence only, not project code. Collects facts about the school container that
agents need in order to operate and train safely: platform, cgroup limits, CPU,
memory, storage, processes and tools, network, GPU/CUDA, Python stack.

Secrets policy: environment *values* are printed only for an allowlist of
non-sensitive build variables; Kubernetes tokens, passwords and Jupyter tokens
are never read. Writes only server-facts.json next to this file.

Usage (from project root):
    .venv/bin/python reports/audit/A-20261026-server/server_probe.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SAFE_ENV = re.compile(
    r"^(CUDA_VERSION|CUDA_DRIVER_VERSION|CUDNN_VERSION|NCCL_VERSION|NVIDIA_PYTORCH_VERSION|"
    r"PYTORCH_VERSION|PYTORCH_BUILD_VERSION|TORCH_CUDA_ARCH_LIST|TRT_VERSION|NVIDIA_VISIBLE_DEVICES|"
    r"NVIDIA_DRIVER_CAPABILITIES|CUDA_MODULE_LOADING|TORCH_ALLOW_TF32_CUBLAS_OVERRIDE|"
    r"CUDA_VISIBLE_DEVICES|OMP_NUM_THREADS|MKL_NUM_THREADS|OPENBLAS_NUM_THREADS|PIP_BREAK_SYSTEM_PACKAGES|"
    r"PIP_CONSTRAINT|PIP_DEFAULT_TIMEOUT|LANG|LC_ALL|TZ|JUPYTER_PORT|TENSORBOARD_PORT|"
    r"SVC_RESOURCE_MASTER_SERVICE_PORT_SSH|SVC_RESOURCE_MASTER_SERVICE_PORT_JUPYTER|HF_HOME|TORCH_HOME|"
    r"XDG_CACHE_HOME|PIP_CACHE_DIR|CUBLAS_WORKSPACE_CONFIG)$"
)


def sh(cmd: str, timeout: int = 30) -> str | None:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip() if res.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def read(path: str) -> str | None:
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def section(fn):
    try:
        return fn()
    except Exception as exc:  # evidence script: record, never crash
        return {"error": f"{type(exc).__name__}: {exc}"}


def platform_facts() -> dict:
    env_names = sorted(os.environ)
    return {
        "hostname": platform.node(),
        "kernel": platform.release(),
        "os": sh(". /etc/os-release && echo $PRETTY_NAME"),
        "container_pid1": (read("/proc/1/cmdline") or "").replace("\x00", " ").strip(),
        "kubernetes_pod": "KUBERNETES_SERVICE_HOST" in os.environ,
        "service_account_mounted": Path("/var/run/secrets/kubernetes.io/serviceaccount").is_dir(),
        "image": {
            "nvidia_pytorch_container": os.environ.get("NVIDIA_PYTORCH_VERSION"),
            "build_id": os.environ.get("NVIDIA_BUILD_ID"),
        },
        "boot_time": sh("uptime -s"),
        "timezone_localtime": os.path.realpath("/etc/localtime"),
        "user": sh("id -un"),
        "home": str(Path.home()),
        "safe_env": {k: os.environ[k] for k in env_names if SAFE_ENV.match(k)},
        "env_var_names_count": len(env_names),
    }


def cgroup_facts() -> dict:
    base = Path("/sys/fs/cgroup")
    out = {"version": sh("stat -fc %T /sys/fs/cgroup")}
    for name in ("cpu.max", "cpu.weight", "cpuset.cpus.effective", "cpuset.mems.effective",
                 "memory.max", "memory.high", "memory.swap.max", "memory.current", "memory.peak",
                 "pids.max", "pids.current"):
        out[name] = read(str(base / name))
    quota = out.get("cpu.max")
    if quota and quota.split()[0] != "max":
        q, period = quota.split()
        out["cpu_quota_cores"] = int(q) / int(period)
    out["memory.events"] = read(str(base / "memory.events"))
    out["cpu.stat_throttling"] = sh("grep -E 'nr_periods|nr_throttled|throttled_usec' /sys/fs/cgroup/cpu.stat | tr '\\n' ' '")
    return out


def cpu_memory_facts() -> dict:
    return {
        "cpu_model": sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2"),
        "logical_cpus_visible": os.cpu_count(),
        "sched_affinity_cpus": len(os.sched_getaffinity(0)),
        "lscpu": sh("lscpu | grep -E 'Socket|Core\\(s\\) per|Thread\\(s\\) per|NUMA node[0-9]? CPU|NUMA node\\(s\\)'"),
        "meminfo_virtualized_by_lxcfs": bool(sh("mount | grep -q 'lxcfs on /proc/meminfo' && echo yes")),
        "meminfo_total_kb": sh("awk '/MemTotal/ {print $2}' /proc/meminfo"),
        "swap_total_kb": sh("awk '/SwapTotal/ {print $2}' /proc/meminfo"),
        "ulimit": sh("ulimit -a | grep -E 'open files|max user processes|locked'"),
    }


def storage_facts() -> dict:
    def df(path: str) -> dict | None:
        try:
            u = shutil.disk_usage(path)
            return {"total_gib": round(u.total / 2**30, 1), "free_gib": round(u.free / 2**30, 1)}
        except OSError:
            return None

    nfs = sh("mount | grep ' /ai/workspace ' | sed -E 's/(addr|clientaddr|mountaddr)=[0-9.]+/\\1=x/g'")
    return {
        "persistent_project_volume": {
            "mount": "/ai/workspace",
            "type": "nfs" if nfs and " type nfs " in nfs else None,
            "options": re.search(r"\((.*)\)", nfs).group(1) if nfs else None,
            "usage": df("/ai/workspace"),
        },
        "container_root_overlay": {"usage": df("/"), "persistent": False},
        "dev_shm": {"usage": df("/dev/shm"), "note": "tmpfs; pages count against cgroup memory.max"},
        "tmp_on_overlay": sh("df --output=fstype /tmp | tail -1"),
        "ephemeral_paths_in_use": {
            "cursor_server": Path("/root/.cursor-server").is_dir(),
            "cursor_agent_transcripts": Path("/root/.cursor/projects/ai-workspace-AIE1903/agent-transcripts").is_dir(),
            "pip_cache": Path("/root/.cache/pip").is_dir(),
            "torch_hub_cache": Path("/root/.cache/torch").is_dir(),
            "hf_cache": Path("/root/.cache/huggingface").is_dir(),
        },
        "nfs_junk_files_at_workspace_root": len(list(Path("/ai/workspace").glob(".!!!*"))),
    }


def process_facts() -> dict:
    tools = ["tmux", "screen", "nohup", "setsid", "timeout", "nice", "ionice", "taskset", "numactl", "flock",
             "watch", "top", "htop", "nvtop", "git", "git-lfs", "rsync", "curl", "wget", "jq", "zip", "unzip",
             "make", "gcc", "nvcc", "cmake", "sqlite3", "lsof", "ss", "docker", "kubectl", "sbatch", "conda",
             "uv", "node", "claude", "tensorboard", "jupyter"]
    ports = set()
    for f in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            for line in Path(f).read_text().splitlines()[1:]:
                parts = line.split()
                if parts[3] == "0A":
                    ports.add(int(parts[1].split(":")[1], 16))
        except OSError:
            pass
    return {
        "tools_available": {t: shutil.which(t) is not None for t in tools},
        "job_scheduler": None if not any(shutil.which(t) for t in ("sbatch", "qsub", "kubectl")) else "present",
        "listening_tcp_ports": sorted(ports),
        "services_from_entrypoint": ["sshd (port 22)", "jupyter notebook (port 8888, cwd /ai)",
                                     "tensorboard only if TENSORBOARD_LOG_DIR set at start"],
        "sshd_permit_root_login": sh("grep -hE '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf | head -1"),
        "user_processes_snapshot": sh("ps -eo pid,user,etime,comm --sort=start_time | grep -vE 'ps|grep|sh$|bash$' | tail -15"),
    }


def network_facts() -> dict:
    resolv = read("/etc/resolv.conf") or ""
    def lookup(name: str, n: int = 50) -> dict:
        fails, t0 = 0, time.time()
        for _ in range(n):
            try:
                socket.getaddrinfo(name, 443, proto=socket.IPPROTO_TCP)
            except socket.gaierror:
                fails += 1
        return {"lookups": n, "failures": fails, "avg_ms": round((time.time() - t0) * 1000 / n, 2)}

    def reach(url: str) -> str:
        r = sh(f"curl -s -o /dev/null -m 10 -w '%{{http_code}} %{{time_total}}' '{url}'", timeout=15)
        return r or "fail"

    has_ipv6 = bool((read("/proc/net/if_inet6") or "").strip())
    return {
        "resolv_conf": {
            "nameserver": re.findall(r"^nameserver\s+(\S+)", resolv, flags=re.M),
            "ndots": re.findall(r"ndots:(\d+)", resolv),
            "search_domains": len(re.findall(r"^search\s+(.*)$", resolv, flags=re.M)[0].split()) if "search" in resolv else 0,
        },
        "ipv6_connectivity": has_ipv6,
        "proxy_env_set": any(k.lower().endswith("_proxy") for k in os.environ),
        "dns_github": lookup("github.com"),
        "reachability": {u: reach(u) for u in (
            "https://github.com", "https://api.github.com/zen", "https://pypi.org/simple/pip/",
            "https://mirrors.aliyun.com/pypi/simple/pip/", "https://pypi.tuna.tsinghua.edu.cn/simple/pip/",
            "https://download.pytorch.org/whl/", "https://huggingface.co", "https://hf-mirror.com")},
        "github_ssh": sh("timeout 20 ssh -F /ai/workspace/.ssh/config -o UserKnownHostsFile=/ai/workspace/.ssh/known_hosts "
                         "-o ConnectTimeout=10 -T git@github.com 2>&1 | grep -c 'successfully authenticated'; true"),
    }


def gpu_facts() -> dict:
    q = sh("nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit,persistence_mode,compute_mode,"
           "clocks.max.sm,pcie.link.gen.max,pcie.link.width.max --format=csv,noheader")
    return {
        "nvidia_smi": q,
        "cuda_umd_version": sh("nvidia-smi | grep -oE 'CUDA UMD Version: [0-9.]+' | awk '{print $4}'"),
        "gpu_numa_affinity": sh("nvidia-smi topo -m | awk '/^GPU0/ {print $(NF-2), $(NF-1)}'"),
        "running_compute_apps": sh("nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader"),
        "nvcc": sh("nvcc --version | tail -1"),
        "cuda_home": os.path.realpath("/usr/local/cuda"),
    }


def python_facts() -> dict:
    pkgs = ["numpy", "pandas", "scipy", "matplotlib", "yaml", "sklearn", "statsmodels", "xgboost", "lightgbm",
            "catboost", "sktime", "darts", "gluonts", "lightning", "pytorch_lightning", "transformers",
            "accelerate", "optuna", "tensorboard", "wandb", "mlflow", "torch", "torchvision", "triton",
            "flash_attn", "transformer_engine", "apex", "numba", "cupy", "pyarrow", "polars", "threadpoolctl",
            "ipykernel", "jupyterlab", "notebook", "psutil", "tqdm", "pytest", "ruff"]
    found = {}
    for p in pkgs:
        spec = importlib.util.find_spec(p)
        if spec is None:
            found[p] = None
            continue
        try:
            from importlib.metadata import version

            dist = {"yaml": "PyYAML", "sklearn": "scikit-learn"}.get(p, p)
            found[p] = version(dist)
        except Exception:
            found[p] = "present"
    constraint = Path(os.environ.get("PIP_CONSTRAINT", "/etc/pip/constraint.txt"))
    lines = [ln for ln in (constraint.read_text().splitlines() if constraint.is_file() else []) if ln.strip() and not ln.startswith("#")]
    kernels = sh("jupyter kernelspec list --json")
    return {
        "executable": sys.executable,
        "version": platform.python_version(),
        "system_python": "/usr/bin/python3",
        "venv": str(ROOT / ".venv") if (ROOT / ".venv").is_dir() else None,
        "packages": found,
        "pip_constraint_file_entries": len(lines),
        "jupyter_kernels": list(json.loads(kernels)["kernelspecs"]) if kernels else None,
    }


def torch_facts() -> dict:
    import numpy as np
    import torch

    blas = None
    try:
        from threadpoolctl import threadpool_info

        blas = [{k: i.get(k) for k in ("internal_api", "num_threads", "version")} for i in threadpool_info()]
    except ImportError:
        cfg = np.show_config(mode="dicts") if "mode" in np.show_config.__code__.co_varnames else None
        blas = (cfg or {}).get("Build Dependencies", {}).get("blas") if cfg else None
    out = {
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "cudnn": torch.backends.cudnn.version(),
        "num_threads_default": torch.get_num_threads(),
        "num_interop_threads_default": torch.get_num_interop_threads(),
        "numpy_blas": blas,
        "tf32_matmul_default": torch.backends.cuda.matmul.allow_tf32,
        "tf32_cudnn_default": torch.backends.cudnn.allow_tf32,
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
    }
    if torch.cuda.is_available():
        out.update({
            "device_name": torch.cuda.get_device_name(0),
            "capability": list(torch.cuda.get_device_capability(0)),
            "arch_list": torch.cuda.get_arch_list(),
            "bf16_supported": torch.cuda.is_bf16_supported(),
            "nccl": ".".join(map(str, torch.cuda.nccl.version())) if hasattr(torch.cuda, "nccl") else None,
            "total_memory_gib": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2),
            "sm_count": torch.cuda.get_device_properties(0).multi_processor_count,
            "flash_sdp_enabled": torch.backends.cuda.flash_sdp_enabled(),
        })
    return out


def main() -> int:
    facts = {
        "audit_id": "A-20261026-server",
        "task_id": "T-20261026-02",
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": section(platform_facts),
        "cgroup": section(cgroup_facts),
        "cpu_memory": section(cpu_memory_facts),
        "storage": section(storage_facts),
        "processes": section(process_facts),
        "network": section(network_facts),
        "gpu": section(gpu_facts),
        "python": section(python_facts),
        "torch": section(torch_facts),
    }
    (OUT / "server-facts.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    errors = {k: v["error"] for k, v in facts.items() if isinstance(v, dict) and "error" in v}
    print(json.dumps({"written": "server-facts.json", "section_errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
