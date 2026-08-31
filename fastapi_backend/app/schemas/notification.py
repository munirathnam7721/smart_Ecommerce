from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    user_id: int

    type: str

    message: str

    read_status: bool

    timestamp: datetime