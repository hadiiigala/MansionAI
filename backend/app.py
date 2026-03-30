from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import torch
from model_handler import InteriorDesignGenerator
from audio_handler import AudioHandler
import base64
from io import BytesIO
from PIL import Image
import uuid
import traceback
import numpy as np
from typing import Optional, Dict, Any

app = Flask(__name__)
CORS(app)

# Disable Flask's automatic reloading in debug mode to prevent constant restarts
app.config['DEBUG'] = False
app.config['USE_RELOADER'] = False

# Initialize the generator (lazy loading)
generator = None
audio_handler = None

def get_generator():
    global generator
    if generator is None:
        print("Loading Stable Diffusion model...")
        generator = InteriorDesignGenerator()
        print("Model loaded successfully!")
    return generator

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/generate', methods=['POST'])
def generate_image():
    try:
        data: Optional[Dict[str, Any]] = request.json
        
        # Get user info and prompts
        user_info = data.get('userInfo', {}) if data else {}
        positive_prompt = data.get('positivePrompt', '') if data else ''
        negative_prompt = data.get('negativePrompt', '') if data else ''
        num_views = data.get('numViews', 1) if data else 1  # Default to 1 view
        
        if not positive_prompt:
            return jsonify({"error": "Positive prompt is required"}), 400
        
        # Get generator
        gen = get_generator()
        
        # Generate images
        print(f"Generating {num_views} view(s) with prompt: {positive_prompt[:50]}...")
        
        # Use fewer steps for faster generation (30 instead of 50)
        # Can be increased for better quality but slower
        images = gen.generate_room_scene(
            prompt=positive_prompt,
            negative_prompt=negative_prompt if negative_prompt else "blurry, low quality, distorted, cluttered, dark, messy",
            num_images=num_views,
            guidance_scale=7.5,
            num_inference_steps=30,  # Reduced from 50 for faster generation
            height=512,
            width=512
        )
        
        print(f"Image generation completed! Generated {len(images)} images.")
        
        # Convert images to base64
        image_data_list = []
        for i, image in enumerate(images):
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Save image to disk (relative to project root)
            generated_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_images")
            os.makedirs(generated_dir, exist_ok=True)
            image_filename = f"{uuid.uuid4()}_view_{i+1}.png"
            image_path = os.path.join(generated_dir, image_filename)
            image.save(image_path)
            
            image_data_list.append({
                "image": f"data:image/png;base64,{img_str}",
                "imagePath": f"/api/image/{image_filename}",
                "viewNumber": i + 1
            })
        
        return jsonify({
            "success": True,
            "images": image_data_list,
            "userInfo": user_info,
            "prompt": positive_prompt,
            "negativePrompt": negative_prompt,
            "numViews": len(images)
        })
        
    except torch.cuda.OutOfMemoryError as e:
        print(f"CUDA out of memory error: {str(e)}")
        return jsonify({
            "error": "Out of memory. The image generation requires too much GPU memory. Try reducing image size or restart the server.",
            "details": str(e)
        }), 500
    except RuntimeError as e:
        error_msg = str(e)
        print(f"Runtime error: {error_msg}")
        if "out of memory" in error_msg.lower():
            return jsonify({
                "error": "Out of memory. Try reducing image size or inference steps.",
                "details": error_msg
            }), 500
        return jsonify({"error": f"Generation failed: {error_msg}"}), 500
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Failed to generate image: {str(e)}",
            "details": "Check server logs for more information"
        }), 500

@app.route('/api/image/<filename>', methods=['GET'])
def get_image(filename):
    try:
        generated_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_images")
        image_path = os.path.join(generated_dir, filename)
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/png')
        return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compute-similarity', methods=['POST'])
def compute_similarity():
    """
    Compute similarity between generated images and IKEA images using CLIP embeddings.
    """
    try:
        data: Optional[Dict[str, Any]] = request.json
        generated_images_dir = data.get('generatedImagesDir', '../generated_images') if data else '../generated_images'
        ikea_images_dir = data.get('ikeaImagesDir', '../ikea_dataset') if data else '../ikea_dataset'
        
        # Import here to avoid issues if clip is not installed
        try:
            from clip_similarity import CLIPImageSimilarity
        except ImportError as e:
            return jsonify({
                "error": "CLIP module not found. Please install clip package.",
                "details": str(e)
            }), 500
        
        # Initialize the similarity evaluator
        evaluator = CLIPImageSimilarity()
        
        # Compute similarity matrix
        similarity_matrix, generated_paths, ikea_paths = evaluator.compute_similarity_matrix(
            generated_images_dir, ikea_images_dir
        )
        
        # Find most similar pairs (only if we have IKEA images)
        results = []
        if len(ikea_paths) > 0:
            top_pairs = evaluator.find_most_similar_pairs(
                similarity_matrix, generated_paths, ikea_paths, top_k=5
            )
            
            # Format results
            for gen_path, ikea_path, similarity in top_pairs:
                results.append({
                    "generated_image": os.path.basename(gen_path),
                    "ikea_image": os.path.basename(ikea_path),
                    "similarity": float(similarity)
                })
        else:
            print(f"Warning: No IKEA images found in directory: {ikea_images_dir}")
        
        return jsonify({
            "success": True,
            "results": results,
            "matrix_shape": similarity_matrix.shape,
            "ikea_images_found": len(ikea_paths) > 0
        })
        
    except Exception as e:
        print(f"Error computing similarity: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Failed to compute similarity: {str(e)}",
            "details": "Check server logs for more information"
        }), 500

def get_audio_handler():
    global audio_handler
    if audio_handler is None:
        audio_handler = AudioHandler()
    return audio_handler

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data: Optional[Dict[str, Any]] = request.json
        text = data.get('text', '') if data else ''
        rate = data.get('rate', 150) if data else 150
        volume = data.get('volume', 0.9) if data else 0.9
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Get audio handler
        handler = get_audio_handler()
        
        # Set voice properties if provided
        if rate or volume:
            handler.set_voice_properties(rate=rate, volume=volume)
        
        # Convert text to speech
        result = handler.text_to_speech(text, output_format='base64')
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"Error in text_to_speech endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        data: Optional[Dict[str, Any]] = request.json
        audio_base64 = data.get('audio', '') if data else ''
        language = data.get('language', 'en-US') if data else 'en-US'
        
        if not audio_base64:
            return jsonify({"error": "Audio data is required"}), 400
        
        # Get audio handler
        handler = get_audio_handler()
        
        # Convert speech to text
        result = handler.speech_to_text(audio_base64, language=language)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Error in speech_to_text endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    # Disable reloader to prevent constant restarts
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)