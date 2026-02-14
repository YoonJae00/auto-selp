import { motion } from 'framer-motion';
import { Edit2, Check, X } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

export const PromptCard = ({ prompt, onEdit, onToggleActive }) => {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
        >
            <Card className="h-full flex flex-col hover:border-indigo-500/30 transition-colors">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <span className="inline-block px-2 py-1 rounded-md text-xs font-medium bg-gray-800 text-gray-400 mb-2 capitalize">
                            {prompt.type.replace('_', ' ')}
                        </span>
                        <h3 className="text-xl font-bold text-white">{prompt.title}</h3>
                    </div>
                    <button
                        onClick={() => onToggleActive(prompt)}
                        className={`p-2 rounded-full transition-colors ${prompt.is_active
                            ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                            : 'bg-gray-800 text-gray-500 hover:bg-gray-700'
                            }`}
                        title={prompt.is_active ? "활성" : "비활성"}
                    >
                        {prompt.is_active ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                    </button>
                </div>

                <div className="flex-1 bg-black/20 rounded-xl p-3 mb-4 overflow-hidden relative group">
                    <p className="text-gray-400 text-sm line-clamp-4 font-mono">
                        {prompt.content}
                    </p>
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900/90 to-transparent opacity-50 group-hover:opacity-30 transition-opacity" />
                </div>

                <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => onEdit(prompt)}
                    className="w-full"
                >
                    <Edit2 className="w-3 h-3 mr-2" />
                    프롬프트 편집
                </Button>
            </Card>
        </motion.div>
    );
};
