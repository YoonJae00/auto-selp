import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Lock, User, KeyRound, Wand2 } from 'lucide-react';

const AdminSetup = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Step 1 state
    const [adminCode, setAdminCode] = useState('');

    // Step 2 state
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleVerifyCode = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await api.post('/api/auth/verify-admin-code', { admin_code: adminCode });
            setStep(2);
        } catch (err) {
            setError(err.response?.data?.detail || '인증 코드가 올바르지 않습니다.');
        } finally {
            setLoading(false);
        }
    };

    const handleRegisterAdmin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await api.post('/api/auth/register-admin', {
                username,
                password,
            });
            // Upon success, redirect to login
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || '관리자 계정 생성 중 오류가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-gray-950 to-gray-950">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-[100px] animate-pulse" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[100px]" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md relative z-10"
            >
                <Card className="border-white/5 bg-gray-950/60 p-8 shadow-2xl">
                    <div className="text-center mb-8">
                        <motion.div
                            initial={{ y: -20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.2 }}
                            className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 mb-4"
                        >
                            <Wand2 className="w-6 h-6" />
                        </motion.div>
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            Auto-Selp Admin
                        </h1>
                        <p className="text-gray-400 mt-2">
                            {step === 1 ? '관리자 인증 코드를 입력하세요' : '관리자 계정 생성'}
                        </p>
                    </div>

                    {step === 1 ? (
                        <form onSubmit={handleVerifyCode} className="space-y-6">
                            <div className="space-y-4">
                                <Input
                                    type="password"
                                    placeholder="인증 코드"
                                    value={adminCode}
                                    onChange={(e) => setAdminCode(e.target.value)}
                                    icon={<KeyRound className="w-5 h-5 text-gray-500" />}
                                    required
                                    className="bg-black/20"
                                />
                            </div>

                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="text-red-400 text-sm text-center bg-red-500/10 py-2 rounded-lg border border-red-500/20"
                                >
                                    {error}
                                </motion.div>
                            )}

                            <Button
                                type="submit"
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 border-none h-12 text-lg font-semibold shadow-xl shadow-indigo-500/20"
                                isLoading={loading}
                            >
                                인증하기
                            </Button>
                        </form>
                    ) : (
                        <form onSubmit={handleRegisterAdmin} className="space-y-6">
                            <div className="space-y-4">
                                <Input
                                    type="text"
                                    placeholder="관리자 아이디"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    icon={<User className="w-5 h-5 text-gray-500" />}
                                    required
                                    className="bg-black/20"
                                />
                                <Input
                                    type="password"
                                    placeholder="비밀번호"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    icon={<Lock className="w-5 h-5 text-gray-500" />}
                                    required
                                    className="bg-black/20"
                                />
                            </div>

                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="text-red-400 text-sm text-center bg-red-500/10 py-2 rounded-lg border border-red-500/20"
                                >
                                    {error}
                                </motion.div>
                            )}

                            <Button
                                type="submit"
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 border-none h-12 text-lg font-semibold shadow-xl shadow-indigo-500/20"
                                isLoading={loading}
                            >
                                관리자 계정 생성
                            </Button>
                        </form>
                    )}
                </Card>
            </motion.div>
        </div>
    );
};

export default AdminSetup;
