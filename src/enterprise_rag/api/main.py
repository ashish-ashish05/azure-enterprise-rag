from fastapi import FastAPI

from enterprise_rag.api.routes import router


app = FastAPI(
    title="Enterprise RAG API",
    version="1.0.0",
    description="Enterprise document question-answering API.",
)

app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
    }