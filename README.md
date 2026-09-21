# GrantGuard v2

Grant evaluation platform with **source-grounded evaluation**, **on-chain evidence verification**, **real escrow/payout**, and **payout address management**.

## Deployed on Studio Next (Chain 61997)

| Contract | Address |
|----------|---------|
| GrantGuard v2 | `0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0` |
| Explorer | https://explorer-studio-next.genlayer.com/address/0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 |

## Frontend

**URL:** https://adebisi1111.github.io/grantguard/

Features:
- Wallet connection (MetaMask)
- View all grants
- Create and fund grants
- Apply for grants with payout address
- Evaluate applications
- Release funds to payout address
- Cancel grants with refund

## Steward Request Fixes (Resubmission)

### 1. Payout Address per Applicant
- `submit_application()` now validates and stores `payout_address` (must be valid 0x + 40 hex chars)
- `release_funds()` sends funds to the stored payout address (not a placeholder)

### 2. Cancellation with Refund
- `cancel_grant()` marks grant as cancelled, refunds remaining balance to creator
- **Reject repeat cancellation**: Second call raises `ValueError("Grant already cancelled")`

### 3. Repository Tests
- 9 comprehensive tests covering:
  - Creating and funding multiple grants
  - Submitting applications with payout addresses
  - Evaluating and approving applications
  - Releasing funds to stored payout addresses
  - Cancellation with refund verification
  - Rejecting repeat cancellation
  - Invalid payout address rejection
  - Cross-grant balance verification

Run tests:
```bash
genlayer test tests/test_payouts_refunds.py --network studio-next
```

### 4. Fixed Browser Script
- **Parses correctly**: No syntax errors, all variables defined
- **Exposes funding action**: Fund Grant section with amount input and button
- **One configurable contract address**: Single `const CONTRACT = '0xba22...'` used everywhere

## Full Testing Flow

### Create Grant
```bash
genlayer write 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 create_grant \
  '"test-grant-1"' '"DeFi Innovation Grant"' '"Supporting DeFi projects"' \
  '"Open to all developers"' '"Technical merit and innovation"' \
  '"Max 10000 GEN per project"' '"GitHub repo with working demo"' '"2026-12-31"'
```

### Fund Grant
```bash
genlayer write 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 fund_grant \
  '"test-grant-1"' --value 1000000000000000000
```

### Submit Application (with payout address)
```bash
genlayer write 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 submit_application \
  '"test-grant-1"' '"DeFi Analytics Dashboard"' '"Real-time on-chain analytics"' \
  '"Solo developer"' '500000000000000000' \
  '"0x61fd0047595A30A067f1F21F3b28C4AE8A8e3Dc3"'
```

### Check Status
```bash
genlayer call 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 get_application '"app_0"'
```

### Evaluate
```bash
genlayer write 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 evaluate_application '"app_0"'
```

### Release Funds (to stored payout address)
```bash
genlayer write 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 release_funds '"app_0"'
```

### Cancel Grant (with refund)
```bash
genlayer write 0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0 cancel_grant '"test-grant-1"'
```

## Key Features for Steward Review

1. **Payout address validation** — Only valid Ethereum addresses accepted (0x + 40 hex)
2. **Funds go to stored address** — release_funds sends to applicant's payout_address
3. **Cancellation refunds** — Remaining balance returned to creator
4. **No double cancellation** — Second cancel attempt rejected
5. **Source-grounded evaluation** — Validators fetch evidence URLs via `gl.nondet.web.render()`
6. **Prompt-based consensus** — Uses `gl.eq_principle.prompt_comparative()` for LLM evaluation
7. **Real escrow** — Funds locked until evaluation completes
8. **Anti-cheat** — Validators independently verify evidence

## Tech Stack

- **Smart Contract:** GenLayer Python (v0.3.0 pattern)
- **Frontend:** Vanilla JS + Viem (GitHub Pages)
- **Network:** GenLayer Studio Next (61997)

## Submission Package

- GitHub: https://github.com/Adebisi1111/grantguard
- Live: https://adebisi1111.github.io/grantguard/
- Contract: `0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0`
- Tests: `tests/test_payouts_refunds.py`
