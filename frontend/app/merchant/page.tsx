"use client";

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import GrowthInsightsCard from '@/components/GrowthInsightsCard';
import CartRecoveryCard from '@/components/CartRecoveryCard';
import { fetchMerchantGrowth, fetchRevenueTrends, MerchantGrowthResponse } from '@/lib/api';
import { TrendingUp, ShoppingBag, DollarSign, Users, AlertOctagon, Sparkles, Zap, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function MerchantPage() {
  const [data, setData] = useState<MerchantGrowthResponse | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadMerchantData = async () => {
    try {
      const growth = await fetchMerchantGrowth();
      const tr = await fetchRevenueTrends();
      setData(growth);
      setTrends(tr);
    } catch (err) {
      console.error("Failed to load merchant growth data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMerchantData();
  }, []);

  return (
    <div className="min-h-screen bg-[#060919]">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <span className="text-xs text-emerald-400 font-bold uppercase tracking-widest bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full inline-flex items-center gap-1.5 mb-2">
              <TrendingUp className="w-3.5 h-3.5" /> Merchant Growth Control Center
            </span>
            <h1 className="text-3xl font-extrabold text-white">Commerce Analytics & AI Growth Agent</h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-1">
              Autonomous AI agent analyzing shopper search intent, conversion bottlenecks, and abandoned cart recovery.
            </p>
          </div>

          <button
            onClick={loadMerchantData}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-md transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" /> Refresh Insights
          </button>
        </div>

        {/* Executive KPI Cards */}
        {data && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <div className="glass-card p-5 rounded-2xl border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 text-xs">
                <span>Total Store Revenue</span>
                <DollarSign className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mt-2">
                ₹{data.metrics_summary.total_revenue.toLocaleString()}
              </div>
              <div className="text-[11px] text-emerald-400 font-semibold mt-1">
                +14.2% vs last week
              </div>
            </div>

            <div className="glass-card p-5 rounded-2xl border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 text-xs">
                <span>Store Conversion Rate</span>
                <Users className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mt-2">
                {data.metrics_summary.conversion_rate}%
              </div>
              <div className="text-[11px] text-cyan-400 font-semibold mt-1">
                Industry avg: 14.5%
              </div>
            </div>

            <div className="glass-card p-5 rounded-2xl border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 text-xs">
                <span>AI-Assisted Sales</span>
                <Sparkles className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mt-2">
                ₹{data.metrics_summary.ai_assisted_sales.toLocaleString()}
              </div>
              <div className="text-[11px] text-purple-400 font-semibold mt-1">
                42% of total store sales
              </div>
            </div>

            <div className="glass-card p-5 rounded-2xl border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 text-xs">
                <span>Abandoned Carts Revenue at Risk</span>
                <AlertOctagon className="w-4 h-4 text-rose-400" />
              </div>
              <div className="text-2xl font-extrabold text-rose-400 mt-2">
                ₹{data.metrics_summary.abandoned_revenue_at_risk.toLocaleString()}
              </div>
              <div className="text-[11px] text-rose-400 font-semibold mt-1">
                {data.metrics_summary.abandoned_carts_count} high-intent carts
              </div>
            </div>

          </div>
        )}

        {/* Revenue Trend Chart & AI Growth Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Revenue Chart */}
          <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-base">Store Revenue & AI-Assisted Sales Trend</h3>
                <p className="text-xs text-slate-400">Daily performance Breakdown (INR)</p>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-indigo-500" /> Total Sales
                </span>
                <span className="flex items-center gap-1 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-cyan-400" /> AI Sales
                </span>
              </div>
            </div>

            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorAI" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00d2ff" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#00d2ff" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `₹${val/1000}k`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                    formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, '']}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" name="Total Sales" />
                  <Area type="monotone" dataKey="ai_revenue" stroke="#00d2ff" strokeWidth={3} fillOpacity={1} fill="url(#colorAI)" name="AI Sales" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* AI Growth Insights Feed */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyan-400" /> AI Merchant Growth Agent
              </h3>
              <span className="text-[10px] text-cyan-400 font-bold bg-cyan-400/10 px-2 py-0.5 rounded-full border border-cyan-400/30">
                Actionable Feed
              </span>
            </div>

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((n) => (
                  <div key={n} className="glass-card h-40 rounded-2xl animate-pulse bg-slate-900/50" />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {data?.insights.map((insight, idx) => {
                  if (insight.title.includes("Cart Recovery")) {
                    return (
                      <CartRecoveryCard
                        key={idx}
                        insight={insight}
                        onCampaignActivated={loadMerchantData}
                      />
                    );
                  }
                  return (
                    <GrowthInsightsCard
                      key={idx}
                      insight={insight}
                      onCampaignExecuted={loadMerchantData}
                    />
                  );
                })}
              </div>
            )}
          </div>

        </div>

      </main>
    </div>
  );
}
