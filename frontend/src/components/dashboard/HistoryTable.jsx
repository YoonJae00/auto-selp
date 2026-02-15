import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Download, File, Clock, CheckCircle, XCircle, Loader2, Eye, Ban } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../../lib/api';
import { cn } from '../../lib/utils';

const statusConfig = {
    pending: {
        label: '대기 중',
        color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        icon: Clock
    },
    processing: {
        label: '처리 중',
        color: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        icon: Loader2
    },
    completed: {
        label: '완료',
        color: 'bg-green-500/10 text-green-400 border-green-500/20',
        icon: CheckCircle
    },
    failed: {
        label: '실패',
        color: 'bg-red-500/10 text-red-400 border-red-500/20',
        icon: XCircle
    },
    cancelled: {
        label: '취소됨',
        color: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
        icon: Ban
    }
};

export const HistoryTable = ({ onJobClick }) => {
    const navigate = useNavigate();

    const { data: jobs, isLoading } = useQuery({
        queryKey: ['jobHistory'],
        queryFn: async () => {
            const { data } = await api.get('/api/jobs/');
            return data;
        },
        refetchInterval: 5000, // Auto-refresh every 5 seconds
    });

    const handleRowClick = (jobId) => {
        navigate(`/job/${jobId}`);
    };

    const handleDownload = async (e, jobId) => {
        e.stopPropagation(); // Prevent row click
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
            minute: '2-digit'
        });
    };

    if (isLoading) {
        return (
            <div className="mt-8">
                <h3 className="text-xl font-semibold text-white mb-4">최근 활동 내역</h3>
                <div className="flex items-center justify-center py-12 text-gray-400">
                    <Loader2 className="w-6 h-6 animate-spin mr-2" />
                    로딩 중...
                </div>
            </div>
        );
    }

    return (
        <div className="mt-8">
            <h3 className="text-xl font-semibold text-white mb-4">최근 활동 내역</h3>

            {!jobs || jobs.length === 0 ? (
                <div className="text-center py-12 text-gray-400 bg-gray-950/40 rounded-xl border border-white/10">
                    아직 처리한 작업이 없습니다.
                </div>
            ) : (
                <div className="overflow-hidden rounded-xl border border-white/10 bg-gray-950/40 backdrop-blur-sm">
                    <table className="w-full text-left text-sm text-gray-400">
                        <thead className="bg-white/5 uppercase text-xs font-semibold text-gray-300">
                            <tr>
                                <th className="px-6 py-4">파일명</th>
                                <th className="px-6 py-4">상태</th>
                                <th className="px-6 py-4">진행률</th>
                                <th className="px-6 py-4">생성 시간</th>
                                <th className="px-6 py-4 text-right">작업</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {jobs.map((job, index) => {
                                const status = statusConfig[job.status] || statusConfig.pending;
                                const Icon = status.icon;

                                return (
                                    <motion.tr
                                        key={job.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.05 }}
                                        onClick={() => handleRowClick(job.id)}
                                        className="hover:bg-white/5 transition-colors cursor-pointer"
                                    >
                                        <td className="px-6 py-4 font-medium text-white">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                                                    <File className="w-4 h-4" />
                                                </div>
                                                <span className="max-w-[300px] truncate">
                                                    {job.meta_data?.original_filename || '파일명 없음'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={cn(
                                                "inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border",
                                                status.color
                                            )}>
                                                <Icon className={cn(
                                                    "w-3 h-3",
                                                    job.status === 'processing' && 'animate-spin'
                                                )} />
                                                {status.label}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <div className="flex-1 bg-gray-700/50 rounded-full h-2 max-w-[100px]">
                                                    <div
                                                        className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                                                        style={{ width: `${job.progress || 0}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs">{job.progress || 0}%</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">{formatDate(job.created_at)}</td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                {job.status === 'completed' && (
                                                    <button
                                                        onClick={(e) => handleDownload(e, job.id)}
                                                        className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
                                                        title="다운로드"
                                                    >
                                                        <Download className="w-4 h-4" />
                                                    </button>
                                                )}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleRowClick(job.id);
                                                    }}
                                                    className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
                                                    title="상세 보기"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
