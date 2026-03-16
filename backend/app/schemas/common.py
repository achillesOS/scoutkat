from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedResponse(AppBaseModel):
    timestamp: datetime

