"use client";

import Image from 'next/image';
import { Star, ShoppingCart, Check, Sparkles, Scale } from 'lucide-react';
import { Product } from '@/lib/api';

interface ProductCardProps {
  product: Product;
  onAddToCart: (p: Product) => void;
  onCompare?: (p: Product) => void;
  isRecommended?: boolean;
}

export default function ProductCard({ product, onAddToCart, onCompare, isRecommended }: ProductCardProps) {
  return (
    <div className={`glass-card rounded-2xl overflow-hidden flex flex-col justify-between group relative ${
      isRecommended ? 'ring-2 ring-indigo-500 shadow-xl shadow-indigo-500/20' : ''
    }`}>
      
      {/* Recommended Tag */}
      {isRecommended && (
        <div className="absolute top-3 left-3 z-10 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-[11px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1 shadow-md">
          <Sparkles className="w-3 h-3 text-cyan-300" /> AI Top Pick
        </div>
      )}

      {/* Image Banner */}
      <div className="relative h-48 w-full bg-slate-900 overflow-hidden">
        <img
          src={product.image_url || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />
        <span className="absolute bottom-2 right-3 text-xs bg-slate-900/80 backdrop-blur-md px-2 py-0.5 rounded-md text-slate-300 border border-slate-700">
          {product.category}
        </span>
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">{product.brand}</span>
            <div className="flex items-center gap-1 text-amber-400 text-xs font-bold bg-amber-400/10 px-2 py-0.5 rounded-full">
              <Star className="w-3 h-3 fill-amber-400" />
              <span>{product.rating}</span>
              <span className="text-slate-400 font-normal">({product.review_count})</span>
            </div>
          </div>

          <h3 className="font-bold text-slate-100 text-base line-clamp-1 group-hover:text-indigo-400 transition-colors">
            {product.title}
          </h3>

          <p className="text-slate-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">
            {product.description}
          </p>

          {/* Specs preview tags */}
          {product.specs && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {Object.entries(product.specs).slice(0, 3).map(([key, val]) => (
                <span key={key} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                  <strong className="text-indigo-300">{key}:</strong> {String(val)}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Pricing & Actions */}
        <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg font-extrabold text-white">₹{product.price.toLocaleString()}</span>
              {product.original_price && (
                <span className="text-xs text-slate-500 line-through">₹{product.original_price.toLocaleString()}</span>
              )}
            </div>
            <span className="text-[10px] text-emerald-400 font-medium">In Stock ({product.stock_quantity})</span>
          </div>

          <div className="flex items-center gap-1.5">
            {onCompare && (
              <button
                onClick={() => onCompare(product)}
                className="flex items-center gap-1 px-2.5 py-2 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 hover:text-purple-200 border border-purple-500/30 text-xs font-semibold transition-all active:scale-95 shadow-sm"
                title={`Compare ${product.title} with similar ${product.category}`}
              >
                <Scale className="w-3.5 h-3.5 text-purple-400" />
                <span>Compare</span>
              </button>
            )}
            <button
              onClick={() => onAddToCart(product)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all active:scale-95"
            >
              <ShoppingCart className="w-3.5 h-3.5" />
              Add
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
