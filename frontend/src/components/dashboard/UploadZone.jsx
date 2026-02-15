import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileSpreadsheet, X, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';
import api from '../../lib/api';
import { ColumnMappingStep } from './ColumnMappingStep';

export const UploadZone = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [step, setStep] = useState('upload'); // 'upload' | 'mapping'
    const [previewData, setPreviewData] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles?.length > 0) {
            setFile(acceptedFiles[0]);
            setError(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls']
        },
        maxFiles: 1,
        multiple: false
    });

    const handlePreview = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const { data } = await api.post('/api/jobs/preview', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setPreviewData(data);
            setStep('mapping');
        } catch (err) {
            console.error(err);
            setError('파일 미리보기 실패. 올바른 엑셀 파일인지 확인해주세요.');
        } finally {
            setLoading(false);
        }
    };

    const handleUploadWithMapping = async (mapping) => {
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('column_mapping', JSON.stringify(mapping));

        try {
            const { data } = await api.post('/api/jobs/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Reset state
            setFile(null);
            setStep('upload');
            setPreviewData(null);

            if (onUploadSuccess) onUploadSuccess(data);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || '업로드 실패. 다시 시도해주세요.');
        } finally {
            setUploading(false);
        }
    };

    const handleBackToUpload = () => {
        setStep('upload');
        setPreviewData(null);
    };

    const removeFile = (e) => {
        e.stopPropagation();
        setFile(null);
        setError(null);
    };

    // Show column mapping step
    if (step === 'mapping' && previewData) {
        return (
            <ColumnMappingStep
                previewData={previewData}
                fileName={file?.name}
                onSubmit={handleUploadWithMapping}
                onBack={handleBackToUpload}
            />
        );
    }

    // Show upload step
    return (
        <div className="w-full">
            <div
                {...getRootProps()}
                className={cn(
                    "relative group border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 cursor-pointer overflow-hidden",
                    isDragActive
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50 hover:bg-muted",
                    file ? "border-primary/30 bg-primary/5" : ""
                )}
            >
                <input {...getInputProps()} />

                {/* Animated Background Gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                <AnimatePresence mode="wait">
                    {!file ? (
                        <motion.div
                            key="prompt"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-4"
                        >
                            <div className="w-16 h-16 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-300">
                                <UploadCloud className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-lg font-medium text-foreground">
                                    {isDragActive ? "파일을 여기에 놓으세요" : "여기에 엑셀 파일을 드래그 앤 드롭하세요"}
                                </p>
                                <p className="text-sm text-muted-foreground mt-1">
                                    또는 클릭하여 파일 선택 (.xlsx, .xls)
                                </p>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="file"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="flex flex-col items-center gap-4"
                        >
                            <div className="relative">
                                <div className="w-16 h-16 rounded-2xl bg-green-100 dark:bg-green-500/10 flex items-center justify-center text-green-600 dark:text-green-400 shadow-lg shadow-green-500/10">
                                    <FileSpreadsheet className="w-8 h-8" />
                                </div>
                                {!loading && !uploading && (
                                    <button
                                        onClick={removeFile}
                                        className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition shadow-md"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                )}
                            </div>

                            <div>
                                <p className="font-medium text-foreground">{file.name}</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>

                            {(loading || uploading) && (
                                <div className="flex items-center gap-2 text-primary text-sm">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>{loading ? '미리보기 로딩 중...' : '업로드 처리 중...'}</span>
                                </div>
                            )}

                            {error && (
                                <p className="text-destructive text-sm bg-destructive/10 px-3 py-1 rounded-full">
                                    {error}
                                </p>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <AnimatePresence>
                {file && !loading && !uploading && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="mt-4 flex justify-end"
                    >
                        <Button
                            onClick={(e) => {
                                e.stopPropagation();
                                handlePreview();
                            }}
                            className="w-full sm:w-auto shadow-indigo-500/20"
                            size="lg"
                        >
                            다음 단계 →
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

