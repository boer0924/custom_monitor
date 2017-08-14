import os
import sys
import time
import json
from urllib import request

from daemon import DaemonBase
from host_performence import get_cpu_percent
from host_performence import get_mem_usage
from host_performence import get_disk_usage
from host_performence import get_net_io_counters
from host_performence import get_network_traffic


class MyDaemon(DaemonBase):
    """Real Daemon class"""

    def __init__(self,
                 url,
                 pidfile,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null'):
        self.url = url
        super().__init__(pidfile, stdin, stdout, stderr)

    def do_post(self, params):
        data = json.dumps(params)
        headers = {'Content-Type': 'application/json'}
        # url = 'http://127.0.0.1:5000/monitor'
        req = request.Request(self.url, data.encode('utf-8'), headers=headers)
        try:
            resp = request.urlopen(req, timeout=3)
        except Exception as e:
            f = open('/tmp/test_daemon.err', 'a')
            print('%s at: %s' % (e, time.ctime()), file=f)
            f.close()
        # return resp.code

    def run(self):
        sys.stdout.write('Daemon started with pid %s\n' % os.getpid())
        pnic_before = get_net_io_counters()
        while 1:
            sys.stdout.write('Hello World Daemon! %s\n' % time.ctime())
            self.do_post(get_cpu_percent())
            self.do_post(get_mem_usage())
            self.do_post(get_disk_usage())
            time.sleep(60)
            pnic_after = get_net_io_counters()
            self.do_post(get_network_traffic(pnic_before, pnic_after))
            pnic_before = get_net_io_counters()


if __name__ == '__main__':
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