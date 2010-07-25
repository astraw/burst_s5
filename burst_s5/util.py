import subprocess
import sys

def get_stdout(cmd):
    """call a command and return the stdout, raising exception if error"""
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    sys.stdout.write('calling "%s"...'%(' '.join(cmd)))
    sys.stdout.flush()
    p.wait()
    if p.returncode != 0:
        raise RuntimeError('command "%s" failed with code %d'%(
                ' '.join(cmd), p.returncode))
    sys.stdout.write('OK\n')
    sys.stdout.flush()
    return p.stdout.read()
