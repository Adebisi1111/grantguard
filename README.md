# GrantGuard v2

Grant evaluation platform with **source-grounded evaluation**, **on-chain evidence verification**, and **real escrow/payout**.

## Links
- **Frontend:** https://adebisi1111.github.io/grantguard/
- **Contract:** `0x671990450Bab8f89144F50B6A619c6382E824172`
- **Explorer:** https://explorer-studio-next.genlayer.com/address/0x671990450Bab8f89144F50B6A619c6382E824172
- **Network:** GenLayer Studio Next (chain 61997)

## Steward Concerns → Fixes

| Concern | Fix |
|---------|-----|
| Evaluation ignores stored grant rules | Prompt reads `eligibility`, `criteria`, `budget_rules`, `required_evidence` from contract storage and checks each against the application |
| No evidence verification | Validators fetch evidence URLs via `gl.nondet.web.render()` on-chain before scoring |
| No escrow/payout | `fund_grant()` (payable) → `release_funds()` → `gl.pay()` transfers actual GEN |
| Unsafe fallback | Consensus failure → FAIL (not auto-PASS) |

## Contract Source

```python
# v0.3.0
# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

# Key methods:
# - create_grant(grant_id, name, description, eligibility, criteria, budget_rules, required_evidence, deadline) → str
# - fund_grant(grant_id) payable → str
# - submit_application(grant_id, project_name, project_description, team_info, requested_amount, website, github_url, evidence_urls, additional_info) → str
# - evaluate_application(app_id) → str (validators fetch evidence + consensus)
# - release_funds(app_id) → str (transfers GEN via gl.pay)
# - get_grant(grant_id) → Grant
# - get_application(app_id) → Application
```

## Testing Steps

### Prerequisites
1. MetaMask connected to **Studio Next** (chain 61997)
2. Wallet with GEN tokens
3. Open https://adebisi1111.github.io/grantguard/
4. Click **Connect Wallet** in top-right

### Step 1: Create Grant
Go to **Create Grant** tab:

| Field | Value |
|-------|-------|
| Grant ID | `defi-grant-1` |
| Grant Name | `DeFi Innovation Grant` |
| Description | `Supporting DeFi projects` |
| Eligibility Criteria | `Open to all developers` |
| Evaluation Criteria | `Technical merit and innovation` |
| Budget Rules | `Max 10000 GEN per project` |
| Required Evidence | `GitHub repo with working demo` |
| Deadline | `2026-12-31` |

Click **Publish Grant** → sign in MetaMask

### Step 2: View Grants
Go to **Grants** tab → click your grant to view details

### Step 3: Fund Grant
On grant detail page:
- Click **Fund Grant**
- Enter amount: `1000000000000000000` (1 GEN)
- Sign in MetaMask

### Step 4: Submit Application
On grant detail page, scroll to **Apply for this Grant**:

| Field | Value |
|-------|-------|
| Project Name | `DeFi Analytics Dashboard` |
| Requested Amount (wei) | `500000000000000000` (0.5 GEN) |
| Project Description | `A comprehensive DeFi analytics dashboard` |
| Team Information | `Team of 3 developers` |
| Website | `https://defi-dashboard.example.com` |
| GitHub URL | `https://github.com/ethereum/ethereum-org-website` |
| Evidence URLs | `https://github.com/ethereum/ethereum-org-website` |
| Additional Info | `Built with React` |

Click **Submit Application** → sign in MetaMask

Note the App ID shown (e.g., `app_0`)

### Step 5: Check Status
Go to **Check Status** tab:
- Enter App ID: `app_0`
- Click **Check Status**

Should show: `Status: SUBMITTED`

### Step 6: Evaluate Application
Click **Evaluate Application** button → sign in MetaMask

**Wait 1-3 minutes.** Validators:
1. Fetch evidence URL (`https://github.com/ethereum/ethereum-org-website`)
2. Compare against stored criteria ("Technical merit and innovation")
3. Reach consensus via `prompt_comparative`

### Step 7: Check Evaluation Result
After evaluation, check status again:
- Status: **REJECTED** (evidence doesn't match project description)
- Evaluation: `{eligibility: "PASS", criteria: "FAIL", budget: "PASS", evidence: "FAIL", final: "FAIL", reasons: [...]}`

### Step 8: Test Approved Application
Create a new grant and submit with a matching repo:

| Field | Value |
|-------|-------|
| Grant ID | `ai-grant-1` |
| Grant Name | `AI Project Grant` |
| Grant ID (app) | `ai-grant-1` |
| Project Name | `Ethereum Analytics` |
| GitHub URL | `https://github.com/ethereum/ethereum-org-website` |
| Evidence URLs | `https://github.com/ethereum/ethereum-org-website` |
| Project Description | `Analytics dashboard for ethereum.org` |

Evaluate → should show **APPROVED** (evidence matches project description)

### Step 9: Release Funds (if APPROVED)
Click **Release Funds** → sign in MetaMask

GEN is transferred from escrow to applicant via `gl.pay()`.

### Expected Results

| Test | GitHub URL | Project | Result |
|------|------------|---------|--------|
| Mismatched | ethereum.org | DeFi Dashboard | **REJECTED** |
| Matched | ethereum.org | Ethereum Analytics | **APPROVED** |

## Contract Methods

| Method | Type | Description |
|--------|------|-------------|
| `create_grant` | write | Create grant with rules stored on-chain |
| `fund_grant` | payable | Deposit GEN into grant escrow |
| `submit_application` | write | Submit with evidence URLs |
| `evaluate_application` | write | Consensus evaluation (validators fetch evidence) |
| `release_funds` | write | Pay approved applicant from escrow |
| `cancel_grant` | write | Cancel grant, refund creator |
| `get_grant` | view | Read grant details |
| `get_application` | view | Read application details |
| `get_stats` | view | Platform statistics |

## Architecture

```
Frontend (GitHub Pages)
    ↕ MetaMask
Backend (Render) → GenLayer Studio Next
    ↕
Contract: 0x671990450Bab8f89144F50B6A619c6382E824172
```

## Files

```
grantguard/
├── index.html          # Frontend (GitHub Pages)
├── server.js           # Backend relay (Render)
├── package.json        # Dependencies (genlayer-js v2.0.0-rc.1)
├── fee-profile.json    # Fee config for Studio Next
├── README.md           # This file
└── contracts/
    └── grantguard.py   # Smart contract source
```

## Build & Deploy

### Backend (Render)
1. Create Web Service from https://github.com/Adebisi1111/grantguard
2. Build: `npm install`
3. Start: `node server.js`
4. Env: `PRIVATE_KEY=0x023d...c0af`, `CONTRACT_ADDRESS=0x6719...4172`

### Frontend (GitHub Pages)
1. Push to https://github.com/Adebisi1111/grantguard
2. GitHub Pages → Source: gh-pages branch
3. Access at https://adebisi1111.github.io/grantguard/
