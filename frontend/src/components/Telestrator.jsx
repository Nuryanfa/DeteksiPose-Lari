import React, { useRef, useState, useEffect } from 'react';

const Telestrator = ({ width, height, active }) => {
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);
    
    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            canvas.width = width || 640;
            canvas.height = height || 480;
            const ctx = canvas.getContext('2d');
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.lineWidth = 4;
            ctx.strokeStyle = '#facc15'; // Yellow
        }
    }, [width, height]);

    const startDrawing = (e) => {
        if (!active) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();
        const x = e.nativeEvent.offsetX;
        const y = e.nativeEvent.offsetY;
        
        ctx.beginPath();
        ctx.moveTo(x, y);
        setIsDrawing(true);
    };

    const draw = (e) => {
        if (!isDrawing || !active) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const x = e.nativeEvent.offsetX;
        const y = e.nativeEvent.offsetY;
        
        ctx.lineTo(x, y);
        ctx.stroke();
    };

    const stopDrawing = () => {
        if (!isDrawing) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.closePath();
        setIsDrawing(false);
    };

    const clearCanvas = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    return (
        <div className={`absolute inset-0 z-20 ${active ? 'pointer-events-auto' : 'pointer-events-none'}`}>
             {active && (
                <div className="absolute top-2 right-2 flex gap-2">
                    <button onClick={clearCanvas} className="bg-red-500 text-white text-xs px-2 py-1 rounded shadow hover:bg-red-600">Clear</button>
                </div>
            )}
            <canvas
                ref={canvasRef}
                className="w-full h-full cursor-crosshair"
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseOut={stopDrawing}
            />
        </div>
    );
};

export default Telestrator;
