import dynamic from 'next/dynamic';
import { Plot } from '@/types';
import Badge from '../ui/Badge';
import RatingBreakdown from './RatingBreakdown';
import ReviewForm from '../reviews/ReviewForm';
import ReviewList from '../reviews/ReviewList';

// Dynamically import Leaflet map with no SSR
const NestMap = dynamic(
    () => import('../map/NestMap'),
    { ssr: false, loading: () => <div className="h-full w-full flex items-center justify-center bg-[#0F172A]"><Badge variant="neutral">Loading Map...</Badge></div> }
);

export default function PlotDetail({ plot, reviews }: { plot: Plot; reviews: any }) {
    const isUnrated = !plot.weighted_score || plot.total_ratings === 0;

    // Format plot for Map component expectations
    const plotMapData = {
        id: plot.id,
        name: plot.name,
        area: plot.area,
        gps_lat: plot.gps_lat,
        gps_lng: plot.gps_lng,
        weighted_score: plot.weighted_score,
        total_ratings: plot.total_ratings,
        status: plot.status
    };

    return (
        <div className="max-w-5xl mx-auto w-full px-4 py-8 space-y-12">
            {/* Header Section */}
            <section className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <h1 className="text-3xl md:text-4xl font-bold font-space text-[#F1F5F9]">{plot.name}</h1>
                        {plot.status === 'under_review' && <Badge variant="warning" className="text-xs shrink-0">Under Review</Badge>}
                        {plot.landlord_claimed && <Badge variant="success" className="text-xs shrink-0">Landlord Active</Badge>}
                    </div>
                    <div className="flex items-center gap-2 text-[#94A3B8]">
                        <Badge variant="transparent">{plot.area}</Badge>
                        <span>•</span>
                        <span className="text-sm">{plot.description}</span>
                    </div>
                </div>

                <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-4 flex items-center gap-4 min-w-[140px] shadow-lg shrink-0">
                    <div className="flex flex-col">
                        <span className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-1">NestScore</span>
                        <span className="text-3xl font-bold font-space text-[#F1F5F9] leading-none">
                            {isUnrated ? '—' : plot.weighted_score?.toFixed(1)}
                        </span>
                    </div>
                </div>
            </section>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Left Column: Reviews & Forms */}
                <div className="lg:col-span-2 space-y-12">
                    <section id="reviews">
                        <div className="flex justify-between items-end mb-6">
                            <h2 className="text-2xl font-bold font-space text-[#F1F5F9]">Student Reviews</h2>
                            <span className="text-sm font-medium text-[#94A3B8]">{plot.total_ratings} Total Ratings</span>
                        </div>
                        <ReviewList reviews={reviews.reviews} plotId={plot.id} />
                    </section>

                    <section id="write-review" className="scroll-mt-24">
                        <ReviewForm plotId={plot.id} />
                    </section>
                </div>

                {/* Right Column: Mini Map & Breakdown */}
                <div className="space-y-8">
                    <section>
                        <h3 className="text-lg font-bold font-space text-[#F1F5F9] mb-4">Rating Breakdown</h3>
                        <RatingBreakdown
                            weightedScore={plot.weighted_score}
                            totalRatings={plot.total_ratings}
                            reviews={reviews.reviews}
                        />
                    </section>

                    <section className="bg-[#1E293B] border border-[#334155] rounded-xl overflow-hidden shadow-lg h-[300px]">
                        <NestMap plots={[plotMapData]} isInteractive={false} />
                    </section>
                </div>
            </div>
        </div>
    );
}
