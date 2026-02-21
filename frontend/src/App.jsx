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

const queryClient = new QueryClient();

const ProtectedRoute = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            setIsAuthenticated(true);
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

    return children;
};

function App() {
    return (
        <ThemeProvider>
            <QueryClientProvider client={queryClient}>
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route
                            path="/*"
                            element={
                                <ProtectedRoute>
                                    <Routes>
                                        <Route path="/" element={<Dashboard />} />
                                        <Route path="/excel" element={<ExcelProcessor />} />
                                        <Route path="/prompts" element={<Prompts />} />
                                        <Route path="/settings" element={<Settings />} />
                                        <Route path="/job/:jobId" element={<JobDetail />} />
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
