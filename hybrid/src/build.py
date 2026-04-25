import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent.resolve()
DIST_DIR = SCRIPT_DIR / "dist"
INDEX_HTML = SCRIPT_DIR  / "src" / "index.html"
PLOTLY_JS = SCRIPT_DIR  / "src" / "plotly.min.js"
PYSRC = SCRIPT_DIR  / "src" / "calc_gui.py"

def build():
    if DIST_DIR.exists():
        import shutil
        shutil.rmtree(DIST_DIR)

    cmd = [
        "python", "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--include-module=webview",
        "--include-module=numpy",
        f"--include-data-files={INDEX_HTML}=.",
        f"--include-data-files={PLOTLY_JS}=.",
        "--assume-yes-for-downloads",
        "--output-filename=pylatum",
        f"{PYSRC}"
    ]

    print("Building:", " ".join(cmd))
    if not os.path.exists(SCRIPT_DIR/"build"):
        os.mkdir(SCRIPT_DIR/"build")
    print("\x1b[1;32m" + f"Artifact location: {SCRIPT_DIR/"build"}" + "\x1b[0m")
    return subprocess.run(cmd, cwd=SCRIPT_DIR/"build").returncode

def main():
    sys.exit(build())

if __name__ == "__main__":
    sys.exit(build())
