# 🎬 RazorBuy — 5-Minute Hackathon Demo Script & Video Pitch Guide

This guide provides the exact 5-minute demo flow and pitch script to wow hackathon judges.

---

## ⏱️ Video Pitch Outline (5 Minutes)

### 📍 Phase 1: Problem & Vision (0:00 – 0:45)
- **Script**:
  > *"Traditional e-commerce forces customers to manually browse, apply filters, and compare dozens of tabs, while merchants struggle to figure out why shoppers abandon carts. RazorBuy transforms e-commerce from search-based browsing to AI-agentic commerce."*
- **Visual**: Show the RazorBuy Storefront (`http://localhost:3000/shop`).

---

### 📍 Phase 2: Customer AI Agent Search & Hybrid Recommendation (0:45 – 2:15)
- **Action**: Click **[Ask AI Agent]** button in the navbar.
- **Input Query**:
  ```text
  I need wireless headphones under ₹5,000. Main use is calls and music, battery life is important.
  ```
- **What to Highlight**:
  1. Show the agent executing **3 real-time tools**: `search_products()`, `compare_products()`, and `get_recommendations()`.
  2. Point out the **Hybrid Recommendation Score**: **SoundMax Pro Wireless Headphones (Score: 94.5/100)**.
  3. Explain the score breakdown: 30% preference + 25% price fit + 20% rating + 15% specs + 10% popularity.
  4. Show the side-by-side spec comparison table.

---

### 📍 Phase 3: Human Authorization & Razorpay Checkout (2:15 – 3:15)
- **Action**: Click **[Buy SoundMax Pro for ₹4,499]** or type *"Buy this product"*.
- **What to Highlight**:
  1. **Human Authorization Guardrail**: Emphasize that the AI agent *never* spends money autonomously. It stages the order and requests explicit customer authorization.
  2. **Server-Side Security**: Point out that the order total (`₹4,499.00`) is calculated strictly by the FastAPI backend to prevent client-side amount tampering.
  3. Click **[Confirm Purchase & Pay ₹4,499]**.
  4. Complete payment in **Razorpay Test Mode**.
  5. Show **HMAC SHA256 Signature Verification** passing and order status updating to **PAID**.

---

### 📍 Phase 4: Merchant AI Growth Agent Dashboard (3:15 – 4:15)
- **Action**: Navigate to `http://localhost:3000/merchant`.
- **What to Highlight**:
  1. Show live updated KPI stat cards: Total Revenue, Conversion Rate, AI-Assisted Sales %, and Abandoned Cart Risk.
  2. Point out the **AI Growth Agent Feed**:
     - *Opportunity Identified*: High headphone search volume under ₹5,000 with conversion gap.
     - *Recommendation*: Promote SoundMax Pro with 5% discount.
  3. Click **[Apply Recommendation]** button and show the campaign activating in real-time.

---

### 📍 Phase 5: AI Decision Log Audit Timeline & Closing (4:15 – 5:00)
- **Action**: Navigate to `http://localhost:3000/timeline`.
- **What to Highlight**:
  1. Show the live **AI Decision Log** tracing every tool call, execution latency (in milliseconds), input parameters, and output payloads.
  2. **Closing Statement**:
     > *"RazorBuy bridges customer intent to Razorpay payment with AI autonomy and human control, giving merchants an autonomous growth engine."*

---

## 🛠️ Quick Local Setup Check Before Recording

1. **Backend Server**:
   ```bash
   cd backend
   python -m app.db.seed
   python -m uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend Server**:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:3000/shop` and begin your recording!
