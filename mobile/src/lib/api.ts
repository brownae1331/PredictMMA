import { API_CONFIG } from './config';
import { handleResponse } from './apiUtils';

export async function getUpcomingEvents(limit?: number): Promise<Event[]> {
    try {
        const url = new URL(`${API_CONFIG.BASE_URL}/ufc/events/upcoming`);
        if (limit) url.searchParams.append('limit', limit.toString());

        const response = await fetch(url.toString());
        return handleResponse<Event[]>(response);
    } catch (error) {
        console.error('Error fetching upcoming events:', error);
        throw error;
    }
}