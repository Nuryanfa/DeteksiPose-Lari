import React, { useState, useEffect } from 'react';
import client from '../api/client';
import Skeleton from '../components/Skeleton';

const ManagementDashboard = () => {
    const [summary, setSummary] = useState(null);
    const [recentSessions, setRecentSessions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [summaryRes, sessionsRes] = await Promise.all([
                client.get('/organization/summary'),
                client.get('/organization/recent-sessions')
            ]);
            setSummary(summaryRes.data);
            setRecentSessions(sessionsRes.data);
        } catch (error) {
            console.error("Failed to fetch management data", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-[1600px] mx-auto space-y-8 animate-fade-in font-sans p-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-800">Organization Overview</h1>
                <p className="text-gray-500">Monitor team performance and activity across the organization.</p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KPICard 
                    title="Total Athletes" 
                    value={summary?.total_athletes} 
                    icon={<UserGroupIcon />} 
                    color="blue" 
                    loading={loading} 
                />
                <KPICard 
                    title="Total Sessions" 
                    value={summary?.total_sessions} 
                    icon={<VideoCameraIcon />} 
                    color="purple" 
                    loading={loading} 
                />
                <KPICard 
                    title="Avg Technique Score" 
                    value={summary?.avg_system_score} 
                    icon={<ChartBarIcon />} 
                    color="green" 
                    loading={loading} 
                />
                <KPICard 
                    title="Active Today" 
                    value={summary?.active_today} 
                    icon={<LightningBoltIcon />} 
                    color="orange" 
                    loading={loading} 
                />
            </div>

            {/* Recent Activity Table */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 overflow-hidden">
                <h2 className="text-lg font-bold text-gray-800 mb-6">Global Recent Activity</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-gray-400 uppercase border-b border-gray-100">
                            <tr>
                                <th className="py-3 px-4 font-semibold">Athlete</th>
                                <th className="py-3 px-4 font-semibold">Date</th>
                                <th className="py-3 px-4 font-semibold">Technique Score</th>
                                <th className="py-3 px-4 font-semibold">Duration</th>
                                <th className="py-3 px-4 font-semibold text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {loading ? (
                                [...Array(5)].map((_, i) => (
                                    <tr key={i}>
                                        <td className="py-4 px-4"><Skeleton className="h-4 w-32" /></td>
                                        <td className="py-4 px-4"><Skeleton className="h-4 w-24" /></td>
                                        <td className="py-4 px-4"><Skeleton className="h-4 w-12" /></td>
                                        <td className="py-4 px-4"><Skeleton className="h-4 w-16" /></td>
                                        <td className="py-4 px-4"><Skeleton className="h-4 w-8 ml-auto" /></td>
                                    </tr>
                                ))
                            ) : recentSessions.length > 0 ? (
                                recentSessions.map((session) => (
                                    <tr key={session.id} className="hover:bg-gray-50/50 transition-colors">
                                        <td className="py-4 px-4 font-medium text-gray-900">{session.athlete_name}</td>
                                        <td className="py-4 px-4 text-gray-500">
                                            {new Date(session.created_at).toLocaleDateString('en-GB', {
                                                day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                                            })}
                                        </td>
                                        <td className="py-4 px-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                                                session.technique_score >= 80 ? 'bg-green-100 text-green-700' :
                                                session.technique_score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                                'bg-red-100 text-red-700'
                                            }`}>
                                                {session.technique_score.toFixed(1)}
                                            </span>
                                        </td>
                                        <td className="py-4 px-4 text-gray-500">{session.duration_seconds.toFixed(1)}s</td>
                                        <td className="py-4 px-4 text-right">
                                            <button className="text-gray-400 hover:text-blue-600 font-medium transition-colors">
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="py-12 text-center text-gray-400">
                                        No recent sessions found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

// --- Components ---

const KPICard = ({ title, value, icon, color, loading }) => {
    const colors = {
        blue: 'text-blue-600 bg-blue-50',
        purple: 'text-purple-600 bg-purple-50',
        green: 'text-green-600 bg-green-50',
        orange: 'text-orange-600 bg-orange-50'
    };

    return (
        <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-4 hover:shadow-md transition-all">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${colors[color]}`}>
                {icon}
            </div>
            <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-500">{title}</h3>
                {loading ? (
                    <Skeleton className="h-8 w-16 mt-1" />
                ) : (
                    <p className="text-2xl font-bold text-gray-800 animate-slide-in">{value}</p>
                )}
            </div>
        </div>
    );
};

// Icons (Simple SVGs)
const UserGroupIcon = () => (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
);
const VideoCameraIcon = () => (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
);
const ChartBarIcon = () => (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
);
const LightningBoltIcon = () => (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

export default ManagementDashboard;
