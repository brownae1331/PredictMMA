import { API_CONFIG } from '../config';
import { handleResponse } from '../utils/apiUtils';

export async function registerUser(username: string, password: string): Promise<void> {
    const url = new URL(`${API_CONFIG.BASE_URL}/auth/register`);
    const response = await fetch(url.toString(), {
        method: 'POST',
        headers: API_CONFIG.HEADERS,
        body: JSON.stringify({ username, password }),
    });
    await handleResponse<void>(response);
}

export async function loginUser(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const url = new URL(`${API_CONFIG.BASE_URL}/auth/login`);
    const response = await fetch(url.toString(), {
        method: 'POST',
        headers: API_CONFIG.HEADERS,
        body: JSON.stringify({ username, password }),
    });
    return handleResponse<{ access_token: string; token_type: string }>(response);
}