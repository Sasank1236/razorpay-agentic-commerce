"use client";

import { Brain, Heart, ShieldAlert, Sparkles, Target } from 'lucide-react';
import { CustomerMemoryProfile } from '@/lib/api';

interface CustomerMemoryBadgeProps {
  memory: CustomerMemoryProfile;
}

export default function CustomerMemoryBadge({ memory }: CustomerMemoryBadgeProps) {
  if (!memory) return null;

  return (
    <div className="mt-2.5 p-3.5 bg-gradient-to-r from-purple-950/80 via-slate-900/90 to-indigo-950/80 border border-purple-500/40 rounded-2xl w-full max-w-[95%] shadow-xl space-y-2.5">
      {/* Badge Header */}
      <div className="flex items-center justify-between border-b border-purple-500/20 pb-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300">
            <Brain className="w-3.5 h-3.5 text-purple-300" />
          </div>
          <span className="font-extrabold text-white text-xs uppercase tracking-wider">
            Customer Memory Active
          </span>
        </div>
        <span className="text-[10px] text-purple-400 bg-purple-900/40 px-2 py-0.5 rounded-full font-mono border border-purple-500/30">
          Persistent Memory
        </span>
      </div>

      {/* Memory Summary Text */}
      <p className="text-xs text-slate-300 italic leading-relaxed">
        "{memory.memory_summary || 'Prefers Sony, avoids bulky designs, prioritizes microphone & travel.'}"
      </p>

      {/* Structured Preference Tags */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1">
        {/* Preferred Brands */}
        {memory.preferred_brands && memory.preferred_brands.map((brand, i) => (
          <span key={i} className="inline-flex items-center gap-1 text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded-full">
            <Heart className="w-2.5 h-2.5 text-indigo-400 fill-indigo-400" /> Brand: {brand}
          </span>
        ))}

        {/* Avoid Traits */}
        {memory.avoid_traits && memory.avoid_traits.map((trait, i) => (
          <span key={i} className="inline-flex items-center gap-1 text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 px-2 py-0.5 rounded-full">
            <ShieldAlert className="w-2.5 h-2.5 text-rose-400" /> Avoid: {trait}
          </span>
        ))}

        {/* Primary Use Cases */}
        {memory.primary_use_cases && memory.primary_use_cases.map((useCase, i) => (
          <span key={i} className="inline-flex items-center gap-1 text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 px-2 py-0.5 rounded-full">
            <Target className="w-2.5 h-2.5 text-cyan-400" /> {useCase}
          </span>
        ))}
      </div>
    </div>
  );
}
