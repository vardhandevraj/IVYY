import sys

import eventlet
from eventlet import hubs

from gunicorn.workers.geventlet import EventletWorker as BaseEventletWorker
from gunicorn.workers.geventlet import patch_sendfile


class EventletWorker(BaseEventletWorker):
    """Eventlet gunicorn worker that leaves the stdlib ssl module alone.

    gunicorn's stock eventlet worker calls eventlet.monkey_patch() with no
    arguments, which also replaces the ssl module. Once patched, library code
    that sets SSLContext.minimum_version (urllib3, httpx, authlib via requests)
    recurses infinitely inside ssl.py and dies with RecursionError. We restore
    the untouched stdlib ssl module right after patching so TLS uses the real
    implementation and the recursion never happens.
    """

    def patch(self):
        orig_ssl = sys.modules["ssl"]
        hubs.use_hub()
        eventlet.monkey_patch()
        sys.modules["ssl"] = orig_ssl
        patch_sendfile()