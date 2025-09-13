import socket
import threading
import uuid

HOST = "0.0.0.0"
PORT = 8080

def parse_headers(request_text):
    lines = request_text.split("\r\n")
    request_line = lines[0] if lines else ""
    headers = {}
    for line in lines[1:]:
        if not line:
            break
        parts = line.split(":", 1)
        if len(parts) == 2:
            headers[parts[0].strip()] = parts[1].strip()
    return request_line, headers

def handle_client(conn, addr):
    try:
        data = conn.recv(4096).decode(errors="ignore")
        if not data:
            conn.close()
            return

        request_line, headers = parse_headers(data)
        cookie = headers.get("Cookie")

        if cookie:
            # Look for "user="
            for part in cookie.split(";"):
                part = part.strip()
                if part.startswith("user="):
                    value = part.split("=", 1)[1]
                    body = f"<html><body><h1>Welcome back, {value}!</h1></body></html>"
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        f"Content-Length: {len(body.encode())}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        f"{body}"
                    )
                    conn.sendall(response.encode())
                    conn.close()
                    return

        # No cookie → assign new
        user_id = "User" + uuid.uuid4().hex[:6]
        body = f"<html><body><h1>Welcome, {user_id}!</h1></body></html>"
        headers_out = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Set-Cookie: user={user_id}; Max-Age=86400; Path=/\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        conn.sendall(headers_out.encode() + body.encode())

    finally:
        conn.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Cookie server running at http://{HOST}:{PORT}/")
        try:
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Server stopped.")

if __name__ == "__main__":
    run_server()
