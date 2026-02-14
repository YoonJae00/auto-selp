import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

export const Card = ({ className, children, ...props }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
                'relative overflow-hidden rounded-2xl border border-white/10 bg-gray-950/40 backdrop-blur-xl shadow-2xl',
                className
            )}
            {...props}
        >
            {/* Decorative gradient blob */}
            <div className="absolute -top-20 -right-20 w-40 h-40 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 p-6">
                {children}
            </div>
        </motion.div>
    );
};
