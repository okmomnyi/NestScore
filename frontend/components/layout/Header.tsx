import Link from 'next/link';

export default function Header() {
    return (
        <header className="border-b border-[#1E293B] bg-[#0F172A]/80 backdrop-blur-md sticky top-0 z-50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link href="/" className="text-2xl font-bold tracking-tight text-[#38BDF8]">
                    NestScore
                </Link>
                <nav className="flex items-center gap-6">
                    <Link href="/suggest" className="text-sm font-medium text-[#94A3B8] hover:text-[#F1F5F9] transition-colors">
                        Suggest a Plot
                    </Link>

                </nav>
            </div>
        </header>
    );
}
