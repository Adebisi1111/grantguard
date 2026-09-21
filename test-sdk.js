// Test GenLayer SDK encoding
const path = require('path');
const genlayerPath = '/home/administrator/.local/lib/node_modules/genlayer/dist/index.js';

try {
    const genlayer = require(genlayerPath);
    console.log('GenLayer SDK loaded');
    console.log('Available exports:', Object.keys(genlayer));
} catch (e) {
    console.log('Error loading GenLayer SDK:', e.message);
    
    // Try loading viem directly from GenLayer's node_modules
    try {
        const viem = require('/home/administrator/.local/lib/node_modules/genlayer/node_modules/viem');
        console.log('viem loaded from GenLayer');
        
        const data = viem.encodeFunctionData({
            abi: [{
                name: 'create_grant',
                type: 'function',
                stateMutability: 'nonpayable',
                inputs: [
                    { name: 'grant_id', type: 'string' },
                    { name: 'name', type: 'string' },
                    { name: 'description', type: 'string' },
                    { name: 'eligibility', type: 'string' },
                    { name: 'criteria', type: 'string' },
                    { name: 'budget_rules', type: 'string' },
                    { name: 'required_evidence', type: 'string' },
                    { name: 'deadline', type: 'string' }
                ],
                outputs: [{ type: 'string' }]
            }],
            functionName: 'create_grant',
            args: ['test-grant-100', 'Test', 'Desc', 'All', 'Tech', 'Max', 'GitHub', '2026-12-31']
        });
        console.log('Encoded data:', data);
    } catch (e2) {
        console.log('viem error:', e2.message);
    }
}
