const express = require('express');
const cors = require('cors');
const { createClient, chains } = require('genlayer-js');
const { privateKeyToAccount } = require('viem/accounts');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = process.env.CONTRACT_ADDRESS || '0x141D04fcbEB85BE92e8e12f1bB482020F9b37AF3';
const PK = process.env.PRIVATE_KEY || '';

// UUID mapping file (off-chain lookup: UUID -> sequential ID)
const UUID_MAP_FILE = path.join(__dirname, '.uuid-map.json');

function loadUuidMap() {
  try {
    return JSON.parse(fs.readFileSync(UUID_MAP_FILE, 'utf8'));
  } catch {
    return {};
  }
}

function saveUuidMap(map) {
  fs.writeFileSync(UUID_MAP_FILE, JSON.stringify(map, null, 2));
}

function generateAppId() {
  return crypto.randomUUID();
}

function findUuidBySequentialId(seqId) {
  const map = loadUuidMap();
  for (const [uuid, id] of Object.entries(map)) {
    if (id === seqId) return uuid;
  }
  return null;
}

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
    const seqId = Number(nextId) - 1;

    // Generate unique non-guessable UUID for user-facing ID
    const appId = generateAppId();

    // Persist UUID -> sequential ID mapping
    const map = loadUuidMap();
    map[appId] = seqId;
    saveUuidMap(map);

    res.json({ status: 'success', tx_hash: txHash, app_id: appId });
  } catch (err) {
    console.error('submitApplication error:', err);
    res.status(500).json({ detail: err.message });
  }
});

app.get('/api/applications/:id', async (req, res) => {
  try {
    let seqId = Number(req.params.id);

    // If id is not a number, look up the UUID map
    if (isNaN(seqId)) {
      const map = loadUuidMap();
      seqId = map[req.params.id];
      if (seqId === undefined) {
        return res.status(404).json({ detail: 'Application not found' });
      }
    }

    const raw = await read('getApplication', [seqId]);
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
    let seqId = Number(req.params.id);

    // If id is not a number, look up the UUID map
    if (isNaN(seqId)) {
      const map = loadUuidMap();
      seqId = map[req.params.id];
      if (seqId === undefined) {
        return res.status(404).json({ detail: 'Application not found' });
      }
    }

    const raw = await client.writeContract({
      address: CONTRACT,
      functionName: 'evaluateApplication',
      args: [seqId],
      gasLimit: GAS_LIMIT
    });
    
    let evaluation;
    try {
      evaluation = JSON.parse(raw);
    } catch (e) {
      evaluation = { result: raw };
    }
    
    res.json({ status: 'success', evaluation });
  } catch (err) {
    console.error('evaluateApplication error:', err);
    res.status(500).json({ detail: err.message });
  }
});

// Serve static files from root (for Render)
app.use(express.static('.'));

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`GrantGuard API on port ${PORT}`));
