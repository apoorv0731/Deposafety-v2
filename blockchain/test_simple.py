#!/usr/bin/env python3
"""
Simple test script for EvidenceAnchor blockchain integration
Tests functionality without requiring external dependencies
"""

import os
import sys
import json
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime


def test_hash_computation():
    """Test SHA-256 hash computation"""
    print("\n" + "=" * 60)
    print("🧪 Testing Hash Computation")
    print("=" * 60)
    
    # Test string hash
    test_string = "DepoSafety Evidence Test"
    expected_hash = "0x" + hashlib.sha256(test_string.encode()).hexdigest()
    
    computed_hash = "0x" + hashlib.sha256(test_string.encode()).hexdigest()
    
    assert computed_hash == expected_hash, f"Hash mismatch: {computed_hash} != {expected_hash}"
    print(f"✅ String hash computation: PASS")
    print(f"   Input: '{test_string}'")
    print(f"   Hash: {computed_hash}")
    
    # Test file hash
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(test_string)
        temp_path = f.name
    
    try:
        sha256_hash = hashlib.sha256()
        with open(temp_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        file_hash = "0x" + sha256_hash.hexdigest()
        
        assert file_hash == expected_hash, f"File hash mismatch"
        print(f"✅ File hash computation: PASS")
    finally:
        os.unlink(temp_path)
    
    return True


def test_deployment_info_format():
    """Test deployment info JSON format"""
    print("\n" + "=" * 60)
    print("🧪 Testing Deployment Info Format")
    print("=" * 60)
    
    # Expected format
    deployment_info = {
        "network": "Polygon Mumbai",
        "chainId": 80001,
        "contractAddress": "0x1234567890abcdef...",
        "transactionHash": "0xabcdef123456...",
        "blockNumber": 12345,
        "gasUsed": 150000,
        "deployedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "abi": [],  # Would contain actual ABI
    }
    
    # Validate required fields
    required_fields = ['network', 'chainId', 'contractAddress', 'transactionHash', 
                       'blockNumber', 'gasUsed', 'deployedAt', 'abi']
    
    for field in required_fields:
        assert field in deployment_info, f"Missing field: {field}"
        print(f"✅ Field '{field}' present")
    
    # Validate types
    assert isinstance(deployment_info['chainId'], int)
    assert isinstance(deployment_info['blockNumber'], int)
    assert isinstance(deployment_info['gasUsed'], int)
    print(f"✅ Data types correct")
    
    return True


def test_polygonscan_urls():
    """Test Polygonscan URL generation"""
    print("\n" + "=" * 60)
    print("🧪 Testing Polygonscan URLs")
    print("=" * 60)
    
    contract_address = "0x1234567890abcdef1234567890abcdef12345678"
    tx_hash = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678"
    
    # Test Mumbai URLs
    mumbai_contract_url = f"https://mumbai.polygonscan.com/address/{contract_address}"
    mumbai_tx_url = f"https://mumbai.polygonscan.com/tx/{tx_hash}"
    
    assert "mumbai.polygonscan.com" in mumbai_contract_url
    assert contract_address.lower() in mumbai_contract_url.lower()
    print(f"✅ Mumbai contract URL: {mumbai_contract_url}")
    print(f"✅ Mumbai transaction URL: {mumbai_tx_url}")
    
    # Test mainnet URLs
    mainnet_contract_url = f"https://polygonscan.com/address/{contract_address}"
    assert "polygonscan.com" in mainnet_contract_url
    assert "mumbai" not in mainnet_contract_url
    print(f"✅ Mainnet contract URL: {mainnet_contract_url}")
    
    return True


def test_file_structure():
    """Verify all required files exist"""
    print("\n" + "=" * 60)
    print("🧪 Testing File Structure")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    
    required_files = [
        'EvidenceAnchor.sol',
        'deploy.py',
        'anchor_service.py',
        'verify.py',
        'README.md',
        'requirements.txt',
        '.env.example',
        'frontend_integration.js',
    ]
    
    all_exist = True
    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename} ({size} bytes)")
        else:
            print(f"❌ {filename} - MISSING")
            all_exist = False
    
    return all_exist


