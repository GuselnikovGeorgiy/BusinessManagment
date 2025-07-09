from fastapi import APIRouter, Depends

from app.schemas.auth import (
    SignUpRequestSchema,
    SignUpResponseSchema,
    CompleteSignUpResponse,
    CompleteSignUpRequest,
    TokenInfo,
    SignInRequestSchema,
)
from app.services.auth import AuthService


auth_router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@auth_router.post("/sign-up/", response_model=SignUpResponseSchema)
async def sign_up(
    schema: SignUpRequestSchema, service: AuthService = Depends()
) -> SignUpResponseSchema:
    return await service.sign_up(schema=schema)


@auth_router.post("/sign-up-complete/", response_model=CompleteSignUpResponse)
async def sign_up_complete(
    schema: CompleteSignUpRequest, service: AuthService = Depends()
) -> CompleteSignUpResponse:
    return await service.sign_up_complete(schema=schema)


@auth_router.post("/sign-in", response_model=TokenInfo)
async def sign_in(
    schema: SignInRequestSchema, service: AuthService = Depends()
) -> TokenInfo:
    return await service.sign_in(schema=schema)
