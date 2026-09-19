const express = require('express');
const cors = require('cors');
const { createClient, chains } = require('genlayer-js');
const { privateKeyToAccount } = require('viem/accounts');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = process.env.CONTRACT_ADDRESS || '0xA8Ff9ABF68011Cd0aa5BF5cdE71Ab22AD0665231';
const PK = process.env.PRIVATE_KEY || '';

if (!PK) console.error('WARNING: PRIVATE_KEY not set!');
const account = PK ? privateKeyToAccount(PK) : null;
const client = account
  ? createClient({ chain: chains.testnetBradbury, account })
  : createClient({ chain: chains.testnetBradbury });

const GAS_LIMIT = 5000000n;

async function read(functionName, args = []) {
  return client.readContract({ address: CONTRACT, functionName, args });
}

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', contract: CONTRACT, has_private_key: !!PK });
});

app.get('/healthz', (req, res) => res.send('ok'));

app.post('/api/grants', async (req, res) => {
  try {
    const { name, description, eligibility, criteria, budget_rules, required_evidence, deadline } = req.body;
    if (!name || !description || !criteria) {
      return res.status(400).json({ detail: 'name, description, criteria required' });
    }
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });

    const txHash = await client.writeContract({
      address: CONTRACT,
      functionName: 'createGrant',
      args: [name, description, eligibility || '', criteria, budget_rules || '', required_evidence || '', deadline || ''],
      gasLimit: GAS_LIMIT
    });

    const nextId = await read('getNextGrantId');
    const grantId = Number(nextId) - 1;

    res.json({ status: 'success', tx_hash: txHash, grant_id: grantId });
  } catch (err) {
    console.error('createGrant error:', err);
    res.status(500).json({ detail: err.message });
  }
});

app.get('/api/grants', async (req, res) => {
  try {
    const raw = await read('getAllGrants');
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

app.get('/api/grants/:id', async (req, res) => {
  try {
    const raw = await read('getGrant', [Number(req.params.id)]);
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

app.post('/api/applications', async (req, res) => {
  try {
    const { grant_id, project_name, project_description, team_info, requested_amount, website, github_url, evidence_urls, additional_info } = req.body;
    if (!grant_id && grant_id !== 0 || !project_name || !project_description) {
      return res.status(400).json({ detail: 'grant_id, project_name, project_description required' });
    }
    if (!PK) return res.status(500).json({ detail: 'PRIVATE_KEY not set' });

    const txHash = await client.writeContract({
      address: CONTRACT,
      functionName: 'submitApplication',
      args: [Number(grant_id), project_name, project_description, team_info || '', requested_amount || '', website || '', github_url || '', evidence_urls || '', additional_info || ''],
      gasLimit: GAS_LIMIT
    });

    const nextId = await read('getNextAppId');
    const appId = Number(nextId) - 1;

    res.json({ status: 'success', tx_hash: txHash, app_id: appId });
  } catch (err) {
    console.error('submitApplication error:', err);
    res.status(500).json({ detail: err.message });
  }
});

app.get('/api/applications/:id', async (req, res) => {
  try {
    const raw = await read('getApplication', [Number(req.params.id)]);
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

app.get('/api/grants/:grantId/applications', async (req, res) => {
  try {
    const raw = await read('getApplicationsForGrant', [Number(req.params.grantId)]);
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

app.post('/api/applications/:id/evaluate', async (req, res) => {
  try {
    const raw = await client.writeContract({
      address: CONTRACT,
      functionName: 'evaluateApplication',
      args: [Number(req.params.id)],
      gasLimit: GAS_LIMIT
    });
    res.json({ status: 'success', evaluation: JSON.parse(raw) });
  } catch (err) {
    console.error('evaluateApplication error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Serve static files from root (for Render)
app.use(express.static('.'));

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`GrantGuard API on port ${PORT}`));
