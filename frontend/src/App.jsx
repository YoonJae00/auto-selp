import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Prompts from './pages/Prompts';
import JobDetail from './pages/JobDetail';
import Settings from './pages/Settings';
import ExcelProcessor from './pages/ExcelProcessor';
import AdminSetup from './pages/AdminSetup';
import ProfileSetup from './pages/ProfileSetup';
import UserManagement from './pages/UserManagement';

const queryClient = new QueryClient();

const ProtectedRoute = ({ children, requireProfileCompleted = true, requireAdmin = false }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const userStr = localStorage.getItem('user');
        if (token) {
            setIsAuthenticated(true);
            if (userStr) {
                setUser(JSON.parse(userStr));
            }
        }
        setLoading(false);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">
                Loading...
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (requireProfileCompleted && user && !user.is_profile_completed) {
        return <Navigate to="/profile-setup" replace />;
    }

    if (requireAdmin && user && user.role !== 'admin') {
        return <Navigate to="/" replace />;
    }

    return children;
};

function App() {
    return (
        <ThemeProvider>
            <QueryClientProvider client={queryClient}>
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/admin-setup" element={<AdminSetup />} />

                        {/* Route that requires auth but NOT profile completion */}
                        <Route
                            path="/profile-setup"
                            element={
                                <ProtectedRoute requireProfileCompleted={false}>
                                    <ProfileSetup />
                                </ProtectedRoute>
                            }
                        />

                        {/* Routes that require full auth & setup */}
                        <Route
                            path="/*"
                            element={
                                <ProtectedRoute requireProfileCompleted={true}>
                                    <Routes>
                                        <Route path="/" element={<Dashboard />} />
                                        <Route path="/excel" element={<ExcelProcessor />} />
                                        <Route path="/prompts" element={<Prompts />} />
                                        <Route path="/settings" element={<Settings />} />
                                        <Route path="/job/:jobId" element={<JobDetail />} />
                                        <Route
                                            path="/users"
                                            element={
                                                <ProtectedRoute requireAdmin={true}>
                                                    <UserManagement />
                                                </ProtectedRoute>
                                            }
                                        />
                                        <Route path="*" element={<Navigate to="/" replace />} />
                                    </Routes>
                                </ProtectedRoute>
                            }
                        />
                    </Routes>
                </Router>
            </QueryClientProvider>
        </ThemeProvider>
    );
}

export default App;
