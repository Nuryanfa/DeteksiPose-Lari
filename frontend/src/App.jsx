import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Comparison from './pages/Comparison';
import Register from './pages/Register';
import CoachDashboard from './pages/CoachDashboard';
import ManagementDashboard from './pages/ManagementDashboard';
import ErrorBoundary from './components/ErrorBoundary';

import Sidebar from './components/Sidebar';

const ProtectedRoute = () => {
    const { user } = useAuth();
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(false); // Default collapsed (mini)

    if (!user) {
        return <Navigate to="/login" replace />;
    }
    return (
        <div className="flex bg-gray-50 min-h-screen">
            <Sidebar isOpen={isSidebarOpen} toggle={() => setIsSidebarOpen(!isSidebarOpen)} />
            <div className={`flex-1 p-8 transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
                <Outlet />
            </div>
        </div>
    );
};

import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                <Route element={<ProtectedRoute />}>
                    <Route path="/dashboard" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
                    <Route path="/coach-dashboard" element={<CoachDashboard />} />
                    <Route path="/history" element={<History />} />
                    <Route path="/compare" element={<Comparison />} />
                    <Route path="/management-dashboard" element={<ManagementDashboard />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                </Route>
            </Routes>
        </Router>
    </AuthProvider>
  );
}

export default App;
