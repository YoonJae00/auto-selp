import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
    ArrowLeft, Download, CheckCircle, XCircle, Clock, Loader2,
    AlertCircle, FileText, Activity, TrendingUp, Ban
} from 'lucide-react';
import { Layout } from '../components/layout/Layout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import api from '../lib/api';
import { cn } from '../lib/utils';
import { useState } from 'react';

const stepLabels = {
    product_name: '상품명 가공',
    keyword: '키워드 생성',
    category: '카테고리 분류'
};

const statusConfig = {
    pending: {
        label: '대기 중',
        color: 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-400/10 border-yellow-200 dark:border-yellow-500/20',
        icon: Clock
    },
    processing: {
        label: '처리 중',
        color: 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-400/10 border-blue-200 dark:border-blue-500/20',
        icon: Loader2
    },
    completed: {
        label: '완료',
        color: 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-400/10 border-green-200 dark:border-green-500/20',
        icon: CheckCircle
    },
    failed: {
        label: '실패',
        color: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-400/10 border-red-200 dark:border-red-500/20',
        icon: XCircle
    },
    cancelled: {
        label: '취소됨',
        color: 'text-muted-foreground bg-muted border-border',
        icon: Ban
    }
};

const JobDetail = () => {
    const { jobId } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [showCancelConfirm, setShowCancelConfirm] = useState(false);

    const { data: job, isLoading } = useQuery({
        queryKey: ['jobDetail', jobId],
        queryFn: async () => {
            const { data } = await api.get(`/api/jobs/${jobId}`);
            return data;
        },
        refetchInterval: (data) =>
        (data?.status === 'completed' || data?.status === 'failed' || data?.status === 'cancelled'
            ? false
            : 2000), // Poll every 2 seconds when processing
    });

    const cancelMutation = useMutation({
        mutationFn: async () => {
            await api.delete(`/api/jobs/${jobId}/cancel`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['jobDetail', jobId]);
            queryClient.invalidateQueries(['jobHistory']);
            setShowCancelConfirm(false);
        },
        onError: (error) => {
            alert(`취소 실패: ${error.response?.data?.detail || error.message}`);
        }
    });

    const handleDownload = async () => {
        try {
            const response = await api.get(`/api/jobs/${jobId}/download/result`, {
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `processed_${Date.now()}.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Download failed:', err);
            alert('다운로드에 실패했습니다.');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    const formatDuration = (seconds) => {
        if (!seconds || seconds < 0) return '-';
        if (seconds < 60) return `${seconds}초`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}분 ${seconds % 60}초`;
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}시간 ${minutes}분`;
    };

    if (isLoading) {
        return (
            <Layout>
                <div className="flex items-center justify-center min-h-[50vh]">
                    <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
                </div>
            </Layout>
        );
    }

    if (!job) {
        return (
            <Layout>
                <div className="text-center py-12">
                    <AlertCircle className="w-16 h-16 mx-auto mb-4 text-destructive" />
                    <h2 className="text-xl font-semibold text-foreground mb-2">작업을 찾을 수 없습니다</h2>
                    <Button onClick={() => navigate('/')} className="mt-4">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        대시보드로 돌아가기
                    </Button>
                </div>
            </Layout>
        );
    }

    const metaData = job.meta_data || {};
    const status = statusConfig[job.status] || statusConfig.pending;
    const Icon = status.icon;
    const currentRow = metaData.current_row || 0;
    const totalRows = metaData.total_rows || 0;
    const rowsProcessed = metaData.rows_processed || 0;
    const currentStep = metaData.current_step;
    const estimatedSeconds = metaData.estimated_completion_seconds || 0;
    const chunks = metaData.chunks || [];
    const parallelCount = metaData.parallel_count || 1;

    return (
        <Layout>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
            >
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate('/')}
                            className="mb-4 text-muted-foreground hover:text-foreground"
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            돌아가기
                        </Button>
                        <h1 className="text-3xl font-bold text-foreground">작업 상세 정보</h1>
                        <p className="text-muted-foreground mt-2">실시간 진행 상황을 확인하세요</p>
                    </div>

                    {job.status === 'processing' && (
                        <Button
                            variant="ghost"
                            onClick={() => setShowCancelConfirm(true)}
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                            <Ban className="w-4 h-4 mr-2" />
                            작업 취소
                        </Button>
                    )}
                </div>

                {/* Status Card */}
                <Card className="border-border shadow-sm">
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-4">
                            <div className="p-4 rounded-xl bg-primary/10 text-primary">
                                <FileText className="w-8 h-8" />
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold text-foreground">
                                    {metaData.original_filename || '파일명 없음'}
                                </h2>
                                <p className="text-sm text-muted-foreground mt-1">작업 ID: {job.id.slice(0, 8)}...</p>
                            </div>
                        </div>
                        <div className={cn(
                            "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium border",
                            status.color
                        )}>
                            <Icon className={cn(
                                "w-4 h-4",
                                job.status === 'processing' && 'animate-spin'
                            )} />
                            {status.label}
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-muted rounded-full h-3 mb-2 overflow-hidden">
                        <motion.div
                            className="bg-primary h-3 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${job.progress || 0}%` }}
                            transition={{ duration: 0.5 }}
                        />
                    </div>
                    <div className="flex justify-between text-sm text-muted-foreground">
                        <span>진행률</span>
                        <span className="font-medium text-foreground">{job.progress || 0}%</span>
                    </div>
                </Card>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Current Progress Card */}
                    {job.status === 'processing' && currentStep && (
                        <Card className="border-blue-200 dark:border-blue-500/30 bg-blue-50 dark:bg-blue-500/5">
                            <div className="flex items-center gap-3 mb-4">
                                <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                <h3 className="text-lg font-semibold text-foreground">현재 진행 상황</h3>
                            </div>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">처리 중인 행</span>
                                    <span className="text-foreground font-medium">{currentRow} / {totalRows}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">완료된 행</span>
                                    <span className="text-foreground font-medium">{rowsProcessed}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">현재 단계</span>
                                    <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                                        {stepLabels[currentStep] || currentStep}
                                    </span>
                                </div>
                                {estimatedSeconds > 0 && (
                                    <div className="flex justify-between items-center pt-2 border-t border-border">
                                        <span className="text-muted-foreground">예상 완료 시간</span>
                                        <span className="text-green-600 dark:text-green-400 font-medium">{formatDuration(estimatedSeconds)}</span>
                                    </div>
                                )}
                            </div>
                        </Card>
                    )}

                    {/* Statistics Card */}
                    <Card className="border-border shadow-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <TrendingUp className="w-5 h-5 text-primary" />
                            <h3 className="text-lg font-semibold text-foreground">작업 정보</h3>
                        </div>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-muted-foreground">생성 시간</span>
                                <span className="text-foreground text-sm">{formatDate(job.created_at)}</span>
                            </div>
                            {metaData.processing_started_at && (
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">처리 시작</span>
                                    <span className="text-foreground text-sm">{formatDate(metaData.processing_started_at)}</span>
                                </div>
                            )}
                            {metaData.last_updated && job.status === 'processing' && (
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">마지막 업데이트</span>
                                    <span className="text-foreground text-sm">{formatDate(metaData.last_updated)}</span>
                                </div>
                            )}
                            {(metaData.completed_at || metaData.failed_at || metaData.cancelled_at) && job.status !== 'processing' && (
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">
                                        {job.status === 'completed' && '완료 시간'}
                                        {job.status === 'failed' && '실패 시간'}
                                        {job.status === 'cancelled' && '취소 시간'}
                                    </span>
                                    <span className="text-foreground text-sm">
                                        {formatDate(metaData.completed_at || metaData.failed_at || metaData.cancelled_at)}
                                    </span>
                                </div>
                            )}
                        </div>
                    </Card>
                </div>

                {/* Chunk Progress Section */}
                {parallelCount > 1 && chunks.length > 0 && (
                    <Card className="border-border shadow-sm">
                        <h3 className="text-lg font-semibold text-foreground mb-4">병렬 처리 상태</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                            {chunks.map((chunk) => {
                                const chunkStatusColors = {
                                    pending: 'border-yellow-200 dark:border-yellow-500/30 bg-yellow-50 dark:bg-yellow-500/5',
                                    processing: 'border-blue-200 dark:border-blue-500/30 bg-blue-50 dark:bg-blue-500/5',
                                    completed: 'border-green-200 dark:border-green-500/30 bg-green-50 dark:bg-green-500/5',
                                };

                                const chunkStatusIcons = {
                                    pending: '⏳',
                                    processing: '🔄',
                                    completed: '✅',
                                };

                                return (
                                    <motion.div
                                        key={chunk.id}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className={cn(
                                            "border rounded-lg p-3",
                                            chunkStatusColors[chunk.status] || chunkStatusColors.pending
                                        )}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs font-medium text-foreground">
                                                청크 #{chunk.id + 1}
                                            </span>
                                            <span className="text-sm">
                                                {chunkStatusIcons[chunk.status] || chunkStatusIcons.pending}
                                            </span>
                                        </div>
                                        <div className="w-full bg-muted rounded-full h-1.5 mb-2">
                                            <motion.div
                                                className="bg-primary h-1.5 rounded-full"
                                                initial={{ width: 0 }}
                                                animate={{ width: `${chunk.progress || 0}%` }}
                                                transition={{ duration: 0.3 }}
                                            />
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-xs text-muted-foreground">
                                                {chunk.rows_processed || 0}/{chunk.total_rows || 0}
                                            </span>
                                            <span className="text-xs text-foreground font-medium">
                                                {chunk.progress || 0}%
                                            </span>
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </Card>
                )}

                {/* Column Mapping Card */}
                {metaData.column_mapping && (
                    <Card className="border-border shadow-sm">
                        <h3 className="text-lg font-semibold text-foreground mb-4">열 매핑 설정</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-muted/30 rounded-lg p-3 border border-border">
                                <p className="text-xs text-muted-foreground mb-1">원본 상품명</p>
                                <p className="text-foreground font-medium">{metaData.column_mapping.original_product_name}열</p>
                            </div>
                            <div className="bg-muted/30 rounded-lg p-3 border border-border">
                                <p className="text-xs text-muted-foreground mb-1">가공된 상품명</p>
                                <p className="text-foreground font-medium">{metaData.column_mapping.refined_product_name}열</p>
                            </div>
                            <div className="bg-muted/30 rounded-lg p-3 border border-border">
                                <p className="text-xs text-muted-foreground mb-1">키워드</p>
                                <p className="text-foreground font-medium">{metaData.column_mapping.keyword}열</p>
                            </div>
                            <div className="bg-muted/30 rounded-lg p-3 border border-border">
                                <p className="text-xs text-muted-foreground mb-1">카테고리</p>
                                <p className="text-foreground font-medium">{metaData.column_mapping.category}열</p>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Error Message */}
                {job.status === 'failed' && job.error_message && (
                    <Card className="border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/5">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
                            <div>
                                <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">오류 발생</h3>
                                <p className="text-red-500 dark:text-red-300 text-sm">{job.error_message}</p>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Cancelled Message */}
                {job.status === 'cancelled' && (
                    <Card className="border-border bg-muted/30">
                        <div className="flex items-center gap-3">
                            <Ban className="w-6 h-6 text-muted-foreground" />
                            <div>
                                <h3 className="text-lg font-semibold text-muted-foreground">작업 취소됨</h3>
                                <p className="text-muted-foreground/80 text-sm mt-1">
                                    {job.error_message || '사용자에 의해 작업이 취소되었습니다'}
                                </p>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Success Message with Download */}
                {job.status === 'completed' && (
                    <Card className="border-green-200 dark:border-green-500/30 bg-green-50 dark:bg-green-500/5">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                                <div>
                                    <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">처리 완료!</h3>
                                    <p className="text-green-600/80 dark:text-green-300 text-sm mt-1">결과 파일을 다운로드할 수 있습니다</p>
                                </div>
                            </div>
                            <Button
                                onClick={handleDownload}
                                className="bg-green-600 hover:bg-green-700 text-white"
                                size="lg"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                결과 다운로드
                            </Button>
                        </div>
                    </Card>
                )}

                {/* Cancel Confirmation Modal */}
                {showCancelConfirm && (
                    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-card border border-border rounded-xl p-6 max-w-md w-full mx-4 shadow-xl"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-3 rounded-full bg-red-100 dark:bg-red-500/10">
                                    <Ban className="w-6 h-6 text-destructive" />
                                </div>
                                <h3 className="text-xl font-semibold text-foreground">작업 취소</h3>
                            </div>
                            <p className="text-muted-foreground mb-6">
                                정말로 이 작업을 취소하시겠습니까? 진행 중인 모든 작업이 중단되며 복구할 수 없습니다.
                            </p>
                            <div className="flex gap-3">
                                <Button
                                    variant="ghost"
                                    onClick={() => setShowCancelConfirm(false)}
                                    className="flex-1"
                                    disabled={cancelMutation.isPending}
                                >
                                    아니오
                                </Button>
                                <Button
                                    onClick={() => cancelMutation.mutate()}
                                    className="flex-1 bg-red-600 hover:bg-red-700"
                                    disabled={cancelMutation.isPending}
                                >
                                    {cancelMutation.isPending ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            취소 중...
                                        </>
                                    ) : (
                                        <>예, 취소합니다</>
                                    )}
                                </Button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </motion.div>
        </Layout>
    );
};

export default JobDetail;
