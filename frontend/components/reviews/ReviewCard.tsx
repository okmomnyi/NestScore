"use client";

import { Review } from '@/types';
import StarRating from '../ui/StarRating';
import FlagButton from './FlagButton';
import { formatDistanceToNow } from 'date-fns';
import { MessageSquareWarning } from 'lucide-react';
import DisagreeButton from './DisagreeButton';
import ReplyForm from './ReplyForm';
import { useState } from 'react';

export default function ReviewCard({ review, plotId }: { review: Review; plotId: string }) {
    const isDisputed = review.status === 'disputed' || review.dispute_response;

    let dateText = '';
    try {
        const d = new Date(review.publish_at);
        dateText = formatDistanceToNow(d, { addSuffix: true });
    } catch (e) {
        dateText = 'recently';
    }

    // Track local response so it shows instantly without refresh
    const [localResponse, setLocalResponse] = useState<string | null>(review.dispute_response);

    return (
        <div className="bg-[#0F172A] border border-[#334155] rounded-xl p-5 md:p-6 transition-all hover:border-[#475569]">
            <div className="flex justify-between items-start mb-3">
                <StarRating value={review.stars} size={16} readonly />
                <span className="text-xs text-[#64748B] font-medium">{dateText}</span>
            </div>

            <p className="text-[#E2E8F0] text-sm md:text-base leading-relaxed mb-4 whitespace-pre-wrap font-dm">
                {review.comment_text}
            </p>

            <div className="flex justify-between items-center pt-3 border-t border-[#1E293B]">
                <div className="flex items-center gap-2">
                    <div className="h-6 w-6 rounded-full bg-[#1E293B] border border-[#334155] flex items-center justify-center text-[#64748B] text-[10px]">
                        {(review.nickname || review.id).substring(0, 2).toUpperCase()}
                    </div>
                    <span className="text-xs text-[#64748B]">{review.nickname || 'Verified Student'}</span>
                </div>
            </div>

            <div className="flex justify-between items-center mt-4">
                <div className="flex gap-2 w-full">
                    <DisagreeButton reviewId={review.id} initialCount={review.disagree_count || 0} />
                    {!localResponse && (
                        <ReplyForm plotId={plotId} reviewId={review.id} onReplySuccess={setLocalResponse} />
                    )}
                </div>
                <div className="flex items-center gap-2 border-l border-[#334155] pl-2 ml-2">
                    <FlagButton reviewId={review.id} />
                </div>
            </div>

            {localResponse && (
                <div className="mt-5 pt-4 border-t border-[#334155] bg-[#1E293B] -mx-5 md:-mx-6 -mb-5 md:-mb-6 px-5 py-4 md:px-6 md:py-5 border-t-2 border-t-[#D97706] rounded-b-xl">
                    <div className="flex items-center gap-1.5 mb-2 text-[#FBBF24]">
                        <MessageSquareWarning size={14} />
                        <span className="text-xs font-bold uppercase tracking-wider font-space">Landlord Response</span>
                    </div>
                    <p className="text-[#CBD5E1] text-sm leading-relaxed border-l-2 border-[#475569] pl-3 italic whitespace-pre-wrap">
                        "{localResponse}"
                    </p>
                </div>
            )}
        </div>
    );
}
