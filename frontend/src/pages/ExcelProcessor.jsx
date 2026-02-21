import { useState, useEffect } from 'react';
import { UploadZone } from '../components/dashboard/UploadZone';
import { JobStatus } from '../components/dashboard/JobStatus';
import { HistoryTable } from '../components/dashboard/HistoryTable';
import { Layout } from '../components/layout/Layout';
import { motion } from 'framer-motion';
import api from '../lib/api';
import { Link } from 'react-router-dom';
import { AlertCircle, Key, ArrowRight, Loader2 } from 'lucide-react';

const ExcelProcessor = () => {
    const [activeJobId, setActiveJobId] = useState(null);
    const [isLoadingSettings, setIsLoadingSettings] = useState(true);
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
                setKeyStatuses([{ name: "설정 정보 (서버 연결 오류)", isMissing: true }]);
            } finally {
                setIsLoadingSettings(false);
            }
        };

        fetchSettings();
    }, []);

    const handleUploadSuccess = (data) => {
        // Backend returns { job_id: "..." }
        if (data?.job_id) {
            setActiveJobId(data.job_id);
        }
    };

    const hasMissingKeys = keyStatuses.some(s => s.isMissing);

    const renderMissingKeysAlert = () => (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-destructive/5 border-l-4 border-destructive p-6 rounded-xl shadow-sm my-8"
        >
            <div className="flex items-start gap-4">
                <div className="p-2 bg-destructive/10 rounded-full mt-1">
                    <AlertCircle className="w-6 h-6 text-destructive" />
                </div>
                <div className="flex-1">
                    <h3 className="text-xl font-bold text-destructive mb-2">
                        필수 API 키 입력이 필요합니다
                    </h3>
                    <p className="text-foreground/80 mb-4 font-medium">
                        대량 엑셀 처리를 시작하려면 아래의 API 키가 반드시 필요합니다. 설정 페이지에서 누락된 키를 먼저 입력해주세요.
                    </p>
                    <ul className="space-y-2.5 mb-6">
                        {keyStatuses.map((item, idx) => (
                            <li key={idx} className={`flex items-center gap-2 text-sm font-semibold ${item.isMissing ? 'text-destructive' : 'text-green-600 dark:text-green-500'}`}>
                                {item.isMissing ? (
                                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-destructive/20 text-destructive text-xs">✕</span>
                                ) : (
                                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-green-500/20 text-green-600 dark:text-green-500 text-xs">✓</span>
                                )}
                                {item.name}
                            </li>
                        ))}
                    </ul>
                    <Link
                        to="/settings"
                        className="inline-flex items-center gap-2 px-6 py-2.5 bg-primary text-primary-foreground font-bold rounded-lg hover:bg-primary/90 transition-all shadow-md hover:shadow-lg active:scale-95"
                    >
                        <Key className="w-4 h-4" />
                        API 키 설정하기
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </div>
        </motion.div>
    );

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

                {isLoadingSettings ? (
                    <div className="flex flex-col items-center justify-center py-24 bg-card rounded-2xl border border-border mt-8">
                        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
                        <p className="text-muted-foreground font-medium">API 키 상태를 확인 중입니다...</p>
                    </div>
                ) : hasMissingKeys ? (
                    renderMissingKeysAlert()
                ) : (
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
                )}
            </motion.div>
        </Layout>
    );
};

export default ExcelProcessor;
