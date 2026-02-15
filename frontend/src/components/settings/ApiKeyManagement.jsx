import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PasswordInput } from '../ui/PasswordInput';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Check, AlertCircle, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import api from '../../lib/api';

export const ApiKeyManagement = ({ apiKeys, onChange, onSave, isSaving }) => {
    const [localKeys, setLocalKeys] = useState(apiKeys || {});
    const [hasChanges, setHasChanges] = useState(false);
    const [testingApi, setTestingApi] = useState(null);
    const [testResults, setTestResults] = useState({});

    useEffect(() => {
        setLocalKeys(apiKeys || {});
    }, [apiKeys]);

    const handleChange = (field, value) => {
        const updated = { ...localKeys, [field]: value };
        setLocalKeys(updated);
        setHasChanges(true);
        if (onChange) onChange(updated);

        // 변경 시 테스트 결과 초기화
        if (testResults[field]) {
            setTestResults(prev => {
                const newResults = { ...prev };
                delete newResults[field];
                return newResults;
            });
        }
    };

    const handleSave = () => {
        if (onSave) {
            onSave(localKeys);
            setHasChanges(false);
        }
    };

    const testApiConnection = async (apiType, credentials) => {
        setTestingApi(apiType);
        try {
            const response = await api.post(`/api/settings/test-api/${apiType}`, credentials);
            setTestResults(prev => ({
                ...prev,
                [apiType]: response.data
            }));
        } catch (error) {
            setTestResults(prev => ({
                ...prev,
                [apiType]: {
                    success: false,
                    message: error.response?.data?.detail || '연결 테스트 실패'
                }
            }));
        } finally {
            setTestingApi(null);
        }
    };

    const apiSections = [
        {
            title: 'Gemini API',
            description: 'Google Gemini API를 사용한 AI 상품명 가공 및 키워드 발굴',
            apiType: 'gemini',
            fields: [
                {
                    key: 'gemini_api_key',
                    label: 'API 키',
                    placeholder: 'AIzaSy...',
                    type: 'password'
                }
            ]
        },
        {
            title: 'OpenAI API',
            description: 'OpenAI ChatGPT API를 사용한 AI 상품명 가공 및 키워드 발굴',
            apiType: 'openai',
            fields: [
                {
                    key: 'openai_api_key',
                    label: 'API 키',
                    placeholder: 'sk-proj-...',
                    type: 'password'
                }
            ]
        },
        {
            title: 'Naver 광고 API',
            description: '네이버 광고 관리 시스템 API',
            apiType: 'naver_ad',
            fields: [
                {
                    key: 'naver_api_key',
                    label: 'API 키',
                    placeholder: '0100000000...',
                    type: 'password'
                },
                {
                    key: 'naver_secret_key',
                    label: 'Secret 키',
                    placeholder: 'AQAAAACs...',
                    type: 'password'
                },
                {
                    key: 'naver_customer_id',
                    label: 'Customer ID',
                    placeholder: '2949678',
                    type: 'text'
                }
            ]
        },
        {
            title: 'Naver 쇼핑 검색 API',
            description: '네이버 쇼핑 검색 API',
            apiType: 'naver_search',
            fields: [
                {
                    key: 'naver_client_id',
                    label: 'Client ID',
                    placeholder: 'E0a_unupf...',
                    type: 'password'
                },
                {
                    key: 'naver_client_secret',
                    label: 'Client Secret',
                    placeholder: 'IXrAF6u8XL',
                    type: 'password'
                }
            ]
        },
        {
            title: 'Nano Banana API',
            description: 'Nano Banana 서비스 API (선택)',
            apiType: 'nano_banana',
            fields: [
                {
                    key: 'nano_banana_api_key',
                    label: 'API 키',
                    placeholder: 'API 키를 입력하세요',
                    type: 'password'
                }
            ]
        }
    ];

    return (
        <div className="space-y-6">
            <div className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                        <h3 className="text-sm font-semibold text-amber-300 mb-1">보안 안내</h3>
                        <p className="text-sm text-gray-400">
                            API 키는 암호화되어 안전하게 저장됩니다. 입력한 키는 마스킹(••••••••)으로 표시됩니다.
                        </p>
                    </div>
                </div>
            </div>

            {apiSections.map((section) => (
                <div key={section.apiType} className="bg-gray-900/30 border border-white/5 rounded-xl p-6 space-y-4">
                    <div className="flex items-start justify-between">
                        <div>
                            <h3 className="text-lg font-semibold text-white">{section.title}</h3>
                            <p className="text-sm text-gray-400 mt-1">{section.description}</p>
                        </div>

                        {testResults[section.apiType] && (
                            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm ${testResults[section.apiType].success
                                ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                                : 'bg-red-500/10 text-red-400 border border-red-500/20'
                                }`}>
                                {testResults[section.apiType].success ? (
                                    <>
                                        <CheckCircle2 className="w-4 h-4" />
                                        연결 성공
                                    </>
                                ) : (
                                    <>
                                        <XCircle className="w-4 h-4" />
                                        연결 실패
                                    </>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="space-y-3">
                        {section.fields.map((field) => (
                            <div key={field.key} className="space-y-2">
                                <label className="block text-sm font-medium text-gray-300">
                                    {field.label}
                                </label>
                                {field.type === 'password' ? (
                                    <PasswordInput
                                        value={localKeys[field.key] || ''}
                                        onChange={(e) => handleChange(field.key, e.target.value)}
                                        placeholder={field.placeholder}
                                    />
                                ) : (
                                    <Input
                                        value={localKeys[field.key] || ''}
                                        onChange={(e) => handleChange(field.key, e.target.value)}
                                        placeholder={field.placeholder}
                                    />
                                )}
                            </div>
                        ))}
                    </div>

                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                            const credentials = {};
                            section.fields.forEach(field => {
                                if (localKeys[field.key]) {
                                    credentials[field.key] = localKeys[field.key];
                                }
                            });
                            testApiConnection(section.apiType, credentials);
                        }}
                        disabled={testingApi === section.apiType || section.fields.every(f => !localKeys[f.key])}
                        isLoading={testingApi === section.apiType}
                    >
                        {testingApi === section.apiType ? '테스트 중...' : '연결 테스트'}
                    </Button>
                </div>
            ))}

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
