from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
app.counter = 0


class HelloResp(BaseModel):
    msg: str


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

#@app.get("/method")
#def method():
    
