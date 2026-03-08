import { Lock } from 'lucide-react';

export default function PrivacyPage() {
    return (
        <div className="container mx-auto px-4 py-12 max-w-3xl">
            <div className="mb-10 text-center">
                <div className="w-16 h-16 bg-[#1E293B] border border-[#334155] rounded-full flex items-center justify-center mx-auto mb-6">
                    <Lock className="text-[#38BDF8]" size={28} />
                </div>
                <h1 className="text-3xl font-bold font-space text-[#F1F5F9] mb-4">Privacy Policy</h1>
                <p className="text-[#94A3B8]">Last Updated: {new Date().toLocaleDateString()}</p>
            </div>

            <div className="prose prose-invert prose-[#94A3B8] max-w-none bg-[#1E293B] border border-[#334155] rounded-xl p-8 font-dm leading-relaxed">
                <h2 className="text-xl font-bold text-[#F1F5F9] font-space mt-0">1. Our Philosophy</h2>
                <p>
                    NestScore is built privacy-first. We believe students should be able to share their housing experiences without fear of retaliation from landlords. We achieve this through extreme data minimization and strict cryptographic irreversibility.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">2. Data We Collect</h2>
                <p>We actively collect the following data when you interact with the platform:</p>
                <ul className="list-disc pl-5 mt-2 space-y-2">
                    <li><strong>Review Content:</strong> The text and star rating you submit.</li>
                    <li><strong>Plot Suggestions:</strong> Information submitted via the Suggest a Plot form.</li>
                    <li><strong>Hashed Device Fingerprints:</strong> We generate a local device fingerprint when you submit a review or interaction. This string is hashed on your device using SHA-256 before leaving your browser. Upon reaching our server, it is hashed <em>again</em> with a server-side secret salt. We only store the final double-hashed string.</li>
                    <li><strong>Hashed IP Addresses:</strong> We do not log or store plaintext IP addresses. When you connect, your IP address is immediately hashed using SHA-256 combined with a daily-rotating salt. This allows us to prevent rate-limit abuse for a 24-hour period, after which the salt changes and historical IP tracking becomes impossible.</li>
                </ul>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">3. No Personal Data Collection</h2>
                <p className="bg-[#422006]/30 border-l-4 border-[#D97706] p-4 text-[#E2E8F0] my-6 italic">
                    <strong>Explicit Statement:</strong> NestScore collects absolutely zero personally identifiable information (PII) as defined by the Kenya Data Protection Act 2019 regarding students. We do not ask for, collect, or store student names, registration numbers, phone numbers, or email addresses.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">4. Landlord Data</h2>
                <p>
                    If a landlord chooses to claim a plot, they must provide an email address. This email address is used <strong>one time</strong> to send a verification link and is hashed immediately by our servers using SHA-256. We do not store the plaintext email address in our database.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">5. Third-Party Services</h2>
                <p>
                    We use Cloudflare Turnstile to prevent automated abuse (bots). Turnstile respects privacy and does not rely on invasive tracking. If advertisements are enabled, they are served via standard generic ad networks (like Google AdSense) which may set their own standard session cookies. We use Google's Gemini AI API purely for evaluating review toxicity and quality; review text is transmitted securely for analysis but is never linked to PII.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">6. Data Retention</h2>
                <p>
                    Hashed identifiers (device and IP) are retained strictly for abuse prevention and rate-limiting enforcement. Review content and related metadata are retained indefinitely unless removed by community flagging or moderation due to policy violations.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">7. Contact</h2>
                <p>
                    For privacy queries or legal requests regarding data handling, please use the secure <a href="/contact" className="text-[#38BDF8] hover:underline">Contact Form</a>.
                </p>
            </div>
        </div>
    );
}
