import { useState, useEffect, useRef, useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { AlertTriangle, RotateCcw, Plus } from 'lucide-react';
import api from '../../lib/api';

// 타입별 필수 변수 정의 (백엔드와 동기화)
const REQUIRED_VARIABLES = {
    product_name: ['{{product_name}}'],
    keyword: ['{{product_name}}', '{{keywords_str}}'],
};

const TYPE_LABELS = {
    product_name: '상품명 가공',
    keyword: '키워드 발굴',
};

export const EditPromptModal = ({ isOpen, onClose, prompt }) => {
    const queryClient = useQueryClient();
    const textareaRef = useRef(null);
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [type, setType] = useState('product_name');

    // 기본 프롬프트 데이터 가져오기
    const { data: defaults } = useQuery({
        queryKey: ['prompt-defaults'],
        queryFn: async () => {
            const { data } = await api.get('/api/prompts/defaults');
            return data;
        },
        staleTime: Infinity,
    });

    const isNew = !prompt?.id;
    const currentType = isNew ? type : prompt?.type;
    const requiredVars = REQUIRED_VARIABLES[currentType] || [];

    // 실시간 검증: 필수 변수 누락 체크
    const missingVariables = useMemo(() => {
        return requiredVars.filter(v => !content.includes(v));
    }, [content, requiredVars]);

    const hasValidationError = missingVariables.length > 0;

    useEffect(() => {
        if (prompt) {
            setTitle(prompt.title || '');
            setContent(prompt.content || '');
            setType(prompt.type || 'product_name');
        }
    }, [prompt]);

    // 저장 (생성/수정)
    const mutation = useMutation({
        mutationFn: async (updatedData) => {
            const payload = {
                ...updatedData,
                type: currentType,
            };

            if (prompt?.id) {
                return api.put(`/api/prompts/${prompt.id}`, payload);
            } else {
                return api.post('/api/prompts/', {
                    ...payload,
                    is_active: false,
                });
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['prompts']);
            onClose();
        },
    });

    // 기본값 초기화
    const resetMutation = useMutation({
        mutationFn: async () => {
            if (prompt?.id) {
                return api.put(`/api/prompts/${prompt.id}/reset`);
            }
        },
        onSuccess: (res) => {
            // 로컬 상태도 기본값으로 갱신
            const defaultPrompt = defaults?.find(d => d.type === currentType);
            if (defaultPrompt) {
                setTitle(defaultPrompt.title);
                setContent(defaultPrompt.content);
            }
            queryClient.invalidateQueries(['prompts']);
        },
    });

    // 변수 삽입 헬퍼
    const insertVariable = (variable) => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const newContent = content.substring(0, start) + variable + content.substring(end);
        setContent(newContent);

        // 커서 위치 조정
        requestAnimationFrame(() => {
            textarea.focus();
            textarea.selectionStart = textarea.selectionEnd = start + variable.length;
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (hasValidationError) return;
        mutation.mutate({ title, content });
    };

    const handleReset = () => {
        if (window.confirm('프롬프트를 기본 템플릿으로 초기화하시겠습니까?\n현재 내용이 덮어씌워집니다.')) {
            resetMutation.mutate();
        }
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={isNew ? '새 프롬프트' : `${prompt?.title || ''} 편집`}
            size="lg"
        >
            <form onSubmit={handleSubmit} className="space-y-5">
                {/* 타입 선택 (새 프롬프트 생성 시만) */}
                {isNew && (
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300 ml-1">프롬프트 타입</label>
                        <div className="flex gap-3">
                            {Object.entries(TYPE_LABELS).map(([key, label]) => (
                                <button
                                    key={key}
                                    type="button"
                                    onClick={() => setType(key)}
                                    className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-medium transition-all border ${type === key
                                        ? 'bg-indigo-600/30 border-indigo-500 text-indigo-300'
                                        : 'bg-gray-800/50 border-white/10 text-gray-400 hover:bg-gray-800 hover:text-gray-300'
                                        }`}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* 타입 표시 (편집 시) */}
                {!isNew && (
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">타입:</span>
                        <span className="inline-block px-2.5 py-1 rounded-lg text-xs font-medium bg-indigo-600/20 text-indigo-300 border border-indigo-500/30">
                            {TYPE_LABELS[prompt?.type] || prompt?.type}
                        </span>
                    </div>
                )}

                <Input
                    label="제목"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="예: 상품명 가공 v2"
                    required
                />

                {/* 프롬프트 내용 */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                        <label className="text-sm font-medium text-gray-300 ml-1">프롬프트 내용</label>
                        {/* 기본값 초기화 버튼 (기존 프롬프트 편집 시) */}
                        {!isNew && (
                            <button
                                type="button"
                                onClick={handleReset}
                                className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-amber-400 transition-colors"
                                title="기본 템플릿으로 초기화"
                            >
                                <RotateCcw className="w-3 h-3" />
                                기본값 초기화
                            </button>
                        )}
                    </div>

                    <textarea
                        ref={textareaRef}
                        className="w-full h-64 bg-gray-950/50 border border-white/10 text-white rounded-xl px-4 py-3 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder:text-gray-500 backdrop-blur-sm transition-all resize-y leading-relaxed"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="프롬프트 템플릿을 입력하세요..."
                        required
                    />

                    {/* 필수 변수 태그 + 삽입 버튼 */}
                    <div className="flex flex-wrap items-center gap-2 mt-2">
                        <span className="text-xs text-gray-500">필수 변수:</span>
                        {requiredVars.map((v) => {
                            const isPresent = content.includes(v);
                            return (
                                <button
                                    key={v}
                                    type="button"
                                    onClick={() => insertVariable(v)}
                                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono transition-all border ${isPresent
                                        ? 'bg-green-500/10 border-green-500/30 text-green-400'
                                        : 'bg-red-500/10 border-red-500/30 text-red-400 animate-pulse'
                                        }`}
                                    title={isPresent ? '포함됨 (클릭하면 커서 위치에 삽입)' : '누락됨! 클릭하여 삽입'}
                                >
                                    <Plus className="w-3 h-3" />
                                    {v}
                                </button>
                            );
                        })}
                    </div>

                    {/* 검증 경고 메시지 */}
                    {hasValidationError && content.length > 0 && (
                        <div className="flex items-start gap-2 mt-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                            <div className="text-xs text-red-300">
                                <p className="font-medium">필수 변수가 누락되었습니다:</p>
                                <p className="mt-1 font-mono">
                                    {missingVariables.join(', ')}
                                </p>
                                <p className="mt-1 text-red-400/70">
                                    위 변수 버튼을 클릭하면 커서 위치에 삽입됩니다.
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* 액션 버튼 */}
                <div className="flex justify-end gap-3 mt-6 pt-2 border-t border-white/5">
                    <Button type="button" variant="ghost" onClick={onClose}>
                        취소
                    </Button>
                    <Button
                        type="submit"
                        isLoading={mutation.isPending}
                        disabled={hasValidationError}
                        className={hasValidationError ? 'opacity-50 cursor-not-allowed' : ''}
                    >
                        {isNew ? '생성' : '저장'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};
