export async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        let errorDetail = '';
        try {
            const data = await response.json();
            if (data && data.detail) {
                if (Array.isArray(data.detail)) {
                    errorDetail = data.detail.map((d: any) => d.msg).join('\n');
                } else {
                    errorDetail = data.detail;
                }
            } else {
                errorDetail = JSON.stringify(data);
            }
        } catch (e) {
            errorDetail = await response.text();
        }
        throw new Error(errorDetail || `API Error: ${response.status} ${response.statusText}`);
    }
    return response.json();
} 