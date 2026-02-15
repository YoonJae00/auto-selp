import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, XCircle, Clock, Download } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import api from '../../lib/api';

const fetchJobStatus = async (jobId) => {
    const { data } = await api.get(`/api/jobs/${jobId}`);
    return data;
};

export const JobStatus = ({ jobId }) => {
    const { data, error, isError } = useQuery({
        queryKey: ['jobStatus', jobId],
        queryFn: () => fetchJobStatus(jobId),
        refetchInterval: (data) => (data?.status === 'completed' || data?.status === 'failed' ? false : 5000), // Poll every 5s
        enabled: !!jobId,
    });

    if (!jobId) return null;

    if (isError) return <div className="text-red-400">Error loading status: {error.message}</div>;
    if (!data) return null;

    const { status, progress, error_message, meta_data } = data;
    const chunks = meta_data?.chunks || [];
    const parallelCount = meta_data?.parallel_count || 1;

    const statusColors = {
        pending: 'text-yellow-400 bg-yellow-400/10',
        processing: 'text-blue-400 bg-blue-400/10',
        completed: 'text-green-400 bg-green-400/10',
        failed: 'text-red-400 bg-red-400/10',
    };

    const statusIcons = {
        pending: Clock,
        processing: Loader2,
        completed: CheckCircle,
        failed: XCircle,
    };

    const statusLabels = {
        pending: '대기 중',
        processing: '처리 중',
        completed: '완료',
        failed: '실패',
    };

    const Icon = statusIcons[status] || Clock;

    const handleDownload = async () => {
        try {
            const response = await api.get(`/api/jobs/${jobId}/download/result`, {
                responseType: 'blob',
            });

            // Create download link
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

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
        >
            <Card className="border-indigo-500/30 bg-indigo-500/5">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">현재 작업 상태</h3>
                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${statusColors[status]}`}>
                        <Icon className={`w-4 h-4 ${status === 'processing' ? 'animate-spin' : ''}`} />
                        <span>{statusLabels[status]}</span>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-700/50 rounded-full h-2.5 mb-2 overflow-hidden">
                    <motion.div
                        className="bg-indigo-500 h-2.5 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress || 0}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>
                <div className="flex justify-between text-xs text-gray-400 mb-4">
                    <span>진행률</span>
                    <span>{progress || 0}%</span>
                </div>

                {/* Chunk Progress Grid */}
                {parallelCount > 1 && chunks.length > 0 && (
                    <div className="mb-4">
                        <p className="text-sm text-gray-300 mb-3 font-medium">병렬 처리 상태</p>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                            {chunks.map((chunk) => {
                                const chunkStatusColors = {
                                    pending: 'border-yellow-500/30 bg-yellow-500/5',
                                    processing: 'border-blue-500/30 bg-blue-500/5',
                                    completed: 'border-green-500/30 bg-green-500/5',
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
                                        className={`border rounded-lg p-3 ${chunkStatusColors[chunk.status] || chunkStatusColors.pending}`}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs font-medium text-gray-300">
                                                청크 #{chunk.id + 1}
                                            </span>
                                            <span className="text-sm">
                                                {chunkStatusIcons[chunk.status] || chunkStatusIcons.pending}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-700/50 rounded-full h-1.5 mb-2">
                                            <motion.div
                                                className="bg-indigo-400 h-1.5 rounded-full"
                                                initial={{ width: 0 }}
                                                animate={{ width: `${chunk.progress || 0}%` }}
                                                transition={{ duration: 0.3 }}
                                            />
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-xs text-gray-400">
                                                {chunk.rows_processed || 0}/{chunk.total_rows || 0}
                                            </span>
                                            <span className="text-xs text-gray-400 font-medium">
                                                {chunk.progress || 0}%
                                            </span>
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {status === 'completed' && (
                    <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                        <p className="text-green-300 mb-3 text-center font-medium">✅ 처리 완료!</p>
                        <Button
                            onClick={handleDownload}
                            className="w-full bg-green-600 hover:bg-green-700"
                            size="lg"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            결과 파일 다운로드
                        </Button>
                    </div>
                )}

                {status === 'failed' && (
                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                        <p className="text-red-300 font-medium mb-2">❌ 처리 실패</p>
                        {error_message && (
                            <p className="text-sm text-red-400/80 mt-2">{error_message}</p>
                        )}
                    </div>
                )}
            </Card>
        </motion.div>
    );
};
