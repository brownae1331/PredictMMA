from fastapi import APIRouter, HTTPException, status
from app.schemas.predict_schemas import Prediction as PredictionSchema
from app.db.database import db_dependency
from app.db.models import models
from sqlalchemy.exc import IntegrityError
from typing import List

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_or_update_prediction(prediction: PredictionSchema, db: db_dependency):
    """Create a new prediction or update an existing one for the given user & fight."""

    db_prediction = db.query(models.Prediction).filter(
        models.Prediction.user_id == prediction.user_id,
        models.Prediction.event_url == prediction.event_url,
        models.Prediction.fight_id == prediction.fight_id,
    ).first()

    if db_prediction:
        db_prediction.fighter_prediction = prediction.fighter_prediction
        db_prediction.method_prediction = prediction.method_prediction
        db_prediction.round_prediction = prediction.round_prediction
    else:
        db_prediction = models.Prediction(
            user_id=prediction.user_id,
            event_url=prediction.event_url,
            fight_id=prediction.fight_id,
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

@router.get("", response_model=PredictionSchema)
async def get_prediction(user_id: int, event_url: str, fight_id: str, db: db_dependency):
    """Return the saved prediction for a given *user_id*, *event_url* and *fight_id*."""

    db_prediction = (
        db.query(models.Prediction)
        .filter(
            models.Prediction.user_id == user_id,
            models.Prediction.event_url == event_url,
            models.Prediction.fight_id == fight_id,
        )
        .first()
    )

    if not db_prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return PredictionSchema(
        user_id=db_prediction.user_id,
        event_url=db_prediction.event_url,
        fight_id=db_prediction.fight_id,
        fight_idx=db_prediction.fight_idx,
        fighter_prediction=db_prediction.fighter_prediction,
        method_prediction=db_prediction.method_prediction,
        round_prediction=db_prediction.round_prediction,
    )

@router.get("/all")
async def get_all_predictions(user_id: int, db: db_dependency):
    """Return all predictions for a given *user_id*."""
    db_predictions = (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Prediction.event_url)
        .all()
    )

    if not db_predictions:
        raise HTTPException(status_code=404, detail="No predictions found")

    return [
        PredictionSchema(
            user_id=p.user_id,
            event_url=p.event_url,
            fight_id=p.fight_id,
            fight_idx=p.fight_idx,
            fighter_prediction=p.fighter_prediction,
            method_prediction=p.method_prediction,
            round_prediction=p.round_prediction,
        )
        for p in db_predictions
    ]