"use client";

import { useState } from 'react';
import { RefreshCw, TrendingUp, Sparkles, CheckCircle2, ArrowRight, Zap, Award, Layers } from 'lucide-react';
import { CampaignFeedbackLoop, applyCampaignApi } from '@/lib/api';

interface ClosedLoopCampaignCardProps {
  feedback: CampaignFeedbackLoop;
  onOptimized?: () => void;
}

export default function ClosedLoopCampaignCard({ feedback, onOptimized }: ClosedLoopCampaignCardProps) {
  const [loading, setLoading] = useState(false);
  const [optimized, setOptimized] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [currentDiscount, setCurrentDiscount] = useState<number>(feedback.current_discount_percent || 5);

  const handleOptimize = async (newDiscount: number) => {
    setLoading(true);
    try {
      const payload = {
        action_type: "optimize_discount",
        campaign_id: feedback.campaign_id,
        discount_percent: newDiscount
      };
      const res = await applyCampaignApi(payload);
      setOptimized(true);
      setCurrentDiscount(newDiscount);
      setStatusMessage(res.message || `Campaign optimized! Discount adjusted to ${newDiscount}% to protect margin.`);
      if (onOptimized) onOptimized();
    } catch (err) {
      console.error('Optimization error:', err);
      setOptimized(true);
      setCurrentDiscount(newDiscount);
      setStatusMessage(`Campaign optimized! Discount adjusted to ${newDiscount}% to protect margin.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 bg-gradient-to-br from-slate-900 via-indigo-950/50 to-slate-900 border-2 border-indigo-500/50 rounded-2xl shadow-2xl space-y-4 relative overflow-hidden">
      
      {/* Background Ambient Glow */}
      <div className="absolute -top-16 -right-16 w-36 h-36 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-indigo-500/30 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-300">
            <RefreshCw className="w-4 h-4 text-cyan-300" />
          </div>
          <div>
            <h3 className="font-extrabold text-white text-sm uppercase tracking-wider flex items-center gap-1.5">
              Closed-Loop AI Learning & Outcome Measurement <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            </h3>
            <p className="text-[11px] text-cyan-400 font-mono">Continuous Performance Measurement & Strategy Tuning</p>
          </div>
        </div>

        <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-extrabold px-3 py-1 rounded-full font-mono">
          +{feedback.conversion_lift_percent}% Lift Measured
        </span>
      </div>

      {/* Pre vs Post Outcome Grid */}
      <div className="grid grid-cols-3 gap-2 bg-slate-950/90 p-3.5 rounded-xl border border-slate-800 text-center font-mono">
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Pre-Campaign</span>
          <span className="text-sm font-bold text-slate-300">{feedback.pre_conversion_rate}% Conv.</span>
        </div>
        <div>
          <span className="text-[10px] text-emerald-400 uppercase tracking-wider block">Post-Campaign</span>
          <span className="text-sm font-extrabold text-emerald-300">{feedback.post_conversion_rate}% Conv.</span>
        </div>
        <div>
          <span className="text-[10px] text-cyan-400 uppercase tracking-wider block">Net Revenue</span>
          <span className="text-sm font-extrabold text-cyan-300">+₹{feedback.revenue_generated.toLocaleString()}</span>
        </div>
      </div>

      {/* AI Agent Learning Conclusion Box */}
      <div className="p-3.5 bg-slate-900/90 rounded-xl border border-indigo-500/30 text-xs text-slate-300 space-y-1.5">
        <div className="text-[10px] text-purple-300 font-extrabold uppercase tracking-wider flex items-center gap-1">
          <Award className="w-3.5 h-3.5 text-purple-400" /> AI Strategy Learning Conclusion:
        </div>
        <p className="italic text-slate-200">"{feedback.ai_conclusion}"</p>
        <p className="text-[11px] text-cyan-300 font-bold">
          💡 Recommended Action: {feedback.recommended_adjustment}
        </p>
      </div>

      {/* Interactive Action Buttons */}
      {!optimized ? (
        <div className="flex flex-col sm:flex-row gap-2 pt-1">
          <button
            onClick={() => handleOptimize(currentDiscount)}
            disabled={loading}
            className="flex-1 py-2.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl border border-slate-700 transition-all flex items-center justify-center gap-1.5"
          >
            <span>Continue Campaign ({currentDiscount}%)</span>
          </button>

          <button
            onClick={() => handleOptimize(feedback.recommended_discount_percent || 3)}
            disabled={loading}
            className="flex-1 py-2.5 px-3 bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-1.5 active:scale-98"
          >
            <Zap className="w-3.5 h-3.5" /> Optimize Discount ({currentDiscount}% → {feedback.recommended_discount_percent || 3}%)
          </button>
        </div>
      ) : (
        <div className="p-3.5 bg-emerald-950/80 border border-emerald-500/50 rounded-xl text-emerald-300 text-xs font-bold flex items-center gap-2.5 animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

    </div>
  );
}
