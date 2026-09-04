"use client";

import { useState, useRef, useEffect } from 'react';
import { Bot, Send, X, Sparkles, CheckCircle2, ShoppingCart, ShieldAlert, ChevronRight, Terminal, Star, ArrowRight, Cpu, Tag, PackageCheck } from 'lucide-react';
import { sendAgentMessage, AgentChatResponse, Product, WorkflowStep, AINegotiatedOffer, CustomerMemoryProfile } from '@/lib/api';
import PurchaseWorkflowVisualizer from '@/components/PurchaseWorkflowVisualizer';
import AINegotiatedOfferBanner from '@/components/AINegotiatedOfferBanner';
import CustomerMemoryBadge from '@/components/CustomerMemoryBadge';

interface AIChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onInitiateCheckout: (productId?: string, stagedOrderId?: string, stagedAmount?: number) => void;
}

interface MessageItem {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  recommendedProduct?: Product;
  comparisonTable?: Record<string, any>;
  toolTraces?: any[];
  workflowSteps?: WorkflowStep[];
  requiresApproval?: boolean;
  suggestedActions?: string[];
  stagedCartId?: string;
  stagedOrderId?: string;
  couponApplied?: string;
  originalAmount?: number;
  discountAmount?: number;
  finalAmount?: number;
  negotiatedOffer?: AINegotiatedOffer;
  memoryProfile?: CustomerMemoryProfile;
}

