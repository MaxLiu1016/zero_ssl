from fastapi import FastAPI
from module.ssl.router import ssl_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(ssl_router)