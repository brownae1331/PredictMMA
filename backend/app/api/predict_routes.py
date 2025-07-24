from fastapi import APIRouter, HTTPException, status
from app.schemas.predict_schemas import PredictionCreate, PredictionOutMakePrediction, PredictionOutPredict
from app.db.database import db_dependency
from app.db.models import models
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_or_update_prediction(prediction: PredictionCreate, db: db_dependency) -> None:
    """Create a new prediction or update an existing one for the given user & fight."""

    db_prediction = (
        db.query(models.Prediction)
        .filter(
            models.Prediction.user_id == prediction.user_id,
            models.Prediction.fight_id == prediction.fight_id,
        )
        .first()
    )

    if db_prediction:
        db_prediction.fighter_id = prediction.fighter_id
        db_prediction.method = prediction.method
        db_prediction.round = prediction.round

    else:
        db_prediction = models.Prediction(
            user_id=prediction.user_id,
            fight_id=prediction.fight_id,
            fighter_id=prediction.fighter_id,
            method=prediction.method,
            round=prediction.round,
        )
        db.add(db_prediction)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not save prediction")

@router.get("/{user_id}/{fight_id}")
async def get_prediction(user_id: int, fight_id: int, db: db_dependency) -> PredictionOutMakePrediction:
    """Return the saved prediction for a given *user_id* and *fight_id*."""

    db_prediction = (
        db.query(models.Prediction)
        .filter(
            models.Prediction.user_id == user_id,
            models.Prediction.fight_id == fight_id,
        )
        .first()
    )

    if not db_prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")


    db_fight = (
        db.query(models.Fight)
        .filter(models.Fight.id == fight_id)
        .first()
    )

    if not db_fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    

    db_fighter_1 = (
        db.query(models.Fighter)
        .filter(models.Fighter.id == db_fight.fighter_1_id)
        .first()
    )

    if not db_fighter_1:
        raise HTTPException(status_code=404, detail="Fighter 1 not found")
    
    db_fighter_2 = (
        db.query(models.Fighter)
        .filter(models.Fighter.id == db_fight.fighter_2_id)
        .first()
    )

    if not db_fighter_2:
        raise HTTPException(status_code=404, detail="Fighter 2 not found")

    return PredictionOutMakePrediction(
        winner_id=db_prediction.fighter_id,
        method=db_prediction.method,    
        round=db_prediction.round,
    )

@router.get("/all")
async def get_all_predictions(user_id: int, db: db_dependency) -> list[PredictionOutPredict]:
    """Return all predictions for a given *user_id*."""
    db_predictions = (
        db.query(models.Prediction)
        .join(models.Fight, models.Prediction.fight_id == models.Fight.id)
        .join(models.Event, models.Fight.event_id == models.Event.id)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Event.date.asc(), models.Fight.match_number.desc())       
        .all()
    )

    if not db_predictions:
        raise HTTPException(status_code=404, detail="No predictions found")
    
    predictions = []

    for prediction in db_predictions:
        db_fight = (
            db.query(models.Fight)
            .filter(models.Fight.id == prediction.fight_id)
            .first()
        )

        if not db_fight:
            raise HTTPException(status_code=404, detail="Fight not found")

        db_event = (
            db.query(models.Event)
            .filter(models.Event.id == db_fight.event_id)
            .first()
        )

        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        db_fighter_1 = (
            db.query(models.Fighter)
            .filter(models.Fighter.id == db_fight.fighter_1_id)
            .first()
        )

        if not db_fighter_1:
            raise HTTPException(status_code=404, detail="Fighter 1 not found")
        
        db_fighter_2 = (    
            db.query(models.Fighter)
            .filter(models.Fighter.id == db_fight.fighter_2_id)
            .first()
        )

        if not db_fighter_2:
            raise HTTPException(status_code=404, detail="Fighter 2 not found")
        
        db_winner = (
            db.query(models.Fighter)
            .filter(models.Fighter.id == prediction.fighter_id)
            .first()
        )
        
        if not db_winner:
            raise HTTPException(status_code=404, detail="Winner not found")
        
        predictions.append(PredictionOutPredict(
            event_title=db_event.title,
            fighter_1_name=db_fighter_1.name,
            fighter_2_name=db_fighter_2.name,
            winner_image=db_winner.image_url,
            method=prediction.method,
            round=prediction.round,
        ))

    return predictions