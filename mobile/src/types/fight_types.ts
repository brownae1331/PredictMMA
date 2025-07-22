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
    method: string;
    round: number;
    time: string;
}