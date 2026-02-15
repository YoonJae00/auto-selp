import { useTheme } from '../../contexts/ThemeContext';
import { Sun, Moon } from 'lucide-react';

export const ThemeSettings = () => {
    const { theme, toggleTheme, isDark } = useTheme();

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-semibold mb-2">테마 설정</h3>
                <p className="text-sm text-muted-foreground mb-6">
                    화이트 모드와 다크 모드 중 선택하세요.
                </p>
            </div>

            {/* 테마 토글 */}
            <div className="flex items-center justify-between p-6 bg-card border border-border rounded-xl">
                <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-lg transition-colors ${isDark
                        ? 'bg-primary/10 text-primary'
                        : 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400'
                        }`}>
                        {isDark ? <Moon className="w-6 h-6" /> : <Sun className="w-6 h-6" />}
                    </div>
                    <div>
                        <div className="font-medium">
                            {isDark ? '다크 모드' : '화이트 모드'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                            {isDark ? '어두운 배경으로 눈의 피로를 줄여줍니다' : '밝고 따뜻한 화면으로 편안한 작업 환경을 제공합니다'}
                        </div>
                    </div>
                </div>

                {/* 토글 스위치 */}
                <button
                    onClick={toggleTheme}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${isDark ? 'bg-primary' : 'bg-gray-400 dark:bg-gray-300'
                        }`}
                    role="switch"
                    aria-checked={isDark}
                >
                    <span
                        className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform ${isDark ? 'translate-x-7' : 'translate-x-1'
                            }`}
                    />
                </button>
            </div>

            {/* 테마 미리보기 */}
            <div className="grid grid-cols-2 gap-4">
                {/* 화이트 모드 미리보기 */}
                <button
                    onClick={() => theme === 'dark' && toggleTheme()}
                    className={`p-4 rounded-xl border-2 transition-all ${!isDark
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                        }`}
                >
                    <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-4 rounded-lg mb-3">
                        <div className="bg-white rounded p-2 mb-2 shadow-sm">
                            <div className="h-2 bg-gray-800 rounded w-3/4 mb-1"></div>
                            <div className="h-2 bg-gray-400 rounded w-1/2"></div>
                        </div>
                        <div className="flex gap-2">
                            <div className="bg-white rounded p-2 flex-1 shadow-sm">
                                <div className="h-1 bg-indigo-400 rounded"></div>
                            </div>
                            <div className="bg-white rounded p-2 flex-1 shadow-sm">
                                <div className="h-1 bg-indigo-400 rounded"></div>
                            </div>
                        </div>
                    </div>
                    <div className="text-sm font-medium flex items-center justify-center gap-2">
                        <Sun className="w-4 h-4 text-amber-500" />
                        화이트 모드
                    </div>
                </button>

                {/* 다크 모드 미리보기 */}
                <button
                    onClick={() => theme === 'light' && toggleTheme()}
                    className={`p-4 rounded-xl border-2 transition-all ${isDark
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                        }`}
                >
                    <div className="bg-gradient-to-br from-gray-900 to-gray-800 p-4 rounded-lg mb-3">
                        <div className="bg-gray-800 rounded p-2 mb-2">
                            <div className="h-2 bg-gray-100 rounded w-3/4 mb-1"></div>
                            <div className="h-2 bg-gray-400 rounded w-1/2"></div>
                        </div>
                        <div className="flex gap-2">
                            <div className="bg-gray-800 rounded p-2 flex-1">
                                <div className="h-1 bg-indigo-400 rounded"></div>
                            </div>
                            <div className="bg-gray-800 rounded p-2 flex-1">
                                <div className="h-1 bg-indigo-400 rounded"></div>
                            </div>
                        </div>
                    </div>
                    <div className="text-sm font-medium flex items-center justify-center gap-2">
                        <Moon className="w-4 h-4 text-indigo-400" />
                        다크 모드
                    </div>
                </button>
            </div>

            {/* 정보 */}
            <div className="p-4 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground">
                    💡 테마 설정은 자동으로 저장되며, 다음에 접속할 때도 유지됩니다.
                </p>
            </div>
        </div>
    );
};
