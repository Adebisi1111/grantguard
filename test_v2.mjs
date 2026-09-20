import { createClient } from 'genlayer-js';
import { privateKeyToAccount } from 'viem/accounts';
import fs from 'fs';

const studioNext = {
  id: 61997,
  name: 'Studio Next',
  rpcUrls: { default: { http: ['https://studio-next.genlayer.com/api'] } },
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 },
  testnet: true,
  consensusMainContract: {
    address: '0x0112Bf6e83497965A5fdD6Dad1E447a6E004271D',
    abi: [],
  },
  defaultNumberOfInitialValidators: 5,
  defaultConsensusMaxRotations: 3,
};

const account = privateKeyToAccount('0x023d076ab40ea46c59ac7ca7cecfaa2db5fa10b7a481aef27cf68e9cc5a8c0af');
const client = createClient({ chain: studioNext, account });

const ADDR = '0x671990450Bab8f89144F50B6A619c6382E824172';

async function test() {
  // Step 1: Create grant
  console.log('=== Step 1: Create Grant ===');
  const createHash = await client.writeContract({
    address: ADDR,
    functionName: 'create_grant',
    args: [
      'test-grant-1',
      'DeFi Innovation Grant',
      'Supporting DeFi projects',
      'Open to all developers',
      'Technical merit, innovation, feasibility',
      'Max 10000 GEN per project',
      'GitHub repo, working demo',
      '2026-12-31'
    ],
    gasLimit: 5000000n,
  });
  console.log('Create tx:', createHash);
  const createReceipt = await client.waitForTransactionReceipt({ hash: createHash, waitUntil: 'finalized', retries: 300 });
  console.log('Status:', createReceipt.status, createReceipt.txExecutionResultName);

  // Step 2: Fund grant
  console.log('\n=== Step 2: Fund Grant ===');
  const fundHash = await client.writeContract({
    address: ADDR,
    functionName: 'fund_grant',
    args: ['test-grant-1'],
    value: 1000000000000000000n, // 1 GEN
    gasLimit: 5000000n,
  });
  console.log('Fund tx:', fundHash);
  const fundReceipt = await client.waitForTransactionReceipt({ hash: fundHash, waitUntil: 'finalized', retries: 300 });
  console.log('Status:', fundReceipt.status, fundReceipt.txExecutionResultName);

  // Step 3: Check grant state
  console.log('\n=== Step 3: Check Grant State ===');
  const grant = await client.readContract({
    address: ADDR,
    functionName: 'get_grant',
    args: ['test-grant-1'],
  });
  console.log('Grant:', grant);

  // Step 4: Submit application
  console.log('\n=== Step 4: Submit Application ===');
  const submitHash = await client.writeContract({
    address: ADDR,
    functionName: 'submit_application',
    args: [
      'test-grant-1',
      'DeFi Dashboard',
      'A dashboard for DeFi analytics',
      'Team of 3 developers',
      500000000000000000n, // 0.5 GEN
      'https://example.com',
      'https://github.com/ethereum/ethereum-org-website',
      'https://github.com/ethereum/ethereum-org-website',
      'Additional info'
    ],
    gasLimit: 5000000n,
  });
  console.log('Submit tx:', submitHash);
  const submitReceipt = await client.waitForTransactionReceipt({ hash: submitHash, waitUntil: 'finalized', retries: 300 });
  console.log('Status:', submitReceipt.status, submitReceipt.txExecutionResultName);

  // Step 5: Check application state
  console.log('\n=== Step 5: Check Application State ===');
  const app = await client.readContract({
    address: ADDR,
    functionName: 'get_application',
    args: ['app_0'],
  });
  console.log('Application:', app);

  // Step 6: Evaluate (this will take time due to web.render + consensus)
  console.log('\n=== Step 6: Evaluate Application (1-3 min) ===');
  const evalHash = await client.writeContract({
    address: ADDR,
    functionName: 'evaluate_application',
    args: ['app_0'],
    gasLimit: 5000000n,
  });
  console.log('Eval tx:', evalHash);
  const evalReceipt = await client.waitForTransactionReceipt({ hash: evalHash, waitUntil: 'finalized', retries: 300 });
  console.log('Status:', evalReceipt.status, evalReceipt.txExecutionResultName);

  // Step 7: Check evaluation result
  console.log('\n=== Step 7: Check Evaluation Result ===');
  const appAfter = await client.readContract({
    address: ADDR,
    functionName: 'get_application',
    args: ['app_0'],
  });
  console.log('Application after eval:', appAfter);

  // Step 8: Release funds if approved
  if (appAfter && appAfter.status === 'APPROVED') {
    console.log('\n=== Step 8: Release Funds ===');
    const releaseHash = await client.writeContract({
      address: ADDR,
      functionName: 'release_funds',
      args: ['app_0'],
      gasLimit: 5000000n,
    });
    console.log('Release tx:', releaseHash);
    const releaseReceipt = await client.waitForTransactionReceipt({ hash: releaseHash, waitUntil: 'finalized', retries: 300 });
    console.log('Status:', releaseReceipt.status, releaseReceipt.txExecutionResultName);
  } else {
    console.log('\n=== Step 8: Skipped (not approved) ===');
  }

  // Step 9: Final state
  console.log('\n=== Step 9: Final State ===');
  const finalGrant = await client.readContract({
    address: ADDR,
    functionName: 'get_grant',
    args: ['test-grant-1'],
  });
  console.log('Final grant:', finalGrant);
}

test().catch(e => console.error('Error:', e.message));
