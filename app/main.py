from fastapi import FastAPI
from models import model
from db.database import engine
from routers import users
from fastapi.middleware.cors import CORSMiddleware

model.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "Hello, world!"}
