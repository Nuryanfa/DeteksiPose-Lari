import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = ({ isOpen, toggle }) => {
    const location = useLocation();
    const { logout, user } = useAuth();

    const isActive = (path) => location.pathname === path;

    const allNavItems = [
        { 
            path: user?.role === 'management' ? '/management-dashboard' : (user?.role === 'coach' ? '/coach-dashboard' : '/dashboard'), 
            icon: (
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
        ), label: user?.role === 'management' ? 'Overview' : 'Dashboard', roles: ['athlete', 'coach', 'management'] },
        { path: '/history', icon: (
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        ), label: 'History', roles: ['athlete', 'coach'] },
        { path: '/compare', icon: (
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
        ), label: 'Compare', roles: ['athlete', 'coach'] },
    ];

    const navItems = allNavItems.filter(item => item.roles.includes(user?.role || 'athlete'));

    return (
        <div className={`${isOpen ? 'w-64' : 'w-20'} h-screen bg-white border-r border-gray-200 flex flex-col transition-all duration-300 fixed left-0 top-0 z-50`}>
            {/* Logo & Toggle */}
            <div className={`flex items-center ${isOpen ? 'justify-between px-6' : 'justify-center'} py-6 mb-2`}>
                <div className="flex items-center gap-3">
                     <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm shrink-0">
                        S
                    </div>
                    {isOpen && <span className="font-bold text-xl text-gray-800 tracking-tight whitespace-nowrap animate-fade-in">SSTS Pro</span>}
                </div>
                {/* Toggle Button (Only visible if open, or maybe handle differently?) */}
                {isOpen && (
                    <button onClick={toggle} className="p-1 rounded-lg hover:bg-gray-100 text-gray-400">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                    </button>
                )}
            </div>
            
            {!isOpen && (
                 <div className="flex justify-center mb-6">
                    <button onClick={toggle} className="p-2 rounded-lg hover:bg-gray-100 text-gray-400">
                         <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
                    </button>
                 </div>
            )}

            {/* Nav Items */}
            <nav className="flex-1 space-y-2 w-full px-3">
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`flex items-center gap-4 p-3 rounded-xl transition-all duration-200 group relative ${
                            isActive(item.path) 
                                ? 'bg-blue-50 text-blue-600' 
                                : 'text-gray-400 hover:bg-gray-50 hover:text-gray-600'
                        } ${isOpen ? '' : 'justify-center aspect-square'}`}
                        title={!isOpen ? item.label : ''}
                    >
                        <div className="shrink-0">{item.icon}</div>
                        {isOpen && (
                            <span className="font-medium text-sm whitespace-nowrap animate-fade-in">
                                {item.label}
                            </span>
                        )}
                    </Link>
                ))}
            </nav>

            {/* Bottom Actions */}
            <div className="space-y-2 w-full px-3 pb-6">
                 {/* Settings */}
                 <Link
                    to="/settings"
                    className={`flex items-center gap-4 p-3 rounded-xl transition-all duration-200 group relative ${
                        isActive('/settings') 
                            ? 'bg-blue-50 text-blue-600' 
                            : 'text-gray-400 hover:bg-gray-50 hover:text-gray-600'
                    } ${isOpen ? '' : 'justify-center aspect-square'}`}
                    title={!isOpen ? 'Settings' : ''}
                >
                    <div className="shrink-0">
                         <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </div>
                    {isOpen && <span className="font-medium text-sm animate-fade-in">Settings</span>}
                </Link>
                
                {/* Logout */}
                <button 
                    onClick={logout}
                    className={`flex items-center gap-4 p-3 rounded-xl text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors w-full ${isOpen ? '' : 'justify-center aspect-square'}`}
                    title={!isOpen ? "Logout" : ''}
                >
                    <div className="shrink-0">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                    </div>
                     {isOpen && <span className="font-medium text-sm animate-fade-in">Logout</span>}
                </button>
            </div>
        </div>
    );
};
export default Sidebar;
