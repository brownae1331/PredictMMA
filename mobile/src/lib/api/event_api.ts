import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { HomePageMainEvent, Event } from '../../types/event_types';

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

export async function getUpcomingEvents(): Promise<Event[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/events/upcoming`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Event[]>(response);
}