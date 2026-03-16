from app.schemas.common import AppBaseModel
from app.schemas.token import TokenResponse


class WatchlistResponse(AppBaseModel):
    items: list[TokenResponse]


class WatchlistCreateRequest(AppBaseModel):
    token_id: str

