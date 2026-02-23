# Quick Start Guide - DepoSafety Blockchain Anchoring

## 🚀 Deploy in 5 Minutes

### 1. Setup Environment

```bash
cd /root/.openclaw/workspace/deposafety-v2/blockchain

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Wallet

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your private key
# Get a new wallet from: https://vanity-eth.tk/
# Or export from MetaMask
```

### 3. Get Test MATIC

1. Copy your wallet address (0x...)
2. Visit: https://faucet.polygon.technology/
3. Select "Mumbai" network
4. Paste your address
5. Click "Submit"

Wait ~30 seconds for the MATIC to arrive.

### 4. Deploy Contract

```bash
python deploy.py
```

The script will:
- Compile the Solidity contract
- Deploy to Mumbai testnet
- Save deployment info to `deployment_info.json`

**Save the contract address!** You'll need it for anchoring.

### 5. Anchor Your First Evidence

```python
from anchor_service import EvidenceAnchorService

# Initialize
service = EvidenceAnchorService()

# Compute hash of your file
hash = service.compute_hash_from_file("evidence.pdf")
print(f"Hash: {hash}")

# Anchor on blockchain
result = service.anchor_evidence(hash, "Case #12345")
print(f"Transaction: {result.transaction_hash}")
print(f"Explorer: {service.get_polygonscan_link(result.transaction_hash)}")
```

### 6. Verify Evidence

```bash
python verify.py --contract 0xYOUR_CONTRACT --file evidence.pdf
```

## 📋 Common Commands

```bash
# Deploy contract
python deploy.py

# Anchor a file
python anchor_service.py --action anchor --file evidence.pdf --metadata "Case #123"

# Verify a file
python verify.py --contract 0x... --file evidence.pdf

# Verify by hash
python verify.py --contract 0x... --hash 0xabc123...

# Run tests
python test_simple.py
```

## 🔗 Useful Links

- **Mumbai Explorer**: https://mumbai.polygonscan.com/
- **Faucet**: https://faucet.polygon.technology/
- **Web3.py Docs**: https://web3py.readthedocs.io/

## 🆘 Troubleshooting

**"Could not connect to RPC"**
- Check internet connection
- Try a different RPC endpoint in the code

**"Insufficient funds"**
- Get more MATIC from the faucet
- Check balance: https://mumbai.polygonscan.com/address/YOUR_ADDRESS

**"Contract deployment failed"**
- Make sure you have enough MATIC for gas
- Check that your private key is correct (with 0x prefix)

## 📁 File Overview

| File | Purpose |
|------|---------|
| `EvidenceAnchor.sol` | Smart contract source code |
| `deploy.py` | Deploy contract to Mumbai |
| `anchor_service.py` | Python service for anchoring/verification |
| `verify.py` | Standalone verification script |
| `frontend_integration.js` | React/Vue components |
| `README.md` | Full documentation |
