import syslog
import time
import logging
import requests
from pds.backend.utils import tstostr
from pds.backend import plugin_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


post_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
def l(event, source):
    def function_wrapper(func):
        def function_wrapped(*args, **kwargs):
            log(syslog.LOG_NOTICE, f"{event}_begin", timestamp(), source, *args, **kwargs)
            try:
                ret = func(*args, **kwargs)
                log(syslog.LOG_NOTICE, f"{event}_end", timestamp(), source, *args, ret=ret, **kwargs)
                return ret
            except Exception as e:
                log(syslog.LOG_ERR, f"{event}_exception", timestamp(), source, *args, exception=e, **kwargs)
                raise
        return function_wrapped
    return function_wrapper


def to_json(d):
    return d


def log(level, event, timestamp, source,*args, **kwargs):
    pc = plugin_config.get_plugin_config("logging")
    if pc is None:
        logger.log(logging.INFO, f"{level},{event},{timestamp},{source},{args},{kwargs}")
    else:
        requests.post("http://{host}:{port}/log".format(host=pc["name"], port=pc["port"]), headers=post_headers, json={
            "event": event,
            "level": level,
            "timestamp": timestamp,
            "source": source,
            "args": to_json(args),
            "kwargs": to_json(kwargs)
        })
    

def timestamp():
    return tstostr(time.time())


