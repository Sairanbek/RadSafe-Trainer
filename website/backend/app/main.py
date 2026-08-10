from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import ai, admin, auth, questions, stats, tests

app = FastAPI(title="RST — RadSafe Trainer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(tests.router)
app.include_router(stats.router)
app.include_router(admin.router)
app.include_router(ai.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
