'use client';

import Link from "next/link";
import { ArrowRight, Terminal, Crosshair, Maximize, Shield, Cpu, Activity, ChevronRight } from "lucide-react";
import { useState, useEffect } from "react";

export default function Home() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="min-h-screen bg-black text-white font-mono selection:bg-green-500 selection:text-black overflow-x-hidden">

      {/* Tech Grid Background */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-20"
        style={{ backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      {/* Navbar */}
      <nav className="fixed w-full z-50 top-0 border-b border-white/20 bg-black/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <img src="/logo.png" alt="Nano Banana" className="h-8 w-8 object-contain" />
            <span className="font-bold tracking-widest text-lg">EDU_AI_SYSTEM</span>
          </div>
          <div className="flex items-center space-x-8 text-xs tracking-widest uppercase">
            <Link href="/login" className="hover:text-green-500 transition-colors">Login</Link>
            <Link href="/signup" className="border border-white hover:bg-white hover:text-black px-6 py-2 transition-all">
              Initialize Protocol
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 max-w-7xl mx-auto z-10 border-l border-r border-white/5 min-h-[90vh] flex flex-col justify-center">

        <div className="mb-6 flex items-center space-x-2 text-green-500 text-xs tracking-[0.2em] uppercase">
          <Terminal className="h-4 w-4" />
          <span>System Status: Online</span>
        </div>

        <h1 className="text-5xl md:text-8xl font-black tracking-tighter mb-8 leading-none uppercase">
          Optimized <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-gray-500">Pathways</span> <br />
          <span className="text-green-500">Engaged.</span>
        </h1>

        <p className="text-lg text-gray-400 max-w-2xl mb-12 font-sans leading-relaxed border-l-2 border-green-500 pl-6">
          Execute your university application strategy with algorithmic precision.
          Reject ambiguity. Embrace data-driven success.
        </p>

        <div className="flex flex-col sm:flex-row gap-0 sm:gap-6 w-full sm:w-auto">
          <Link href="/signup" className="group relative px-8 py-5 bg-white text-black font-bold text-lg overflow-hidden flex items-center justify-center hover:bg-green-500 transition-colors">
            START DIAGNOSTIC
            <ArrowRight className="ml-3 h-5 w-5 group-hover:translate-x-2 transition-transform" />
          </Link>
          <div className="hidden sm:flex items-center space-x-4 px-6 opacity-50">
            <Activity className="h-5 w-5" />
            <span className="text-xs uppercase tracking-widest">Latency: 12ms</span>
          </div>
        </div>
      </section>

      {/* Marquee Stripe */}
      <div className="border-y border-white/20 bg-white/5 py-4 overflow-hidden relative">
        <div className="flex space-x-12 animate-marquee whitespace-nowrap text-xs uppercase tracking-[0.3em] text-gray-300">
          <span>/// PROFILE ANALYSIS ACTIVE</span>
          <span>/// DEADLINE ENFORCER ONLINE</span>
          <span>/// UNIVERSITY DATABASE MAPPED</span>
          <span>/// ACTION STEPS GENERATED</span>
          <span>/// PROFILE ANALYSIS ACTIVE</span>
          <span>/// DEADLINE ENFORCER ONLINE</span>
          <span>/// UNIVERSITY DATABASE MAPPED</span>
          <span>/// ACTION STEPS GENERATED</span>
        </div>
      </div>

      {/* Features Grid */}
      <section className="py-0 border-b border-white/10">
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/10 max-w-7xl mx-auto border-x border-white/10">

          {/* F1 */}
          <div className="p-12 hover:bg-white/5 transition-colors group">
            <Cpu className="h-10 w-10 text-white mb-6 group-hover:text-green-500 transition-colors" />
            <h3 className="text-xl font-bold uppercase mb-4 tracking-wider">Logic Core</h3>
            <p className="text-gray-400 text-sm font-sans leading-relaxed">
              Our AI doesn't chat. It calculates. It scans your profile variables and computes the optimal path to acceptance.
            </p>
          </div>

          {/* F2 */}
          <div className="p-12 hover:bg-white/5 transition-colors group">
            <Shield className="h-10 w-10 text-white mb-6 group-hover:text-green-500 transition-colors" />
            <h3 className="text-xl font-bold uppercase mb-4 tracking-wider">Gateway Lock</h3>
            <p className="text-gray-400 text-sm font-sans leading-relaxed">
              Strict state management. You cannot proceed to applications until your profile meets the required strength threshold.
            </p>
          </div>

          {/* F3 */}
          <div className="p-12 hover:bg-white/5 transition-colors group">
            <Crosshair className="h-10 w-10 text-white mb-6 group-hover:text-green-500 transition-colors" />
            <h3 className="text-xl font-bold uppercase mb-4 tracking-wider">Target Aquisition</h3>
            <p className="text-gray-400 text-sm font-sans leading-relaxed">
              Shortlist logic filters noise. Lock your targets and generate a specific execution plan for each university.
            </p>
          </div>

        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 bg-black text-center border-t border-white/10">
        <div className="mb-4">
          <span className="text-2xl font-black tracking-widest">EDU_AI</span>
        </div>
        <p className="text-gray-600 text-xs uppercase tracking-widest max-w-md mx-auto leading-loose">
          System Architecture v1.0 <br />
          Designed for High-Performance Applicants.
        </p>
      </footer>
    </div>
  );
}
