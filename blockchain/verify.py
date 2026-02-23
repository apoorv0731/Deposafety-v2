#!/usr/bin/env python3
"""
Evidence Verification Script
Standalone script for verifying evidence hashes on the blockchain
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.types import HexBytes
from datetime import datetime
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()


class EvidenceVerifier:
    """Standalone verifier for evidence on the blockchain"""
    
    # Contract ABI (minimal for verification)
    CONTRACT_ABI = [
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
            "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
            "name": "isAnchored",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
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
    ]
    
    # Polygon Mumbai RPC endpoints
    RPC_URLS = [
        "https://rpc-mumbai.maticvigil.com/",
        "https://polygon-mumbai.chainstacklabs.com/",
        "https://matic-mumbai.chainstacklabs.com/",
    ]
    
    POLYGONSCAN_URL = "https://mumbai.polygonscan.com"
    
    def __init__(self, contract_address: str, rpc_url: Optional[str] = None):
        """
        Initialize the verifier
        
        Args:
            contract_address: Address of the deployed EvidenceAnchor contract
            rpc_url: Optional custom RPC URL
        """
        self.contract_address = contract_address
        
        # Initialize Web3
        if rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        else:
            self.w3 = self._connect_to_rpc()
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Polygon Mumbai")
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(contract_address),
            abi=self.CONTRACT_ABI
        )
    
    def _connect_to_rpc(self) -> Web3:
        """Try to connect to available RPC endpoints"""
        # Try Alchemy if API key available
        alchemy_key = os.getenv("ALCHEMY_API_KEY")
        if alchemy_key:
            w3 = Web3(Web3.HTTPProvider(f"https://polygon-mumbai.g.alchemy.com/v2/{alchemy_key}"))
            if w3.is_connected():
                return w3
        
        # Try Infura if API key available
        infura_key = os.getenv("INFURA_API_KEY")
        if infura_key:
            w3 = Web3(Web3.HTTPProvider(f"https://polygon-mumbai.infura.io/v3/{infura_key}"))
            if w3.is_connected():
                return w3
        
        # Try public endpoints
        for url in self.RPC_URLS:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                return w3
        
        raise ConnectionError("Could not connect to any Polygon Mumbai RPC endpoint")
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return "0x" + sha256_hash.hexdigest()
    
    @staticmethod
    def compute_string_hash(data: str) -> str:
        """Compute SHA-256 hash of a string"""
        return "0x" + hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def compute_bytes_hash(data: bytes) -> str:
        """Compute SHA-256 hash of bytes"""
        return "0x" + hashlib.sha256(data).hexdigest()
    
    def verify(self, evidence_hash: str) -> Dict[str, Any]:
        """
        Verify if an evidence hash is anchored on the blockchain
        
        Args:
            evidence_hash: SHA-256 hash (hex string with 0x prefix)
            
        Returns:
            Dictionary with verification results
        """
        # Normalize hash
        if not evidence_hash.startswith("0x"):
            evidence_hash = "0x" + evidence_hash
        
        evidence_hash = evidence_hash.lower()
        
        try:
            hash_bytes = HexBytes(evidence_hash)
            
            # Check if anchored
            is_anchored = self.contract.functions.isAnchored(hash_bytes).call()
            
            if not is_anchored:
                return {
                    "verified": False,
                    "evidence_hash": evidence_hash,
                    "message": "Evidence hash not found on blockchain"
                }
            
            # Get verification details
            result = self.contract.functions.verifyEvidence(hash_bytes).call()
            anchored, timestamp, submitter, block_number = result
            
            # Get full details including metadata
            details = self.contract.functions.getAnchorDetails(hash_bytes).call()
            metadata = details[4] if len(details) > 4 else ""
            
            # Get block info for additional details
            try:
                block = self.w3.eth.get_block(block_number)
                block_hash = block['hash'].hex()
            except:
                block_hash = None
            
            return {
                "verified": True,
                "evidence_hash": evidence_hash,
                "timestamp": timestamp,
                "timestamp_human": datetime.fromtimestamp(timestamp).isoformat(),
                "submitter": submitter,
                "block_number": block_number,
                "block_hash": block_hash,
                "metadata": metadata,
                "contract_address": self.contract_address,
                "network": "Polygon Mumbai Testnet",
                "chain_id": 80001,
                "explorer_url": f"{self.POLYGONSCAN_URL}/address/{self.contract_address}",
            }
            
        except Exception as e:
            return {
                "verified": False,
                "evidence_hash": evidence_hash,
                "error": str(e)
            }
    
    def verify_file(self, file_path: str) -> Dict[str, Any]:
        """
        Verify a file by computing its hash and checking the blockchain
        
        Args:
            file_path: Path to the file to verify
            
        Returns:
            Dictionary with verification results
        """
        if not Path(file_path).exists():
            return {
                "verified": False,
                "error": f"File not found: {file_path}"
            }
        
        evidence_hash = self.compute_file_hash(file_path)
        result = self.verify(evidence_hash)
        result["file_path"] = file_path
        result["computed_hash"] = evidence_hash
        
        return result
    
    def format_verification_output(self, result: Dict[str, Any]) -> str:
        """Format verification result as a readable string"""
        
        lines = []
        lines.append("=" * 60)
        lines.append("🔍 EVIDENCE VERIFICATION RESULT")
        lines.append("=" * 60)
        
        if result.get("file_path"):
            lines.append(f"📁 File: {result['file_path']}")
            lines.append(f"🔐 Computed Hash: {result['computed_hash']}")
        
        lines.append(f"🔐 Evidence Hash: {result['evidence_hash']}")
        
        if result.get("verified"):
            lines.append("")
            lines.append("✅ VERIFIED - Evidence is anchored on blockchain")
            lines.append("")
            lines.append(f"📅 Anchored: {result.get('timestamp_human', 'N/A')}")
            lines.append(f"👤 Submitter: {result.get('submitter', 'N/A')}")
            lines.append(f"📦 Block: {result.get('block_number', 'N/A')}")
            
            if result.get('metadata'):
                lines.append(f"📝 Metadata: {result['metadata']}")
            
            lines.append("")
            lines.append(f"🔗 Contract: {result.get('contract_address', 'N/A')}")
            lines.append(f"🌐 Network: {result.get('network', 'N/A')}")
            lines.append(f"📊 Explorer: {result.get('explorer_url', 'N/A')}")
        else:
            lines.append("")
            lines.append("❌ NOT VERIFIED")
            lines.append(f"   {result.get('message', result.get('error', 'Unknown error'))}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Verify evidence hashes on Polygon Mumbai blockchain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a hash directly
  python verify.py --contract 0x... --hash 0xabc123...
  
  # Verify a file
  python verify.py --contract 0x... --file evidence.pdf
  
  # Output as JSON
  python verify.py --contract 0x... --file evidence.pdf --json
        """
    )
    
    parser.add_argument(
        "--contract",
        help="Contract address (or set CONTRACT_ADDRESS env var)",
        default=os.getenv("CONTRACT_ADDRESS")
    )
    parser.add_argument("--hash", help="Evidence hash to verify (with 0x prefix)")
    parser.add_argument("--file", help="File to verify")
    parser.add_argument("--rpc", help="Custom RPC URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.contract:
        print("Error: Contract address required (--contract or CONTRACT_ADDRESS env var)")
        sys.exit(1)
    
    if not args.hash and not args.file:
        print("Error: Either --hash or --file required")
        sys.exit(1)
    
    try:
        # Initialize verifier
        verifier = EvidenceVerifier(args.contract, args.rpc)
        
        # Perform verification
        if args.file:
            result = verifier.verify_file(args.file)
        else:
            result = verifier.verify(args.hash)
        
        # Output result
        if args.json:
            print(json.dumps(result, indent=2))
        elif args.quiet:
            print("VERIFIED" if result.get("verified") else "NOT_VERIFIED")
        else:
            print(verifier.format_verification_output(result))
        
        # Exit with appropriate code
        sys.exit(0 if result.get("verified") else 1)
        
    except ConnectionError as e:
        print(f"Connection error: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
