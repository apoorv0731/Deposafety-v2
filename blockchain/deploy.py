#!/usr/bin/env python3
"""
EvidenceAnchor Contract Deployment Script
Deploys the EvidenceAnchor smart contract to Polygon Mumbai testnet
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

# ============ Configuration ============

# Polygon Mumbai RPC endpoints (free tier options)
RPC_ENDPOINTS = {
    "alchemy": "https://polygon-mumbai.g.alchemy.com/v2/",
    "infura": "https://polygon-mumbai.infura.io/v3/",
    "public": "https://rpc-mumbai.maticvigil.com/",
    "chainstack": "https://polygon-mumbai.chainstacklabs.com/",
}

# Mumbai testnet chain ID
CHAIN_ID = 80001

# Contract bytecode and ABI will be loaded from compiled contract
CONTRACT_NAME = "EvidenceAnchor"

# ============ Contract Bytecode & ABI ============
# This is the compiled bytecode for EvidenceAnchor.sol (Solidity ^0.8.19)
# To regenerate: solc --bin --abi EvidenceAnchor.sol -o build/

CONTRACT_BYTECODE = "0x" + ""  # Will be populated after compilation

CONTRACT_ABI = []  # Will be populated after compilation


def get_web3_provider():
    """Initialize Web3 connection using available RPC provider"""
    
    # Try Alchemy first (if API key provided)
    alchemy_key = os.getenv("ALCHEMY_API_KEY")
    if alchemy_key:
        rpc_url = f"{RPC_ENDPOINTS['alchemy']}{alchemy_key}"
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            print(f"✓ Connected via Alchemy")
            return w3
    
    # Try Infura (if API key provided)
    infura_key = os.getenv("INFURA_API_KEY")
    if infura_key:
        rpc_url = f"{RPC_ENDPOINTS['infura']}{infura_key}"
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            print(f"✓ Connected via Infura")
            return w3
    
    # Try public RPC endpoints
    for name, rpc_url in RPC_ENDPOINTS.items():
        if name in ["alchemy", "infura"]:
            continue
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            print(f"✓ Connected via {name} RPC")
            return w3
    
    raise ConnectionError("Could not connect to any Polygon Mumbai RPC endpoint")


def load_contract_artifacts():
    """Load compiled contract bytecode and ABI"""
    global CONTRACT_BYTECODE, CONTRACT_ABI
    
    # Check for Hardhat/Foundry build artifacts
    build_paths = [
        Path("artifacts/contracts/EvidenceAnchor.sol/EvidenceAnchor.json"),
        Path("build/EvidenceAnchor.json"),
        Path("out/EvidenceAnchor.sol/EvidenceAnchor.json"),
        Path("contract_artifacts.json"),
    ]
    
    for build_path in build_paths:
        if build_path.exists():
            with open(build_path, "r") as f:
                artifact = json.load(f)
                
                # Handle different artifact formats
                if "bytecode" in artifact:
                    bytecode = artifact["bytecode"]
                    if isinstance(bytecode, dict) and "object" in bytecode:
                        CONTRACT_BYTECODE = "0x" + bytecode["object"]
                    else:
                        CONTRACT_BYTECODE = bytecode if bytecode.startswith("0x") else "0x" + bytecode
                
                if "abi" in artifact:
                    CONTRACT_ABI = artifact["abi"]
                
                print(f"✓ Loaded contract artifacts from {build_path}")
                return
    
    # If no artifacts found, use embedded bytecode/ABI
    print("⚠ No build artifacts found, using embedded bytecode")
    load_embedded_artifacts()


def load_embedded_artifacts():
    """Load embedded contract bytecode and ABI"""
    global CONTRACT_BYTECODE, CONTRACT_ABI
    
    # Embedded ABI (generated from EvidenceAnchor.sol)
    CONTRACT_ABI = [
        {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
                {"indexed": True, "internalType": "address", "name": "submitter", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"indexed": False, "internalType": "uint256", "name": "blockNumber", "type": "uint256"}
            ],
            "name": "EvidenceAnchored",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
                {"indexed": False, "internalType": "string", "name": "metadata", "type": "string"}
            ],
            "name": "MetadataUpdated",
            "type": "event"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
            "name": "anchors",
            "outputs": [
                {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "address", "name": "submitter", "type": "address"},
                {"internalType": "uint256", "name": "blockNumber", "type": "uint256"},
                {"internalType": "string", "name": "metadata", "type": "string"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "_evidenceHash", "type": "bytes32"}],
            "name": "getAnchorDetails",
            "outputs": [
                {
                    "components": [
                        {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
                        {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                        {"internalType": "address", "name": "submitter", "type": "address"},
                        {"internalType": "uint256", "name": "blockNumber", "type": "uint256"},
                        {"internalType": "string", "name": "metadata", "type": "string"}
                    ],
                    "internalType": "struct EvidenceAnchor.Anchor",
                    "name": "",
                    "type": "tuple"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getAnchorCount",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "_start", "type": "uint256"}, {"internalType": "uint256", "name": "_limit", "type": "uint256"}],
            "name": "getAnchorsPaginated",
            "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "_evidenceHash", "type": "bytes32"}],
            "name": "isAnchored",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "owner",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "_evidenceHash", "type": "bytes32"}, {"internalType": "string", "name": "_metadata", "type": "string"}],
            "name": "anchorEvidence",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32[]", "name": "_evidenceHashes", "type": "bytes32[]"}, {"internalType": "string[]", "name": "_metadataArray", "type": "string[]"}],
            "name": "batchAnchorEvidence",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "renounceOwnership",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "_newOwner", "type": "address"}],
            "name": "transferOwnership",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "_evidenceHash", "type": "bytes32"}, {"internalType": "string", "name": "_metadata", "type": "string"}],
            "name": "updateMetadata",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "_evidenceHash", "type": "bytes32"}],
            "name": "verifyEvidence",
            "outputs": [
                {"internalType": "bool", "name": "anchored", "type": "bool"},
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "address", "name": "submitter", "type": "address"},
                {"internalType": "uint256", "name": "blockNumber", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    # Note: Full bytecode is too large to embed, compilation required
    CONTRACT_BYTECODE = None


def deploy_contract(w3, account):
    """Deploy the EvidenceAnchor contract"""
    
    if CONTRACT_BYTECODE is None or CONTRACT_BYTECODE == "0x":
        raise ValueError("Contract bytecode not available. Please compile the contract first.")
    
    # Create contract instance
    Contract = w3.eth.contract(abi=CONTRACT_ABI, bytecode=CONTRACT_BYTECODE)
    
    # Build deployment transaction
    print("\n📦 Building deployment transaction...")
    tx = Contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,  # Adjust based on contract size
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID,
    })
    
    # Sign transaction
    print("🔏 Signing transaction...")
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    
    # Send transaction
    print("📤 Sending deployment transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"⏳ Transaction hash: {tx_hash.hex()}")
    
    # Wait for receipt
    print("⏳ Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if tx_receipt['status'] == 1:
        contract_address = tx_receipt['contractAddress']
        print(f"\n✅ Contract deployed successfully!")
        print(f"📍 Contract address: {contract_address}")
        print(f"🔗 Polygonscan: https://mumbai.polygonscan.com/address/{contract_address}")
        print(f"⛽ Gas used: {tx_receipt['gasUsed']}")
        
        # Save deployment info
        save_deployment_info(contract_address, tx_hash.hex(), tx_receipt)
        
        return contract_address
    else:
        raise Exception("Deployment transaction failed")


def save_deployment_info(contract_address, tx_hash, tx_receipt):
    """Save deployment information to file"""
    
    deployment_info = {
        "network": "Polygon Mumbai",
        "chainId": CHAIN_ID,
        "contractAddress": contract_address,
        "transactionHash": tx_hash,
        "blockNumber": tx_receipt['blockNumber'],
        "gasUsed": tx_receipt['gasUsed'],
        "deployedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "abi": CONTRACT_ABI,
    }
    
    output_path = Path("deployment_info.json")
    with open(output_path, "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\n💾 Deployment info saved to {output_path}")


def compile_contract():
    """Compile the Solidity contract using solc"""
    import subprocess
    
    print("\n🔨 Compiling contract...")
    
    # Create build directory
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    
    try:
        # Try to compile with solc
        result = subprocess.run(
            ["solc", "--bin", "--abi", "--optimize", "--output-dir", str(build_dir), "EvidenceAnchor.sol"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Contract compiled successfully")
        
        # Read compiled artifacts
        bytecode_path = build_dir / "EvidenceAnchor.bin"
        abi_path = build_dir / "EvidenceAnchor.abi"
        
        if bytecode_path.exists() and abi_path.exists():
            with open(bytecode_path, "r") as f:
                bytecode = f.read().strip()
                global CONTRACT_BYTECODE
                CONTRACT_BYTECODE = "0x" + bytecode
            
            with open(abi_path, "r") as f:
                global CONTRACT_ABI
                CONTRACT_ABI = json.load(f)
            
            print("✓ Loaded compiled bytecode and ABI")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠ Compilation failed: {e.stderr}")
        print("⚠ Using embedded ABI, bytecode must be compiled separately")
    except FileNotFoundError:
        print("⚠ solc not found. Please install Solidity compiler")
        print("   npm install -g solc  or  pip install py-solc-x")


def main():
    """Main deployment function"""
    
    print("=" * 60)
    print("🚀 EvidenceAnchor Contract Deployment")
    print("🌐 Network: Polygon Mumbai Testnet")
    print("=" * 60)
    
    # Get private key
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    if not private_key:
        print("\n❌ Error: DEPLOYER_PRIVATE_KEY not set in environment")
        print("   Set it with: export DEPLOYER_PRIVATE_KEY=0x...")
        return
    
    # Create account from private key
    account = Account.from_key(private_key)
    print(f"\n👤 Deployer address: {account.address}")
    
    # Connect to network
    print("\n🔗 Connecting to Polygon Mumbai...")
    w3 = get_web3_provider()
    print(f"✓ Connected (Block: {w3.eth.block_number})")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_matic = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_matic:.4f} MATIC")
    
    if balance < w3.to_wei(0.01, 'ether'):
        print("\n⚠️  Warning: Low balance. Get free MATIC from:")
        print("   https://faucet.polygon.technology/")
        print("   https://mumbaifaucet.com/")
        return
    
    # Compile contract
    compile_contract()
    
    # Load contract artifacts
    load_contract_artifacts()
    
    # Confirm deployment
    print("\n" + "=" * 60)
    response = input("Proceed with deployment? (yes/no): ")
    if response.lower() != "yes":
        print("Deployment cancelled")
        return
    
    # Deploy contract
    try:
        contract_address = deploy_contract(w3, account)
        print("\n" + "=" * 60)
        print("🎉 Deployment complete!")
        print(f"📍 Contract: {contract_address}")
        print(f"🔗 Explorer: https://mumbai.polygonscan.com/address/{contract_address}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        raise


if __name__ == "__main__":
    main()
