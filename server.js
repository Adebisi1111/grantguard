// GrantGuard v2 Backend - uses GenLayer CLI for writes
const express = require('express');
const cors = require('cors');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = '0x671990450Bab8f89144F50B6A619c6382E824172';
const FEE_PROFILE = path.join(__dirname, 'fee-profile-studio-next.json');

// Private key (from environment or default)
const PK = process.env.PRIVATE_KEY || '0x023d7e4e950d8cea0d8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8';

// RPC helper for reads
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
    res.json({ status: 'ok', contract: CONTRACT });
});

// Read via eth_call using viem encoding (works for reads)
app.get('/api/read/:method', async (req, res) => {
    try {
        const { method } = req.params;
        const args = req.query.args ? JSON.parse(req.query.args) : [];
        
        const ABI = getABI();
        const abiItem = ABI.find(f => f.name === method);
        if (!abiItem) throw new Error('Unknown method: ' + method);
        
        const data = encodeFunctionData({ abi: ABI, functionName: method, args });
        const result = await rpc('eth_call', [{ to: CONTRACT, data }, 'latest']);
        res.json({ result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Write via GenLayer CLI
app.post('/api/write', async (req, res) => {
    try {
        const { method, args } = req.body;
        
        // Build CLI command
        const argsJson = JSON.stringify(args).replace(/"/g, '\\"');
        const cmd = `cd ${__dirname} && echo "test1234" | genlayer write ${CONTRACT} ${method} --fee-profile ${FEE_PROFILE} --args '${JSON.stringify(args)}' 2>&1`;
        
        console.log('Executing:', cmd);
        const output = execSync(cmd, { 
            encoding: 'utf8',
            timeout: 120000,
            env: { ...process.env, PRIVATE_KEY: PK }
        });
        
        res.json({ output });
    } catch (e) {
        res.status(500).json({ error: e.message, stderr: e.stderr, stdout: e.stdout });
    }
});

// Get ABI
function getABI() {
    return [
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
}

// Simple ABI encoder for reads
function encodeFunctionData({ abi, functionName, args }) {
    const abiItem = abi.find(f => f.name === functionName);
    if (!abiItem) throw new Error('Unknown function: ' + functionName);
    
    const types = abiItem.inputs.map(i => i.type).join(',');
    const sig = `${functionName}(${types})`;
    const selector = keccak256(sig).slice(0, 10);
    
    let encodedParams = '';
    let dynamicData = '';
    let dynamicOffset = args.length * 32;
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        const type = abiItem.inputs[i]?.type || 'string';
        
        if (type === 'string') {
            encodedParams += toHex(dynamicOffset, 64);
            const hex = stringToHex(String(arg));
            dynamicData += toHex(hex.length / 2, 64);
            dynamicData += hex.padEnd(Math.ceil(hex.length / 64) * 64, '0');
            dynamicOffset += 64 + Math.ceil(hex.length / 64) * 64;
        } else if (type === 'uint256') {
            encodedParams += toHex(BigInt(arg || 0), 64);
        } else if (type === 'bool') {
            encodedParams += arg ? '01' : '00';
        }
    }
    
    return selector + encodedParams + dynamicData;
}

function keccak256(message) {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(message).digest('hex');
}

function stringToHex(str) {
    let hex = '';
    for (let i = 0; i < str.length; i++) {
        hex += str.charCodeAt(i).toString(16).padStart(2, '0');
    }
    return hex;
}

function toHex(value, length) {
    let hex = BigInt(value).toString(16);
    while (hex.length < length) hex = '0' + hex;
    return hex;
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`GrantGuard API on port ${PORT}`);
});
