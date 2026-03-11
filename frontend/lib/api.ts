import { API_BASE_URL } from './constants';
import { PaginatedPlots, PaginatedReviews, Plot, PlotMap } from '@/types';
import { getCsrfToken } from './csrf';

class ApiError extends Error {
    status: number;
    constructor(message: string, status: number) {
        super(message);
        this.status = status;
    }
}

async function fetchApi<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;

    const method = (options.method || 'GET').toUpperCase();

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> | undefined),
    };

    // Attach CSRF token for all mutating API requests
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
        const csrfToken = await getCsrfToken();
        headers['X-CSRF-Token'] = csrfToken;
    }

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
        let errorMsg = 'An error occurred';
        try {
            const data = await response.json();
            errorMsg = data.detail || errorMsg;
        } catch (e) { }
        throw new ApiError(errorMsg, response.status);
    }

    return response.json();
}

export const api = {
    plots: {
        list: (params: { page?: number; area?: string; min_stars?: number } = {}) => {
            const searchParams = new URLSearchParams();
            if (params.page) searchParams.append('page', params.page.toString());
            if (params.area && params.area !== 'All') searchParams.append('area', params.area);
            if (params.min_stars !== undefined) searchParams.append('min_stars', params.min_stars.toString());

            const query = searchParams.toString();
            return fetchApi<PaginatedPlots>(`/api/plots${query ? `?${query}` : ''}`);
        },

        map: () => fetchApi<PlotMap[]>('/api/plots/map'),

        get: (id: string, page: number = 1) =>
            fetchApi<{ plot: Plot; reviews: PaginatedReviews }>(`/api/plots/${id}?page=${page}`),
    },

    reviews: {
        submit: (data: { plot_id: string; stars: number; comment_text: string; fingerprint_hash: string; turnstile_token: string }) =>
            fetchApi<{ id: string; publish_at: string }>('/api/reviews', {
                method: 'POST',
                body: JSON.stringify(data),
            }),

        flag: (reviewId: string, data: { reason: string; fingerprint_hash: string }) =>
            fetchApi(`/api/reviews/${reviewId}/flag`, {
                method: 'POST',
                body: JSON.stringify(data),
            }),

        disagree: (reviewId: string, data: { fingerprint_hash: string }) =>
            fetchApi<{ detail: string, disagree_count: number }>(`/api/reviews/${reviewId}/disagree`, {
                method: 'POST',
                body: JSON.stringify({ reason: 'disagree_vote', fingerprint_hash: data.fingerprint_hash }),
            }),
    },

    suggestions: {
        submit: (data: { suggested_name: string; area: string; notes?: string; fingerprint_hash: string }) =>
            fetchApi('/api/suggestions', {
                method: 'POST',
                body: JSON.stringify(data),
            }),
    },

    disputes: {
        submit: (data: { plot_id: string; review_id: string; landlord_response_text: string }) =>
            fetchApi('/api/disputes', {
                method: 'POST',
                body: JSON.stringify(data),
            }),
    },

    contact: {
        submit: (data: { subject: string; message: string; turnstile_token: string }) =>
            fetchApi('/api/contact', {
                method: 'POST',
                body: JSON.stringify(data),
            }),
    }
};
