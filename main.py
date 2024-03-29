from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import organizationsRoute, user,repository,commits
from elasticsearch import Elasticsearch
import asyncio


app = FastAPI(title="github-elk", version="1.0.0", contact={
    "name": "github-elk"
})


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/api")
app.include_router(repository.router, prefix="/api")
app.include_router(organizationsRoute.router, prefix="/api")
app.include_router(commits.router, prefix="/api")

