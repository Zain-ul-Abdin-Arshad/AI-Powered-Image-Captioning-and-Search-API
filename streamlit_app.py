import streamlit as st
import requests
import json
import io
from PIL import Image
import base64
import time
import os

API_BASE_URL = "http://localhost:8000"

def login_user(username, password):
    """Login user and return token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            return None
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None

def get_auth_headers():
    """Get authentication headers if token exists"""
    if "auth_token" in st.session_state:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}

def check_api_status():
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.set_page_config(
        page_title="AI Image Captioning & Search",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🖼️ AI-Powered Image Captioning & Search</h1>', unsafe_allow_html=True)
    
    if "auth_token" not in st.session_state:
        st.markdown('<h2 class="sub-header">🔐 Authentication Required</h2>', unsafe_allow_html=True)
        st.markdown("Please login to access the API features.")
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", value="admin")
        with col2:
            password = st.text_input("Password", type="password", value="admin123")
        
        if st.button("Login", type="primary"):
            token = login_user(username, password)
            if token:
                st.session_state.auth_token = token
                st.session_state.username = username
                st.success("Login successful! Please refresh the page.")
                st.rerun()
            else:
                st.error("Login failed. Please check your credentials.")
        
        st.markdown("""
        **Default credentials:**
        - Username: `admin`, Password: `admin123`
        - Username: `user`, Password: `user123`
        """)
        return
    
    with st.sidebar:
        st.markdown("##  Features")
        st.markdown("""
        -  **Upload Images**: Upload and get AI-generated captions
        -  **Search Images**: Find images using natural language
        -  **View History**: See all uploaded images
        -  **Interactive UI**: Beautiful and easy to use
        """)
        
        st.markdown("##  API Status")
        if check_api_status():
            st.success(" API Connected")
        else:
            st.error(" API Not Connected")
            st.info("Please start the API server first: `python src/main.py`")
            return
        
        st.markdown("##  User Info")
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            del st.session_state.auth_token
            del st.session_state.username
            st.rerun()
        
        with st.expander(" Debug Info"):
            st.write(f"**Current Directory:** {os.getcwd()}")
            st.write(f"**Data directory exists:** {os.path.exists('src/data/raw')}")
            if os.path.exists('src/data/raw'):
                files = os.listdir('src/data/raw')
                st.write(f"**Files in data/raw:** {files}")
    
    tab1, tab2, tab3 = st.tabs([" Upload Images", " Search Images", " Image History"])
    with tab1:
        upload_images_tab()
    
    with tab2:
        search_images_tab()
    
    with tab3:
        view_history_tab()

def upload_images_tab():
    st.markdown('<h2 class="sub-header"> Upload Images</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload images to get AI-generated captions. The system will automatically:
    - Generate descriptive captions
    - Store images for future search
    - Create embeddings for semantic search
    """)
    
    uploaded_files = st.file_uploader(
        label="",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Select one or more images to upload"
    )
    
    if uploaded_files:
        st.markdown("### Upload Progress")
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, use_column_width=True)
                    
                    with col2:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        headers = get_auth_headers()
                        response = requests.post(f"{API_BASE_URL}/upload/", files=files, headers=headers)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.markdown(f"""
                            <div class="success-box">
                                <h4>Upload Successful!</h4>
                                <p><strong>Filename:</strong> {data.get('filename', 'N/A')}</p>
                                <p><strong>Caption:</strong> {data.get('caption', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif response.status_code == 401:
                            st.error("Authentication failed. Please login again.")
                            del st.session_state.auth_token
                            st.rerun()
                        else:
                            st.markdown(f"""
                            <div class="error-box">
                                <h4>Upload Failed</h4>
                                <p>{response.text}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")

def search_images_tab():
    """Search images tab"""
    st.markdown('<h2 class="sub-header">Search Images</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Search through your uploaded images using natural language queries.
    The system uses semantic search to find the most relevant images.
    """)
    
    search_query = st.text_input(
        "Enter your search query",
        placeholder="e.g., red image, cat, landscape, etc.",
        help="Describe what you're looking for in the images"
    )
    
    if search_query:
        if st.button("Search Images", type="primary"):
            with st.spinner("Searching images..."):
                try:
                    headers = get_auth_headers()
                    response = requests.get(f"{API_BASE_URL}/search/?query={search_query}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        
                        if results:
                            st.markdown(f"### Search Results for '{search_query}'")
                            st.markdown(f"Found **{len(results)}** matching images")
                            
                            for i, result in enumerate(results, 1):
                                with st.expander(f"Result {i}: {result['filename']} (Similarity: {result['similarity']:.3f})"):
                                    st.markdown(f"""
                                    <div class="info-box">
                                        <p><strong>Filename:</strong> {result['filename']}</p>
                                        <p><strong>Caption:</strong> {result['caption']}</p>
                                        <p><strong>Similarity Score:</strong> {result['similarity']:.3f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    try:
                                        possible_paths = [
                                            f"src/data/raw/{result['filename']}",
                                            f"data/raw/{result['filename']}",
                                            f"../src/data/raw/{result['filename']}",
                                            os.path.join(os.getcwd(), "src", "data", "raw", result['filename'])
                                        ]                                        
                                        image = None
                                        used_path = None
                                        for path in possible_paths:
                                            try:
                                                if os.path.exists(path):
                                                    image = Image.open(path)
                                                    used_path = path
                                                    break
                                            except:
                                                continue                                        
                                        if image:
                                            max_width = 300
                                            max_height = 300
                                            width, height = image.size
                                            if width > height:
                                                new_width = max_width
                                                new_height = int(height * max_width / width)
                                            else:
                                                new_height = max_height
                                                new_width = int(width * max_height / height)
                                            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                            st.image(resized_image, caption=result['filename'], use_column_width=False)
                                        else:
                                            st.info(f"Image file not found. Tried paths: {', '.join(possible_paths)}")
                                    except Exception as e:
                                        st.info(f"Error loading image: {str(e)}")
                        else:
                            st.markdown("""
                            <div class="info-box">
                                <h4>🔍 No Results Found</h4>
                                <p>Try a different search query or upload more images.</p>
                            </div>
                            """, unsafe_allow_html=True)
                    elif response.status_code == 401:
                        st.error("Authentication failed. Please login again.")
                        del st.session_state.auth_token
                        st.rerun()
                    else:
                        st.error(f"Search failed: {response.text}")
                
                except Exception as e:
                    st.error(f"Error during search: {str(e)}")

def view_history_tab():
    st.markdown('<h2 class="sub-header">📋 Image History</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    View all images that have been uploaded to the system.
    This shows the complete history of your image uploads.
    """)
    
    if st.button("🔄 Refresh History", type="primary"):
        with st.spinner("Loading image history..."):
            try:
                headers = get_auth_headers()
                response = requests.get(f"{API_BASE_URL}/history/", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    images = data.get('images', [])
                    
                    if images:
                        st.markdown(f"### 📊 Image History ({len(images)} images)")
                        
                        cols = st.columns(3)
                        for i, image_data in enumerate(images):
                            col_idx = i % 3
                            with cols[col_idx]:
                                st.markdown(f"""
                                <div class="info-box">
                                    <p><strong>Filename:</strong> {image_data['filename']}</p>
                                    <p><strong>Caption:</strong> {image_data['caption']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                try:
                                    possible_paths = [
                                        f"src/data/raw/{image_data['filename']}",
                                        f"data/raw/{image_data['filename']}",
                                        f"../src/data/raw/{image_data['filename']}",
                                        os.path.join(os.getcwd(), "src", "data", "raw", image_data['filename'])
                                    ]
                                    
                                    image = None
                                    used_path = None
                                    
                                    for path in possible_paths:
                                        try:
                                            if os.path.exists(path):
                                                image = Image.open(path)
                                                used_path = path
                                                break
                                        except:
                                            continue
                                    
                                    if image:
                                        max_width = 250
                                        max_height = 250                                        
                                        width, height = image.size
                                        if width > height:
                                            new_width = max_width
                                            new_height = int(height * max_width / width)
                                        else:
                                            new_height = max_height
                                            new_width = int(width * max_height / height)
                                        
                                        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                        st.image(resized_image, caption=image_data['filename'], use_column_width=False)
                                    else:
                                        st.info(f"Image file not found. Tried paths: {', '.join(possible_paths)}")
                                except Exception as e:
                                    st.info(f"Error loading image: {str(e)}")
                    else:
                        st.markdown("""
                        <div class="info-box">
                            <h4>No Images Found</h4>
                            <p>No images have been uploaded yet. Try uploading some images first!</p>
                        </div>
                        """, unsafe_allow_html=True)
                elif response.status_code == 401:
                    st.error("Authentication failed. Please login again.")
                    del st.session_state.auth_token
                    st.rerun()
                else:
                    st.error(f"Failed to load history: {response.text}")
            
            except Exception as e:
                st.error(f"Error loading history: {str(e)}")

if __name__ == "__main__":
    main() 