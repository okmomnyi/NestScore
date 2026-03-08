"use client";

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

import { api } from '@/lib/api';
import PlotCard from '@/components/plots/PlotCard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { PLOT_AREAS } from '@/lib/constants';
import type { Plot, PlotMap, PaginatedPlots } from '@/types';

const NestMap = dynamic(
  () => import('@/components/map/NestMap'),
  {
    ssr: false,
    loading: () => (
      <div className="h-full w-full bg-[#1E293B] flex items-center justify-center">
        <LoadingSpinner />
      </div>
    ),
  }
);

interface HomeClientProps {
  initialPlots: PaginatedPlots;
  initialMapPlots: PlotMap[];
}

export default function HomeClient({ initialPlots, initialMapPlots }: HomeClientProps) {
  const [plots, setPlots] = useState<Plot[]>(initialPlots.plots);
  const [mapPlots, setMapPlots] = useState<PlotMap[]>(initialMapPlots);
  const [page, setPage] = useState(initialPlots.page);
  const [areaFilter, setAreaFilter] = useState<string>('All');
  const [starsFilter, setStarsFilter] = useState<string>('-1');
  const [searchQuery, setSearchQuery] = useState('');

  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(initialPlots.total_count);
  const [selectedPlotId, setSelectedPlotId] = useState<string | null>(null);

  // Fetch paginated list data when filters or page change
  useEffect(() => {
    const fetchPlots = async () => {
      // We already have initial SSR data for page 1 with default filters
      if (page === initialPlots.page && areaFilter === 'All' && starsFilter === '-1' && !searchQuery) {
        setPlots(initialPlots.plots);
        setTotalCount(initialPlots.total_count);
        return;
      }

      setLoading(true);
      try {
        const res = await api.plots.list({
          page,
          area: areaFilter,
          min_stars: starsFilter !== '-1' ? parseInt(starsFilter, 10) : undefined,
        });

        let filteredPlots = res.plots;
        if (searchQuery) {
          const lowerQuery = searchQuery.toLowerCase();
          filteredPlots = filteredPlots.filter((p) =>
            p.name.toLowerCase().includes(lowerQuery)
          );
        }

        setPlots(filteredPlots);
        setTotalCount(res.total_count);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPlots();
  }, [page, areaFilter, starsFilter, searchQuery, initialPlots]);

  // Keep map data in sync with filters/search (base data comes from SSR)
  const mapDataFiltered = mapPlots.filter((p) => {
    if (areaFilter !== 'All' && p.area !== areaFilter) return false;
    if (starsFilter !== '-1' && (!p.weighted_score || p.weighted_score < parseInt(starsFilter, 10))) {
      return false;
    }
    if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handlePlotSelect = (id: string) => {
    setSelectedPlotId(id);
    const el = document.getElementById(`plot-${id}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const handleMapPinSelect = (id: string) => {
    handlePlotSelect(id);
  };

  return (
    <div className="flex flex-col flex-1 w-full bg-[#0F172A]">
      {/* Map Section - Top 60% approx */}
      <section className="h-[50vh] lg:h-[60vh] w-full relative z-0 border-b border-[#1E293B]">
        <NestMap
          plots={mapDataFiltered}
          selectedPlotId={selectedPlotId}
          onPlotSelect={handleMapPinSelect}
        />

        {/* Floating Search overlay */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 w-11/12 max-w-2xl bg-[#1E293B]/95 backdrop-blur-sm border border-[#334155] rounded-xl shadow-xl shadow-black/50 p-2 flex flex-col md:flex-row gap-2">
          <input
            type="text"
            placeholder="Search hostels..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            className="flex-1 bg-[#0F172A] border border-[#334155] rounded-lg px-4 py-2 text-[#F1F5F9] focus:outline-none focus:ring-1 focus:ring-[#38BDF8] font-dm text-sm"
          />
          <div className="flex gap-2">
            <select
              value={areaFilter}
              onChange={(e) => {
                setAreaFilter(e.target.value);
                setPage(1);
              }}
              className="bg-[#0F172A] border border-[#334155] rounded-lg px-3 py-2 text-[#E2E8F0] focus:outline-none focus:ring-1 focus:ring-[#38BDF8] font-dm text-sm min-w-[120px]"
            >
              <option value="All">All Areas</option>
              {PLOT_AREAS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
            <select
              value={starsFilter}
              onChange={(e) => {
                setStarsFilter(e.target.value);
                setPage(1);
              }}
              className="bg-[#0F172A] border border-[#334155] rounded-lg px-3 py-2 text-[#E2E8F0] focus:outline-none focus:ring-1 focus:ring-[#38BDF8] font-dm text-sm"
            >
              <option value="-1">Any Rating</option>
              <option value="4">4+ Stars</option>
              <option value="3">3+ Stars</option>
            </select>
          </div>
        </div>
      </section>

      {/* List Section */}
      <section className="flex-1 container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold font-space text-[#F1F5F9] tracking-tight">
            Viewing Plots
          </h2>
          <span className="text-sm text-[#94A3B8] font-medium">{totalCount} found</span>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner className="w-8 h-8" />
          </div>
        ) : plots.length === 0 ? (
          <div className="text-center py-12 border border-[#334155] border-dashed rounded-xl bg-[#1E293B]/30">
            <p className="text-[#94A3B8] mb-2 font-medium">No plots match your filters.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setAreaFilter('All');
                setStarsFilter('-1');
                setPage(1);
              }}
              className="text-[#38BDF8] hover:underline text-sm font-semibold"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {plots.map((plot) => (
              <div
                key={plot.id}
                id={`plot-${plot.id}`}
                onMouseEnter={() => setSelectedPlotId(plot.id)}
                onMouseLeave={() => setSelectedPlotId(null)}
              >
                <PlotCard plot={plot} isHighlighted={selectedPlotId === plot.id} />
              </div>
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {totalCount > initialPlots.per_page && (
          <div className="flex justify-center gap-4 mt-8">
            <button
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
              className="px-4 py-2 border border-[#334155] rounded-lg bg-[#1E293B] text-[#F1F5F9] disabled:opacity-50 hover:bg-[#334155] font-dm font-medium text-sm transition-colors"
            >
              Previous
            </button>
            <button
              disabled={plots.length < initialPlots.per_page}
              onClick={() => setPage((p) => p + 1)}
              className="px-4 py-2 border border-[#334155] rounded-lg bg-[#1E293B] text-[#F1F5F9] disabled:opacity-50 hover:bg-[#334155] font-dm font-medium text-sm transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

