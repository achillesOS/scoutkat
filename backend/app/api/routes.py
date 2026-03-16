from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status

from app.core.config import get_settings
from app.core.container import get_signal_service, get_token_service, get_user_service, get_watchlist_service
from app.schemas.health import HealthResponse
from app.schemas.signal import SignalResponse
from app.schemas.token_context import TokenContextResponse
from app.schemas.token import TokenResponse
from app.schemas.user import OnboardingRequest, UserProfileResponse
from app.schemas.watchtower import WatchtowerResponse
from app.schemas.watchlist import WatchlistCreateRequest, WatchlistResponse
from app.services.signal_service import SignalService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from app.services.watchlist_service import WatchlistService


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", environment=settings.app_env)


def require_user_email(x_user_email: str | None = Header(default=None)) -> str:
    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing authenticated user email")
    return x_user_email


@router.get("/tokens", response_model=list[TokenResponse])
def list_tokens(service: TokenService = Depends(get_token_service)) -> list[dict]:
    return service.list_tokens()


@router.get("/watchtower", response_model=WatchtowerResponse)
def get_watchtower(
    symbols: str | None = Query(default=None),
    x_user_email: str | None = Header(default=None),
    service: TokenService = Depends(get_token_service),
) -> dict:
    normalized = [symbol.strip().upper() for symbol in symbols.split(",")] if symbols else None
    return service.get_watchtower(normalized, user_email=x_user_email)


@router.get("/tokens/{symbol}/context", response_model=TokenContextResponse)
def get_token_context(symbol: str, service: TokenService = Depends(get_token_service)) -> dict:
    token = service.get_token_context(symbol)
    if not token:
        raise HTTPException(status_code=404, detail="Token context not found")
    return token


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
def get_watchlist(
    user_email: str = Depends(require_user_email),
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    return WatchlistResponse(items=service.get_watchlist(user_email))


@router.post("/watchlist", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_watchlist(
    payload: WatchlistCreateRequest,
    user_email: str = Depends(require_user_email),
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    return WatchlistResponse(items=service.add(payload.token_id, user_email))


@router.delete("/watchlist/{token_id}", response_model=WatchlistResponse)
def delete_watchlist(
    token_id: str,
    user_email: str = Depends(require_user_email),
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    items = service.remove(token_id, user_email)
    return WatchlistResponse(items=items)


@router.get("/me", response_model=UserProfileResponse)
def get_me(
    user_email: str = Depends(require_user_email),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    profile = service.get_profile(user_email)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfileResponse.model_validate(profile)


@router.post("/me/onboarding", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def save_onboarding(
    payload: OnboardingRequest,
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    profile = service.save_onboarding(payload.email, payload.tracked_symbols, payload.alert_preference)
    if profile is None:
        raise HTTPException(status_code=500, detail="Unable to save onboarding")
    return UserProfileResponse.model_validate(profile)
