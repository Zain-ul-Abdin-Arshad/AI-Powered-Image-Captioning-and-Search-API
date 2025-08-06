import subprocess
import sys
import os
import requests

def main():
    print("Starting Streamlit UI for AI Image Captioning & Search")
    print("=" * 60)
    
    try:
        import streamlit
        print("Streamlit is installed")
    except ImportError:
        print("Streamlit not found")
        print("Please install Streamlit:")
        print("   pip install streamlit")
        return
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("API server is running")
        else:
            print(" API server might not be running")
    except:
        print("API server is not running")
        print("Please start the API server first:")
        print("   python src/main.py")
        return
    
    print("\nStarting Streamlit app...")
    print("UI will be available at: http://localhost:8501")
    print("API is running at: http://localhost:8000")    
    print("\nFeatures:")
    print("- Upload images and get captions")
    print("- Search images with natural language")
    print("- View upload history")
    print("- Beautiful interactive interface")
    
    print("\nTo stop the app:")
    print("   Press Ctrl+C in this terminal")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\nStopping Streamlit app...")
        print("App stopped")

if __name__ == "__main__":
    main() 