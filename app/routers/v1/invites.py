from fastapi import APIRouter, Depends
from pydantic import EmailStr

from app.auth.auth_utils import get_current_user
from app.schemas.user import (
    CheckAccountResponse,
    UserToken, ConfirmRegistrationRequest,
    ConfirmRegistrationResponse
)
from app.services.invite import InviteService


invite_router = APIRouter(prefix="/v1/invites", tags=["Invites"])


@invite_router.get("/check_account/{account}", response_model=CheckAccountResponse)
async def check_account(
    account: EmailStr, service: InviteService = Depends()
) -> CheckAccountResponse:
    return await service.check_account(account=account)


@invite_router.post("/invite-employee/")
async def invite_employee(
    email: EmailStr,
    current_user: UserToken = Depends(get_current_user),
    service: InviteService = Depends(),
) -> dict:
    company_id = current_user.company_id
    return await service.invite_employee(email=email, company_id=company_id)


@invite_router.post("/confirm-invite/")
async def confirm_invite(
    schema: ConfirmRegistrationRequest, service: InviteService = Depends()
) -> ConfirmRegistrationResponse:
    return await service.confirm_invite(schema=schema)
