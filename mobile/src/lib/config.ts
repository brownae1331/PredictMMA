const getBaseUrl = () => {
    const RAILWAY_URL = 'https://predictmma-production.up.railway.app';
        
    //return 'http://localhost:8000';
    return RAILWAY_URL;
};

export const API_CONFIG = {
    BASE_URL: getBaseUrl(),
    TIMEOUT: 10000,
    HEADERS: {
        'Content-Type': 'application/json',
    },
} as const;