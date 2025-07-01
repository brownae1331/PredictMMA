import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { Prediction } from '../../types/predict_types';

export async function createPrediction(prediction: Prediction, token?: string): Promise<void> {
    const url = new URL(`${API_CONFIG.BASE_URL}/predict`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url.toString(), {
        method: 'POST',
        headers,
        body: JSON.stringify(prediction),
    });

    await handleResponse<void>(response);
}

export async function getPrediction(
    user_id: number,
    event_url: string,
    fight_idx: number,
    token?: string,
): Promise<Prediction | null> {
    const url = new URL(`${API_CONFIG.BASE_URL}/predict`);
    url.searchParams.append('user_id', user_id.toString());
    url.searchParams.append('event_url', event_url);
    url.searchParams.append('fight_idx', fight_idx.toString());

    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    if (response.status === 404) {
        return null;
    }

    return handleResponse<Prediction>(response);
}
