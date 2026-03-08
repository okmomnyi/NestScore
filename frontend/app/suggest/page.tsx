"use client";

import { useState } from 'react';
import { api } from '@/lib/api';
import { getFingerprintHash } from '@/lib/fingerprint';
import { PLOT_AREAS } from '@/lib/constants';
import { Loader2, PlusCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import Turnstile from 'react-turnstile';
import { TURNSTILE_SITE_KEY } from '@/lib/constants';

export default function SuggestPlotPage() {
    const [name, setName] = useState('');
    const [area, setArea] = useState(PLOT_AREAS[0] as string);
    const [notes, setNotes] = useState('');
    const [token, setToken] = useState('');

    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [errorMsg, setErrorMsg] = useState('');

    const isFormValid = name.length >= 3 && area && token;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isFormValid) return;

        setStatus('loading');
        setErrorMsg('');

        try {
            const fbHash = await getFingerprintHash();
            await api.suggestions.submit({
                suggested_name: name,
                area,
                notes,
                fingerprint_hash: fbHash
            });
            setStatus('success');
        } catch (err: any) {
            setStatus('error');
            setErrorMsg(err.message || "Failed to submit suggestion.");
            setToken('');
        }
    };

    if (status === 'success') {
        return (
            <div className="container mx-auto px-4 py-16 max-w-2xl">
                <div className="bg-[#14532D]/30 border border-[#22C55E]/30 rounded-xl p-8 text-center flex flex-col items-center">
                    <CheckCircle2 size={48} className="text-[#4ADE80] mb-4" />
                    <h2 className="text-2xl font-bold font-space text-[#F1F5F9] mb-3">Suggestion Received</h2>
                    <p className="text-[#94A3B8]">
                        Thank you for helping grow the NestScore community. Our moderators will review your addition and it should be live shortly.
                    </p>
                    <a href="/" className="mt-8 text-[#38BDF8] hover:underline font-medium">Return to Map</a>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-12 max-w-2xl">
            <div className="mb-10">
                <h1 className="text-3xl font-bold font-space text-[#F1F5F9] flex items-center gap-3 mb-4">
                    <PlusCircle className="text-[#38BDF8]" />
                    Suggest a Plot
                </h1>
                <p className="text-[#94A3B8]">
                    Don't see your hostel or apartment on the map? Add it here. All suggestions are anonymously tracked and manually verified by our team to prevent spam before they appear for rating.
                </p>
            </div>

            <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-6 md:p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm">Plot Name <span className="text-[#DC2626]">*</span></label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g. Genesis Hostel, New Life Apartments"
                            className="w-full bg-[#0F172A] border border-[#334155] text-[#E2E8F0] rounded-lg p-3 focus:outline-none focus:ring-1 focus:ring-[#38BDF8]"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm">Area <span className="text-[#DC2626]">*</span></label>
                        <select
                            value={area}
                            onChange={(e) => setArea(e.target.value)}
                            className="w-full bg-[#0F172A] border border-[#334155] text-[#E2E8F0] rounded-lg p-3 focus:outline-none focus:ring-1 focus:ring-[#38BDF8]"
                        >
                            {PLOT_AREAS.map(a => <option key={a} value={a}>{a}</option>)}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm">Additional Details (Optional)</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Directions from main gate, distinct features, etc."
                            className="w-full bg-[#0F172A] border border-[#334155] text-[#E2E8F0] rounded-lg p-3 min-h-[100px] resize-y focus:outline-none focus:ring-1 focus:ring-[#38BDF8]"
                        />
                    </div>

                    <div className="bg-[#0F172A] p-4 rounded-xl border border-[#334155] overflow-hidden flex justify-center">
                        <Turnstile
                            sitekey={TURNSTILE_SITE_KEY}
                            onVerify={(newToken) => setToken(newToken)}
                            theme="dark"
                        />
                    </div>

                    {status === 'error' && (
                        <div className="bg-[#450A0A] border border-[#7F1D1D] text-[#F87171] p-4 rounded-lg text-sm font-medium flex items-center gap-2">
                            <ShieldAlert size={16} /> {errorMsg}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={!isFormValid || status === 'loading'}
                        className="w-full bg-[#334155] hover:bg-[#475569] text-white font-bold py-4 px-6 rounded-lg transition-all disabled:opacity-50 flex justify-center items-center shadow-lg"
                    >
                        {status === 'loading' ? <Loader2 className="animate-spin" /> : "Submit Plot"}
                    </button>
                </form>
            </div>
        </div>
    );
}
