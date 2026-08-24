"use client";

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import ProductCard from '@/components/ProductCard';
import AIChatDrawer from '@/components/AIChatDrawer';
import ProductCompareModal from '@/components/ProductCompareModal';
import CheckoutModal from '@/components/CheckoutModal';
import { fetchProducts, fetchCart, addToCartApi, stageOrderApi, Product, Cart } from '@/lib/api';
import { Search, Filter, Sparkles, ShoppingBag, Bot, ArrowRight, ShieldCheck, Scale } from 'lucide-react';

const CATEGORIES = ["All", "Audio", "Wearables", "Accessories", "Laptops", "Smart Home"];

export default function ShopPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Cart | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  // Drawers & Modals state
  const [isAIChatOpen, setIsAIChatOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [compareProducts, setCompareProducts] = useState<Product[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [stagedOrderId, setStagedOrderId] = useState("ord_staged_001");
  const [stagedAmount, setStagedAmount] = useState(4499.0);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await fetchProducts(
        selectedCategory === "All" ? undefined : selectedCategory,
        searchQuery ? searchQuery : undefined
      );
      setProducts(data);
    } catch (err) {
      console.error("Failed to load products:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadCartData = async () => {
    try {
      const c = await fetchCart();
      setCart(c);
    } catch (err) {
      console.error("Failed to load cart:", err);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [selectedCategory]);

  useEffect(() => {
    loadCartData();
  }, []);

  const handleAddToCart = async (product: Product) => {
    try {
      await addToCartApi(product.id, 1);
      await loadCartData();
    } catch (err) {
      console.error("Failed to add product to cart:", err);
    }
  };

  const handleCompare = (product: Product) => {
    if (compareProducts.some(p => p.id === product.id)) return;
    const updated = [...compareProducts, product].slice(0, 3);
    setCompareProducts(updated);
    if (updated.length >= 2) {
      setIsCompareOpen(true);
    }
  };

  const handleInitiateCheckout = async (productId?: string) => {
    try {
      const staged = await stageOrderApi();
      setStagedOrderId(staged.id);
      setStagedAmount(staged.total_amount);
      setIsCheckoutOpen(true);
    } catch (err) {
      setStagedOrderId("ord_demo_001");
      setStagedAmount(4499.0);
      setIsCheckoutOpen(true);
    }
  };

  return (
    <div className="min-h-screen bg-[#060919]">
      <Navbar
        cartCount={cart ? cart.items.reduce((sum, i) => sum + i.quantity, 0) : 0}
        onOpenCart={() => setIsCartOpen(!isCartOpen)}
        onOpenAIChat={() => setIsAIChatOpen(true)}
      />

      {/* Hero Banner */}
      <section className="relative overflow-hidden pt-8 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="glass-panel p-8 sm:p-10 rounded-3xl border border-indigo-500/20 relative overflow-hidden">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
          <div className="max-w-3xl space-y-4">
            <span className="text-xs text-cyan-400 font-bold tracking-widest uppercase bg-cyan-400/10 border border-cyan-400/30 px-3 py-1 rounded-full inline-flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> AI Agentic Commerce Platform
            </span>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
              Shopping, Evolved. <br />
              <span className="gradient-text">Let AI Discover, Evaluate & Buy.</span>
            </h1>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Describe your exact request in natural language. Our autonomous agent evaluates specs, compares ratings, calculates scores, and stages your Razorpay checkout after your approval.
            </p>

            <div className="pt-2 flex flex-wrap gap-3">
              <button
                onClick={() => setIsAIChatOpen(true)}
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm rounded-2xl shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all hover:scale-105"
              >
                <Bot className="w-4 h-4" /> Start AI Agent Search
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Catalog Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        
        {/* Search & Category Filter Header */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-8">
          
          {/* Categories */}
          <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              loadProducts();
            }}
            className="relative w-full md:w-80"
          >
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search products..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </form>

        </div>

        {/* Product Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
              <div key={n} className="glass-card h-80 rounded-2xl animate-pulse bg-slate-900/50" />
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-16 glass-panel rounded-3xl">
            <p className="text-slate-400 text-sm">No products found matching your search.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                onCompare={handleCompare}
                isRecommended={product.id === "prod_001"}
              />
            ))}
          </div>
        )}

      </main>

      {/* AI Chat Drawer */}
      <AIChatDrawer
        isOpen={isAIChatOpen}
        onClose={() => setIsAIChatOpen(false)}
        onInitiateCheckout={handleInitiateCheckout}
      />

      {/* Cart Drawer */}
      {isCartOpen && (
        <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[400px] glass-panel shadow-2xl flex flex-col border-l border-slate-800">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900">
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-cyan-400" /> Shopping Cart
            </h3>
            <button onClick={() => setIsCartOpen(false)} className="text-slate-400 hover:text-white">✕</button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {cart && cart.items.length > 0 ? (
              cart.items.map((item) => (
                <div key={item.id} className="glass-card p-3 rounded-xl flex items-center justify-between text-xs">
                  <div>
                    <div className="font-bold text-white">{item.product?.title || `Product #${item.product_id}`}</div>
                    <div className="text-slate-400">{item.quantity} x ₹{item.unit_price.toLocaleString()}</div>
                  </div>
                  <div className="font-bold text-cyan-400">₹{(item.quantity * item.unit_price).toLocaleString()}</div>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-xs text-center py-8">Your cart is empty.</p>
            )}
          </div>
          <div className="p-4 border-t border-slate-800 bg-slate-900">
            <button
              onClick={() => {
                setIsCartOpen(false);
                handleInitiateCheckout();
              }}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg"
            >
              Checkout & Pay ₹{cart ? cart.subtotal.toLocaleString() : "4,499"}
            </button>
          </div>
        </div>
      )}

      {/* Product Compare Modal */}
      <ProductCompareModal
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        products={compareProducts}
      />

      {/* Checkout Modal */}
      <CheckoutModal
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        orderId={stagedOrderId}
        amount={stagedAmount}
        onPaymentSuccess={loadCartData}
      />

    </div>
  );
}
