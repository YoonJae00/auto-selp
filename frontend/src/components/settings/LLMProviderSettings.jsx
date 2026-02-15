import { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Check, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export const LLMProviderSettings = ({ preferences, onChange, onSave, isSaving }) => {
    const [localPreferences, setLocalPreferences] = useState(preferences || {});
    const [hasChanges, setHasChanges] = useState(false);

    useEffect(() => {
        setLocalPreferences(preferences || {});
    }, [preferences]);

    const handleProviderChange = (provider) => {
        const updated = { ...localPreferences, llm_provider: provider };
        setLocalPreferences(updated);
        setHasChanges(true);
        if (onChange) onChange(updated);
    };

    const handleSave = () => {
        if (onSave) {
            onSave(localPreferences);
            setHasChanges(false);
        }
    };

    const currentProvider = localPreferences.llm_provider || 'gemini';

    const providers = [
        {
            id: 'gemini',
            name: 'Google Gemini',
            description: 'Google의 Gemini Flash 모델 사용',
            model: 'gemini-flash-latest',
        },
        {
            id: 'openai',
            name: 'OpenAI ChatGPT',
            description: 'OpenAI의 GPT-4o-mini 모델 사용',
            model: 'gpt-4o-mini',
        },
    ];

    return (
        <div className="space-y-6">
            <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                    <div>
                        <h3 className="text-sm font-semibold text-blue-300 mb-1">LLM 제공자 선택</h3>
                        <p className="text-sm text-gray-400">
                            상품명 가공 및 키워드 발굴에 사용할 AI 모델을 선택하세요.
                            선택한 제공자의 API 키가 설정되어 있어야 합니다.
                        </p>
                    </div>
                </div>
            </div>

            <div className="space-y-3">
                {providers.map((provider) => (
                    <div
                        key={provider.id}
                        onClick={() => handleProviderChange(provider.id)}
                        className={`
                            relative p-4 rounded-xl border-2 transition-all cursor-pointer
                            ${currentProvider === provider.id
                                ? 'border-primary bg-primary/5'
                                : 'border-white/10 bg-gray-900/30 hover:border-white/20'
                            }
                        `}
                    >
                        <div className="flex items-start gap-3">
                            <div className={`
                                w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 flex-shrink-0
                                ${currentProvider === provider.id
                                    ? 'border-primary bg-primary'
                                    : 'border-white/30'
                                }
                            `}>
                                {currentProvider === provider.id && (
                                    <div className="w-2.5 h-2.5 bg-white rounded-full" />
                                )}
                            </div>

                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <h3 className="text-base font-semibold text-white">
                                        {provider.name}
                                    </h3>
                                    {currentProvider === provider.id && (
                                        <span className="px-2 py-0.5 text-xs bg-primary/20 text-primary border border-primary/30 rounded-full">
                                            선택됨
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-gray-400 mt-1">
                                    {provider.description}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    모델: {provider.model}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
                {hasChanges && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-sm text-amber-400 flex items-center gap-2"
                    >
                        <AlertCircle className="w-4 h-4" />
                        저장되지 않은 변경사항이 있습니다
                    </motion.div>
                )}

                <Button
                    onClick={handleSave}
                    disabled={!hasChanges || isSaving}
                    isLoading={isSaving}
                >
                    {isSaving ? '저장 중...' : (
                        <>
                            <Check className="w-4 h-4 mr-2" />
                            저장
                        </>
                    )}
                </Button>
            </div>
        </div>
    );
};
