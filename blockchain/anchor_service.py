#!/usr/bin/env python3
"""
EvidenceAnchor Service - Backend integration for blockchain anchoring
Handles submitting evidence hashes to the smart contract and verification
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.types import TxReceipt, HexBytes
from eth_account import Account

# Load environment variables
load_dotenv()


@dataclass
class AnchorResult:
    """Result of an anchor operation"""
    success: bool
    evidence_hash: str
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: Optional[int] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of a verification operation"""
    is_anchored: bool
    evidence_hash: str
    timestamp: Optional[int] = None
    submitter: Optional[str] = None
    block_number: Optional[int] = None
    metadata: Optional[str] = None


class EvidenceAnchorService:
    """Service for interacting with the EvidenceAnchor smart contract"""
    
    # Polygon Mumbai RPC endpoints
    RPC_ENDPOINTS = {
        "alchemy": "https://polygon-mumbai.g.alchemy.com/v2/",
        "infura": "https://polygon-mumbai.infura.io/v3/",
        "public": "https://rpc-mumbai.maticvigil.com/",
        "chainstack": "https://polygon-mumbai.chainstacklabs.com/",
    }
    
    CHAIN_ID = 80001
    POLYGONSCAN_URL = "https://mumbai.polygonscan.com"
    
    def __init__(
        self,
        contract_address: Optional[str] = None,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        provider_name: str = "public"
    ):
        """
        Initialize the Evidence Anchor Service
        
        Args:
            contract_address: Address of the deployed EvidenceAnchor contract
            private_key: Private key for transaction signing (optional for read-only)
            rpc_url: Custom RPC URL (optional)
            provider_name: Name of the RPC provider to use
        """
        self.contract_address = contract_address or os.getenv("CONTRACT_ADDRESS")
        self.private_key = private_key or os.getenv("ANCHOR_PRIVATE_KEY")
        
        # Initialize Web3
        if rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        else:
            self.w3 = self._get_web3_provider(provider_name)
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Polygon Mumbai")
        
        # Initialize account if private key provided
        self.account = None
        if self.private_key:
            self.account = Account.from_key(self.private_key)
        
        # Initialize contract
        self.contract = None
        if self.contract_address:
            self._init_contract()
    
    def _get_web3_provider(self, provider_name: str = "public") -> Web3:
        """Get Web3 provider for Polygon Mumbai"""
        
        # Try specified provider with API key
        if provider_name == "alchemy":
            api_key = os.getenv("ALCHEMY_API_KEY")
            if api_key:
                return Web3(Web3.HTTPProvider(f"{self.RPC_ENDPOINTS['alchemy']}{api_key}"))
        
        elif provider_name == "infura":
            api_key = os.getenv("INFURA_API_KEY")
            if api_key:
                return Web3(Web3.HTTPProvider(f"{self.RPC_ENDPOINTS['infura']}{api_key}"))
        
        # Try public endpoints
        for name, url in self.RPC_ENDPOINTS.items():
            if name in ["alchemy", "infura"]:
                continue
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                return w3
        
        raise ConnectionError("Could not connect to any Polygon Mumbai RPC endpoint")
    
    def _init_contract(self):
        """Initialize contract instance with ABI"""
        abi = self._load_abi()
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.contract_address),
            abi=abi
        )
    
    def _load_abi(self) -> List[Dict]:
        """Load contract ABI from deployment info or embedded"""
        
        # Try to load from deployment_info.json
        deployment_path = Path("deployment_info.json")
        if deployment_path.exists():
            with open(deployment_path, "r") as f:
                info = json.load(f)
                return info.get("abi", self._get_default_abi())
        
        return self._get_default_abi()
    
    def _get_default_abi(self) -> List[Dict]:
        """Get default contract ABI"""
        return [
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
                "inputs": [{"internalType": "bytes32", "name": "_evidenceHash", "type": "bytes32"}, {"internalType": "string", "name": "_metadata", "type": "string"}],
                "name": "anchorEvidence",
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
                "inputs": [],
                "name": "getAnchorCount",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
        ]
    
    @staticmethod
    def compute_hash(data: bytes) -> str:
        """
        Compute SHA-256 hash of evidence data
        
        Args:
            data: Raw bytes of the evidence file/data
            
        Returns:
            Hex string of the SHA-256 hash
        """
        return "0x" + hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def compute_hash_from_file(file_path: str) -> str:
        """
        Compute SHA-256 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex string of the SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return "0x" + sha256_hash.hexdigest()
    
    def anchor_evidence(
        self,
        evidence_hash: str,
        metadata: str = "",
        wait_for_confirmation: bool = True
    ) -> AnchorResult:
        """
        Anchor an evidence hash on the blockchain
        
        Args:
            evidence_hash: SHA-256 hash of the evidence (hex string)
            metadata: Optional metadata string (e.g., case ID, evidence type)
            wait_for_confirmation: Whether to wait for transaction confirmation
            
        Returns:
            AnchorResult with transaction details
        """
        if not self.account:
            return AnchorResult(
                success=False,
                evidence_hash=evidence_hash,
                error="No private key provided for signing transactions"
            )
        
        if not self.contract:
            return AnchorResult(
                success=False,
                evidence_hash=evidence_hash,
                error="Contract not initialized"
            )
        
        try:
            # Convert hash to bytes32
            hash_bytes = HexBytes(evidence_hash)
            
            # Check if already anchored
            is_anchored = self.contract.functions.isAnchored(hash_bytes).call()
            if is_anchored:
                return AnchorResult(
                    success=False,
                    evidence_hash=evidence_hash,
                    error="Evidence already anchored on blockchain"
                )
            
            # Build transaction
            tx = self.contract.functions.anchorEvidence(
                hash_bytes,
                metadata
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.CHAIN_ID,
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            if wait_for_confirmation:
                # Wait for receipt
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                if receipt['status'] == 1:
                    # Get timestamp from block
                    block = self.w3.eth.get_block(receipt['blockNumber'])
                    
                    return AnchorResult(
                        success=True,
                        evidence_hash=evidence_hash,
                        transaction_hash=tx_hash.hex(),
                        block_number=receipt['blockNumber'],
                        timestamp=block['timestamp'],
                        gas_used=receipt['gasUsed']
                    )
                else:
                    return AnchorResult(
                        success=False,
                        evidence_hash=evidence_hash,
                        transaction_hash=tx_hash.hex(),
                        error="Transaction failed on-chain"
                    )
            else:
                return AnchorResult(
                    success=True,
                    evidence_hash=evidence_hash,
                    transaction_hash=tx_hash.hex()
                )
                
        except Exception as e:
            return AnchorResult(
                success=False,
                evidence_hash=evidence_hash,
                error=str(e)
            )
    
    def verify_evidence(self, evidence_hash: str) -> VerificationResult:
        """
        Verify if an evidence hash is anchored on the blockchain
        
        Args:
            evidence_hash: SHA-256 hash to verify (hex string)
            
        Returns:
            VerificationResult with anchor details
        """
        if not self.contract:
            raise ValueError("Contract not initialized")
        
        try:
            hash_bytes = HexBytes(evidence_hash)
            
            # Call verifyEvidence function
            result = self.contract.functions.verifyEvidence(hash_bytes).call()
            
            anchored, timestamp, submitter, block_number = result
            
            if anchored:
                # Get additional details
                details = self.contract.functions.getAnchorDetails(hash_bytes).call()
                metadata = details[4] if len(details) > 4 else None
                
                return VerificationResult(
                    is_anchored=True,
                    evidence_hash=evidence_hash,
                    timestamp=timestamp,
                    submitter=submitter,
                    block_number=block_number,
                    metadata=metadata
                )
            else:
                return VerificationResult(
                    is_anchored=False,
                    evidence_hash=evidence_hash
                )
                
        except Exception as e:
            raise Exception(f"Verification failed: {e}")
    
    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt for an anchor transaction
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction receipt dictionary or None
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                return {
                    "transactionHash": receipt['transactionHash'].hex(),
                    "blockHash": receipt['blockHash'].hex(),
                    "blockNumber": receipt['blockNumber'],
                    "contractAddress": receipt['contractAddress'],
                    "gasUsed": receipt['gasUsed'],
                    "status": receipt['status'],
                    "from": receipt['from'],
                    "to": receipt['to'],
                }
            return None
        except Exception as e:
            print(f"Error getting receipt: {e}")
            return None
    
    def get_polygonscan_link(self, tx_hash: Optional[str] = None) -> str:
        """Get Polygonscan link for contract or transaction"""
        if tx_hash:
            return f"{self.POLYGONSCAN_URL}/tx/{tx_hash}"
        return f"{self.POLYGONSCAN_URL}/address/{self.contract_address}"
    
    def get_anchor_count(self) -> int:
        """Get total number of anchored evidences"""
        if not self.contract:
            raise ValueError("Contract not initialized")
        return self.contract.functions.getAnchorCount().call()
    
    def batch_anchor_evidence(
        self,
        evidence_hashes: List[str],
        metadata_list: List[str],
        wait_for_confirmation: bool = True
    ) -> List[AnchorResult]:
        """
        Anchor multiple evidence hashes in a batch transaction
        
        Args:
            evidence_hashes: List of SHA-256 hashes
            metadata_list: List of metadata strings
            wait_for_confirmation: Whether to wait for confirmation
            
        Returns:
            List of AnchorResult objects
        """
        if not self.account or not self.contract:
            raise ValueError("Account and contract required for batch anchoring")
        
        if len(evidence_hashes) != len(metadata_list):
            raise ValueError("Hash and metadata lists must have same length")
        
        try:
            # Convert hashes to bytes32
            hash_bytes_list = [HexBytes(h) for h in evidence_hashes]
            
            # Build batch transaction
            tx = self.contract.functions.batchAnchorEvidence(
                hash_bytes_list,
                metadata_list
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000 + (len(evidence_hashes) * 50000),
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.CHAIN_ID,
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            results = []
            
            if wait_for_confirmation:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
                block = self.w3.eth.get_block(receipt['blockNumber'])
                
                for evidence_hash in evidence_hashes:
                    results.append(AnchorResult(
                        success=receipt['status'] == 1,
                        evidence_hash=evidence_hash,
                        transaction_hash=tx_hash.hex(),
                        block_number=receipt['blockNumber'],
                        timestamp=block['timestamp'],
                        gas_used=receipt['gasUsed'] // len(evidence_hashes)
                    ))
            else:
                for evidence_hash in evidence_hashes:
                    results.append(AnchorResult(
                        success=True,
                        evidence_hash=evidence_hash,
                        transaction_hash=tx_hash.hex()
                    ))
            
            return results
            
        except Exception as e:
            return [AnchorResult(
                success=False,
                evidence_hash=h,
                error=str(e)
            ) for h in evidence_hashes]


# Flask/FastAPI integration example
class AnchorAPI:
    """Example API wrapper for web framework integration"""
    
    def __init__(self, service: EvidenceAnchorService):
        self.service = service
    
    def anchor_endpoint(self, file_data: bytes, metadata: str = "") -> Dict[str, Any]:
        """API endpoint handler for anchoring evidence"""
        
        # Compute hash
        evidence_hash = self.service.compute_hash(file_data)
        
        # Submit to blockchain
        result = self.service.anchor_evidence(evidence_hash, metadata)
        
        return {
            "success": result.success,
            "evidence_hash": result.evidence_hash,
            "transaction_hash": result.transaction_hash,
            "block_number": result.block_number,
            "timestamp": result.timestamp,
            "polygonscan_url": self.service.get_polygonscan_link(result.transaction_hash) if result.transaction_hash else None,
            "error": result.error
        }
    
    def verify_endpoint(self, evidence_hash: str) -> Dict[str, Any]:
        """API endpoint handler for verifying evidence"""
        
        result = self.service.verify_evidence(evidence_hash)
        
        response = {
            "is_anchored": result.is_anchored,
            "evidence_hash": result.evidence_hash,
        }
        
        if result.is_anchored:
            response.update({
                "timestamp": result.timestamp,
                "submitter": result.submitter,
                "block_number": result.block_number,
                "metadata": result.metadata,
                "verified_at": datetime.utcnow().isoformat()
            })
        
        return response


def main():
    """CLI example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evidence Anchor Service")
    parser.add_argument("--contract", help="Contract address", default=os.getenv("CONTRACT_ADDRESS"))
    parser.add_argument("--action", choices=["anchor", "verify"], required=True)
    parser.add_argument("--file", help="File to anchor/verify")
    parser.add_argument("--hash", help="Hash to verify")
    parser.add_argument("--metadata", help="Metadata string", default="")
    
    args = parser.parse_args()
    
    # Initialize service
    service = EvidenceAnchorService(contract_address=args.contract)
    
    if args.action == "anchor":
        if not args.file:
            print("Error: --file required for anchor action")
            return
        
        # Compute hash
        evidence_hash = service.compute_hash_from_file(args.file)
        print(f"Evidence hash: {evidence_hash}")
        
        # Anchor on blockchain
        result = service.anchor_evidence(evidence_hash, args.metadata)
        
        if result.success:
            print(f"✅ Anchored successfully!")
            print(f"Transaction: {result.transaction_hash}")
            print(f"Block: {result.block_number}")
            print(f"Explorer: {service.get_polygonscan_link(result.transaction_hash)}")
        else:
            print(f"❌ Failed: {result.error}")
    
    elif args.action == "verify":
        evidence_hash = args.hash
        if args.file:
            evidence_hash = service.compute_hash_from_file(args.file)
        
        if not evidence_hash:
            print("Error: --hash or --file required for verify action")
            return
        
        result = service.verify_evidence(evidence_hash)
        
        if result.is_anchored:
            print(f"✅ Evidence is anchored on blockchain")
            print(f"Hash: {result.evidence_hash}")
            print(f"Timestamp: {datetime.fromtimestamp(result.timestamp)}")
            print(f"Submitter: {result.submitter}")
            print(f"Block: {result.block_number}")
            if result.metadata:
                print(f"Metadata: {result.metadata}")
        else:
            print(f"❌ Evidence not found on blockchain")
            print(f"Hash: {result.evidence_hash}")


if __name__ == "__main__":
    main()
