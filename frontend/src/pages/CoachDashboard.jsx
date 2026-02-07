import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const CoachDashboard = () => {
    const [athletes, setAthletes] = useState([]);
    const [recentSessions, setRecentSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [athletesRes, sessionsRes] = await Promise.all([
                    client.get('/users/athletes'),
                    client.get('/organization/recent-sessions')
                ]);
                setAthletes(athletesRes.data);
                setRecentSessions(sessionsRes.data);
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);



    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 font-sans transition-colors duration-300">
             <div className="max-w-6xl mx-auto space-y-8">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Coach Dashboard</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Management of your Athlete Roster</p>
                    </div>
                     <div className="flex items-center gap-4">
                        <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1.5 rounded-lg dark:bg-blue-900/30 dark:text-blue-400">
                            {user?.full_name} ({user?.role})
                        </span>
                        <a href="/dashboard" className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-200 transition-colors">Go to Analysis</a>
                    </div>
                </div>

                {/* Athlete List */}
                <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                    <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Active Athletes</h2>
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-bold">{athletes.length} Registered</span>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-left text-sm whitespace-nowrap">
                            <thead className="uppercase tracking-wider border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-700/50">
                                <tr>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Name</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Email</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Status</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {athletes.map((athlete) => (
                                    <tr key={athlete.id} className="hover:bg-blue-50/30 dark:hover:bg-blue-900/20 transition-colors">
                                        <td className="px-6 py-4 text-gray-900 dark:text-gray-100 font-medium flex items-center gap-3">
                                            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-xs">
                                                {athlete.full_name.charAt(0)}
                                            </div>
                                            {athlete.full_name}
                                        </td>
                                        <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{athlete.email}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${athlete.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {athlete.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <Link 
                                                to={`/history?userId=${athlete.id}`}
                                                className="text-blue-600 hover:text-blue-800 font-medium text-xs border border-blue-200 px-3 py-1 rounded-lg hover:bg-blue-50 transition-colors inline-block"
                                            >
                                                View details
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                                {athletes.length === 0 && !loading && (
                                    <tr>
                                        <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                                            No athletes found. Invite them to register!
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
                {/* Recent Sessions (Live Feed) */}
                <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                    <div className="p-6 border-b border-gray-100 dark:border-gray-700">
                        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Recent Sessions</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-left text-sm whitespace-nowrap">
                            <thead className="uppercase tracking-wider border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-700/50">
                                <tr>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Date</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Athlete</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Score</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Duration</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {recentSessions.map((session) => (
                                    <tr key={session.id} className="hover:bg-blue-50/30 dark:hover:bg-blue-900/20 transition-colors">
                                        <td className="px-6 py-4 text-gray-900 dark:text-gray-100 font-medium">
                                            {new Date(session.created_at).toLocaleDateString()}
                                            <span className="text-xs text-gray-500 block">{new Date(session.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                                        </td>
                                        <td className="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">
                                            {session.athlete_name}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${session.technique_score >= 80 ? 'bg-green-100 text-green-800' : session.technique_score >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                                {session.technique_score.toFixed(1)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                                            {session.duration_seconds.toFixed(1)}s
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <Link 
                                                to={`/history?userId=${session.athlete_id}`}
                                                className="text-blue-600 hover:text-blue-800 font-medium text-xs hover:underline"
                                            >
                                                View Analysis
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                                {recentSessions.length === 0 && !loading && (
                                    <tr>
                                        <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                                            No recent sessions recorded.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
             </div>
        </div>
    );
};

export default CoachDashboard;
