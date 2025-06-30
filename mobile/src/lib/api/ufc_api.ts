import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { Event, EventSummary, Fight, MainEvent } from '../../types/ufc_types';

export async function getUpcomingEventLinks(): Promise<string[]> {
    try {
        const url = new URL(`${API_CONFIG.BASE_URL}/ufc/events/links/upcoming`);
        const response = await fetch(url);
        return handleResponse<string[]>(response);
    } catch (error) {
        console.error('Error fetching upcoming events links:', error);
        throw error;
    }
}

export async function getEvents(limit?: number): Promise<Event[]> {
    try {
        const event_links = await getUpcomingEventLinks();
        const limited_links = limit ? event_links.slice(0, limit) : event_links;
        const events: Event[] = [];

        for (const link of limited_links) {
            const url = new URL(`${API_CONFIG.BASE_URL}/ufc/event?event_url=${link}`);
            const response = await fetch(url);
            const event = await handleResponse<Event>(response);
            events.push(event);
        }

        return events;
    } catch (error) {
        console.error('Error fetching events:', error);
        throw error;
    }
}

export async function getEventSummaries(limit?: number): Promise<EventSummary[]> {
    try {
        const event_links = await getUpcomingEventLinks();
        const limited_links = limit ? event_links.slice(0, limit) : event_links;
        const event_summaries: EventSummary[] = [];

        for (const link of limited_links) {
            const url = new URL(`${API_CONFIG.BASE_URL}/ufc/event/summary?event_url=${link}`);
            const response = await fetch(url);
            const event_summary = await handleResponse<EventSummary>(response);
            event_summaries.push(event_summary);
        }

        return event_summaries;
    } catch (error) {
        console.error('Error fetching event summaries:', error);
        throw error;
    }
}

export async function getEventFights(event_url: string): Promise<Fight[]> {
    try {
        const url = new URL(`${API_CONFIG.BASE_URL}/ufc/event/fights?event_url=${event_url}`);
        const response = await fetch(url);
        return handleResponse<Fight[]>(response);
    } catch (error) {
        console.error('Error fetching event fights:', error);
        throw error;
    }
}

export async function getEventMainEvent(event_url: string): Promise<MainEvent> {
    try {
        const url = new URL(`${API_CONFIG.BASE_URL}/ufc/event/main-event?event_url=${event_url}`);
        const response = await fetch(url);
        return handleResponse<MainEvent>(response);
    } catch (error) {
        console.error('Error fetching event main event:', error);
        throw error;
    }
}