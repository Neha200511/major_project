# CHILD-SAFE DIGITAL ENVIRONMENT MANAGER

> **"Understand the conversation. Detect the risk. Protect the child."**  
> *Privacy-first AI for safer digital communication.*

---

## 1. Project Overview

The **Child-Safe Digital Environment Manager** is an enterprise-grade full-stack research platform developed as a college major project. It establishes a controlled, multi-user communication environment where children can interact with approved friends in real time, while a sophisticated multi-layer AI pipeline continuously monitors conversational context for grooming, cyberbullying, harassment, threats, and privacy risks.

Unlike simplistic keyword blockers that flag harmless phrases (e.g., *"The villain was killed in that movie"* or *"We killed them in that football match"*), this platform performs contextual NLP, progression tracking, power dynamics evaluation, and behavioral trend analysis.

---

## 2. Problem Statement

Conventional parental control software relies on blunt keyword blacklists, screenshot scrapers, or intrusive keyloggers. This results in two major failures:
1. **Severe False Positives:** Normal discussions involving entertainment, gaming, sports slang, or friendly humor trigger unnecessary alarms.
2. **Gross Privacy Violations:** Parents receive unrestricted surveillance over private conversations, destroying trust between child and guardian.
3. **Detection Blindness:** Sophisticated grooming and social engineering patterns do not use explicit banned words; rather, they escalate subtly through secrecy, isolation, and gradual boundary-testing.

---

## 3. Objectives

- **Context-Aware Safety:** Analyze the full conversation flow and both conversation participants instead of isolated strings.
- **Privacy by Design:** Provide parents with explainable risk summaries, severity levels, and category breakdowns without exposing raw message transcripts.
- **True Multi-Client Architecture:** Support independent sessions from separate computers (Child, Parent, Contact A, Contact B, Contact C, Contact D).
- **Multi-Layer Risk Fusion:** Synthesize fast pattern heuristics, trained machine learning classification, contextual dynamics, and historical behavioral trends.
- **Alert Fatigue Prevention:** Enforce intelligent cooldown periods, multi-layer validation, and delta-escalation triggers.

---

## 4. System Architecture

```
                    ┌─────────────────────────┐
                    │      Client Browser     │
                    │ (Child / Parent / Peer) │
                    └────────────┬────────────┘
                                 │
                   HTTP REST API │ WebSocket (Real-Time)
                                 ▼
                    ┌─────────────────────────┐
                    │    FastAPI Gateway      │
                    │   JWT Authentication    │
                    │   Connection Manager    │
                    └────────────┬────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
        ┌─────────────────────┐     ┌─────────────────────┐
        │   MongoDB Engine    │     │  Monitoring Engine  │
        │ - users             │     │ (Asynchronous Flow) │
        │ - conversations     │     └──────────┬──────────┘
        │ - messages          │                │
        │ - risk_scores       │       ┌────────┴────────┐
        │ - alerts            │       ▼                 ▼
        │ - behaviour_profiles│  Layer 1: Rules   Layer 2: ML Classifier
        └─────────────────────┘  Layer 3: Context Layer 4: Behaviour Trends
                                      │                 │
                                      └────────┬────────┘
                                               ▼
                                      Risk Fusion Engine
                                               │
                                      Alert Decision Core
                                               │
                                      (Push to Parent WS)
```

---

## 5. Technology Stack

### Backend
- **Framework:** Python 3.13 + FastAPI (Asynchronous REST & WebSockets)
- **ASGI Server:** Uvicorn
- **Database:** MongoDB 7.0+ (PyMongo Driver with custom indexing)
- **Security:** Argon2 / BCrypt password hashing, PyJWT authentication, RBAC middleware

### Machine Learning & NLP
- **Libraries:** Scikit-Learn 1.9+, NLTK, TextBlob, NumPy, SciPy
- **Vectorization:** Sublinear TF-IDF (1-3 ngrams, 5,000 max features)
- **Classifier:** Multi-class Logistic Regression with class-weight balancing
- **Evaluation:** Macro Precision, Recall, F1 score, and Confusion Matrix telemetry

### Frontend
- **Framework:** React 19 + TypeScript + Vite 8
- **Styling:** Tailwind CSS v4 (Custom cybersecurity glassmorphism theme)
- **Charts:** Recharts (Responsive Line & Bar Telemetry)
- **Icons:** Lucide React
- **Networking:** Axios HTTP client & Native WebSocket Client with auto-reconnection

---

## 6. Multi-Layer Monitoring Pipeline

### Layer 1: Fast Rule / Pattern Engine (20% Weight)
- Evaluates conversational patterns across 8 risk categories: `GROOMING`, `CYBERBULLYING`, `THREAT`, `SELF_HARM`, `PRIVACY_RISK`, `MANIPULATION`, `SCAM`, `SEXUAL_SAFETY`.
- **Context modifiers:** Automatically scales down threat scores by 70% if pop culture/entertainment/sports terms are detected or laughing emojis are present.

### Layer 2: Machine Learning Text Classifier (25% Weight)
- Pre-trained TF-IDF vectorizer + balanced multi-class model (`ml/model/model.pkl`).
- Generates probability distributions across categories with confidence mapping:
  - High confidence `SAFE` (>70%) &rarr; Score 0–10
  - High confidence Risky (>60%) &rarr; Score 50–90

