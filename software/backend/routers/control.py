from fastapi import APIRouter, HTTPException, status

from ..control import motor, servo

router = APIRouter()


@router.post("/control/", status_code=status.HTTP_200_OK)
async def move(angle: float, speed: float):
    try:
        servo.turn(angle)
        motor.move(speed)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid angle or speed")

    return {"message": "Car moved"}


@router.post("/control/stop", status_code=status.HTTP_200_OK)
async def stop():
    motor.move(0)
    servo.turn(0)
    return {"message": "Car stopped"}
