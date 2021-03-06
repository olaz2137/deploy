from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response, Depends, status
from pydantic import BaseModel
import hashlib
from fastapi.encoders import jsonable_encoder
from datetime import datetime, time, timedelta, date
from typing import Dict
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from hashlib import sha256
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import random 
import sqlite3

app = FastAPI()
security = HTTPBasic()
app.secret_key = "eoirijv30bkr0ek0k-0wa0ELV-WV"
app.session_token = []
app.token_value = []
templates = Jinja2Templates(directory="templates")

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def get_current_password(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.password

class HelloResp(BaseModel):
    msg: str
        
class Patient(BaseModel):
    name: str
    surname: str

app.counter: int = 1
app.storage: Dict[int, dict] = {}
    
item = {"message": "Hello world!"}

@app.get("/morenka/{name}")
def morenka(name: str):
    return PlainTextResponse(f"No to chod?? {name}, zapraszam na morenk??")

@app.get("/")
def root():
    return {"message": "Hello world!"}


#@app.get("/counter")
#def counter():
#    app.counter += 1
#    return app.counter


#@app.get("/hello/{name}", response_model=HelloResp)
#def hello_name_view(name: str):
#    return HelloResp(msg=f"Hello {name}")

@app.get("/method")
def get():
    return {"method": "GET"}

@app.post("/method",status_code=201)
def post():
    return {"method": "POST"}

@app.delete("/method")
def delete():
    return {"method": "DELETE"}

@app.put("/method")
def put():
    return {"method": "PUT"}

@app.options("/method")
def options():
    return {"method": "OPTIONS"}

@app.get("/auth")
def auth(password="", password_hash=""):
    m = hashlib.sha512(password.encode("utf8")).hexdigest()

    if password_hash != m or password == "" or password_hash == "":
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/register", status_code=201)
def register_patient(patient: Patient):
    result = {"id": app.counter, "name": patient.name, "surname": patient.surname, "register_date": str(date.today()),
              "vaccination_date": str(date.today() + timedelta(len(''.join(filter(str.isalpha, patient.name))) + len(''.join(filter(str.isalpha, patient.surname)))))}
    app.storage[app.counter] = result
    app.counter += 1
    return result
    
@app.get("/patient/{id}")
def show_patient(id: int):
    if id<0:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)   
    if id in app.storage:
        return app.storage.get(id)
    return Response(status_code=status.HTTP_404_NOT_FOUND)    

@app.get("/hello")
def read_item(request: Request):
    return templates.TemplateResponse(
        "index.html.j2",
        {"request": request, "today_date": str(date.today())},
    )

@app.post("/login_session/", status_code=201)
def login_session(response: Response, username: str = Depends(get_current_username), password: str = Depends(get_current_password)):
    
    session_token = sha256(f"{username}{password}{str(random.randint(0,2021))}".encode()).hexdigest()
    response.set_cookie("session_token",session_token)
    if len(app.session_token) >= 3:
        app.session_token.pop(0)
    app.session_token.append(session_token)


@app.post("/login_token/", status_code=201)
def login_token(response: Response, username: str = Depends(get_current_username), password: str = Depends(get_current_password)):

    token_value = sha256(f"{username}{password}{str(random.randint(0,2021))}".encode()).hexdigest()
    if len(app.token_value) >= 3:
        app.token_value.pop(0)
    app.token_value.append(token_value)
    return {"token": token_value}

@app.get("/welcome_session/")
def welcome_session(*, response: Response, session_token: str = Cookie(None), format: str = Query(None)):
    if session_token not in app.session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if format == "json":
        return {"message": "Welcome!"}
    elif format == "html":
        return HTMLResponse("""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Welcome!</h1>
        </body>
    </html>
    """)
    else:
        return PlainTextResponse("Welcome!")


@app.get("/welcome_token/")
def welcome_token(*,response: Response, token: str = Query(None), format: str = Query(None)):
    if token not in app.token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if format == "json":
        return {"message": "Welcome!"}
    elif format == "html":
        return HTMLResponse("""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Welcome!</h1>
        </body>
    </html>
    """)
    else:
        return PlainTextResponse("Welcome!")
 

@app.delete("/logout_session")
def logout_session(session_token: str = Cookie(None), format: str = ""):
    if (session_token not in app.session_token and session_token not in app.token_value):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if session_token in app.session_token:
        app.session_token.remove(session_token)
    else:
        app.token_value.remove(session_token)
    return RedirectResponse(url=f"/logged_out?format={format}",status_code=302)

@app.delete("/logout_token")
def logout_token(token: str, format: str = ""):
    if (token not in app.token_value and token not in app.session_token) or token == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if token in app.session_token:
        app.session_token.remove(token)
    else:
        app.token_value.remove(token)
    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)

@app.get("/logged_out")
def logged_out(format:str = ""):
    if format == "json":
        return {"message": "Logged out!"}
    elif format == "html":
        return HTMLResponse("""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Logged out!</h1>
        </body>
    </html>
    """)
    else:
        return PlainTextResponse("Logged out!")
    
@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

#4.1
@app.get("/categories")
async def categories():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT CategoryID, CategoryName FROM Categories").fetchall()
    return {"categories" : [{"id": x['CategoryID'], "name": x['CategoryName']} for x in data]}

@app.get("/customers")
async def customers():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT CustomerID, CompanyName, Address || ' ' || PostalCode || ' '|| City ||' '|| Country AS ConcatenatedString FROM Customers ORDER BY CustomerID").fetchall()
    return {"customers" : [{"id": x['CustomerID'], "name": x['CompanyName'], "full_address": x['ConcatenatedString']} for x in data]}

