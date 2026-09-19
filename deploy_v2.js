const { createClient, chains } = require('genlayer-js');
const { privateKeyToAccount } = require('viem/accounts');
const fs = require('fs');

async function deploy() {
  const account = privateKeyToAccount('0x023d076ab40ea46c59ac7ca7cecfaa2db5fa10b7a481aef27cf68e9cc5a8c0af');
  const client = createClient({ chain: chains.testnetBradbury, account });
  const code = fs.readFileSync('/home/administrator/grantguard/contracts/grantguard.py');

  console.log('Deploying GrantGuard with deterministic evaluation...');
  const hash = await client.deployContract({
    code: new Uint8Array(code),
    args: [],
    value: 0n,
    gasLimit: 5000000n
  });
  console.log('Deploy hash:', hash);

  const receipt = await client.waitForTransactionReceipt({ hash, waitUntil: 'finalized', retries: 120 });
  const addr = receipt.data?.contractAddress || receipt.txDataDecoded?.contractAddress;
  console.log('GrantGuard deployed at:', addr);

  // Verify
  const nextGrantId = await client.readContract({ address: addr, functionName: 'getNextGrantId', args: [] });
  console.log('getNextGrantId:', nextGrantId);
}

deploy().catch(e => console.error('Deploy failed:', e.message));
