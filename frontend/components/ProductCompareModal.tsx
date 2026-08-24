"use client";

import { X, Scale, Star, Check, Sparkles } from 'lucide-react';
import { Product } from '@/lib/api';

interface ProductCompareModalProps {
  isOpen: boolean;
  onClose: () => void;
  products: Product[];
}

export default function ProductCompareModal({ isOpen, onClose, products }: ProductCompareModalProps) {
  if (!isOpen || products.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-4xl rounded-3xl overflow-hidden border border-slate-700 shadow-2xl flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">AI Product Spec Comparison</h3>
              <p className="text-xs text-slate-400">Side-by-side analysis across features, pricing & AI rating</p>
            </div>
          </div>

          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Matrix Body */}
        <div className="p-6 overflow-x-auto overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {products.map((prod, idx) => (
              <div
                key={prod.id}
                className={`glass-card p-5 rounded-2xl border flex flex-col justify-between ${
                  idx === 0 ? 'ring-2 ring-indigo-500 border-indigo-500/50 bg-indigo-950/20' : 'border-slate-800'
                }`}
              >
                <div>
                  {idx === 0 && (
                    <span className="text-[10px] bg-indigo-500 text-white font-bold px-2 py-0.5 rounded-full uppercase tracking-wider mb-2 inline-flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> Top AI Recommendation
                    </span>
                  )}
                  <h4 className="font-bold text-white text-base line-clamp-1 mt-1">{prod.title}</h4>
                  <p className="text-xs text-cyan-400 font-semibold">{prod.brand}</p>
                  
                  <div className="mt-3 text-2xl font-extrabold text-white">₹{prod.price.toLocaleString()}</div>
                  <div className="flex items-center gap-1 text-amber-400 text-xs font-bold mt-1">
                    <Star className="w-3.5 h-3.5 fill-amber-400" /> {prod.rating} / 5.0 rating
                  </div>

                  <div className="mt-4 space-y-2 text-xs border-t border-slate-800 pt-3">
                    <div className="flex justify-between py-1 border-b border-slate-800/60">
                      <span className="text-slate-400">Category:</span>
                      <span className="text-slate-200 font-medium">{prod.category}</span>
                    </div>
                    {prod.specs && Object.entries(prod.specs).map(([key, val]) => (
                      <div key={key} className="flex justify-between py-1 border-b border-slate-800/60">
                        <span className="text-slate-400 capitalize">{key}:</span>
                        <span className="text-slate-200 font-medium">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => onClose()}
                  className="mt-6 w-full py-2 px-3 bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white font-semibold text-xs rounded-xl transition-colors"
                >
                  Select Product
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
