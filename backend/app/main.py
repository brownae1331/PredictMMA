from fastapi import FastAPI
from app.core.config import add_cors
from app.api.ufc_routes import router as ufc_routes
from app.api.auth_routes import router as auth_routes
from app.db.database import engine
from app.db.models import models
from app.api.predict_routes import router as predict_routes

app = FastAPI()

add_cors(app)

models.Base.metadata.create_all(bind=engine)

app.include_router(ufc_routes, prefix="/ufc", tags=["UFC"])
app.include_router(auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(predict_routes, prefix="/predict", tags=["Predict"])

@app.get("/")
def read_root():
    return {"message": "API is running"}