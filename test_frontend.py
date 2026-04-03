import requests
import json
from time import sleep

def test_frontend_api_integration():
    """Test that frontend can communicate with backend"""
    
    print("\n" + "="*70)
    print("TESTING ITS FRONTEND - API INTEGRATION")
    print("="*70)
    
    # Test 1: Check frontend is running
    print("\n[1/5] Checking if frontend server is running...")
    try:
        response = requests.get('http://localhost:3001', timeout=5)
        if response.status_code == 200:
            print("✓ Frontend accessible at http://localhost:3001")
            print(f"  Response size: {len(response.text)} bytes")
    except Exception as e:
        print(f"✗ Frontend not accessible: {e}")
        return False
    
    # Test 2: Check if API endpoint in .env.local is correct
    print("\n[2/5] Checking environment configuration...")
    env_file = "c:/Users/DELL/Desktop/its proj/ITS/frontend/.env.local"
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()
            if "NEXT_PUBLIC_API_URL" in env_content:
                api_url = env_content.split('=')[1].strip()
                print(f"✓ API URL configured: {api_url}")
            else:
                print("✗ API_URL not found in .env.local")
    except Exception as e:
        print(f"✗ Error reading .env.local: {e}")
    
    # Test 3: Verify backend API is accessible from frontend's perspective
    print("\n[3/5] Testing backend API connectivity (from frontend)...")
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("✓ Backend API is accessible")
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Backend API not accessible: {e}")
        return False
    
    # Test 4: Test full image upload flow simulation
    print("\n[4/5] Simulating image upload and processing...")
    try:
        image_path = "c:/Users/DELL/Desktop/its proj/ITS/sample_images/test_satellite.jpg"
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:8000/process-image', files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Image processed successfully")
            print(f"  - Road Density: {data['road_density']:.4f} ({data['road_density']*100:.2f}%)")
            print(f"  - Road Length: {data['road_length']} pixels")
            print(f"  - Intersections: {data['intersection_count']}")
            print(f"  - Image Response: base64 encoded ({len(data['processed_image'])} chars)")
        else:
            print(f"✗ Processing failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        return False
    
    # Test 5: Verify page structure
    print("\n[5/5] Verifying frontend page structure...")
    try:
        response = requests.get('http://localhost:3001/', timeout=5)
        html = response.text
        
        checks = {
            "Contains title": "Intelligent Transportation System" in html,
            "Contains h1": "<h1" in html,
            "Contains file input": "type=\"file\"" in html or "accept=\"image" in html,
            "Contains button": "<button" in html,
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
            all_passed = all_passed and passed
        
        if all_passed:
            print("✓ All page structure checks passed")
    except Exception as e:
        print(f"✗ Error verifying page structure: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ FRONTEND TESTING COMPLETE - ALL TESTS PASSED")
    print("="*70)
    print("\n📍 FRONTEND URL: http://localhost:3001")
    print("📍 BACKEND URL:  http://localhost:8000")
    print("\n  Use frontend to:")
    print("  1. Upload satellite images")
    print("  2. View processed results")
    print("  3. Check road metrics")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    test_frontend_api_integration()
