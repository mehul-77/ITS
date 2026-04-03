import requests
import json

# Test the direct endpoint
image_path = "c:/Users/DELL/Desktop/its proj/ITS/sample_images/test_satellite.jpg"

print("Testing endpoint: http://localhost:8000/process-image")
print("-" * 60)

try:
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8000/process-image', files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body (first 500 chars):")
    print(response.text[:500])
    
except Exception as e:
    print(f"Error: {e}")
