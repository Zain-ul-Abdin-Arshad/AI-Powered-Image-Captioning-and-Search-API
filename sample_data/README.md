# Sample Data for Demo

This directory contains sample images for demonstrating the AI-Powered Image Captioning and Search API.

## Sample Images Included

The following sample images are provided for testing:
1. **demo_cat.jpg** - A cat image for testing animal detection
2. **demo_landscape.jpg** - A landscape image for testing scene recognition
3. **demo_food.jpg** - A food image for testing object recognition

## How to Use Sample Data

### For Streamlit Demo
1. Start the Streamlit app: `streamlit run streamlit_app.py`
2. Go to the "Upload Images" tab
3. Upload the sample images from this directory
4. Try searching with queries like "cat", "landscape", "food"

## Expected Captions

- **demo_cat.jpg**: "a  grey cat"
- **demo_landscape.jpg**: "a beautiful mountain landscape with trees"
- **demo_food.jpg**: "a delicious pizza"

## Creating Your Own Sample Data

To create your own sample dataset:

1. **Collect diverse images** covering different categories:
   - Animals (cats, dogs, birds)
   - Landscapes (mountains, beaches, cities)
   - Objects (cars, buildings, food)
   - People (portraits, activities)

2. **Use appropriate formats**:
   - JPEG (.jpg, .jpeg) - for photographs
   - PNG (.png) - for images with transparency

3. **Optimize file sizes**:
   - Keep images under 5MB for faster processing
   - Resize large images to reasonable dimensions (e.g., 1920x1080)

4. **Test with various queries**:
   - Object names: "cat", "car", "building"
   - Colors: "red", "blue", "green"
   - Actions: "running", "sitting", "standing"
   - Emotions: "happy", "sad", "excited"

## Demo Script

Run the demo script to automatically upload sample images:

```bash
python tests/start_demo.py
```

This will:
1. Start the API server
2. Upload sample images
3. Demonstrate search functionality
4. Show the Streamlit interface 