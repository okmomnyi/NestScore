"use client";

import { useState } from 'react';
import { MessageSquare, Loader2, Send } from 'lucide-react';
import { api } from '@/lib/api';

export default function ReplyForm({ plotId, reviewId, onReplySuccess }: { plotId: string; reviewId: string; onReplySuccess: (text: string) => void }) {
    const [isOpen, setIsOpen] = useState(false);
    const [text, setText] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle');
    const [errorMsg, setErrorMsg] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (text.length < 10) return;

        setStatus('loading');
        setErrorMsg('');

        try {
            await api.disputes.submit({
                plot_id: plotId,
                review_id: reviewId,
                landlord_response_text: text,
            });
            onReplySuccess(text);
            setStatus('idle');
            setIsOpen(false);
        } catch (err: any) {
            setStatus('error');
            setErrorMsg(err.message || 'Failed to post reply.');
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-1.5 px-2 py-1 text-xs font-medium text-[#64748B] hover:text-[#38BDF8] hover:bg-[#38BDF8]/10 rounded-md transition-colors"
            >
                <MessageSquare size={14} />
                Reply
            </button>
        );
    }

    return (
        <div className="mt-4 pt-4 border-t border-[#1E293B] w-full">
            <h4 className="text-sm font-semibold text-[#F1F5F9] mb-2 font-space">Post a Public Reply</h4>
            <form onSubmit={handleSubmit}>
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Write a professional response (minimum 10 characters)..."
                    className="w-full bg-[#0F172A] border border-[#334155] text-sm text-[#E2E8F0] rounded-lg p-3 min-h-[100px] resize-y focus:outline-none focus:ring-1 focus:ring-[#38BDF8] mb-2"
                    maxLength={500}
                />

                {status === 'error' && <p className="text-xs text-[#DC2626] mb-3">{errorMsg}</p>}

                <div className="flex justify-between items-center">
                    <span className="text-[10px] text-[#64748B]">{text.length}/500 chars</span>
                    <div className="flex gap-2">
                        <button
                            type="button"
                            onClick={() => setIsOpen(false)}
                            className="px-3 py-1.5 text-xs text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#334155] rounded-md transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={status === 'loading' || text.length < 10}
                            className="px-3 py-1.5 bg-[#38BDF8] hover:bg-[#0284C7] text-white text-xs font-bold rounded-md disabled:opacity-50 transition-colors flex items-center gap-1.5 shadow-md shadow-blue-500/20"
                        >
                            {status === 'loading' ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
                            Publish Reply
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}