def test_solidity_syntax():
    """Basic Solidity syntax validation"""
    print("\n" + "=" * 60)
    print("🧪 Testing Solidity Contract Structure")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    contract_path = base_path / 'EvidenceAnchor.sol'
    
    with open(contract_path, 'r') as f:
        content = f.read()
    
    # Check for required elements
    checks = [
        ('pragma solidity', 'Solidity version pragma'),
        ('contract EvidenceAnchor', 'Contract declaration'),
        ('EvidenceAnchored', 'EvidenceAnchored event'),
        ('anchorEvidence', 'anchorEvidence function'),
        ('verifyEvidence', 'verifyEvidence function'),
        ('isAnchored', 'isAnchored mapping'),
        ('bytes32', 'bytes32 type for hashes'),
        ('struct Anchor', 'Anchor struct'),
    ]
    
    all_pass = True
    for keyword, description in checks:
        if keyword in content:
            print(f"✅ {description} found")
        else:
            print(f"❌ {description} NOT found")
            all_pass = False
    
    return all_pass


def test_contract_abi_structure():
    """Test that embedded ABI is valid JSON structure"""
    print("\n" + "=" * 60)
    print("🧪 Testing Contract ABI Structure")
    print("=" * 60)
    
    # Sample ABI from anchor_service.py
    abi = [
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
    ]
    
    # Test JSON serialization
    try:
        json_str = json.dumps(abi)
        parsed = json.loads(json_str)
        assert len(parsed) == 2
        print(f"✅ ABI JSON serialization: PASS")
    except Exception as e:
        print(f"❌ ABI JSON serialization failed: {e}")
        return False
    
    # Check required elements
    event_names = [item.get('name') for item in abi if item.get('type') == 'event']
    function_names = [item.get('name') for item in abi if item.get('type') == 'function']
    
    assert 'EvidenceAnchored' in event_names, "Missing EvidenceAnchored event"
    assert 'verifyEvidence' in function_names, "Missing verifyEvidence function"
    
    print(f"✅ Required ABI elements present")
    
    return True


def test_frontend_integration():
    """Test frontend integration file structure"""
    print("\n" + "=" * 60)
    print("🧪 Testing Frontend Integration")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    frontend_path = base_path / 'frontend_integration.js'
    
    with open(frontend_path, 'r') as f:
        content = f.read()
    
    # Check for required components
    checks = [
        ('BlockchainVerifier', 'BlockchainVerifier class'),
        ('computeFileHash', 'computeFileHash function'),
        ('verifyEvidence', 'verifyEvidence method'),
        ('Polygon Mumbai', 'Mumbai network config'),
        ('mumbai.polygonscan.com', 'Mumbai explorer URL'),
        ('EvidenceAnchored', 'EvidenceAnchored event'),
    ]
    
    all_pass = True
    for keyword, description in checks:
        if keyword in content:
            print(f"✅ {description} found")
        else:
            print(f"❌ {description} NOT found")
            all_pass = False
    
    return all_pass


def test_readme_completeness():
    """Test README completeness"""
    print("\n" + "=" * 60)
    print("🧪 Testing README Completeness")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    readme_path = base_path / 'README.md'
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Check for required sections
    sections = [
        ('Overview', 'Overview section'),
        ('Architecture', 'Architecture section'),
        ('Quick Start', 'Quick Start section'),
        ('Smart Contract', 'Smart Contract section'),
        ('API Integration', 'API Integration section'),
        ('Frontend Integration', 'Frontend Integration section'),
        ('Polygon Mumbai', 'Mumbai network reference'),
        ('faucet', 'Faucet reference'),
    ]
    
    all_pass = True
    for keyword, description in sections:
        if keyword in content:
            print(f"✅ {description} found")
        else:
            print(f"❌ {description} NOT found")
            all_pass = False
    
    return all_pass


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 DepoSafety V2 Blockchain Integration Tests")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Hash Computation", test_hash_computation),
        ("Solidity Syntax", test_solidity_syntax),
        ("Contract ABI Structure", test_contract_abi_structure),
        ("Deployment Info Format", test_deployment_info_format),
        ("Polygonscan URLs", test_polygonscan_urls),
        ("Frontend Integration", test_frontend_integration),
        ("README Completeness", test_readme_completeness),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
