from fastapi import APIRouter, status

from ..services import control

router = APIRouter(prefix="/control")


@router.post("/forward", status_code=status.HTTP_200_OK)
async def drive_forward():
    await control.forward(True)
    return {"message": "Forward"}


@router.delete("/forward", status_code=status.HTTP_200_OK)
async def stop_forward():
    await control.forward(False)
    return {"message": "Stop"}


@router.post("/backward", status_code=status.HTTP_200_OK)
async def drive_backward():
    await control.backward(True)
    return {"message": "Backward"}


@router.delete("/backward", status_code=status.HTTP_200_OK)
async def stop_backward():
    await control.backward(False)
    return {"message": "Stop"}


@router.post("/left", status_code=status.HTTP_200_OK)
async def drive_left():
    await control.left(True)
    return {"message": "Left"}


@router.delete("/left", status_code=status.HTTP_200_OK)
async def stop_left():
    await control.left(False)
    return {"message": "Stop"}


@router.post("/right", status_code=status.HTTP_200_OK)
async def drive_right():
    await control.right(True)
    return {"message": "Right"}


@router.delete("/right", status_code=status.HTTP_200_OK)
async def stop_right():
    await control.right(False)
    return {"message": "Stop"}


@router.post("/siren", status_code=status.HTTP_200_OK)
async def enable_siren():
    await control.siren(True)
    return {"message": "Siren on"}


@router.post("/siren", status_code=status.HTTP_200_OK)
async def disable_siren():
    await control.siren(False)
    return {"message": "Siren off"}