import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../ui/Button';
import { Check, AlertCircle } from 'lucide-react';

// A-Z 컬럼 생성 (26개 + AA-AZ 추가 옵션)
const generateColumnOptions = () => {
    const columns = [];
    // A-Z (26개)
    for (let i = 0; i < 26; i++) {
        columns.push(String.fromCharCode(65 + i));
    }
    // AA-AZ (26개 더)
    for (let i = 0; i < 26; i++) {
        columns.push('A' + String.fromCharCode(65 + i));
    }
    return columns;
};

const COLUMN_OPTIONS = generateColumnOptions();

export const ExcelColumnMapping = ({ mapping, onChange, onSave, isSaving }) => {
    const [localMapping, setLocalMapping] = useState(mapping || {
        original_product_name: 'A',
        refined_product_name: 'B',
        keyword: 'C',
        category: 'D'
    });

    const [hasChanges, setHasChanges] = useState(false);

    const handleChange = (field, value) => {
        const updated = { ...localMapping, [field]: value };
        setLocalMapping(updated);
        setHasChanges(true);
        if (onChange) onChange(updated);
    };

    const handleSave = () => {
        if (onSave) {
            onSave(localMapping);
            setHasChanges(false);
        }
    };

    const fields = [
        {
            key: 'original_product_name',
            label: '원본 상품명 컬럼',
            description: '가공 전 상품명이 있는 엑셀 열',
            example: '예: A열, B열'
        },
        {
            key: 'refined_product_name',
            label: '바꿀 상품명 컬럼',
            description: '가공된 상품명을 저장할 열',
            example: '예: B열, C열'
        },
        {
            key: 'keyword',
            label: '키워드 컬럼',
            description: '발굴된 키워드를 저장할 열',
            example: '예: D열, E열'
        },
        {
            key: 'category',
            label: '카테고리 컬럼',
            description: '분류된 카테고리를 저장할 열',
            example: '예: F열, G열'
        }
    ];

    return (
        <div className="space-y-6">
            <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-indigo-400 mt-0.5 flex-shrink-0" />
                    <div>
                        <h3 className="text-sm font-semibold text-indigo-600 dark:text-indigo-300 mb-1">엑셀 컬럼 매핑이란?</h3>
                        <p className="text-sm text-indigo-700/80 dark:text-indigo-400/80">
                            엑셀 파일의 각 열 위치(A, B, C...)를 지정합니다.
                            예: 원본상품명이 C열에 있다면 "C"를 선택하세요.
                        </p>
                    </div>
                </div>
            </div>

            <div className="space-y-5">
                {fields.map((field) => (
                    <div key={field.key} className="space-y-2">
                        <label className="block">
                            <span className="text-sm font-medium text-foreground">{field.label}</span>
                            <span className="text-xs text-muted-foreground ml-2">{field.description}</span>
                        </label>

                        <div className="relative">
                            <select
                                value={localMapping[field.key] || 'A'}
                                onChange={(e) => handleChange(field.key, e.target.value)}
                                className="w-full px-4 py-3 bg-background border border-input rounded-xl text-foreground 
                                         focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                                         transition-all duration-200 appearance-none cursor-pointer
                                         hover:bg-accent"
                            >
                                {COLUMN_OPTIONS.map((col) => (
                                    <option key={col} value={col}>
                                        {col}열
                                    </option>
                                ))}
                            </select>
                            {/* 드롭다운 화살표 아이콘 */}
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                                <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </div>
                        </div>

                        <p className="text-xs text-muted-foreground ml-1">{field.example}</p>
                    </div>
                ))}
            </div>

            {/* 미리보기 */}
            <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
                <h4 className="text-sm font-semibold text-foreground mb-3">📋 현재 매핑</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">원본 상품명:</span>
                        <span className="px-2 py-1 bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 rounded font-mono">
                            {localMapping.original_product_name}열
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">바꿀 상품명:</span>
                        <span className="px-2 py-1 bg-green-500/10 text-green-600 dark:text-green-300 rounded font-mono">
                            {localMapping.refined_product_name}열
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">키워드:</span>
                        <span className="px-2 py-1 bg-purple-500/10 text-purple-600 dark:text-purple-300 rounded font-mono">
                            {localMapping.keyword}열
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">카테고리:</span>
                        <span className="px-2 py-1 bg-orange-500/10 text-orange-600 dark:text-orange-300 rounded font-mono">
                            {localMapping.category}열
                        </span>
                    </div>
                </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
                <AnimatePresence>
                    {hasChanges && (
                        <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -10 }}
                            className="text-sm text-amber-600 dark:text-amber-400 flex items-center gap-2"
                        >
                            <AlertCircle className="w-4 h-4" />
                            저장되지 않은 변경사항이 있습니다
                        </motion.div>
                    )}
                </AnimatePresence>

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
        </div >
    );
};
