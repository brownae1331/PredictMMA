const API_BASE_URL = 'http://192.168.1.106:8000';

export class ApiService {
    private static async handleResponse<T>(response: Response): Promise<T> {
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
        }
        return response.json();
    }

    static async getUpcomingEvents(): Promise<Event[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/upcoming-events`);
            return this.handleResponse<Event[]>(response);
        } catch (error) {
            console.error('Error fetching upcoming events:', error);
            throw error;
        }
    }

    static async getAllUpcomingEvents(): Promise<Event[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/all-upcoming-events`);
            return this.handleResponse<Event[]>(response);
        } catch (error) {
            console.error('Error fetching all upcoming events:', error);
            throw error;
        }
    }
} 