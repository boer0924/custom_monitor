import psutil

__all__ = [
    'get_cpu_percent', 'get_mem_usage', 'get_disk_usage', 'get_disk_speed',
    'get_net_io_counters', 'get_network_traffic'
]


def bytes2human(n):
    """ 
    >>> bytes2human(10000) 
    '9.8 K' 
    >>> bytes2human(100001221) 
    '95.4 M' 
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)


# CPU
def get_cpu_percent():
    return {'percent': str(psutil.cpu_percent()) + ' %'}


# Memory
def get_mem_usage():
    mem = psutil.virtual_memory()
    return {
        'total': bytes2human(mem.total),
        'available': bytes2human(mem.available),
        'percent': str(mem.percent) + ' %',
        'used': bytes2human(mem.used),
        'free': bytes2human(mem.free),
        'active': bytes2human(mem.active),
        'inactive': bytes2human(mem.inactive),
        'buffers': bytes2human(mem.buffers),
        'cached': bytes2human(mem.cached),
        'shared': bytes2human(mem.shared)
    }


# Disk
def get_disk_usage():
    parts = (part.mountpoint for part in psutil.disk_partitions())
    parts_usages = []
    for part in parts:
        part_usage = psutil.disk_usage(part)
        parts_usages.append({
            part: {
                'total': bytes2human(part_usage.total),
                'used': bytes2human(part_usage.used),
                'free': bytes2human(part_usage.free),
                'percent': str(part_usage.percent) + ' %'
            }
        })
    return parts_usages


def get_disk_speed():
    disk_stat = psutil.disk_io_counters()
    return (disk_stat.read_time + disk_stat.write_time) / (
        disk_stat.read_count + disk_stat.write_count)


# Network
def get_net_io_counters():
    return psutil.net_io_counters(pernic=True)


def get_network_traffic(pnic_before, pnic_after):
    pnics_traffics = []
    for nic in pnic_after.keys():
        bytes_sent = pnic_after[nic].bytes_sent - pnic_before[nic].bytes_sent
        bytes_recv = pnic_after[nic].bytes_recv - pnic_before[nic].bytes_recv
        pnics_traffics.append({
            nic: {
                'bytes_sent': bytes2human(bytes_sent),
                'bytes_recv': bytes2human(bytes_recv)
            }
        })
    return pnics_traffics