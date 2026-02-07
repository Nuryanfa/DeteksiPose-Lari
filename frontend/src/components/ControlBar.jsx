import React from 'react';

const ControlBar = ({ 
    isStreaming, 
    isPaused, 
    onStart, 
    onPause, 
    onResume, 
    onStop, 
    onRestart, 
    isLoading 
}) => {
    return (
        <div className="flex items-center justify-between p-2 bg-white border border-gray-200 rounded-2xl shadow-sm">
            
            {/* Primary Transport Controls */}
            <div className="flex items-center gap-2">
                {!isStreaming ? (
                    <button 
                        onClick={onStart}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all shadow-md shadow-blue-500/20 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                        ) : (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        )}
                        <span className="font-semibold text-sm">Start Analysis</span>
                    </button>
                ) : (
                    <>
                        {isPaused ? (
                            <button onClick={onResume} className="p-2.5 text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors" title="Resume">
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </button>
                        ) : (
                            <button onClick={onPause} className="p-2.5 text-amber-600 bg-amber-50 hover:bg-amber-100 rounded-xl transition-colors" title="Pause">
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </button>
                        )}
                        
                        <button onClick={onRestart} className="p-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors" title="Restart">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                        </button>

                        <button onClick={onStop} className="p-2.5 text-red-600 hover:bg-red-50 rounded-xl transition-colors" title="Stop">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
                        </button>
                    </>
                )}
            </div>

            {/* Status Indicator */}
            <div className="flex items-center gap-3 px-4">
                {isStreaming && !isPaused && (
                    <div className="flex items-center gap-2">
                        <span className="relative flex h-3 w-3">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                        </span>
                        <span className="text-xs font-bold text-red-600 uppercase tracking-wider">Live</span>
                    </div>
                )}
                {isPaused && <span className="text-xs font-bold text-amber-500 uppercase tracking-wider">Paused</span>}
                {!isStreaming && <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Ready</span>}
            </div>
        </div>
    );
};

export default ControlBar;
