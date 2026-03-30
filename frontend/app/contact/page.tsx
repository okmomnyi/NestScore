"use client";

import { useState } from 'react';
import { api } from '@/lib/api';
import { TURNSTILE_SITE_KEY } from '@/lib/constants';
import Turnstile from 'react-turnstile';
import { Mail, CheckCircle2, Loader2, ShieldAlert } from 'lucide-react';

export default function ContactPage() {
    const [subject, setSubject] = useState('');
    const [message, setMessage] = useState('');
    const [token, setToken] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [errorMsg, setErrorMsg] = useState('');

    const isFormValid = subject.length >= 3 && message.length >= 20 && token;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isFormValid) return;

        setStatus('loading');
        setErrorMsg('');

        try {
            await api.contact.submit({
                subject,
                message,
                turnstile_token: token
            });
            setStatus('success');
        } catch (err: any) {
            setStatus('error');
            setErrorMsg(err.message || "Failed to send message.");
            setToken('');
        }
    };

    if (status === 'success') {
        return (
            <div className="container mx-auto px-4 py-16 max-w-2xl">
                <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-8 text-center flex flex-col items-center">
                    <CheckCircle2 size={48} className="text-[#4ADE80] mb-4" />
                    <h2 className="text-2xl font-bold font-space text-[#F1F5F9] mb-3">Message Sent</h2>
                    <p className="text-[#94A3B8]">
                        Your message has been forwarded to the NestScore moderation team via an encrypted channel.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-12 max-w-2xl">
            <div className="mb-10 text-center">
                <div className="w-16 h-16 bg-[#1E293B] border border-[#334155] rounded-full flex items-center justify-center mx-auto mb-6">
                    <Mail className="text-[#38BDF8]" size={28} />
                </div>
                <h1 className="text-3xl font-bold font-space text-[#F1F5F9] mb-4">Contact Moderators</h1>
                <p className="text-[#94A3B8] max-w-lg mx-auto">
                    NestScore has no public email address to protect operator anonymity. Please use this secure form to reach us regarding severe policy violations or legal requests.
                </p>
            </div>

            <div className="bg-[#1E293B] border border-[#334155] rounded-xl p-6 md:p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm">Subject <span className="text-[#DC2626]">*</span></label>
                        <input
                            type="text"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            placeholder="Brief context"
                            className="w-full bg-[#0F172A] border border-[#334155] text-[#E2E8F0] rounded-lg p-3 focus:outline-none focus:ring-1 focus:ring-[#38BDF8]"
                            maxLength={100}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-[#E2E8F0] mb-2 font-dm flex justify-between items-end">
                            <span>Message <span className="text-[#DC2626]">*</span></span>
                            <span className="text-xs font-mono font-medium text-[#64748B]">
                                {message.length}/2000 chars
                            </span>
                        </label>
                        <textarea
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Provide sufficient detail for us to act."
                            className="w-full bg-[#0F172A] border border-[#334155] text-[#E2E8F0] rounded-lg p-3 min-h-[160px] resize-y focus:outline-none focus:ring-1 focus:ring-[#38BDF8]"
                            maxLength={2000}
                        />
                        {message.length > 0 && message.length < 20 && (
                            <p className="text-xs text-[#DC2626] mt-2">Minimum 20 characters required.</p>
                        )}
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
                        className="w-full bg-[#38BDF8] hover:bg-[#0EA5E9] text-[#0F172A] font-bold py-4 px-6 rounded-lg transition-all disabled:opacity-50 flex justify-center items-center"
                    >
                        {status === 'loading' ? <Loader2 className="animate-spin" /> : "Send Secure Message"}
                    </button>
                </form>
            </div>
        </div>
    );
}
