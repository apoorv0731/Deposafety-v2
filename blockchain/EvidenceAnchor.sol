// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title EvidenceAnchor
 * @dev Smart contract for anchoring evidence hashes on Polygon Mumbai testnet
 * Stores SHA-256 hashes of evidence with timestamps and submitter addresses
 */
contract EvidenceAnchor {
    
    // ============ State Variables ============
    
    /// @notice Owner of the contract
    address public owner;
    
    /// @notice Mapping of evidence hash to anchor details
    mapping(bytes32 => Anchor) public anchors;
    
    /// @notice Array to track all anchored hashes for enumeration
    bytes32[] public anchorList;
    
    /// @notice Mapping to check if a hash has been anchored
    mapping(bytes32 => bool) public isAnchored;
    
    // ============ Structs ============
    
    /**
     * @dev Structure to store anchor details
     * @param evidenceHash The SHA-256 hash of the evidence
     * @param timestamp Unix timestamp when anchored
     * @param submitter Address that submitted the anchor
     * @param blockNumber Block number when anchored
     * @param metadata Optional metadata string (e.g., evidence type, case ID)
     */
    struct Anchor {
        bytes32 evidenceHash;
        uint256 timestamp;
        address submitter;
        uint256 blockNumber;
        string metadata;
    }
    
    // ============ Events ============
    
    /**
     * @dev Emitted when new evidence is anchored
     * @param evidenceHash The SHA-256 hash of the evidence
     * @param submitter Address that submitted the anchor
     * @param timestamp Unix timestamp when anchored
     * @param blockNumber Block number when anchored
     */
    event EvidenceAnchored(
        bytes32 indexed evidenceHash,
        address indexed submitter,
        uint256 timestamp,
        uint256 blockNumber
    );
    
    /**
     * @dev Emitted when anchor metadata is updated
     * @param evidenceHash The SHA-256 hash of the evidence
     * @param metadata Updated metadata string
     */
    event MetadataUpdated(bytes32 indexed evidenceHash, string metadata);
    
    // ============ Modifiers ============
    
    modifier onlyOwner() {
        require(msg.sender == owner, "EvidenceAnchor: caller is not the owner");
        _;
    }
    
    modifier notAnchored(bytes32 _evidenceHash) {
        require(!isAnchored[_evidenceHash], "EvidenceAnchor: evidence already anchored");
        _;
    }
    
    // ============ Constructor ============
    
    constructor() {
        owner = msg.sender;
    }
    
    // ============ External Functions ============
    
    /**
     * @dev Anchor a new evidence hash on the blockchain
     * @param _evidenceHash The SHA-256 hash of the evidence
     * @param _metadata Optional metadata string
     */
    function anchorEvidence(bytes32 _evidenceHash, string calldata _metadata) 
        external 
        notAnchored(_evidenceHash) 
    {
        require(_evidenceHash != bytes32(0), "EvidenceAnchor: invalid hash");
        
        Anchor memory newAnchor = Anchor({
            evidenceHash: _evidenceHash,
            timestamp: block.timestamp,
            submitter: msg.sender,
            blockNumber: block.number,
            metadata: _metadata
        });
        
        anchors[_evidenceHash] = newAnchor;
        isAnchored[_evidenceHash] = true;
        anchorList.push(_evidenceHash);
        
        emit EvidenceAnchored(
            _evidenceHash,
            msg.sender,
            block.timestamp,
            block.number
        );
    }
    
    /**
     * @dev Update metadata for an existing anchor (only by original submitter or owner)
     * @param _evidenceHash The SHA-256 hash of the evidence
     * @param _metadata New metadata string
     */
    function updateMetadata(bytes32 _evidenceHash, string calldata _metadata) external {
        require(isAnchored[_evidenceHash], "EvidenceAnchor: evidence not anchored");
        require(
            msg.sender == anchors[_evidenceHash].submitter || msg.sender == owner,
            "EvidenceAnchor: not authorized"
        );
        
        anchors[_evidenceHash].metadata = _metadata;
        
        emit MetadataUpdated(_evidenceHash, _metadata);
    }
    
    /**
     * @dev Batch anchor multiple evidence hashes
     * @param _evidenceHashes Array of SHA-256 hashes
     * @param _metadataArray Array of metadata strings (must match length of hashes)
     */
    function batchAnchorEvidence(
        bytes32[] calldata _evidenceHashes, 
        string[] calldata _metadataArray
    ) external {
        require(
            _evidenceHashes.length == _metadataArray.length,
            "EvidenceAnchor: array length mismatch"
        );
        require(_evidenceHashes.length > 0, "EvidenceAnchor: empty arrays");
        require(_evidenceHashes.length <= 100, "EvidenceAnchor: batch too large");
        
        for (uint256 i = 0; i < _evidenceHashes.length; i++) {
            bytes32 hash = _evidenceHashes[i];
            
            if (!isAnchored[hash] && hash != bytes32(0)) {
                Anchor memory newAnchor = Anchor({
                    evidenceHash: hash,
                    timestamp: block.timestamp,
                    submitter: msg.sender,
                    blockNumber: block.number,
                    metadata: _metadataArray[i]
                });
                
                anchors[hash] = newAnchor;
                isAnchored[hash] = true;
                anchorList.push(hash);
                
                emit EvidenceAnchored(
                    hash,
                    msg.sender,
                    block.timestamp,
                    block.number
                );
            }
        }
    }
    
    // ============ View Functions ============
    
    /**
     * @dev Verify if an evidence hash is anchored and get details
     * @param _evidenceHash The SHA-256 hash to verify
     * @return anchored Whether the hash is anchored
     * @return timestamp Timestamp when anchored
     * @return submitter Address of the submitter
     * @return blockNumber Block number when anchored
     */
    function verifyEvidence(bytes32 _evidenceHash) 
        external 
        view 
        returns (
            bool anchored,
            uint256 timestamp,
            address submitter,
            uint256 blockNumber
        ) 
    {
        if (!isAnchored[_evidenceHash]) {
            return (false, 0, address(0), 0);
        }
        
        Anchor storage anchor = anchors[_evidenceHash];
        return (
            true,
            anchor.timestamp,
            anchor.submitter,
            anchor.blockNumber
        );
    }
    
    /**
     * @dev Get full anchor details including metadata
     * @param _evidenceHash The SHA-256 hash
     * @return Full anchor struct
     */
    function getAnchorDetails(bytes32 _evidenceHash) 
        external 
        view 
        returns (Anchor memory) 
    {
        require(isAnchored[_evidenceHash], "EvidenceAnchor: evidence not anchored");
        return anchors[_evidenceHash];
    }
    
    /**
     * @dev Get total number of anchored evidences
     * @return Total count
     */
    function getAnchorCount() external view returns (uint256) {
        return anchorList.length;
    }
    
    /**
     * @dev Get paginated list of anchored hashes
     * @param _start Start index
     * @param _limit Maximum number of items to return
     * @return Array of evidence hashes
     */
    function getAnchorsPaginated(uint256 _start, uint256 _limit) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        require(_start < anchorList.length, "EvidenceAnchor: start out of bounds");
        
        uint256 end = _start + _limit;
        if (end > anchorList.length) {
            end = anchorList.length;
        }
        
        bytes32[] memory result = new bytes32[](end - _start);
        for (uint256 i = _start; i < end; i++) {
            result[i - _start] = anchorList[i];
        }
        
        return result;
    }
    
    // ============ Admin Functions ============
    
    /**
     * @dev Transfer ownership of the contract
     * @param _newOwner Address of the new owner
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "EvidenceAnchor: invalid address");
        owner = _newOwner;
    }
    
    /**
     * @dev Renounce ownership (contract becomes ownerless)
     */
    function renounceOwnership() external onlyOwner {
        owner = address(0);
    }
}
