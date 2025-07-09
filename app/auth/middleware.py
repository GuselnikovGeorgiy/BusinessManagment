import re

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.repositories.user import UserRepository

from app.uow.unit_of_work import UnitOfWork
from app.auth.auth_utils import decode_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/sign-in")


PUBLIC_PATH_REGEX = [
    r"^/v1/invites/check_account/[^/]+$",
    r"^/v1/auth/sign-in$",
    r"^/v1/auth/sign-up$",
    r"^/v1/auth/sign-up-complete$",
    r"^/v1/invites/invite-employee/$",
    r"^/v1/user/\d+/update-email$",
    r"^/v1/invites/confirm-invite",
    r"^/docs$",
    r"^/redoc$",
    r"^/openapi.json$",
]


async def auth_middleware(request: Request, call_next):
    path = request.url.path.rstrip("/")
    if any(re.match(pattern, path) for pattern in PUBLIC_PATH_REGEX):
        return await call_next(request)
    try:
        token = await oauth2_scheme(request)
        payload = decode_jwt(token)
        user_id = int(payload["sub"])
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    async with UnitOfWork() as uow:
        user_repo: UserRepository = UserRepository(uow.session)

        try:
            user = await user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(status_code=403, detail="Inactive account")

            request.state.user = {
                "id": user.id,
                "company_id": user.company_id,
                "is_admin": user.is_admin,
            }

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    return await call_next(request)
