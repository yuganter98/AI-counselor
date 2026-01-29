'use client';

import { useState } from 'react';
import api from '@/lib/api';
import { Loader2, Sparkles, ArrowRight, Bot, MessageSquare } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import clsx from 'clsx';

interface Action {
    type: string;
    label: string;
    payload: any;
}

interface AIResponse {
    message: string;
    actions: Action[];
    next_suggestion: string;
}

export default function AICounsellor() {
    const { refreshUser } = useAuth();
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState<AIResponse | null>(null);
    const [actionLoading, setActionLoading] = useState(false);

    const handleConsult = async () => {
        setLoading(true);
        setResponse(null);
        try {
            const { data } = await api.post('/ai/counsellor', { message: "Consult" });
            setResponse(data);
        } catch (error) {
            console.error("AI Error", error);
        } finally {
            setLoading(false);
        }
    };

    const executeAction = async (action: Action) => {
        if (!confirm(`Confirm Action: ${action.label}?`)) return;

        console.log("Executing Action:", action);
        setActionLoading(true);
        try {
            console.log("Sending API Request...");
            const res = await api.post('/ai/action/execute', {
                action_type: action.type,
                payload: action.payload
            });
            console.log("API Success:", res.data);

            if (action.type === 'TRANSITION') {
                console.log("Reloading...");
                await refreshUser();
                window.location.reload();
            } else {
                handleConsult();
            }

        } catch (error) {
            console.error("Execute Error", error);
            alert('Failed to execute action. Check console.');
        } finally {
            setActionLoading(false);
        }
    };

    return (
        <div className="glass-panel rounded-2xl overflow-hidden flex flex-col h-[500px] transition-all hover:shadow-lg">
            {/* Header */}
            <div className="gradient-bg p-5 text-white flex justify-between items-center shadow-md">
                <div className="flex items-center space-x-3">
                    <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
                        <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-lg leading-none">AI Counsellor</h3>
                        <span className="text-xs text-blue-100 opacity-80">Always active</span>
                    </div>
                </div>
                {!response && !loading && (
                    <button
                        onClick={handleConsult}
                        className="text-xs bg-white text-indigo-600 px-4 py-2 rounded-full font-bold hover:bg-indigo-50 transition shadow-sm animate-pulse-soft"
                    >
                        Start Session
                    </button>
                )}
            </div>

            {/* Content Area */}
            <div className="flex-1 p-6 overflow-y-auto flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm">
                {loading ? (
                    <div className="text-center">
                        <div className="relative">
                            <div className="absolute inset-0 bg-indigo-500 blur-xl opacity-20 animate-pulse"></div>
                            <Loader2 className="h-10 w-10 animate-spin text-indigo-600 relative z-10 mx-auto mb-3" />
                        </div>
                        <span className="text-sm font-medium text-indigo-800 animate-pulse">Analyzing your profile...</span>
                    </div>
                ) : response ? (
                    <div className="w-full space-y-5">
                        {/* Messages */}
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                                <Sparkles className="h-4 w-4 text-white" />
                            </div>
                            <div className="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-indigo-50 text-sm text-gray-700 leading-relaxed">
                                {response.message}
                            </div>
                        </div>

                        {/* Actions */}
                        {response.actions.length > 0 && (
                            <div className="pl-11 space-y-3">
                                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Recommended Actions</p>
                                {response.actions.map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => executeAction(action)}
                                        disabled={actionLoading}
                                        className="w-full flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:border-indigo-300 hover:shadow-md transition-all group relative overflow-hidden"
                                    >
                                        <div className="absolute inset-0 bg-indigo-50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                        <div className="flex items-center space-x-3 relative z-10">
                                            <div className="h-8 w-8 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600">
                                                {action.type === 'TRANSITION' ? <ArrowRight className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
                                            </div>
                                            <span className="text-sm font-semibold text-gray-700">{action.label}</span>
                                        </div>
                                        <ArrowRight className="h-4 w-4 text-indigo-400 opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all relative z-10" />
                                    </button>
                                ))}
                            </div>
                        )}

                        {!response.actions.length && (
                            <div className="text-center text-xs text-gray-400 mt-4 italic">
                                "Waiting for your next move..."
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-center space-y-4 max-w-xs">
                        <div className="w-16 h-16 rounded-2xl gradient-bg mx-auto flex items-center justify-center shadow-lg transform rotate-3 hover:rotate-6 transition-transform">
                            <Sparkles className="h-8 w-8 text-white" />
                        </div>
                        <h4 className="text-lg font-bold text-gray-800">Ready to assist</h4>
                        <p className="text-sm text-gray-500">I can analyze your profile, suggest universities, and guide you through applications.</p>
                        <button onClick={handleConsult} className="text-indigo-600 font-semibold text-sm hover:underline">
                            Click to start
                        </button>
                    </div>
                )}
            </div>

            {/* Footer */}
            {response && (
                <div className="p-3 bg-indigo-50/80 border-t border-indigo-100 text-xs flex justify-between items-center backdrop-blur-sm">
                    <span className="text-indigo-800 font-medium truncate flex-1 mr-2">
                        💡 Tip: {response.next_suggestion}
                    </span>
                    <button onClick={handleConsult} className="text-indigo-600 hover:text-indigo-800 font-bold whitespace-nowrap">
                        Refresh
                    </button>
                </div>
            )}
        </div>
    );
}
