# GrantGuard v2

Grant evaluation platform with **source-grounded evaluation**, **on-chain evidence verification**, and **real escrow/payout**.

## Links
- **Frontend:** https://adebisi1111.github.io/grantguard/
- **Contract:** `0x671990450Bab8f89144F50B6A619c6382E824172`
- **Explorer:** https://explorer-studio-next.genlayer.com/address/0x671990450Bab8f89144F50B6A619c6382E824172
- **Network:** GenLayer Studio Next (chain 61997)

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

## Testing via Studio UI

Since direct MetaMask writes require fee parameters that only the GenLayer SDK provides, testing should be done via Studio Next UI:

1. Go to https://studio-next.genlayer.com/address/0x671990450Bab8f89144F50B6A619c6382E824172
2. Connect wallet `0x61fd0047595A30A067f1F21F3b28C4AE8A8e3Dc3`
3. Test all methods through the UI

### Test Steps

| Step | Method | Args |
|------|--------|------|
| 1 Create | `create_grant` | `test-grant-1`, `DeFi Innovation Grant`, `Supporting DeFi projects`, `Open to all developers`, `Technical merit and innovation`, `Max 10000 GEN`, `GitHub repo`, `2026-12-31` |
| 2 Fund | `fund_grant` | `test-grant-1` + 1 GEN value |
| 3 Apply | `submit_application` | `test-grant-1`, `DeFi Analytics Dashboard`, `A comprehensive DeFi analytics dashboard`, `Team of 3`, `500000000000000000`, `https://example.com`, `https://github.com/ethereum/ethereum-org-website`, `https://github.com/ethereum/ethereum-org-website`, `info` |
| 4 Evaluate | `evaluate_application` | `app_0` → wait 1-3 min |
| 5 Check | `get_application` | `app_0` → see result |

### Expected Results

- `app_0` with mismatched GitHub (ethereum.org for "DeFi Dashboard") → **REJECTED**
- Validators fetch evidence on-chain and compare against stored criteria
- Evaluation JSON shows detailed reasons for rejection/approval

## Files

```
grantguard/
├── index.html          # Frontend (GitHub Pages)
├── server.js           # Backend API (Render) - uses GenLayer SDK
├── package.json        # Dependencies
├── fee-profile-studio-next.json  # Fee config for Studio Next
├── README.md           # This file
├── viem-iife.js        # Viem library (for encoding)
└── contracts/
    └── grantguard.py   # Smart contract source
```

## Contract Schema

```
create_grant(grant_id: string, name: string, description: string, eligibility: string, criteria: string, budget_rules: string, required_evidence: string, deadline: string) -> string
fund_grant(grant_id: string) payable -> string
submit_application(grant_id: string, project_name: string, project_description: string, team_info: string, requested_amount: uint256, website: string, github_url: string, evidence_urls: string, additional_info: string) -> string
evaluate_application(app_id: string) -> string
release_funds(app_id: string) -> string
cancel_grant(grant_id: string) -> bool
get_grant(grant_id: string) -> tuple(id, name, description, eligibility, criteria, budget_rules, required_evidence, deadline, creator, active, funded_amount, paid_out)
get_application(app_id: string) -> tuple(id, grant_id, project_name, project_description, team_info, requested_amount, website, github_url, evidence_urls, additional_info, status, evaluation)
get_stats() -> tuple(total_grants, total_applications)
```
