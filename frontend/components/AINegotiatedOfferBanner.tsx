"use client";

import { useEffect, useState } from 'react';
import { Sparkles, Clock, Tag, TrendingDown, ArrowRight, ShieldAlert } from 'lucide-react';
import { AINegotiatedOffer } from '@/lib/api';

interface AINegotiatedOfferBannerProps {
  offer: AINegotiatedOffer;
  onApproveCheckout?: () => void;
}

export default function AINegotiatedOfferBanner({ offer, onApproveCheckout }: AINegotiatedOfferBannerProps) {
  const [timeLeft, setTimeLeft] = useState<number>(offer.valid_seconds || 600);

  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="mt-3 p-4 bg-gradient-to-br from-indigo-950/90 via-slate-900/90 to-purple-950/90 border-2 border-indigo-500/50 rounded-2xl w-full max-w-[95%] shadow-2xl space-y-3 relative overflow-hidden">
      
      {/* Background Ambient Glow */}
      <div className="absolute -top-12 -right-12 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

      {/* Top Banner Header */}
      <div className="flex items-center justify-between border-b border-indigo-500/30 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <span className="font-extrabold text-white text-xs uppercase tracking-wider block">
              AI-Negotiated Coupon Offer
            </span>
            <span className="text-[10px] text-cyan-400 font-mono">Code: `{offer.coupon_code}`</span>
          </div>
        </div>

        {/* Live Countdown Timer */}
        <div className="flex items-center gap-1.5 bg-rose-950/80 border border-rose-500/40 text-rose-400 text-xs font-mono font-bold px-2.5 py-1 rounded-full animate-pulse">
          <Clock className="w-3.5 h-3.5" />
          <span>Valid for: {formatTimer(timeLeft)}</span>
        </div>
      </div>

      {/* AI Dynamic Reasoning Box */}
      <div className="p-2.5 bg-slate-950/80 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
        <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider block mb-1">
          💡 AI Revenue Optimization Decision:
        </span>
        <p className="italic text-slate-300">"{offer.reasoning}"</p>
      </div>

      {/* Price Comparison Grid */}
      <div className="grid grid-cols-3 gap-2 bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Original Price</span>
          <span className="text-xs text-slate-400 line-through font-mono">₹{offer.original_price.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">AI Offer Price</span>
          <span className="text-sm font-extrabold text-cyan-300 font-mono">₹{offer.offer_price.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-[10px] text-purple-300 font-bold uppercase tracking-wider block">You Save</span>
          <span className="text-xs font-bold text-emerald-400 font-mono">₹{offer.savings.toLocaleString()} ({offer.discount_percent}% OFF)</span>
        </div>
      </div>

    </div>
  );
}
