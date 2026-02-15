import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ChevronDown, FileSpreadsheet, ArrowLeft, Save, CheckCircle, Settings } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';
import api from '../../lib/api';

const fetchSettings = async () => {
    const { data } = await api.get('/api/settings/');
    return data;
};

const saveColumnMapping = async (mapping) => {
    const { data } = await api.put('/api/settings', {
        excel_column_mapping: mapping
    });
    return data;
};

export const ColumnMappingStep = ({ previewData, onSubmit, onBack, fileName }) => {
    const queryClient = useQueryClient();
    const [mapping, setMapping] = useState({
        original_product_name: '',
        refined_product_name: '',
        keyword: '',
        category: ''
    });
    const [error, setError] = useState('');
    const [showSaveSuccess, setShowSaveSuccess] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [parallelCount, setParallelCount] = useState(1);

    // 설정 불러오기
    const { data: settings, isLoading: isLoadingSettings } = useQuery({
        queryKey: ['settings'],
        queryFn: fetchSettings,
    });

    // 설정 저장 mutation
    const saveMutation = useMutation({
        mutationFn: saveColumnMapping,
        onSuccess: () => {
            queryClient.invalidateQueries(['settings']);
            setShowSaveSuccess(true);
            setTimeout(() => setShowSaveSuccess(false), 3000);
        }
    });

    // 설정 자동 로드
    useEffect(() => {
        if (settings?.excel_column_mapping) {
            setMapping(settings.excel_column_mapping);
        }
    }, [settings]);

    const handleSubmit = () => {
        // Validate: all fields are required
        if (!mapping.original_product_name) {
            setError('원본 상품명 열은 필수입니다.');
            return;
        }
        if (!mapping.refined_product_name) {
            setError('가공된 상품명 열은 필수입니다.');
            return;
        }
        if (!mapping.keyword) {
            setError('키워드 열은 필수입니다.');
            return;
        }
        if (!mapping.category) {
            setError('카테고리 열은 필수입니다.');
            return;
        }
        setError('');
        onSubmit(mapping, parallelCount);
    };

    const handleColumnSelect = (field, value) => {
        setMapping(prev => ({
            ...prev,
            [field]: value
        }));
        setError('');
    };

    const handleSaveSettings = () => {
        // 유효성 검사
        if (!mapping.original_product_name || !mapping.refined_product_name ||
            !mapping.keyword || !mapping.category) {
            setError('모든 열을 선택해야 설정을 저장할 수 있습니다.');
            return;
        }
        saveMutation.mutate(mapping);
    };

    const hasValidMapping = mapping.original_product_name &&
        mapping.refined_product_name &&
        mapping.keyword &&
        mapping.category;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6 min-w-0 overflow-hidden"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                        <FileSpreadsheet className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-foreground">열 매핑 설정</h3>
                        <p className="text-sm text-muted-foreground">{fileName}</p>
                    </div>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onBack}
                    className="text-muted-foreground hover:text-foreground"
                >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    돌아가기
                </Button>
            </div>

            {/* 설정 로드 상태 표시 */}
            {!isLoadingSettings && settings?.excel_column_mapping && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 flex items-center gap-2"
                >
                    <CheckCircle className="w-5 h-5 text-blue-400" />
                    <span className="text-sm text-blue-300">저장된 설정을 불러왔습니다</span>
                </motion.div>
            )}

            {/* 저장 성공 메시지 */}
            {showSaveSuccess && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 flex items-center gap-2"
                >
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-sm text-green-300">설정이 저장되었습니다!</span>
                </motion.div>
            )}

            {/* Excel Preview */}
            {/* Excel Preview */}
            <div className="bg-card rounded-xl p-4 overflow-x-auto border border-border shadow-sm max-w-[calc(100vw-340px)]">
                <p className="text-sm text-muted-foreground mb-3">엑셀 미리보기 (처음 5행)</p>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                        <thead>
                            <tr className="bg-muted/50">
                                <th className="border border-border px-3 py-2 text-left text-muted-foreground font-medium min-w-[60px]">#</th>
                                {previewData.columns.map((col, idx) => (
                                    <th
                                        key={idx}
                                        className="border border-border px-3 py-2 text-left text-primary font-medium min-w-[120px] max-w-[200px]"
                                    >
                                        {col}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {/* Headers Row */}
                            <tr className="bg-muted/20">
                                <td className="border border-border px-3 py-2 text-muted-foreground">1</td>
                                {previewData.headers.map((header, idx) => (
                                    <td
                                        key={idx}
                                        className="border border-border px-3 py-2 text-foreground font-medium max-w-[200px] truncate"
                                        title={header || '(비어있음)'}
                                    >
                                        {header || '(비어있음)'}
                                    </td>
                                ))}
                            </tr>
                            {/* Preview Rows */}
                            {previewData.preview_rows.map((row, rowIdx) => (
                                <tr key={rowIdx} className="hover:bg-muted/30">
                                    <td className="border border-border px-3 py-2 text-muted-foreground">{rowIdx + 2}</td>
                                    {row.map((cell, cellIdx) => (
                                        <td
                                            key={cellIdx}
                                            className="border border-border px-3 py-2 text-foreground/80 max-w-[200px] truncate"
                                            title={cell || '-'}
                                        >
                                            {cell || '-'}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Column Mapping Selectors */}
            <div className="space-y-4">
                <p className="text-foreground font-medium">열 선택 <span className="text-red-500 text-sm">(모두 필수)</span></p>

                {/* Original Product Name Column */}
                <div className="bg-card rounded-lg p-4 border border-border shadow-sm">
                    <label className="block text-sm font-medium text-foreground mb-2">
                        원본 상품명 열 <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-muted-foreground/80 mb-2">도매상에서 받은 원본 상품명이 있는 열</p>
                    <div className="relative">
                        <select
                            value={mapping.original_product_name}
                            onChange={(e) => handleColumnSelect('original_product_name', e.target.value)}
                            className={cn(
                                "w-full bg-background border rounded-lg px-4 py-3 text-foreground appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-primary",
                                mapping.original_product_name ? "border-primary" : "border-input"
                            )}
                        >
                            <option value="" className="bg-background text-muted-foreground">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-background text-foreground">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    </div>
                </div>

                {/* Refined Product Name Column */}
                <div className="bg-card rounded-lg p-4 border border-border shadow-sm">
                    <label className="block text-sm font-medium text-foreground mb-2">
                        가공된 상품명 열 <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-muted-foreground/80 mb-2">AI로 가공된 상품명을 저장할 열 (기존 데이터가 있어도 덮어씁니다)</p>
                    <div className="relative">
                        <select
                            value={mapping.refined_product_name}
                            onChange={(e) => handleColumnSelect('refined_product_name', e.target.value)}
                            className={cn(
                                "w-full bg-background border rounded-lg px-4 py-3 text-foreground appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-primary",
                                mapping.refined_product_name ? "border-primary" : "border-input"
                            )}
                        >
                            <option value="" className="bg-background text-muted-foreground">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-background text-foreground">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    </div>
                </div>

                {/* Keyword Column */}
                <div className="bg-card rounded-lg p-4 border border-border shadow-sm">
                    <label className="block text-sm font-medium text-foreground mb-2">
                        키워드 열 <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-muted-foreground/80 mb-2">추천 키워드를 저장할 열</p>
                    <div className="relative">
                        <select
                            value={mapping.keyword}
                            onChange={(e) => handleColumnSelect('keyword', e.target.value)}
                            className={cn(
                                "w-full bg-background border rounded-lg px-4 py-3 text-foreground appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-primary",
                                mapping.keyword ? "border-primary" : "border-input"
                            )}
                        >
                            <option value="" className="bg-background text-muted-foreground">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-background text-foreground">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    </div>
                </div>

                {/* Category Column */}
                <div className="bg-card rounded-lg p-4 border border-border shadow-sm">
                    <label className="block text-sm font-medium text-foreground mb-2">
                        카테고리 열 <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-muted-foreground/80 mb-2">카테고리 코드를 저장할 열</p>
                    <div className="relative">
                        <select
                            value={mapping.category}
                            onChange={(e) => handleColumnSelect('category', e.target.value)}
                            className={cn(
                                "w-full bg-background border rounded-lg px-4 py-3 text-foreground appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-primary",
                                mapping.category ? "border-primary" : "border-input"
                            )}
                        >
                            <option value="" className="bg-background text-muted-foreground">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-background text-foreground">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* Advanced Settings */}
            <div className="bg-card rounded-lg border border-border shadow-sm overflow-hidden">
                <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors"
                >
                    <div className="flex items-center gap-2">
                        <Settings className="w-5 h-5 text-primary" />
                        <span className="font-medium text-foreground">고급 설정</span>
                    </div>
                    <ChevronDown className={cn(
                        "w-5 h-5 text-muted-foreground transition-transform",
                        showAdvanced && "rotate-180"
                    )} />
                </button>

                {showAdvanced && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="border-t border-border p-4 space-y-3"
                    >
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                병렬 처리 개수
                            </label>
                            <p className="text-xs text-muted-foreground mb-3">
                                작업을 여러 개로 나누어 동시에 처리합니다. 숫자가 클수록 빠르지만 서버 부하가 증가합니다.
                            </p>
                            <div className="flex items-center gap-4">
                                <input
                                    type="range"
                                    min="1"
                                    max="10"
                                    value={parallelCount}
                                    onChange={(e) => setParallelCount(parseInt(e.target.value))}
                                    className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                                />
                                <div className="w-12 h-10 flex items-center justify-center bg-primary/10 text-primary font-bold rounded-lg">
                                    {parallelCount}
                                </div>
                            </div>
                            <div className="flex justify-between text-xs text-muted-foreground mt-2">
                                <span>느림 (1개)</span>
                                <span>빠름 (10개)</span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
                <Button
                    variant="outline"
                    onClick={handleSaveSettings}
                    disabled={!hasValidMapping || saveMutation.isPending}
                    isLoading={saveMutation.isPending}
                    className="min-w-[140px]"
                >
                    {saveMutation.isPending ? (
                        '저장 중...'
                    ) : (
                        <>
                            <Save className="w-4 h-4 mr-2" />
                            이 설정 저장
                        </>
                    )}
                </Button>
                <Button
                    onClick={handleSubmit}
                    size="lg"
                    className="flex-1"
                >
                    작업 시작 →
                </Button>
            </div>
        </motion.div>
    );
};
