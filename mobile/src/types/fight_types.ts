import { Method } from "./predict_types";

export enum ResultType {
    WIN = "WIN",
    DRAW = "DRAW",
    NO_CONTEST = "NO_CONTEST",
}

export interface Fight {
    id: number;
    fighter_1_id: number;
    fighter_2_id: number;
    fighter_1_name: string;
    fighter_2_name: string;
    fighter_1_image: string;
    fighter_2_image: string;
    fighter_1_ranking: string;
    fighter_2_ranking: string;
    fighter_1_flag: string;
    fighter_2_flag: string;
    weight_class: string;
    winner: string;
    method: Method;
    round: number;
    time: string;
}

export interface FightResult {
    result_type: ResultType;
    winner_id: number | null;
    method: Method;
    round: number;
    time: string;
}