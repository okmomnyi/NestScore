'use client';

import { event } from '@/lib/analytics';

export const trackReviewSubmit = (plotId: string) => {
  event({
    action: 'submit_review',
    category: 'engagement',
    label: plotId,
  });
};

export const trackPlotView = (plotId: string, plotName: string) => {
  event({
    action: 'view_plot',
    category: 'engagement',
    label: `${plotName} (${plotId})`,
  });
};

export const trackSearch = (searchTerm: string) => {
  event({
    action: 'search',
    category: 'engagement',
    label: searchTerm,
  });
};

export const trackDisputeSubmit = (reviewId: string) => {
  event({
    action: 'submit_dispute',
    category: 'engagement',
    label: reviewId,
  });
};

export const trackSuggestionSubmit = (plotName: string) => {
  event({
    action: 'submit_suggestion',
    category: 'engagement',
    label: plotName,
  });
};

export const trackContactSubmit = () => {
  event({
    action: 'submit_contact',
    category: 'engagement',
  });
};

export const trackMapInteraction = (action: 'zoom' | 'pan' | 'marker_click') => {
  event({
    action: `map_${action}`,
    category: 'map_interaction',
  });
};

export const trackFilterChange = (filterType: string, filterValue: string) => {
  event({
    action: 'filter_change',
    category: 'engagement',
    label: `${filterType}: ${filterValue}`,
  });
};
