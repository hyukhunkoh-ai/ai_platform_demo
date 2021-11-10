import time
import psutil
from subprocess import Popen

def get_proc_ubuntu(cmd):
    for p in psutil.process_iter():
        cmdl = p.cmdline()
        if cmd[0] in cmdl and cmd[1] in cmdl:
            return True, p
    return False, None

def ubuntu():
    cmd = ['python3', 'app.py']
    while True:
        ret, p = get_proc_ubuntu(cmd)
        if not ret:
            Popen(cmd)
        time.sleep(1)

def get_proc_windows(pid):
    for p in psutil.process_iter():
        if p.pid == pid:
            return True, p
    return False, None

def windows():
    cmd = ['python', 'app.py']
    p = Popen(cmd)
    while True:
        ret, p = get_proc_windows(p.pid)
        if not ret:
            p = Popen(cmd)
        time.sleep(1)


if __name__ == '__main__':
    ubuntu()