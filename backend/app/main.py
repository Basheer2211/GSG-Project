
from fastapi import FastAPI

app = FastAPI(
    title="Simera API",
    description="Resume Parsing & Data Enrichment",
    version="1.0.0"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
