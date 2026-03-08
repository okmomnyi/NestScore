import { PlotMap } from '@/types';

export const getPinColor = (weighted_score: number | null, status: string, total_ratings: number) => {
    if (status === 'under_review') return '#D97706';
    if (weighted_score === null || total_ratings === 0) return '#6B7280';
    if (weighted_score >= 4.0) return '#16A34A';
    if (weighted_score >= 3.0) return '#D97706';
    return '#DC2626';
};

export const createCustomIcon = (L: any, color: string, isPulsing: boolean) => {
    return L.divIcon({
        className: 'custom-pin',
        html: `
      <div class="relative w-4 h-4">
        ${isPulsing ? `<div class="absolute inset-0 rounded-full pulse-animation" style="background-color: ${color}"></div>` : ''}
        <div class="absolute inset-0 rounded-full border-2 border-white shadow-md z-10" style="background-color: ${color}"></div>
      </div>
    `,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
        popupAnchor: [0, -10],
    });
};
