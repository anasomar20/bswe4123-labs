# Campus Room Booking Service

## 1. Project Description

This project implements a REST API for a university campus room booking service using FastAPI, Pydantic, and HTTPX.

The service allows students and staff to manage rooms and bookings while preventing overlapping reservations.

Room and booking data are stored in memory.

## 2. API Design

| Method | URI                         | Request Body    | Success Status       | Error Status  |
| ------ | --------------------------- | --------------- | -------------------- | ------------- |
| GET    | `/rooms`                    | None            | 200 OK               | None          |
| POST   | `/rooms`                    | Room details    | 201 Created          | 409, 422      |
| GET    | `/rooms/{room_id}`          | None            | 200 OK               | 404           |
| PUT    | `/bookings/{booking_id}`    | Booking details | 201 Created / 200 OK | 404, 409, 422 |
| GET    | `/bookings/{booking_id}`    | None            | 200 OK               | 404           |
| GET    | `/rooms/{room_id}/bookings` | None            | 200 OK               | 404           |
| DELETE | `/bookings/{booking_id}`    | None            | 204 No Content       | 404           |

### Example Room Request

```json
{
  "id": "B205",
  "building": "Engineering",
  "capacity": 30
}
```

### Example Booking Request

```json
{
  "room_id": "B205",
  "date": "2026-12-01",
  "start_hour": 10,
  "end_hour": 12,
  "purpose": "Study group"
}
```

## 3. Validation and Error Handling

- **200 OK:** The requested resource was retrieved or updated.
- **201 Created:** A new room or booking was created.
- **204 No Content:** A booking was successfully deleted.
- **404 Not Found:** The requested room or booking does not exist.
- **409 Conflict:** A duplicate room or overlapping booking was detected.
- **422 Unprocessable Entity:** The submitted data failed validation.

Booking hours must be between 8 and 20, and the end hour must be greater than the start hour.

The service prevents overlapping bookings for the same room on the same date.

Two bookings are considered overlapping when:

`new_start < existing_end AND existing_start < new_end`

Therefore, bookings from 10:00–12:00 and 12:00–13:00 are allowed.

## 4. Idempotent Booking Creation

The service uses the PUT method with a client-selected booking ID.

For example:

`PUT /bookings/booking-001`

When the booking ID does not exist, the service creates the booking and returns **201 Created**.

When the same request is sent again using the same booking ID, the service updates the existing booking and returns **200 OK** instead of creating a duplicate.

This makes retrying the same request safe.

## 5. Test Results

The automated tests were implemented in `test_bookings.py` using HTTPX.

### Command

```powershell
python test_bookings.py
```

### Test Output

```text
=== Campus Room Booking API Tests ===

GET    /rooms                              Status: 200
POST   /rooms                              Status: 201
POST   /rooms                              Status: 409
GET    /rooms/B205                         Status: 200
GET    /rooms/Z999                         Status: 404
PUT    /bookings/booking-001               Status: 201
PUT    /bookings/booking-001               Status: 200
PUT    /bookings/booking-002               Status: 409
PUT    /bookings/booking-003               Status: 201
PUT    /bookings/booking-004               Status: 422
PUT    /bookings/booking-005               Status: 404
GET    /bookings/booking-001               Status: 200
GET    /bookings/booking-999               Status: 404
GET    /rooms/B205/bookings                Status: 200
GET    /rooms/Z999/bookings                Status: 404
DELETE /bookings/booking-003               Status: 204
GET    /bookings/booking-003               Status: 404
DELETE /bookings/booking-999               Status: 404

=== All tests passed successfully! ===
```

All 18 automated tests passed successfully.

## 6. Project Files

- `booking_service.py`: FastAPI application and API endpoints.
- `test_bookings.py`: Automated API tests using HTTPX.
- `README.md`: Project documentation.
