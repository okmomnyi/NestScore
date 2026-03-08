import { api } from '@/lib/api';
import PlotDetail from '@/components/plots/PlotDetail';
import { ADS_ENABLED } from '@/lib/constants';

// This page is server-side rendered by default 
export default async function PlotPage({ params }: { params: { id: string } }) {
    let plotData = null;
    let errorMsg = null;

    try {
        // Note: since this is a server component fetching from our backend API,
        // the NEXT_PUBLIC_API_BASE_URL must be an absolute URL accessible from the Next.js server context.
        // If it's a relative path to proxy, it will fail during SSR.
        // In local dev `docker-compose`, the backend is at http://backend:8000
        // So if fetch fails, we use a try-catch and handle graceful degredation

        // For the sake of this implementation, we assume we want to fetch the data
        const res = await api.plots.get(params.id);
        plotData = res;
    } catch (err: any) {
        errorMsg = err.message || "Failed to load plot details.";

        // If we're getting a connection refused during SSR (e.g. Next.js trying to fetch localhost that isn't running yet)
        // we show an error instead of crashing the page.
    }

    if (errorMsg || !plotData) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center h-screen">
                <h1 className="text-2xl font-bold text-[#F87171] mb-2">{errorMsg || "Plot Not Found"}</h1>
                <p className="text-[#94A3B8]">The plot you are looking for does not exist or the server is temporarily unavailable.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col flex-1 w-full mx-auto">
            <PlotDetail plot={plotData.plot} reviews={plotData.reviews} />

            {ADS_ENABLED && (
                <div className="w-full max-w-5xl mx-auto px-4 mt-8 pb-8 text-center">
                    {/* Generic Google AdSense Unit (Non-property-related as per spec) */}
                    <div className="bg-[#1E293B] border border-[#334155] rounded-lg h-24 flex items-center justify-center text-[#64748B] text-xs">
                        Advertisement Space
                    </div>
                </div>
            )}
        </div>
    );
}
