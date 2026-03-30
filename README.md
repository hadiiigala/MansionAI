# 🏠 Interior Design Generator

A web-based application that generates stunning interior design images using Stable Diffusion AI. Users can input their preferences through positive and negative prompts to create custom interior design visualizations.

## ✨ Features

- **User Registration**: Collect user information (name, email, registration ID)
- **Dual Prompt System**: 
  - Positive prompt: Describe what you want in your design
  - Negative prompt: Specify what to avoid in the generated image
- **AI-Powered Generation**: Uses Stable Diffusion v1.5 for high-quality interior design images
- **Modern UI/UX**: Beautiful, responsive interface with smooth animations
- **Image Download**: Save generated designs to your device
- **Real-time Generation**: Watch as AI creates your custom interior design

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework for API
- **Stable Diffusion**: AI model for image generation
- **PyTorch**: Deep learning framework
- **Diffusers**: Hugging Face library for diffusion models

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with modern design
- **JavaScript**: Client-side logic and API communication

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (Python 3.10+ recommended)
- **pip** (Python package manager)
- **CUDA-capable GPU** (optional but recommended for faster generation)
- **Git** (for cloning repositories)

### System Requirements

- **Minimum RAM**: 8GB (16GB+ recommended)
- **GPU**: NVIDIA GPU with CUDA support (optional, CPU mode available)
- **Storage**: At least 10GB free space (for model downloads)

## 🚀 Installation

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: The first time you run the application, it will download the Stable Diffusion model (~4GB). Ensure you have a stable internet connection.

### Step 2: Verify Installation

Check if all dependencies are installed correctly:

```bash
python -c "import torch, flask, diffusers; print('All dependencies installed!')"
```

## 🏃 Running the Application

### Start the Backend Server

1. Navigate to the backend directory:
```bash
cd backend
```

2. Run the Flask server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

You should see:
```
Starting Flask server...
 * Running on http://0.0.0.0:5000
```

**Note**: On first run, the model loading may take 2-5 minutes. You'll see:
```
Loading Stable Diffusion model...
Using device: cuda  (or cpu)
Model loaded successfully!
```

### Start the Frontend

#### Option 1: Direct File Opening
Simply open `frontend/index.html` in your web browser.

#### Option 2: Using a Local Server (Recommended)

**Python 3:**
```bash
cd frontend
python -m http.server 8000
```
Then open `http://localhost:8000` in your browser.

## 📁 Project Structure

```
ipd_with_ide/
├── backend/
│   ├── app.py                 # Flask server and API endpoints
│   ├── model_handler.py       # Stable Diffusion model wrapper
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── styles.css             # Styling
│   └── script.js              # Frontend JavaScript logic
├── generated_images/          # Directory for saved generated images
├── IpdSD_1 - Copy.ipynb      # Original notebook (reference)
├── erics code ipd - Copy.ipynb # Additional reference notebook
└── README.md                  # This file
```

## 🎯 Usage Guide

### 1. Fill User Information
- **Name**: Your full name
- **Email**: Your email address
- **Registration ID**: Your unique registration identifier

### 2. Enter Prompts

#### Positive Prompt (Required)
Describe what you want in your interior design. Be specific!

**Good Examples:**
- "Modern Scandinavian living room with natural light, featuring light wood floors, white furniture, and minimalist decor"
- "Industrial loft bedroom with exposed brick walls, metal bed frame, and vintage lighting"
- "Cozy minimalist kitchen with white cabinets, marble countertops, and pendant lights"

#### Negative Prompt (Optional)
Describe what you want to avoid in the generated image.

**Common Examples:**
- "blurry, dark, cluttered, people, low quality, distortion"
- "messy, cramped, outdated furniture, poor lighting"
- "cartoon, sketch, painting, unrealistic proportions"

### 3. Generate Image
Click the "Generate Design" button and wait for the AI to create your design (typically 30-60 seconds).

### 4. Download Result
Hover over the generated image and click the "Download" button to save it to your device.

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns server status.

**Response:**
```json
{
  "status": "healthy"
}
```

### Generate Image
```
POST /api/generate
```
Generates an interior design image based on prompts.

**Request Body:**
```json
{
  "userInfo": {
    "name": "John Doe",
    "email": "john@example.com",
    "registration": "REG123456"
  },
  "positivePrompt": "Modern living room with minimalist design",
  "negativePrompt": "blurry, dark, cluttered"
}
```

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "imagePath": "/api/image/uuid.png",
  "userInfo": {...},
  "prompt": "...",
  "negativePrompt": "..."
}
```

### Get Image
```
GET /api/image/<filename>
```
Retrieves a previously generated image by filename.

## ⚙️ Configuration

### Model Settings

You can modify generation parameters in `backend/app.py`:

```python
images = gen.generate_room_scene(
    prompt=positive_prompt,
    negative_prompt=negative_prompt,
    num_images=1,              # Number of images to generate
    guidance_scale=7.5,        # How closely to follow prompt (7-15 recommended)
    num_inference_steps=50,    # Quality vs speed (20-100)
    height=512,                # Image height
    width=512                  # Image width
)
```

### Change Model

To use a different Stable Diffusion model, edit `backend/model_handler.py`:

```python
def __init__(self, model_id="runwayml/stable-diffusion-v1-5"):
    # Change model_id to:
    # "stabilityai/stable-diffusion-2-1" for SD 2.1
    # "CompVis/stable-diffusion-v1-4" for SD 1.4
    # Or any other compatible model
```

## 🐛 Troubleshooting

### Model Loading Issues

**Problem**: Model fails to download or load
- **Solution**: Check internet connection. Models are downloaded from Hugging Face. Ensure you have sufficient disk space (~4-5GB).

### CUDA/GPU Issues

**Problem**: "CUDA out of memory" error
- **Solution**: 
  - Reduce image size (height/width) in `app.py`
  - Reduce `num_inference_steps`
  - Use CPU mode (slower but works)

**Problem**: CUDA not available
- **Solution**: The app will automatically fall back to CPU mode. Generation will be slower but functional.

### Port Already in Use

**Problem**: "Address already in use" error
- **Solution**: Change the port in `backend/app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Use different port
```

### CORS Errors

**Problem**: Frontend can't connect to backend
- **Solution**: Ensure Flask-CORS is installed and backend is running on the correct port.

### Slow Generation

**Problem**: Image generation takes too long
- **Solutions**:
  - Use GPU if available
  - Reduce `num_inference_steps` (try 30 instead of 50)
  - Reduce image dimensions (try 384x384 instead of 512x512)

---

**Happy Designing! 🎨**

