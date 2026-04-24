import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DIST_DIR = SCRIPT_DIR / "dist"
INDEX_HTML = SCRIPT_DIR / "index.html"
PLOTLY_JS = SCRIPT_DIR / "plotly.min.js"

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
        "calc_gui.py"
    ]

    print("Building:", " ".join(cmd))
    return subprocess.run(cmd, cwd=SCRIPT_DIR).returncode

if __name__ == "__main__":
    sys.exit(build())