export default function AIChatDrawer({ isOpen, onClose, onInitiateCheckout }: AIChatDrawerProps) {
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'welcome_1',
      sender: 'agent',
      text: "👋 Hi! I'm your **Personalized RazorBuy Purchase Agent**. I remember your brand preferences across sessions, execute 11-step workflows, and dynamically negotiate custom offers for you.\n\nTry testing multi-session memory:\n**Session 1**: *'I prefer Sony products and I don't like bulky headphones.'*\n**Session 2**: *'Find headphones for travel.'*",
      suggestedActions: [
        "I prefer Sony products and I don't like bulky headphones.",
        "Find headphones for travel.",
        "I need headphones under ₹5,000 for online classes. Buy best one."
      ]
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  if (!isOpen) return null;

  const renderFormattedText = (text: string) => {
    if (!text) return null;
    const lines = text.split('\n');
    return lines.map((line, lIdx) => {
      // Split by **bold** and `code`
      const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g);
      return (
        <div key={lIdx} className={lIdx > 0 ? "mt-1.5" : ""}>
          {parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <strong key={pIdx} className="font-extrabold text-white">
                  {part.slice(2, -2)}
                </strong>
              );
            } else if (part.startsWith('`') && part.endsWith('`')) {
              return (
                <code key={pIdx} className="bg-slate-950 text-cyan-300 px-1.5 py-0.5 rounded text-xs font-mono border border-slate-700">
                  {part.slice(1, -1)}
                </code>
              );
            } else {
              return <span key={pIdx}>{part}</span>;
            }
          })}
        </div>
      );
    });
  };

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const userMsgId = `usr_${Date.now()}`;
    const userMsg: MessageItem = { id: userMsgId, sender: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const response: AgentChatResponse = await sendAgentMessage(text);
      const agentMsgId = `agent_${Date.now()}`;
      const agentMsg: MessageItem = {
        id: agentMsgId,
        sender: 'agent',
        text: response.reply,
        recommendedProduct: response.recommended_product,
        comparisonTable: response.comparison_table,
        toolTraces: response.tool_traces,
        workflowSteps: response.workflow_steps,
        requiresApproval: response.requires_user_approval,
        suggestedActions: response.suggested_actions,
        stagedCartId: response.staged_cart_id,
        stagedOrderId: response.staged_order_id,
        couponApplied: response.coupon_applied,
        originalAmount: response.original_amount,
        discountAmount: response.discount_amount,
        finalAmount: response.final_amount,
        negotiatedOffer: response.negotiated_offer,
        memoryProfile: response.memory_profile
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'agent',
          text: "⚠️ Sorry, I ran into an error communicating with the agent server. Please try again."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[500px] glass-panel shadow-2xl flex flex-col border-l border-slate-800">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-white text-base flex items-center gap-1.5">
              Personalized Purchase Agent <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            </h2>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Persistent Customer Memory Active
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            {/* Message Bubble */}
            <div
              className={`max-w-[92%] p-3.5 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20'
                  : 'bg-slate-800/90 text-slate-200 border border-slate-700 rounded-bl-none'
              }`}
            >
              <div>{renderFormattedText(msg.text)}</div>
            </div>

            {/* Customer Memory Profile Badge */}
            {msg.memoryProfile && (
              <CustomerMemoryBadge memory={msg.memoryProfile} />
            )}

            {/* AI Negotiated Offer Banner Component */}
            {msg.negotiatedOffer && (
              <AINegotiatedOfferBanner
                offer={msg.negotiatedOffer}
                onApproveCheckout={() => onInitiateCheckout(msg.recommendedProduct?.id || "prod_001")}
              />
            )}

            {/* Visual Workflow Stepper UI */}
            {msg.workflowSteps && msg.workflowSteps.length > 0 && (
              <PurchaseWorkflowVisualizer
                steps={msg.workflowSteps}
                couponApplied={msg.couponApplied}
                originalAmount={msg.originalAmount}
                discountAmount={msg.discountAmount}
                finalAmount={msg.finalAmount}
              />
            )}

            {/* Comparison Table View if returned */}
            {msg.comparisonTable && (
              <div className="mt-3 p-3 bg-slate-900/90 border border-slate-800 rounded-2xl w-full max-w-[92%] overflow-x-auto">
                <table className="w-full text-xs text-slate-300 font-mono">
                  <thead>
                    <tr className="border-b border-slate-700 text-cyan-400 text-[11px] uppercase">
                      <th className="py-1.5 px-2 text-left">Model</th>
                      <th className="py-1.5 px-2 text-center">Price</th>
                      <th className="py-1.5 px-2 text-center">Rating</th>
                      <th className="py-1.5 px-2 text-center">Mic</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(msg.comparisonTable).map(([itemKey, itemData]: [string, any], idx) => (
                      <tr key={idx} className="border-b border-slate-800/50">
                        <td className="py-2 px-2 text-white font-bold">{itemData.title || itemKey}</td>
                        <td className="py-2 px-2 text-center text-cyan-300">₹{itemData.price?.toLocaleString()}</td>
                        <td className="py-2 px-2 text-center text-amber-400">{itemData.rating}★</td>
                        <td className="py-2 px-2 text-center text-emerald-400">{itemData.mic || "Clear HD"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Recommended Product Card */}
            {msg.recommendedProduct && (
              <div className="mt-3 p-3 bg-slate-900/90 border border-indigo-500/40 rounded-2xl w-full max-w-[92%] shadow-lg">
                <div className="text-xs text-indigo-400 font-bold uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Selected Best Product</span>
                  <span className="bg-indigo-500/20 text-indigo-300 text-[10px] px-2 py-0.5 rounded-full font-bold">
                    94.5 / 100 Score
                  </span>
                </div>
                <div className="flex gap-3 items-center">
                  <img
                    src={msg.recommendedProduct.image_url || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"}
                    alt={msg.recommendedProduct.title}
                    className="w-16 h-16 object-cover rounded-xl border border-slate-700"
                  />
                  <div>
                    <h4 className="font-bold text-white text-sm">{msg.recommendedProduct.title}</h4>
                    <div className="text-xs text-amber-400 flex items-center gap-1 font-semibold mt-0.5">
                      <Star className="w-3 h-3 fill-amber-400" /> {msg.recommendedProduct.rating} ★
                    </div>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-sm font-extrabold text-cyan-300">
                        ₹{(msg.finalAmount || msg.recommendedProduct.price).toLocaleString()}
                      </span>
                      {msg.originalAmount && (
                        <span className="text-xs text-slate-500 line-through">
                          ₹{msg.originalAmount.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Human Authorization Required Box */}
            {msg.requiresApproval && (
              <div className="mt-3 p-4 bg-gradient-to-r from-indigo-950/90 via-purple-950/90 to-slate-900/90 border border-cyan-500/60 rounded-2xl w-full max-w-[95%] shadow-2xl">
                <div className="flex items-center gap-2 text-cyan-300 font-bold text-xs uppercase tracking-wider mb-1.5">
                  <ShieldAlert className="w-4 h-4 text-cyan-400" /> Step 11: Human Authorization Guardrail
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  The AI Purchase Agent completed steps 1–10 autonomously. Click below to confirm AI-negotiated price and launch Razorpay Checkout.
                </p>
                <button
                  onClick={() => onInitiateCheckout(msg.recommendedProduct?.id || "prod_001", msg.stagedOrderId, msg.finalAmount || msg.negotiatedOffer?.offer_price)}
                  className="mt-3.5 w-full py-3 px-4 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-white font-extrabold text-xs uppercase tracking-widest rounded-xl shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2 transition-all active:scale-98"
                >
                  <ShoppingCart className="w-4 h-4" /> Approve & Pay ₹{(msg.finalAmount || 4184).toLocaleString()} via Razorpay
                </button>
              </div>
            )}

            {/* Suggested Action Pills */}
            {msg.suggestedActions && (
              <div className="mt-2.5 flex flex-wrap gap-1.5 max-w-[92%]">
                {msg.suggestedActions.map((action, i) => {
                  const isApproveAction = action.toLowerCase().includes("approve") || action.toLowerCase().includes("pay");
                  return (
                    <button
                      key={i}
                      onClick={() => isApproveAction ? onInitiateCheckout(msg.recommendedProduct?.id || "prod_001", msg.stagedOrderId, msg.finalAmount || msg.negotiatedOffer?.offer_price) : handleSend(action)}
                      className="text-xs bg-slate-800/80 hover:bg-indigo-600/30 text-indigo-300 hover:text-white border border-indigo-500/30 px-3 py-1 rounded-full transition-all flex items-center gap-1"
                    >
                      <span>{action}</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  );
                })}
              </div>
            )}

          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs bg-slate-800/50 p-3 rounded-2xl border border-slate-700/50 w-fit">
            <Cpu className="w-4 h-4 text-cyan-400 animate-spin" />
            <span>Autonomous Agent recalling memory & processing request...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-3.5 border-t border-slate-800 bg-slate-900/90">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Try: 'Check Stock Inventory' or 'View Spec Comparison'"
            className="flex-1 bg-slate-800 border border-slate-700 text-white text-sm rounded-xl px-3.5 py-2.5 focus:outline-none focus:border-indigo-500 placeholder-slate-500"
          />
          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all shadow-md shadow-indigo-600/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
}
