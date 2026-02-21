import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { User, Mail, Phone, UserCircle2 } from 'lucide-react';

const ProfileSetup = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');

    const handleProfileSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await api.post('/api/auth/update-profile', {
                name,
                email,
                phone
            });

            // Update local user state
            const userStr = localStorage.getItem('user');
            if (userStr) {
                const user = JSON.parse(userStr);
                user.is_profile_completed = true;
                localStorage.setItem('user', JSON.stringify(user));
            }

            // Redirect to dashboard
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || '프로필 업데이트 중 오류가 발생했습니다.');
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
                            <UserCircle2 className="w-6 h-6" />
                        </motion.div>
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            환영합니다!
                        </h1>
                        <p className="text-gray-400 mt-2">
                            시작하기 전에 추가 정보를 입력해 주세요.
                        </p>
                    </div>

                    <form onSubmit={handleProfileSubmit} className="space-y-6">
                        <div className="space-y-4">
                            <Input
                                type="text"
                                placeholder="이름 (담당자명)"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                icon={<User className="w-5 h-5 text-gray-500" />}
                                required
                                className="bg-black/20"
                            />
                            <Input
                                type="email"
                                placeholder="이메일 주소"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                icon={<Mail className="w-5 h-5 text-gray-500" />}
                                required
                                className="bg-black/20"
                            />
                            <Input
                                type="tel"
                                placeholder="연락처 (010-0000-0000)"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                icon={<Phone className="w-5 h-5 text-gray-500" />}
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
                            시작하기
                        </Button>
                    </form>
                </Card>
            </motion.div>
        </div>
    );
};

export default ProfileSetup;
