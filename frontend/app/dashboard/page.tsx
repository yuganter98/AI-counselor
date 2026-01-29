'use client';

import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import { useEffect, useState } from 'react';
import { CheckCircle, AlertTriangle, XCircle, Loader2, Lock, LayoutDashboard, LogOut, GraduationCap, MapPin, BookOpen } from 'lucide-react';
import AICounsellor from '@/components/AICounsellor';
import clsx from 'clsx';

interface StrengthComponent {
    label: string;
    value: string;
    status: 'success' | 'warning' | 'error';
}

interface ProfileStrength {
    label: string;
    reason: string;
    components: {
        academics: StrengthComponent;
        exams: StrengthComponent;
        sop: StrengthComponent;
    };
}

interface Task {
    id: number;
    title: string;
    description: string;
    status: 'PENDING' | 'DONE';
    university_id?: number;
    university_name?: string;
}

export default function DashboardPage() {
    const { user, logout } = useAuth();
    const [strength, setStrength] = useState<ProfileStrength | null>(null);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const endpoints = [api.get('/dashboard/strength')];
            if (user?.current_stage === 'APPLICATION') {
                endpoints.push(api.get('/application/tasks'));
            } else {
                endpoints.push(api.get('/dashboard/tasks'));
            }

            const [strengthRes, tasksRes] = await Promise.all(endpoints);
            setStrength(strengthRes.data);
            setTasks(tasksRes.data);
        } catch (error) {
            console.error("Failed to fetch dashboard data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user?.profile_completed) {
            fetchData();
        }
    }, [user]);

    const handleCompleteTask = async (taskId: number) => {
        try {
            await api.post(`/dashboard/tasks/${taskId}/complete`);
            setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: 'DONE' } : t));
        } catch (error) {
            console.error("Failed to complete task", error);
        }
    };

    if (!user || !user.profile_completed) return null;

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center bg-gray-50"><Loader2 className="animate-spin h-10 w-10 text-indigo-600" /></div>;
    }

    return (
        <div className="min-h-screen bg-gray-50 text-slate-800 font-sans pb-10">
            {/* Navbar */}
            <nav className="sticky top-0 z-50 glass-panel border-b-0 border-b-white/20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center space-x-2">
                            <img src="/logo.png" alt="EduAI" className="h-10 w-10 object-contain" />
                            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">EduAI</span>
                        </div>
                        <div className="flex items-center space-x-6">
                            <div className="flex flex-col items-end hidden sm:flex">
                                <span className="text-sm font-bold text-slate-700">{user.name}</span>
                                <div className="flex items-center space-x-1">
                                    <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                                    <span className="text-xs text-indigo-600 font-semibold uppercase tracking-wider">{user.current_stage}</span>
                                </div>
                            </div>
                            <button onClick={logout} className="p-2 rounded-full hover:bg-slate-100 transition-colors text-slate-500 hover:text-red-600">
                                <LogOut className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">

                {/* Greeting / Hero */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">
                            Welcome back, <span className="text-indigo-600">{user.name.split(' ')[0]}</span> 👋
                        </h1>
                        <p className="text-slate-500 mt-1">Let's continue your journey to your dream university.</p>
                    </div>

                </div>

                {/* Top Section: Strength & AI */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Left: Strength & Focus */}
                    <div className="lg:col-span-2 space-y-8">

                        {/* 1. Strength Card */}
                        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <LayoutDashboard className="h-32 w-32 text-indigo-400 transform rotate-12" />
                            </div>

                            <div className="flex justify-between items-start mb-6 relative z-10">
                                <div>
                                    <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                        Profile Analysis
                                    </h2>
                                    <p className="text-sm text-slate-500 mt-1 max-w-md">{strength?.reason}</p>
                                </div>
                                <div className={clsx("px-4 py-2 rounded-xl text-sm font-bold border shadow-sm", {
                                    "bg-green-50 text-green-700 border-green-200": strength?.label === 'STRONG',
                                    "bg-yellow-50 text-yellow-700 border-yellow-200": strength?.label === 'AVERAGE',
                                    "bg-red-50 text-red-700 border-red-200": strength?.label === 'WEAK',
                                })}>
                                    {strength?.label}
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 relative z-10">
                                {Object.entries(strength?.components || {}).map(([key, comp]) => (
                                    <div key={key} className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-white/50 shadow-sm hover:shadow-md transition-shadow">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="capitalize text-xs font-bold text-slate-400 tracking-wider">{key}</span>
                                            {comp.status === 'success' && <CheckCircle className="h-4 w-4 text-green-500" />}
                                            {comp.status === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                                            {comp.status === 'error' && <XCircle className="h-4 w-4 text-red-500" />}
                                        </div>
                                        <div className="text-lg font-bold text-slate-800">{comp.value}</div>
                                        <div className={clsx("text-xs mt-1 font-semibold", {
                                            "text-green-600": comp.status === 'success',
                                            "text-yellow-600": comp.status === 'warning',
                                            "text-red-600": comp.status === 'error',
                                        })}>
                                            {comp.label}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* 2. Tasks Section */}
                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-xl font-bold text-slate-800">Your Action Plan</h3>
                                {user.current_stage === 'APPLICATION' && (
                                    <span className="bg-indigo-100 text-indigo-700 text-xs px-3 py-1 rounded-full font-bold">Applications Active</span>
                                )}
                            </div>
                            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                                {tasks.length === 0 ? (
                                    <div className="p-10 text-center text-slate-400 flex flex-col items-center">
                                        <CheckCircle className="h-10 w-10 mb-3 text-slate-200" />
                                        <p>All caught up! Use the AI Counsellor to see what's next.</p>
                                    </div>
                                ) : (
                                    <div className="divide-y divide-slate-50">
                                        {user.current_stage === 'APPLICATION' ? (
                                            <ApplicationTaskGroup tasks={tasks} onComplete={handleCompleteTask} />
                                        ) : (
                                            tasks.map(task => (
                                                <TaskItem key={task.id} task={task} onComplete={handleCompleteTask} />
                                            ))
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Shortlist Section (Conditional) */}
                        {['DISCOVERY', 'FINALIZE', 'APPLICATION'].includes(user.current_stage) && (
                            <ShortlistSection
                                stage={user.current_stage}
                                api={api}
                                onRefresh={fetchData}
                            />
                        )}

                    </div>

                    {/* Right: AI & Focus */}
                    <div className="space-y-6">
                        {/* Current Focus Card */}
                        <div className="gradient-bg rounded-2xl shadow-xl text-white p-6 relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-4 opacity-10">
                                <MapPin className="h-24 w-24 text-white transform rotate-12" />
                            </div>
                            <div className="relative z-10">
                                <h3 className="text-lg font-bold mb-1 opacity-90">Current Focus</h3>
                                <div className="text-2xl font-bold mb-4">{user.current_stage}</div>
                                <div className="bg-white/10 backdrop-blur-md rounded-lg p-3 border border-white/20">
                                    <div className="text-3xl font-bold">{tasks.filter(t => t.status === 'PENDING').length}</div>
                                    <div className="text-indigo-100 text-xs font-medium uppercase tracking-wide">Pending Actions</div>
                                </div>
                            </div>
                        </div>

                        {/* AI Counsellor */}
                        <AICounsellor />
                    </div>
                </div>
            </main>
        </div >
    );
}

// Helper Components
function TaskItem({ task, onComplete }: { task: Task, onComplete: (id: number) => void }) {
    return (
        <div className={clsx("p-5 flex items-start group transition-all hover:bg-indigo-50/30", { "opacity-60 grayscale": task.status === 'DONE' })}>
            <button
                onClick={() => onComplete(task.id)}
                disabled={task.status === 'DONE'}
                className={clsx("mt-1 h-6 w-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mr-4 transition-all", {
                    "border-slate-300 hover:border-indigo-500 group-hover:scale-110": task.status === 'PENDING',
                    "bg-green-500 border-green-500 text-white": task.status === 'DONE'
                })}
            >
                {task.status === 'DONE' && <CheckCircle className="h-4 w-4" />}
            </button>
            <div className="flex-1">
                <h4 className={clsx("font-semibold text-sm transition-colors", {
                    "text-slate-800 group-hover:text-indigo-700": task.status === 'PENDING',
                    "text-slate-500 line-through": task.status === 'DONE'
                })}>
                    {task.title}
                </h4>
                <p className="text-sm text-slate-500 mt-1 leading-relaxed">{task.description}</p>
            </div>
            {task.status === 'PENDING' && (
                <button
                    onClick={() => onComplete(task.id)}
                    className="opacity-0 group-hover:opacity-100 text-xs font-bold text-indigo-600 px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 transition-all translate-x-2 group-hover:translate-x-0"
                >
                    Complete
                </button>
            )}
        </div>
    );
}

function ApplicationTaskGroup({ tasks, onComplete }: { tasks: Task[], onComplete: (id: number) => void }) {
    const grouped: Record<string, Task[]> = {};
    tasks.forEach(t => {
        const key = t.university_name || "General Application Tasks";
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(t);
    });

    return (
        <div className="divide-y divide-slate-100">
            {Object.entries(grouped).map(([uniName, uniTasks]) => (
                <div key={uniName} className="p-0">
                    <div className="bg-slate-50 px-6 py-3 flex items-center gap-2">
                        <BookOpen className="h-4 w-4 text-slate-400" />
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{uniName}</span>
                    </div>
                    {uniTasks.map(task => (
                        <TaskItem key={task.id} task={task} onComplete={onComplete} />
                    ))}
                </div>
            ))}
        </div>
    );
}

function ShortlistSection({ stage, api, onRefresh }: { stage: string, api: any, onRefresh: () => void }) {
    const [shortlists, setShortlists] = useState<any[]>([]);
    const [canProceed, setCanProceed] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const { data } = await api.get('/finalize/status');
                setShortlists(data.shortlists);
                setCanProceed(data.can_proceed);
            } catch (err) {
                console.error("Fetch shortlist failed", err);
            } finally {
                setLoading(false);
            }
        };
        fetchStatus();
    }, [stage]);

    const handleLock = async (id: number) => {
        if (!confirm("Lock this university? This is a commitment.")) return;
        try {
            await api.post('/finalize/lock', { university_id: id });
            window.location.reload();
        } catch (e) { alert("Failed to lock"); }
    };

    const handleUnlock = async (id: number) => {
        if (!confirm("Unlock this university? You will lose application progress.")) return;
        try {
            await api.post('/finalize/unlock', { university_id: id });
            window.location.reload();
        } catch (e) { alert("Failed to unlock"); }
    };

    if (loading) return null;

    return (
        <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-slate-800">Your Universities</h3>
                {canProceed && stage === 'FINALIZE' && (
                    <button
                        onClick={async () => {
                            if (!confirm("Start Application Phase? This will generate specific tasks for locked universities.")) return;
                            try {
                                await api.post('/application/start');
                                window.location.reload();
                            } catch (e) { alert("Error starting application"); }
                        }}
                        className="text-sm bg-green-500 text-white px-5 py-2 rounded-full font-bold hover:bg-green-600 transition shadow-lg animate-pulse"
                    >
                        START APPLICATIONS →
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {shortlists.length === 0 ? (
                    <div className="col-span-2 p-6 border-2 border-dashed border-slate-200 rounded-xl flex items-center justify-center text-slate-400">
                        No universities shortlisted yet. Ask the AI Counsellor!
                    </div>
                ) : (
                    shortlists.map((s: any) => (
                        <div key={s.university_id} className={clsx("p-5 rounded-xl border transition-all relative group bg-white", {
                            "border-yellow-400 shadow-lg ring-1 ring-yellow-400/50": s.locked,
                            "border-slate-100 hover:border-indigo-200 hover:shadow-md": !s.locked
                        })}>
                            {s.locked && <div className="absolute top-3 right-3 bg-yellow-100 text-yellow-700 p-1.5 rounded-full"><Lock className="h-4 w-4" /></div>}

                            <h4 className="font-bold text-slate-800 text-lg">{s.university_name}</h4>
                            <div className="flex items-center gap-2 mt-1 mb-4">
                                <span className="text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-600">{s.country}</span>
                                <span className={clsx("text-xs px-2 py-0.5 rounded font-bold", {
                                    "bg-purple-100 text-purple-700": s.category === 'DREAM',
                                    "bg-blue-100 text-blue-700": s.category === 'TARGET',
                                    "bg-green-100 text-green-700": s.category === 'SAFE',
                                })}>{s.category}</span>
                            </div>

                            {stage === 'FINALIZE' && (
                                <div className="mt-3">
                                    {!s.locked ? (
                                        <button onClick={() => handleLock(s.university_id)} className="w-full py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-black transition shadow-md">
                                            Lock Choice
                                        </button>
                                    ) : (
                                        <button onClick={() => handleUnlock(s.university_id)} className="w-full py-2 border border-red-200 text-red-500 rounded-lg text-sm font-semibold hover:bg-red-50 transition">
                                            Unlock
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
