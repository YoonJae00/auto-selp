import { motion } from 'framer-motion';
import { Download, File, MoreHorizontal } from 'lucide-react';

const mockHistory = [
    { id: 1, name: 'products_march_01.xlsx', status: 'completed', date: '2025-03-01 10:00' },
    { id: 2, name: 'keywords_fashion.xlsx', status: 'completed', date: '2025-02-28 15:30' },
    { id: 3, name: 'raw_data_v2.xlsx', status: 'failed', date: '2025-02-28 09:15' },
];

export const HistoryTable = () => {
    return (
        <div className="mt-8">
            <h3 className="text-xl font-semibold text-white mb-4">최근 활동 내역</h3>

            <div className="overflow-hidden rounded-xl border border-white/10 bg-gray-950/40 backdrop-blur-sm">
                <table className="w-full text-left text-sm text-gray-400">
                    <thead className="bg-white/5 uppercase text-xs font-semibold text-gray-300">
                        <tr>
                            <th className="px-6 py-4">파일명</th>
                            <th className="px-6 py-4">상태</th>
                            <th className="px-6 py-4">날짜</th>
                            <th className="px-6 py-4 text-right">작업</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {mockHistory.map((item, index) => (
                            <motion.tr
                                key={item.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className="hover:bg-white/5 transition-colors"
                            >
                                <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                                        <File className="w-4 h-4" />
                                    </div>
                                    {item.name}
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                    ${item.status === 'completed' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}
                  `}>
                                        {item.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4">{item.date}</td>
                                <td className="px-6 py-4 text-right">
                                    <button className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg">
                                        <Download className="w-4 h-4" />
                                    </button>
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
