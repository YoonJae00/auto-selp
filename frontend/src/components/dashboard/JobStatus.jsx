import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Card } from '../ui/Card';
import api from '../../lib/api';

const fetchJobStatus = async (jobId) => {
    const { data } = await api.get(`/api/jobs/${jobId}`);
    return data;
};

export const JobStatus = ({ jobId }) => {
    const { data, error, isError } = useQuery({
        queryKey: ['jobStatus', jobId],
        queryFn: () => fetchJobStatus(jobId),
        refetchInterval: (data) => (data?.status === 'completed' || data?.status === 'failed' ? false : 2000), // Poll every 2s
        enabled: !!jobId,
    });

    if (!jobId) return null;

    if (isError) return <div className="text-red-400">Error loading status: {error.message}</div>;
    if (!data) return null;

    const { status, progress, result_file } = data;

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

    const Icon = statusIcons[status] || Clock;

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
                        <span className="capitalize">{status}</span>
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
                    <span>{progress}%</span>
                </div>

                {status === 'completed' && (
                    <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-center">
                        <p className="text-green-300 mb-2">처리 완료!</p>
                        {/* TODO: Add Download Link if backend supports returning file URL */}
                        {/* <a href={result_file} className="text-sm underline hover:text-green-200">Download Result</a> */}
                    </div>
                )}

                {status === 'failed' && (
                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-center">
                        <p className="text-red-300">처리 실패.</p>
                    </div>
                )}
            </Card>
        </motion.div>
    );
};
