import subprocess
import sys
import time
import os
import requests
import json
import re

def check_ngrok():
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("Ngrok is installed")
            return True
        else:
            print("Ngrok not found")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Ngrok not found or not responding")
        print("Please install Ngrok:")
        return False

def start_server():
    print("Starting API server...")
    
    try:
        os.chdir('src')
        process = subprocess.Popen([sys.executable, 'main.py'])
        print("Server started successfully!")
        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def wait_for_server():
    print("Waiting for server to be ready...")
    
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    print("Server failed to start within 30 seconds")
    return False

def start_ngrok():
    print("Starting Ngrok...")
    try:
        ngrok_process = subprocess.Popen(['ngrok', 'http', '8000'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True)
        time.sleep(3)
        
        # Try multiple times to get the URL
        for attempt in range(5):
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels and len(tunnels) > 0:
                        public_url = tunnels[0]['public_url']
                        print(f" Ngrok started successfully!")
                        print(f" Public URL: {public_url}")
                        print(f" API Docs: {public_url}/docs")
                        return ngrok_process, public_url
            except:
                pass
            time.sleep(2)
        
        print("   Ngrok started but couldn't get URL automatically")
        print("   Check Ngrok dashboard at: http://localhost:4040")
        
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'tunnels' in data and len(data['tunnels']) > 0:
                    public_url = data['tunnels'][0]['public_url']
                    print(f" Found URL: {public_url}")
                    return ngrok_process, public_url
        except:
            pass
        
        return ngrok_process, None
        
    except Exception as e:
        print(f" Failed to start Ngrok: {e}")
        return None, None

def test_ngrok_endpoints(public_url):
    """Test Ngrok endpoints with proper authentication"""
    print("\n" + "=" * 70)
    print(" TESTING NGROK ENDPOINTS WITH AUTHENTICATION")
    print("=" * 70)
    
    print("\n1. Testing root endpoint (no auth required)...")
    try:
        response = requests.get(f"{public_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Getting authentication token...")
    try:
        token_data = {
            "username": "admin",
            "password": "admin123"
        }
        print(f"   Sending request to: {public_url}/token")
        response = requests.post(f"{public_url}/token", data=token_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get("access_token")
            print(f"   Token received: {access_token[:20]}...")
            print(f"   Full token: {access_token}")
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print("\n3. Testing /users/me endpoint...")
            print(f"   Sending request to: {public_url}/users/me")
            print(f"   Headers: {headers}")
            response = requests.get(f"{public_url}/users/me", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            if response.status_code == 200:
                print(f"   User info: {response.json()}")
            else:
                print(f"   Error: {response.text}")
            
            print("\n4. Testing /history/ endpoint...")
            response = requests.get(f"{public_url}/history/", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                history = response.json()
                print(f"   History items: {len(history.get('images', []))}")
            else:
                print(f"   Error: {response.text}")
            
            print("\n5. Testing /search/ endpoint...")
            response = requests.get(f"{public_url}/search/?query=test", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                search_results = response.json()
                print(f"   Search results: {len(search_results.get('results', []))}")
            else:
                print(f"   Error: {response.text}")
            
            print("\n6. Testing /test-auth endpoint...")
            response = requests.get(f"{public_url}/test-auth", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Auth test: {response.json()}")
            else:
                print(f"   Error: {response.text}")
            
            print("\n" + "=" * 70)
            print(" AUTHENTICATION TESTING COMPLETE!")
            print("=" * 70)
            print("\n Manual Testing Instructions:")
            print("1. Use the token above for testing protected endpoints")
            print("2. Include 'Authorization: Bearer <token>' in headers")
            print("3. Test endpoints using curl, Postman, or browser")
            print("\n Example curl commands:")
            print(f"   curl -H 'Authorization: Bearer {access_token}' {public_url}/users/me")
            print(f"   curl -H 'Authorization: Bearer {access_token}' {public_url}/history/")
            print(f"   curl -H 'Authorization: Bearer {access_token}' '{public_url}/search/?query=test'")
            
        else:
            print(f"   Error getting token: {response.text}")
            print("\n Troubleshooting:")
            print("1. Check if the server is running properly")
            print("2. Verify the Ngrok URL is correct")
            print("3. Try accessing the root endpoint first")
            
    except Exception as e:
        print(f"   Error: {e}")
        print("\n Troubleshooting:")
        print("1. Check if Ngrok is working properly")
        print("2. Verify the public URL is accessible")
        print("3. Try accessing the root endpoint manually")

def main():
    print(" AI-Powered Image Captioning and Search API with Ngrok")
    print("=" * 70)
    if not check_ngrok():
        print("\n Please install Ngrok first, then run this script again.")
        return
    server_process = start_server()
    if not server_process:
        return
    if not wait_for_server():
        server_process.terminate()
        return
    
    print("\n Server is running at: http://localhost:8000")
    print(" API Documentation: http://localhost:8000/docs")
    
    ngrok_process, public_url = start_ngrok()
    
    if public_url:
        print("\n SUCCESS! Your API is now publicly accessible!")
        print("=" * 70)
        print(f" Public URL: {public_url}")
        print(f" API Documentation: {public_url}/docs")
        print(f" Interactive Testing: {public_url}/docs")
        
        test_ngrok_endpoints(public_url)
        
        print("\n Demo Instructions:")
        print("1. Share the public URL with your interviewer")
        print("2. Use the API docs to demonstrate all endpoints")
        print("3. Upload images and test search functionality")
        print("4. Show the history of uploaded images")
        
        print("\n Swagger UI Testing Instructions:")
        print("1. Open the Swagger UI: " + public_url + "/docs")
        print("2. Get authentication token:")
        print("   - Go to POST /token endpoint")
        print("   - Enter username: admin, password: admin123")
        print("   - Copy the access_token from response")
        print("3. Authorize Swagger UI:")
        print("   - Click 'Authorize' button at top")
        print("   - Enter: Bearer YOUR_TOKEN")
        print("   - Click 'Authorize' and close popup")
        print("4. Test protected endpoints:")
        print("   - /users/me - Get user info")
        print("   - /upload/ - Upload images")
        print("   - /search/ - Search images")
        print("   - /history/ - View all images")
        print("   - /test-auth - Test authentication")
        
        print("\n Available Endpoints:")
        print(f"   GET  {public_url}/                    - Welcome message")
        print(f"   POST {public_url}/token               - Get authentication token")
        print(f"   GET  {public_url}/test-auth           - Test authentication")
        print(f"   GET  {public_url}/users/me            - Get user info")
        print(f"   POST {public_url}/upload/             - Upload image")
        print(f"   GET  {public_url}/search/?query=test  - Search images")
        print(f"   GET  {public_url}/history/            - View all images")
    else:
        print("\n Ngrok started but URL not detected automatically.")
        print("=" * 70)
        print(" Manual Testing Instructions:")
        print("1. Open http://localhost:4040 in your browser")
        print("2. Copy the Ngrok URL (e.g., https://abc123.ngrok.io)")
        print("3. Test the endpoints manually:")
        print("\n Step 1: Get authentication token")
        print("   curl -X POST 'YOUR_NGROK_URL/token' \\")
        print("     -H 'Content-Type: application/x-www-form-urlencoded' \\")
        print("     -d 'username=admin&password=admin123'")
        print("\n Step 2: Use the token for protected endpoints")
        print("   curl -H 'Authorization: Bearer YOUR_TOKEN' YOUR_NGROK_URL/users/me")
        print("   curl -H 'Authorization: Bearer YOUR_TOKEN' YOUR_NGROK_URL/history/")
        print("   curl -H 'Authorization: Bearer YOUR_TOKEN' 'YOUR_NGROK_URL/search/?query=test'")
        
        try:
            manual_url = input("\n Enter your Ngrok URL manually (or press Enter to skip): ").strip()
            if manual_url:
                if not manual_url.startswith('http'):
                    manual_url = 'https://' + manual_url
                print(f"\n Testing with manual URL: {manual_url}")
                test_ngrok_endpoints(manual_url)
        except KeyboardInterrupt:
            print("\n Skipping manual testing...")
    
    print("\n To stop everything:")
    print("   Press Ctrl+C in this terminal")
    
    try:
        if ngrok_process:
            ngrok_process.wait()
        else:
            server_process.wait()
    except KeyboardInterrupt:
        print("\n Stopping services...")
        if ngrok_process:
            ngrok_process.terminate()
        server_process.terminate()
        print(" All services stopped")

if __name__ == "__main__":
    main() 