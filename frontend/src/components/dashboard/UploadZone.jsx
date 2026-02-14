import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone'; // need to install this
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileSpreadsheet, X, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';
import api from '../../lib/api';

export const UploadZone = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);

    const onDrop = useCallback((acceptedFiles) => {
        // Only accept one file for now
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

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const { data } = await api.post('/api/jobs/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Reset after success
            setFile(null);
            if (onUploadSuccess) onUploadSuccess(data);
        } catch (err) {
            console.error(err);
            setError('업로드 실패. 다시 시도해주세요.');
        } finally {
            setUploading(false);
        }
    };

    const removeFile = (e) => {
        e.stopPropagation();
        setFile(null);
    };

    return (
        <div className="w-full">
            <div
                {...getRootProps()}
                className={cn(
                    "relative group border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 cursor-pointer overflow-hidden",
                    isDragActive
                        ? "border-indigo-500 bg-indigo-500/10"
                        : "border-white/10 hover:border-indigo-500/50 hover:bg-white/5",
                    file ? "border-indigo-500/30 bg-indigo-500/5" : ""
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
                            <div className="w-16 h-16 mx-auto rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform duration-300">
                                <UploadCloud className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-lg font-medium text-white">
                                    {isDragActive ? "파일을 여기에 놓으세요" : "여기에 엑셀 파일을 드래그 앤 드롭하세요"}
                                </p>
                                <p className="text-sm text-gray-400 mt-1">
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
                                <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center text-green-400 shadow-lg shadow-green-500/10">
                                    <FileSpreadsheet className="w-8 h-8" />
                                </div>
                                {!uploading && (
                                    <button
                                        onClick={removeFile}
                                        className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition shadow-md"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                )}
                            </div>

                            <div>
                                <p className="font-medium text-white">{file.name}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>

                            {uploading && (
                                <div className="flex items-center gap-2 text-indigo-400 text-sm">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>업로드 처리 중...</span>
                                </div>
                            )}

                            {error && (
                                <p className="text-red-400 text-sm bg-red-500/10 px-3 py-1 rounded-full">
                                    {error}
                                </p>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <AnimatePresence>
                {file && !uploading && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="mt-4 flex justify-end"
                    >
                        <Button
                            onClick={(e) => {
                                e.stopPropagation();
                                handleUpload();
                            }}
                            className="w-full sm:w-auto shadow-indigo-500/20"
                            size="lg"
                        >
                            자동화 작업 시작
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
