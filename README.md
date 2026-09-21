# GrantGuard v2

Grant evaluation platform with **source-grounded evaluation**, **on-chain evidence verification**, and **real escrow/payout**.

## Deployed on Studio Next (Chain 61997)

| Contract | Address |
|----------|---------|
| GrantGuard v2 | `0x671990450Bab8f89144F50B6A619c6382E824172` |
| Explorer | https://explorer-studio-next.genlayer.com/address/0x671990450Bab8f89144F50B6A619c6382E824172 |

## Frontend

**URL:** https://adebisi1111.github.io/grantguard/

Features:
- Wallet connection (MetaMask)
- View all grants
- Apply for grants
- Check application status

## Full Testing Flow (via Studio UI)

### 1. Create Grant
```
genlayer write 0x671990450Bab8f89144F50B6A619c6382E824172 create_grant \
  '"test-grant-1"' '"DeFi Innovation Grant"' '"Supporting DeFi projects"' \
  '"Open to all developers"' '"Technical merit and innovation"' \
  '"Max 10000 GEN per project"' '"GitHub repo with working demo"' '"2026-12-31"'
```

### 2. Fund Grant
Send GEN to the contract to fund the grant.

### 3. Apply for Grant
```
genlayer write 0x671990450Bab8f89144F50B6A619c6382E824172 submit_application \
  '"test-grant-1"' '"DeFi Analytics Dashboard"' '"Real-time on-chain analytics"' \
  '"Solo developer"' '500000000000000000' '"https://example.com"' \
  '"https://github.com/test/defi-analytics"' '"https://github.com/test/defi-analytics"' '"Test info"'
```

### 4. Check Status
```
genlayer call 0x671990450Bab8f89144F50B6A619c6382E824172 get_application '"app_0"'
```

### 5. Evaluate
```
genlayer write 0x671990450Bab8f89144F50B6A619c6382E824172 evaluate_application '"app_0"'
```

### 6. Release Funds (if approved)
```
genlayer write 0x671990450Bab8f89144F50B6A619c6382E824172 release_funds '"app_0"'
```

## Key Features for Steward Review

1. **Source-grounded evaluation** — Validators fetch evidence URLs via `gl.nondet.web.render()` and compare against grant criteria
2. **Prompt-based consensus** — Uses `gl.eq_principle.prompt_comparative()` for LLM evaluation
3. **Real escrow** — Funds locked until evaluation completes
4. **Anti-cheat** — Validators independently verify evidence, caller cannot submit fake data

## Tech Stack

- **Smart Contract:** GenLayer Python (v0.3.0 pattern)
- **Frontend:** Vanilla JS + Viem (GitHub Pages)
- **Network:** GenLayer Studio Next (61997)

## Submission Package

- GitHub: https://github.com/Adebisi1111/grantguard
- Live: https://adebisi1111.github.io/grantguard/
- Contract: `0x671990450Bab8f89144F50B6A619c6382E824172`
