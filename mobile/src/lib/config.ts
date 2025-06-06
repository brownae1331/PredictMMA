export const API_CONFIG = {
    BASE_URL: 'http://192.168.1.106:8000',
    TIMEOUT: 10000, // 10 seconds timeout
    HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000, // 1 second delay between retries
} as const; 