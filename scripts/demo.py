import httpx

BASE = "http://127.0.0.1:8000"


def show(title, data):
    print(f"\n=== {title} ===")
    print(data)


def main():
    try:
        with httpx.Client(base_url=BASE, timeout=10.0) as client:
            response = client.get("/health")
            response.raise_for_status()
            show("health", response.json())

            response = client.get("/api/grid/config")
            response.raise_for_status()
            show("grid config", response.json())

            response = client.get("/api/grid/health")
            response.raise_for_status()
            show("grid health", response.json())

            response = client.post("/api/grid/clear")
            response.raise_for_status()
            show("clear grid", response.json())

            first = client.post(
                "/api/prompt",
                json={"prompt": "demo prompt"},
            )
            first.raise_for_status()
            first_result = first.json()
            if first_result["cache"] != "miss":
                raise RuntimeError("The first prompt should be a cache miss.")
            show("prompt #1 (expect miss)", first_result)

            second = client.post(
                "/api/prompt",
                json={"prompt": "demo prompt"},
            )
            second.raise_for_status()
            second_result = second.json()
            if second_result["cache"] != "hit":
                raise RuntimeError("The repeated prompt should be a cache hit.")
            show("prompt #2 (expect hit)", second_result)

            response = client.get("/api/grid/stats")
            response.raise_for_status()
            show("grid stats", response.json())

            bad = client.post(
                "/api/prompt",
                json={"prompt": ""},
            )
            if bad.status_code != 400:
                raise RuntimeError(
                    "Expected an empty prompt to return HTTP 400, "
                    f"got HTTP {bad.status_code}: {bad.text}"
                )
            show(
                "empty prompt (expect 400)",
                {"status_code": bad.status_code, "body": bad.json()},
            )
    except httpx.ConnectError as exc:
        raise SystemExit(
            "Cannot connect to the API at http://127.0.0.1:8000. "
            "Start it in another terminal with:\n"
            "  .venv\\Scripts\\python -m uvicorn app.main:app --reload "
            "--host 127.0.0.1 --port 8000"
        ) from exc
    except httpx.HTTPError as exc:
        raise SystemExit(f"API request failed: {exc}") from exc


if __name__ == "__main__":
    main()
