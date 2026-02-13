from http import HTTPStatus


def test_root_return_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


def test_return_ola_mundo_html(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == """
    <html>
      <body>
        <h1>Olá mundo!</h1>
      </body>
    </html>
    """
    )
