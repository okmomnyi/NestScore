import { PlotMap } from '@/types';
import { Star } from 'lucide-react';
import { renderToString } from 'react-dom/server';

export const getPopupContent = (plot: PlotMap) => {
    const isUnrated = !plot.weighted_score || plot.total_ratings === 0;

    // Render HTML string for Leaflet popup binding
    return `
    <div class="p-1 min-w-[200px] font-dm">
      <h3 class="font-bold text-base text-[#F1F5F9] mb-1 font-space">${plot.name}</h3>
      <p class="text-xs text-[#94A3B8] mb-3 uppercase tracking-wider font-semibold">${plot.area}</p>
      
      <div class="flex items-center justify-between mb-4 bg-[#0F172A] rounded-lg p-2 border border-[#334155]">
        <div class="flex flex-col">
          <span class="text-xl font-bold text-[#F1F5F9] leading-none">${isUnrated ? '—' : plot.weighted_score?.toFixed(1)}</span>
        </div>
        <div class="flex items-center text-xs text-[#E2E8F0]">
          <span class="mr-1">★</span>
          <span>${plot.total_ratings} review${plot.total_ratings !== 1 ? 's' : ''}</span>
        </div>
      </div>
      
      ${isUnrated ?
            `<a href="/plots/${plot.id}#write-review" class="block w-full text-center text-xs font-semibold bg-[#2563EB] hover:bg-[#1D4ED8] text-white py-2 px-3 rounded transition-colors">Be the first to review</a>` :
            `<a href="/plots/${plot.id}" class="block w-full text-center text-xs font-semibold bg-[#334155] hover:bg-[#475569] text-white py-2 px-3 rounded transition-colors border border-[#475569]">View Listing</a>`
        }
    </div>
  `;
};
