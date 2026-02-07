import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import client from '../api/client';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

import { useAuth } from '../contexts/AuthContext';

const FeedbackModal = ({ session, onClose, onSave, isCoach }) => {
    const [notes, setNotes] = useState(session.coach_notes || '');
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        await onSave(session.id, notes);
        setSaving(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-lg w-full p-6 animate-scale-in">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Coach Feedback</h3>
                
                {isCoach ? (
                    <textarea
                        className="w-full h-32 p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 mb-4"
                        placeholder="Write your feedback here..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                    />
                ) : (
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-4 min-h-[5rem]">
                        <p className="text-gray-700 dark:text-gray-300 italic">
                            {notes ? `"${notes}"` : "No feedback provided yet."}
                        </p>
                    </div>
                )}

                <div className="flex justify-end gap-3">
                    <button 
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                        Close
                    </button>
                    {isCoach && (
                        <button 
                            onClick={handleSave}
                            disabled={saving}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg shadow-blue-500/30 transition-all"
                        >
                            {saving ? 'Saving...' : 'Save Feedback'}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

const History = () => {
    const { user } = useAuth();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedSession, setSelectedSession] = useState(null);

    const [searchParams] = useSearchParams();
    const targetUserId = searchParams.get('userId');

    useEffect(() => {
        fetchHistory();
    }, [targetUserId]);

    const fetchHistory = async () => {
        try {
            const url = targetUserId ? `/history/?user_id=${targetUserId}` : '/history/';
            const res = await client.get(url);
            setSessions(res.data);
        } catch (error) {
            console.error("Failed to fetch history:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateFeedback = async (sessionId, notes) => {
        try {
            await client.put(`/history/${sessionId}/feedback`, { coach_notes: notes });
            // Update local state
            setSessions(sessions.map(s => s.id === sessionId ? { ...s, coach_notes: notes } : s));
        } catch (error) {
            console.error("Failed to save feedback:", error);
            alert("Failed to save feedback");
        }
    };

    const formatDate = (dateString) => {
        const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    };

    const exportPDF = () => {
        const doc = new jsPDF();
        
        // Header
        doc.setFontSize(20);
        doc.text("SSTS Training Report", 14, 22);
        
        doc.setFontSize(11);
        doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 30);
        
        // Table
        const tableColumn = ["Date", "Score", "Cadence", "Stride (m)", "GCT (ms)", "Duration (s)", "Notes"];
        const tableRows = [];

        sessions.forEach(session => {
            const sessionData = [
                formatDate(session.created_at),
                session.technique_score.toFixed(1),
                session.avg_cadence.toFixed(0),
                session.avg_stride_length.toFixed(2),
                session.avg_gct.toFixed(0),
                session.duration_seconds.toFixed(1),
                session.coach_notes || '-'
            ];
            tableRows.push(sessionData);
        });

        autoTable(doc, {
            head: [tableColumn],
            body: tableRows,
            startY: 40,
        });

        doc.save("ssts_training_report.pdf");
    };

    // Prepare Chart Data (Score Progress)
    // Reverse sessions so graph goes left-to-right (Oldest to Newest)
    const reversedSessions = [...sessions].reverse();
    const chartData = {
        labels: reversedSessions.map(s => new Date(s.created_at).toLocaleDateString()),
        datasets: [
            {
                label: 'Technique Score',
                data: reversedSessions.map(s => s.technique_score),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                tension: 0.3,
            },
            {
                label: 'Avg Cadence',
                data: reversedSessions.map(s => s.avg_cadence),
                borderColor: 'rgb(34, 197, 94)',
                backgroundColor: 'rgba(34, 197, 94, 0.5)',
                tension: 0.3,
                yAxisID: 'y1'
            }
        ],
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Training Progress' },
        },
        scales: {
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                min: 0,
                max: 100,
                title: { display: true, text: 'Score' }
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                grid: { drawOnChartArea: false },
                title: { display: true, text: 'Cadence (spm)' }
            },
        },
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 font-sans transition-colors duration-300">
             <div className="max-w-6xl mx-auto space-y-8">
                <div className="flex justify-between items-center">
                    <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Session History</h1>
                    <div className="flex gap-3">
                        <button onClick={exportPDF} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-lg shadow-blue-500/30 transition-all transform hover:scale-105">Export PDF</button>
                        <a href="/" className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-200 transition-colors">Back to Dashboard</a>
                    </div>
                </div>

                {/* Progress Chart */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="h-80">
                         {sessions.length > 0 ? <Line options={chartOptions} data={chartData} /> : <p className="text-center text-gray-400 mt-32">No session data available yet.</p>}
                    </div>
                </div>

                {/* Session List */}
                <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-left text-sm whitespace-nowrap">
                            <thead className="uppercase tracking-wider border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-700/50">
                                <tr>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Date</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Score</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Cadence</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Stride (m)</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">GCT (ms)</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Duration</th>
                                    <th className="px-6 py-4 font-bold text-gray-600 dark:text-gray-300">Feedback</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {sessions.map((session) => (
                                    <tr key={session.id} className="hover:bg-blue-50/30 dark:hover:bg-blue-900/20 transition-colors">
                                        <td className="px-6 py-4 text-gray-900 dark:text-gray-100 font-medium">{formatDate(session.created_at)}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${session.technique_score >= 80 ? 'bg-green-100 text-green-800' : session.technique_score >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                                {session.technique_score.toFixed(1)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{session.avg_cadence.toFixed(0)} spm</td>
                                        <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{session.avg_stride_length.toFixed(2)} m</td>
                                        <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{session.avg_gct.toFixed(0)} ms</td>
                                        <td className="px-6 py-4 text-gray-400 dark:text-gray-500">{session.duration_seconds.toFixed(1)}s</td>
                                        <td className="px-6 py-4">
                                            <button 
                                                onClick={() => setSelectedSession(session)}
                                                className={`flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                                                    session.coach_notes 
                                                    ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' 
                                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                }`}
                                            >
                                                {user?.role === 'athlete' ? (
                                                    <>
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                                                        View Feedback
                                                    </>
                                                ) : (
                                                    session.coach_notes ? (
                                                        <>
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                                                            Edit Feedback
                                                        </>
                                                    ) : (
                                                        <>
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
                                                            Give Feedback
                                                        </>
                                                    )
                                                )}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {sessions.length === 0 && (
                                    <tr>
                                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                                            No sessions found. Start training to see your history!
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
             </div>

             {/* Feedback Modal */}
             {selectedSession && (
                <FeedbackModal 
                    session={selectedSession} 
                    onClose={() => setSelectedSession(null)} 
                    onSave={handleUpdateFeedback}
                    isCoach={user?.role === 'coach' || user?.role === 'management'} // Management can also comment? Assuming yes or strict check.
                />
            )}
        </div>
    );
};

export default History;
