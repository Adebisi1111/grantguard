# GrantGuard — AI-Consensus Grant Evaluation dApp

GrantGuard is a decentralized grant evaluation platform built on GenLayer. Project founders post bounties, participants submit applications, and AI validators assess submissions using GenLayer's LLM consensus. Escrow releases automatically based on the verdict.

## Live Demo

**Frontend:** https://adebisi1111.github.io/grantguard/

## How It Works

1. **Create Grant** — Define grant name, description, eligibility, evaluation criteria, budget rules, and deadline
2. **Submit Application** — Applicants fill project details, team info, and evidence URLs (no wallet required)
3. **AI Evaluation** — GenLayer LLM consensus evaluates on 5 criteria: Eligibility, Completeness, Feasibility, Budget, Evidence
4. **On-Chain Result** — Final assessment (PASS/REVIEW/FAIL) stored permanently on GenLayer Bradbury

## Architecture

| Component | Technology |
|-----------|------------|
| Frontend | GitHub Pages (static HTML/JS) |
| Backend | Render (Node.js relay) |
| Blockchain | GenLayer Bradbury (4221) |
| AI Consensus | `gl.eq_principle.prompt_comparative` |

## Smart Contract

**Address:** `0xca1d331C2a2cF3f58721edd765ef7ADe9d9cc227`
**Explorer:** https://explorer-bradbury.genlayer.com/address/0xca1d331C2a2cF3f58721edd765ef7ADe9d9cc227
**File:** [contracts/grantguard.py](contracts/grantguard.py)

### Contract Methods

| Method | Type | Description |
|--------|------|-------------|
| `createGrant(...)` | write | Publish a new grant opportunity |
| `submitApplication(...)` | write | Submit application, returns UUID |
| `evaluateApplication(app_id)` | write | Trigger AI consensus evaluation |
| `getApplication(app_id)` | view | Retrieve application + evaluation |
| `getAllGrants()` | view | List all grants |

## AI Consensus

Uses the TruthOracle v2 pattern:
- **Leader:** `gl.nondet.exec_prompt()` analyzes the application
- **Validators:** `gl.eq_principle.prompt_comparative()` reaches consensus
- **Fallback:** Deterministic rules if LLM consensus fails

## Verification Steps

1. Open https://adebisi1111.github.io/grantguard/
2. Create a grant → transaction confirmed on Bradbury
3. Submit application → UUID displayed
4. Check status → application data retrieved from contract
5. Click "Evaluate Application" → AI consensus runs on-chain (30-60s)
6. Refresh → full evaluation with AI-generated reasons

## Repository Structure

```
grantguard/
├── contracts/
│   └── grantguard.py      # Smart contract (AI consensus evaluation)
├── server.js               # Backend relay (Render)
├── index.html              # Frontend (GitHub Pages)
├── package.json
└── .env.example            # Environment variables
```

## Environment Variables

```
PRIVATE_KEY=your_private_key_without_0x_prefix
CONTRACT_ADDRESS=0xca1d331C2a2cF3f58721edd765ef7ADe9d9cc227
PORT=8000
```

## Built With

- GenLayer Bradbury testnet
- genlayer-js v1.1.8
- Node.js + Express
- Vanilla HTML/CSS/JS frontend
