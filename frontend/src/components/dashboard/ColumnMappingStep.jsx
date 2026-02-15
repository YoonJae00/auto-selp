import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, FileSpreadsheet, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';

export const ColumnMappingStep = ({ previewData, onSubmit, onBack, fileName }) => {
    const [mapping, setMapping] = useState({
        original_product_name: '',
        refined_product_name: '',
        keyword: '',
        category: ''
    });
    const [error, setError] = useState('');

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
        onSubmit(mapping);
    };

    const handleColumnSelect = (field, value) => {
        setMapping(prev => ({
            ...prev,
            [field]: value
        }));
        setError('');
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                        <FileSpreadsheet className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">열 매핑 설정</h3>
                        <p className="text-sm text-gray-400">{fileName}</p>
                    </div>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onBack}
                    className="text-gray-400 hover:text-white"
                >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    돌아가기
                </Button>
            </div>

            {/* Excel Preview */}
            <div className="bg-white/5 rounded-xl p-4 overflow-x-auto border border-white/10">
                <p className="text-sm text-gray-400 mb-3">엑셀 미리보기 (처음 5행)</p>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                        <thead>
                            <tr className="bg-gray-800/50">
                                <th className="border border-gray-700 px-3 py-2 text-left text-gray-500 font-medium min-w-[60px]">#</th>
                                {previewData.columns.map((col, idx) => (
                                    <th
                                        key={idx}
                                        className="border border-gray-700 px-3 py-2 text-left text-indigo-400 font-medium min-w-[120px] max-w-[200px]"
                                    >
                                        {col}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {/* Headers Row */}
                            <tr className="bg-white/5">
                                <td className="border border-gray-700 px-3 py-2 text-gray-500">1</td>
                                {previewData.headers.map((header, idx) => (
                                    <td
                                        key={idx}
                                        className="border border-gray-700 px-3 py-2 text-white font-medium max-w-[200px] truncate"
                                        title={header || '(비어있음)'}
                                    >
                                        {header || '(비어있음)'}
                                    </td>
                                ))}
                            </tr>
                            {/* Preview Rows */}
                            {previewData.preview_rows.map((row, rowIdx) => (
                                <tr key={rowIdx} className="hover:bg-white/5">
                                    <td className="border border-gray-700 px-3 py-2 text-gray-500">{rowIdx + 2}</td>
                                    {row.map((cell, cellIdx) => (
                                        <td
                                            key={cellIdx}
                                            className="border border-gray-700 px-3 py-2 text-gray-300 max-w-[200px] truncate"
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
                <p className="text-white font-medium">열 선택 <span className="text-red-400 text-sm">(모두 필수)</span></p>

                {/* Original Product Name Column */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <label className="block text-sm font-medium text-white mb-2">
                        원본 상품명 열 <span className="text-red-400">*</span>
                    </label>
                    <p className="text-xs text-gray-400 mb-2">도매상에서 받은 원본 상품명이 있는 열</p>
                    <div className="relative">
                        <select
                            value={mapping.original_product_name}
                            onChange={(e) => handleColumnSelect('original_product_name', e.target.value)}
                            className={cn(
                                "w-full bg-white/10 border rounded-lg px-4 py-3 text-white appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-indigo-500",
                                mapping.original_product_name ? "border-indigo-500" : "border-white/20"
                            )}
                        >
                            <option value="" className="bg-gray-900">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-gray-900">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                    </div>
                </div>

                {/* Refined Product Name Column */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <label className="block text-sm font-medium text-white mb-2">
                        가공된 상품명 열 <span className="text-red-400">*</span>
                    </label>
                    <p className="text-xs text-gray-400 mb-2">AI로 가공된 상품명을 저장할 열 (기존 데이터가 있어도 덮어씁니다)</p>
                    <div className="relative">
                        <select
                            value={mapping.refined_product_name}
                            onChange={(e) => handleColumnSelect('refined_product_name', e.target.value)}
                            className={cn(
                                "w-full bg-white/10 border rounded-lg px-4 py-3 text-white appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-indigo-500",
                                mapping.refined_product_name ? "border-indigo-500" : "border-white/20"
                            )}
                        >
                            <option value="" className="bg-gray-900">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-gray-900">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                    </div>
                </div>

                {/* Keyword Column */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <label className="block text-sm font-medium text-white mb-2">
                        키워드 열 <span className="text-red-400">*</span>
                    </label>
                    <p className="text-xs text-gray-400 mb-2">추천 키워드를 저장할 열</p>
                    <div className="relative">
                        <select
                            value={mapping.keyword}
                            onChange={(e) => handleColumnSelect('keyword', e.target.value)}
                            className={cn(
                                "w-full bg-white/10 border rounded-lg px-4 py-3 text-white appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-indigo-500",
                                mapping.keyword ? "border-indigo-500" : "border-white/20"
                            )}
                        >
                            <option value="" className="bg-gray-900">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-gray-900">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                    </div>
                </div>

                {/* Category Column */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <label className="block text-sm font-medium text-white mb-2">
                        카테고리 열 <span className="text-red-400">*</span>
                    </label>
                    <p className="text-xs text-gray-400 mb-2">카테고리 코드를 저장할 열</p>
                    <div className="relative">
                        <select
                            value={mapping.category}
                            onChange={(e) => handleColumnSelect('category', e.target.value)}
                            className={cn(
                                "w-full bg-white/10 border rounded-lg px-4 py-3 text-white appearance-none cursor-pointer",
                                "focus:outline-none focus:ring-2 focus:ring-indigo-500",
                                mapping.category ? "border-indigo-500" : "border-white/20"
                            )}
                        >
                            <option value="" className="bg-gray-900">선택하세요</option>
                            {previewData.columns.map((col, idx) => (
                                <option key={col} value={col} className="bg-gray-900">
                                    {col}열 - {previewData.headers[idx] || '(제목 없음)'}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Submit Button */}
            <Button
                onClick={handleSubmit}
                size="lg"
                className="w-full"
            >
                작업 시작
            </Button>
        </motion.div>
    );
};
