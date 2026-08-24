"use client";

import { useState } from 'react';
import { TrendingUp, AlertTriangle, Zap, CheckCircle2, ArrowUpRight } from 'lucide-react';
import { MerchantGrowthInsight, applyCampaignApi } from '@/lib/api';

interface GrowthInsightsCardProps {
  insight: MerchantGrowthInsight;
  onCampaignExecuted?: () => void;
}

export default function GrowthInsightsCard({ insight, onCampaignExecuted }: GrowthInsightsCardProps) {
  const [applied, setApplied] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleApply = async () => {
    setLoading(true);
    try {
      await applyCampaignApi(insight.campaign_payload);
      setApplied(true);
      if (onCampaignExecuted) onCampaignExecuted();
    } catch (err) {
      console.error('Failed to execute growth campaign:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-5 rounded-2xl border border-indigo-500/20 hover:border-indigo-500/50 relative overflow-hidden transition-all">
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-bl-full pointer-events-none" />

      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Zap className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h4 className="font-bold text-white text-base">{insight.title}</h4>
            <span className="text-[11px] text-amber-400 font-semibold bg-amber-400/10 px-2 py-0.5 rounded-full inline-block mt-0.5">
              {insight.metric_highlight}
            </span>
          </div>
        </div>
      </div>

      <p className="text-xs text-slate-300 mt-3 leading-relaxed">
        {insight.description}
      </p>

      <div className="mt-3 p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-2 text-xs text-emerald-400 font-semibold">
        <ArrowUpRight className="w-4 h-4 shrink-0" />
        <span>{insight.impact_estimate}</span>
      </div>

      {/* Action Button */}
      <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
        <span className="text-[11px] text-slate-400 font-medium">{insight.recommended_action}</span>

        {applied ? (
          <span className="text-xs text-emerald-400 font-bold bg-emerald-500/20 px-3 py-1.5 rounded-xl border border-emerald-500/40 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" /> Campaign Active
          </span>
        ) : (
          <button
            onClick={handleApply}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs rounded-xl shadow-md shadow-indigo-600/20 transition-all flex items-center gap-1.5 active:scale-95 disabled:opacity-50"
          >
            {loading ? 'Activating...' : 'Apply Recommendation'}
          </button>
        )}
      </div>

    </div>
  );
}
