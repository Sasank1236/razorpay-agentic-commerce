# 🚀 RazorBuy — AI Agentic Commerce Platform

> **RazorBuy is an autonomous dual-agent commerce platform that understands customer natural-language shopping intent, remembers preferences across sessions, executes an 11-step purchase workflow, dynamically negotiates personalized coupon offers with live timers, and completes purchases via Razorpay after human authorization. On the merchant side, an AI Growth Agent analyzes commerce data, detects abandoned carts, executes 1-click recovery campaigns, and measures post-campaign outcomes in a closed feedback loop.**

---

## 🌟 Dual-Agent System Architecture

```text
                                  RAZORBUY PLATFORM
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
          CUSTOMER SIDE                                   MERCHANT SIDE
                 │                                               │
                 ↓                                               ↓
       AI Purchase Agent                               AI Growth Agent
                 │                                               │
 ┌───────────────┼───────────────┐               ┌───────────────┼───────────────┐
 │               │               │               │               │               │
 ↓               ↓               ↓               ↓               ↓               ↓
11-Step       Dynamic AI     Personalized    Abandoned Cart   Closed-Loop      AI Decision
Workflow      Negotiation     Memory          Recovery Loop    Campaign        Log Audit
 (Stepper)    (10m Timer)    (Brand/Avoid)    (5-Point Tree)   Learning        Timeline
                 │                                               │
                 └───────────────┬───────────────────────────────┘
                                 │
                                 ↓
                     User Authorization Guardrail
                                 │
                                 ↓
                        Razorpay Test Mode
                                 │
                                 ↓
                     HMAC SHA256 Verification
                                 │
                                 ↓
                         Order Creation
```

---

## 🔥 Key Features

### 1. 🤖 11-Step Autonomous Purchase Agent Workflow
- **Full Workflow Stepper**: Executes an explicit 11-step pipeline:
  `Understand Request` $\rightarrow$ `Search Products` $\rightarrow$ `Filter Budget` $\rightarrow$ `Evaluate Specs` $\rightarrow$ `Compare Candidates` $\rightarrow$ `Select Best Product` $\rightarrow$ `Check Inventory` $\rightarrow$ `Dynamic AI Negotiation` $\rightarrow$ `Calculate Price` $\rightarrow$ `Stage Order` $\rightarrow$ `Request Human Approval`.
- **Hybrid Recommendation Engine**: Scores products using `30% preference match + 25% price fit + 20% rating + 15% specs + 10% popularity`.
- **Human-in-the-Loop Confirmation**: The AI never charges money automatically. Order creation requires explicit customer authorization before launching Razorpay Checkout.

### 2. 🏷️ Dynamic AI Coupon Negotiation Engine
- **Revenue-Optimized Offer Engine**: Evaluates Customer Purchase Intent Score, Inventory Level (scarcity vs clearance), and Cart Abandonment History.
- **Transparent AI Reasoning**:
  > *"This customer has high purchase intent, product has 18 units in inventory, and abandoned checkout 1 time. An AI-negotiated 7% coupon is optimal."*
- **10-Minute Expiry Countdown**: Live countdown timer (`⏳ Valid for 09:59`) creates urge to convert.

### 3. 🧠 Personalized Customer Memory Engine
- **Multi-Session Memory Persistence**: Scans customer chat prompts across sessions to remember:
  - **Preferred Brands**: `Sony`, `SoundMax`, `JBL`
  - **Avoided Traits**: `Bulky (>220g)`, `Heavy weight`
  - **Primary Use Cases**: `Travel`, `Calls`, `Online Classes`
- **Memory-Infused Scoring**: Applies +15 pts Brand Loyalty bonus and -25 pts Avoidance penalty in product ranking.

### 4. 🚨 Agent Cart Recovery Loop
- **5-Point AI Decision Analysis**: Scans abandoned carts and evaluates:
  `1. Product Demand` | `2. Customer Intent` | `3. Cart Value` | `4. Discount Usage` | `5. Recommended Incentive`
- **At-Risk Revenue Calculation**: Identifies total recoverable revenue (e.g. `Recover ₹73,494 At-Risk Revenue`).
- **1-Click Campaign Activation**: Dispatches recovery offer (`RECOVER5`) and logs execution in timeline.

### 5. 🔄 Closed-Loop Campaign Learning & Outcome Measurement
- **Pre vs Post Measurement**: Compares baseline vs outcome performance:
  - `Pre-Campaign Conversion`: `9.2%`
  - `Post-Campaign Conversion`: `12.8%` (`+39.1% Lift!`)
  - `Net Revenue Delta`: `+₹18,450`
  - `Gross Margin Impact`: `34.0% → 31.5% (-2.5%)`
- **AI Parameter Optimization**: Enables 1-click discount tuning (5% $\rightarrow$ 3%) to preserve gross margins while maintaining high conversion rates.

### 6. 🛡️ Security & Payment Safety
- **Server-Side Calculation**: Order totals are strictly calculated server-side from backend database records (never client parameters).
- **HMAC Signature Verification**: Verifies `razorpay_order_id`, `razorpay_payment_id`, and `razorpay_signature` server-side before marking orders as `PAID`.
- **Full Auditability**: Every agent action is logged with timing metrics into the **AI Decision Log Timeline**.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14+ App Router (TypeScript, Tailwind CSS, Lucide Icons, Recharts)
- **Backend**: Python FastAPI, SQLAlchemy, Pydantic, uvicorn
- **AI Agent Orchestration**: Multi-Tool Function Calling & Autonomous Reasoning Loops
- **Database**: SQLite / PostgreSQL with seed dataset of 105 realistic products
- **Payments**: Razorpay Test Mode API (HMAC SHA256 verification)

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

## 🧪 Running Automated Tests

```bash
cd backend
python -m pytest tests/test_api.py
```
All 8 test suites pass covering root health, product catalog, customer memory, purchase agent workflow, dynamic negotiation, cart recovery, closed-loop feedback, merchant growth, and Razorpay HMAC signature verification:
```text
tests/test_api.py ........                                               [100%]
======================== 8 passed in 2.30s ========================
```

---

## 📄 License
MIT
