import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Settings, LogOut, Wand2, ChevronDown, FileSpreadsheet, Key, Palette } from 'lucide-react';
import { cn } from '../../lib/utils';
import { supabase } from '../../lib/supabase';

const navItems = [
    { icon: LayoutDashboard, label: '대시보드', path: '/' },
    { icon: FileSpreadsheet, label: '엑셀 가공', path: '/excel' },
];

const settingsSubItems = [
    { label: '엑셀 설정', path: '/settings?tab=excel', icon: FileSpreadsheet },
    { label: 'API 키', path: '/settings?tab=api', icon: Key },
    { label: '프롬프트', path: '/settings?tab=prompts', icon: Wand2 },
    { label: '테마', path: '/settings?tab=theme', icon: Palette },
];

export const Sidebar = () => {
    const location = useLocation();
    const [settingsOpen, setSettingsOpen] = useState(location.pathname.includes('/settings'));
    const isSettingsActive = location.pathname.includes('/settings');

    return (
        <motion.aside
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="w-64 h-screen bg-card/95 backdrop-blur-xl border-r border-border flex flex-col fixed left-0 top-0 z-40 shadow-[4px_0_24px_rgba(0,0,0,0.02)] dark:shadow-[4px_0_24px_rgba(0,0,0,0.2)]"
        >
            <div className="p-6 flex items-center gap-3 border-b border-border">
                <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <Wand2 className="w-5 h-5" />
                </div>
                <span className="font-bold text-xl text-foreground">
                    Auto-Selp
                </span>
            </div>

            <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative",
                            isActive
                                ? "bg-primary/10 text-primary shadow-md border border-primary/20 font-medium"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.label}</span>
                    </NavLink>
                ))}

                {/* Settings Dropdown */}
                <div>
                    <button
                        onClick={() => setSettingsOpen(!settingsOpen)}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 w-full",
                            isSettingsActive
                                ? "bg-primary/10 text-primary shadow-md border border-primary/20 font-medium"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                    >
                        <Settings className="w-5 h-5" />
                        <span className="font-medium flex-1 text-left">설정</span>
                        <ChevronDown
                            className={cn(
                                "w-4 h-4 transition-transform duration-200",
                                settingsOpen ? "rotate-180" : ""
                            )}
                        />
                    </button>

                    <AnimatePresence>
                        {settingsOpen && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.2 }}
                                className="overflow-hidden"
                            >
                                <div className="ml-4 mt-1 space-y-1 border-l-2 border-border pl-2">
                                    {settingsSubItems.map((subItem) => (
                                        <NavLink
                                            key={subItem.path}
                                            to={subItem.path}
                                            className={({ isActive }) => cn(
                                                "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm",
                                                location.search.includes(subItem.path.split('=')[1]) || (subItem.path.includes('excel') && !location.search && isSettingsActive)
                                                    ? "bg-primary/5 text-primary font-medium"
                                                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                                            )}
                                        >
                                            <subItem.icon className="w-4 h-4" />
                                            <span>{subItem.label}</span>
                                        </NavLink>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </nav>

            <div className="p-4 border-t border-border">
                <button
                    onClick={() => supabase.auth.signOut()}
                    className="flex items-center gap-3 px-4 py-3 w-full text-left text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-xl transition-colors"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">로그아웃</span>
                </button>
            </div>
        </motion.aside>
    );
};
