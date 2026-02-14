import { Sidebar } from './Sidebar';

export const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-background text-foreground">
            <Sidebar />
            <main className="pl-64 min-h-screen">
                <div className="container mx-auto p-8 max-w-7xl animate-in fade-in duration-500">
                    {children}
                </div>
            </main>
        </div>
    );
};
