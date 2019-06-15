from subprocess import run as _
from pathlib import Path as _p

def which(exe):
    t = _p(_(["where.exe",exe],capture_output=True).stdout.decode().strip()).resolve()
    if t.is_file():
        return str(t)

