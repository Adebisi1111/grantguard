# GrantGuard — AI-Verified Grant Evaluation

GrantGuard is an Intelligent Contract-based grant application evaluator built on GenLayer.

## What It Does

Grant administrators publish grants with criteria. Applicants submit applications without needing a wallet. The GenLayer Intelligent Contract evaluates each application against the published criteria and produces a transparent, explainable assessment.

**Result categories:**
- `PASS` — Application meets the criteria
- `REVIEW` — Human judgment needed
- `FAIL` — Application does not meet criteria
- `INSUFFICIENT_EVIDENCE` — Not enough information to evaluate

## Architecture

```
Frontend (GitHub Pages) → Backend (Render/Node.js) → GenLayer Blockchain
         ↑                      ↑
   No wallet needed          genlayer-js v1.1.8
   (any applicant)           (signing + submitting)
```

### Key Design Decisions

1. **No wallet required for applicants** — MetaMask is not needed; the backend handles transaction signing
2. **Backend relay pattern** — ethers.js cannot encode GenLayer transactions; the Node.js backend uses genlayer-js for all contract writes
3. **Deterministic evaluation** — Uses `gl.eq_principle.prompt_comparative()` for AI consensus where supported; falls back to deterministic rules when LLM consensus is unavailable
4. **Transparent reasoning** — Every evaluation explains why each criterion was marked PASS/REVIEW/FAIL/INSUFFICIENT_EVIDENCE

## Smart Contract API

### Writes (state-changing)

| Method | Args | Returns |
|--------|------|---------|
| `createGrant` | name, description, eligibility, criteria, budget_rules, required_evidence, deadline | `u256` grant_id |
| `submitApplication` | grant_id, project_name, project_description, team_info, requested_amount, website, github_url, evidence_urls, additional_info | `u256` app_id |
| `evaluateApplication` | app_id | `string` JSON evaluation |

### Views (read-only)

| Method | Args | Returns |
|--------|------|---------|
| `getGrant` | grant_id | `string` JSON |
| `getAllGrants` | — | `string` JSON array |
| `getApplication` | app_id | `string` JSON |
| `getApplicationsForGrant` | grant_id | `string` JSON array |
| `getNextGrantId` | — | `string` |
| `getNextAppId` | — | `string` |

## Evaluation Criteria

Each application is evaluated against:

- **ELIGIBILITY** — Does the applicant meet the grant requirements?
- **COMPLETENESS** — Is the application sufficiently detailed?
- **FEASIBILITY** — Is the technical approach sound?
- **BUDGET** — Is the requested amount reasonable and justified?
- **EVIDENCE** — Are supporting documents provided and verifiable?

Each criterion receives PASS/REVIEW/FAIL/INSUFFICIENT_EVIDENCE with documented reasoning.

## Evidence Handling

The system explicitly distinguishes between:

1. **Evidence supporting a claim** — Successfully verified and used
2. **Evidence contradicting a claim** — Flagged in conflicts
3. **Unavailable/unreachable evidence** — Marked as evidence_unreachable
4. **Insufficient evidence** — No evidence provided or verification failed

**Critical:** URL retrieval failure is NOT treated as proof of fraud. It is explicitly marked as unavailable evidence.

## Testing

```bash
cd grantguard
pytest tests/ -v
```

Test coverage (14 tests):
- ✅ Grant creation
- ✅ Grant criteria storage
- ✅ Valid application submission
- ✅ Invalid/incomplete application rejection
- ✅ Evaluation request
- ✅ PASS evaluation
- ✅ REVIEW evaluation
- ✅ FAIL evaluation
- ✅ INSUFFICIENT_EVIDENCE handling
- ✅ Unreachable evidence handling
- ✅ Evaluation result retrieval
- ✅ Application status transitions
- ✅ Multiple applications
- ✅ No data mixing between applicants

## Deployment

### Prerequisites

- Node.js v18+
- Python 3.11+
- GenLayer CLI (`genlayer`)
- A funded wallet on Bradbury testnet

### Deploy Contract

```bash
cd grantguard
genlayer deploy --contract contracts/grantguard.py
```

Record the contract address and update `backend/.env`.

### Deploy Backend

```bash
cd backend
npm install
# Set PRIVATE_KEY and CONTRACT_ADDRESS in .env
npm start
```

Or deploy to Render with:
- Build: `npm install`
- Start: `node server.js`

### Deploy Frontend

Push to GitHub Pages branch.

## Local Development

```bash
# Terminal 1: Backend
cd backend && npm start

# Terminal 2: Frontend (simple HTTP server)
cd frontend && python3 -m http.server 3000
```

Open http://localhost:3000

## Project Structure

```
grantguard/
├── contracts/
│   └── grantguard.py          # Intelligent Contract
├── backend/
│   ├── server.js              # Express API + contract relay
│   ├── deploy.js              # Deployment script
│   └── package.json
├── frontend/
│   └── index.html             # Single-page app
├── tests/
│   └── test_grantguard.py     # Pytest test suite
├── PROJECT_STATE.md           # Project tracking
└── README.md                  # This file
```

## Known Limitations

1. **LLM consensus** — `gl.eq_principle.prompt_comparative()` may revert on some testnet configurations. The fallback deterministic evaluation is used.
2. **No wallet** — Applicants are not cryptographically identified. This is intentional for MVP.
3. **No token distribution** — GrantGuard evaluates, it does not disburse funds.
4. **Evidence verification** — URL retrieval depends on network accessibility. Unreachable URLs are marked explicitly.
5. **Single active grant** — The MVP supports one active grant at a time.

## Future Improvements

- [ ] Optional wallet-based applicant identity (sign application submission)
- [ ] Onchain application signing
- [ ] DAO voting for final funding decisions
- [ ] Grant disbursement after approval
- [ ] Applicant reputation tracking
- [ ] Historical application analytics
- [ ] Multiple concurrent grants
- [ ] Human reviewer override mechanism
- [ ] Appeal process for rejected applications

## License

MIT
