#!/usr/bin/env python
import psutil
import Log


def get_system_info():
    try:
        return {
            'system': {
                'cpu': _get_cpu(),
                'memory': _get_memory_info(),
                'disk': _get_disk_info()
            }
        }
    except Exception as exc:
        Log.dlog_e(exc)
        return {
            'system': None
        }


def _get_cpu():
    return {
        'cpu_freq': psutil.cpu_freq(percpu=False)[0],
        'count': psutil.cpu_count(logical=True),
        'cpu_percentage_usage': psutil.cpu_percent(interval=0.1, percpu=False),
    }


def _get_memory_info():
    virtual_memory = psutil.virtual_memory()
    return {
        "total": virtual_memory.total,
        "available": virtual_memory.available,
        "percentage_usage": virtual_memory.percent
    }


def _get_disk_info():
    disk_usage = psutil.disk_usage('/')
    return {
        "total": disk_usage.total,
        "free": disk_usage.free,
        "percentage_usage": disk_usage.percent,
    }

# print(json.dumps(get_system_info()))
