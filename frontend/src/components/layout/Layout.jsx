import { Sidebar } from './Sidebar';

export const Layout = ({ children }) => {
    return (
        <div className="flex min-h-screen bg-background">
            <Sidebar />
            <main className="flex-1 ml-64 p-8 min-w-0">
                {children}
            </main>
        </div>
    );
};
