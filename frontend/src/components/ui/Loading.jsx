import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 'md', message = '로딩 중...' }) => {
    const sizes = {
        sm: 'w-4 h-4',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
        xl: 'w-16 h-16'
    };

    return (
        <div className="flex flex-col items-center justify-center gap-4">
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
                <Loader2 className={`${sizes[size]} text-indigo-500`} />
            </motion.div>
            {message && (
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="text-sm text-gray-400"
                >
                    {message}
                </motion.p>
            )}
        </div>
    );
};

export const LoadingSkeleton = ({ count = 3 }) => {
    return (
        <div className="space-y-4">
            {Array.from({ length: count }).map((_, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-900/30 border border-white/5 rounded-xl p-6 space-y-4"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gray-800 rounded-lg animate-pulse" />
                        <div className="flex-1 space-y-2">
                            <div className="h-4 bg-gray-800 rounded animate-pulse w-1/3" />
                            <div className="h-3 bg-gray-800 rounded animate-pulse w-2/3" />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <div className="h-10 bg-gray-800 rounded animate-pulse" />
                        <div className="h-10 bg-gray-800 rounded animate-pulse" />
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
