import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
) -> bool:
    """
    Validate API key when API_KEY is configured.

    If API_KEY is empty, authentication is disabled.
    """

    if not settings.API_KEY:
        return True

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required.",
        )

    if not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return True
