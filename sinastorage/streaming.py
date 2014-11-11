"""Streaming with :mod:`sinastorage` via :mod:`poster.streaminghttp`

Usage::

    >>> bucket = StreamingSCSBucket("foo.com")
    >>> bucket.put_file("huge_cd.iso", "foo/huge_cd.iso", acl="public-read")
    >>> with open("foo/huge_cd.iso", "rb") as fp:
    ...     bucket.put_file("memdump.bin", fp)
"""

import os
# import urllib2
from sinastorage.compat import six, StringIO, urllib, http_client
from sinastorage.bucket import SCSBucket

class ProgressCallingFile(object):
    __slots__ = ("fp", "pos", "size", "progress")

    def __init__(self, fp, size, progress):
        self.fp = fp
        self.pos = fp.tell()
        self.size = size
        self.progress = progress

    def __getattr__(self, attnam):
        return getattr(self.fp, attnam)

    def read(self, *a, **k):
        chunk = self.fp.read(*a, **k)
        self.pos += len(chunk)
        self.progress(self.pos, self.size, len(chunk))
        return chunk

class StreamingMixin(object):
    def put_file(self, key, fp, acl=None, metadata={}, progress=None,
                 size=None, mimetype=None, transformer=None, headers={}):
        """Put file-like object or filename *fp* on SCS as *key*.

        *fp* must have a read method that takes a buffer size, and must behave
        correctly with regards to seeking and telling.

        *size* can be specified as a size hint. Otherwise the size is figured
        out via ``os.fstat``, and requires that *fp* have a functioning
        ``fileno()`` method.

        *progress* is a callback that might look like ``p(current, total,
        last_read)``. ``current`` is the current position, ``total`` is the
        size, and ``last_read`` is how much was last read. ``last_read`` is
        zero on EOF.
        """
        headers = headers.copy()
        do_close = False
        if not hasattr(fp, "read"):
            fp = open(fp, "rb")
            do_close = True

        if size is None and hasattr(fp, "fileno"):
            size = os.fstat(fp.fileno()).st_size
        if "Content-Length" not in headers:
            if size is None:
                raise TypeError("no size given and fp does not have a fileno")
            headers["Content-Length"] = str(size)

        if progress:
            fp = ProgressCallingFile(fp, int(size), progress)

        try:
            self.put(key, data=fp, acl=acl, metadata=metadata,
                     mimetype=mimetype, transformer=transformer,
                     headers=headers)
        finally:
            if do_close:
                fp.close()

class UnimplementedStreamingMixin(StreamingMixin):
    exc_text = """it appears you forgot to install a streaming http library\n
for example, you could run ``sudo easy_install poster``
"""

    @classmethod
    def build_opener(cls):
        raise NotImplementedError(cls.exc_text)

default_stream_mixin = UnimplementedStreamingMixin

try:
    from poster.streaminghttp import StreamingHTTPHandler
except ImportError:
    pass
else:
    class PosterStreamingMixin(StreamingMixin):
        @classmethod
        def build_opener(cls):
            return urllib.request.build_opener(StreamingHTTPHandler)

    default_stream_mixin = PosterStreamingMixin

class StreamingSCSBucket(default_stream_mixin, SCSBucket): pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
