from dataclasses import asdict
from datetime import datetime

from sqlalchemy import select

from api_acess_alterdata.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User, time=datetime.now()) as time:
        new_user = User(
            username='test', email='test@example.com', password='secret'
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'test'))

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }
