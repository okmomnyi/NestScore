import { Review } from '@/types';
import ReviewCard from './ReviewCard';

export default function ReviewList({ reviews, plotId }: { reviews: Review[]; plotId: string }) {
    if (!reviews || reviews.length === 0) {
        return (
            <div className="text-center py-12 px-4 bg-[#1E293B] border border-[#334155] rounded-xl flex flex-col items-center">
                <div className="w-16 h-16 bg-[#0F172A] border border-[#334155] rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl opacity-50">✍️</span>
                </div>
                <h3 className="text-lg font-bold text-[#F1F5F9] mb-2 font-space">No Student Reviews Yet</h3>
                <p className="text-sm text-[#94A3B8] max-w-sm">
                    No one has reviewed this plot yet. Be the first to share your experience and help the MUST community.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {reviews.map((review) => (
                <ReviewCard key={review.id} review={review} plotId={plotId} />
            ))}
        </div>
    );
}
