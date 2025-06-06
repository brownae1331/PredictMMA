from fastapi import FastAPI
from app.core.config import add_cors
from app.api.ufc_routes import router

app = FastAPI()

add_cors(app)

app.include_router(router, prefix="/ufc", tags=["UFC"])

@app.get("/")
def read_root():
    return {"message": "API is running"}
