
from datetime import date

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, model_validator
import asyncio
import os

app = FastAPI(title="Campus Room Booking Service")

@app.middleware("http")
async def add_delay(request, call_next):
    delay = float(os.getenv("ROOM_BOOKING_DELAY", "0"))

    if delay > 0:
        await asyncio.sleep(delay)

    response = await call_next(request)
    return response
    
# In-memory storage
rooms = {}
bookings = {}


# Models
class RoomCreate(BaseModel):
    id: str
    building: str
    capacity: int = Field(gt=0)


class BookingCreate(BaseModel):
    room_id: str
    date: date
    start_hour: int = Field(ge=8, le=20)
    end_hour: int = Field(ge=8, le=20)
    purpose: str

    @model_validator(mode="after")
    def validate_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self


# Room endpoints
@app.get("/rooms")
def get_rooms():
    return list(rooms.values())


@app.post("/rooms", status_code=201)
def create_room(room: RoomCreate):
    if room.id in rooms:
        raise HTTPException(
            status_code=409,
            detail="Room already exists"
        )

    rooms[room.id] = room.model_dump()
    return rooms[room.id]


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    return rooms[room_id]


# Booking endpoints
@app.put("/bookings/{booking_id}")
def create_or_update_booking(
    booking_id: str,
    booking: BookingCreate,
    response: Response
):
    if booking.room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    new_booking = booking.model_dump(mode="json")

    # Check for overlapping bookings
    for existing_id, existing in bookings.items():
        if existing_id == booking_id:
            continue

        same_room = existing["room_id"] == booking.room_id
        same_date = existing["date"] == new_booking["date"]

        overlaps = (
            booking.start_hour < existing["end_hour"]
            and existing["start_hour"] < booking.end_hour
        )

        if same_room and same_date and overlaps:
            raise HTTPException(
                status_code=409,
                detail="Room is already booked during this time"
            )

    is_new = booking_id not in bookings

    bookings[booking_id] = {
        "id": booking_id,
        **new_booking
    }

    response.status_code = 201 if is_new else 200

    return bookings[booking_id]


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail="Booking not found")

    return bookings[booking_id]


@app.get("/rooms/{room_id}/bookings")
def get_room_bookings(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    return [
        booking
        for booking in bookings.values()
        if booking["room_id"] == room_id
    ]


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail="Booking not found")

    del bookings[booking_id]
    return Response(status_code=204)
