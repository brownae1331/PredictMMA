import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { Fight } from '../../types/fight_types';

export async function getFightsByEvent(event_id: number): Promise<Fight[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/fights/event/${event_id}`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Fight[]>(response);
}

export async function getFightById(fight_id: number): Promise<Fight> {
    const url = new URL(`${API_CONFIG.BASE_URL}/fights/fight/${fight_id}`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Fight>(response);
}