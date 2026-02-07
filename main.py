from fastapi import FastAPI
from Router.chat import router


app = FastAPI()

app.include_router(router)