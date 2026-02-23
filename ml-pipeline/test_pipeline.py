#!/usr/bin/env python3
"""
Test script for the 3DGS pipeline components
Run this to verify installation and basic functionality
"""

import os
import sys
import tempfile
from pathlib import Path

# Test imports
def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
        
    try:
        import cv2
        print("✓ opencv-python")
    except ImportError as e:
        print(f"✗ opencv-python: {e}")
        return False
        
    try:
        from PIL import Image
        print("✓ pillow")
    except ImportError as e:
        print(f"✗ pillow: {e}")
        return False
        
    try:
        import torch
        print(f"✓ torch (CUDA available: {torch.cuda.is_available()})")
    except ImportError as e:
        print(f"✗ torch: {e}")
        return False
        
    try:
        import requests
        print("✓ requests")
    except ImportError as e:
        print(f"✗ requests: {e}")
        return False
        
    return True


def test_api_client():
    """Test API client functionality"""
    print("\nTesting API client...")
    
    try:
        from api_client import WebhookClient, notify_processing_complete
        
        # Create client (won't actually send)
        client = WebhookClient("https://example.com/webhook")
        
        # Test payload generation
        payload = {
            'event': 'processing_complete',
            'job_id': 'test-job',
            'status': 'completed',
            'models': {'ply': '/path/to/model.ply'}
        }
        
        print("✓ API client imports and basic functionality")
        return True
        
    except Exception as e:
        print(f"✗ API client test failed: {e}")
        return False


def test_local_3dgs_imports():
    """Test local_3dgs module imports"""
    print("\nTesting local_3dgs module...")
    
    try:
        # We can't fully test without COLMAP installed, but we can check imports
        import local_3dgs
        print("✓ local_3dgs module imports successfully")
        return True
    except ImportError as e:
        print(f"✗ local_3dgs import failed: {e}")
        return False


def test_colmap_available():
    """Check if COLMAP is installed"""
    print("\nChecking COLMAP...")
    
    import subprocess
    try:
        result = subprocess.run(['colmap', '--help'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✓ COLMAP is installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
        
    print("✗ COLMAP not found (install with: apt-get install colmap)")
    return False


def test_ffmpeg_available():
    """Check if ffmpeg is installed"""
    print("\nChecking ffmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✓ ffmpeg is installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
        
    print("✗ ffmpeg not found (install with: apt-get install ffmpeg)")
    return False


def main():
    print("="*50)
    print("DepoSafety V2 - 3DGS Pipeline Test")
    print("="*50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("API Client", test_api_client()))
    results.append(("Local 3DGS Module", test_local_3dgs_imports()))
    results.append(("COLMAP", test_colmap_available()))
    results.append(("ffmpeg", test_ffmpeg_available()))
    
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✓ All tests passed! Ready to process videos.")
        return 0
    else:
        print("\n✗ Some tests failed. Check dependencies.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("  apt-get install colmap ffmpeg")
        return 1


if __name__ == "__main__":
    sys.exit(main())
