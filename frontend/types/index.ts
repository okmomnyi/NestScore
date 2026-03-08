export interface Plot {
    id: string;
    name: string;
    area: string;
    description: string;
    gps_lat: number;
    gps_lng: number;
    weighted_score: number | null;
    raw_avg: number | null;
    total_ratings: number;
    status: 'active' | 'under_review' | 'removed';
    landlord_claimed: boolean;
}

export interface PlotMap {
    id: string;
    name: string;
    area: string;
    gps_lat: number;
    gps_lng: number;
    weighted_score: number | null;
    total_ratings: number;
    status: 'active' | 'under_review' | 'removed';
}

export interface Review {
    id: string;
    stars: number;
    comment_text: string;
    status: 'active' | 'cleared' | 'disputed';
    flag_count: number;
    disagree_count: number;
    publish_at: string;
    created_at: string;
    dispute_response: string | null;
    nickname: string | null;
}

export interface PaginatedPlots {
    plots: Plot[];
    total_count: number;
    page: number;
    per_page: number;
}

export interface PaginatedReviews {
    reviews: Review[];
    total_count: number;
    page: number;
    per_page: number;
}
