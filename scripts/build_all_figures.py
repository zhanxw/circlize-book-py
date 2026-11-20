"""Run all chapter figure-generation scripts (`ch00_about.py` .. `ch17_make_fun.py`)."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def main() -> None:
    env = dict(os.environ)
    mpl_dir = Path("/tmp/mplconfig")
    mpl_dir.mkdir(parents=True, exist_ok=True)
    env.setdefault("MPLCONFIGDIR", str(mpl_dir))

    scripts = sorted(SCRIPTS_DIR.glob("ch[0-9][0-9]_*.py"))
    if not scripts:
        raise RuntimeError(f"No chapter scripts found in {SCRIPTS_DIR}")

    total_t0 = time.perf_counter()
    for script in scripts:
        t0 = time.perf_counter()
        print(f"=== Running {script.name} ===", flush=True)
        subprocess.run([sys.executable, str(script)], check=True, env=env)
        dt = time.perf_counter() - t0
        print(f"--- Finished {script.name} in {dt:.1f}s ---", flush=True)

    print(f"All {len(scripts)} chapter figure scripts finished in {time.perf_counter() - total_t0:.1f}s.")


if __name__ == "__main__":
    main()
