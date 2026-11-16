from fastapi import FastAPI

app = FastAPI(title="Demo Internal App")


@app.get("/health")
def health():
    return {"status": "ok"}