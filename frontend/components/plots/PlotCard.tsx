import { Plot } from '@/types';
import Link from 'next/link';
import Badge from '../ui/Badge';
import { Star } from 'lucide-react';
import { cn } from '../ui/Badge';

export default function PlotCard({ plot, isHighlighted }: { plot: Plot; isHighlighted?: boolean }) {
    const isUnrated = !plot.weighted_score || plot.total_ratings === 0;

    const getScoreColor = (score: number | null) => {
        if (!score) return 'bg-[#334155] text-[#94A3B8]';
        if (score >= 4.0) return 'bg-[#14532D] text-[#4ADE80] border-[#22C55E]/30';
        if (score >= 3.0) return 'bg-[#422006] text-[#FBBF24] border-[#F59E0B]/30';
        return 'bg-[#450A0A] text-[#F87171] border-[#EF4444]/30';
    };

    return (
        <Link href={`/plots/${plot.id}`} className="block">
            <div
                className={cn(
                    "bg-[#1E293B] border border-[#334155] hover:border-[#475569] rounded-xl p-5 transition-all duration-200 group flex flex-col h-full",
                    isHighlighted && "ring-2 ring-[#38BDF8] border-[#38BDF8]"
                )}
            >
                <div className="flex justify-between items-start mb-3">
                    <div>
                        <h3 className="font-bold text-lg text-[#F1F5F9] group-hover:text-[#38BDF8] transition-colors leading-tight mb-1">
                            {plot.name}
                        </h3>
                        <div className="flex items-center gap-2">
                            <Badge variant="transparent">{plot.area}</Badge>
                            {plot.status === 'under_review' && <Badge variant="warning">Under Review</Badge>}
                        </div>
                    </div>

                    <div className={cn(
                        "flex flex-col items-center justify-center rounded-lg p-2 min-w-[3.5rem] border",
                        getScoreColor(plot.weighted_score)
                    )}>
                        <span className="font-bold text-lg leading-none mb-0.5">
                            {isUnrated ? '—' : plot.weighted_score?.toFixed(1)}
                        </span>
                        <span className="text-[0.65rem] uppercase tracking-wider font-semibold opacity-80">
                            {isUnrated ? 'Unrated' : 'Score'}
                        </span>
                    </div>
                </div>

                <p className="text-sm text-[#94A3B8] line-clamp-2 mb-4 flex-grow">
                    {plot.description}
                </p>

                <div className="flex items-center justify-between border-t border-[#334155] pt-3 mt-auto">
                    <div className="flex items-center text-sm text-[#cbd5e1]">
                        <Star size={14} className={isUnrated ? "text-[#64748B]" : "text-[#FBBF24] fill-[#FBBF24]"} />
                        <span className="ml-1.5 font-medium">{plot.total_ratings}</span>
                        <span className="ml-1 text-[#64748B]"> review{plot.total_ratings !== 1 ? 's' : ''}</span>
                    </div>
                    <span className="text-sm font-medium text-[#2563EB] group-hover:text-[#38BDF8] transition-colors flex items-center">
                        View Listing <span className="ml-1 transition-transform group-hover:translate-x-1">→</span>
                    </span>
                </div>
            </div>
        </Link>
    );
}
