# AI-Powered Image Captioning and Search API

A FastAPI-based application that allows users to upload images, automatically generates captions using AI, and enables semantic search through natural language queries.

## Features

- **Image Upload**: Upload JPEG/PNG images with automatic caption generation
- **AI Captioning**: Uses BLIP model to generate descriptive captions
- **Semantic Search**: Search images using natural language queries with CLIP embeddings
- **History**: View all uploaded images and their captions
- **Live Demo**: Ready for Ngrok deployment

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **ML Models**: Hugging Face Transformers (BLIP, CLIP)
- **Database**: SQLite
- **Image Processing**: PIL (Pillow)
- **Live Demo**: Ngrok

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Build and run with Docker
docker build -t image-captioning-api .
docker run -p 8000:8000 image-captioning-api

# Access the API at http://localhost:8000
# View docs at http://localhost:8000/docs
```

### Option 2: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the API
python src/main.py

# Start Streamlit UI (optional)
python run_streamlit.py
```

### Option 3: Live Demo with Ngrok
```bash
# Start with Ngrok for live demo
python run_with_ngrok.py
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AI-Powered-Image-Captioning-and-Search-API
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create data directories**
   ```bash
   mkdir -p data/raw data/processed
   ```

5. **Run the application**
   ```bash
   cd src
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Welcome Message
- **GET** `/`
- **Description**: Welcome message
- **Response**:
  ```json
  {
    "message": "Welcome to the AI-Powered Image Captioning and Search API!"
  }
  ```

#### 2. Upload Image
- **POST** `/upload/`
- **Description**: Upload an image and generate caption
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file`: Image file (JPEG/PNG)
- **Response**:
  ```json
  {
    "message": "Image uploaded successfully",
    "filename": "example.jpg",
    "caption": "a cat sitting on a windowsill"
  }
  ```

#### 3. Search Images
- **GET** `/search/`
- **Description**: Search images using natural language query
- **Parameters**:
  - `query`: Text query (string)
- **Response**:
  ```json
  {
    "query": "cat",
    "results": [
      {
        "filename": "cat.jpg",
        "caption": "a cat sitting on a windowsill",
        "similarity": 0.85
      }
    ]
  }
  ```

#### 4. Get History
- **GET** `/history/`
- **Description**: Get all uploaded images and captions
- **Authentication**: Required (Bearer token)
- **Response**:
  ```json
  {
    "images": [
      {
        "filename": "cat.jpg",
        "caption": "a cat sitting on a windowsill"
      }
    ]
  }
  ```

#### 5. Authentication Endpoints

##### Login
- **POST** `/token`
- **Description**: Get JWT access token
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**:
  - `username`: Username
  - `password`: Password
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

##### Get User Info
- **GET** `/users/me`
- **Description**: Get current user information
- **Authentication**: Required (Bearer token)
- **Response**:
  ```json
  {
    "username": "admin",
    "full_name": "Administrator",
    "email": "admin@example.com"
  }
  ```

## Live Demo with Ngrok

### Setup Ngrok

1. **Install Ngrok**
   - Download from [ngrok.com](https://ngrok.com)
   - Or install via package manager:
     ```bash
     # Windows (with chocolatey)
     choco install ngrok
     
     # macOS (with homebrew)
     brew install ngrok
     ```

2. **Start the API**
   ```bash
   cd src
   python main.py
   ```

3. **Expose with Ngrok**
   ```bash
   ngrok http 8000
   ```

4. **Access your live demo**
   - Ngrok will provide a public URL (e.g., `https://abc123.ngrok.io`)
   - Share this URL for your live demo
   - API documentation will be available at `https://abc123.ngrok.io/docs`

### Example API Calls

#### Authentication
```bash
# Get JWT token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

#### Upload an Image (with authentication)
```bash
# First get token
TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Upload with token
curl -X POST "http://localhost:8000/upload/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

