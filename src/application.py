import uvicorn

from fastapi import FastAPI

from .configs.config import SERVICE_CONFIG

app = FastAPI()


@app.get("/")
def ping() -> str:
    return f"Welcome! The server is running at {SERVICE_CONFIG.web.host}:{SERVICE_CONFIG.web.port}."


if __name__ == "__main__":
    uvicorn.run(app, host=SERVICE_CONFIG.web.host, port=SERVICE_CONFIG.web.port)
