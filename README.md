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

## Testing Steps

### Prerequisites
1. MetaMask connected to **Studio Next** (chain 61997)
2. Wallet with GEN tokens
3. Open https://adebisi1111.github.io/grantguard/
4. Click **Connect Wallet** in top-right

### Step 1: Lookup Existing Grant
Go to **Grants** tab:
- Enter Grant ID: `test-grant-1`
- Click **View Grant**
- Grant details should appear

### Step 2: Apply for the Grant
On the grant detail page, fill in the application form:

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

### Step 3: Check Status
Go to **Check Status** tab:
- Enter App ID: `app_0`
- Click **Check Status**

Should show: `Status: SUBMITTED`

### Step 4: Evaluate Application
Click **Evaluate Application** button → sign in MetaMask

**Wait 1-3 minutes.** Validators:
1. Fetch evidence URL (`https://github.com/ethereum/ethereum-org-website`)
2. Compare against stored criteria ("Technical merit and innovation")
3. Reach consensus via `prompt_comparative`

### Step 5: Check Evaluation Result
After evaluation, check status again:
- Status: **REJECTED** (evidence doesn't match project description)
- Evaluation: `{eligibility: "PASS", criteria: "FAIL", budget: "PASS", evidence: "FAIL", final: "FAIL", reasons: [...]}`

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
Frontend (GitHub Pages) → MetaMask → GenLayer Studio Next
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