#### Search Images (with authentication)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/search/?query=cat"
```

#### Get History (with authentication)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/history/"
```

## Testing

### Manual Testing
1. Start the server: `python src/main.py`
2. Open browser to `http://localhost:8000/docs`
3. Use the interactive Swagger UI to test endpoints
4. Upload test images and try search queries

### Automated Testing
```bash
# Run all tests
python tests/run_all_tests.py

# Run individual test suites
python tests/run_all_tests.py      # Run all tests
python -m pytest tests/test_pytest.py -v  # Comprehensive pytest tests
python tests/run_all_tests.py      # Run all tests
python run_with_ngrok.py           # Demo with Ngrok integration
```

## Project Structure

```
AI-Powered-Image-Captioning-and-Search-API/
├── src/
│   ├── main.py              # FastAPI application
│   ├── auth.py              # JWT authentication
│   ├── utils/
│   │   └── database.py      # Database utilities
│   ├── images.db            # SQLite database
│   └── data/
│       └── raw/             # User uploaded images
├── streamlit_app.py         # Web interface
├── run_streamlit.py         # Streamlit launcher
├── run_with_ngrok.py        # Ngrok integration
├── tests/
│   ├── test_pytest.py       # Comprehensive test suite
│   ├── run_all_tests.py     # Test runner
│   └── README.md            # Test documentation
├── sample_data/             # Demo images
├── requirements.txt          # Dependencies
├── Dockerfile               # Container configuration
├── env.example              # Environment variables
├── .gitignore               # Git ignore rules
└── README.md                # Project documentation
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid Bearer token.

### Default Users

For testing purposes, the following users are available:

- **Username**: `admin`, **Password**: `admin123`
- **Username**: `user`, **Password**: `user123`

### Authentication Flow

1. **Get Token**: POST `/token` with username and password
2. **Use Token**: Include `Authorization: Bearer <token>` header in requests
3. **Token Expiry**: Tokens expire after 1 hour (configurable)

### Testing Authentication

```bash
# Test authentication
python -m pytest tests/test_pytest.py::TestAuthentication -v
```

## ML Models Used

- **BLIP (Salesforce/blip-image-captioning-base)**: Generates natural language captions
- **CLIP (openai/clip-vit-base-patch32)**: Creates embeddings for semantic search

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- Model loading errors
- Database connection issues
- Image processing errors

## Performance Notes

- First request may be slower due to model loading
- Large images are automatically resized for processing
- Embeddings are cached in the database for faster search

## Troubleshooting

### Common Issues

1. **Model Download Issues**
   - Ensure stable internet connection
   - Check Hugging Face access

2. **Memory Issues**
   - Close other applications
   - Consider using smaller models

3. **Port Already in Use**
   - Change port in `main.py`
   - Or kill existing process: `lsof -ti:8000 | xargs kill`

## ✅ Completed Features

- [x] **Core API** - FastAPI with image upload, captioning, and search
- [x] **ML Integration** - BLIP for captioning, CLIP for embeddings
- [x] **Database** - SQLite with proper schema
- [x] **Live Demo** - Ngrok integration ready
- [x] **Swagger Docs** - Auto-generated OpenAPI documentation
- [x] **Streamlit UI** - Beautiful web interface
- [x] **Docker Support** - Containerized deployment
- [x] **Unit Tests** - Comprehensive pytest test suite
- [x] **Environment Config** - .env.example with all settings
- [x] **Sample Data** - Demo images and instructions
- [x] **Error Handling** - Comprehensive error management
- [x] **Image Processing** - Automatic resizing and optimization
- [x] **JWT Authentication** - Secure API with token-based authentication

## Future Enhancements

- [ ] Reverse image search functionality
- [ ] Advanced caching mechanisms
- [ ] Multi-language support
- [ ] Batch upload processing
- [ ] Image preprocessing pipeline
- [ ] User management system
- [ ] Role-based access control

## License

This project is for assessment purposes.
