
import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const Settings = () => {
    const { user, login } = useAuth(); // Assuming login re-fetches user or we need a way to refresh context
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        height: '',
        weight: '',
        personal_best: ''
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || '',
                email: user.email || '',
                height: user.height || '',
                weight: user.weight || '',
                personal_best: user.personal_best || ''
            });
        }
    }, [user]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        setError(null);

        try {
            // Filter out empty strings to avoid validation errors if backend expects numbers
            const payload = {
                ...formData,
                height: formData.height ? parseInt(formData.height) : null,
                weight: formData.weight ? parseInt(formData.weight) : null,
            };
            
            // Remove email from payload as it's usually not updatable here or requires special verification
             delete payload.email;

            await client.put('/users/me', payload);
            setMessage('Profile updated successfully!');
            
            // Optionally refresh user context here if needed
            // For now, user might need to relogin or we rely on next fetch
             
        } catch (err) {
            console.error(err);
            setError('Failed to update profile.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6 text-gray-800">Profile Settings</h1>
            
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 max-w-2xl">
                {message && (
                    <div className="mb-4 p-4 bg-green-50 text-green-700 rounded-lg flex items-center">
                         <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                        {message}
                    </div>
                )}
                {error && (
                    <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                        <input
                            type="text"
                            name="full_name"
                            value={formData.full_name}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email (Read Only)</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            disabled
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Height (cm)</label>
                            <input
                                type="number"
                                name="height"
                                value={formData.height}
                                onChange={handleChange}
                                placeholder="e.g. 175"
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
                            <input
                                type="number"
                                name="weight"
                                value={formData.weight}
                                onChange={handleChange}
                                placeholder="e.g. 70"
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            />
                        </div>
                    </div>

                     <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Personal Best (100m)</label>
                        <input
                            type="text"
                            name="personal_best"
                            value={formData.personal_best}
                            onChange={handleChange}
                            placeholder="e.g. 10.50s"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                    </div>

                    <div className="pt-4 flex justify-end">
                        <button
                            type="submit"
                            disabled={loading}
                            className={`px-6 py-2 rounded-lg text-white font-medium transition-all ${
                                loading 
                                ? 'bg-blue-400 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30'
                            }`}
                        >
                            {loading ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Settings;
