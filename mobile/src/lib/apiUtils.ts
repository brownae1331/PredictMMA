import { API_CONFIG } from './config';

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export async function fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...API_CONFIG.HEADERS,
                ...options.headers,
            },
            signal: controller.signal,
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

export async function fetchWithRetry(url: string, options: RequestInit = {}): Promise<Response> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= API_CONFIG.MAX_RETRIES; attempt++) {
        try {
            return await fetchWithTimeout(url, options);
        } catch (error) {
            lastError = error as Error;
            if (attempt < API_CONFIG.MAX_RETRIES) {
                await sleep(API_CONFIG.RETRY_DELAY);
            }
        }
    }

    throw lastError || new Error('Failed to fetch after all retries');
}

export async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
    }
    return response.json();
} 