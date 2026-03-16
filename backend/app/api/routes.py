from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.config import get_settings
from app.core.container import get_signal_service, get_token_service, get_watchlist_service
from app.schemas.health import HealthResponse
from app.schemas.signal import SignalResponse
from app.schemas.token import TokenResponse
from app.schemas.watchlist import WatchlistCreateRequest, WatchlistResponse
from app.services.signal_service import SignalService
from app.services.token_service import TokenService
from app.services.watchlist_service import WatchlistService


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", environment=settings.app_env)


@router.get("/tokens", response_model=list[TokenResponse])
def list_tokens(service: TokenService = Depends(get_token_service)) -> list[dict]:
    return service.list_tokens()


@router.get("/tokens/{symbol}")
def get_token(symbol: str, service: TokenService = Depends(get_token_service)) -> dict:
    token = service.get_token_detail(symbol)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token


@router.get("/signals", response_model=list[SignalResponse])
def list_signals(service: SignalService = Depends(get_signal_service)) -> list[dict]:
    return service.list_signals()


@router.get("/signals/{signal_id}", response_model=SignalResponse)
def get_signal(signal_id: str, service: SignalService = Depends(get_signal_service)) -> dict:
    signal = service.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.get("/watchlist", response_model=WatchlistResponse)
def get_watchlist(service: WatchlistService = Depends(get_watchlist_service)) -> WatchlistResponse:
    return WatchlistResponse(items=service.get_watchlist())


@router.post("/watchlist", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_watchlist(
    payload: WatchlistCreateRequest,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    return WatchlistResponse(items=service.add(payload.token_id))


@router.delete("/watchlist/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(token_id: str, service: WatchlistService = Depends(get_watchlist_service)) -> Response:
    service.remove(token_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

