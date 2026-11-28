
import os
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Response

# Room Booking Service configuration
ROOM_BOOKING_URL = os.getenv(
    "ROOM_BOOKING_URL",
    "http://127.0.0.1:8001"
)

REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "3"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Create FastAPI application
app = FastAPI(title="Exam Scheduler Service")


# Exam request model
class ExamRequest(BaseModel):
    exam_id: str
    course_code: str
    day: date
    start_hour: int = Field(ge=8, le=19)
    end_hour: int = Field(ge=9, le=20)
    students_count: int = Field(gt=0)


import asyncio


async def request_with_retry(method, url, **kwargs):
    for attempt in range(MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT
            ) as client:
                response = await client.request(
                    method,
                    url,
                    **kwargs
                )

                # Retry only on server errors (5xx)
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        "Server error",
                        request=response.request,
                        response=response
                    )

                return response

        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError
        ) as error:

            # Do not retry client errors such as 404 or 409
            if isinstance(error, httpx.HTTPStatusError):
                if error.response.status_code < 500:
                    raise

            if attempt == MAX_RETRIES:
                raise

            delay = 0.5 * (2 ** attempt)
            await asyncio.sleep(delay)

@app.get("/config")
async def get_config():
    return {
        "room_booking_url": ROOM_BOOKING_URL,
        "request_timeout": REQUEST_TIMEOUT,
        "max_retries": MAX_RETRIES
    }


async def get_available_rooms(exam: ExamRequest):
    # Get all rooms
    response = await request_with_retry(
        "GET",
        f"{ROOM_BOOKING_URL}/rooms"
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve rooms"
        )

    rooms = response.json()

    available_rooms = []

    # Check bookings for each room
    for room in rooms:
        if room["capacity"] < exam.students_count:
            continue

        bookings_response = await request_with_retry(
            "GET",
            f"{ROOM_BOOKING_URL}/rooms/{room['id']}/bookings"
        )

        if bookings_response.status_code != 200:
            raise HTTPException(
                status_code=503,
                detail="Could not retrieve room bookings"
            )

        bookings = bookings_response.json()

        # Check for time conflicts
        conflict = any(
            booking["date"] == exam.day.isoformat()
            and exam.start_hour < booking["end_hour"]
            and booking["start_hour"] < exam.end_hour
            for booking in bookings
        )

        if not conflict:
            available_rooms.append(room)

    # Choose the smallest suitable room
    available_rooms.sort(key=lambda room: room["capacity"])

    return available_rooms


@app.post("/exams", status_code=201)
async def create_exam(exam: ExamRequest, response: Response):

    # Validate exam hours
    if exam.end_hour <= exam.start_hour:
        raise HTTPException(
            status_code=422,
            detail="End hour must be greater than start hour"
        )

    try:
        # Find available rooms
        available_rooms = await get_available_rooms(exam)

        if not available_rooms:
            raise HTTPException(
                status_code=409,
                detail="No suitable room available"
            )

        # Select the smallest available room
        selected_room = available_rooms[0]

        # Use a fixed booking ID based on exam ID
        booking_id = f"exam-{exam.exam_id}"

        # Check if this exam was already booked
        existing_response = await request_with_retry(
            "GET",
            f"{ROOM_BOOKING_URL}/bookings/{booking_id}"
        )

        if existing_response.status_code == 200:
            existing_booking = existing_response.json()

            room_response = await request_with_retry(
                "GET",
                f"{ROOM_BOOKING_URL}/rooms/{existing_booking['room_id']}"
            )

            if room_response.status_code != 200:
                raise HTTPException(
                    status_code=503,
                    detail="Could not retrieve existing room"
                )

            response.status_code = 200

            return {
                "exam_id": exam.exam_id,
                "course_code": exam.course_code,
                "room": room_response.json(),
                "booking": existing_booking
            }
        # Create the booking
        booking_response = await request_with_retry(
            "PUT",
            f"{ROOM_BOOKING_URL}/bookings/{booking_id}",
            json={
                "room_id": selected_room["id"],
                "date": exam.day.isoformat(),
                "start_hour": exam.start_hour,
                "end_hour": exam.end_hour,
                "purpose": f"Exam {exam.course_code}"
            }
        )

        if booking_response.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail="Room is no longer available"
            )

        if booking_response.status_code not in (200, 201):
            raise HTTPException(
                status_code=503,
                detail="Could not book the room"
            )

        return {
            "exam_id": exam.exam_id,
            "course_code": exam.course_code,
            "room": selected_room,
            "booking": booking_response.json()
        }

    except HTTPException:
        raise

    except (httpx.TimeoutException, httpx.ConnectError):
        raise HTTPException(
            status_code=503,
            detail="Room Booking Service is unavailable"
        )
