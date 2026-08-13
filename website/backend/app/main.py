from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.database import Base, engine
from app.rate_limit import limiter
from app.routers import ai, admin, auth, questions, stats, tests

app = FastAPI(title="RST — RadSafe Trainer API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # Разрешает мобильное веб-приложение (Expo web) с любого адреса в локальной сети,
    # чтобы CORS не ломался каждый раз, когда Mac получает новый IP по DHCP.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+",
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
