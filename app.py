import sys

from post_to_srv import MyDaemon

# Settings
# API_URL = 'http://127.0.0.1:5000/monitor'
# MONITOR_PORT = 'wlp2s0'
# API_URL = 'http://172.19.3.66:10081/collection'
API_URL = 'http://192.168.28.2:10081/collection'
MONITOR_PORT = 'eth0'
PIDFILE = '/tmp/host_monitor_daemon.pid'
LOGFILE = '/tmp/host_monitor.log'

if len(sys.argv) != 2:
    print('Usage: %s [start|stop|restart]' % sys.argv[0], file=sys.stderr)
    raise SystemExit(1)
md = MyDaemon(API_URL, MONITOR_PORT, PIDFILE, stdout=LOGFILE, stderr=LOGFILE)
if sys.argv[1] == 'start':
    md.start()
elif sys.argv[1] == 'stop':
    md.stop()
elif sys.argv[1] == 'restart':
    md.restart()
else:
    print('Unkown command %s' % sys.argv[1], file=sys.stderr)
    raise SystemExit(1)