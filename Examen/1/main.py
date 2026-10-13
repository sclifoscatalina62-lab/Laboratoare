from checker import (
    build_url,
    is_https,
    show_response,
    check_site,
    scan_sites,
    check_headers,
    retry_check
)

def main():
    print("--- Partea 1 ---")
    print("build_url fara slash:", build_url("example.com", "login"))
    print("build_url cu slash:", build_url("example.com", "/login"))
    print("is_https (True):", is_https("https://example.com"))
    print("is_https (False):", is_https("http://example.com"))

    print("\n--- Partea 2 ---")
    print("show_response(https://example.com):")
    show_response("https://example.com")

    print("\n--- Partea 3 ---")
    print("check_site (site activ):", check_site("https://example.com"))
    print("check_site (site inexistent):", check_site("http://this-site-does-not-exist.invalid"))

    print("\n--- Partea 4 ---")
    scan_sites()

    print("\n--- Partea 5 ---")
    print("check_headers (cu antete):", check_headers("https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff"))
    print("check_headers (fără antete):", check_headers("https://example.com"))

    print("\n--- Partea 6 ---")
    print("retry_check (200 OK):", retry_check("https://httpbin.org/status/200"))
    print("retry_check (404 Not Found):", retry_check("https://httpbin.org/status/404"))
    print("retry_check (500 Error):", retry_check("https://httpbin.org/status/500"))
    print("retry_check (site inexistent):", retry_check("http://this-site-does-not-exist.invalid"))

if __name__ == "__main__":
    main()
