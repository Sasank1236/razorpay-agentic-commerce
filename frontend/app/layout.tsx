import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'RazorBuy — AI Agentic Commerce Platform',
  description: 'AI-Powered Commerce Agent for discovery, personalized recommendations, human-in-the-loop Razorpay test checkout, and merchant growth analytics.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#060919] text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
