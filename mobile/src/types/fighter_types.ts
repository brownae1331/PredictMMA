export interface Fighter {
    id: number;
    name: string;
    nickname?: string;
    image_url?: string;
    record?: string;
    ranking?: string;
    country?: string;
    city?: string;
    dob?: string;
    height?: string;
    weight_class?: string;
    association?: string;
}

export interface FighterSearchResponse {
    fighters: Fighter[];
    total: number;
}
