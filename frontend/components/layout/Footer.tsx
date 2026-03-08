import Link from 'next/link';
import Disclaimer from '../ui/Disclaimer';

export default function Footer() {
    return (
        <footer className="border-t border-[#1E293B] bg-[#0F172A] mt-12 py-12">
            <div className="container mx-auto px-4 max-w-4xl">
                <Disclaimer />

                <div className="mt-8 pt-8 border-t border-[#1E293B] flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[#64748B]">
                    <p>© {new Date().getFullYear()} NestScore Community. All rights reserved.</p>
                    <div className="flex gap-6">
                        <Link href="/terms" className="hover:text-[#38BDF8] transition-colors">Terms of Service</Link>
                        <Link href="/privacy" className="hover:text-[#38BDF8] transition-colors">Privacy Policy</Link>
                        <Link href="/contact" className="hover:text-[#38BDF8] transition-colors">Contact</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
