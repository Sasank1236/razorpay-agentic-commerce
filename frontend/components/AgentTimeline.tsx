"use client";

import { useEffect, useState } from 'react';
import { Terminal, Clock, CheckCircle, Cpu, Zap } from 'lucide-react';
import { fetchAgentTimeline } from '@/lib/api';

export default function AgentTimeline() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadLogs = async () => {
    try {
      const data = await fetchAgentTimeline();
      setLogs(data);
    } catch (err) {
      console.error('Failed to load agent decision log timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 text-center text-slate-400 text-sm">
        <Cpu className="w-6 h-6 text-indigo-400 animate-spin mx-auto mb-2" />
        Loading Agent Decision Log...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-white text-lg flex items-center gap-2">
          <Terminal className="w-5 h-5 text-cyan-400" /> AI Decision Log & Execution Trace
        </h3>
        <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
          Live Audit Stream
        </span>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-4 space-y-6 pt-2">
        {logs.map((log) => (
          <div key={log.id} className="relative pl-6 group">
            {/* Timeline Dot */}
            <div className={`absolute -left-[9px] top-1.5 w-4 h-4 rounded-full border-2 border-slate-900 shadow-md ${
              log.agent_type === 'customer' ? 'bg-indigo-500 shadow-indigo-500/50' : 'bg-emerald-500 shadow-emerald-500/50'
            }`} />

            <div className="glass-card p-4 rounded-2xl border border-slate-800 group-hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                    log.agent_type === 'customer' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-emerald-500/20 text-emerald-300'
                  }`}>
                    {log.agent_type} agent
                  </span>
                  <span className="font-mono text-sm text-cyan-400 font-bold">⚡ {log.action_name}()</span>
                </div>
                <div className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                  <span className="text-emerald-400 font-mono ml-2">({log.execution_time_ms}ms)</span>
                </div>
              </div>

              {log.input_params && (
                <div className="mt-2.5 bg-slate-950/80 p-2.5 rounded-xl border border-slate-900 font-mono text-xs text-slate-300 overflow-x-auto">
                  <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">Input Parameters:</span>
                  <pre className="whitespace-pre-wrap">{JSON.stringify(log.input_params, null, 2)}</pre>
                </div>
              )}

              {log.output_summary && (
                <div className="mt-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 font-mono text-xs text-slate-300 overflow-x-auto">
                  <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">Output Summary:</span>
                  <pre className="whitespace-pre-wrap">{JSON.stringify(log.output_summary, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
