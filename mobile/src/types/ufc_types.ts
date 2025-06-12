export interface MainEvent {
    event_url: string;
    fighter_1_link: string;
    fighter_2_link: string;
    fighter_1_name: string;
    fighter_2_name: string;
    fighter_1_image: string;
    fighter_2_image: string;
    fighter_1_rank: string;
    fighter_2_rank: string;
}

export interface EventSummary {
    event_url: string;
    event_title: string;
    event_date: string;
}

export interface Fight {
    event_url: string;
    fighter_1_link: string;
    fighter_2_link: string;
    fighter_1_name: string;
    fighter_2_name: string;
    fighter_1_image: string;
    fighter_2_image: string;
    fighter_1_rank: string;
    fighter_2_rank: string;
    fighter_1_flag: string;
    fighter_2_flag: string;
    fight_weight: string;
}

export interface Event {
    event_url: string;
    event_title: string;
    event_date: string;
    event_venue: string;
    event_location: string;
    event_location_flag: string;
}