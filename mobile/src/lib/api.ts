import { API_CONFIG } from './config';
import { handleResponse } from './apiUtils';

export async function getUpcomingEvents(): Promise<Event[]> {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/ufc/upcoming-events`);
        return handleResponse<Event[]>(response);
    } catch (error) {
        console.error('Error fetching upcoming events:', error);
        throw error;
    }
}

export async function getAllUpcomingEvents(): Promise<Event[]> {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/ufc/all-upcoming-events`);
        return handleResponse<Event[]>(response);
    } catch (error) {
        console.error('Error fetching all upcoming events:', error);
        throw error;
    }
}