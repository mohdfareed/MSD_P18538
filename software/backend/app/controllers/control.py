from fastapi import APIRouter, HTTPException, status

from ..models.movement import Movement
from ..services.control import motors

router = APIRouter()


@router.post("/control/movement", status_code=status.HTTP_200_OK)
async def move(movement: Movement):
    try:
        motors.drive(movement)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid angle or speed")

    return {"message": "Car moved"}

@router.post("/control/siren")
async def enableSiren(bool: enabled):
    try:
        # todo: Implement the GPIO to drive the Siren
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid value")
    
    return {"message": "Siren updated"}
