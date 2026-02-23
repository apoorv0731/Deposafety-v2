/**
 * DepoSafety V2 - Blockchain Verification Frontend Integration
 * 
 * This module provides React/Vue components and utility functions
 * for displaying blockchain verification badges and linking to Polygonscan.
 */

// ============================================
// Configuration
// ============================================

const CONFIG = {
  // Mumbai testnet
  MUMBAI: {
    chainId: 80001,
    name: 'Polygon Mumbai',
    rpcUrl: 'https://rpc-mumbai.maticvigil.com/',
    explorerUrl: 'https://mumbai.polygonscan.com',
    contractAddress: process.env.REACT_APP_CONTRACT_ADDRESS || '0x...',
  },
  // Polygon mainnet (for production)
  POLYGON: {
    chainId: 137,
    name: 'Polygon',
    rpcUrl: 'https://polygon-rpc.com',
    explorerUrl: 'https://polygonscan.com',
    contractAddress: process.env.REACT_APP_CONTRACT_ADDRESS || '0x...',
  }
};

// Contract ABI (minimal for verification)
const CONTRACT_ABI = [
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
    "anonymous": false,
    "inputs": [
      {"indexed": true, "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
      {"indexed": true, "internalType": "address", "name": "submitter", "type": "address"},
      {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
      {"indexed": false, "internalType": "uint256", "name": "blockNumber", "type": "uint256"}
    ],
    "name": "EvidenceAnchored",
    "type": "event"
  }
];

// ============================================
// Utility Functions
// ============================================

/**
 * Compute SHA-256 hash of a file
 * @param {File} file - Browser File object
 * @returns {Promise<string>} - Hex string with 0x prefix
 */
export async function computeFileHash(file) {
  const arrayBuffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return '0x' + hashHex;
}

/**
 * Compute SHA-256 hash of a string
 * @param {string} data - String to hash
 * @returns {Promise<string>} - Hex string with 0x prefix
 */
export async function computeStringHash(data) {
  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest('SHA-256', encoder.encode(data));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return '0x' + hashHex;
}

/**
 * Format timestamp to human-readable date
 * @param {number} timestamp - Unix timestamp
 * @returns {string} - Formatted date string
 */
export function formatTimestamp(timestamp) {
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });
}

/**
 * Truncate address for display
 * @param {string} address - Ethereum address
 * @returns {string} - Truncated address (0x1234...5678)
 */
