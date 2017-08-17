import sys

from post_to_srv import MyDaemon

if len(sys.argv) != 2:
    print('Usage: %s [start|stop|restart]' % sys.argv[0], file=sys.stderr)
    raise SystemExit(1)
md = MyDaemon(
    'http://127.0.0.1:5000/monitor',
    '/tmp/test_mydaemon.pid',
    stdout='/tmp/test_daemon.log',
    stderr='/tmp/test_daemon.log')
if sys.argv[1] == 'start':
    md.start()
elif sys.argv[1] == 'stop':
    md.stop()
elif sys.argv[1] == 'restart':
    md.restart()
else:
    print('Unkown command %s' % sys.argv[1], file=sys.stderr)
    raise SystemExit(1)