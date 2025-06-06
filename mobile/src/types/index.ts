export interface Fight {
    fighter_1_link: string;
    fighter_2_link: string;
    fighter_1_name: string;
    fighter_2_name: string;
    fighter_1_image: string;
    fighter_2_image: string;
    card_position: string;
    fight_weight: string;
    num_rounds: string;
}

export interface Event {
    event_title: string;
    event_date: string;
    event_venue: string;
    event_location: string;
    event_location_flag?: string | null;
    event_fight_data: Fight[];
} 