import os
import sys
import time
import atexit
import signal

import psutil


class DaemonBase:
    """Daemon Base Class"""
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
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


class MyDaemon(DaemonBase):
    """Real Daemon class"""
    def run(self):
        sys.stdout.write('Daemon started with pid %s\n' % os.getpid())
        while 1:
            sys.stdout.write('Hello World Daemon! %s\n' % time.ctime())
            cpu_percent = psutil.cpu_percent()
            print(str(cpu_percent) + '%')
            time.sleep(60)

if __name__ == '__main__':
    md = MyDaemon('/tmp/test_mydaemon.pid', stdout='/tmp/test_daemon.log', stderr='/tmp/test_daemon.log')
    if len(sys.argv) != 2:
        print('Usage: %s [start|stop|restart]' % sys.argv[0], file=sys.stderr)
        raise SystemExit(1)
    if sys.argv[1] == 'start':
        md.start()
    elif sys.argv[1] == 'stop':
        md.stop()
    elif sys.argv[1] == 'restart':
        md.restart()
    else:
        print('Unkown command %s' % sys.argv[1], file=sys.stderr)
        raise SystemExit(1)