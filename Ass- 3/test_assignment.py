import requests

# --- Part 1: Caching ---
print("=== Part 1: Caching ===")
url1 = "http://localhost:8000/"
r1 = requests.get(url1)
print("First response:", r1.status_code, r1.headers.get("ETag"))

etag = r1.headers.get("ETag")
last_mod = r1.headers.get("Last-Modified")

# Test If-None-Match
r2 = requests.get(url1, headers={"If-None-Match": etag})
print("If-None-Match response:", r2.status_code)

# Test If-Modified-Since
r3 = requests.get(url1, headers={"If-Modified-Since": last_mod})
print("If-Modified-Since response:", r3.status_code)

# --- Part 2: Cookies ---
print("\n=== Part 2: Cookies ===")
url2 = "http://localhost:8080/"
r4 = requests.get(url2)
print("First visit:", r4.text.strip(), "Set-Cookie:", r4.headers.get("Set-Cookie"))

cookie = r4.cookies.get("user")
r5 = requests.get(url2, cookies={"user": cookie})
print("Second visit:", r5.text.strip())
