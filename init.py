#!/usr/bin/env python3

"""A test wrapper script."""

import sys
import os
from pathlib import Path

if __name__ == "__main__":
    project_dir: Path = Path(sys.path[0])
    source_dir: Path = Path(project_dir, "src")
    sys.path.append(str(source_dir.absolute()))
    sources: list[Path] = []
    for directory in os.listdir(source_dir):
        file: Path = Path(source_dir, directory).absolute()
        if file.is_dir():
            sys.path.append(str(file))

    try:
        # Trying to find module on sys.path
        from mc_resourcepacks_util_tools import main
        main()
        del main
    except ModuleNotFoundError:
        print("Absolute import failed")
