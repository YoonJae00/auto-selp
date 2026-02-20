import { useState } from 'react';
import { UploadZone } from '../components/dashboard/UploadZone';
import { JobStatus } from '../components/dashboard/JobStatus';
import { HistoryTable } from '../components/dashboard/HistoryTable';
import { Layout } from '../components/layout/Layout';
import { motion } from 'framer-motion';

const ExcelProcessor = () => {
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
                className="space-y-8 pb-12"
            >
                <div className="mb-6">
                    <h1 className="text-3xl font-extrabold text-foreground w-fit pb-1 flex items-center gap-3">
                        <span className="p-2 rounded-xl bg-primary/10 text-primary">📦</span>
                        엑셀 대량 상품 가공
                    </h1>
                    <p className="text-muted-foreground mt-2 font-medium">
                        원본 상품 엑셀을 업로드하여 자동으로 상품명과 키워드를 최적화합니다.
                    </p>
                </div>

                <div className="space-y-8">
                    <UploadZone onUploadSuccess={handleUploadSuccess} />

                    {activeJobId && <JobStatus jobId={activeJobId} />}

                    <div className="pt-6 border-t border-border">
                        <div className="mb-6">
                            <h2 className="text-xl font-bold text-foreground">최근 작업 내역</h2>
                            <p className="text-sm text-muted-foreground mt-1">
                                과거에 처리한 엑셀 가공 작업들의 상태를 확인하고 다운로드합니다.
                            </p>
                        </div>
                        <HistoryTable />
                    </div>
                </div>
            </motion.div>
        </Layout>
    );
};

export default ExcelProcessor;
