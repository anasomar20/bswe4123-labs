
import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_request(client, method, path, expected_status, json=None):
    response = client.request(method, path, json=json)

    print(
        f"{method:6} {path:35} "
        f"Status: {response.status_code}"
    )

    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}: "
        f"{response.text}"
    )

    return response


def run_tests():
    with httpx.Client(base_url=BASE_URL) as client:

        print("\n=== Campus Room Booking API Tests ===\n")

        # 1. Get all rooms
        test_request(client, "GET", "/rooms", 200)

        # 2. Create a room
        room = {
            "id": "B205",
            "building": "Engineering",
            "capacity": 30
        }

        test_request(client, "POST", "/rooms", 201, room)

        # 3. Duplicate room
        test_request(client, "POST", "/rooms", 409, room)

        # 4. Get existing room
        test_request(client, "GET", "/rooms/B205", 200)

        # 5. Get missing room
        test_request(client, "GET", "/rooms/Z999", 404)

        # 6. Create first booking
        booking = {
            "room_id": "B205",
            "date": "2026-12-01",
            "start_hour": 10,
            "end_hour": 12,
            "purpose": "Study group"
        }

        test_request(
            client, "PUT", "/bookings/booking-001",
            201, booking
        )

        # 7. Repeat the same request (idempotency)
        test_request(
            client, "PUT", "/bookings/booking-001",
            200, booking
        )

        # 8. Overlapping booking
        overlapping_booking = {
            "room_id": "B205",
            "date": "2026-12-01",
            "start_hour": 11,
            "end_hour": 13,
            "purpose": "Team meeting"
        }

        test_request(
            client, "PUT", "/bookings/booking-002",
            409, overlapping_booking
        )

        # 9. Adjacent booking (allowed)
        adjacent_booking = {
            "room_id": "B205",
            "date": "2026-12-01",
            "start_hour": 12,
            "end_hour": 13,
            "purpose": "Lab session"
        }

        test_request(
            client, "PUT", "/bookings/booking-003",
            201, adjacent_booking
        )

        # 10. Invalid time range
        invalid_booking = {
            "room_id": "B205",
            "date": "2026-12-02",
            "start_hour": 14,
            "end_hour": 12,
            "purpose": "Invalid booking"
        }

        test_request(
            client, "PUT", "/bookings/booking-004",
            422, invalid_booking
        )

        # 11. Booking for a missing room
        missing_room_booking = {
            "room_id": "Z999",
            "date": "2026-12-03",
            "start_hour": 10,
            "end_hour": 12,
            "purpose": "Missing room test"
        }

        test_request(
            client, "PUT", "/bookings/booking-005",
            404, missing_room_booking
        )

        # 12. Get existing booking
        test_request(
            client, "GET", "/bookings/booking-001", 200
        )

        # 13. Get missing booking
        test_request(
            client, "GET", "/bookings/booking-999", 404
        )

        # 14. Get bookings for an existing room
        test_request(
            client, "GET", "/rooms/B205/bookings", 200
        )

        # 15. Get bookings for a missing room
        test_request(
            client, "GET", "/rooms/Z999/bookings", 404
        )

        # 16. Delete an existing booking
        test_request(
            client, "DELETE", "/bookings/booking-003", 204
        )

        # 17. Verify that the booking was deleted
        test_request(
            client, "GET", "/bookings/booking-003", 404
        )

        # 18. Delete a missing booking
        test_request(
            client, "DELETE", "/bookings/booking-999", 404
        )

        print("\n=== All tests passed successfully! ===")


if __name__ == "__main__":
    run_tests()
