import React, { useState, useRef } from 'react';

const Comparison = () => {
    const [videoA, setVideoA] = useState(null);
    const [videoB, setVideoB] = useState(null);
    const videoARef = useRef(null);
    const videoBRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const handleFileChange = (e, setVideo) => {
        const file = e.target.files[0];
        if (file) {
            setVideo(URL.createObjectURL(file));
        }
    };

    const togglePlay = () => {
        if (isPlaying) {
            videoARef.current?.pause();
            videoBRef.current?.pause();
        } else {
            videoARef.current?.play();
            videoBRef.current?.play();
        }
        setIsPlaying(!isPlaying);
    };

    const reset = () => {
        if (videoARef.current) videoARef.current.currentTime = 0;
        if (videoBRef.current) videoBRef.current.currentTime = 0;
        if (!isPlaying) togglePlay(); 
        setIsPlaying(false);
    };

    return (
        <div className="max-w-[1600px] mx-auto space-y-6 animate-fade-in font-sans">
            <div className="flex justify-between items-end mb-4 border-b border-gray-200 pb-4">
                 <div>
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Comparison Mode</h1>
                    <p className="text-sm text-gray-500">Side-by-side Video Analysis</p>
                </div>
            </div>

            {/* Controls */}
            <div className="flex justify-center gap-4 py-2">
                <button 
                    onClick={togglePlay} 
                    className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all shadow-md shadow-blue-500/20 active:scale-95 text-sm font-semibold"
                >
                    {isPlaying ? (
                        <>
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            <span>Pause All</span>
                        </>
                    ) : (
                         <>
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            <span>Play All</span>
                        </>
                    )}
                </button>
                <button 
                    onClick={reset} 
                    className="flex items-center gap-2 px-6 py-2.5 text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl transition-all text-sm font-semibold"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                    <span>Reset</span>
                </button>
            </div>

            {/* Video Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Video A */}
                <div className="space-y-3">
                    <div className="flex justify-between items-center">
                         <span className="text-xs font-bold text-blue-600 uppercase tracking-widest border-b-2 border-blue-600 pb-1">Video A (You)</span>
                         <input type="file" accept="video/*" onChange={(e) => handleFileChange(e, setVideoA)} className="text-xs text-gray-500 file:mr-2 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors" />
                    </div>
                    <div className="bg-black rounded-2xl overflow-hidden shadow-sm relative ring-1 ring-gray-200 aspect-video group">
                        {videoA ? (
                            <video ref={videoARef} src={videoA} className="w-full h-full object-contain" controls />
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 opacity-50">
                                <svg className="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                                <span className="text-sm font-medium">Select a Video</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Video B */}
                <div className="space-y-3">
                     <div className="flex justify-between items-center">
                         <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest border-b-2 border-emerald-600 pb-1">Video B (Reference)</span>
                         <input type="file" accept="video/*" onChange={(e) => handleFileChange(e, setVideoB)} className="text-xs text-gray-500 file:mr-2 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 transition-colors" />
                    </div>
                    <div className="bg-black rounded-2xl overflow-hidden shadow-sm relative ring-1 ring-gray-200 aspect-video group">
                         {videoB ? (
                            <video ref={videoBRef} src={videoB} className="w-full h-full object-contain" controls />
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 opacity-50">
                                <svg className="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                                <span className="text-sm font-medium">Select a Video</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Comparison;
