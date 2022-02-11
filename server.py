from fastapi import FastAPI, Form
from fastapi.responses import Response


app = FastAPI()

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


@app.get('/')
def index_page():
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    return Response(login_page, media_type='text/html')


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user["password"] != password:
        return Response("Fuck off", media_type='text/html')

    return Response(
        f"Hello, {user['name']}!<br/>Your balance: {user['balance']}",
        media_type='text/html'
    )
