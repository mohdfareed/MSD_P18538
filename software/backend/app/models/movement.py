from pydantic import BaseModel, validator


class Movement(BaseModel):
    speed: float
    angle: float

    @validator("speed", "angle")
    def check_range(cls, v):
        if abs(v) > 1:
            raise ValueError("Value must be between -1 and 1")
        return v
