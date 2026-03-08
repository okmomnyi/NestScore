"use client";

import { useState } from 'react';
import { Star } from 'lucide-react';
import { cn } from '../ui/Badge';

interface StarRatingProps {
    value: number;
    onChange?: (val: number) => void;
    size?: number;
    readonly?: boolean;
}

export default function StarRating({ value, onChange, size = 20, readonly = false }: StarRatingProps) {
    const [hoverState, setHoverState] = useState(0);

    return (
        <div className="flex items-center gap-1" role="radiogroup" aria-label="Star Rating">
            {[1, 2, 3, 4, 5].map((star) => {
                const active = hoverState || value;
                const fill = star <= active;
                return (
                    <button
                        key={star}
                        type="button"
                        disabled={readonly}
                        onClick={() => onChange?.(star)}
                        onMouseEnter={() => !readonly && setHoverState(star)}
                        onMouseLeave={() => !readonly && setHoverState(0)}
                        className={cn(
                            "transition-all duration-150 outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8] rounded-sm",
                            readonly ? "cursor-default" : "cursor-pointer hover:scale-110"
                        )}
                        aria-label={`${star} star${star !== 1 ? 's' : ''}`}
                        aria-checked={star === value}
                        role="radio"
                    >
                        <Star
                            size={size}
                            strokeWidth={fill ? 0 : 1.5}
                            className={cn(
                                "transition-colors",
                                fill ? "fill-[#FBBF24] text-[#FBBF24]" : "text-[#64748B]",
                                !readonly && hoverState >= star && hoverState !== value && "opacity-70"
                            )}
                        />
                    </button>
                );
            })}
        </div>
    );
}
