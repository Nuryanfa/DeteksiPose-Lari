import React, { useState, useEffect } from 'react';

const TOUR_STEPS = [
    {
        title: "Welcome to SSTS Pro! 🚀",
        content: "Your advanced biomechanics analysis dashboard. Let's get you set up in 3 easy steps.",
        image: null
    },
    {
        title: "1. Connect Your Camera 📷",
        content: "Select 'Webcam' for live analysis or 'Upload File' to analyze pre-recorded videos. Use the input field for DroidCam/External IDs.",
        highlight: "camera-controls"
    },
    {
        title: "2. Analyze & Correct 🏃‍♂️",
        content: "Watch the 'Real-time Kinematics' graph and 'Coach Insights' for instant feedback on your form.",
        highlight: "stats-panel"
    },
    {
        title: "3. Track Progress 📈",
        content: "Don't forget to click 'Save Session' after your workout to track your Technique Score history.",
        highlight: "save-btn"
    }
];

const OnboardingTour = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        // Check if user has seen tour
        const hasSeenTour = localStorage.getItem('ssts_tour_completed');
        if (!hasSeenTour) {
            setIsOpen(true);
        }
    }, []);

    const handleNext = () => {
        if (currentStep < TOUR_STEPS.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            handleClose();
        }
    };

    const handleClose = () => {
        setIsOpen(false);
        localStorage.setItem('ssts_tour_completed', 'true');
    };

    if (!isOpen) return null;

    const step = TOUR_STEPS[currentStep];

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden transform transition-all scale-100">
                {/* Header Image or Gradient */}
                <div className="h-32 bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-full opacity-20 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]"></div>
                    <svg className="w-16 h-16 text-white/90 drop-shadow-lg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>

                <div className="p-8">
                    <div className="flex justify-between items-start mb-4">
                        <h2 className="text-xl font-bold text-gray-800">{step.title}</h2>
                        <span className="text-xs font-semibold px-2 py-1 bg-gray-100 rounded-lg text-gray-500">
                            {currentStep + 1} / {TOUR_STEPS.length}
                        </span>
                    </div>
                    
                    <p className="text-gray-600 mb-8 leading-relaxed">
                        {step.content}
                    </p>

                    <div className="flex justify-between items-center">
                        <button 
                            onClick={handleClose}
                            className="text-sm font-medium text-gray-400 hover:text-gray-600 px-4 py-2"
                        >
                            Skip Tour
                        </button>

                        <button 
                            onClick={handleNext}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-semibold shadow-lg shadow-blue-500/30 transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
                        >
                            {currentStep === TOUR_STEPS.length - 1 ? 'Get Started' : 'Next Step'}
                            {currentStep !== TOUR_STEPS.length - 1 && (
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>
                
                {/* Progress Bar */}
                <div className="h-1.5 w-full bg-gray-100">
                    <div 
                        className="h-full bg-blue-600 transition-all duration-300" 
                        style={{ width: `${((currentStep + 1) / TOUR_STEPS.length) * 100}%` }}
                    ></div>
                </div>
            </div>
        </div>
    );
};

export default OnboardingTour;
