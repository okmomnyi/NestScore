"use client";

import { useState } from 'react';
import { ThumbsDown, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { getFingerprintHash } from '@/lib/fingerprint';

export default function DisagreeButton({ reviewId, initialCount }: { reviewId: string; initialCount: number }) {
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [count, setCount] = useState(initialCount);

    const submitDisagree = async () => {
        if (status === 'success' || status === 'loading') return;

        setStatus('loading');
        try {
            const fbHash = await getFingerprintHash();
            const res = await api.reviews.disagree(reviewId, {
                fingerprint_hash: fbHash
            });
            setCount(res.disagree_count);
            setStatus('success');
        } catch (err: any) {
            setStatus('error');
            // If conflict (409) they already disagreed, just show success state anyway
            if (err.status === 409) {
                setStatus('success');
            } else {
                alert(err.message || 'Failed to submit disagreement');
            }
        }
    };

    return (
        <button
            onClick={submitDisagree}
            disabled={status === 'loading' || status === 'success'}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium transition-colors
                ${status === 'success'
                    ? 'text-[#F59E0B] bg-[#F59E0B]/10 border border-[#F59E0B]/20 cursor-default'
                    : 'text-[#64748B] hover:text-[#F1F5F9] hover:bg-[#334155] border border-transparent'
                }`}
            title="I disagree with this review"
        >
            {status === 'loading' ? (
                <Loader2 size={14} className="animate-spin" />
            ) : (
                <ThumbsDown size={14} className={status === 'success' ? 'fill-current' : ''} />
            )}
            <span>{count > 0 ? count : 'Disagree'}</span>
        </button>
    );
}
