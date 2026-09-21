const express = require('express');
const cors = require('cors');
const { encodeFunctionData } = require('viem');
const { keccak256, stringToBytes } = require('viem');

const app = express();
app.use(cors());
app.use(express.json());

const CONTRACT = '0xba22BF8161c7B9D2E9A5bED6430EFF0147DDCeB0';
const CONSENSUS_CONTRACT = '0xb7278A61aa25c888815aFC32Ad3cC52fF24fE575';

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

// Encode a contract call and wrap it in addTransaction for the consensus contract
async function encodeCalldata(functionName, args) {
    const abiItem = ABI.find(f => f.name === functionName);
    if (!abiItem) throw new Error('Unknown function: ' + functionName);
    
    // Step 1: Encode the inner function call
    const innerData = encodeFunctionData({
        abi: [abiItem],
        functionName,
        args
    });
    
    // Step 2: Build the addTransaction params
    const params = {
        sender: '0x61fd0047595A30A067f1F21F3b28C4AE8A8e3Dc3',
        recipient: CONTRACT,
        numOfInitialValidators: 5n,
        maxRotations: 3n,
        validUntil: BigInt(Math.floor(Date.now() / 1000) + 3600),
        saltNonce: 0n,
        userValue: 0n,
        feesDistribution: {
            leaderTimeunitsAllocation: 100n,
            validatorTimeunitsAllocation: 200n,
            executionBudgetPerRound: 94630500000000n,
            totalMessageFees: 0n,
            rotations: 3n
        },
        txCalldata: innerData,
        messageAllocations: []
    };
    
    // Step 3: Encode the addTransaction call
    const ADD_TRANSACTION_ABI = [{
        type: 'function',
        name: 'addTransaction',
        stateMutability: 'payable',
        inputs: [{
            name: '_params',
            type: 'tuple',
            components: [
                { name: 'sender', type: 'address' },
                { name: 'recipient', type: 'address' },
                { name: 'numOfInitialValidators', type: 'uint256' },
                { name: 'maxRotations', type: 'uint256' },
                { name: 'validUntil', type: 'uint256' },
                { name: 'saltNonce', type: 'uint256' },
                { name: 'userValue', type: 'uint256' },
                { name: 'feesDistribution', type: 'tuple', components: [
                    { name: 'leaderTimeunitsAllocation', type: 'uint256' },
                    { name: 'validatorTimeunitsAllocation', type: 'uint256' },
                    { name: 'executionBudgetPerRound', type: 'uint256' },
                    { name: 'totalMessageFees', type: 'uint256' },
                    { name: 'rotations', type: 'uint256' }
                ]},
                { name: 'txCalldata', type: 'bytes' },
                { name: 'messageAllocations', type: 'tuple[]', components: [] }
            ]
        }],
        outputs: []
    }];
    
    const data = encodeFunctionData({
        abi: ADD_TRANSACTION_ABI,
        functionName: 'addTransaction',
        args: [params]
    });
    
    return { data, to: CONSENSUS_CONTRACT };
}

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', contract: CONTRACT, consensus: CONSENSUS_CONTRACT });
});

app.get('/api/consensus', (req, res) => {
    res.json({ consensusAddress: CONSENSUS_CONTRACT, contractAddress: CONTRACT });
});

app.post('/api/encode', async (req, res) => {
    try {
        const { method, args } = req.body;
        const result = await encodeCalldata(method, args);
        res.json(result);
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/api/simulate', async (req, res) => {
    try {
        const { method, args, from } = req.body;
        const { data, to } = await encodeCalldata(method, args);
        
        const result = await rpc('gen_call', [{
            type: 'write',
            to: CONTRACT,
            from: from || '0x61fd0047595A30A067f1F21F3b28C4AE8A8e3Dc3',
            data,
            transaction_hash_variant: 'latest-nonfinal'
        }]);
        
        res.json({ success: true, result: result.toString() });
    } catch (e) {
        res.status(500).json({ success: false, error: e.message });
    }
});

app.post('/api/read', async (req, res) => {
    try {
        const { method, args } = req.body;
        const abiItem = ABI.find(f => f.name === method);
        const data = encodeFunctionData({ abi: [abiItem], functionName: method, args });
        const result = await rpc('eth_call', [{ to: CONTRACT, data }, 'latest']);
        res.json({ result });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`GrantGuard v2 API on port ${PORT}`);
});
