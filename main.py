import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from api.auth.routers import router as api_auth_router
from pages.auth.routers import router as pages_auth_router
from api.chat.routers import router as api_chat_router

app = FastAPI()

origins = [
    "*"
]  # Сервера, которые могут отправлять запросы на Backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin",
                   "Access-Control-Allow-Methods", "X-Requested-With",
                   "Authorization", "X-CSRF-Token"]
)  # Побеждаем политику CORS

app.include_router(api_auth_router)
app.include_router(pages_auth_router)
app.include_router(api_chat_router)

app.mount("/media", StaticFiles(directory="media"), name="media")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, log_level="info")
