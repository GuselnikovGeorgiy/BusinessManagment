from datetime import datetime, timezone

from fastapi import HTTPException

from app.auth.auth_utils import hash_password, encode_jwt, validate_password
from app.schemas.auth import (
    SignUpRequestSchema,
    SignUpResponseSchema,
    CompleteSignUpRequest,
    CompleteSignUpResponse,
    SignInRequestSchema,
    TokenInfo,
)
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode


class AuthService(BaseService):

    @transaction_mode
    async def sign_up(self, schema: SignUpRequestSchema) -> SignUpResponseSchema:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.email)
        if not invite or invite.token != schema.token:
            raise HTTPException(
                status_code=400,
                detail="Invalid or missing verification code.",
            )

        await self.uow.invite.update_one_by_id(obj_id=invite.id, is_verified=True)
        return SignUpResponseSchema(
            message="Account successfully verified.",
            email=schema.email,
        )

    @transaction_mode
    async def sign_up_complete(
            self, schema: CompleteSignUpRequest
    ) -> CompleteSignUpResponse:
        invite = await self.uow.invite.get_by_query_one_or_none(email=schema.email)
        if not invite or not invite.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Account not verified.",
            )

        company_exists = await self.uow.company.get_by_query_one_or_none(
            name=schema.company_name
        )
        if company_exists:
            raise HTTPException(
                status_code=400,
                detail="Company name already in use.",
            )

        hashed_password = hash_password(schema.password)
        company_id = await self.uow.company.add_one_and_get_id(name=schema.company_name)
        user_data = {
            "email": schema.email,
            "first_name": schema.first_name,
            "last_name": schema.last_name,
            "hashed_password": hashed_password,
            "is_admin": True,
            "company_id": company_id,
            "position_id": None,
        }
        await self.uow.user.add_one(**user_data)

        return CompleteSignUpResponse(
            email=schema.email,
            password=hashed_password,
            first_name=schema.first_name,
            last_name=schema.last_name,
            company_name=schema.company_name,
        )

    @transaction_mode
    async def sign_in(self, schema: SignInRequestSchema) -> TokenInfo:
        user = await self._validate_auth_user(
            schema.email,
            schema.password,
        )

        current_time = datetime.now(timezone.utc)
        jwt_payload = {
            "sub": user.id,
            "company_id": user.company_id,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "iat": int(current_time.timestamp()),
        }
        token = encode_jwt(jwt_payload)

        return TokenInfo(access_token=token, token_type="Bearer")

    async def _validate_auth_user(self, email: str, password: str):
        user = await self.uow.user.get_by_query_one_or_none(email=email)

        if not user:
            raise HTTPException(
                status_code=400,
                detail="User with this email does not exist.",
            )
        if not validate_password(
                password=password,
                hashed_password=user.hashed_password,
        ):
            raise HTTPException(
                status_code=400,
                detail="Incorrect password.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="User account is inactive.",
            )

        return user
