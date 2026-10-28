import httpx

BASE = "http://localhost:8000"


def show(title, data):
    print(f"\n=== {title} ===")
    print(data)


def main():
    show("health", httpx.get(f"{BASE}/health").json())
    show("grid config", httpx.get(f"{BASE}/api/grid/config").json())
    show("grid health", httpx.get(f"{BASE}/api/grid/health").json())

    httpx.post(f"{BASE}/api/grid/clear")

    r1 = httpx.post(f"{BASE}/api/prompt", json={"prompt": "demo prompt"}).json()
    show("prompt #1 (expect miss)", r1)

    r2 = httpx.post(f"{BASE}/api/prompt", json={"prompt": "demo prompt"}).json()
    show("prompt #2 (expect hit)", r2)

    show("grid stats", httpx.get(f"{BASE}/api/grid/stats").json())

    bad = httpx.post(f"{BASE}/api/prompt", json={"prompt": ""})
    show("empty prompt (expect 400)", {"status_code": bad.status_code, "body": bad.json()})


if __name__ == "__main__":
    main()
