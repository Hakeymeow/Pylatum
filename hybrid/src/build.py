import os, sys, subprocess
from argparse import ArgumentParser
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "src")
BUILD_DIR = os.path.join(PROJECT_ROOT_DIR, "build")

BASIC_CMD = [
    "python", "-m", "nuitka", "--standalone", "--onefile"
]

def buildGUI():
    guicmd = BASIC_CMD + [
        f"--include-module={m}" for m in ["webview"]
    ] + [
        f"--include-data-files={os.path.join(SRC_DIR, f)}=."
        for f in ["index.html"]
    ] + [
        "--output-filename=pylatum-gui",
        os.path.join(SRC_DIR, "calc_gui.py")
    ]
    print("\x1b[1;32m", "Building:", " ".join(guicmd), "\x1b[0m")
    return subprocess.run(guicmd, cwd=BUILD_DIR).returncode

def buildCLI():
    clicmd = BASIC_CMD + [
        "--output-filename=pylatum-cli",
        os.path.join(SRC_DIR, "calc.py")
    ]
    print("\x1b[1;32m", "Building:", " ".join(clicmd), "\x1b[0m")
    return subprocess.run(clicmd, cwd=BUILD_DIR).returncode

def main():
    parser = ArgumentParser()
    parser.add_argument("--cli", "-c", action="store_true", help="build cli pylatum")
    parser.add_argument("--gui", "-g", action="store_true", help="build gui pylatum")
    args = parser.parse_args()

    exitCode = 0
    if args.cli or args.gui:
        os.makedirs(BUILD_DIR, exist_ok=True)
    if args.cli:
        exitCode = buildCLI() or exitCode
    if args.gui:
        exitCode = buildGUI() or exitCode
    print("\x1b[1;32m", "Artifact location:", BUILD_DIR, "\x1b[0m")
    sys.exit(exitCode)

if __name__ == "__main__":
    main()
