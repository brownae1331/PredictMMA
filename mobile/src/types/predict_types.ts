export interface Prediction {
    user_id: number;
    event_url: string;
    fight_idx: number;
    fighter_prediction: string;
    method_prediction: string;
    round_prediction: number | null;
}