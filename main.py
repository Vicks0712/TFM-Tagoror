# main.py
from api.app_factory import create_app
import uvicorn

app = create_app()

@app.get("/rag", tags=["Index"])
async def root():
    return {"message": "Welcome to Hermes RAG!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
