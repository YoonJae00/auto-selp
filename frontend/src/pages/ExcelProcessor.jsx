import { useState, useEffect } from 'react';
import { UploadZone } from '../components/dashboard/UploadZone';
import { JobStatus } from '../components/dashboard/JobStatus';
import { HistoryTable } from '../components/dashboard/HistoryTable';
import { Layout } from '../components/layout/Layout';
import { motion } from 'framer-motion';
import api from '../lib/api';
import { Link } from 'react-router-dom';
import { AlertCircle, Key, ArrowRight } from 'lucide-react';

const ExcelProcessor = () => {
    const [activeJobId, setActiveJobId] = useState(null);
    const [keyStatuses, setKeyStatuses] = useState([]);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const response = await api.get('/settings');
                const keys = response.data?.api_keys || {};

                const statuses = [
                    {
                        name: "LLM API 키 (Gemini 또는 OpenAI)",
                        isMissing: !keys.gemini_api_key && !keys.openai_api_key
                    },
                    {
                        name: "네이버 검색광고 API 키 세트 (키, 시크릿, 커스터머 ID)",
                        isMissing: !keys.naver_api_key || !keys.naver_secret_key || !keys.naver_customer_id
                    },
                    {
                        name: "네이버 쇼핑 검색 API 키 세트 (Client ID, Client Secret)",
                        isMissing: !keys.naver_client_id || !keys.naver_client_secret
                    },
                    {
                        name: "쿠팡 API 키 세트 (Access Key, Secret Key)",
                        isMissing: !keys.coupang_access_key || !keys.coupang_secret_key
                    }
                ];

                setKeyStatuses(statuses);
            } catch (error) {
                console.error("Failed to fetch settings:", error);
            }
        };

        fetchSettings();
    }, []);

    const handleUploadSuccess = (data) => {
        if (data?.job_id) {
            setActiveJobId(data.job_id);
        }
    };

    const missingKeys = keyStatuses.filter(s => s.isMissing);

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

                {missingKeys.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3"
                    >
                        <AlertCircle className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
                        <div className="flex-1">
                            <p className="font-semibold text-amber-600 dark:text-amber-400 text-sm mb-1">
                                일부 API 키가 설정되지 않았습니다
                            </p>
                            <ul className="text-sm text-amber-700 dark:text-amber-300 space-y-0.5 mb-2">
                                {missingKeys.map((item, idx) => (
                                    <li key={idx}>• {item.name}</li>
                                ))}
                            </ul>
                            <Link
                                to="/settings"
                                className="inline-flex items-center gap-1.5 text-sm font-semibold text-amber-700 dark:text-amber-300 hover:underline"
                            >
                                <Key className="w-3.5 h-3.5" />
                                설정 페이지에서 입력하기
                                <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                        </div>
                    </motion.div>
                )}

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
