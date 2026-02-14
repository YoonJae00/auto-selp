import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { Layout } from '../components/layout/Layout';
import { PromptCard } from '../components/prompts/PromptCard';
import { EditPromptModal } from '../components/prompts/EditPromptModal';
import { Button } from '../components/ui/Button';
import api from '../lib/api';

const fetchPrompts = async () => {
    const { data } = await api.get('/api/prompts');
    return data;
};

const Prompts = () => {
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedPrompt, setSelectedPrompt] = useState(null);

    const { data: prompts, isLoading } = useQuery({
        queryKey: ['prompts'],
        queryFn: fetchPrompts,
    });

    const activateMutation = useMutation({
        mutationFn: async (prompt) => {
            // Toggle active status (backend currently only supports set active)
            // We need to implement logic: if active, do nothing? or toggle?
            // Backend: PUT /api/prompts/{id}/active -> sets it to active and others of same type to inactive.
            if (prompt.is_active) return;
            return api.put(`/api/prompts/${prompt.id}/active`);
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
            type: 'product_name'
        });
        setIsModalOpen(true);
    };

    const handleToggleActive = (prompt) => {
        activateMutation.mutate(prompt);
    };

    return (
        <Layout>
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">프롬프트 관리자</h1>
                    <p className="text-gray-400 mt-2">AI가 제품을 처리하는 방식을 사용자 정의하세요.</p>
                </div>
                <Button onClick={handleCreate}>
                    <Plus className="w-4 h-4 mr-2" />
                    새 프롬프트
                </Button>
            </div>

            {isLoading ? (
                <div className="text-white">프롬프트 로딩 중...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {prompts?.map((prompt) => (
                        <PromptCard
                            key={prompt.id}
                            prompt={prompt}
                            onEdit={handleEdit}
                            onToggleActive={handleToggleActive}
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
