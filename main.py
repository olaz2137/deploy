from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel
import hashlib
from fastapi.encoders import jsonable_encoder
from datetime import datetime, time, timedelta, date
from typing import Dict


app = FastAPI()

class HelloResp(BaseModel):
    msg: str
        
class Patient(BaseModel):
    name: str
    surname: str

app.counter: int = 1
app.storage: Dict[int, Patient] = {}
    
item = {"message": "Hello world!"}

@app.get("/")
def root():
    return {"message": "Hello world!"}


#@app.get("/counter")
#def counter():
#    app.counter += 1
#    return app.counter


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
def auth(password="", password_hash=""):
    m = hashlib.sha512(password.encode("utf8")).hexdigest()

    if password_hash != m or password == "" or password_hash == "":
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/register", status_code=201)
def register_patient(patient: Patient):
    result = {"id": app.counter, "name": patient.name, "surname": patient.surname, "register_date": str(date.today()),
              "vaccination_date": str(date.today() + timedelta(len(''.join(filter(str.isalpha, patient.name))) + len(''.join(filter(str.isalpha, patient.surname)))))}
    app.storage[app.counter] = patient
    app.counter += 1
    return result
    
    
@app.get("/patient/{id}")
def show_patient(id: int):
    if id in app.storage:
        return app.storage.get(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
