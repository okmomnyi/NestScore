import { Review } from '@/types';
import { Star } from 'lucide-react';

interface RatingBreakdownProps {
    weightedScore: number | null;
    totalRatings: number;
    reviews: Review[];
}

export default function RatingBreakdown({ weightedScore, totalRatings, reviews }: RatingBreakdownProps) {
    // If there are no reviews or no score yet, show empty state
    if (!weightedScore || totalRatings === 0) {
        return (
            <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-6 h-full flex flex-col justify-center items-center text-center">
                <Star size={48} strokeWidth={1} className="text-[#475569] mb-4" />
                <h3 className="text-xl font-bold font-space text-[#F1F5F9] mb-2">No Ratings Yet</h3>
                <p className="text-sm text-[#94A3B8] max-w-xs">Be the first to share your experience living here to help other students.</p>
            </div>
        );
    }

    // Calculate histogram from the currently loaded page of reviews
    // Note: in a true production app, histogram counts should come from backend
    const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
    let maxCount = 0;

    reviews.forEach(r => {
        if (r.stars >= 1 && r.stars <= 5) {
            counts[r.stars as keyof typeof counts]++;
            if (counts[r.stars as keyof typeof counts] > maxCount) {
                maxCount = counts[r.stars as keyof typeof counts];
            }
        }
    });

    // Ensure we don't divide by zero
    const divisor = Math.max(maxCount, 1);

    return (
        <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-6 h-full flex flex-col justify-center">
            <div className="flex items-center gap-6 mb-6">
                <div className="flex flex-col items-center">
                    <span className="text-5xl font-bold font-space text-[#F1F5F9] tracking-tight">{weightedScore.toFixed(1)}</span>
                    <div className="flex mt-2 gap-1 px-1.5 py-1 bg-[#0F172A] rounded-lg">
                        {[1, 2, 3, 4, 5].map((s) => (
                            <Star
                                key={s}
                                size={14}
                                className={s <= Math.round(weightedScore) ? "text-[#FBBF24] fill-[#FBBF24]" : "text-[#475569]"}
                            />
                        ))}
                    </div>
                    <span className="text-xs text-[#64748B] mt-2 font-medium">{totalRatings} review{totalRatings !== 1 && 's'}</span>
                </div>

                <div className="flex-1 space-y-2.5 border-l border-[#334155] pl-6">
                    {[5, 4, 3, 2, 1].map((star) => {
                        const count = counts[star as keyof typeof counts];
                        const pct = (count / divisor) * 100;
                        return (
                            <div key={star} className="flex items-center gap-3">
                                <div className="flex items-center gap-1 w-8">
                                    <span className="text-sm font-medium text-[#CBD5E1]">{star}</span>
                                    <Star size={12} strokeWidth={2.5} className="text-[#64748B]" />
                                </div>
                                <div className="flex-1 h-2.5 bg-[#0F172A] rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-[#38BDF8] rounded-full"
                                        style={{ width: `${pct}%` }}
                                    />
                                </div>
                                <div className="w-8 text-right text-xs text-[#94A3B8] font-medium">{count}</div>
                            </div>
                        );
                    })}
                </div>
            </div>
            <p className="text-xs text-[#64748B] text-center pt-4 border-t border-[#334155]">
                Scores are calculated using a Bayesian weighted model to prevent manipulation.
            </p>
        </div>
    );
}
