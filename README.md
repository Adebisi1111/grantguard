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
| Evaluation ignores stored grant rules | Prompt reads `eligibility`, `criteria`, `budget_rules`, `required_evidence` from contract storage |
| No evidence verification | Validators fetch evidence URLs via `gl.nondet.web.render()` on-chain |
| No escrow/payout | `fund_grant()` (payable) → `release_funds()` → `gl.pay()` transfers actual GEN |
| Unsafe fallback | Consensus failure → FAIL (not auto-PASS) |

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
Go to **Grants** tab → grants should appear automatically (searches test-grant-1, test-grant-2, grant_0, grant_1, etc.)

### Step 3: Fund Grant
Click on your grant → click **Fund Grant** → enter `1000000000000000000` (1 GEN) → sign

### Step 4: Submit Application
From grant detail page:

| Field | Value |
|-------|-------|
| Project Name | `DeFi Analytics Dashboard` |
| Requested Amount (wei) | `500000000000000000` (0.5 GEN) |
| Project Description | `A comprehensive DeFi analytics dashboard with real-time data` |
| Team Information | `Team of 3 senior developers` |
| Website | `https://defi-dashboard.example.com` |
| GitHub URL | `https://github.com/ethereum/ethereum-org-website` |
| Evidence URLs | `https://github.com/ethereum/ethereum-org-website` |
| Additional Info | `Built with React and TypeScript` |

Click **Submit Application** → sign → note the App ID (app_0)

### Step 5: Check Status
Go to **Check Status** tab → enter `app_0` → click **Check Status**

Should show: `Status: SUBMITTED`

### Step 6: Evaluate Application
Click **Evaluate Application** button → sign in MetaMask → wait 1-3 minutes

### Step 7: Check Evaluation Result
Check status again:
- Status: **REJECTED** (evidence doesn't match project description)
- Evaluation shows reasons like "The provided GitHub repository is for the official ethereum.org website, not a unique DeFi Analytics Dashboard"

### Step 8: Release Funds (if APPROVED)
If status is APPROVED, click **Release Funds** → sign

## Expected Results

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

## Files

```
grantguard/
├── index.html          # Frontend (GitHub Pages) - MetaMask direct
├── server.js           # Backend relay (Render) - optional
├── package.json        # Dependencies
├── fee-profile.json    # Fee config for Studio Next
├── README.md           # This file
└── contracts/
    └── grantguard.py   # Smart contract source
```
