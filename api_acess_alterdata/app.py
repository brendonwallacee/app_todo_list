from http import HTTPStatus

from fastapi import FastAPI

from api_acess_alterdata.schemas import Message

app = FastAPI(title='API de acesso ao Alterdata')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}
