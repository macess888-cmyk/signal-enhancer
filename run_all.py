import subprocess
import sys

result = subprocess.run([sys.executable, "enhancer.py"], check=False)
raise SystemExit(result.returncode)