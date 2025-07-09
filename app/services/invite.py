import secrets
import uuid
from datetime import datetime, timedelta, timezone

import anyio
import bcrypt
from fastapi import Depends, HTTPException
from pydantic import EmailStr

from app.auth.auth_utils import generate_invite_token, hash_password
from app.config import settings
from app.schemas.user import (
    CheckAccountResponse,
    ConfirmRegistrationResponse,
    ConfirmRegistrationRequest,
)
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode


DEFAULT_COMPANY_NAME = settings.DEFAULT_COMPANY_NAME

INVITE_COOLDOWN_SECONDS = 60


class InviteService(BaseService):

    @transaction_mode
    async def check_account(self, account_email: EmailStr) -> CheckAccountResponse:
        existing_user = await self.uow.user.get_by_query_one_or_none(email=account_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use.")

        company = await self.uow.company.get_by_query_one_or_none(name=DEFAULT_COMPANY_NAME)
        if not company:
            company_id = await self.uow.company.add_one_and_get_id(name=DEFAULT_COMPANY_NAME)
        else:
            company_id = company.id

        invite = await self.uow.invite.get_by_query_one_or_none(email=account_email)

        invite_token = generate_invite_token()

        if invite and not invite.is_verified:
            await self.uow.invite.update_one_by_id(
                obj_id=invite.id,
                token=invite_token,
                updated_at=datetime.now(timezone.utc),
            )

        elif not invite:
            await self.uow.invite.add_one(
                email=account_email,
                token=invite_token,
                company_id=company_id,
            )


        return CheckAccountResponse(
            message="Verification code generated.",
            email=account_email,
            invite_token=invite_token,
        )

    @transaction_mode
    async def invite_employee(self, email: EmailStr, company_id: int) -> dict:
        invite = await self.uow.invite.get_by_query_one_or_none(email=email)

        if invite and (datetime.now(timezone.utc) - invite.updated_at) < timedelta(
            seconds=INVITE_COOLDOWN_SECONDS
        ):
            raise HTTPException(
                status_code=429,
                detail="Invite already requested; please wait before requesting again.",
            )

        invite_token = generate_invite_token()

        if invite:
            if invite.is_verified:
                raise HTTPException(status_code=400, detail="User already verified.")
            await self.uow.invite.update_one_by_id(
                obj_id=invite.id, token=invite_token, updated_at=datetime.utcnow()
            )
        else:
            await self.uow.invite.add_one(
                email=email,
                token=invite_token,
                company_id=company_id,
            )

        return {
            "message": "Invite successfully generated and sent.",
            "email": email,
        }

    @transaction_mode
    async def confirm_invite(
        self, schema: ConfirmRegistrationRequest
    ) -> ConfirmRegistrationResponse:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.email)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found.")
        if invite.is_verified:
            raise HTTPException(status_code=400, detail="Invite already used.")

        # тайминг‑безопасное сравнение токенов
        if not secrets.compare_digest(invite.token, schema.token):
            raise HTTPException(status_code=400, detail="Invalid invite token.")

        user = await self.uow.user.get_by_query_one_or_none(email=schema.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        hashed_password = await anyio.to_thread.run_sync(
            hash_password, schema.password
        )

        await self.uow.user.update_one_by_id(
            obj_id=user.id,
            hashed_password=hashed_password,
            is_active=True,
        )
        await self.uow.invite.update_one_by_id(obj_id=invite.id, is_verified=True)

        return ConfirmRegistrationResponse(
            message="Registration completed successfully."
        )
