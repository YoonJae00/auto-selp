import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Plus, FileText, Search } from 'lucide-react';
import { Layout } from '../components/layout/Layout';
import { PromptCard } from '../components/prompts/PromptCard';
import { EditPromptModal } from '../components/prompts/EditPromptModal';
import { Button } from '../components/ui/Button';
import api from '../lib/api';

const fetchPrompts = async () => {
    const { data } = await api.get('/api/prompts/');
    return data;
};

const FILTER_TABS = [
    { key: 'all', label: '전체', icon: null },
    { key: 'product_name', label: '상품명 가공', icon: FileText },
    { key: 'keyword', label: '키워드 발굴', icon: Search },
];

const Prompts = () => {
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedPrompt, setSelectedPrompt] = useState(null);
    const [activeFilter, setActiveFilter] = useState('all');

    const { data: prompts, isLoading } = useQuery({
        queryKey: ['prompts'],
        queryFn: fetchPrompts,
    });

    const activateMutation = useMutation({
        mutationFn: async (prompt) => {
            if (prompt.is_active) return;
            return api.put(`/api/prompts/${prompt.id}/active`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['prompts']);
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (promptId) => {
            return api.delete(`/api/prompts/${promptId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['prompts']);
        }
    });

    const handleEdit = (prompt) => {
        setSelectedPrompt(prompt);
        setIsModalOpen(true);
    };

    const handleCreate = () => {
        setSelectedPrompt({  // Default template
            title: '',
            content: '',
            type: activeFilter !== 'all' ? activeFilter : 'product_name',
        });
        setIsModalOpen(true);
    };

    const handleToggleActive = (prompt) => {
        activateMutation.mutate(prompt);
    };

    const handleDelete = (prompt) => {
        if (window.confirm(`'${prompt.title}' 프롬프트를 삭제하시겠습니까?`)) {
            deleteMutation.mutate(prompt.id);
        }
    };

    // 필터링된 프롬프트 목록
    const filteredPrompts = prompts?.filter(p =>
        activeFilter === 'all' ? true : p.type === activeFilter
    );

    return (
        <Layout>
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-white">프롬프트 관리자</h1>
                    <p className="text-gray-400 mt-2">AI가 제품을 처리하는 방식을 사용자 정의하세요.</p>
                </div>
                <Button onClick={handleCreate}>
                    <Plus className="w-4 h-4 mr-2" />
                    새 프롬프트
                </Button>
            </div>

            {/* 필터 탭 */}
            <div className="flex gap-2 mb-6">
                {FILTER_TABS.map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveFilter(tab.key)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all border ${activeFilter === tab.key
                                ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300'
                                : 'bg-gray-800/50 border-white/5 text-gray-400 hover:bg-gray-800 hover:text-gray-300'
                            }`}
                    >
                        {tab.icon && <tab.icon className="w-3.5 h-3.5" />}
                        {tab.label}
                        {/* 타입별 개수 뱃지 */}
                        {prompts && (
                            <span className={`ml-1 px-1.5 py-0.5 rounded-md text-[10px] ${activeFilter === tab.key
                                    ? 'bg-indigo-500/30 text-indigo-200'
                                    : 'bg-gray-700 text-gray-500'
                                }`}>
                                {tab.key === 'all'
                                    ? prompts.length
                                    : prompts.filter(p => p.type === tab.key).length
                                }
                            </span>
                        )}
                    </button>
                ))}
            </div>

            {isLoading ? (
                <div className="text-white">프롬프트 로딩 중...</div>
            ) : filteredPrompts?.length === 0 ? (
                <div className="text-center py-16">
                    <div className="text-gray-500 text-lg mb-2">
                        {activeFilter === 'all'
                            ? '프롬프트가 없습니다.'
                            : `'${FILTER_TABS.find(t => t.key === activeFilter)?.label}' 타입의 프롬프트가 없습니다.`
                        }
                    </div>
                    <p className="text-gray-600 text-sm mb-6">
                        새 프롬프트를 만들어 AI의 동작을 커스터마이징하세요.
                    </p>
                    <Button variant="secondary" onClick={handleCreate}>
                        <Plus className="w-4 h-4 mr-2" />
                        프롬프트 만들기
                    </Button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredPrompts?.map((prompt) => (
                        <PromptCard
                            key={prompt.id}
                            prompt={prompt}
                            onEdit={handleEdit}
                            onToggleActive={handleToggleActive}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}

            <EditPromptModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                prompt={selectedPrompt}
            />
        </Layout>
    );
};

export default Prompts;
