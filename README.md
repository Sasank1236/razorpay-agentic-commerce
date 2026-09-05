# ⚡ RazorBuy — AI Agentic Commerce Platform

> **An autonomous dual-agent commerce platform that understands natural-language shopping intent, remembers customer preferences across sessions, executes an 11-step AI purchase workflow, dynamically negotiates personalised coupon offers, and completes purchases via Razorpay Standard Checkout after explicit human authorization. On the merchant side, an AI Growth Agent analyses commerce data, detects abandoned carts, runs 1-click recovery campaigns, and measures outcomes in a closed feedback loop.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-razorpay--agentic--commerce--beige.vercel.app-6366f1?style=for-the-badge&logo=vercel)](https://razorpay-agentic-commerce-beige.vercel.app/shop)
[![Backend API](https://img.shields.io/badge/Backend%20API-onrender.com-22c55e?style=for-the-badge&logo=fastapi)](https://razorpay-agentic-commerce-r80s.onrender.com/docs)
[![Demo Video](https://img.shields.io/badge/Demo%20Video-Watch%20Now-ef4444?style=for-the-badge&logo=youtube)](https://razorpay-agentic-commerce-beige.vercel.app/demo.html)
[![Razorpay Builathon](https://img.shields.io/badge/Razorpay-Builathon%202026-0ea5e9?style=for-the-badge)](https://razorpay.com)

---

## 🌐 Live Links

| Resource | URL |
|---|---|
| 🛍️ **Customer Store** | https://razorpay-agentic-commerce-beige.vercel.app/shop |
| 📊 **Merchant Dashboard** | https://razorpay-agentic-commerce-beige.vercel.app/merchant |
| 🕐 **Agent Decision Timeline** | https://razorpay-agentic-commerce-beige.vercel.app/timeline |
| 🎬 **Demo Video** | https://razorpay-agentic-commerce-beige.vercel.app/demo.html |
| 🔧 **Backend API Docs** | https://razorpay-agentic-commerce-r80s.onrender.com/docs |

> ⚠️ The backend runs on Render's **free tier** — it sleeps after 15 min of inactivity. First request may take 30–60s to wake up.

---

## 🏗️ Architecture

```text
                              RAZORBUY PLATFORM
                                     │
             ┌───────────────────────┴───────────────────────┐
             │                                               │
      CUSTOMER SIDE                                   MERCHANT SIDE
             │                                               │
             ↓                                               ↓
   AI Purchase Agent (Gemini)                    AI Growth Agent (Gemini)
             │                                               │
┌────────────┼────────────┐               ┌─────────────────┼─────────────┐
│            │            │               │                 │             │
↓            ↓            ↓               ↓                 ↓             ↓
11-Step    Dynamic AI  Customer       Abandoned Cart   Closed-Loop    AI Decision
Workflow   Coupon      Memory         Recovery Loop    Campaign        Log Audit
(Stepper)  Engine      (Persist)      (5-Point Tree)   Learning       Timeline
           │                                               │
           └───────────────────┬───────────────────────────┘
                               │
                               ↓
                   Human Authorization Guardrail
                               │
                               ↓
                  Razorpay Standard Checkout (Test)
                               │
                               ↓
                   HMAC SHA256 Signature Verify
                               │
                               ↓
                  Inventory Reduction + Order PAID
```

---

## 🔥 Key Features

### 1. 🤖 11-Step Autonomous Purchase Agent

An end-to-end agentic pipeline powered by **Google Gemini Flash**:

| Step | Action |
|---|---|
| 1 | **Understand Request & Recall Memory** — LLM parses intent, recalls stored preferences |
| 2 | **Search Products** — semantic catalog search |
| 3 | **Filter Budget** — eliminates out-of-range products |
| 4 | **Evaluate Specifications** — scores against customer preferences |
| 5 | **Compare Candidates** — side-by-side spec table |
| 6 | **Select Best Product** — hybrid scoring (`rating + price fit + specs + popularity`) |
| 7 | **Check Inventory** — live stock availability |
| 8 | **Dynamic AI Coupon Negotiation** — Gemini-reasoned personalised discount |
| 9 | **Calculate Final Price** — net payable after discount |
| 10 | **Stage Order** — creates DB record for exact 1 product (no cart accumulation) |
| 11 | **🛡️ Human Authorization Guardrail** — customer must explicitly approve before payment |

### 2. 🏷️ Dynamic AI Coupon Negotiation Engine

Gemini evaluates three live signals to calculate the optimal discount:
- **Purchase Intent Score** — high/medium/low based on message urgency
- **Inventory Level** — scarcity pricing vs clearance pricing
- **Cart Abandonment History** — reactivation discount for returning abandoners

**Sample reasoning:**
> *"This customer has high purchase intent, the product has 50 units in inventory, and new checkout session. An AI-negotiated 6% coupon is optimal to maximize conversion while protecting margin."*

Coupon expires in **10 minutes** with a live countdown timer.

### 3. 🧠 Personalized Customer Memory Engine

Extracts and persists customer preferences across sessions:
- **Preferred Brands**: `Sony`, `JBL`, `Boat`
- **Avoided Traits**: `Bulky (>220g)`, `Heavy`
- **Use Cases**: `Travel`, `Calls`, `Online Classes`
- **Budget Ceiling**: inferred from natural language

Memory applies a **+15pt Brand Loyalty bonus** and **-25pt Avoidance penalty** in product ranking.

### 4. ⚖️ Product Comparison

One-click comparison of same-category products with a side-by-side spec modal triggered directly from any product card.

### 5. 🚨 AI Cart Recovery Loop (Merchant Side)

- **5-Point AI Decision Analysis** — scans abandoned carts for Product Demand, Customer Intent, Cart Value, Discount Usage, and Recommended Incentive
- **At-Risk Revenue Visibility** — e.g. `Recover ₹73,494 At-Risk Revenue`
- **1-Click Campaign Activation** — dispatches recovery offer and logs it to the timeline

### 6. 🔄 Closed-Loop Campaign Learning

- **Pre vs Post Measurement** — compares baseline vs outcome conversion rates
- **AI Parameter Optimisation** — 1-click discount tuning (5% → 3%) to protect gross margins

### 7. 🛡️ Security & Payment Safety

- Order totals calculated **server-side only** — never from client parameters
- **HMAC-SHA256 signature verification** before marking any order as `PAID`
- Inventory decremented **only after** verified payment
- Full auditability via the **AI Decision Log Timeline**

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 App Router, TypeScript, Tailwind CSS, Lucide Icons, Recharts |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.x, Pydantic v2, Uvicorn |
| **AI / LLM** | Google Gemini Flash (`gemini-3.5-flash`) |
| **Payments** | Razorpay Standard Checkout SDK (Test Mode) |
| **Database** | SQLite (local) / PostgreSQL (production via Render) |
| **Deployment** | Vercel (frontend) + Render (backend + DB) |

---

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone the repo

```bash
git clone https://github.com/Sasank1236/razorpay-agentic-commerce.git
cd razorpay-agentic-commerce
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` (copy from `.env.example`):

```env
DATABASE_URL=sqlite:///./razorbuy.db
GEMINI_API_KEY=your_gemini_api_key_here
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
BACKEND_CORS_ORIGINS=http://localhost:3000
```

Seed the database and start the server:

```bash
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

API docs → http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
```

Start the dev server:

```bash
npm run dev
```

Open → http://localhost:3000

---

## 🚢 Production Deployment

| Service | Platform | Notes |
|---|---|---|
| Frontend | **Vercel** | Connect GitHub, set root dir to `frontend` |
| Backend | **Render** | Free web service, root dir `backend` |
| Database | **Render PostgreSQL** | Free tier, URL auto-injected as `DATABASE_URL` |

### Vercel Environment Variables

| Key | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com/api/v1` |
| `NEXT_PUBLIC_RAZORPAY_KEY_ID` | `rzp_test_xxxxxxxxxxxx` |

### Render Environment Variables

| Key | Value |
|---|---|
| `DATABASE_URL` | *(auto-injected from Render PostgreSQL)* |
| `GEMINI_API_KEY` | your Google AI Studio key |
| `RAZORPAY_KEY_ID` | `rzp_test_xxxxxxxxxxxx` |
| `RAZORPAY_KEY_SECRET` | your Razorpay secret |
| `BACKEND_CORS_ORIGINS` | `https://your-app.vercel.app` |

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/test_api.py -v
```

```
tests/test_api.py ........                                        [100%]
======================== 8 passed in 2.30s ========================
```

Tests cover: root health, product catalog, customer memory, purchase agent workflow, dynamic negotiation, cart recovery, closed-loop feedback, merchant growth, and Razorpay HMAC signature verification.

---

## 📁 Project Structure

```
razorpay-agentic-commerce/
├── backend/
│   ├── app/
│   │   ├── agents/          # shopping_agent.py — 11-step workflow
│   │   ├── api/             # FastAPI routers (products, agents, payments)
│   │   ├── db/              # database.py, seed.py (105 products)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── services/        # memory_service, razorpay_service, negotiation
│   │   └── tools/           # product_tools, cart_tools, etc.
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── shop/            # Customer storefront + AI agent drawer
│   │   ├── merchant/        # Merchant growth dashboard
│   │   └── timeline/        # Agent decision log
│   ├── components/          # AIChatDrawer, CheckoutModal, ProductCard, etc.
│   ├── lib/api.ts           # API client
│   └── public/demo.html     # Demo video viewer
├── render.yaml              # Render deployment blueprint
└── README.md
```

---

## 📄 License

MIT © 2026 — Built for the Razorpay Builathon
