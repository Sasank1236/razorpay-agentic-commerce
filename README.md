# 🚀 RazorBuy — AI Agentic Commerce Platform

> **RazorBuy is an AI-powered commerce agent platform that understands customer natural-language shopping intent, discovers and evaluates products, makes personalized hybrid-scored recommendations, and—after explicit human approval—completes purchases through Razorpay Test Mode, while a merchant-side AI growth agent continuously analyzes commerce behavior to launch conversion-boosting interventions.**

---

## 🌟 Dual-Agent System Architecture

```text
                                  RAZORBUY
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
          CUSTOMER SIDE                           MERCHANT SIDE
                 │                                       │
                 ↓                                       ↓
        AI Shopping Agent                       AI Growth Agent
                 │                                       │
   ┌─────────────┼─────────────┐               ┌─────────┴─────────┐
   │             │             │               │                   │
   ↓             ↓             ↓               ↓                   ↓
Search &     Product       Cart &          Commerce           Abandoned Cart
Filter       Compare       Staging         Analytics          Recovery & Interventions
   │                                           │
   └─────────────┬─────────────┘               │
                 │                             │
                 ↓                             │
         User Confirmation                     │
                 │                             │
                 ↓                             │
        Razorpay Test Mode                     │
                 │                             │
                 ↓                             │
          HMAC Signature                       │
           Verification                        │
                 │                             │
                 ↓                             │
           Order Creation                      │
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ↓
                      Merchant Dashboard &
                     AI Decision Log Timeline
```

---

## 🔥 Key Features

### 1. 🤖 Customer Commerce Agent
- **Natural Language Shopping Intent**: Converts prompts like *"I need wireless headphones under ₹5,000 for calls with good battery"* into structured parameters.
- **Hybrid Recommendation Engine**: Combines database candidate retrieval, deterministic scoring formula (`30% preference match + 25% price fit + 20% rating + 15% specs + 10% popularity`), and OpenAI reasoning generation.
- **Tool-Calling Architecture**: Uses tools (`search_products`, `get_product_details`, `compare_products`, `get_recommendations`, `add_to_cart`, `create_staged_order`).
- **Human-in-the-Loop Confirmation**: AI never spends money autonomously. It stages carts and requires explicit customer approval before launching Razorpay Checkout.

### 2. 📈 Merchant AI Growth Agent
- **Commerce Analytics Engine**: Tracks Revenue, Orders, Store Conversion %, Average Order Value (AOV), AI-Assisted Sales %, and Abandoned Cart Risk Revenue.
- **Automated Opportunity Interventions**: Detects high-demand low-converting products and abandoned high-value carts.
- **Single-Click Campaign Execution**: Allows merchants to launch targeted recovery discounts and bundle promotions with one click.

### 3. 🛡️ Security & Payment Safety
- **Server-Side Order Calculation**: Order totals are strictly calculated server-side from backend database values (never client params).
- **HMAC Signature Verification**: Verifies `razorpay_order_id`, `razorpay_payment_id`, and `razorpay_signature` server-side before marking orders as `PAID`.
- **Full Auditability**: Every agent action is logged with timing metrics into the **AI Decision Log Timeline**.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14+ (TypeScript, Tailwind CSS, Lucide Icons, Recharts)
- **Backend**: Python FastAPI, SQLAlchemy, Pydantic, uvicorn
- **AI Agent Orchestration**: OpenAI Function Calling, LangGraph tool patterns
- **Database**: SQLite / PostgreSQL with seed dataset of 105 realistic products
- **Payments**: Razorpay Test Mode API

---

## 🚀 Quickstart Guide

### 1. Backend Setup (FastAPI)

```bash
cd backend
python -m pip install -r requirements.txt
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```
Backend API interactive documentation will be live at `http://localhost:8000/docs`.

### 2. Frontend Setup (Next.js)

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to view the storefront, AI agent assistant drawer, merchant growth center, and decision log timeline!

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/test_api.py
```

---

## 📄 License
MIT
