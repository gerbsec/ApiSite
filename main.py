from os import access
from types import MethodType
from fastapi_login import LoginManager
from fastapi import FastAPI, Request, Depends 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
app = FastAPI()
templates = Jinja2Templates(directory="html/")
SECRET = "abir is cool"
DB = {
    'users': {
        'admin': {
            'name': 'admin',
            'password': 'admin'
        }
    }
}

class NotAuthenticatedException(Exception):
    pass

def exc_handler(request, exc):
    return RedirectResponse(url='/login')

manager = LoginManager(SECRET, '/api/login', custom_exception=NotAuthenticatedException, use_cookie=True)

manager.not_authenticated_exception = NotAuthenticatedException

app.add_exception_handler(NotAuthenticatedException, exc_handler)

@manager.user_loader
def query_user(user_id: str):
    return DB['users'].get(user_id)


@app.post('/api/login')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = query_user(email)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data={'sub': email}
    )
    response = RedirectResponse(url='/', status_code=302)
    manager.set_cookie(response, access_token.decode())
    return response

@app.get("/login")
async def read_form(request: Request):
    return templates.TemplateResponse('login.html', context={'request': request})


@app.get('/')
async def index(request: Request, user = Depends(manager)):
    return templates.TemplateResponse('crud.html', context={'request': request})

