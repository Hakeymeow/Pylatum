import os, sys, subprocess, tempfile, shutil
from argparse import ArgumentParser

PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "hylatum", "src")
BUILD_DIR = os.path.join(PROJECT_ROOT_DIR, "build")


def _build_isolated(entry_point: str, output_name: str, extra_args: list[str] | None = None) -> int:
    tmp_venv = tempfile.mkdtemp(prefix="hybrid-build-")
    try:
        subprocess.run(
            ["uv", "venv", tmp_venv],
            cwd=PROJECT_ROOT_DIR, check=True, capture_output=True,
        )
        python_bin = os.path.join(tmp_venv, 
            "Scripts" if sys.platform == "win32" else "bin", 
            "python" + ".exe" if sys.platform == "win32" else ""
        )

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
    extra_args = [
        *[f"--include-module={m}" for m in ["webview"]],
        *[f"--include-data-files={os.path.join(SRC_DIR, f)}={f}" for f in ["index.html"]],
    ]
    if sys.platform == "win32":
        # pywebview plugin of nuitka has some problems on Windows
        # so the webview dependency needs to solve manually
        extra_args += [
            "--disable-plugin=pywebview",
            "--include-module=webview.platforms.win32",
            "--windows-disable-console",
            *[
                f"--nofollow-import-to=webview.platforms.{p}" for p in [
                    "android", "gtk", "qt", "cocoa"
                ]                
            ]
        ]
    return _build_isolated(
        entry_point=os.path.join(SRC_DIR, "calc_gui.py"),
        output_name="hylatum-gui",
        extra_args=extra_args
    )


def buildCLI() -> int:
    return _build_isolated(
        entry_point=os.path.join(SRC_DIR, "calc.py"),
        output_name="hylatum-cli",
    )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-c", "--cli", action="store_true", help="build cli hylatum")
    parser.add_argument("-g", "--gui", action="store_true", help="build gui hylatum")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    exit_code = 0
    if args.cli:
        exit_code = buildCLI() or exit_code
    if args.gui:
        exit_code = buildGUI() or exit_code
    print("\x1b[1;32m", "Artifact location:", BUILD_DIR, "\x1b[0m")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
