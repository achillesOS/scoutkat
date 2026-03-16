from app.schemas.common import AppBaseModel


class TokenResponse(AppBaseModel):
    id: str
    symbol: str
    name: str
    market_type: str
    is_active: bool

