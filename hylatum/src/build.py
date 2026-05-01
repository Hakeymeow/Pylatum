import os, sys, subprocess, tempfile, shutil
from argparse import ArgumentParser

PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "src")
BUILD_DIR = os.path.join(PROJECT_ROOT_DIR, "build")


def _build_isolated(entry_point: str, output_name: str, extra_args: list[str] | None = None) -> int:
    tmp_venv = tempfile.mkdtemp(prefix="hybrid-build-")
    try:
        subprocess.run(
            ["uv", "venv", tmp_venv],
            cwd=PROJECT_ROOT_DIR, check=True, capture_output=True,
        )
        python_bin = os.path.join(tmp_venv, "bin", "python")

        subprocess.run(
            ["uv", "pip", "install", "-e", PROJECT_ROOT_DIR, "--python", python_bin],
            cwd=PROJECT_ROOT_DIR, check=True, capture_output=True,
        )
        subprocess.run(
            ["uv", "pip", "install", "nuitka[onefile]", "--python", python_bin],
            cwd=PROJECT_ROOT_DIR, check=True, capture_output=True,
        )

        cmd: list[str] = [
            python_bin, "-m", "nuitka",
            "--standalone", "--onefile",
        ]
        if extra_args:
            cmd.extend(extra_args)
        cmd += [f"--output-filename={output_name}", entry_point]

        print("\x1b[1;32m", "Building (isolated):", " ".join(cmd), "\x1b[0m")
        os.makedirs(BUILD_DIR, exist_ok=True)
        return subprocess.run(cmd, cwd=BUILD_DIR).returncode
    finally:
        shutil.rmtree(tmp_venv, ignore_errors=True)


def buildGUI() -> int:
    return _build_isolated(
        entry_point=os.path.join(SRC_DIR, "calc_gui.py"),
        output_name="pylatum-gui",
        extra_args=[
            *[f"--include-module={m}" for m in ["webview"]],
            *[f"--include-data-files={os.path.join(SRC_DIR, f)}=." for f in ["index.html"]],
        ],
    )


def buildCLI() -> int:
    return _build_isolated(
        entry_point=os.path.join(SRC_DIR, "calc.py"),
        output_name="pylatum-cli",
    )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--cli", "-c", action="store_true", help="build cli pylatum")
    parser.add_argument("--gui", "-g", action="store_true", help="build gui pylatum")
    args = parser.parse_args()

    exit_code = 0
    if args.cli:
        exit_code = buildCLI() or exit_code
    if args.gui:
        exit_code = buildGUI() or exit_code
    print("\x1b[1;32m", "Artifact location:", BUILD_DIR, "\x1b[0m")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
