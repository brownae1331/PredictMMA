from fastapi import APIRouter, HTTPException, status
from app.schemas.predict_schemas import Prediction as PredictionSchema
from app.db.database import db_dependency
from app.db.models import models
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/prediction", status_code=status.HTTP_201_CREATED)
async def create_or_update_prediction(prediction: PredictionSchema, db: db_dependency):
    """Create a new prediction or update an existing one for the given user & fight."""
    # Check if prediction already exists
    db_prediction = db.query(models.Prediction).filter(
        models.Prediction.user_id == prediction.user_id,
        models.Prediction.event_url == prediction.event_url,
        models.Prediction.fight_idx == prediction.fight_idx,
    ).first()

    if db_prediction:
        # Update existing prediction
        db_prediction.fighter_prediction = prediction.fighter_prediction
        db_prediction.method_prediction = prediction.method_prediction
        db_prediction.round_prediction = prediction.round_prediction
    else:
        # Create new prediction
        db_prediction = models.Prediction(
            user_id=prediction.user_id,
            event_url=prediction.event_url,
            fight_idx=prediction.fight_idx,
            fighter_prediction=prediction.fighter_prediction,
            method_prediction=prediction.method_prediction,
            round_prediction=prediction.round_prediction,
        )
        db.add(db_prediction)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not save prediction")

    return {"message": "Prediction saved successfully"} 