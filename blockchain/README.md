# DepoSafety V2 - Blockchain Evidence Anchoring

This module provides blockchain-based evidence integrity verification for the DepoSafety platform using Polygon Mumbai testnet.

## Overview

The EvidenceAnchor smart contract stores SHA-256 hashes of evidence files on the blockchain, providing:

- **Immutable timestamping**: Proof of existence at a specific time
- **Tamper detection**: Any modification changes the hash
- **Non-repudiation**: Submitter address recorded on-chain
- **Public verification**: Anyone can verify evidence integrity

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Evidence File │────▶│  Anchor Service  │────▶│  Smart Contract │
│   (PDF, Video)  │     │  (Web3.py)       │     │  (Polygon)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌──────────────┐          ┌──────────────┐
                        │  SHA-256     │          │  Blockchain  │
                        │  Hash        │          │  Storage     │
                        └──────────────┘          └──────────────┘
```

## Quick Start

### 1. Prerequisites

```bash
# Install dependencies
pip install web3 python-dotenv

# For contract compilation (optional)
npm install -g solc
# or
pip install py-solc-x
```

### 2. Environment Setup

Create a `.env` file:

```bash
# Required for deployment and anchoring
DEPLOYER_PRIVATE_KEY=0x...
ANCHOR_PRIVATE_KEY=0x...

# Contract address (after deployment)
CONTRACT_ADDRESS=0x...

# RPC Provider API keys (optional - public RPCs work too)
ALCHEMY_API_KEY=your_alchemy_key
INFURA_API_KEY=your_infura_key
```

### 3. Get Test MATIC

Get free MATIC for Mumbai testnet:

- [Polygon Faucet](https://faucet.polygon.technology/)
- [Mumbai Faucet](https://mumbaifaucet.com/)

### 4. Deploy Contract

```bash
cd /root/.openclaw/workspace/deposafety-v2/blockchain
python deploy.py
```

This will:
1. Compile the Solidity contract
2. Deploy to Polygon Mumbai
3. Save deployment info to `deployment_info.json`

### 5. Anchor Evidence

```python
from anchor_service import EvidenceAnchorService

# Initialize service
service = EvidenceAnchorService()

# Anchor a file
with open("evidence.pdf", "rb") as f:
    file_data = f.read()

evidence_hash = service.compute_hash(file_data)
result = service.anchor_evidence(
    evidence_hash,
    metadata="Case #12345 - Witness Statement"
)

print(f"Transaction: {result.transaction_hash}")
print(f"Explorer: {service.get_polygonscan_link(result.transaction_hash)}")
```

### 6. Verify Evidence

```bash
# Using the verify script
python verify.py --contract 0x... --file evidence.pdf

# Or verify by hash
python verify.py --contract 0x... --hash 0xabc123...
```

Or in Python:

```python
from anchor_service import EvidenceAnchorService

service = EvidenceAnchorService()
result = service.verify_evidence("0x...")

if result.is_anchored:
    print(f"Anchored at: {result.timestamp}")
    print(f"Submitter: {result.submitter}")
```

## Smart Contract

### EvidenceAnchor.sol

**Key Features:**
- Store SHA-256 hashes (32 bytes)
- Record timestamp, submitter, block number
- Batch anchoring for multiple files
- Metadata support (case IDs, descriptions)
- Ownership management

**Events:**
```solidity
event EvidenceAnchored(
    bytes32 indexed evidenceHash,
    address indexed submitter,
    uint256 timestamp,
    uint256 blockNumber
);
```

**Main Functions:**
- `anchorEvidence(bytes32 hash, string metadata)` - Anchor single evidence
- `batchAnchorEvidence(bytes32[] hashes, string[] metadata)` - Batch anchor
- `verifyEvidence(bytes32 hash)` - Check if anchored and get details
- `getAnchorDetails(bytes32 hash)` - Get full anchor info

## API Integration

### FastAPI Example

```python
from fastapi import FastAPI, UploadFile, File
from anchor_service import EvidenceAnchorService, AnchorAPI

app = FastAPI()
service = EvidenceAnchorService()
anchor_api = AnchorAPI(service)

@app.post("/anchor")
async def anchor_file(file: UploadFile = File(...), metadata: str = ""):
    content = await file.read()
    return anchor_api.anchor_endpoint(content, metadata)

@app.get("/verify/{evidence_hash}")
async def verify_hash(evidence_hash: str):
    return anchor_api.verify_endpoint(evidence_hash)
```

## Frontend Integration

### Verification Badge Component

```html
<!-- Example React/Vue component -->
<div class="blockchain-badge" :class="{ verified: isVerified }">
  <span v-if="isVerified">
    ✅ Anchored on {{ network }}
    <a :href="polygonscanUrl" target="_blank">
      View on Polygonscan
    </a>
    <span class="timestamp">{{ formattedTimestamp }}</span>
  </span>
  <span v-else>
    ⚠️ Not verified on blockchain
  </span>
</div>
```

### JavaScript Verification

```javascript
// Using ethers.js or web3.js
const contractAddress = "0x...";
const provider = new ethers.JsonRpcProvider("https://rpc-mumbai.maticvigil.com/");
const contract = new ethers.Contract(contractAddress, ABI, provider);

async function verifyEvidence(hash) {
  const [isAnchored, timestamp, submitter, blockNumber] = 
    await contract.verifyEvidence(hash);
  
  return {
    isAnchored,
    timestamp: new Date(timestamp * 1000),
    submitter,
    blockNumber
  };
}
```

## File Structure

```
blockchain/
├── EvidenceAnchor.sol      # Smart contract source
├── deploy.py               # Deployment script
├── anchor_service.py       # Backend service
├── verify.py               # Standalone verification
├── deployment_info.json    # Deployment details (generated)
└── README.md              # This file
```

## Testing

```bash
# Test deployment locally (requires Ganache/Hardhat node)
python deploy.py --local

# Test anchoring
python anchor_service.py --action anchor --file test.pdf

# Test verification
python verify.py --contract 0x... --hash 0x...
```

## Security Considerations

1. **Private Keys**: Never commit private keys to version control
2. **RPC Endpoints**: Use API keys for production (Alchemy/Infura)
3. **Contract Ownership**: Transfer ownership to multisig for production
4. **Hash Verification**: Always verify hashes client-side before trusting

## Production Deployment

For production on Polygon mainnet:

1. Update RPC URLs to mainnet endpoints
2. Change `CHAIN_ID` to 137 (Polygon mainnet)
3. Use real MATIC (not testnet)
4. Verify contract on Polygonscan
5. Set up monitoring and alerts

## Troubleshooting

### Connection Issues
```bash
# Test RPC connection
curl -X POST https://rpc-mumbai.maticvigil.com/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Low Balance
```bash
# Check balance
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.maticvigil.com/')); print(w3.eth.get_balance('0x...'))"
```

### Gas Issues
- Mumbai gas prices are low but can spike
- Use `w3.eth.gas_price` for current price
- Set reasonable gas limits (200k for single anchor)

## Resources

- [Polygon Mumbai Faucet](https://faucet.polygon.technology/)
- [Polygonscan Mumbai](https://mumbai.polygonscan.com/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)

## License

MIT License - See parent project for details.
