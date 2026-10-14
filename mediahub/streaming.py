"""Streaming progressif avec support des requêtes HTTP Range (lecture/seek vidéo mobile)."""
import re

from django.http import HttpResponse, StreamingHttpResponse

RANGE_RE = re.compile(r"bytes\s*=\s*(\d*)\s*-\s*(\d*)", re.IGNORECASE)
CHUNK_SIZE = 1024 * 512


def _iterate(handle, start, length):
    try:
        handle.seek(start)
        remaining = length
        while remaining > 0:
            data = handle.read(min(CHUNK_SIZE, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data
    finally:
        handle.close()


def range_file_response(request, fieldfile, content_type, filename, as_attachment=False):
    size = fieldfile.size
    start, end, partial = 0, size - 1, False

    match = RANGE_RE.match(request.headers.get("Range", ""))
    if match and size > 0:
        first, last = match.groups()
        if first == "" and last == "":
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{size}"})
        if first == "":  # "bytes=-500" : les 500 derniers octets
            start = max(size - int(last), 0)
        else:
            start = int(first)
            if last:
                end = min(int(last), size - 1)
        if start > end or start >= size:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{size}"})
        partial = True

    length = end - start + 1 if size else 0
    handle = fieldfile.storage.open(fieldfile.name, "rb")
    response = StreamingHttpResponse(
        _iterate(handle, start, length),
        status=206 if partial else 200,
        content_type=content_type or "application/octet-stream",
    )
    response["Accept-Ranges"] = "bytes"
    response["Content-Length"] = str(length)
    if partial:
        response["Content-Range"] = f"bytes {start}-{end}/{size}"
    disposition = "attachment" if as_attachment else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response
