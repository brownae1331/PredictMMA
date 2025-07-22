export enum Method {
    KO = "KO",
    SUBMISSION = "SUBMISSION",
    DECISION = "DECISION",
}

export interface PredictionCreate {
    user_id: number;
    fight_id: number;
    fighter_id: number;
    method: Method;
    round: number | null;
}

export interface PredictionOutMakePrediction {
    winner_id: number;
    method: Method;
    round: number | null;
}

export interface PredictionOutPredict {
    event_title: string;
    fighter_1_name: string;
    fighter_2_name: string;
    winner_image: string;
    method: Method;
    round: number | null;
}