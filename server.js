// GrantGuard v2 Backend - Uses GenLayer SDK for proper encoding
const express = require('express');
const cors = require('cors');
const { createClient, createAccount, chains } = require('genlayer-js');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = '0x671990450Bab8f89144F50B6A619c6382E824172';
const PK = process.env.PRIVATE_KEY || '0x023d7e4e950d8cea0d8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8';

// Create GenLayer client
const account = createAccount(PK);
const client = createClient({
    chain: chains.studioDevnet,
    account: account
});

// ABI matching the contract schema
const ABI = [
    { name: 'create_grant', type: 'function', stateMutability: 'nonpayable', inputs: [{ name: 'grant_id', type: 'string' }, { name: 'name', type: 'string' }, { name: 'description', type: 'string' }, { name: 'eligibility', type: 'string' }, { name: 'criteria', type: 'string' }, { name: 'budget_rules', type: 'string' }, { name: 'required_evidence', type: 'string' }, { name: 'deadline', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'fund_grant', type: 'function', stateMutability: 'payable', inputs: [{ name: 'grant_id', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'submit_application', type: 'function', stateMutability: 'nonpayable', inputs: [{ name: 'grant_id', type: 'string' }, { name: 'project_name', type: 'string' }, { name: 'project_description', type: 'string' }, { name: 'team_info', type: 'string' }, { name: 'requested_amount', type: 'uint256' }, { name: 'website', type: 'string' }, { name: 'github_url', type: 'string' }, { name: 'evidence_urls', type: 'string' }, { name: 'additional_info', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'evaluate_application', type: 'function', stateMutability: 'nonpayable', inputs: [{ name: 'app_id', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'release_funds', type: 'function', stateMutability: 'nonpayable', inputs: [{ name: 'app_id', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'cancel_grant', type: 'function', stateMutability: 'nonpayable', inputs: [{ name: 'grant_id', type: 'string' }], outputs: [{ type: 'bool' }] },
    { name: 'get_grant', type: 'function', stateMutability: 'view', inputs: [{ name: 'grant_id', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'get_application', type: 'function', stateMutability: 'view', inputs: [{ name: 'app_id', type: 'string' }], outputs: [{ type: 'string' }] },
    { name: 'get_stats', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'string' }] }
];

// Health check
app.get('/api/health', async (req, res) => {
    try {
        const schema = await client.readContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'get_stats',
            args: []
        });
        res.json({ status: 'ok', contract: CONTRACT, account: account.address, stats: schema });
    } catch (e) {
        res.json({ status: 'ok', contract: CONTRACT, account: account.address, error: e.message });
    }
});

// Read grant
app.get('/api/grants/:id', async (req, res) => {
    try {
        const result = await client.readContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'get_grant',
            args: [req.params.id]
        });
        res.json({ id: req.params.id, data: result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Read application
app.get('/api/applications/:id', async (req, res) => {
    try {
        const result = await client.readContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'get_application',
            args: [req.params.id]
        });
        res.json({ id: req.params.id, data: result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Create grant
app.post('/api/grants', async (req, res) => {
    try {
        const { grant_id, name, description, eligibility, criteria, budget_rules, required_evidence, deadline } = req.body;
        const hash = await client.writeContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'create_grant',
            args: [grant_id, name, description, eligibility, criteria, budget_rules, required_evidence, deadline]
        });
        res.json({ tx_hash: hash, grant_id });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Fund grant
app.post('/api/grants/:id/fund', async (req, res) => {
    try {
        const { value } = req.body;
        const hash = await client.writeContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'fund_grant',
            args: [req.params.id],
            value: BigInt(value)
        });
        res.json({ tx_hash: hash });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Submit application
app.post('/api/applications', async (req, res) => {
    try {
        const { grant_id, project_name, project_description, team_info, requested_amount, website, github_url, evidence_urls, additional_info } = req.body;
        const hash = await client.writeContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'submit_application',
            args: [grant_id, project_name, project_description, team_info, BigInt(requested_amount), website, github_url, evidence_urls, additional_info]
        });
        res.json({ tx_hash: hash });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Evaluate application
app.post('/api/applications/:id/evaluate', async (req, res) => {
    try {
        const hash = await client.writeContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'evaluate_application',
            args: [req.params.id]
        });
        res.json({ tx_hash: hash });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Release funds
app.post('/api/applications/:id/release', async (req, res) => {
    try {
        const hash = await client.writeContract({
            address: CONTRACT,
            abi: ABI,
            functionName: 'release_funds',
            args: [req.params.id]
        });
        res.json({ tx_hash: hash });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`GrantGuard v2 API on port ${PORT}`);
    console.log(`Account: ${account.address}`);
    console.log(`Contract: ${CONTRACT}`);
});
