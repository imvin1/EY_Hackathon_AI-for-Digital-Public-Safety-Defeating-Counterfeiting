import os
import shutil
import subprocess
import sys


def main() -> int:
    streamlit_exe = shutil.which("streamlit")
    if streamlit_exe:
        cmd = [streamlit_exe] + sys.argv[1:]
    else:
        cmd = [sys.executable, "-m", "streamlit"] + sys.argv[1:]

    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
