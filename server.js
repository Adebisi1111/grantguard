const express = require('express');
const cors = require('cors');
const { abi } = require('genlayer-js');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = '0x671990450Bab8f89144F50B6A619c6382E824172';
const CONSENSUS_CONTRACT = '0x0112Bf6e83497965A5fdD6Dad1E447a6E004271d';

// GenLayer-compatible encoding
function encodeCalldata(functionName, args) {
    const calldataObj = abi.calldata.makeCalldataObject(functionName, args, undefined);
    const encoded = abi.calldata.encode(calldataObj);
    const serialized = abi.transactions.serialize([encoded, false]);
    return serialized;
}

// RPC helper
async function rpc(method, params) {
    const r = await fetch('https://studio-next.genlayer.com/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: Date.now(), method, params })
    });
    const j = await r.json();
    if (j.error) throw new Error(j.error.message);
    return j.result;
}

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', contract: CONTRACT, consensus: CONSENSUS_CONTRACT });
});

// Get consensus contract address
app.get('/api/consensus', (req, res) => {
    res.json({ 
        consensusAddress: CONSENSUS_CONTRACT,
        contractAddress: CONTRACT
    });
});

// Encode calldata for a method
app.post('/api/encode', (req, res) => {
    try {
        const { method, args } = req.body;
        const data = encodeCalldata(method, args);
        res.json({ data, to: CONSENSUS_CONTRACT });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Read via eth_call
app.post('/api/read', async (req, res) => {
    try {
        const { method, args } = req.body;
        const data = encodeCalldata(method, args);
        const result = await rpc('eth_call', [{ to: CONTRACT, data }, 'latest']);
        res.json({ result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Simulate write
app.post('/api/simulate', async (req, res) => {
    try {
        const { method, args, from } = req.body;
        const data = encodeCalldata(method, args);
        const result = await rpc('gen_call', [{
            type: 'write',
            to: CONTRACT,
            from: from || '0x0000000000000000000000000000000000000000',
            data,
            transaction_hash_variant: 'latest-nonfinal'
        }]);
        res.json({ result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Get transaction count (nonce)
app.get('/api/nonce/:address', async (req, res) => {
    try {
        const result = await rpc('eth_getTransactionCount', [req.params.address, 'latest']);
        res.json({ nonce: result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Get gas price
app.get('/api/gasPrice', async (req, res) => {
    try {
        const result = await rpc('eth_gasPrice', []);
        res.json({ gasPrice: result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`GrantGuard v2 API on port ${PORT}`);
    console.log(`Contract: ${CONTRACT}`);
    console.log(`Consensus: ${CONSENSUS_CONTRACT}`);
});
