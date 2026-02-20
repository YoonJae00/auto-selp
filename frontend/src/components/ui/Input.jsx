import { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

export const Input = forwardRef(({ className, error, label, ...props }, ref) => {
    return (
        <div className="space-y-2">
            {label && (
                <label className="text-sm font-medium text-muted-foreground ml-1">
                    {label}
                </label>
            )}
            <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl opacity-20 group-hover:opacity-100 transition duration-500 blur group-focus-within:opacity-100" />
                <input
                    className={cn(
                        'relative w-full bg-background border border-input text-foreground rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-transparent placeholder:text-muted-foreground backdrop-blur-sm transition-all',
                        error && 'border-destructive focus:ring-destructive',
                        className
                    )}
                    ref={ref}
                    {...props}
                />
            </div>
            {error && (
                <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-destructive ml-1"
                >
                    {error}
                </motion.p>
            )}
        </div>
    );
});

Input.displayName = 'Input';
