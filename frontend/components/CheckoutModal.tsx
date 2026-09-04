"use client";

import { useState } from 'react';
import { ShieldCheck, CreditCard, Lock, CheckCircle2, AlertCircle, X, Sparkles, Tag } from 'lucide-react';
import { createRazorpayOrderApi, verifyPaymentApi } from '@/lib/api';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId?: string;
  amount?: number;
  discountAmount?: number;
  couponCode?: string;
  onPaymentSuccess: () => void;
}

export default function CheckoutModal({
  isOpen,
  onClose,
  orderId = "ord_staged_001",
  amount = 4049.0,
  discountAmount = 450.0,
  couponCode = "STUDENT10",
  onPaymentSuccess,
}: CheckoutModalProps) {
  const [loading, setLoading] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const loadRazorpayScript = (): Promise<boolean> => {
    return new Promise((resolve) => {
      if (typeof window !== 'undefined' && (window as any).Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handleRazorpayStandardCheckout = async () => {
    setLoading(true);
    setErrorMsg('');

    try {
      // 1. Backend Order Creation (Safety: Amount calculated server-side in paise)
      const razorpayOrder = await createRazorpayOrderApi(orderId);
      // Prefer an explicit env override, otherwise trust the key_id the
      // backend returned (which reflects whatever RAZORPAY_KEY_ID is
      // configured server-side). No hardcoded fallback key.
      const razorpayKey = process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || razorpayOrder.key_id;

      // Load Razorpay Standard Checkout JS Script
      const isLoaded = await loadRazorpayScript();

      if (isLoaded && typeof window !== 'undefined' && (window as any).Razorpay) {
        const options = {
          key: razorpayKey,
          amount: razorpayOrder.amount_in_paisa,
          currency: razorpayOrder.currency || "INR",
          name: "RazorBuy Agentic Commerce",
          description: `Order #${orderId}`,
          image: "https://razorpay.com/favicon.ico",
          order_id: razorpayOrder.razorpay_order_id,
          handler: async function (response: any) {
            try {
              // On payment success: Verify payment signature on backend
              const verifyRes = await verifyPaymentApi(
                orderId,
                response.razorpay_order_id,
                response.razorpay_payment_id,
                response.razorpay_signature
              );

              if (verifyRes.success) {
                setPaymentSuccess(true);
                onPaymentSuccess();
              } else {
                setErrorMsg('Payment signature verification failed.');
              }
            } catch (err: any) {
              setErrorMsg(err.message || 'Signature verification failed.');
            } finally {
              setLoading(false);
            }
          },
          prefill: {
            name: "Rahul Sharma",
            email: "rahul.sharma@example.com",
            contact: "9876543210"
          },
          theme: {
            color: "#6366f1"
          },
          modal: {
            ondismiss: function () {
              setLoading(false);
            }
          }
        };

        const rzp = new (window as any).Razorpay(options);
        rzp.on('payment.failed', function (response: any) {
          setErrorMsg(response.error?.description || 'Payment failed in Razorpay Checkout.');
          setLoading(false);
        });
        rzp.open();
      } else {
        // Fallback for simulated test environment
        const simulatedPaymentId = `pay_test_${Math.random().toString(36).substring(2, 10)}`;
        const simulatedSignature = `sig_test_${Math.random().toString(36).substring(2, 12)}`;

        const verifyRes = await verifyPaymentApi(
          orderId,
          razorpayOrder.razorpay_order_id,
          simulatedPaymentId,
          simulatedSignature
        );

        if (verifyRes.success) {
          setPaymentSuccess(true);
          onPaymentSuccess();
        } else {
          setErrorMsg('Payment verification failed.');
        }
        setLoading(false);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Payment processing failed.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-md rounded-3xl overflow-hidden border border-slate-700 shadow-2xl animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Razorpay Standard Checkout</h3>
              <p className="text-xs text-slate-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Human Authorization Guardrail
              </p>
            </div>
          </div>

          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {paymentSuccess ? (
            <div className="text-center py-6 space-y-3">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center border border-emerald-500/40 animate-bounce">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h4 className="text-xl font-bold text-white">Payment Successful!</h4>
              <p className="text-sm text-slate-300">
                Your order <strong className="text-cyan-400">#{orderId}</strong> has been marked <span className="text-emerald-400 font-bold">PAID</span> and inventory updated.
              </p>
              <button
                onClick={onClose}
                className="mt-4 w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-indigo-600/20"
              >
                Return to Store
              </button>
            </div>
          ) : (
            <>
              {/* Amount Breakdown */}
              <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Product Price</span>
                  <span className="text-slate-200">₹{(amount + (discountAmount || 0)).toLocaleString()}</span>
                </div>
                {discountAmount > 0 && (
                  <div className="flex justify-between text-xs text-emerald-400 font-semibold">
                    <span className="flex items-center gap-1">
                      <Tag className="w-3 h-3" /> Coupon `{couponCode}` Discount
                    </span>
                    <span>-₹{discountAmount.toLocaleString()}</span>
                  </div>
                )}
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Shipping & Taxes</span>
                  <span className="text-emerald-400">FREE</span>
                </div>
                <div className="pt-2 border-t border-slate-800 flex justify-between items-baseline">
                  <span className="font-bold text-white text-sm">Net Payable Amount</span>
                  <span className="font-extrabold text-2xl text-cyan-400">₹{amount.toLocaleString()}</span>
                </div>
              </div>

              {/* Safety Badges */}
              <div className="text-xs text-slate-400 bg-slate-900/50 p-3 rounded-xl border border-slate-800 flex items-start gap-2">
                <Lock className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <p>
                  <strong>Razorpay Standard Web Checkout:</strong> Amount calculated server-side in paise. Uses HMAC-SHA256 signature verification.
                </p>
              </div>

              {errorMsg && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs rounded-xl flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              {/* Razorpay Standard Pay Button */}
              <button
                onClick={handleRazorpayStandardCheckout}
                disabled={loading}
                className="w-full py-3.5 px-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-extrabold text-sm uppercase tracking-wider rounded-2xl shadow-xl shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all active:scale-98 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Sparkles className="w-5 h-5 animate-spin" /> Opening Razorpay Checkout...
                  </>
                ) : (
                  <>
                    <CreditCard className="w-5 h-5" /> Pay ₹{amount.toLocaleString()} via Razorpay
                  </>
                )}
              </button>
            </>
          )}
        </div>

      </div>
    </div>
  );
}