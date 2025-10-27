from fastapi import FastAPI
from app.routers import routers
app=FastAPI()
app.include_router(routers.router)
