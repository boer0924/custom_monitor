import os
import sys
import time
import json
import socket
from urllib import request
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

import psutil

from daemon import DaemonBase
from host_performence import *


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

    @staticmethod
    def get_host_addrs(family):
        for nic, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == family:
                    yield (nic, snic.address)

    def do_post(self, params):
        data = json.dumps(params)
        headers = {'Content-Type': 'application/json'}
        req = request.Request(self.url, data.encode('utf-8'), headers=headers)
        try:
            with request.urlopen(req, timeout=3) as resp:
                return resp.status
        except Exception as e:
            with open('/tmp/test_daemon.err', 'a') as f:
                print('%s at: %s' % (e, time.ctime()), file=f)

    def tasks(self):
        pnic_before = get_net_io_counters()
        while 1:
            # sys.stdout.write('Hello World! %s\n' % time.ctime())
            time.sleep(60)
            pnic_after = get_net_io_counters()
            send_datas = {
                'ip_addr': ''.join([
                    n[1] for n in self.get_host_addrs(socket.AF_INET)
                    if n[0] == 'wlp2s0'
                ]),
                'cpu_perf': get_cpu_percent(),
                'mem_perf': get_mem_usage(),
                'disk_perf': get_disk_usage(),
                'net_perf': get_network_traffic(pnic_before, pnic_after)
            }
            self.do_post(send_datas)
            pnic_before = get_net_io_counters()

    def run(self):
        sys.stdout.write('Daemon started with pid %s\n' % os.getpid())
        _p = Process(target=self.tasks, daemon=True)
        _p.start()
        p = psutil.Process(_p.pid)
        while 1:
            current_cpu = p.cpu_percent()
            current_mem = p.memory_percent()
            print(current_cpu, current_mem, time.ctime())
            if p.is_running() and (current_mem > 1 or current_cpu > 1):
                p.kill()
                with open('/tmp/test_daemon.log', 'a') as f:
                    f.write('CPU: %s - MEM: %s - at: %s' %
                            (current_cpu, current_mem, time.ctime()))
                _p = Process(target=self.tasks, daemon=True)
                _p.start()
                p = psutil.Process(_p.pid)
            time.sleep(60)