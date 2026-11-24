
import time
import httpx

SERVICES = {
    "Service 1": "http://127.0.0.1:8001/health",
    "Service 2": "http://127.0.0.1:8002/health",
    "Service 3": "http://127.0.0.1:8003/health",
}

FAILURE_COUNTS = {
    name: 0 for name in SERVICES
}

MAX_FAILURES = 3
TIMEOUT = 2.0
CHECK_INTERVAL = 2.0



def check_service(client, name, url):
    start_time = time.perf_counter()

    try:
        response = client.get(url, timeout=TIMEOUT)
        response.raise_for_status()

        response_time = (time.perf_counter() - start_time) * 1000

        # Reset failure counter after a successful response
        FAILURE_COUNTS[name] = 0

        if response_time > 500:
            status = "SLOW"
        else:
            status = "UP"

        print(f"{name}: {status} - {response_time:.2f} ms")

    except (httpx.RequestError, httpx.HTTPStatusError):
        FAILURE_COUNTS[name] += 1

        if FAILURE_COUNTS[name] >= MAX_FAILURES:
            print(f"{name}: DOWN - {FAILURE_COUNTS[name]} consecutive failures")
        else:
            print(
                f"{name}: SUSPECT - "
                f"{FAILURE_COUNTS[name]}/{MAX_FAILURES} failures"
            )


def monitor():
    with httpx.Client() as client:
        while True:
            print("\n--- Service Health Check ---")

            for name, url in SERVICES.items():
                check_service(client, name, url)

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()
