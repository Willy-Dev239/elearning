import mimetypes
import os
import re

from django.http import HttpResponse, StreamingHttpResponse


def stream_file(request, path, chunk=64 * 1024):
    """Envoie un fichier avec support HTTP Range (lecture/avance rapide vidéo)."""
    size = os.path.getsize(path)
    start, end, status = 0, size - 1, 200
    m = re.match(r"bytes=(\d*)-(\d*)", request.headers.get("Range", ""))
    if m and (m.group(1) or m.group(2)):
        if m.group(1):
            start = int(m.group(1))
            if m.group(2):
                end = min(int(m.group(2)), size - 1)
        else:  # suffixe : les N derniers octets
            start = max(size - int(m.group(2)), 0)
        if start > end or start >= size:
            r = HttpResponse(status=416)
            r["Content-Range"] = f"bytes */{size}"
            return r
        status = 206
    length = end - start + 1

    def reader():
        with open(path, "rb") as f:
            f.seek(start)
            left = length
            while left > 0:
                data = f.read(min(chunk, left))
                if not data:
                    break
                left -= len(data)
                yield data

    resp = StreamingHttpResponse(reader(), status=status,
                                 content_type=mimetypes.guess_type(path)[0] or "application/octet-stream")
    resp["Accept-Ranges"] = "bytes"
    resp["Content-Length"] = str(length)
    if status == 206:
        resp["Content-Range"] = f"bytes {start}-{end}/{size}"
    return resp
