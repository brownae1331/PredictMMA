import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { Prediction } from '../../types/predict_types';

export async function createPrediction(prediction: Prediction, token?: string): Promise<void> {
    const url = new URL(`${API_CONFIG.BASE_URL}/predict/prediction`);
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
