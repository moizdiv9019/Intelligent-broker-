
from fastapi import FastAPI 
app=FastAPI()

@app.get("/home")
def user():
    return("well come all working")