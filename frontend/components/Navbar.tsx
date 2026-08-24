"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShoppingBag, Bot, TrendingUp, History, Sparkles, ShieldCheck } from 'lucide-react';

interface NavbarProps {
  cartCount?: number;
  onOpenCart?: () => void;
  onOpenAIChat?: () => void;
}

export default function Navbar({ cartCount = 0, onOpenCart, onOpenAIChat }: NavbarProps) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/shop" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
              Razor<span className="gradient-text">Buy</span>
            </span>
            <span className="text-[10px] text-cyan-400 font-medium tracking-wider uppercase flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-cyan-400" /> AI Commerce Agent
            </span>
          </div>
        </Link>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-full border border-slate-800">
          <Link
            href="/shop"
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
              pathname === '/shop' || pathname === '/'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            Customer Store
          </Link>
          <Link
            href="/merchant"
            className={`px-4 py-1.5 rounded-full text-sm font-medium flex items-center gap-1.5 transition-all ${
              pathname === '/merchant'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <TrendingUp className="w-4 h-4 text-emerald-400" /> Merchant Growth
          </Link>
          <Link
            href="/timeline"
            className={`px-4 py-1.5 rounded-full text-sm font-medium flex items-center gap-1.5 transition-all ${
              pathname === '/timeline'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <History className="w-4 h-4 text-purple-400" /> Agent Log
          </Link>
        </nav>

        {/* Right Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenAIChat}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-medium hover:opacity-95 shadow-lg shadow-indigo-600/20 transition-all hover:scale-105"
          >
            <Bot className="w-4 h-4 animate-bounce" />
            <span className="hidden sm:inline">Ask AI Agent</span>
          </button>

          <button
            onClick={onOpenCart}
            className="relative p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 transition-all"
            aria-label="View Cart"
          >
            <ShoppingBag className="w-5 h-5 text-cyan-400" />
            {cartCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-indigo-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-md">
                {cartCount}
              </span>
            )}
          </button>
        </div>

      </div>
    </header>
  );
}
