import os
import sys
import time
import atexit
import signal

import psutil

__all__ = ['DaemonBase']


class DaemonBase:
    """Daemon Base Class"""

    def __init__(self,
                 pidfile,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null'):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def _daemonize(self):
        if os.path.exists(self.pidfile):
            raise RuntimeError('Already running.')

        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #1 failed.')

        os.chdir('/')
        os.umask(0)
        os.setsid()

        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #2 failed.')

        sys.stdout.flush()
        sys.stderr.flush()

        with open(self.stdin, 'rb', 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(self.stdout, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(self.stderr, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        with open(self.pidfile, 'w') as f:
            print(os.getpid(), file=f)

        atexit.register(lambda: os.remove(self.pidfile))

        signal.signal(signal.SIGTERM, self.__sigterm_handler)

    @staticmethod
    def __sigterm_handler(signo, frame):
        raise SystemExit(1)

    def run(self):
        pass

    def start(self):
        try:
            self._daemonize()
        except RuntimeError as e:
            print(e, file=sys.stderr)
            raise SystemExit(1)

        self.run()

    def stop(self):
        if os.path.exists(self.pidfile):
            with open(self.pidfile) as f:
                os.kill(int(f.read()), signal.SIGTERM)
        else:
            print('Not running', file=sys.stderr)
            raise SystemExit(1)

    def restart(self):
        self.stop()
        time.sleep(0.1)
        self.start()