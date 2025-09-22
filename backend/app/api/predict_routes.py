from fastapi import APIRouter, HTTPException, status
from app.schemas.predict_schemas import PredictionCreate, PredictionOutMakePrediction, PredictionOutPredict, PredictionResult
from app.db.database import db_dependency
from app.db.models import models
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from zoneinfo import ZoneInfo

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

    db_fight_event = (
        db.query(models.Fight, models.Event)
        .join(models.Event, models.Fight.event_id == models.Event.id)
        .filter(models.Fight.id == prediction.fight_id)
        .first()
    )

    db_fight, db_event = db_fight_event

    if not db_fight:
        raise HTTPException(status_code=404, detail="Fight not found")

    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    if db_event.date < datetime.now(ZoneInfo("Europe/London")):
        raise HTTPException(status_code=400, detail="Cannot predict for past events")

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

        db_fight_result = (
            db.query(models.Fight)
            .filter(models.Fight.id == prediction.fight_id)
            .first()
        )

        if not db_fight_result:
            raise HTTPException(status_code=404, detail="Fight result not found")

        if not db_fight_result.winner:
            result = None
        elif db_fight_result.winner.lower() in ["draw", "no contest"]:
            result = PredictionResult(fighter=False, method=False, round=False)
        else:
            winner_id = db_fight_result.fighter_1_id
            predicted_fighter_id = db_winner.id

            if winner_id != predicted_fighter_id:
                result = PredictionResult(fighter=False, method=False, round=False)
            else:
                fighter_correct = True

                method_correct = False
                if db_fight_result.method and prediction.method:

                    normalized_actual = None
                    if "decision" in db_fight_result.method.lower():
                        normalized_actual = "DECISION"
                    elif "submission" in db_fight_result.method.lower() or db_fight_result.method.lower().startswith("sub"):
                        normalized_actual = "SUBMISSION"
                    elif any(term in db_fight_result.method.lower() for term in ["ko", "tko", "knockout", "technical knockout"]):
                        normalized_actual = "KO"

                    method_correct = normalized_actual == prediction.method

                round_correct = False
                if normalized_actual == "DECISION":
                    round_correct = True
                elif db_fight_result.round and prediction.round:
                    round_correct = db_fight_result.round == prediction.round

                result = PredictionResult(
                    fighter=fighter_correct,
                    method=method_correct,
                    round=round_correct
                )
        
        
        predictions.append(PredictionOutPredict(
            event_title=db_event.title,
            event_date=db_event.date,
            fighter_1_name=db_fighter_1.name,
            fighter_2_name=db_fighter_2.name,
            winner_name=db_winner.name,
            method=prediction.method,
            round=prediction.round,
            result=result,
        ))

    return predictions