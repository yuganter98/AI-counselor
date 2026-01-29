'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';
import { ArrowLeft, Loader2, Sparkles } from 'lucide-react';

export default function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const { data } = await api.post('/auth/login', { email, password });
            login(data.access_token, data.user);
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Login failed';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
            {/* Left: Branding & Visuals */}
            <div className="hidden lg:flex flex-col justify-between p-12 bg-slate-900 relative overflow-hidden text-white">
                <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 transform translate-x-1/2 -translate-y-1/2"></div>
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 transform -translate-x-1/2 translate-y-1/2"></div>

                <div className="relative z-10">
                    <div className="flex items-center space-x-2.5">
                        <div className="bg-white/10 p-2 rounded-xl backdrop-blur-sm border border-white/10">
                            <Sparkles className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-2xl font-bold tracking-tight">EduAI</span>
                    </div>
                </div>

                <div className="relative z-10 max-w-lg">
                    <h1 className="text-5xl font-bold mb-6 leading-tight">
                        Your personal AI counsellor is waiting.
                    </h1>
                    <p className="text-lg text-slate-400 leading-relaxed">
                        Log in to continue your profile analysis, university shortlisting, and task management.
                    </p>
                </div>

                <div className="relative z-10 text-sm text-slate-500">
                    © 2026 EduAI Platform
                </div>
            </div>

            {/* Right: Login Form */}
            <div className="flex flex-col justify-center items-center p-8 sm:p-12 lg:p-24 bg-white relative">
                <Link href="/" className="absolute top-8 left-8 text-slate-400 hover:text-indigo-600 flex items-center gap-2 text-sm font-medium transition-colors z-50">
                    <ArrowLeft className="h-4 w-4" /> Back to Home
                </Link>

                <div className="w-full max-w-sm space-y-8">
                    <div className="text-center">
                        <h2 className="text-3xl font-bold tracking-tight text-slate-900">Welcome back</h2>
                        <p className="mt-2 text-sm text-slate-500">
                            Don't have an account?{' '}
                            <Link href="/signup" className="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors">
                                Sign up for free
                            </Link>
                        </p>
                    </div>

                    {error && (
                        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm border border-red-100 flex items-center">
                            <span className="w-1.5 h-1.5 bg-red-500 rounded-full mr-2"></span>
                            {error}
                        </div>
                    )}

                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Email address</label>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-3 bg-slate-50 transition-all text-black"
                                placeholder="name@example.com"
                            />
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <label className="text-sm font-medium text-slate-700">Password</label>
                                <a href="#" className="text-xs font-medium text-indigo-600 hover:text-indigo-500">Forgot password?</a>
                            </div>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-3 bg-slate-50 transition-all text-black"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg shadow-indigo-200 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="animate-spin h-5 w-5" /> : "Sign in to Dashboard"}
                        </button>
                    </form>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-slate-100"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-white text-slate-400">Secure & Private</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
