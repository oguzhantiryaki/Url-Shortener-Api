from fastapi import FastAPI,Request
from routes.index import url,auth
from config.db import create_tables

app = FastAPI()

create_tables()
app.include_router(auth)
app.include_router(url)