### Layer 3: Conversational Context & Power Dynamics (25% Weight)
- Inspects the rolling window of the last 20 messages across both participants.
- Detects velocity shifts, topic pivots, and directional grooming (e.g. adult/older peer probing personal life, asking child to keep secrets).

### Layer 4: Historical Behavioral Trend Tracking (20% Weight)
- Maintains persistent `behaviour_profiles` for each unique `conversation_id`.
- Computes trajectory: `Increasing ↗`, `Stable →`, or `Decreasing ↘`.
- Applies multi-day risk amplification if suspicion compounds gradually.

### Layer 5: Optional Deep Semantic LLM Analysis (10% Weight)
- Conditionally invoked only when preliminary layers indicate moderate risk (&ge; 30%) and a valid external API key is provided.
- If unconfigured, the 10% weight is automatically redistributed proportionally to Layers 1–4.

---

## 7. Database Collections & Schema

| Collection | Key Fields | Description |
|---|---|---|
| `users` | `_id`, `name`, `email`, `password_hash`, `role`, `status` | Registered users (`CHILD`, `PARENT`, `CONTACT`) |
| `conversations` | `conversation_id`, `participants`, `last_message_at` | Unique communication channels (e.g. `CHAT001`) |
| `messages` | `message_id`, `conversation_id`, `sender_id`, `content`, `timestamp` | Stored chat messages with delivery status |
| `risk_scores` | `risk_id`, `conversation_id`, `risk_score`, `severity`, `layer_scores` | Internal audit scores from the risk fusion engine |
| `alerts` | `alert_id`, `child_id`, `conversation_id`, `severity`, `status` | Parent notifications (`NEW`, `ACKNOWLEDGED`, `RESOLVED`) |
| `behaviour_profiles` | `conversation_id`, `risk_history`, `trend`, `average_risk` | Longitudinal behavioral trends per conversation |
| `parent_child_links` | `parent_id`, `child_id` | Enforces relational access control boundaries |

---

## 8. Demo Seed Accounts

The platform includes a deterministic seed script with pre-configured multi-user scenarios:

| Role | Name | Email | Password | Scenario / Characteristics |
|---|---|---|---|---|
| **Parent** | Parent User | `parent@example.com` | `demo123` | Master guardian account with full security dashboard |
| **Child** | Nimai | `child@example.com` | `demo123` | Child account with 4 distinct contact channels |
| **Contact** | Alice | `alice@example.com` | `demo123` | **SAFE:** Academic & exam preparation discussion |
| **Contact** | Bob | `bob@example.com` | `demo123` | **FALSE POSITIVE:** Movie discussion using words like *"killed"* |
| **Contact** | Charlie | `charlie@example.com` | `demo123` | **HIGH RISK:** Gradual grooming, secrecy, & private photo request |
| **Contact** | David | `david@example.com` | `demo123` | **SAFE:** Sports slang (*"we killed them in cricket"*) |

---

## 9. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node.js 24)
- MongoDB Server running locally on `localhost:27017`

### Step 1: Clone & Environment Variables
```bash
git clone <repo-url> child-safe-platform
cd child-safe-platform

# Review .env
cp .env.example .env
```

### Step 2: Backend Setup & ML Training
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Train the ML Classifier (Generates model.pkl & metrics.json)
python -m ml.train

# Seed the MongoDB database with demo users & conversations
python -m scripts.seed_data
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm run build
```

---

## 10. Running the Application

### Option A: Development Mode (Two Terminals)

**Terminal 1 (Backend API & WebSockets):**
```bash
cd child-safe-platform
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend Client):**
```bash
cd child-safe-platform/frontend
npm run dev
```

Visit `http://localhost:5173` in your browser.

### Option B: Docker Compose
```bash
docker-compose up --build
```

---

## 11. Testing & Demonstration Workflow

To demonstrate multi-client real-time behavior:
1. Open **Browser 1 (e.g. Chrome normal):** Sign in as `child@example.com` (`demo123`).
2. Open **Browser 2 (e.g. Incognito window):** Sign in as `charlie@example.com` (`demo123`).
3. Open **Browser 3 (e.g. Edge or second window):** Sign in as `parent@example.com` (`demo123`).
4. In Browser 2 (Charlie), send messages to the Child testing secrecy and requests (*"Don't tell your parents"*).
5. Watch the **Parent Dashboard** in Browser 3 immediately trigger an **animated real-time alert pop-up** via WebSockets without page reload.
6. Verify that chatting with Bob about movies (*"The villain killed everyone in that scene"*) produces **zero alerts** and remains classified as `SAFE (12%)`.

---

## 12. Security & Privacy Guarantees

- **No Passwords in Code:** Passwords hashed with salt via modern BCrypt.
- **Granular RBAC:** Child and Contacts are strictly prevented from querying parent endpoints or viewing peer channels.
- **Privacy-Preserving Reporting:** Transcripts are not dumped in plain text into parent summaries.
- **Fail-Safe Architecture:** If optional LLMs or ML files fail to load, the chat remains 100% responsive and falls back cleanly on pattern heuristics.

---

## 13. Academic Disclaimer & Future Roadmap

*Disclaimer: This system provides AI-assisted probabilistic risk analysis and does not claim 100% detection accuracy.*

### Future Roadmap
- Multilingual and Hinglish / regional dialect NLP support.
- Optical Character Recognition (OCR) and computer vision for image safety.
- Android and iOS React Native client applications.
- Differential privacy & federated on-device ML model updates.
