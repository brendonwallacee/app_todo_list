from http import HTTPStatus

from fastapi.testclient import TestClient

from api_acess_alterdata.app import app


def test_root_deve_retornar_ola_mundo():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


def test_deve_retornar_ola_mundo_em_html():
    client = TestClient(app)

    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == """
    <html>
      <body>
        <h1>Olá mundo!</h1>
      </body>
    </html>"""
    )
