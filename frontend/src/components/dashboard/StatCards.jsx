import { motion } from 'framer-motion';
import { PackageOpen, CheckCircle2, TrendingUp, AlertCircle } from 'lucide-react';

const stats = [
    { label: "오늘 처리한 상품", value: "0", icon: PackageOpen, color: "text-blue-500", bg: "bg-blue-500/10" },
    { label: "성공률", value: "0%", icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" },
    { label: "실패 건수", value: "0", icon: AlertCircle, color: "text-red-500", bg: "bg-red-500/10" },
    { label: "주간 판매 추이", value: "+0%", icon: TrendingUp, color: "text-purple-500", bg: "bg-purple-500/10" },
];

export const StatCards = () => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat, i) => (
                <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="bg-card border border-border rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
                >
                    <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/5 to-transparent rounded-bl-full -z-10 opacity-50 group-hover:scale-110 transition-transform duration-500" />
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground mb-1">{stat.label}</p>
                            <h3 className="text-2xl font-bold text-foreground">{stat.value}</h3>
                        </div>
                        <div className={`p-2.5 rounded-xl ${stat.bg} ${stat.color}`}>
                            <stat.icon className="w-5 h-5" />
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