export function truncateAddress(address) {
  if (!address || address.length < 10) return address;
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

/**
 * Get Polygonscan URL for address or transaction
 * @param {string} hash - Address or transaction hash
 * @param {string} type - 'address' or 'tx'
 * @param {boolean} isMainnet - Use mainnet instead of Mumbai
 * @returns {string} - Polygonscan URL
 */
export function getExplorerUrl(hash, type = 'address', isMainnet = false) {
  const config = isMainnet ? CONFIG.POLYGON : CONFIG.MUMBAI;
  return `${config.explorerUrl}/${type}/${hash}`;
}

// ============================================
// Blockchain Verification Service
// ============================================

export class BlockchainVerifier {
  constructor(provider, contractAddress, isMainnet = false) {
    this.provider = provider;
    this.contractAddress = contractAddress;
    this.config = isMainnet ? CONFIG.POLYGON : CONFIG.MUMBAI;
    
    // Initialize contract (using ethers.js)
    if (window.ethers) {
      this.contract = new ethers.Contract(contractAddress, CONTRACT_ABI, provider);
    }
  }

  /**
   * Verify if evidence hash is anchored on blockchain
   * @param {string} evidenceHash - SHA-256 hash with 0x prefix
   * @returns {Promise<Object>} - Verification result
   */
  async verifyEvidence(evidenceHash) {
    if (!this.contract) {
      throw new Error('Ethers.js not loaded');
    }

    try {
      const [isAnchored, timestamp, submitter, blockNumber] = 
        await this.contract.verifyEvidence(evidenceHash);

      if (!isAnchored) {
        return {
          isAnchored: false,
          evidenceHash,
          message: 'Evidence not found on blockchain'
        };
      }

      // Get additional details
      const details = await this.contract.getAnchorDetails(evidenceHash);
      
      return {
        isAnchored: true,
        evidenceHash,
        timestamp: timestamp.toNumber(),
        timestampFormatted: formatTimestamp(timestamp.toNumber()),
        submitter,
        blockNumber: blockNumber.toNumber(),
        metadata: details[4],
        contractAddress: this.contractAddress,
        network: this.config.name,
        explorerUrl: getExplorerUrl(this.contractAddress, 'address', this.config.chainId === 137)
      };
    } catch (error) {
      console.error('Verification error:', error);
      return {
        isAnchored: false,
        evidenceHash,
        error: error.message
      };
    }
  }

  /**
   * Verify a file by computing its hash
   * @param {File} file - Browser File object
   * @returns {Promise<Object>} - Verification result
   */
  async verifyFile(file) {
    const hash = await computeFileHash(file);
    const result = await this.verifyEvidence(hash);
    return {
      ...result,
      fileName: file.name,
      fileSize: file.size,
      computedHash: hash
    };
  }
}

// ============================================
// React Components (for React apps)
// ============================================

/**
 * React Component: BlockchainVerificationBadge
 * 
 * Usage:
 * <BlockchainVerificationBadge 
 *   evidenceHash="0x..."
 *   verifier={verifierInstance}
 * />
 */
export function BlockchainVerificationBadge({ evidenceHash, verifier, file }) {
  const [status, setStatus] = React.useState('loading'); // loading | verified | not-verified | error
  const [data, setData] = React.useState(null);

  React.useEffect(() => {
    async function verify() {
      try {
        let result;
        if (file) {
          result = await verifier.verifyFile(file);
        } else {
          result = await verifier.verifyEvidence(evidenceHash);
        }
        
        setData(result);
        setStatus(result.isAnchored ? 'verified' : 'not-verified');
      } catch (error) {
        setStatus('error');
        setData({ error: error.message });
      }
    }

    if (verifier && (evidenceHash || file)) {
      verify();
    }
  }, [evidenceHash, file, verifier]);

  // Loading state
  if (status === 'loading') {
    return (
      <div className="blockchain-badge loading">
        <span className="spinner">⏳</span>
        <span>Verifying on blockchain...</span>
      </div>
    );
  }

  // Error state
  if (status === 'error') {
    return (
      <div className="blockchain-badge error">
        <span>⚠️</span>
        <span>Verification failed: {data?.error}</span>
      </div>
    );
  }

  // Not verified state
  if (status === 'not-verified') {
    return (
      <div className="blockchain-badge not-verified">
        <span>⚠️</span>
        <span>Not verified on blockchain</span>
      </div>
    );
  }

  // Verified state
  return (
    <div className="blockchain-badge verified">
      <div className="badge-header">
        <span className="icon">✅</span>
        <span className="title">Verified on {data.network}</span>
      </div>
      
      <div className="badge-details">
        <div className="detail-row">
          <span className="label">Anchored:</span>
          <span className="value">{data.timestampFormatted}</span>
        </div>
        
        <div className="detail-row">
          <span className="label">Submitter:</span>
          <a 
            href={getExplorerUrl(data.submitter, 'address')} 
            target="_blank" 
            rel="noopener noreferrer"
            className="value link"
          >
            {truncateAddress(data.submitter)}
          </a>
        </div>
        
        <div className="detail-row">
          <span className="label">Block:</span>
          <span className="value">#{data.blockNumber}</span>
        </div>
        
        {data.metadata && (
          <div className="detail-row">
            <span className="label">Metadata:</span>
            <span className="value">{data.metadata}</span>
          </div>
        )}
        
        <div className="badge-actions">
          <a 
            href={data.explorerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="explorer-link"
          >
            🔗 View on Polygonscan
          </a>
        </div>
      </div>
    </div>
  );
}

// ============================================
// CSS Styles (can be used as a CSS module)
// ============================================

export const blockchainBadgeStyles = `
.blockchain-badge {
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.blockchain-badge.loading {
  background: #f0f0f0;
  color: #666;
}

.blockchain-badge.verified {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border: 1px solid #4caf50;
}

.blockchain-badge.not-verified {
  background: #fff3e0;
  border: 1px solid #ff9800;
  color: #e65100;
}

.blockchain-badge.error {
  background: #ffebee;
  border: 1px solid #f44336;
  color: #c62828;
}

.badge-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 16px;
}

.blockchain-badge.verified .title {
  color: #2e7d32;
}

.badge-details {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  padding: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  color: #666;
  font-size: 13px;
}

.detail-row .value {
  color: #333;
  font-size: 13px;
  font-weight: 500;
}

.detail-row .value.link {
  color: #1976d2;
  text-decoration: none;
}

.detail-row .value.link:hover {
  text-decoration: underline;
}

.badge-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.explorer-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #1976d2;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.explorer-link:hover {
  text-decoration: underline;
}

.spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
`;

// ============================================
// Vue Component (for Vue apps)
// ============================================

/**
 * Vue Component: BlockchainVerificationBadge
 * 
 * Usage:
 * <BlockchainVerificationBadge 
 *   :evidence-hash="hash"
 *   :verifier="verifier"
 * />
 */
export const BlockchainVerificationBadgeVue = {
  name: 'BlockchainVerificationBadge',
  props: {
    evidenceHash: String,
    file: File,
    verifier: Object
  },
  data() {
    return {
      status: 'loading',
      data: null
    };
  },
  async mounted() {
    await this.verify();
  },
  methods: {
    async verify() {
      try {
        let result;
        if (this.file) {
          result = await this.verifier.verifyFile(this.file);
        } else {
          result = await this.verifier.verifyEvidence(this.evidenceHash);
        }
        
        this.data = result;
        this.status = result.isAnchored ? 'verified' : 'not-verified';
      } catch (error) {
        this.status = 'error';
        this.data = { error: error.message };
      }
    },
    formatTimestamp(timestamp) {
      return formatTimestamp(timestamp);
    },
    truncateAddress(address) {
      return truncateAddress(address);
    },
    getExplorerUrl(hash, type = 'address') {
      return getExplorerUrl(hash, type, this.data?.network === 'Polygon');
    }
  },
  template: `
    <div :class="['blockchain-badge', status]">
      <div v-if="status === 'loading'" class="badge-loading">
        <span class="spinner">⏳</span>
        <span>Verifying on blockchain...</span>
      </div>
      
      <div v-else-if="status === 'error'" class="badge-error">
        <span>⚠️ Verification failed: {{ data?.error }}</span>
      </div>
      
      <div v-else-if="status === 'not-verified'" class="badge-not-verified">
        <span>⚠️ Not verified on blockchain</span>
      </div>
      
      <div v-else class="badge-verified">
        <div class="badge-header">
          <span>✅</span>
          <span>Verified on {{ data.network }}</span>
        </div>
        
        <div class="badge-details">
          <div class="detail-row">
            <span>Anchored:</span>
            <span>{{ formatTimestamp(data.timestamp) }}</span>
          </div>
          
          <div class="detail-row">
            <span>Submitter:</span>
            <a :href="getExplorerUrl(data.submitter)" target="_blank">
              {{ truncateAddress(data.submitter) }}
            </a>
          </div>
          
          <div class="detail-row">
            <span>Block:</span>
            <span>#{{ data.blockNumber }}</span>
          </div>
          
          <div v-if="data.metadata" class="detail-row">
            <span>Metadata:</span>
            <span>{{ data.metadata }}</span>
          </div>
          
          <a :href="data.explorerUrl" target="_blank" class="explorer-link">
            🔗 View on Polygonscan
          </a>
        </div>
      </div>
    </div>
  `
};

// ============================================
// Default Export
// ============================================

export default {
  BlockchainVerifier,
  BlockchainVerificationBadge,
  BlockchainVerificationBadgeVue,
  computeFileHash,
  computeStringHash,
  formatTimestamp,
  truncateAddress,
  getExplorerUrl,
  blockchainBadgeStyles,
  CONFIG,
  CONTRACT_ABI
};
