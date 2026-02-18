from dataclasses import asdict
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_acess_alterdata.database import get_session
from api_acess_alterdata.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User, time=datetime.now()) as time:
        new_user = User(
            username='test', email='test@example.com', password='secret'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'test')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_get_session_returns_async_session():
    gen = get_session()

    session = await anext(gen)

    assert isinstance(session, AsyncSession)

    await gen.aclose()
