from functools import wraps
from threading import Lock

def sync_required(fun):
    _lock = Lock()
    @wraps(fun)
    def _fun(*args, **kwargs):
        _lock.acquire()
        resp = fun(*args, **kwargs)
        _lock.release()
        return resp

    return _fun