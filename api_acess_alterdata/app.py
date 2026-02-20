from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from api_acess_alterdata.routers import auth, todos, users
from api_acess_alterdata.schemas import Message

app = FastAPI(
    title='To-Do List - API',
    version='DEV',
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def read_root():
    return {'message': 'Olá mundo!'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
async def read_root_html():
    return """
    <html>
      <body>
        <h1>Olá mundo!</h1>
      </body>
    </html>
    """
