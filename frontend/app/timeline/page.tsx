"use client";

import Navbar from '@/components/Navbar';
import AgentTimeline from '@/components/AgentTimeline';
import { Terminal, ShieldCheck } from 'lucide-react';

export default function TimelinePage() {
  return (
    <div className="min-h-screen bg-[#060919]">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Header */}
        <div>
          <span className="text-xs text-purple-400 font-bold uppercase tracking-widest bg-purple-500/10 border border-purple-500/30 px-3 py-1 rounded-full inline-flex items-center gap-1.5 mb-2">
            <Terminal className="w-3.5 h-3.5" /> Full Auditability & Transparency
          </span>
          <h1 className="text-3xl font-extrabold text-white">AI Decision Log Timeline</h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Real-time step-by-step trace of every tool execution, candidate scoring matrix, cart staging event, and Razorpay signature verification.
          </p>
        </div>

        {/* Timeline Component */}
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800">
          <AgentTimeline />
        </div>

      </main>
    </div>
  );
}
