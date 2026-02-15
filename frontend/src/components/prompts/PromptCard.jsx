import { motion } from 'framer-motion';
import { Edit2, Check, X, Trash2 } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

const TYPE_LABELS = {
    product_name: '상품명 가공',
    keyword: '키워드 발굴',
};

// 프롬프트 내용에서 사용된 변수를 추출
const extractVariables = (content) => {
    const regex = /\{\{(\w+)\}\}/g;
    const vars = new Set();
    let match;
    while ((match = regex.exec(content)) !== null) {
        vars.add(`{{${match[1]}}}`);
    }
    return [...vars];
};

export const PromptCard = ({ prompt, onEdit, onToggleActive, onDelete }) => {
    const variables = extractVariables(prompt.content);

    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
        >
            <Card className="h-full flex flex-col hover:border-indigo-500/30 transition-colors">
                <div className="flex justify-between items-start mb-3">
                    <div>
                        <span className="inline-block px-2.5 py-1 rounded-lg text-xs font-medium bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 mb-2">
                            {TYPE_LABELS[prompt.type] || prompt.type}
                        </span>
                        <h3 className="text-xl font-bold text-white">{prompt.title}</h3>
                    </div>
                    <button
                        onClick={() => onToggleActive(prompt)}
                        className={`p-2 rounded-full transition-colors ${prompt.is_active
                            ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                            : 'bg-gray-800 text-gray-500 hover:bg-gray-700'
                            }`}
                        title={prompt.is_active ? "활성" : "비활성 (클릭하여 활성화)"}
                    >
                        {prompt.is_active ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                    </button>
                </div>

                {/* 변수 태그 */}
                {variables.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                        {variables.map((v) => (
                            <span
                                key={v}
                                className="inline-block px-2 py-0.5 rounded-md text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                            >
                                {v}
                            </span>
                        ))}
                    </div>
                )}

                <div className="flex-1 bg-black/20 rounded-xl p-3 mb-4 overflow-hidden relative group">
                    <p className="text-gray-400 text-sm line-clamp-4 font-mono whitespace-pre-wrap">
                        {prompt.content}
                    </p>
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900/90 to-transparent opacity-50 group-hover:opacity-30 transition-opacity" />
                </div>
                <div className="flex items-center">
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => onEdit(prompt)}
                        className="flex-1"
                    >
                        <Edit2 className="w-3 h-3 mr-2" />
                        편집
                    </Button>
                    <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onDelete(prompt)}
                        className="ml-2"
                        title="삭제"
                    >
                        <Trash2 className="w-3 h-3" />
                    </Button>
                </div>
            </Card>
        </motion.div>
    );
};
