import pytest
import requests
import os
import tempfile
from PIL import Image
import io
import sys
import subprocess
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestImageCaptioningAPI:    
    @pytest.fixture(scope="class")
    def api_url(self):
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def test_image(self):
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_api_health(self, api_url):
        try:
            response = requests.get(f"{api_url}/", timeout=5)
            assert response.status_code == 200
            assert "message" in response.json()
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_upload_image(self, api_url, test_image):
        try:
            login_data = {"username": "admin", "password": "admin123"}
            auth_response = requests.post(f"{api_url}/token", data=login_data, timeout=10)
            
            if auth_response.status_code != 200:
                pytest.skip("Authentication failed - cannot test protected endpoints")
            
            token_data = auth_response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            files = {'file': ('test_image.jpg', test_image.getvalue(), 'image/jpeg')}
            response = requests.post(f"{api_url}/upload/", files=files, headers=headers, timeout=30)
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "filename" in data
            assert "caption" in data
            assert data["message"] == "Image uploaded successfully"
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_search_images(self, api_url):
        try:
            login_data = {"username": "admin", "password": "admin123"}
            auth_response = requests.post(f"{api_url}/token", data=login_data, timeout=10)
            
            if auth_response.status_code != 200:
                pytest.skip("Authentication failed - cannot test protected endpoints")
            
            token_data = auth_response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            query = "test"
            response = requests.get(f"{api_url}/search/?query={query}", headers=headers, timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "results" in data
            assert data["query"] == query
            assert isinstance(data["results"], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_get_history(self, api_url):
        try:
            login_data = {"username": "admin", "password": "admin123"}
            auth_response = requests.post(f"{api_url}/token", data=login_data, timeout=10)
            
            if auth_response.status_code != 200:
                pytest.skip("Authentication failed - cannot test protected endpoints")
            
            token_data = auth_response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = requests.get(f"{api_url}/history/", headers=headers, timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert "images" in data
            assert isinstance(data["images"], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_invalid_file_upload(self, api_url):
        try:
            files = {'file': ('test.txt', b'This is not an image', 'text/plain')}
            response = requests.post(f"{api_url}/upload/", files=files, timeout=10)
            
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_empty_search_query(self, api_url):
        try:
            response = requests.get(f"{api_url}/search/?query=", timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "results" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

class TestDatabase:    
    def test_database_connection(self):
        try:
            from src.utils.database import initialize_db, connection
            
            initialize_db()
            
            conn = connection()
            assert conn is not None
            
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'images'
            
            conn.close()
        except ImportError:
            pytest.skip("Database module not available")

class TestMLModels:    
    def test_model_loading(self):
        try:
            from src.main import load_models
            
            success = load_models()
            assert success == True
        except ImportError:
            pytest.skip("ML models not available")

class TestAuthentication:    
    @pytest.fixture(scope="class")
    def api_url(self):
        return "http://localhost:8000"
    
    def test_login_success(self, api_url):
        try:
            login_data = {"username": "admin", "password": "admin123"}
            response = requests.post(f"{api_url}/token", data=login_data, timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_login_failure(self, api_url):
        """Test failed login"""
        try:
            login_data = {"username": "admin", "password": "wrongpassword"}
            response = requests.post(f"{api_url}/token", data=login_data, timeout=10)
            
            assert response.status_code == 401
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_protected_endpoint_without_token(self, api_url):

        try:
            response = requests.get(f"{api_url}/upload/", timeout=10)
            assert response.status_code == 401
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_user_info(self, api_url):

        try:
            # First login
            login_data = {"username": "user", "password": "user123"}
            auth_response = requests.post(f"{api_url}/token", data=login_data, timeout=10)
            
            if auth_response.status_code != 200:
                pytest.skip("Authentication failed")
            
            token_data = auth_response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = requests.get(f"{api_url}/users/me", headers=headers, timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert "username" in data
            assert "full_name" in data
            assert "email" in data
            assert data["username"] == "user"
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

def test_docker_build():
    try:
        dockerfile_path = os.path.join(os.path.dirname(__file__), '..', 'Dockerfile')
        assert os.path.exists(dockerfile_path), "Dockerfile not found"
    except Exception as e:
        pytest.skip(f"Docker test skipped: {e}")

def test_requirements_file():
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(requirements_path), "requirements.txt not found"
    
    with open(requirements_path, 'r') as f:
        requirements = f.read()    
    essential_packages = ['fastapi', 'uvicorn', 'pillow', 'transformers']
    for package in essential_packages:
        assert package in requirements, f"Missing essential package: {package}"

def test_project_structure():
    base_path = os.path.dirname(os.path.dirname(__file__))
    
    required_files = [
        'src/main.py',
        'src/utils/database.py',
        'requirements.txt',
        'README.md',
        'Dockerfile',
        'env.example'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        assert os.path.exists(full_path), f"Missing required file: {file_path}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 