import psutil


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
    return {'percent': str(psutil.cpu_percent(interval=1)) + ' %'}


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


# Network
def get_network_traffic():
    nics_traffics = []
    for k, v in psutil.net_io_counters(pernic=True).items():
        nics_traffics.append({
            k: {
                'bytes_sent': v.bytes_sent,
                'bytes_recv': v.bytes_recv,
                'packets_sent': v.packets_sent,
                'packets_recv': v.packets_recv
            }
        })
    return nics_traffics


print(get_cpu_percent())
print(get_mem_usage())
print(get_disk_usage())
print(get_network_traffic())