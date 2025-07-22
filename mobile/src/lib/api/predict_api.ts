import { API_CONFIG } from '../config';
import { handleResponse } from '../apiUtils';
import { PredictionCreate, PredictionOutMakePrediction, PredictionOutPredict } from '../../types/predict_types';

export async function createPrediction(prediction: PredictionCreate): Promise<void> {
    const url = new URL(`${API_CONFIG.BASE_URL}/predict`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'POST',
        headers,
        body: JSON.stringify(prediction),
    });

    await handleResponse<void>(response);
}

export async function getPrediction(user_id: number, fight_id: number): Promise<PredictionOutMakePrediction | null> {
    const url = new URL(`${API_CONFIG.BASE_URL}/predict/${user_id}/${fight_id}`);
    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    if (response.status === 404) {
        return null;
    }

    return handleResponse<PredictionOutMakePrediction>(response);
}

export async function getAllPredictions(user_id: number): Promise<PredictionOutPredict[]> {
    const url = new URL(`${API_CONFIG.BASE_URL}/predict/all`);
    url.searchParams.set('user_id', user_id.toString());

    const headers: Record<string, string> = { ...API_CONFIG.HEADERS };

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
    });

    if (response.status === 404) {
        return [];
    }

    return handleResponse<PredictionOutPredict[]>(response);
}   