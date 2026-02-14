import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, Settings, LogOut, Wand2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { supabase } from '../../lib/supabase';

const navItems = [
    { icon: LayoutDashboard, label: '대시보드', path: '/' },
    { icon: FileText, label: '프롬프트', path: '/prompts' },
    { icon: Settings, label: '설정', path: '/settings' },
];

export const Sidebar = () => {
    return (
        <motion.aside
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="w-64 h-screen bg-gray-950/50 backdrop-blur-xl border-r border-white/10 flex flex-col fixed left-0 top-0 z-40"
        >
            <div className="p-6 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                    <Wand2 className="w-5 h-5" />
                </div>
                <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    Auto-Selp
                </span>
            </div>

            <nav className="flex-1 px-4 py-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                            isActive
                                ? "bg-indigo-500/10 text-indigo-400 shadow-lg shadow-indigo-500/5 border border-indigo-500/20"
                                : "text-gray-400 hover:bg-white/5 hover:text-white"
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.label}</span>
                        {/* Active Indicator */}
                        {({ isActive }) => isActive && (
                            <motion.div
                                layoutId="activeNav"
                                className="absolute left-0 w-1 h-8 bg-indigo-500 rounded-r-full"
                            />
                        )}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-white/5">
                <button
                    onClick={() => supabase.auth.signOut()}
                    className="flex items-center gap-3 px-4 py-3 w-full text-left text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-colors"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">로그아웃</span>
                </button>
            </div>
        </motion.aside>
    );
};
