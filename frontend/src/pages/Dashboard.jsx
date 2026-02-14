import { useState } from 'react';
import { UploadZone } from '../components/dashboard/UploadZone';
import { JobStatus } from '../components/dashboard/JobStatus';
import { HistoryTable } from '../components/dashboard/HistoryTable';
import { Layout } from '../components/layout/Layout';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const [activeJobId, setActiveJobId] = useState(null);

    const handleUploadSuccess = (data) => {
        // Backend returns { job_id: "..." }
        if (data?.job_id) {
            setActiveJobId(data.job_id);
        }
    };

    return (
        <Layout>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
            >
                <div>
                    <h1 className="text-3xl font-bold text-white">대시보드</h1>
                    <p className="text-gray-400 mt-2">엑셀 파일을 업로드하여 처리를 시작하세요.</p>
                </div>

                <UploadZone onUploadSuccess={handleUploadSuccess} />

                {activeJobId && <JobStatus jobId={activeJobId} />}

                <HistoryTable />
            </motion.div>
        </Layout>
    );
};

export default Dashboard;
