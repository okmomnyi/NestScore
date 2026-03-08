"use client";

import { useState } from 'react';
import { Flag, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { getFingerprintHash } from '@/lib/fingerprint';

export default function FlagButton({ reviewId }: { reviewId: string }) {
    const [isOpen, setIsOpen] = useState(false);
    const [reason, setReason] = useState('offensive');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [errorMsg, setErrorMsg] = useState('');

    const submitFlag = async () => {
        setStatus('loading');
        setErrorMsg('');
        try {
            const fbHash = await getFingerprintHash();
            await api.reviews.flag(reviewId, {
                fingerprint_hash: fbHash,
                reason
            });
            setStatus('success');
            setIsOpen(false);
        } catch (err: any) {
            setStatus('error');
            setErrorMsg(err.message || 'Failed to submit flag');
        }
    };

    if (status === 'success') {
        return <span className="text-xs text-[#16A34A] flex items-center gap-1"><Flag size={12} className="fill-current" /> Flagged for review</span>;
    }

    return (
        <div className="relative">
            <button
                title="Report this review"
                onClick={() => setIsOpen(!isOpen)}
                className="text-[#64748B] hover:text-[#EF4444] transition-colors p-1 rounded-md hover:bg-[#450A0A]/30 flex items-center gap-1.5"
            >
                <Flag size={14} />
            </button>

            {isOpen && (
                <div className="absolute right-0 bottom-full mb-2 w-64 bg-[#1E293B] border border-[#334155] rounded-lg shadow-xl p-4 z-10">
                    <h4 className="text-sm font-semibold text-[#F1F5F9] mb-2 font-space">Report Review</h4>
                    <p className="text-xs text-[#94A3B8] mb-3">Please select a reason for reporting this review to the moderators.</p>

                    <select
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        className="w-full bg-[#0F172A] border border-[#334155] text-sm text-[#E2E8F0] rounded p-2 mb-3 form-select focus:ring-1 focus:ring-[#38BDF8]"
                    >
                        <option value="offensive">Offensive language/abuse</option>
                        <option value="spam">Spam or advertising</option>
                        <option value="false_claim">False claims/Not a tenant</option>
                        <option value="other">Other policy violation</option>
                    </select>

                    {status === 'error' && <p className="text-xs text-[#F87171] mb-2">{errorMsg}</p>}

                    <div className="flex justify-end gap-2">
                        <button
                            onClick={() => setIsOpen(false)}
                            className="px-3 py-1.5 text-xs text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#334155] rounded transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={submitFlag}
                            disabled={status === 'loading'}
                            className="px-3 py-1.5 text-xs bg-[#DC2626] text-white rounded hover:bg-[#B91C1C] disabled:opacity-50 transition-colors flex items-center"
                        >
                            {status === 'loading' ? <Loader2 size={12} className="animate-spin" /> : 'Submit Flag'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
