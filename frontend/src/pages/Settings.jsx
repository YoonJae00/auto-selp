import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Layout } from '../components/layout/Layout';
import { ExcelColumnMapping } from '../components/settings/ExcelColumnMapping';
import { ApiKeyManagement } from '../components/settings/ApiKeyManagement';
import { ThemeSettings } from '../components/settings/ThemeSettings';
import { PromptManagement } from '../components/settings/PromptManagement';
import { LLMProviderSettings } from '../components/settings/LLMProviderSettings';
import { LoadingSkeleton } from '../components/ui/Loading';
import { FileSpreadsheet, Key, Wand2, Palette, Settings as SettingsIcon } from 'lucide-react';
import api from '../lib/api';
import { useSearchParams } from 'react-router-dom';

const fetchSettings = async () => {
    const { data } = await api.get('/api/settings/');
    return data;
};

const TABS = [
    { key: 'excel', label: '엑셀 설정', icon: FileSpreadsheet, description: '엑셀 컬럼명 매핑 설정' },
    { key: 'api', label: 'API 키', icon: Key, description: 'API 키 관리 및 연결 테스트' },
    { key: 'llm', label: 'AI 모델', icon: SettingsIcon, description: 'LLM 제공자 선택' },
    { key: 'prompts', label: '프롬프트', icon: Wand2, description: 'AI 프롬프트 관리' },
    { key: 'theme', label: '테마', icon: Palette, description: '화이트/다크 모드 설정' },
];

const Settings = () => {
    const queryClient = useQueryClient();
    const [searchParams, setSearchParams] = useSearchParams();
    const tabFromUrl = searchParams.get('tab') || 'excel';
    const [activeTab, setActiveTab] = useState(tabFromUrl);

    // Sync activeTab with URL query parameter
    useEffect(() => {
        const tab = searchParams.get('tab') || 'excel';
        setActiveTab(tab);
    }, [searchParams]);

    const { data: settings, isLoading } = useQuery({
        queryKey: ['settings'],
        queryFn: fetchSettings,
    });

    const updateSettingsMutation = useMutation({
        mutationFn: async (data) => {
            return api.put('/api/settings', data);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['settings']);
        }
    });

    const handleSaveExcelMapping = (mapping) => {
        updateSettingsMutation.mutate({
            excel_column_mapping: mapping
        });
    };

    const handleSaveApiKeys = (apiKeys) => {
        updateSettingsMutation.mutate({
            api_keys: apiKeys
        });
    };

    const handleSaveLLMPreferences = (preferences) => {
        updateSettingsMutation.mutate({
            preferences: preferences
        });
    };

    return (
        <Layout>
            <div className="max-w-5xl mx-auto">
                {/* 헤더 */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-foreground mb-2">설정</h1>
                    <p className="text-muted-foreground">
                        엑셀 컬럼 매핑, API 키, 프롬프트 등을 관리합니다.
                    </p>
                </div>

                {isLoading ? (
                    <div className="space-y-6">
                        <div className="flex gap-2 mb-6">
                            {TABS.map((tab) => (
                                <div key={tab.key} className="h-16 bg-muted rounded animate-pulse w-32" />
                            ))}
                        </div>
                        <LoadingSkeleton count={2} />
                    </div>
                ) : (
                    <>
                        {/* 탭 네비게이션 */}
                        <div className="flex gap-2 mb-6 border-b border-border overflow-x-auto">
                            {TABS.map((tab) => (
                                <button
                                    key={tab.key}
                                    onClick={() => setActiveTab(tab.key)}
                                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all border-b-2 whitespace-nowrap ${activeTab === tab.key
                                        ? 'border-primary text-primary'
                                        : 'border-transparent text-muted-foreground hover:text-foreground'
                                        }`}
                                >
                                    <tab.icon className="w-4 h-4" />
                                    <div className="text-left">
                                        <div>{tab.label}</div>
                                        <div className="text-xs text-muted-foreground">{tab.description}</div>
                                    </div>
                                </button>
                            ))}
                        </div>

                        {/* 탭 컨텐츠 */}
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeTab}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.2 }}
                                className="bg-card border border-border rounded-2xl p-6 shadow-sm"
                            >
                                {activeTab === 'theme' && (
                                    <ThemeSettings />
                                )}

                                {activeTab === 'excel' && (
                                    <ExcelColumnMapping
                                        mapping={settings?.excel_column_mapping}
                                        onChange={() => { }}
                                        onSave={handleSaveExcelMapping}
                                        isSaving={updateSettingsMutation.isPending}
                                    />
                                )}

                                {activeTab === 'api' && (
                                    <ApiKeyManagement
                                        apiKeys={settings?.api_keys}
                                        onChange={() => { }}
                                        onSave={handleSaveApiKeys}
                                        isSaving={updateSettingsMutation.isPending}
                                    />
                                )}

                                {activeTab === 'llm' && (
                                    <LLMProviderSettings
                                        preferences={settings?.preferences}
                                        onChange={() => { }}
                                        onSave={handleSaveLLMPreferences}
                                        isSaving={updateSettingsMutation.isPending}
                                    />
                                )}

                                {activeTab === 'prompts' && (
                                    <PromptManagement />
                                )}
                            </motion.div>
                        </AnimatePresence>
                    </>
                )}
            </div>
        </Layout>
    );
};

export default Settings;
