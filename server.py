import base64
import hmac
import hashlib
from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = "57319b1d3cd68fadbe552c149dd4e9c3b7e86c8f731c30c3c4bb55b931950d8c"


users = {
    "alex@user.com": {
        "name": "Alex",
        "password": "123456",
        "balance": 100000
    },
    "peet@user.com": {
        "name": "Peet",
        "password": "234567",
        "balance": 20000
    }
}


def create_data_sign(data: str) -> str:
    sign = hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()
    return sign


def sign_cookie(data: str) -> str:
    encoded_data = base64.b64encode(data.encode()).decode()
    signed_cookie = f'{encoded_data}.{create_data_sign(data)}'
    return signed_cookie


def get_data_from_signed_cookie(signed_cookie: str) -> Optional[str]:
    data_base64, sign = signed_cookie.split('.')
    data = base64.b64decode(data_base64.encode()).decode()
    valid_sign = create_data_sign(data)
    if hmac.compare_digest(valid_sign, sign):
        return data


@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()

    response = Response(login_page, media_type='text/html')

    if not username:
        return response

    valid_username = get_data_from_signed_cookie(username)

    if not valid_username:
        response.delete_cookie("username")
        return response

    try:
        user = users[valid_username]

    except KeyError:
        response.delete_cookie(key="username")
        return response

    response = Response(f'Hello, {user["name"]}!', media_type='text/html')
    return response


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user["password"] != password:
        return Response("Fuck off", media_type='text/html')

    response = Response(
        f"Hello, {user['name']}!<br/>Your balance: {user['balance']}",
        media_type='text/html'
    )

    response.set_cookie(key="username", value=sign_cookie(username))
    return response
