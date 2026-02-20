import { motion } from 'framer-motion';
import { UploadCloud, Store, ShoppingBag } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const QuickActions = () => {
    const navigate = useNavigate();

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-card border border-border rounded-2xl p-6 shadow-sm flex flex-col h-full"
        >
            <div className="mb-4">
                <h3 className="text-lg font-bold text-foreground">빠른 작업</h3>
                <p className="text-sm text-muted-foreground mt-1">자주 사용하는 기능을 선택하세요.</p>
            </div>

            <div className="space-y-3 flex-1 flex flex-col justify-center">
                <button
                    onClick={() => navigate('/excel')}
                    className="flex items-center gap-3 p-4 rounded-xl border border-border bg-background hover:border-primary/50 hover:bg-primary/5 transition-all w-full text-left group shadow-sm hover:shadow"
                >
                    <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform">
                        <UploadCloud className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="font-semibold text-foreground group-hover:text-primary transition-colors">엑셀 대량 가공</div>
                        <div className="text-xs text-muted-foreground mt-0.5">제품명 최적화 및 키워드 추출</div>
                    </div>
                </button>

                <button className="flex items-center gap-3 p-4 rounded-xl border border-border bg-background/50 opacity-60 cursor-not-allowed w-full text-left shadow-sm">
                    <div className="p-2.5 rounded-lg bg-green-500/10 text-green-600 dark:text-green-500">
                        <Store className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="font-semibold text-foreground flex items-center gap-2">
                            스마트스토어 등록
                            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-muted text-muted-foreground">예정</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-0.5">가공된 상품 원클릭 등록</div>
                    </div>
                </button>

                <button className="flex items-center gap-3 p-4 rounded-xl border border-border bg-background/50 opacity-60 cursor-not-allowed w-full text-left shadow-sm">
                    <div className="p-2.5 rounded-lg bg-red-500/10 text-red-600 dark:text-red-500">
                        <ShoppingBag className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="font-semibold text-foreground flex items-center gap-2">
                            쿠팡 상품 등록
                            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-muted text-muted-foreground">예정</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-0.5">쿠팡 API를 통한 자동 업로드</div>
                    </div>
                </button>
            </div>
        </motion.div>
    );
};
