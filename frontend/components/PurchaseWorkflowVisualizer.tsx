"use client";

import { CheckCircle2, Circle, Sparkles, Loader2, Tag, ShieldAlert, Cpu } from 'lucide-react';
import { WorkflowStep } from '@/lib/api';

interface PurchaseWorkflowVisualizerProps {
  steps: WorkflowStep[];
  couponApplied?: string;
  originalAmount?: number;
  discountAmount?: number;
  finalAmount?: number;
}

export default function PurchaseWorkflowVisualizer({
  steps,
  couponApplied,
  originalAmount,
  discountAmount,
  finalAmount,
}: PurchaseWorkflowVisualizerProps) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="mt-3 p-3.5 bg-slate-950/90 border border-indigo-500/30 rounded-2xl w-full max-w-[95%] shadow-xl space-y-3">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
          <Cpu className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>Autonomous Purchase Agent Pipeline</span>
        </div>
        <span className="text-[10px] bg-indigo-500/20 text-indigo-300 font-mono px-2 py-0.5 rounded-full border border-indigo-500/40">
          11 Steps Automated
        </span>
      </div>

      {/* Steps List */}
      <div className="space-y-2">
        {steps.map((step) => {
          const isCompleted = step.status === 'completed';
          const isInProgress = step.status === 'in_progress';

          return (
            <div key={step.step_number} className="flex items-start gap-2.5 text-xs">
              
              {/* Step Icon */}
              <div className="mt-0.5 shrink-0">
                {isCompleted ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : isInProgress ? (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-600" />
                )}
              </div>

              {/* Step Text & Detail */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className={`font-semibold ${isCompleted ? 'text-slate-200' : isInProgress ? 'text-cyan-300 font-bold' : 'text-slate-500'}`}>
                    Step {step.step_number}: {step.step_name}
                  </span>
                  {step.execution_time_ms > 0 && (
                    <span className="text-[10px] text-slate-500 font-mono">{step.execution_time_ms}ms</span>
                  )}
                </div>
                {step.detail_message && (
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    {step.detail_message}
                  </p>
                )}
              </div>

            </div>
          );
        })}
      </div>

      {/* Coupon & Discount Highlight Banner */}
      {couponApplied && discountAmount && (
        <div className="mt-3 p-2.5 bg-emerald-950/60 border border-emerald-500/40 rounded-xl flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold">
            <Tag className="w-4 h-4 text-emerald-400" />
            <span>Coupon `{couponApplied}` Applied!</span>
          </div>
          <div className="text-emerald-300 font-extrabold font-mono">
            Saved ₹{discountAmount.toLocaleString()}
          </div>
        </div>
      )}

      {/* Net Payable Breakdown */}
      {originalAmount && finalAmount && (
        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400">Net Calculated Total:</span>
          <div className="flex items-baseline gap-2">
            <span className="text-slate-500 line-through text-[11px]">₹{originalAmount.toLocaleString()}</span>
            <span className="text-cyan-300 font-extrabold text-sm">₹{finalAmount.toLocaleString()}</span>
          </div>
        </div>
      )}

    </div>
  );
}
