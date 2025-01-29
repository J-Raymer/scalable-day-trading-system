import jwt
from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Annotated, Union

class Item(BaseModel):
    name: str
    pwd : str
    
class Token(BaseModel):
    token : str
    


app = FastAPI()

secret = "secret123456"
adminToken = jwt.encode({"name":"admin","admin" : True}, secret, algorithm="HS256")



@app.get("/")
async def root():
    return {"message" : "hello world"}

@app.post("/login")
async def login(item : Item):
    if item.name == 'admin' and item.pwd == 'password':
        return adminToken
    return 'Wrong credentials'

@app.get("/protected")
async def proctect(token : Annotated[str | None, Header()] = None):
    decoded = jwt.decode(token, secret, algorithms="HS256")
    if decoded["name"]== 'admin' and decoded["admin"] == True:
        return 'Grant Access'
    return "Access Denied"
