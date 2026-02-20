import { BarChart, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export const SalesChart = () => {
    // Dummy heights for chart bars
    const dummyData = [40, 60, 30, 80, 50, 90, 70];
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-1 lg:col-span-2 bg-card border border-border rounded-2xl p-6 shadow-sm overflow-hidden relative"
        >
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/5 rounded-full blur-3xl" />

            <div className="flex items-center justify-between mb-6 relative z-10">
                <div>
                    <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                        <BarChart className="w-5 h-5 text-primary" />
                        주간 매출 현황 (예정)
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                        스마트스토어와 쿠팡 연동 시 이곳에 매출 그래프가 표시됩니다.
                    </p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 text-primary rounded-full text-xs font-semibold">
                    <Activity className="w-3.5 h-3.5" />
                    Coming Soon
                </div>
            </div>

            {/* Mock Chart Area */}
            <div className="h-48 w-full flex items-end justify-between gap-2 px-2 pb-6 border-b border-border/50 relative z-10">
                {/* Horizontal Guide Lines */}
                <div className="absolute top-0 w-full border-t border-border/50 border-dashed" />
                <div className="absolute top-1/2 w-full border-t border-border/50 border-dashed transform -translate-y-1/2" />

                {dummyData.map((height, i) => (
                    <div key={i} className="flex flex-col items-center flex-1 group h-full justify-end relative">
                        <div className="w-full flex justify-center h-full items-end relative">
                            {/* Hover tooltip placeholder */}
                            <div className="absolute -top-8 bg-foreground text-background text-xs font-bold py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-20 shadow-lg">
                                데이터 수집중
                            </div>
                            <div
                                className="w-8/12 max-w-[40px] bg-primary/20 group-hover:bg-primary/50 transition-colors rounded-t-sm"
                                style={{ height: `${height}%` }}
                            />
                        </div>
                        <span className="text-xs text-muted-foreground mt-3 font-medium">{days[i]}</span>
                    </div>
                ))}
            </div>
        </motion.div>
    );
};
