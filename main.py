from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel
import hashlib

app = FastAPI()
app.counter = 0


class HelloResp(BaseModel):
    msg: str

item = {"message": "Hello world!"}

@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/counter")
def counter():
    app.counter += 1
    return app.counter


@app.get("/hello/{name}", response_model=HelloResp)
def hello_name_view(name: str):
    return HelloResp(msg=f"Hello {name}")

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
def auth(password: str, password_hash: str):
    return item
    

    
