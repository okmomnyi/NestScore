import { Shield } from 'lucide-react';

export default function TermsPage() {
    return (
        <div className="container mx-auto px-4 py-12 max-w-3xl">
            <div className="mb-10 text-center">
                <div className="w-16 h-16 bg-[#1E293B] border border-[#334155] rounded-full flex items-center justify-center mx-auto mb-6">
                    <Shield className="text-[#38BDF8]" size={28} />
                </div>
                <h1 className="text-3xl font-bold font-space text-[#F1F5F9] mb-4">Terms of Service</h1>
                <p className="text-[#94A3B8]">Last Updated: {new Date().toLocaleDateString()}</p>
            </div>

            <div className="prose prose-invert prose-[#94A3B8] max-w-none bg-[#1E293B] border border-[#334155] rounded-xl p-8 font-dm leading-relaxed">
                <h2 className="text-xl font-bold text-[#F1F5F9] font-space mt-0">1. Operator Identity and Platform Purpose</h2>
                <p>
                    NestScore is operated transparently but anonymously by the "NestScore Community." We do not identify individual operators to prevent retaliation or pressure from property owners. The platform serves exclusively as a peer-to-peer venue for students at Meru University of Science and Technology (MUST) to share <em>subjective experiences</em> regarding local rental properties.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">2. Listing Policy (Cannot Opt-Out)</h2>
                <p>
                    NestScore lists all known student rental plots near MUST regardless of whether the landlord or property manager consents to being listed. <strong>Landlords cannot opt out of being listed.</strong> If students live at a property, it is considered listable. We maintain this policy to ensure the platform remains a comprehensive, independent resource for the student community, rather than a curated advertising board.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">3. Content Rules</h2>
                <p>Users submitting reviews must adhere strictly to the following rules:</p>
                <ul className="list-disc pl-5 mt-2 space-y-2">
                    <li><strong>No Individual Names:</strong> Reviews must address the property, management company, or the role (e.g., "the caretaker"), not specific individual names.</li>
                    <li><strong>Opinions Only:</strong> Reviews must represent your subjective experience. Do not state contested factual claims as absolute truth.</li>
                    <li><strong>No Commercial Content:</strong> Spam, advertising, or promotional material is strictly prohibited.</li>
                    <li><strong>Length Requirements:</strong> Reviews must be between 80 and 2000 characters to ensure detailed, helpful feedback.</li>
                    <li><strong>Zero Tolerance for Abuse:</strong> Hate speech, severe profanity, threats, or harassment will result in immediate removal by our moderation AI or human review team.</li>
                </ul>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">4. Advertisement Policy</h2>
                <p>
                    To maintain absolute impartiality, NestScore only runs generic, third-party network advertisements (such as Google AdSense). We strictly prohibit direct sponsorships, "featured plot" payments, or any property-related advertisers from buying targeted space on the platform.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">5. Disclaimer of Verification</h2>
                <p>
                    NestScore does not verify the factual accuracy of claims made in student reviews, nor do we verify the identity of the students posting them. We employ algorithmic and moderation strategies to limit spam, but all reviews are published "as is." Readers must exercise their own judgment. Note that landlords may claim a property to post official dispute responses.
                </p>

                <h2 className="text-xl font-bold text-[#F1F5F9] font-space">6. Modifications</h2>
                <p>
                    The NestScore Community reserves the right to modify these Terms at any time without prior individual notice. Continued use of the platform constitutes agreement to the updated Terms.
                </p>
            </div>
        </div>
    );
}
