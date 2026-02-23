"""
Blockchain anchoring service using Polygon Mumbai testnet.
Uses Web3.py for smart contract interactions.
"""
from web3 import Web3
from eth_account import Account
from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging
import hashlib

from config import get_settings

logger = logging.getLogger(__name__)


# Simplified ABI for the DepoSafety smart contract
# In production, load this from a compiled contract JSON
DEPO_SAFETY_ABI = [
    {
        "inputs": [
            {"name": "scanId", "type": "string"},
            {"name": "metadataHash", "type": "string"},
            {"name": "timestamp", "type": "uint256"}
        ],
        "name": "anchorInspection",
        "outputs": [{"name": "", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "scanId", "type": "string"}],
        "name": "getAnchor",
        "outputs": [
            {"name": "metadataHash", "type": "string"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "blockNumber", "type": "uint256"},
            {"name": "transactionHash", "type": "bytes32"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "scanId", "type": "string"}],
        "name": "isAnchored",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "scanId", "type": "string"},
            {"indexed": False, "name": "metadataHash", "type": "string"},
            {"indexed": False, "name": "timestamp", "type": "uint256"},
            {"indexed": False, "name": "transactionHash", "type": "bytes32"}
        ],
        "name": "InspectionAnchored",
        "type": "event"
    }
]


class BlockchainClient:
    """Polygon blockchain client for anchoring inspection data."""
    
    _instance: Optional['BlockchainClient'] = None
    _web3: Optional[Web3] = None
    _contract = None
    _account: Optional[Account] = None
    _chain_id: int = 80001  # Mumbai testnet
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._web3 is None:
            settings = get_settings()
            self._chain_id = settings.chain_id
            
            if settings.polygon_rpc_url:
                try:
                    self._web3 = Web3(Web3.HTTPProvider(settings.polygon_rpc_url))
                    
                    # Initialize account from private key
                    if settings.wallet_private_key:
                        self._account = Account.from_key(settings.wallet_private_key)
                        logger.info(f"Blockchain account loaded: {self._account.address}")
                    
                    # Initialize contract
                    if settings.contract_address:
                        self._contract = self._web3.eth.contract(
                            address=Web3.to_checksum_address(settings.contract_address),
                            abi=DEPO_SAFETY_ABI
                        )
                    
                    # Test connection
                    if self._web3.is_connected():
                        logger.info(f"Connected to Polygon (Chain ID: {self._web3.eth.chain_id})")
                    else:
                        logger.warning("Failed to connect to Polygon RPC")
                        
                except Exception as e:
                    logger.error(f"Failed to initialize blockchain client: {e}")
                    self._web3 = None
            else:
                logger.warning("Polygon RPC URL not configured")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to the blockchain."""
        return self._web3 is not None and self._web3.is_connected()
    
    @property
    def web3(self) -> Optional[Web3]:
        """Get the Web3 instance."""
        return self._web3
    
    def generate_metadata_hash(self, scan_data: Dict[str, Any]) -> str:
        """Generate a hash of scan metadata for anchoring."""
        # Create a deterministic hash from scan data
        data_string = json.dumps(scan_data, sort_keys=True, default=str)
        return "0x" + hashlib.sha256(data_string.encode()).hexdigest()
    
    async def anchor_inspection(
        self, 
        scan_id: str, 
        metadata_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Anchor inspection data to the blockchain.
        
        Args:
            scan_id: Unique scan identifier
            metadata_hash: Hash of the inspection metadata
            
        Returns:
            Transaction details or None if failed
        """
        if not self.is_connected or not self._account or not self._contract:
            logger.error("Blockchain client not properly initialized")
            return None
        
        try:
            timestamp = int(datetime.utcnow().timestamp())
            
            # Build transaction
            tx = self._contract.functions.anchorInspection(
                scan_id,
                metadata_hash,
                timestamp
            ).build_transaction({
                'from': self._account.address,
                'nonce': self._web3.eth.get_transaction_count(self._account.address),
                'gas': 200000,  # Estimate or calculate dynamically
                'gasPrice': self._web3.eth.gas_price,
                'chainId': self._chain_id
            })
            
            # Sign transaction
            signed_tx = self._web3.eth.account.sign_transaction(tx, self._account.key)
            
            # Send transaction
            tx_hash = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if tx_receipt['status'] == 1:
                logger.info(f"Inspection anchored successfully: {tx_hash.hex()}")
                return {
                    'success': True,
                    'transaction_hash': tx_hash.hex(),
                    'block_number': tx_receipt['blockNumber'],
                    'gas_used': tx_receipt['gasUsed'],
                    'timestamp': datetime.utcnow()
                }
            else:
                logger.error(f"Transaction failed: {tx_hash.hex()}")
                return None
                
        except Exception as e:
            logger.error(f"Error anchoring inspection: {e}")
            return None
    
    async def verify_anchor(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify if a scan is anchored on the blockchain.
        
        Args:
            scan_id: Unique scan identifier
            
        Returns:
            Verification details or None if not found
        """
        if not self.is_connected or not self._contract:
            logger.error("Blockchain client not properly initialized")
            return None
        
        try:
            # Check if anchored
            is_anchored = self._contract.functions.isAnchored(scan_id).call()
            
            if not is_anchored:
                return {
                    'scan_id': scan_id,
                    'is_verified': False,
                    'transaction_hash': None,
                    'block_number': None,
                    'timestamp': None,
                    'metadata_hash': None
                }
            
            # Get anchor details
            result = self._contract.functions.getAnchor(scan_id).call()
            metadata_hash, timestamp, block_number, tx_hash = result
            
            return {
                'scan_id': scan_id,
                'is_verified': True,
                'transaction_hash': tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash,
                'block_number': block_number,
                'timestamp': datetime.utcfromtimestamp(timestamp),
                'metadata_hash': metadata_hash
            }
            
        except Exception as e:
            logger.error(f"Error verifying anchor: {e}")
            return None
    
    async def get_transaction_status(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get the status of a transaction."""
        if not self.is_connected:
            return None
        
        try:
            receipt = self._web3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                return {
                    'transaction_hash': tx_hash,
                    'block_number': receipt['blockNumber'],
                    'status': 'confirmed' if receipt['status'] == 1 else 'failed',
                    'gas_used': receipt['gasUsed'],
                    'confirmations': self._web3.eth.block_number - receipt['blockNumber']
                }
            else:
                return {
                    'transaction_hash': tx_hash,
                    'status': 'pending'
                }
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return None
    
    def get_balance(self) -> Optional[float]:
        """Get the wallet balance in MATIC."""
        if not self.is_connected or not self._account:
            return None
        
        try:
            balance_wei = self._web3.eth.get_balance(self._account.address)
            return self._web3.from_wei(balance_wei, 'ether')
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None


# Global blockchain client instance
blockchain = BlockchainClient()
