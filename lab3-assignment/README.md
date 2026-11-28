# Lab Assignment 3 - Exam Scheduler

## Services
- Exam Scheduler: Port 8000
- Room Booking: Port 8001

## Run Room Booking
python -m uvicorn booking_service:app --port 8001

## Run Exam Scheduler
python -m uvicorn exam_scheduler:app --reload --port 8000

## Configuration
GET /config displays:
- ROOM_BOOKING_URL
- REQUEST_TIMEOUT
- MAX_RETRIES

## Main Endpoint
POST /exams

The scheduler selects the smallest available room that can accommodate the students.

## Tests
- 201: Exam created successfully.
- 200: Repeated exam returns the existing booking.
- 409: No suitable room available.

## Retry
Retries timeout, connection errors, and server errors using exponential backoff:
0.5, 1, and 2 seconds.

## Idempotency
A fixed booking ID based on exam_id is used.

## Limitation
Room Booking uses in-memory storage, so data is lost after restarting the service.
