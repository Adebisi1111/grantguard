# GrantGuard v2

Grant evaluation platform with **source-grounded evaluation**, **on-chain evidence verification**, and **real escrow/payout**.

## Contract
- **Address:** `0x671990450Bab8f89144F50B6A619c6382E824172`
- **Network:** GenLayer Studio Next (chain 61997)
- **Explorer:** https://explorer-studio-next.genlayer.com/address/0x671990450Bab8f89144F50B6A619c6382E824172

## Deployment
- **Frontend:** GitHub Pages (index.html)
- **Backend:** Render (server.js) at https://grantguard.onrender.com

---

## Steward Concerns → Fixes

| Concern | Fix |
|---------|-----|
| Evaluation ignores stored grant rules | Prompt reads `eligibility`, `criteria`, `budget_rules`, `required_evidence` from contract storage |
| No evidence verification | Validators fetch evidence URLs via `gl.nondet.web.render()` on-chain |
| No escrow/payout | `fund_grant()` (payable) → `release_funds()` → `gl.pay()` transfers actual GEN |
| Unsafe fallback | Consensus failure → FAIL, not auto-PASS |

---

## Testing Steps

### Prerequisites
1. Go to https://adebisi1111.github.io/grantguard/index.html
2. Wallet: `0x61fd0047595A30A067f1F21F3b28C4AE8A8e3Dc3`
3. Network: Studio Next (chain 61997)

### Step 1: Create Grant
Click **Create Grant**, fill in:
- Grant ID: `test-grant-1`
- Grant Name: `DeFi Innovation Grant`
- Description: `Supporting DeFi projects`
- Eligibility Criteria: `Open to all developers`
- Evaluation Criteria: `Technical merit and innovation`
- Budget Rules: `Max 10000 GEN per project`
- Required Evidence: `GitHub repo with working demo`
- Deadline: `2026-12-31`

Click **Publish Grant** → sign in MetaMask

### Step 2: View Grants
Go back to **Grants** tab → click on your grant to view details

### Step 3: Fund Grant
From grant detail page:
- Click **Fund Grant** button
- Enter amount: `1000000000000000000` (1 GEN)
- Sign in MetaMask

### Step 4: Submit Application
From grant detail page, scroll to application form:
- Project Name: `DeFi Analytics Dashboard`
- Requested Amount (wei): `500000000000000000` (0.5 GEN)
- Project Description: `A comprehensive DeFi analytics dashboard with real-time data`
- Team Information: `Team of 3 senior developers`
- Website: `https://defi-dashboard.example.com`
- GitHub URL: `https://github.com/ethereum/ethereum-org-website`
- Evidence URLs: `https://github.com/ethereum/ethereum-org-website`
- Additional Info: `Built with React and TypeScript`

Click **Submit Application** → sign

Save your App ID (e.g., `app_0`)

### Step 5: Check Status
Go to **Check Status** tab → enter App ID → click **Check Status**

Should show:
- Status: SUBMITTED
- Evaluation: empty

### Step 6: Evaluate Application
Click **Evaluate Application** button → sign in MetaMask

**Wait 1-3 minutes.** Validators:
1. Fetch evidence URLs on-chain
2. Compare against stored criteria
3. Reach consensus via `prompt_comparative`

### Step 7: Check Evaluation Result
After evaluation, check status again. Should show:
- Status: APPROVED or REJECTED
- Evaluation: `{eligibility: "PASS", criteria: "PASS/FAIL", budget: "PASS/FAIL", evidence: "PASS/FAIL", final: "PASS/FAIL", reasons: [...]}`

### Step 8: Release Funds (if APPROVED)
If status is APPROVED, click **Release Funds** → sign

GEN is transferred from escrow to applicant via `gl.pay()`.

### Step 9: Check Final State
Verify:
- Grant `paid_out` increased
- Application status: PAID

---

## Expected Results

### Test Case 1: Legitimate Application (should APPROVED)
- Use a real GitHub repo that matches the project description
- All criteria should PASS
- Final: PASS → APPROVED
- Funds can be released

### Test Case 2: Mismatched Application (should REJECTED)
- Use a GitHub repo that doesn't match (e.g., ethereum.org website for a DeFi Dashboard project)
- Criteria FAIL
- Final: FAIL → REJECTED
- Funds NOT released

---

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

---

## File Structure
```
grantguard/
├── index.html          # Frontend app
├── server.js           # Backend relay (Express)
├── package.json        # Dependencies
├── fee-profile.json    # Fee config for Studio Next
└── contracts/
    └── grantguard.py   # Smart contract
```

## Build & Deploy

### Backend (Render)
1. Create Web Service from GitHub repo
2. Build command: `npm install`
3. Start command: `node server.js`
4. Environment:
   - `PRIVATE_KEY=0x023d076ab40ea46c59ac7ca7cecfaa2db5fa10b7a481aef27cf68e9cc5a8c0af`
   - `CONTRACT_ADDRESS=0x671990450Bab8f89144F50B6A619c6382E824172`

### Frontend (GitHub Pages)
1. Push to GitHub
2. Enable GitHub Pages in repo settings
3. Deploy from main branch
4. Access at `https://<username>.github.io/grantguard/index.html`
