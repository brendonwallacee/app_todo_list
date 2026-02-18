from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_acess_alterdata.database import get_session
from api_acess_alterdata.models import User
from api_acess_alterdata.schemas import Token
from api_acess_alterdata.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])
Session = Annotated[AsyncSession, Depends(get_session)]
OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuthForm,
    session: Session,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Usuário ou senha incorretos',
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Usuário ou senha incorretos',
        )
    access_token = create_access_token({'sub': user.email})
    return Token(access_token=access_token, token_type='Bearer')
