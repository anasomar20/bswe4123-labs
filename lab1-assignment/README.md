# Lab Assignment 1: Is the Service Up, Slow or Down?

## 1. Project Description

This project implements a health monitoring system for three FastAPI service instances running on different ports.

Each service provides a `/health` endpoint that returns its status and uptime. The monitoring program checks all services every two seconds and classifies them as UP, SLOW, SUSPECT, or DOWN.

## 2. Project Files

- `service.py`: Implements the FastAPI service, health endpoint, and configurable health delay.
- `monitor.py`: Monitors the three services using HTTPX.
- `README.md`: Documents the implementation and test results.

## 3. Running the Services

The three service instances run on:

| Service   | Port |
| --------- | ---- |
| Service 1 | 8001 |
| Service 2 | 8002 |
| Service 3 | 8003 |

Run Service 1:

```powershell
python -m uvicorn service:app --host 127.0.0.1  --port 8002
```

Run Service 3:

```powershell
python -m uvicorn service:app --host 127.0.0.1 --port 8003
```

## 4. Running the Monitor

Run the monitoring program:

```powershell
python monitor.py
```

The monitor checks all services every two seconds using HTTPX.

## 5. Monitoring Results

The monitor uses the following classifications:

- **UP:** The service responds within 500 milliseconds.
- **SLOW:** The response time exceeds 500 milliseconds.
- **SUSPECT:** The service has failed one or two consecutive checks.
- **DOWN:** The service has failed three consecutive checks.

### Test 1: All Services Running

All three services responded successfully and were classified as UP.

### Test 2: Service Unavailable

Service 3 was stopped manually.

The monitor detected the connection failures and classified it as DOWN after three consecutive failures in the improved version.--port 8001
```

Run Service 2 with a delay of 0.8 seconds:

```powershell
$env:HEALTH_DELAY="0.8"
python -m uvicorn service:app --host 127.0.0.1

### Test 3: Slow Service

Service 2 was configured with a delay of 0.8 seconds.

The observed response times were:

- First check: 806.78 ms.
- Second check: 808.52 ms.

Service 2 was correctly classified as SLOW.

## 6. Improved Failure Detection

The monitor was improved to avoid declaring a service DOWN after a single failed request.

It counts consecutive failures:

- First failure: SUSPECT (1/3).
- Second failure: SUSPECT (2/3).
- Third consecutive failure: DOWN (3 consecutive failures).

When a request succeeds, its failure counter resets to zero.

This reduces false DOWN alerts caused by temporary network problems.

### Actual Test Output

```text
Service 1: UP - 9.89 ms
Service 2: SLOW - 827.40 ms
Service 3: SUSPECT - 1/3 failures

Service 1: UP - 7.03 ms
Service 2: SLOW - 808.94 ms
Service 3: SUSPECT - 2/3 failures

Service 1: UP - 7.14 ms
Service 2: SLOW - 809.81 ms
Service 3: DOWN - 3 consecutive failures
```

## 7. Timeout and Retry Discussion

The monitor uses a timeout of 2 seconds and requires three consecutive failures before declaring a service DOWN.

A shorter timeout detects failures faster but may incorrectly classify slow services or temporary network delays as unavailable.

A longer timeout reduces false failure detections but delays the identification of unavailable services.

Using three consecutive failures improves reliability by reducing false alarms. However, it also increases the time needed to detect a real failure.

## 8. Conclusion

This assignment demonstrates how to monitor multiple distributed services, measure response times, detect slow or unavailable services, and improve failure detection using consecutive failure counting.
