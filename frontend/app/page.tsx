"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/shop');
  }, [router]);

  return (
    <div className="min-h-screen bg-[#060919] flex items-center justify-center text-slate-300">
      <div className="text-center space-y-2">
        <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-slate-400 font-mono">Redirecting to RazorBuy E-Commerce Storefront...</p>
      </div>
    </div>
  );
}
