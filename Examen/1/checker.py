import requests

SITES = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    host_clean = host.rstrip('/')
    path_clean = path.lstrip('/')
    return f"https://{host_clean}/{path_clean}"


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.lower().startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type', 'unknown')}")
    except requests.RequestException:
        print("Eroare la conexiune (site inaccesibil)")


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        r = requests.get(url, timeout=5)
        content_type = r.headers.get("Content-Type", "").split(";")[0]
        length = len(r.content)
        server = r.headers.get("Server", "unknown")
        
        return {
            "status": r.status_code,
            "content_type": content_type,
            "length": length,
            "server": server
        }
    except requests.RequestException:
        return {"status": None, "error": "conexiune esuata"}


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    results = []
    for url in SITES:
        info = check_site(url)
        info["url"] = url
        results.append(info)

    successful = [item for item in results if item.get("status") == 200]
    failed = [item for item in results if item.get("status") != 200]

    # Sortează după length, cel mai mare primul
    successful.sort(key=lambda x: x.get("length", 0), reverse=True)

    for site in successful:
        print(f"{site['url']} -> 200, {site['length']} octeți")

    print(f"Reușite: {len(successful)} Eșuate: {len(failed)}")


def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        r = requests.get(url, timeout=5)
        received_headers_lower = {k.lower(): v for k, v in r.headers.items()}
        
        present = []
        missing = []

        for h in SECURITY_HEADERS:
            if h.lower() in received_headers_lower:
                present.append(h)
            else:
                missing.append(h)

        score = int((len(present) / len(SECURITY_HEADERS)) * 100)

        return {
            "present": present,
            "missing": missing,
            "score": score
        }
    except requests.RequestException:
        return {"status": None, "error": "conexiune esuata"}


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    last_status = None
    actual_attempts = 0

    for _ in range(attempts):
        actual_attempts += 1
        try:
            r = requests.get(url, timeout=5)
            last_status = r.status_code
            
            # Dacă răspunsul are un status < 500 (2xx, 3xx, 4xx), ne oprim
            if last_status < 500:
                return {
                    "status": last_status,
                    "attempts": actual_attempts
                }
        except requests.RequestException:
            last_status = None

    res = {
        "status": last_status,
        "attempts": actual_attempts
    }
    if last_status is None:
        res["error"] = "conexiune esuata"

    return res
