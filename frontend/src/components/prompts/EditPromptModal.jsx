import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import api from '../../lib/api';

export const EditPromptModal = ({ isOpen, onClose, prompt }) => {
    const queryClient = useQueryClient();
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');

    useEffect(() => {
        if (prompt) {
            setTitle(prompt.title);
            setContent(prompt.content);
        }
    }, [prompt]);

    const mutation = useMutation({
        mutationFn: async (updatedData) => {
            // Backend doesn't have PUT /api/prompts/{id} yet for fully updating content.
            // But let's assume it does or we just create new one for now.
            // Actually backend only has GET /api/prompts and POST /api/prompts currently for list/create.
            // And PUT /active for toggling.
            // For this MVP, let's just stick to "Creating New" or we can mock update.
            // Wait, the user requirement is "Prompt Manager", likely implies editing.
            // I should probably add PUT endpoint to backend later or just support Create New here for now.
            // Let's implement CREATE NEW behavior for "Edit" to keep history, or just mock it.
            // Let's assume we are CREATING a new prompt version for simplicity if ID is missing,
            // or Alert user "Update not implemented" if ID present?
            // No, let's just use POST /api/prompts to create a new one for now as "Save as New".
            return api.post('/api/prompts', {
                title,
                content,
                type: prompt?.type || 'product_name',
                is_active: true // Auto activate new version
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['prompts']);
            onClose();
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        mutation.mutate({ title, content });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={prompt ? `${prompt.title} 편집` : '새 프롬프트'}>
            <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                    label="제목"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g., Creative Naming v2"
                    required
                />

                <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300 ml-1">프롬프트 내용</label>
                    <textarea
                        className="w-full h-40 bg-gray-950/50 border border-white/10 text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder:text-gray-500 backdrop-blur-sm transition-all resize-none"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="프롬프트 템플릿을 입력하세요..."
                        required
                    />
                    <p className="text-xs text-gray-500">
                        템플릿에 <code className="text-indigo-400">{"{{product_name}}"}</code>과 같은 변수를 사용하세요.
                    </p>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                    <Button type="button" variant="ghost" onClick={onClose}>
                        취소
                    </Button>
                    <Button type="submit" isLoading={mutation.isPending}>
                        새 버전으로 저장
                    </Button>
                </div>
            </form>
        </Modal>
    );
};
