"""Training entry point to complete after the project task is selected."""

import argparse
from pathlib import Path

from aie1903_project.pipeline import RunContext


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = RunContext.from_file(args.config)
    raise NotImplementedError(
        f"Define the final task before implementing training: {context.config_path}"
    )


if __name__ == "__main__":
    main()
