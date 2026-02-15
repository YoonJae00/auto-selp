import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { supabase } from './lib/supabase';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Prompts from './pages/Prompts';
import JobDetail from './pages/JobDetail';

const queryClient = new QueryClient();

// Protected Route Component
const ProtectedRoute = ({ children }) => {
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session);
            setLoading(false);
        });

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
        });

        return () => subscription.unsubscribe();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">
                Loading...
            </div>
        );
    }

    if (!session) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

function App() {
    return (
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
                                    <Route path="/prompts" element={<Prompts />} />
                                    <Route path="/job/:jobId" element={<JobDetail />} />
                                    <Route path="*" element={<Navigate to="/" replace />} />
                                </Routes>
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </Router>
        </QueryClientProvider>
    );
}

export default App;
