const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Product {
  id: string;
  title: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  original_price?: number;
  rating: number;
  review_count: number;
  specs?: Record<string, any>;
  tags?: string[];
  image_url?: string;
  stock_quantity: number;
}

export interface CartItem {
  id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  product?: Product;
}

export interface Cart {
  id: string;
  user_id: string;
  status: string;
  items: CartItem[];
  subtotal: number;
}

export interface ToolTrace {
  tool_name: string;
  input_args: any;
  output_summary: any;
  execution_time_ms: number;
}

export interface WorkflowStep {
  step_number: number;
  step_name: string;
  status: string;
  detail_message: string;
  execution_time_ms: number;
}

export interface AINegotiatedOffer {
  coupon_code: string;
  discount_percent: number;
  original_price: number;
  offer_price: number;
  savings: number;
  reasoning: string;
  valid_seconds: number;
}

export interface CustomerMemoryProfile {
  preferred_brands: string[];
  avoid_traits: string[];
  primary_use_cases: string[];
  budget_ceiling: number;
  memory_summary: string;
}

export interface AgentChatResponse {
  reply: string;
  recommended_product?: Product;
  comparison_table?: Record<string, any>;
  tool_traces: ToolTrace[];
  workflow_steps?: WorkflowStep[];
  requires_user_approval: boolean;
  staged_cart_id?: string;
  staged_order_id?: string;
  coupon_applied?: string;
  original_amount?: number;
  discount_amount?: number;
  final_amount?: number;
  negotiated_offer?: AINegotiatedOffer;
  memory_profile?: CustomerMemoryProfile;
  suggested_actions?: string[];
}

export interface MerchantGrowthInsight {
  title: string;
  metric_highlight: string;
  description: string;
  impact_estimate: string;
  recommended_action: string;
  analysis_tree?: Record<string, string>;
  campaign_payload: Record<string, any>;
}

export interface CampaignFeedbackLoop {
  campaign_id: string;
  title: string;
  pre_conversion_rate: number;
  post_conversion_rate: number;
  conversion_lift_percent: number;
  revenue_generated: number;
  margin_impact: string;
  current_discount_percent: number;
  recommended_discount_percent: number;
  ai_conclusion: string;
  recommended_adjustment: string;
}

export interface MerchantGrowthResponse {
  insights: MerchantGrowthInsight[];
  metrics_summary: {
    total_revenue: number;
    total_orders: number;
    conversion_rate: number;
    avg_order_value: number;
    ai_assisted_sales: number;
    abandoned_carts_count: number;
    abandoned_revenue_at_risk: number;
  };
  campaign_feedback_loops?: CampaignFeedbackLoop[];
  tool_traces: ToolTrace[];
}

export async function fetchProducts(category?: string, query?: string, max_price?: number): Promise<Product[]> {
  try {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (query) params.append('query', query);
    if (max_price) params.append('max_price', max_price.toString());

    const res = await fetch(`${API_BASE_URL}/products?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch products');
    return await res.json();
  } catch (err) {
    console.error('Fetch products error:', err);
    return [];
  }
}

export async function sendAgentMessage(message: string, userId: string = 'user_customer_01'): Promise<AgentChatResponse> {
  const res = await fetch(`${API_BASE_URL}/agents/customer/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message }),
  });
  if (!res.ok) throw new Error('Agent service unavailable');
  return await res.json();
}

export async function fetchCart(userId: string = 'user_customer_01'): Promise<Cart> {
  const res = await fetch(`${API_BASE_URL}/orders/cart/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch cart');
  return await res.json();
}

export async function addToCartApi(productId: string, quantity: number = 1, userId: string = 'user_customer_01') {
  const res = await fetch(`${API_BASE_URL}/orders/cart/${userId}/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  if (!res.ok) throw new Error('Failed to add to cart');
  return await res.json();
}

export async function stageOrderApi(userId: string = 'user_customer_01') {
  const res = await fetch(`${API_BASE_URL}/orders/stage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) throw new Error('Failed to stage order');
  return await res.json();
}

export async function createRazorpayOrderApi(orderId: string) {
  const res = await fetch(`${API_BASE_URL}/payments/create-order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order_id: orderId }),
  });
  if (!res.ok) throw new Error('Failed to create Razorpay order');
  return await res.json();
}

export async function verifyPaymentApi(orderId: string, razorpayOrderId: string, razorpayPaymentId: string, razorpaySignature: string) {
  const res = await fetch(`${API_BASE_URL}/payments/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      order_id: orderId,
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature,
    }),
  });
  if (!res.ok) throw new Error('Payment verification failed');
  return await res.json();
}

export async function fetchMerchantGrowth(): Promise<MerchantGrowthResponse> {
  const res = await fetch(`${API_BASE_URL}/agents/merchant/growth`);
  if (!res.ok) throw new Error('Failed to fetch merchant growth insights');
  return await res.json();
}

export async function applyCampaignApi(payload: Record<string, any>) {
  const res = await fetch(`${API_BASE_URL}/agents/merchant/campaign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to execute campaign');
  return await res.json();
}

export async function fetchAgentTimeline() {
  const res = await fetch(`${API_BASE_URL}/analytics/timeline`);
  if (!res.ok) throw new Error('Failed to fetch timeline');
  return await res.json();
}

export async function fetchRevenueTrends() {
  const res = await fetch(`${API_BASE_URL}/analytics/trends`);
  if (!res.ok) throw new Error('Failed to fetch revenue trends');
  return await res.json();
}