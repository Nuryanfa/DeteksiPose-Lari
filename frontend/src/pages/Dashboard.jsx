import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
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
import ThreeDView from '../components/ThreeDView';
import Skeleton from '../components/Skeleton';
import OnboardingTour from '../components/OnboardingTour';
import Telestrator from '../components/Telestrator';
import ErrorBoundary from '../components/ErrorBoundary';
import Sidebar from '../components/Sidebar';
import SmartTimeline from '../components/SmartTimeline';
import ControlBar from '../components/ControlBar';
import { generatePDF } from '../utils/pdfGenerator';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [sourceType, setSourceType] = useState('0'); 
    const [customCameraId, setCustomCameraId] = useState('1'); 
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [streamUrl, setStreamUrl] = useState('');
    const [ytUrl, setYtUrl] = useState('');
    
    // Vis State
    const [show3D, setShow3D] = useState(false);
    const [isTelestratorActive, setIsTelestratorActive] = useState(false);
    const videoContainerRef = useRef(null);
    const statsInterval = useRef(null);

    // Errors for timeline
    const [timelineErrors, setTimelineErrors] = useState([]);

    const startStream = () => {
        let finalSource = '0'; 
        if (sourceType === '0') finalSource = '0';
        else if (sourceType === 'custom') finalSource = customCameraId;
        else if(sourceType === 'youtube') finalSource = ytUrl;
        else if (sourceType === 'file' && file) {
             handleFileUpload();
             return; 
        }
        
        setIsStreaming(true);
        setIsPaused(false);
        setTimelineErrors([]); // Reset errors
        setStreamUrl(`http://localhost:8000/api/v1/stream/video_feed?source=${encodeURIComponent(finalSource)}`);
        statsInterval.current = setInterval(fetchStats, 200);
    };

    const stopStream = async () => {
        setIsStreaming(false);
        setIsPaused(false);
        setStreamUrl('');
        if (statsInterval.current) clearInterval(statsInterval.current);
        try { await client.post('/stream/stop'); } catch (e) {}
    };
    
    const pauseStream = async () => {
        setIsPaused(true);
        try { await client.post('/stream/pause'); } catch (e) {}
    };

    const resumeStream = async () => {
        setIsPaused(false);
        try { await client.post('/stream/resume'); } catch (e) {}
    };

    const restartStream = async () => {
        try { await client.post('/stream/restart'); } catch (e) {}
    };

    const fetchStats = async () => {
        try {
            const res = await client.get('/stream/stats');
            setStats(res.data);
            
            // Collect errors for timeline
            if (res.data?.feedback && res.data.feedback.length > 0) {
                 // Check if new error (naively by count for now, smarter diffing later)
                 // Just adding a marker every time we get '⚠️' for demo
                 const hasWarning = res.data.feedback.some(msg => msg.includes('⚠️'));
                 if (hasWarning) {
                     setTimelineErrors(prev => [...prev, { 
                         timestamp: res.data.duration_seconds || Date.now(), // Fallback
                         type: 'Warning' 
                     }]);
                 }
            }
        } catch (error) {}
    };

    const handleFileUpload = async () => {
        if (!file) return;
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await client.post('/upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const filePath = res.data.filepath;
            setSourceType('file'); 
            setIsStreaming(true);
            setStreamUrl(`http://localhost:8000/api/v1/stream/video_feed?source=${encodeURIComponent(filePath)}`);
            statsInterval.current = setInterval(fetchStats, 200);
        } catch (error) { alert('Upload failed'); } 
        finally { setUploading(false); }
    };
    
    const exportCsv = async () => {
        try {
            const res = await client.post('/stream/export_csv');
            const url = "http://localhost:8000" + res.data.download_url;
            window.open(url, '_blank');
        } catch (error) { alert('Error exporting CSV'); }
    };

    const [toast, setToast] = useState(null); // { message, type: 'success'|'error' }

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    const saveSession = async () => {
         if (!stats) {
             showToast("No data to save!", 'error');
             return;
         }
         try {
             // Create payload matching SessionCreate schema
            const payload = {
                duration_seconds: stats.duration_seconds || 0,
                // Map API 'score' to schema 'technique_score'
                technique_score: stats.score || 0,
                avg_cadence: stats.cadence || 0,
                avg_stride_length: stats.stride_length || 0,
                avg_gct: stats.gct || 0,
                max_swing_error: 0, 
                max_hip_error: 0, 
                video_path: sourceType === 'file' ? streamUrl : null
            };
            
            await client.post('/history/save', payload);
            showToast('Session Saved Successfully!', 'success');
        } catch (error) { 
            console.error(error);
            showToast('Save Failed', 'error'); 
        }
    };

    // Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e) => {
            // Ignore if typing in input/textarea
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

            switch(e.code) {
                case 'Space':
                    e.preventDefault(); // Prevent scroll
                    if (isStreaming) {
                        if (isPaused) resumeStream();
                        else pauseStream();
                    }
                    break;
                case 'KeyD':
                    setIsTelestratorActive(prev => !prev);
                    break;
                case 'Digit3':
                    setShow3D(prev => !prev);
                    break;
                case 'KeyR':
                     if (isStreaming) restartStream();
                     break;
                default:
                    break;
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isStreaming, isPaused]);

    // Chart Options (Clinical Style)
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        elements: {
            line: { tension: 0.3, borderWidth: 1.5 }, // Slightly smoother, thinner lines
            point: { radius: 0, hitRadius: 10 } // Clean look, but interactive
        },
        plugins: {
            legend: { display: true, position: 'top', align: 'end', labels: { boxWidth: 10, usePointStyle: true } },
            title: { display: false },
        },
        scales: {
            y: {
                min: 0, max: 180,
                grid: { display: true, color: '#f3f4f6' }, // Very light grid
                border: { display: false }
            },
            x: {
                grid: { display: false },
                ticks: { display: false } // Hide time labels for cleanliness
            }
        },
        animation: { duration: 0 },
    };

    const chartData = {
        labels: stats?.graph_data?.labels || [],
        datasets: [
            {
                label: 'R. Knee',
                data: stats?.graph_data?.knee || [],
                borderColor: '#2563EB', // Clinical Blue
                backgroundColor: 'transparent',
                borderWidth: 1.5,
                tension: 0.3,
                pointRadius: 0
            },
            {
                label: 'R. Hip',
                data: stats?.graph_data?.hip || [],
                borderColor: '#EF4444', // Clinical Red
                backgroundColor: 'transparent',
                borderWidth: 1.5,
                tension: 0.3,
                pointRadius: 0
            }
        ],
    };

    // Helper for GCT Color
    const getGctColor = (status) => {
        if (status === 'Good') return 'text-emerald-600 bg-white border-l-4 border-l-emerald-500 shadow-sm';
        if (status === 'Fair') return 'text-amber-600 bg-white border-l-4 border-l-amber-500 shadow-sm';
        return 'text-red-600 bg-white border-l-4 border-l-red-500 shadow-sm';
    };

    return (
        <div className="max-w-[1600px] mx-auto space-y-6 animate-fade-in font-sans relative">
            <OnboardingTour />
            {/* Toast Notification */}
            {toast && (
                <div className={`fixed top-6 right-6 z-50 px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 transform transition-all duration-300 animate-slide-in ${
                    toast.type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
                }`}>
                    <div className="bg-white/20 p-1 rounded-full">
                        {toast.type === 'error' ? (
                             <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                        ) : (
                             <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" /></svg>
                        )}
                    </div>
                    <div>
                        <h4 className="font-bold text-sm">{toast.type === 'error' ? 'Error' : 'Success'}</h4>
                        <p className="text-xs opacity-90">{toast.message}</p>
                    </div>
                </div>
            )}
            
            {/* Header Area */}
            <div className="flex justify-between items-end mb-4 border-b border-gray-200 pb-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Dashboard</h1>
                    <p className="text-sm text-gray-500">Real-time Biomechanical Analysis</p>
                </div>
                <div className="flex gap-4">
                     {/* Source Selectors in Header */}
                     <select 
                        className="text-sm border-gray-200 rounded-lg bg-white px-3 py-2 focus:ring-2 focus:ring-blue-500/20"
                        value={sourceType}
                        onChange={(e) => setSourceType(e.target.value)}
                        disabled={isStreaming}
                    >
                        <option value="0">Default Webcam</option>
                        <option value="custom">External Camera</option>
                        <option value="file">Upload Video</option>
                        <option value="youtube">YouTube URL</option>
                    </select>
                    {sourceType === 'custom' && (
                        <input 
                            type="number" 
                            className="text-sm border-gray-200 rounded-lg px-3 w-24" 
                            placeholder="Cam ID"
                            value={customCameraId}
                            onChange={(e) => setCustomCameraId(e.target.value)}
                            disabled={isStreaming}
                            min="0"
                            max="5"
                        />
                    )}
                    {sourceType === 'youtube' && (
                        <input 
                            type="text" 
                            className="text-sm border-gray-200 rounded-lg px-3 w-64"
                            placeholder="Paste YouTube URL..."
                            value={ytUrl}
                            onChange={(e) => setYtUrl(e.target.value)}
                            disabled={isStreaming}
                        />
                    )}
                     {sourceType === 'file' && (
                        <input type="file" className="text-sm w-48 text-gray-500" onChange={(e) => setFile(e.target.files[0])} disabled={isStreaming} />
                    )}
                     {sourceType === 'custom' && (
                          <input type="text" className="text-sm border-gray-200 rounded-lg px-3 w-20" placeholder="ID" value={customCameraId} onChange={(e) => setCustomCameraId(e.target.value)} disabled={isStreaming} />
                     )}
                </div>
            </div>

            {/* Main Grid: 70% Video, 30% Data */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                
                {/* Left Column: Video & Controls (Col-span-8) */}
                <div className="lg:col-span-8 space-y-4">
                    
                    {/* Video Container - Aspect Ratio Locked */}
                    <div className="bg-black rounded-2xl overflow-hidden shadow-sm relative ring-1 ring-gray-200 aspect-video group w-full mx-auto">
                         {/* 3D Overlay */}
                        {show3D && (
                            <div className="absolute top-4 right-4 w-48 h-64 bg-black/50 backdrop-blur-sm rounded-xl border border-white/10 z-20 pointer-events-none">
                                <ThreeDView landmarks={stats?.biomechanics?.world_landmarks} />
                            </div>
                        )}

                        {/* Title Overlay */}
                        <div className="absolute top-0 left-0 p-4 w-full bg-gradient-to-b from-black/60 to-transparent z-10 flex justify-between items-start pointer-events-none">
                            <span className="text-white/80 text-xs font-mono tracking-wider uppercase">Live Feed</span>
                            {isStreaming && <span className="flex h-2 w-2 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)] animate-pulse"></span>}
                        </div>

                         <div ref={videoContainerRef} className="w-full h-full relative flex items-center justify-center">
                             <Telestrator 
                                width={videoContainerRef.current?.clientWidth} 
                                height={videoContainerRef.current?.clientHeight} 
                                active={isTelestratorActive} 
                            />
                            {isStreaming ? (
                                <img src={streamUrl} alt="Stream" className="w-full h-full object-contain" />
                            ) : (
                                <div className="text-gray-600 flex flex-col items-center opacity-50">
                                    <svg className="w-16 h-16 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                                    <span className="text-sm font-medium">No Signal</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Smart Timeline */}
                    <SmartTimeline 
                        isStreaming={isStreaming} 
                        duration={stats?.duration_seconds || 60} 
                        currentTime={stats?.duration_seconds || 0} // Using same for now as placeholder 
                        errors={timelineErrors}
                    />

                    {/* Control Bar */}
                    <ControlBar
                        isStreaming={isStreaming}
                        isPaused={isPaused}
                        onStart={startStream}
                        onPause={pauseStream}
                        onResume={resumeStream}
                        onStop={stopStream}
                        onRestart={restartStream}
                        isLoading={uploading}
                    />
                    
                    {/* Footer Actions */}
            <div className="flex justify-between items-center border-t border-gray-200 pt-6 mt-8">
                <div className="flex items-center gap-2">
                    <input type="checkbox" id="show3d" checked={show3D} onChange={(e) => setShow3D(e.target.checked)} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    <label htmlFor="show3d" className="text-sm text-gray-600 font-medium">Show 3D Skeleton (Hotkey: 3)</label>
                </div>
                 <div className="flex items-center gap-2">
                    <input type="checkbox" id="enableDrawing" checked={isTelestratorActive} onChange={(e) => setIsTelestratorActive(e.target.checked)} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    <label htmlFor="enableDrawing" className="text-sm text-gray-600 font-medium">Enable Drawing (Hotkey: D)</label>
                </div>

                <div className="flex gap-4">
                     <button onClick={exportCsv} className="text-sm font-bold text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-4 py-2 rounded-lg transition-colors uppercase tracking-wide flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                        Download CSV
                    </button>
                    <button 
                        onClick={() => generatePDF(stats, user)} 
                        className="text-sm font-bold text-gray-700 hover:text-gray-900 hover:bg-gray-100 px-4 py-2 rounded-lg transition-colors uppercase tracking-wide flex items-center gap-2 border border-gray-200"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                        Export Report
                    </button>
                    <button onClick={saveSession} className="text-sm font-bold text-gray-400 hover:text-gray-600 px-4 py-2 rounded-lg transition-colors uppercase tracking-wide">
                        Save Session
                    </button>
                </div>
            </div>          {/* Kinematics Graph */}
                    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm h-64">
                         <div className="flex justify-between items-center mb-2">
                            <h3 className="text-xs font-bold text-gray-500 uppercase">Real-time Kinematics</h3>
                             {isStreaming && <span className="flex h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>}
                        </div>
                        {chartData.labels.length > 0 ? ( // Check if there's actual data to display
                            <div className="h-full w-full pb-6">
                                <Line options={chartOptions} data={chartData} />
                            </div>
                        ) : (
                            <div className="h-full w-full flex flex-col gap-2">
                                <Skeleton className="h-4 w-1/3 mb-4" />
                                <div className="flex-1 flex gap-2 items-end pb-2">
                                     <Skeleton className="h-32 w-full rounded-t-lg" />
                                     <Skeleton className="h-20 w-full rounded-t-lg" />
                                     <Skeleton className="h-40 w-full rounded-t-lg" />
                                     <Skeleton className="h-28 w-full rounded-t-lg" />
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column: Data Panel (Col-span-4) */}
                <div className="lg:col-span-4 space-y-6">
                    
                    {/* Score Card */}
                    <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm text-center relative overflow-hidden">
                        <h3 className="text-sm font-extrabold text-gray-700 uppercase tracking-widest mb-4">Technique Score</h3>
                        <div className="relative inline-block w-40 h-40">
                             {/* Thin Modern Gauge */}
                            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                                <path className="text-gray-100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="1" />
                                <path className={`${stats?.score >= 80 ? 'text-emerald-500' : stats?.score >= 60 ? 'text-blue-500' : 'text-amber-500'} transition-all duration-1000 ease-out drop-shadow-md`} style={{ strokeDasharray: `${stats?.score || 0}, 100` }} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                             <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                                <span className="text-5xl font-light text-gray-900 block font-mono tracking-tighter">{stats?.score || 0}</span>
                                <span className="text-[10px] text-gray-400 font-medium">/ 100</span>
                            </div>
                        </div>
                        
                        <div className="mt-4 grid grid-cols-2 divide-x divide-gray-100 border-t border-gray-100 pt-4">
                             <div>
                                 <p className="text-[10px] text-gray-400 uppercase">Avg Score</p>
                                 <p className="text-lg font-bold text-gray-700">72</p>
                             </div>
                             <div>
                                 <p className="text-[10px] text-gray-400 uppercase">Target</p>
                                 <p className="text-lg font-bold text-blue-600">&gt; 80</p>
                             </div>
                        </div>
                    </div>

                    {/* Key Metrics Compact Grid */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white p-4 rounded-xl border border-gray-200">
                             <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Cadence</p>
                             <p className="text-2xl font-light text-gray-900 font-mono">{stats?.cadence || 0} <span className="text-xs text-gray-400 font-sans">spm</span></p>
                        </div>
                        <div className={`p-4 rounded-xl border ${getGctColor(stats?.gct_status)}`}>
                             <p className="text-[10px] font-bold opacity-60 uppercase mb-1">GCT</p>
                             <p className="text-2xl font-light font-mono">{stats?.gct || 0} <span className="text-xs opacity-60 font-sans">ms</span></p>
                        </div>
                    </div>

                    {/* AI Alerts (New Card Style) */}
                    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col h-[320px]">
                        <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                            <h3 className="font-bold text-xs text-gray-700 uppercase flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span> Coach Insights
                            </h3>
                             <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold">{stats?.feedback?.length || 0}</span>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
                             {stats?.feedback && stats.feedback.length > 0 ? (
                                stats.feedback.map((msg, idx) => {
                                    const isPositive = msg.includes('✅');
                                    const isWarning = msg.includes('⚠️'); // Assuming warning sign used
                                    let borderClass = 'border-l-4 border-l-blue-500';
                                    let bgClass = 'bg-white';
                                    
                                    if(isPositive) borderClass = 'border-l-4 border-l-emerald-500';
                                    if(isWarning) borderClass = 'border-l-4 border-l-amber-500';

                                    return (
                                        <div key={idx} className={`p-3 rounded-lg border border-gray-100 shadow-sm text-sm text-gray-600 ${borderClass} ${bgClass} hover:bg-gray-50 transition-colors`}>
                                            {msg.replace(/✅|⚠️/g, '').trim()}
                                        </div>
                                    )
                                })
                            ) : (
                                <div className="p-4 space-y-3">
                                    <div className="flex gap-2">
                                        <Skeleton className="h-10 w-10 !rounded-full shrink-0" />
                                        <div className="flex-1 space-y-2">
                                            <Skeleton className="h-4 w-3/4" />
                                            <Skeleton className="h-4 w-1/2" />
                                        </div>
                                    </div>
                                    <div className="flex gap-2 opacity-50">
                                        <Skeleton className="h-10 w-10 !rounded-full shrink-0" />
                                        <div className="flex-1 space-y-2">
                                            <Skeleton className="h-4 w-full" />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
