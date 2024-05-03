from fastapi import FastAPI
from models.model import Base
from db.database import engine
from routers import (
    user_routes,
    exam_routes,
    admin_routes,
    examiner_routes,
    request_exam_routes,
)
from auth import auth
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(auth.router)
app.include_router(exam_routes.router)
app.include_router(admin_routes.router)
app.include_router(examiner_routes.router)
app.include_router(request_exam_routes.router)


@app.get("/")
def root():
    return {"message": "Hello, world!"}
