// GrantGuard v2 Backend - Studio Next
const express = require('express');
const cors = require('cors');
const { createClient } = require('genlayer-js');
const { privateKeyToAccount } = require('viem/accounts');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = process.env.CONTRACT_ADDRESS || '0x671990450Bab8f89144F50B6A619c6382E824172';
const PK = process.env.PRIVATE_KEY;

// Studio Next chain config
const studioNext = {
  id: 61997,
  name: 'Studio Next',
  rpcUrls: { default: { http: ['https://studio-next.genlayer.com/api'] } },
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 },
  testnet: true,
  consensusMainContract: { address: '0x0112Bf6e83497965A5fdD6Dad1E447a6E004271D', abi: [] },
  defaultNumberOfInitialValidators: 5,
  defaultConsensusMaxRotations: 3,
};

let account = null;
if (PK && PK.length === 66 && PK.startsWith('0x')) {
  try {
    account = privateKeyToAccount(PK);
  } catch (e) {
    console.error('Invalid PRIVATE_KEY');
  }
}
const client = account
  ? createClient({ chain: studioNext, account })
  : createClient({ chain: studioNext });

const GAS_LIMIT = 5000000n;

async function read(functionName, args = []) {
  return client.readContract({ address: CONTRACT, functionName, args });
}

async function write(functionName, args, value) {
  return client.writeContract({ address: CONTRACT, functionName, args, gasLimit: GAS_LIMIT, value });
}

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', contract: CONTRACT, has_private_key: !!PK });
});

app.get('/healthz', (req, res) => res.send('ok'));

// Create grant (returns grant_id string)
app.post('/api/grants', async (req, res) => {
  try {
    const { grant_id, name, description, eligibility, criteria, budget_rules, required_evidence, deadline } = req.body;
    if (!grant_id || !name || !description || !criteria) {
      return res.status(400).json({ detail: 'grant_id, name, description, criteria required' });
    }
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });

    const txHash = await write('create_grant', [
      grant_id, name, description, eligibility || '', criteria,
      budget_rules || '', required_evidence || '', deadline || ''
    ]);

    res.json({ status: 'success', tx_hash: txHash, grant_id: grant_id });
  } catch (err) {
    console.error('create_grant error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Get all grants (read individual grants by iterating IDs)
app.get('/api/grants', async (req, res) => {
  try {
    const stats = await read('get_stats');
    const total = Number(stats.total_grants);
    const grants = [];
    for (let i = 0; i < total; i++) {
      const grant = await read('get_grant', [`grant_${i}`]);
      if (grant && grant.id) {
        grants.push({
          id: grant.id,
          name: grant.name,
          description: grant.description,
          eligibility: grant.eligibility,
          criteria: grant.criteria,
          budget_rules: grant.budget_rules,
          required_evidence: grant.required_evidence,
          deadline: grant.deadline,
          active: grant.active,
          funded_amount: grant.funded_amount?.toString() || '0',
          paid_out: grant.paid_out?.toString() || '0',
          creator: grant.creator,
        });
      }
    }
    res.json(grants);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

app.get('/api/grants/:id', async (req, res) => {
  try {
    const grant = await read('get_grant', [req.params.id]);
    if (!grant || !grant.id) {
      return res.status(404).json({ detail: 'Grant not found' });
    }
    res.json({
      id: grant.id,
      name: grant.name,
      description: grant.description,
      eligibility: grant.eligibility,
      criteria: grant.criteria,
      budget_rules: grant.budget_rules,
      required_evidence: grant.required_evidence,
      deadline: grant.deadline,
      active: grant.active,
      funded_amount: grant.funded_amount?.toString() || '0',
      paid_out: grant.paid_out?.toString() || '0',
      creator: grant.creator,
    });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Fund grant (payable)
app.post('/api/grants/:id/fund', async (req, res) => {
  try {
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });
    const value = BigInt(req.body.value || '0');
    const txHash = await write('fund_grant', [req.params.id], value);
    res.json({ status: 'success', tx_hash: txHash });
  } catch (err) {
    console.error('fund_grant error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Submit application (returns app_id string like "app_0")
app.post('/api/applications', async (req, res) => {
  try {
    const { grant_id, project_name, project_description, team_info, requested_amount, website, github_url, evidence_urls, additional_info } = req.body;
    if (!grant_id || !project_name || !project_description) {
      return res.status(400).json({ detail: 'grant_id, project_name, project_description required' });
    }
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });

    const txHash = await write('submit_application', [
      grant_id, project_name, project_description, team_info || '',
      BigInt(requested_amount || '0'), website || '', github_url || '',
      evidence_urls || '', additional_info || ''
    ]);

    const stats = await read('get_stats');
    const appId = `app_${Number(stats.total_applications) - 1}`;

    res.json({ status: 'success', tx_hash: txHash, app_id: appId });
  } catch (err) {
    console.error('submit_application error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Get application by ID
app.get('/api/applications/:id', async (req, res) => {
  try {
    const app = await read('get_application', [req.params.id]);
    if (!app || !app.id) {
      return res.status(404).json({ detail: 'Application not found' });
    }
    res.json({
      id: app.id,
      grant_id: app.grant_id,
      project_name: app.project_name,
      project_description: app.project_description,
      team_info: app.team_info,
      requested_amount: app.requested_amount?.toString() || '0',
      website: app.website,
      github_url: app.github_url,
      evidence_urls: app.evidence_urls,
      additional_info: app.additional_info,
      status: app.status,
      evaluation: app.evaluation,
    });
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// Evaluate application
app.post('/api/applications/:id/evaluate', async (req, res) => {
  try {
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });
    const raw = await write('evaluate_application', [req.params.id], 0n);
    
    let evaluation;
    try {
      evaluation = JSON.parse(raw);
    } catch (e) {
      evaluation = { result: raw };
    }
    
    res.json({ status: 'success', evaluation });
  } catch (err) {
    console.error('evaluate_application error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Release funds
app.post('/api/applications/:id/release', async (req, res) => {
  try {
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });
    const raw = await write('release_funds', [req.params.id], 0n);
    res.json({ status: 'success', result: raw });
  } catch (err) {
    console.error('release_funds error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Cancel grant
app.post('/api/grants/:id/cancel', async (req, res) => {
  try {
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });
    const txHash = await write('cancel_grant', [req.params.id], 0n);
    res.json({ status: 'success', tx_hash: txHash });
  } catch (err) {
    console.error('cancel_grant error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Serve static files
app.use(express.static('.'));

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`GrantGuard v2 API on port ${PORT}`));
