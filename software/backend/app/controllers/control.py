from fastapi import APIRouter, HTTPException, status

from ..models.movement import Movement
from ..services.control import motors

router = APIRouter()


@router.post("/control/", status_code=status.HTTP_200_OK)
async def move(movement: Movement):
    try:
        motors.drive(movement)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid angle or speed")

    return {"message": "Car moved"}


@router.post("/control/stop", status_code=status.HTTP_200_OK)
async def stop():
    motors.drive(Movement(speed=0, angle=0))
    return {"message": "Car stopped"}
