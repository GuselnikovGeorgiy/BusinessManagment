from fastapi import HTTPException
from pydantic import EmailStr

from app.auth.auth_utils import generate_invite_token, hash_password
from app.schemas.user import CheckAccountResponse, ConfirmRegistrationResponse, ConfirmRegistrationRequest
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode


class InviteService(BaseService):

    @transaction_mode
    async def check_account(self, account_email: EmailStr) -> CheckAccountResponse:
        user_exists = await self.uow.user.get_by_query_one_or_none(email=account_email)
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already in use.")

        default_company = await self.uow.company.get_by_query_one_or_none(
            name="Default Company"
        )
        if not default_company:
            default_company_id = await self.uow.company.add_one_and_get_id(
                name="Default Company"
            )
        else:
            default_company_id = default_company.id

        invite = await self.uow.invite.get_by_query_one_or_none(email=account_email)
        invite_token = invite.token if invite else generate_invite_token()

        if invite and not invite.is_verified:
            await self.uow.invite.update_one_by_id(
                obj_id=invite.id,
                token=invite_token,
            )
        elif not invite:
            await self.uow.invite.add_one(
                email=account_email,
                token=invite_token,
                company_id=default_company_id,
            )

        return CheckAccountResponse(
            message="Verification code generated.",
            email=account_email,
            invite_token=invite_token,
        )

    @transaction_mode
    async def invite_employee(self, email: EmailStr, company_id: int) -> dict:
        invite = await self.uow.invite.get_by_query_one_or_none(email=email)

        if invite:
            if invite.is_verified:
                raise HTTPException(status_code=400, detail="User already verified.")
            invite_token = generate_invite_token()
            await self.uow.invite.update_one_by_id(obj_id=invite.id, token=invite_token)
        else:
            invite_token = generate_invite_token()
            await self.uow.invite.add_one(
                email=email, token=invite_token, company_id=company_id
            )

        return {
            "message": "Invite successfully generated.",
            "email": email,
            "invite_token": invite_token,
        }

    @transaction_mode
    async def confirm_invite(
            self, schema: ConfirmRegistrationRequest
    ) -> ConfirmRegistrationResponse:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.email)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found.")
        if invite.token != schema.token:
            raise HTTPException(status_code=400, detail="Invalid invite token.")
        if invite.is_verified:
            raise HTTPException(status_code=400, detail="Invite already used.")

        user = await self.uow.user.get_by_query_one_or_none(email=schema.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        hashed_password = hash_password(schema.password)
        await self.uow.user.update_one_by_id(
            obj_id=user.id,
            hashed_password=hashed_password,
            is_active=True,
        )
        await self.uow.invite.update_one_by_id(obj_id=invite.id, is_verified=True)

        return ConfirmRegistrationResponse(
            message="Registration completed successfully."
        )
