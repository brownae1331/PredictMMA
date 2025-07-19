export interface HomePageMainEvent {
    event_id: number;
    event_title: string;
    event_date: Date;
    fighter_1_id: number;
    fighter_2_id: number;
    fighter_1_name: string;
    fighter_2_name: string;
    fighter_1_nickname: string | null;
    fighter_2_nickname: string | null;
    fighter_1_image: string | null;
    fighter_2_image: string | null;
    fighter_1_ranking: string | null;
    fighter_2_ranking: string | null;
}