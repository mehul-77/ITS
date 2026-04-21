import requests
import json
from PIL import Image, ImageDraw
import numpy as np

# Create a synthetic satellite image for testing
def create_test_satellite_image():
    """Create a simple synthetic satellite image with road-like patterns"""
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some "roads" as dark lines
    road_color = (50, 50, 50)
    
    # Main highway diagonally
    draw.line([(50, 100), (450, 400)], fill=road_color, width=15)
    
    # Vertical road
    draw.line([(200, 50), (200, 450)], fill=road_color, width=12)
    
    # Horizontal road
    draw.line([(50, 250), (450, 250)], fill=road_color, width=12)
    
    # Some intersections and junctions
    draw.line([(150, 200), (300, 280)], fill=road_color, width=10)
    draw.line([(300, 150), (350, 300)], fill=road_color, width=8)
    
    # Add some "buildings" (noise)
    for i in range(0, 500, 80):
        for j in range(0, 500, 80):
            draw.rectangle(
                [i + 10, j + 10, i + 40, j + 40],
                fill=(100, 100, 100)
            )
    
    # Save the image
    img.save('sample_images/test_satellite.jpg')
    print("✓ Test satellite image created: sample_images/test_satellite.jpg")
    return img


def test_api():
    """Test the backend API"""
    api_url = "http://localhost:8000/process-image"
    image_path = "sample_images/test_satellite.jpg"
    
    # Create test image
    create_test_satellite_image()
    
    print("\n" + "="*60)
    print("TESTING ITS BACKEND API")
    print("="*60)
    
    # Send request
    print(f"\n1. Uploading image to: {api_url}\n")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(api_url, files=files)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ SUCCESS! API Response:")
            print("-" * 60)
            print(f"Road Density:      {data['road_density']:.6f} ({data['road_density']*100:.3f}%)")
            print(f"Road Length:       {data['road_length']} pixels")
            print(f"Intersection Count: {data['intersection_count']}")
            print("-" * 60)
            
            # Save processed image
            if 'processed_image' in data:
                processed_img_base64 = data['processed_image']
                print(f"\nProcessed Image: base64 encoded ({len(processed_img_base64)} chars)")
                
                # Decode and save
                import base64
                img_data = base64.b64decode(processed_img_base64.split(',')[1])
                with open('sample_images/processed_result.png', 'wb') as f:
                    f.write(img_data)
                print("✓ Saved processed image to: sample_images/processed_result.png")
            
            print("\n" + "="*60)
            print("TEST RESULTS")
            print("="*60)
            print(f"✓ Backend is working correctly!")
            print(f"✓ Image processing pipeline executed successfully")
            print(f"✓ All metrics calculated")
            print("="*60 + "\n")
            
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"✗ Failed to connect to API: {e}")
        print("\nMake sure the backend is running:")
        print("  cd backend && python main.py")


if __name__ == "__main__":
    test_api()
