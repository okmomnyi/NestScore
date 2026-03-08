"use client";

import { useState } from 'react';
import { api } from '@/lib/api';
import { getFingerprintHash } from '@/lib/fingerprint';
import { TURNSTILE_SITE_KEY } from '@/lib/constants';
import Turnstile from 'react-turnstile';
import StarRating from '../ui/StarRating';
import { Loader2, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { cn } from '../ui/Badge';

export default function ReviewForm({ plotId }: { plotId: string }) {
    const [stars, setStars] = useState(0);
    const [comment, setComment] = useState('');
    const [token, setToken] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [errorMsg, setErrorMsg] = useState('');

    const minChars = 80;
    const maxChars = 2000;
    const isLengthValid = comment.length >= minChars && comment.length <= maxChars;
    const isFormValid = stars > 0 && isLengthValid && token;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isFormValid) return;

        setStatus('loading');
        setErrorMsg('');

        try {
            const fingerprint_hash = await getFingerprintHash();
            await api.reviews.submit({
                plot_id: plotId,
                stars,
                comment_text: comment,
                fingerprint_hash,
                turnstile_token: token,
            });
            setStatus('success');
        } catch (err: any) {
            setStatus('error');
            setErrorMsg(err.message || 'An error occurred while submitting your review.');
            // Reset Turnstile on error
            setToken('');
        }
    };

    if (status === 'success') {
        return (
            <div className="bg-[#14532D]/30 border border-[#22C55E]/30 rounded-xl p-8 text-center flex flex-col items-center">
                <div className="h-16 w-16 bg-[#14532D] rounded-full flex items-center justify-center mb-4">
                    <CheckCircle2 size={32} className="text-[#4ADE80]" />
                </div>
                <h3 className="text-xl font-bold text-[#F1F5F9] mb-2 font-space">Review Submitted Successfully</h3>
                <p className="text-[#94A3B8] max-w-md">
                    Thank you for contributing to the NestScore community. Your review has been published instantly and is now visible to everyone.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-6 md:p-8">
            <div className="flex items-center gap-2 mb-6 text-[#38BDF8]">
                <ShieldCheck size={20} />
                <h3 className="text-xl font-bold font-space text-[#F1F5F9]">Leave an Anonymous Review</h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm">
                        Overall Rating <span className="text-[#DC2626]">*</span>
                    </label>
                    <div className="bg-[#0F172A] p-4 rounded-lg inline-block border border-[#334155]">
                        <StarRating value={stars} onChange={setStars} size={28} />
                    </div>
                    {stars === 0 && <p className="text-xs text-[#94A3B8] mt-2 font-medium">Please select a rating.</p>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm flex justify-between items-end">
                        <span>Review <span className="text-[#DC2626]">*</span></span>
                        <span className={cn(
                            "text-xs font-mono font-medium",
                            comment.length < minChars ? "text-[#DC2626]" : "text-[#16A34A]"
                        )}>
                            {comment.length}/{maxChars} chars
                        </span>
                    </label>
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Describe your living experience here. Be honest and objective. Tell us about water reliability, security, landlord responsiveness, noise levels, and internet connection."
                        className="w-full bg-[#0F172A] border border-[#334155] text-[#E2E8F0] rounded-xl p-4 min-h-[160px] resize-y focus:outline-none focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent transition-all font-dm placeholder:text-[#475569] leading-relaxed"
                        maxLength={maxChars}
                    />
                    {comment.length > 0 && comment.length < minChars && (
                        <p className="text-xs text-[#DC2626] mt-2 font-medium">Minimum {minChars} characters required. Keep typing.</p>
                    )}
                </div>

                <div className="bg-[#0F172A] p-4 rounded-xl border border-[#334155] overflow-hidden">
                    <Turnstile
                        sitekey={TURNSTILE_SITE_KEY}
                        onVerify={(newToken) => setToken(newToken)}
                        theme="dark"
                        className="mx-auto"
                    />
                </div>

                {status === 'error' && (
                    <div className="bg-[#450A0A] border border-[#7F1D1D] text-[#F87171] p-4 rounded-lg text-sm font-medium">
                        {errorMsg}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={!isFormValid || status === 'loading'}
                    className="w-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold py-4 px-6 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center shadow-lg shadow-blue-900/20 active:scale-[0.98] font-space text-lg"
                >
                    {status === 'loading' ? (
                        <span className="flex items-center gap-2"><Loader2 className="animate-spin" size={20} /> Submitting...</span>
                    ) : (
                        isFormValid ? "Submit Review Anonymously" : "Complete all fields to submit"
                    )}
                </button>
                <p className="text-center text-xs text-[#64748B] mt-4 font-medium px-4">
                    By submitting this review, you agree to our Terms of Service. NestScore does not collect IP addresses or email addresses for review submissions. Your device fingerprint is hashed locally before transmission to ensure anonymity.
                </p>
            </form>
        </div>
    );
}
