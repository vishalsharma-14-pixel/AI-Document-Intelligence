from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, documents

app = FastAPI(title="AI Document Intelligence")

app.add_middleware(
    CORSMiddleware,
    # regex (not a fixed port) so the Vite dev server still works if 5173 is taken and it picks another port
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
