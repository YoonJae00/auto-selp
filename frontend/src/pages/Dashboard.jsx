import { StatCards } from '../components/dashboard/StatCards';
import { SalesChart } from '../components/dashboard/SalesChart';
import { QuickActions } from '../components/dashboard/QuickActions';
import { Layout } from '../components/layout/Layout';
import { motion } from 'framer-motion';

const Dashboard = () => {

    return (
        <Layout>
            <div className="space-y-8 pb-12">
                {/* Welcome & Stats */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className="mb-6">
                        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-500 w-fit pb-1">
                            환영합니다!
                        </h1>
                        <p className="text-muted-foreground mt-2 font-medium">
                            Auto-Selp 대시보드에서 비즈니스 현황을 한눈에 확인하세요.
                        </p>
                    </div>
                    <StatCards />
                </motion.div>

                {/* Charts & Actions Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <SalesChart />
                    <QuickActions />
                </div>
            </div>
        </Layout>
    );
};

export default Dashboard;
