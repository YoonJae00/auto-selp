import { useState } from 'react';
import { motion } from 'framer-motion';
import api from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { UserPlus, User, Lock, AlertCircle } from 'lucide-react';

const UserManagement = () => {
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);
    const [error, setError] = useState(null);

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleCreateUser = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccessMessage(null);

        try {
            await api.post('/api/auth/register-user', {
                username,
                password,
            });

            setSuccessMessage(`성공적으로 계정을 생성했습니다: ${username}`);
            setUsername('');
            setPassword('');
        } catch (err) {
            setError(err.response?.data?.detail || '일반 회원 계정 생성 중 오류가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                    <UserPlus className="w-8 h-8 text-indigo-400" />
                    회원 관리
                </h1>
                <p className="text-gray-400">
                    관리자 전용 기능입니다. 새로운 회원을 등록하여 접속 권한을 부여하세요.
                </p>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid gap-6 md:grid-cols-2"
            >
                <Card className="border-white/5 bg-gray-900/50 p-6 backdrop-blur-xl">
                    <h2 className="text-xl font-semibold text-white mb-6">신규 계정 발급</h2>
                    <form onSubmit={handleCreateUser} className="space-y-4">
                        <div className="space-y-4">
                            <Input
                                type="text"
                                placeholder="회원 아이디"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                icon={<User className="w-5 h-5 text-gray-500" />}
                                required
                                className="bg-black/20"
                            />
                            <Input
                                type="password"
                                placeholder="임시 비밀번호"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                icon={<Lock className="w-5 h-5 text-gray-500" />}
                                required
                                className="bg-black/20"
                            />
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20"
                            >
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </motion.div>
                        )}

                        {successMessage && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex items-center gap-2 text-green-400 text-sm bg-green-500/10 p-3 rounded-lg border border-green-500/20"
                            >
                                {successMessage}
                            </motion.div>
                        )}

                        <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 border-none"
                            isLoading={loading}
                        >
                            생성하기
                        </Button>
                    </form>
                </Card>

                <Card className="border-white/5 bg-gray-900/50 p-6 backdrop-blur-xl flex flex-col justify-center text-center">
                    <div className="inline-flex mx-auto p-4 rounded-full bg-indigo-500/10 text-indigo-400 mb-4">
                        <AlertCircle className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-2">계정 발급 안내</h3>
                    <p className="text-sm text-gray-400 leading-relaxed">
                        발급된 아이디와 임시 비밀번호를 회원에게 전달해 주세요.<br />
                        회원은 최초 로그인 시 추가 프로필 정보를 입력해야만 시스템을 정상적으로 사용할 수 있습니다.
                    </p>
                </Card>
            </motion.div>
        </div>
    );
};

export default UserManagement;
