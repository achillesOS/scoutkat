from app.schemas.common import AppBaseModel


class HealthResponse(AppBaseModel):
    status: str
    environment: str

