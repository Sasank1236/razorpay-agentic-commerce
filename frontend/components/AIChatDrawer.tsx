"use client";

import { useState, useRef, useEffect } from 'react';
import { Bot, Send, X, Sparkles, CheckCircle2, ShoppingCart, ShieldAlert, ChevronRight, Terminal, Star, ArrowRight } from 'lucide-react';
import { sendAgentMessage, AgentChatResponse, Product } from '@/lib/api';

interface AIChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onInitiateCheckout: (productId?: string) => void;
}

interface MessageItem {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  recommendedProduct?: Product;
  comparisonTable?: Record<string, any>;
  toolTraces?: any[];
  requiresApproval?: boolean;
  suggestedActions?: string[];
  stagedCartId?: string;
}

export default function AIChatDrawer({ isOpen, onClose, onInitiateCheckout }: AIChatDrawerProps) {
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'welcome_1',
      sender: 'agent',
      text: "👋 Hi! I'm your **RazorBuy Commerce Agent**. Tell me what you're looking for, budget, or key priorities (e.g. *'Wireless headphones under ₹5,000 for calls and music with long battery'*).",
      suggestedActions: [
        "Headphones under ₹5,000 for calls",
        "Smartwatches with AMOLED & BT calling",
        "Ergonomic mechanical keyboard"
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
        requiresApproval: response.requires_user_approval,
        suggestedActions: response.suggested_actions,
        stagedCartId: response.staged_cart_id
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
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] glass-panel shadow-2xl flex flex-col border-l border-slate-800">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-md">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-white text-base flex items-center gap-1.5">
              Customer AI Agent <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            </h2>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Tool-Calling Autonomous Agent
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
              className={`max-w-[90%] p-3.5 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20'
                  : 'bg-slate-800/90 text-slate-200 border border-slate-700 rounded-bl-none'
              }`}
            >
              <div className="whitespace-pre-line">{msg.text}</div>
            </div>

            {/* Agent Tool Traces Audit Pill */}
            {msg.toolTraces && msg.toolTraces.length > 0 && (
              <div className="mt-2 text-xs bg-slate-950/70 border border-slate-800 rounded-xl p-2.5 w-full max-w-[92%]">
                <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1">
                  <Terminal className="w-3 h-3 text-cyan-400" /> Agent Decision Log ({msg.toolTraces.length} tools called)
                </div>
                <div className="space-y-1">
                  {msg.toolTraces.map((t, idx) => (
                    <div key={idx} className="flex items-center justify-between text-[11px] text-slate-400 font-mono bg-slate-900/80 px-2 py-1 rounded">
                      <span className="text-purple-300 font-medium">⚡ {t.tool_name}()</span>
                      <span className="text-emerald-400 text-[10px]">{t.execution_time_ms}ms</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommended Product Card */}
            {msg.recommendedProduct && (
              <div className="mt-3 p-3 bg-slate-900/90 border border-indigo-500/40 rounded-2xl w-full max-w-[92%] shadow-lg">
                <div className="text-xs text-indigo-400 font-bold uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Top Agent Recommendation</span>
                  <span className="bg-indigo-500/20 text-indigo-300 text-[10px] px-2 py-0.5 rounded-full">
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
                    <p className="text-sm font-extrabold text-white mt-1">₹{msg.recommendedProduct.price.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Human Approval Required Box */}
            {msg.requiresApproval && (
              <div className="mt-3 p-3.5 bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-cyan-500/50 rounded-2xl w-full max-w-[92%] shadow-xl">
                <div className="flex items-center gap-2 text-cyan-300 font-bold text-xs uppercase mb-1">
                  <ShieldAlert className="w-4 h-4 text-cyan-400" /> Human Authorization Required
                </div>
                <p className="text-xs text-slate-300 leading-normal">
                  The AI agent has calculated order totals and staged your transaction safely. Click below to launch Razorpay Test Checkout.
                </p>
                <button
                  onClick={() => onInitiateCheckout(msg.recommendedProduct?.id || "prod_001")}
                  className="mt-3 w-full py-2.5 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all active:scale-98"
                >
                  <ShoppingCart className="w-4 h-4" /> Confirm Purchase & Pay ₹4,499
                </button>
              </div>
            )}

            {/* Suggested Action Pills */}
            {msg.suggestedActions && (
              <div className="mt-2.5 flex flex-wrap gap-1.5 max-w-[92%]">
                {msg.suggestedActions.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(action)}
                    className="text-xs bg-slate-800/80 hover:bg-indigo-600/30 text-indigo-300 hover:text-white border border-indigo-500/30 px-3 py-1 rounded-full transition-all flex items-center gap-1"
                  >
                    <span>{action}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                ))}
              </div>
            )}

          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs bg-slate-800/50 p-3 rounded-2xl border border-slate-700/50 w-fit">
            <Bot className="w-4 h-4 text-indigo-400 animate-spin" />
            <span>AI Agent is searching 105 products & reasoning...</span>
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
            placeholder="Ask AI: e.g. Headphones under ₹5k for calls..."
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
