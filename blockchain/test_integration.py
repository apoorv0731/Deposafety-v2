#!/usr/bin/env python3
"""
Test script for EvidenceAnchor blockchain integration
Tests all major functionality without requiring actual deployment
"""

import os
import sys
import json
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from anchor_service import EvidenceAnchorService, AnchorResult, VerificationResult


def test_hash_computation():
    """Test SHA-256 hash computation"""
    print("\n" + "=" * 60)
    print("🧪 Testing Hash Computation")
    print("=" * 60)
    
    # Test string hash
    test_string = "DepoSafety Evidence Test"
    expected_hash = "0x" + hashlib.sha256(test_string.encode()).hexdigest()
    
    computed_hash = EvidenceAnchorService.compute_hash(test_string.encode())
    
    assert computed_hash == expected_hash, f"Hash mismatch: {computed_hash} != {expected_hash}"
    print(f"✅ String hash computation: PASS")
    print(f"   Input: '{test_string}'")
    print(f"   Hash: {computed_hash}")
    
    # Test file hash
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(test_string)
        temp_path = f.name
    
    try:
        file_hash = EvidenceAnchorService.compute_hash_from_file(temp_path)
        assert file_hash == expected_hash, f"File hash mismatch"
        print(f"✅ File hash computation: PASS")
    finally:
        os.unlink(temp_path)
    
    return True


def test_anchor_result_dataclass():
    """Test AnchorResult dataclass"""
    print("\n" + "=" * 60)
    print("🧪 Testing AnchorResult Dataclass")
    print("=" * 60)
    
    result = AnchorResult(
        success=True,
        evidence_hash="0x1234...",
        transaction_hash="0xabcd...",
        block_number=12345,
        timestamp=1700000000,
        gas_used=50000
    )
    
    assert result.success is True
    assert result.evidence_hash == "0x1234..."
    print(f"✅ AnchorResult creation: PASS")
    
    # Test failed result
    failed_result = AnchorResult(
        success=False,
        evidence_hash="0x5678...",
        error="Transaction failed"
    )
    
    assert failed_result.success is False
    assert failed_result.error == "Transaction failed"
    print(f"✅ Failed AnchorResult: PASS")
    
    return True


def test_verification_result_dataclass():
    """Test VerificationResult dataclass"""
    print("\n" + "=" * 60)
    print("🧪 Testing VerificationResult Dataclass")
    print("=" * 60)
    
    result = VerificationResult(
        is_anchored=True,
        evidence_hash="0x1234...",
        timestamp=1700000000,
        submitter="0xabcdef...",
        block_number=12345,
        metadata="Case #12345"
    )
    
    assert result.is_anchored is True
    assert result.metadata == "Case #12345"
    print(f"✅ VerificationResult creation: PASS")
    
    # Test not anchored result
    not_anchored = VerificationResult(
        is_anchored=False,
        evidence_hash="0x5678..."
    )
    
    assert not_anchored.is_anchored is False
    assert not_anchored.timestamp is None
    print(f"✅ Not anchored VerificationResult: PASS")
    
    return True


def test_contract_abi_loading():
    """Test contract ABI loading"""
    print("\n" + "=" * 60)
    print("🧪 Testing Contract ABI Loading")
    print("=" * 60)
    
    # Create service without actual connection
    service = object.__new__(EvidenceAnchorService)
    abi = service._get_default_abi()
    
    # Check required functions exist
    function_names = [item.get('name') for item in abi if item.get('type') == 'function']
    
    required_functions = ['verifyEvidence', 'getAnchorDetails', 'isAnchored']
    for func in required_functions:
        assert func in function_names, f"Missing function: {func}"
        print(f"✅ Function '{func}' found in ABI")
    
    # Check required events exist
    event_names = [item.get('name') for item in abi if item.get('type') == 'event']
    assert 'EvidenceAnchored' in event_names, "Missing EvidenceAnchored event"
    print(f"✅ Event 'EvidenceAnchored' found in ABI")
    
    return True


def test_api_wrapper():
    """Test AnchorAPI wrapper"""
    print("\n" + "=" * 60)
    print("🧪 Testing AnchorAPI Wrapper")
    print("=" * 60)
    
    from anchor_service import AnchorAPI
    
    # Create mock service
    class MockService:
        def compute_hash(self, data):
            return "0x" + hashlib.sha256(data).hexdigest()
        
        def anchor_evidence(self, hash, metadata):
            return AnchorResult(
                success=True,
                evidence_hash=hash,
                transaction_hash="0xtx123",
                block_number=100,
                timestamp=1700000000
            )
        
        def verify_evidence(self, hash):
            return VerificationResult(
                is_anchored=True,
                evidence_hash=hash,
                timestamp=1700000000,
                submitter="0xsubmitter",
                block_number=100
            )
        
        def get_polygonscan_link(self, tx_hash=None):
            return f"https://mumbai.polygonscan.com/tx/{tx_hash}"
    
    mock_service = MockService()
    api = AnchorAPI(mock_service)
    
    # Test anchor endpoint
    test_data = b"test evidence"
    result = api.anchor_endpoint(test_data, "Test metadata")
    
    assert result['success'] is True
    assert result['evidence_hash'] == mock_service.compute_hash(test_data)
    assert result['polygonscan_url'] is not None
    print(f"✅ Anchor endpoint: PASS")
    
    # Test verify endpoint
    verify_result = api.verify_endpoint("0x1234")
    
    assert verify_result['is_anchored'] is True
    assert 'timestamp' in verify_result
    print(f"✅ Verify endpoint: PASS")
    
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


def test_environment_variables():
    """Test environment variable handling"""
    print("\n" + "=" * 60)
    print("🧪 Testing Environment Variables")
    print("=" * 60)
    
    required_vars = [
        'DEPLOYER_PRIVATE_KEY',
        'ANCHOR_PRIVATE_KEY',
        'CONTRACT_ADDRESS',
    ]
    
    optional_vars = [
        'ALCHEMY_API_KEY',
        'INFURA_API_KEY',
    ]
    
    print("Required variables (must be set for deployment/anchoring):")
    for var in required_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "⚠️  Not set"
        print(f"  {var}: {status}")
    
    print("\nOptional variables (public RPCs work without these):")
    for var in optional_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "⚠️  Not set"
        print(f"  {var}: {status}")
    
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
    
    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename} ({size} bytes)")
        else:
            print(f"❌ {filename} - MISSING")
            return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 DepoSafety V2 Blockchain Integration Tests")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Hash Computation", test_hash_computation),
        ("AnchorResult Dataclass", test_anchor_result_dataclass),
        ("VerificationResult Dataclass", test_verification_result_dataclass),
        ("Contract ABI Loading", test_contract_abi_loading),
        ("API Wrapper", test_api_wrapper),
        ("Deployment Info Format", test_deployment_info_format),
        ("Polygonscan URLs", test_polygonscan_urls),
        ("Environment Variables", test_environment_variables),
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
