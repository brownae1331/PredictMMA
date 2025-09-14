import { API_CONFIG } from '../config';
import { handleResponse } from '../utils/apiUtils';
import { Fighter, FighterSearchResponse } from '../../types/fighter_types';
import { FighterFightHistory } from '../../types/fight_types';

export async function getAllFighters(): Promise<Fighter[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/fighters`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Fighter[]>(response);
}

export async function getFighterById(fighter_id: number): Promise<Fighter> {
    const url = new URL(`${API_CONFIG.BASE_URL}/fighters/${fighter_id}`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Fighter>(response);
}

export async function searchFighters(query: string): Promise<FighterSearchResponse> {
    const url = new URL(`${API_CONFIG.BASE_URL}/fighters/search`);
    url.searchParams.append('q', query);
    
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<FighterSearchResponse>(response);
}

export async function getFighterFightHistory(fighter_id: number): Promise<FighterFightHistory[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/fighters/${fighter_id}/fights`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<FighterFightHistory[]>(response);
}
