import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'neutral' | 'transparent';
    children: React.ReactNode;
}

export default function Badge({ variant = 'default', className, children, ...props }: BadgeProps) {
    const variants = {
        default: 'bg-[#1E3A8A] text-[#93C5FD]',
        success: 'bg-[#14532D] text-[#4ADE80]',
        warning: 'bg-[#422006] text-[#FBBF24]',
        danger: 'bg-[#450A0A] text-[#F87171]',
        neutral: 'bg-[#334155] text-[#CBD5E1]',
        transparent: 'bg-transparent border border-[#334155] text-[#94A3B8]',
    };

    return (
        <span
            className={cn(
                "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
                variants[variant],
                className
            )}
            {...props}
        >
            {children}
        </span>
    );
}
