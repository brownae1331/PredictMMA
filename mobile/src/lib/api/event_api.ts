import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { HomePageMainEvent } from '../../types/sherdog_types';

export async function getHomePageMainEvents(limit: number): Promise<HomePageMainEvent[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/events/main-events`);
    url.searchParams.append('limit', limit.toString());
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<HomePageMainEvent[]>(response);
}