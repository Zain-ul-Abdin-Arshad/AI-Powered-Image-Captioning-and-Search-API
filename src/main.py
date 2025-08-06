from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from utils.database import initialize_db, connection
from auth import authenticate_user, create_access_token, get_current_user, User
from PIL import Image
import io
import numpy as np
import os
import hashlib

USE_ML_MODELS = True

if USE_ML_MODELS:
    from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPProcessor, CLIPModel
    import torch

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  
        "http://localhost:8501",
        "https://localhost:8501",
        "http://127.0.0.1:8501", 
        "https://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

initialize_db()

blip_processor = None
blip_model = None
clip_processor = None
clip_model = None
models_loaded = False

def load_models():
    global blip_processor, blip_model, clip_processor, clip_model, models_loaded    
    if not USE_ML_MODELS:
        return True    
    if models_loaded:
        return True
    try:
        print("Loading BLIP model...")
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        print("Loading CLIP model...")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        
        models_loaded = True
        print("All models loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def generate_caption(image):
    if USE_ML_MODELS:
        try:
            if not load_models():
                return "Error: Models not loaded"
            
            inputs = blip_processor(image, return_tensors="pt")
            out = blip_model.generate(**inputs, max_length=50, num_beams=5)
            caption = blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            return f"Error generating caption: {str(e)}"
    else:
        width, height = image.size
        return f"An image with dimensions {width}x{height} pixels"

def generate_embedding(image):
    if USE_ML_MODELS:
        try:
            if not load_models():
                return b""            
            inputs = clip_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                image_features = clip_model.get_image_features(**inputs)
            embedding = image_features.cpu().numpy().tobytes()
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return b""
    else:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()
        hash_obj = hashlib.md5(img_data)
        return hash_obj.digest()

def insert_image(filename, caption, embedding):
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO images (filename, caption, embedding)
            VALUES (?, ?, ?)
        """, (filename, caption, embedding))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def fetch_images():
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM images")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Database error: {e}")
        return []

@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Powered Image Captioning and Search API!"}

@app.get("/test-auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    return {"message": "Authentication successful", "user": current_user.username}

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email
    }

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:
        if not file.content_type.startswith('image/'):
            return {"error": "File must be an image"}
        
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        caption = generate_caption(image)
        embedding = generate_embedding(image)
        
        os.makedirs("data/raw", exist_ok=True)
        
        file_location = f"data/raw/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(image_data)
        
        if insert_image(file.filename, caption, embedding):
            return {
                "message": "Image uploaded successfully",
                "filename": file.filename,
                "caption": caption
            }
        else:
            return {"error": "Failed to save to database"}
            
    except Exception as e:
        print(f"Upload error: {e}")
        return {"error": str(e)}

@app.get("/search/")
async def search_images(query: str, current_user: User = Depends(get_current_user)):
    try:
        print(f"Search request received for query: '{query}'")
        
        images = fetch_images()
        print(f"Found {len(images)} images in database")
        
        if not images:
            print("No images found in database")
            return {"query": query, "results": []}
        
        if USE_ML_MODELS:
            print("Using ML models for search")
            if not load_models():
                print("Models not loaded, returning error")
                return JSONResponse(status_code=500, content={"error": "Models not loaded"})
            
            query_inputs = clip_processor(text=[query], return_tensors="pt", padding=True)
            with torch.no_grad():
                query_features = clip_model.get_text_features(**query_inputs)
            query_embedding = query_features.cpu().numpy()
            
            similarities = []
            for row in images:
                try:
                    stored_embedding = np.frombuffer(row["embedding"], dtype=np.float32).reshape(1, -1)
                    similarity = np.dot(query_embedding, stored_embedding.T) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                    )
                    similarities.append((similarity[0][0], row))
                except Exception as e:
                    print(f"Error processing image {row['filename']}: {e}")
                    continue
        else:
            print("Using simple text-based search")
            similarities = []
            query_lower = query.lower()
            for row in images:
                try:
                    caption_lower = row["caption"].lower()
                    if query_lower in caption_lower:
                        similarity = 0.8
                    else:
                        similarity = 0.1
                    similarities.append((similarity, row))
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
                    continue
        
        print(f"Processed {len(similarities)} similarities")
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        results = [
            {
                "filename": row["filename"], 
                "caption": row["caption"],
                "similarity": float(sim)
            } 
            for sim, row in similarities[:3]
        ]
        
        print(f"Returning {len(results)} results")
        return {"query": query, "results": results}
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/history/")
async def get_history(current_user: User = Depends(get_current_user)):
    try:
        images = fetch_images()
        return {"images": [{"filename": row["filename"], "caption": row["caption"]} for row in images]}
    except Exception as e:
        print(f"History error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    print("Starting AI-Powered Image Captioning and Search API...")
    if USE_ML_MODELS:
        print("Loading models (this may take a few minutes on first run)...")
    else:
        print("Running in test mode with simplified captioning and search...")
    run(app, host="0.0.0.0", port=8000)

