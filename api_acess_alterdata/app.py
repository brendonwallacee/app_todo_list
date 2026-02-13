from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api_acess_alterdata.database import get_session
from api_acess_alterdata.models import User
from api_acess_alterdata.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from api_acess_alterdata.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI(title='API de acesso ao Alterdata')


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def read_root():
    return {'message': 'Olá mundo!'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_root_html():
    return """
    <html>
      <body>
        <h1>Olá mundo!</h1>
      </body>
    </html>
    """


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username já existe',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email já existe',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def update_user(
    user_id: int,
    user: UserSchema,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Permissão insuficiente',
        )
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username ou email ja cadastrado',
        )


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_user(
    user_id: int,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Não autorizado a deletar este usuário',
        )
    session.delete(current_user)
    session.commit()
    return Message(message='Usuário deletado com sucesso')


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    return db_user


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
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
