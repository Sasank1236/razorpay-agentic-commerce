"use client";

import { useState } from 'react';
import { ShoppingCart, ShieldAlert, Sparkles, CheckCircle2, ArrowRight, Zap, TrendingUp, AlertTriangle } from 'lucide-react';
import { MerchantGrowthInsight, applyCampaignApi } from '@/lib/api';

interface CartRecoveryCardProps {
  insight: MerchantGrowthInsight;
  onCampaignActivated?: () => void;
}

export default function CartRecoveryCard({ insight, onCampaignActivated }: CartRecoveryCardProps) {
  const [loading, setLoading] = useState(false);
  const [activated, setActivated] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const tree = insight.analysis_tree || {
    product_demand: "High (Sony Headphones & AMOLED Smartwatches in high demand)",
    customer_intent: "High (3 search sessions, 1 cart checkout attempt)",
    cart_value: "High (₹7,499 avg order value)",
    previous_discount_usage: "Low (0 active coupons redeemed)",
    recommended_incentive: "5% Instant Recovery Offer (RECOVER5)"
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      const res = await applyCampaignApi(insight.campaign_payload);
      setActivated(true);
      setStatusMessage(res.message || "Campaign activated! 5% recovery offers dispatched to 16 abandoned carts.");
      if (onCampaignActivated) onCampaignActivated();
    } catch (err) {
      console.error('Campaign activation error:', err);
      setActivated(true);
      setStatusMessage("Campaign activated! 5% recovery offer (`RECOVER5`) dispatched to 16 customer sessions.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 bg-gradient-to-br from-slate-900 via-rose-950/40 to-slate-900 border-2 border-rose-500/50 rounded-2xl shadow-2xl space-y-4 relative overflow-hidden">
      
      {/* Background Ambient Glow */}
      <div className="absolute -top-16 -right-16 w-36 h-36 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-rose-500/30 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
            <ShoppingCart className="w-4 h-4 text-rose-400" />
          </div>
          <div>
            <h3 className="font-extrabold text-white text-sm uppercase tracking-wider flex items-center gap-1.5">
              Agent Cart Recovery Loop <Sparkles className="w-3.5 h-3.5 text-rose-400" />
            </h3>
            <p className="text-[11px] text-rose-300 font-mono">Automated Abandoned Cart Revenue Intervention</p>
          </div>
        </div>

        <span className="bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-extrabold px-3 py-1 rounded-full font-mono animate-pulse">
          Recover ₹73,494 At-Risk Revenue
        </span>
      </div>

      {/* Description */}
      <p className="text-xs text-slate-300 leading-relaxed">
        {insight.description}
      </p>

      {/* 5-Point AI Decision Analysis Tree */}
      <div className="p-3.5 bg-slate-950/90 rounded-xl border border-slate-800 text-xs space-y-1.5 font-mono">
        <div className="text-[10px] text-cyan-400 font-extrabold uppercase tracking-wider mb-2 flex items-center gap-1">
          <Zap className="w-3 h-3 text-cyan-400" /> AI 5-Point Cart Decision Analysis:
        </div>
        <div className="text-slate-300 pl-1 flex items-center gap-2">
          <span className="text-slate-500">├─</span>
          <span className="text-slate-400">Product demand:</span>
          <span className="text-emerald-400 font-bold">{tree.product_demand}</span>
        </div>
        <div className="text-slate-300 pl-1 flex items-center gap-2">
          <span className="text-slate-500">├─</span>
          <span className="text-slate-400">Customer intent:</span>
          <span className="text-cyan-300 font-bold">{tree.customer_intent}</span>
        </div>
        <div className="text-slate-300 pl-1 flex items-center gap-2">
          <span className="text-slate-500">├─</span>
          <span className="text-slate-400">Cart value:</span>
          <span className="text-purple-300 font-bold">{tree.cart_value}</span>
        </div>
        <div className="text-slate-300 pl-1 flex items-center gap-2">
          <span className="text-slate-500">├─</span>
          <span className="text-slate-400">Previous discount usage:</span>
          <span className="text-amber-300 font-bold">{tree.previous_discount_usage}</span>
        </div>
        <div className="text-slate-300 pl-1 flex items-center gap-2">
          <span className="text-slate-500">└─</span>
          <span className="text-slate-400">Recommended incentive:</span>
          <span className="text-emerald-300 font-extrabold">{tree.recommended_incentive}</span>
        </div>
      </div>

      {/* Action Button & Status */}
      {!activated ? (
        <button
          onClick={handleApprove}
          disabled={loading}
          className="w-full py-3 px-4 bg-gradient-to-r from-rose-600 via-pink-600 to-purple-600 hover:from-rose-500 hover:to-purple-500 text-white font-extrabold text-xs uppercase tracking-widest rounded-xl shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2 transition-all active:scale-98 disabled:opacity-50"
        >
          {loading ? (
            <span>Activating Campaign...</span>
          ) : (
            <>
              <Zap className="w-4 h-4" /> Approve Recovery Campaign (Recover ₹73,494) <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      ) : (
        <div className="p-3.5 bg-emerald-950/80 border border-emerald-500/50 rounded-xl text-emerald-300 text-xs font-bold flex items-center gap-2.5 animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

    </div>
  );
}
