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

export async function getUpcomingEvents(offset = 0, limit = 10): Promise<Event[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/events/upcoming`);
    url.searchParams.append('offset', offset.toString());
    url.searchParams.append('limit', limit.toString());

    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Event[]>(response);
}

export async function getPastEvents(offset = 0, limit = 10): Promise<Event[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/events/past`);
    url.searchParams.append('offset', offset.toString());
    url.searchParams.append('limit', limit.toString());

    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    return handleResponse<Event[]>(response);
}   