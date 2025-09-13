import http.server
import socketserver
import hashlib
import os
from email.utils import formatdate, parsedate_to_datetime
from http import HTTPStatus
from datetime import timezone
import io

PORT = 8000
INDEX_FILE = "index.html"

class CachingHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        if self.path in ("/", "/index.html"):
            try:
                stat = os.stat(INDEX_FILE)
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return None

            with open(INDEX_FILE, "rb") as f:
                content = f.read()

            # Generate ETag (hash of content)
            etag = hashlib.md5(content).hexdigest()
            last_mod = formatdate(stat.st_mtime, usegmt=True)

            inm = self.headers.get("If-None-Match")
            ims = self.headers.get("If-Modified-Since")

            # If-None-Match check
            if inm is not None and inm.strip() == etag:
                self.send_response(HTTPStatus.NOT_MODIFIED)
                self.send_header("ETag", etag)
                self.send_header("Last-Modified", last_mod)
                self.end_headers()
                return None

            # If-Modified-Since check
            if ims is not None:
                try:
                    client_dt = parsedate_to_datetime(ims)
                    server_dt = parsedate_to_datetime(last_mod)
                    if server_dt <= client_dt.replace(tzinfo=timezone.utc):
                        self.send_response(HTTPStatus.NOT_MODIFIED)
                        self.send_header("ETag", etag)
                        self.send_header("Last-Modified", last_mod)
                        self.end_headers()
                        return None
                except Exception:
                    pass

            # Otherwise return full response
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("ETag", etag)
            self.send_header("Last-Modified", last_mod)
            self.end_headers()
            return io.BytesIO(content)
        else:
            return super().send_head()

    def do_GET(self):
        result = self.send_head()
        if result:
            self.wfile.write(result.read())

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CachingHandler) as httpd:
        print(f"Serving on port {PORT}, open http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
