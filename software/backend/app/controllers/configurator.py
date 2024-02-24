import logging

from fastapi import APIRouter, HTTPException, status

from ..models.config import Config
from ..services import configurator

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config")
async def get_config():
    config = await configurator.get_config()
    LOGGER.debug("Sending config: %s", config)
    return config


@router.put("/config")
async def set_configs(new_config: Config):
    try:
        await configurator.set_config(new_config)
        LOGGER.debug("Config updated to %s", new_config)
    except configurator.ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        LOGGER.exception("Error updating config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return {"message": "Config updated successfully"}
