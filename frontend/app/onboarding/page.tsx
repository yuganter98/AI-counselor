'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import { GraduationCap, Target, Wallet, CheckCircle, ArrowRight, ArrowLeft, Loader2, Sparkles } from 'lucide-react';
import clsx from 'clsx';

export default function OnboardingPage() {
    const { user, refreshUser } = useAuth();
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // Form State
    const [academic, setAcademic] = useState({
        education_level: 'Undergraduate',
        major: '',
        graduation_year: 2025,
        gpa: 0.0
    });

    const [goals, setGoals] = useState({
        target_degree: 'Masters',
        field_of_study: '',
        intake_year: 2026,
        preferred_countries: [] as string[]
    });

    const [budget, setBudget] = useState({
        budget_min: 0,
        budget_max: 50000,
        funding_type: 'Self-Funded'
    });

    const [readiness, setReadiness] = useState({
        ielts_status: 'Not Taken',
        gre_status: 'Not Taken',
        sop_status: 'Not Started'
    });

    const steps = [
        { id: 1, label: 'Academic Profile', icon: <GraduationCap className="h-5 w-5" /> },
        { id: 2, label: 'Study Goals', icon: <Target className="h-5 w-5" /> },
        { id: 3, label: 'Budget & Funding', icon: <Wallet className="h-5 w-5" /> },
        { id: 4, label: 'Readiness Check', icon: <CheckCircle className="h-5 w-5" /> },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            if (step === 1) {
                await api.post('/onboarding/academic', academic);
                setStep(2);
            } else if (step === 2) {
                await api.post('/onboarding/goals', goals);
                setStep(3);
            } else if (step === 3) {
                await api.post('/onboarding/budget', budget);
                setStep(4);
            } else if (step === 4) {
                await api.post('/onboarding/readiness', readiness);
                await api.post('/onboarding/complete');
                await refreshUser();
            }
        } catch (err) {
            alert('Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;

    return (
        <div className="min-h-screen bg-white font-sans flex flex-col md:flex-row">

            {/* Sidebar / Progress */}
            <div className="md:w-1/3 min-h-[300px] md:min-h-screen bg-slate-900 text-white p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden">
                {/* Decorative Blobs */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 transform translate-x-1/3 -translate-y-1/2"></div>
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 transform -translate-x-1/3 translate-y-1/2"></div>

                <div className="relative z-10">
                    <div className="flex items-center space-x-2.5 mb-12">
                        <img src="/logo.png" alt="EduAI" className="h-10 w-10 object-contain p-1 bg-black rounded-xl border border-white/10" />
                        <span className="text-xl font-bold tracking-tight">EduAI Profile</span>
                    </div>

                    <div className="space-y-6">
                        {steps.map((s) => (
                            <div key={s.id} className={clsx("flex items-center space-x-4 transition-all duration-300", {
                                "opacity-100 translate-x-0": step === s.id,
                                "opacity-50": step !== s.id,
                                "text-green-400": step > s.id
                            })}>
                                <div className={clsx("w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all", {
                                    "border-indigo-500 bg-indigo-500 text-white": step === s.id,
                                    "border-green-500 bg-green-500 text-white": step > s.id,
                                    "border-slate-700 bg-slate-800 text-slate-400": step < s.id
                                })}>
                                    {step > s.id ? <CheckCircle className="h-5 w-5" /> : s.icon}
                                </div>
                                <div>
                                    <p className={clsx("text-sm font-bold", { "text-white": step === s.id, "text-slate-400": step !== s.id })}>
                                        {s.label}
                                    </p>
                                    {step === s.id && (
                                        <p className="text-xs text-indigo-300 mt-0.5 animate-pulse">In Progress...</p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="relative z-10 mt-12 md:mt-0 text-slate-500 text-xs">
                    Step {step} of 4 • {Math.round((step / 4) * 100)}% Completed
                </div>
            </div>

            {/* Main Form Area */}
            <div className="flex-1 bg-white p-8 lg:p-16 flex flex-col justify-center max-w-2xl mx-auto">
                <div className="mb-8">
                    <button
                        onClick={() => step > 1 && setStep(step - 1)}
                        disabled={step === 1}
                        className={clsx("flex items-center text-sm font-medium transition-colors mb-4", {
                            "text-slate-400 hover:text-indigo-600 cursor-pointer": step > 1,
                            "text-slate-200 cursor-not-allowed": step === 1
                        })}
                    >
                        <ArrowLeft className="h-4 w-4 mr-2" /> Back
                    </button>
                    <h2 className="text-3xl font-bold text-slate-900">
                        {step === 1 && "Tell us about your background."}
                        {step === 2 && "What are your study goals?"}
                        {step === 3 && "Let's plan your budget."}
                        {step === 4 && "Are you exam ready?"}
                    </h2>
                    <p className="text-slate-500 mt-2">
                        {step === 1 && "Start by adding your most recent academic qualification."}
                        {step === 2 && "This helps our AI find universities that match your ambition."}
                        {step === 3 && "We'll suggest options that fit your financial comfort zone."}
                        {step === 4 && "Don't worry if you haven't taken them yet; we'll guide you."}
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {step === 1 && (
                        <>
                            <FormInput label="Major / Stream" value={academic.major} onChange={v => setAcademic({ ...academic, major: v })} placeholder="e.g. Computer Science" />
                            <div className="grid grid-cols-2 gap-4">
                                <FormSelect label="Education Level" value={academic.education_level} onChange={v => setAcademic({ ...academic, education_level: v })} options={['Undergraduate', 'Postgraduate', 'High School']} />
                                <FormInput label="Graduation Year" type="number" value={academic.graduation_year} onChange={v => setAcademic({ ...academic, graduation_year: parseInt(v) })} />
                            </div>
                            <FormInput label="CGPA / Percentage" type="number" step="0.1" value={academic.gpa} onChange={v => setAcademic({ ...academic, gpa: parseFloat(v) })} placeholder="e.g. 3.8 or 85" />
                        </>
                    )}

                    {step === 2 && (
                        <>
                            <FormInput label="Target Degree" value={goals.target_degree} onChange={v => setGoals({ ...goals, target_degree: v })} placeholder="e.g. MS in Data Science" />
                            <FormInput label="Field of Study" value={goals.field_of_study} onChange={v => setGoals({ ...goals, field_of_study: v })} placeholder="e.g. Artificial Intelligence" />
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Preferred Countries</label>
                                <input
                                    type="text"
                                    className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-3 bg-slate-50 transition-all text-black"
                                    placeholder="USA, UK, Canadan (comma separated)"
                                    onChange={e => setGoals({ ...goals, preferred_countries: e.target.value.split(',').map(s => s.trim()) })}
                                />
                                <p className="text-xs text-slate-400">Separate multiple countries with commas.</p>
                            </div>
                        </>
                    )}

                    {step === 3 && (
                        <>
                            <FormInput label="Max Budget (USD / Year)" type="number" value={budget.budget_max} onChange={v => setBudget({ ...budget, budget_max: parseInt(v) })} placeholder="e.g. 40000" />
                            <FormSelect label="Funding Type" value={budget.funding_type} onChange={v => setBudget({ ...budget, funding_type: v })} options={['Self-Funded', 'Loan', 'Scholarship Required']} />
                        </>
                    )}

                    {step === 4 && (
                        <>
                            <div className="grid grid-cols-2 gap-6">
                                <FormSelect label="IELTS / TOEFL" value={readiness.ielts_status} onChange={v => setReadiness({ ...readiness, ielts_status: v })} options={['Not Taken', 'Prepared', 'Taken']} />
                                <FormSelect label="GRE / GMAT" value={readiness.gre_status} onChange={v => setReadiness({ ...readiness, gre_status: v })} options={['Not Taken', 'Prepared', 'Taken']} />
                            </div>
                            <FormSelect label="SOP Status" value={readiness.sop_status} onChange={v => setReadiness({ ...readiness, sop_status: v })} options={['Not Started', 'Drafting', 'Reviewed', 'Finalized']} />
                        </>
                    )}

                    <div className="pt-6">
                        <button
                            type="submit"
                            disabled={loading}
                            className={clsx("w-full flex justify-center items-center py-4 px-6 rounded-xl shadow-lg text-sm font-bold text-white transition-all hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed", {
                                "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200": step < 4,
                                "bg-green-600 hover:bg-green-700 shadow-green-200": step === 4
                            })}
                        >
                            {loading ? <Loader2 className="animate-spin h-5 w-5" /> : (
                                <>
                                    {step === 4 ? "Complete Profile" : "Save & Continue"}
                                    {step < 4 && <ArrowRight className="ml-2 h-4 w-4" />}
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// Reusable Components
function FormInput({ label, type = "text", value, onChange, placeholder, step }: any) {
    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">{label}</label>
            <input
                type={type}
                step={step}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                required
                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-3 bg-slate-50 transition-all text-black placeholder:text-slate-400"
                placeholder={placeholder}
            />
        </div>
    );
}

function FormSelect({ label, value, onChange, options }: any) {
    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">{label}</label>
            <div className="relative">
                <select
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-3 bg-slate-50 transition-all text-black appearance-none cursor-pointer"
                >
                    {options.map((opt: string) => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-slate-500">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
            </div>
        </div>
    );
}
