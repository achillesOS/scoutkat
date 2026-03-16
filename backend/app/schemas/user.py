from datetime import datetime

from app.schemas.common import AppBaseModel


class UserProfileResponse(AppBaseModel):
    email: str
    tracked_symbols: list[str]
    alert_preference: str | None
    onboarding_completed_at: datetime | None


class OnboardingRequest(AppBaseModel):
    email: str
    tracked_symbols: list[str]
    alert_preference: str
